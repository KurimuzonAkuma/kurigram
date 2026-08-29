#  Pyrogram - Telegram MTProto API Client Library for Python
#  Copyright (C) 2017-present Dan <https://github.com/delivrance>
#
#  This file is part of Pyrogram.
#
#  Pyrogram is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Lesser General Public License as published
#  by the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  Pyrogram is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Lesser General Public License for more details.
#
#  You should have received a copy of the GNU Lesser General Public License
#  along with Pyrogram.  If not, see <http://www.gnu.org/licenses/>.

import asyncio
from concurrent.futures import Executor
from pathlib import Path
from typing import Final, List, Optional, Union

import pytest

from pyrogram import raw, types
from pyrogram.methods.advanced.save_file import SaveFile

_PART_SIZE: Final[int] = 512 * 1024

# `rnd_id()` below answers with this too, so a re-upload addresses the same file as the
#  upload that produced it.
_FILE_ID: Final[int] = 1234567890


class Storage:
    async def dc_id(self) -> int:
        return 2


class Media:
    """A media session that records the parts it was asked to save."""

    def __init__(self, rejects_part: Optional[int] = None) -> None:
        self.rejects_part = rejects_part
        self.saved_parts: List[int] = []

    async def invoke(
        self,
        query: Union[raw.functions.upload.SaveFilePart, raw.functions.upload.SaveBigFilePart],
    ) -> None:
        if query.file_part == self.rejects_part:
            raise ConnectionError("the server closed the connection")

        self.saved_parts.append(query.file_part)


class Uploader(SaveFile):
    def __init__(self, media: Media) -> None:
        self.media = media
        self.me: Optional[types.User] = None
        self.storage = Storage()
        self.executor: Optional[Executor] = None
        self.save_file_semaphore = asyncio.Semaphore(1)

    @property
    def loop(self) -> asyncio.AbstractEventLoop:
        return asyncio.get_event_loop()

    def rnd_id(self) -> int:
        return _FILE_ID

    async def get_session(self, dc_id: int, *, is_media: bool = False) -> Media:
        return self.media


@pytest.fixture
def three_parts(tmp_path: Path) -> str:
    path = tmp_path / "upload.bin"
    path.write_bytes(b"x" * (2 * _PART_SIZE + 1))

    return str(path)


@pytest.mark.asyncio
async def test_a_finished_upload_describes_every_part(three_parts: str) -> None:
    media = Media()

    file = await Uploader(media).save_file(three_parts)

    assert isinstance(file, raw.types.InputFile)
    assert file.parts == 3
    assert media.saved_parts == [0, 1, 2]


@pytest.mark.asyncio
async def test_a_part_the_server_refused_reaches_the_caller(three_parts: str) -> None:
    # The failure used to be logged inside the worker and nowhere else: `save_file()` handed back
    #  an `InputFile` for a file the server never received in full, and the send that followed
    #  failed with an unrelated error — or, for a caller that stored the id, much later.
    media = Media(rejects_part=1)

    with pytest.raises(ConnectionError):
        await Uploader(media).save_file(three_parts)


@pytest.mark.asyncio
async def test_the_parts_around_the_refused_one_are_still_sent(three_parts: str) -> None:
    media = Media(rejects_part=1)

    with pytest.raises(ConnectionError):
        await Uploader(media).save_file(three_parts)

    # The upload is not aborted mid-way — a worker that stops consuming leaves the producer
    #  blocked on a queue of size one, so every part is offered and only the answer is remembered.
    assert media.saved_parts == [0, 2]


@pytest.mark.asyncio
async def test_re_uploading_one_missing_part_answers_with_nothing(three_parts: str) -> None:
    media = Media()

    file = await Uploader(media).save_file(three_parts, file_id=_FILE_ID, file_part=1)

    assert file is None
    assert media.saved_parts == [1]


@pytest.mark.asyncio
async def test_a_missing_part_the_server_refused_reaches_the_caller_too(three_parts: str) -> None:
    media = Media(rejects_part=1)

    with pytest.raises(ConnectionError):
        await Uploader(media).save_file(three_parts, file_id=_FILE_ID, file_part=1)


@pytest.mark.asyncio
async def test_no_path_is_not_an_upload_at_all() -> None:
    assert await Uploader(Media()).save_file(None) is None
