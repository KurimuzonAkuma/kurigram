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

from typing import List

import pyrogram
from pyrogram import raw, types

from ..object import Object


class GiftUpgradeVariants(Object):
    """Contains all possible variants of upgraded gifts for the given regular gift.

    Parameters:
        models (List of :obj:`~pyrogram.types.GiftAttribute`):
            Models that can be chosen for the gift after upgrade.

        symbols (List of :obj:`~pyrogram.types.GiftAttribute`):
            Symbols that can be chosen for the gift after upgrade.

        backdrops (List of :obj:`~pyrogram.types.GiftAttribute`):
            Backdrops that can be chosen for the gift after upgrade.
    """

    def __init__(
        self,
        *,
        models: List["types.GiftAttribute"],
        symbols: List["types.GiftAttribute"],
        backdrops: List["types.GiftAttribute"]
    ):
        super().__init__()

        self.models = models
        self.symbols = symbols
        self.backdrops = backdrops

    @staticmethod
    async def _parse(client: "pyrogram.Client", gift_upgrade_attributes: "raw.types.payments.StarGiftUpgradeAttributes"):
        models = types.List()
        symbols = types.List()
        backdrops = types.List()

        for attr in gift_upgrade_attributes.attributes:
            if isinstance(attr, raw.types.StarGiftAttributeModel):
                models.append(await types.GiftAttribute._parse(client, attr, {}, {}))
            elif isinstance(attr, raw.types.StarGiftAttributePattern):
                symbols.append(await types.GiftAttribute._parse(client, attr, {}, {}))
            elif isinstance(attr, raw.types.StarGiftAttributeBackdrop):
                backdrops.append(await types.GiftAttribute._parse(client, attr, {}, {}))

        return GiftUpgradeVariants(
            models=models,
            symbols=symbols,
            backdrops=backdrops
        )
