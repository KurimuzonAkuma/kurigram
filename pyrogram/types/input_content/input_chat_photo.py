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

from typing import BinaryIO, Optional, Union, cast

import pyrogram
from pyrogram import raw, utils
from pyrogram.file_id import FileType

from ..object import Object


class InputChatPhoto(Object):
    """Describes a photo to be set as a user profile or chat photo.

    It should be one of:

    - :obj:`~pyrogram.types.InputChatPhotoPrevious`
    - :obj:`~pyrogram.types.InputChatPhotoStatic`
    - :obj:`~pyrogram.types.InputChatPhotoAnimation`
    """
    # TODO: - :obj:`~pyrogram.types.InputChatPhotoSticker`

    def __init__(
        self,
    ):
        super().__init__()

    async def write(self, client: "pyrogram.Client") -> Union["raw.base.InputFile", "raw.base.InputPhoto"]:
        raise NotImplementedError


class InputChatPhotoPrevious(InputChatPhoto):
    """A previously used profile photo of the current user.

    Parameters:
        chat_photo_file_id (``str``):
            Identifier of the current user's profile photo to reuse.
    """
    def __init__(
        self,
        chat_photo_file_id: str
    ):
        super().__init__()

        self.chat_photo_file_id = chat_photo_file_id

    async def write(self, client: "pyrogram.Client") -> "raw.base.InputPhoto":
        photo = utils.get_input_media_from_file_id(self.chat_photo_file_id, FileType.PHOTO)

        # The helper rejects any other file type when it is given one to expect, so the
        #  document half of its return type is unreachable from here.
        return cast("raw.types.InputMediaPhoto", photo).id


class InputChatPhotoStatic(InputChatPhoto):
    """A static photo in JPEG format.

    Parameters:
        photo (``str`` | ``BinaryIO``):
            Photo to be set as profile photo.
    """
    def __init__(
        self,
        photo: Union[str, BinaryIO]
    ):
        super().__init__()

        self.photo = photo

    async def write(self, client: "pyrogram.Client") -> "raw.base.InputFile":
        return await client.save_file(self.photo)


class InputChatPhotoAnimation(InputChatPhoto):
    """An animation in H.264/MPEG-4 AVC format.

    .. note::

        Must be square, at most 10 seconds long, have width between 160 and 1280 and be at most 2MB in size

    Parameters:
        animation (``str`` | ``BinaryIO``):
            Animation to be set as profile photo.

        main_frame_timestamp (``float``):
            Timestamp of the frame, which will be used as static chat photo.
    """
    def __init__(
        self,
        animation: Union[str, BinaryIO],
        main_frame_timestamp: Optional[float] = None
    ):
        super().__init__()

        self.animation = animation
        self.main_frame_timestamp = main_frame_timestamp

    async def write(self, client: "pyrogram.Client") -> "raw.base.InputFile":
        return await client.save_file(self.animation)
