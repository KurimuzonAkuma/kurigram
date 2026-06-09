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

from typing import Optional, Union

import pyrogram
from pyrogram import raw, types


class SetContactNote:
    async def set_contact_note(
        self: "pyrogram.Client",
        user_id: Union[int, str],
        note: Optional[Union[str, "types.FormattedText"]] = None,
    ):
        """Changes a note of a contact user.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            user_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target user.

            note (``str`` | :obj:`~pyrogram.types.FormattedText`, *optional*):
                Note to set for the user.

        Returns:
            ``bool``: On success, True is returned.

        Example:
            .. code-block:: python

                await app.set_contact_note(12345678, types.FormattedText(text="My best friend!"))
        """
        if isinstance(note, str):
            note = types.FormattedText(text=note)

        r = await self.invoke(
            raw.functions.contacts.UpdateContactNote(
                id=await self.resolve_peer(user_id),
                note=await note.write(self)
                if note is not None
                else raw.types.TextWithEntities(text="", entities=[]),
            )
        )

        return r
