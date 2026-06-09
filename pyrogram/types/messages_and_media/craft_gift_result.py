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

from pyrogram import types

from ..object import Object


class CraftGiftResult(Object):
    """Contains result of gift crafting.

    It can be one of:

    - :obj:`~pyrogram.types.CraftGiftResultSuccess`
    - :obj:`~pyrogram.types.CraftGiftResultFail`
    """

    def __init__(self):
        super().__init__()


class CraftGiftResultSuccess(CraftGiftResult):
    """Craft was successful.

    Parameters:
        gift (:obj:`~pyrogram.types.Gift`):
            The created gift.
    """

    def __init__(
        self,
        gift: "types.Gift"
    ):
        super().__init__()

        self.gift = gift


class CraftGiftResultFail(CraftGiftResult):
    """Craft has failed."""

    def __init__(self):
        super().__init__()
