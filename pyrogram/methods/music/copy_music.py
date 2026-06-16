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

from typing import Union

import pyrogram
from pyrogram import types


class CopyMusic:
    async def copy_music(
        self: "pyrogram.Client",
        audio: Union[str, "types.Audio"],
    ):
        """Copy an existing Telegram audio into the current user's saved music list.

        Unlike :meth:`~pyrogram.Client.copy_story`, Telegram does not expose a dedicated
        raw ``copy`` method for saved music, so this helper reuses the source audio file_id
        and saves it through :meth:`~pyrogram.Client.add_music`.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            audio (``str`` | :obj:`~pyrogram.types.Audio`):
                An audio ``file_id`` or a parsed :obj:`~pyrogram.types.Audio` object.

        Returns:
            ``bool``: On success, True is returned.

        Example:
            .. code-block:: python

                await app.copy_music(message.audio)
        """
        file_id = audio.file_id if isinstance(audio, types.Audio) else audio
        return await self.add_music(file_id)
