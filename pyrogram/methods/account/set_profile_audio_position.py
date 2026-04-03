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

from typing import Optional

import pyrogram
from pyrogram import raw, utils
from pyrogram.file_id import FileType


class SetProfileAudioPosition:
    async def set_profile_audio_position(
        self: "pyrogram.Client", file_id: str, after_file_id: Optional[str] = None
    ):
        """Changes position of an audio file in the profile audio files of the current user.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            file_id (``str``):
                Identifier of the file from profile audio files, which position will be changed.

            after_file_id (``str``):
                Identifier of the file from profile audio files after which the file will be positioned.
                Pass None to move the file to the beginning of the list.

        Returns:
            ``bool``: On success, True is returned.

        Example:
            .. code-block:: python

                # Change audio position in profile
                await app.set_profile_audio_position(file_id, after_file_id)

                # Move audio to the beginning of profile
                await app.set_profile_audio_position(file_id)
        """
        r = await self.invoke(
            raw.functions.account.SaveMusic(
                id=(utils.get_input_media_from_file_id(file_id, FileType.AUDIO)).id,
                after_id=(utils.get_input_media_from_file_id(after_file_id, FileType.AUDIO)).id
                if after_file_id
                else None
            )
        )

        return r
