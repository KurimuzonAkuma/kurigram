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

from typing import List, Optional

import pyrogram
from pyrogram import enums, raw, types, utils
from pyrogram.types.messages_and_media.message import Str

from ..object import Object


class FormattedText(Object):
    """Contains information about a text with some entities.

    Parameters:
        text (``str``):
            The text.

        parse_mode (:obj:`~pyrogram.types.ParseMode`, *optional*):
            Parse mode of the text.

        entities (List of :obj:`~pyrogram.types.MessageEntity`, *optional*):
            Entities contained in the text. Entities can be nested, but must not mutually intersect with each other.
    """

    def __init__(
        self,
        *,
        text: Str,
        parse_mode: Optional["enums.ParseMode"] = None,
        entities: Optional[List["types.MessageEntity"]] = None,
    ):
        super().__init__()

        self.text = text
        self.parse_mode = parse_mode
        self.entities = entities

    def __str__(self) -> str:
        return self.text

    @staticmethod
    def _parse(client: "pyrogram.Client", text: "raw.types.TextWithEntities") -> "FormattedText":
        if not isinstance(text, raw.types.TextWithEntities):
            return None

        entities = types.List(
            filter(
                lambda x: x is not None,
                [types.MessageEntity._parse(client, entity, {}) for entity in text.entities],
            )
        )

        return FormattedText(
            text=Str(text.text).init(entities),
            entities=entities or None,
        )

    async def write(self, client: "pyrogram.Client") -> "raw.types.TextWithEntities":
        message, entities = (
            await utils.parse_text_entities(client, self.text, self.parse_mode or client.parse_mode, self.entities)
        ).values()

        return raw.types.TextWithEntities(text=message, entities=entities or [])
