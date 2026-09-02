#  Pyrogram - Telegram MTProto API Client Library for Python
#  Copyright (C) 2017-present <https://github.com/TelegramPlayGround>
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

from pyrogram import raw, types

from ..object import Object


class UpgradedGiftAttributeId(Object):
    """This object contains identifier of an upgraded gift attribute to search for.

    It can be one of:

    - :obj:`~pyrogram.types.UpgradedGiftAttributeIdModel`
    - :obj:`~pyrogram.types.UpgradedGiftAttributeIdSymbol`
    - :obj:`~pyrogram.types.UpgradedGiftAttributeIdBackdrop`
    """

    def __init__(
        self,
    ):
        super().__init__()

    @staticmethod
    def _parse(
        attribute_id: "raw.base.StarGiftAttributeId"
    ) -> Optional["UpgradedGiftAttributeId"]:
        if not attribute_id:
            return None

        if isinstance(attribute_id, raw.types.StarGiftAttributeIdModel):
            return types.UpgradedfGiftAttributeIdModel(
                sticker_id=attribute_id.document_id
            )
        elif isinstance(attribute_id, raw.types.StarGiftAttributeIdPattern):
            return types.UpgradedfGiftAttributeIdSymbol(
                sticker_id=attribute_id.document_id
            )
        elif isinstance(attribute_id, raw.types.StarGiftAttributeIdBackdrop):
            return types.UpgradedfGiftAttributeIdBackdrop(
                backdrop_id=attribute_id.backdrop_id
            )
