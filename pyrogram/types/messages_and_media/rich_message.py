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

from typing import Dict, List, Optional

import pyrogram
from pyrogram import raw, types

from ..object import Object


class RichMessage(Object):
    """Rich formatted message.

    Parameters:
        blocks (List of :obj:`pyrogram.types.RichBlock`):
            Content of the message.

        is_rtl (``bool``, *optional*):
            True, if the rich message must be shown right-to-left.
    """

    def __init__(self, *, blocks: List["types.RichBlock"], is_rtl: Optional[bool] = None):
        super().__init__()

        self.blocks = blocks
        self.is_rtl = is_rtl

    @staticmethod
    async def _parse(
        client: "pyrogram.Client",
        rich_message: "raw.types.RichMessage",
        users: Dict[int, "raw.base.User"] = {},
        chats: Dict[int, "raw.base.Chat"] = {},
    ) -> "RichMessage":
        if isinstance(rich_message, raw.types.RichMessage):
            photos = {photo.id: photo for photo in rich_message.photos}
            documents = {document.id: document for document in rich_message.documents}

            return RichMessage(
                blocks=types.List(
                    [
                        await types.RichBlock._parse(
                            client,
                            block,
                            photos,
                            documents,
                            rich_message.part,
                            users,
                            chats,
                        )
                        for block in rich_message.blocks
                    ]
                ),
                is_rtl=rich_message.rtl,
            )
