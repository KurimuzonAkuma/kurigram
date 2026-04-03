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

from enum import auto

from .auto_name import AutoName


class UpgradedGiftOrigin(AutoName):
    """Origin from which the upgraded gift was obtained. Used in :obj:`~pyrogram.types.Gift`."""

    UPGRADE = auto()
    "The gift was obtained by upgrading of a previously received gift."

    TRANSFER = auto()
    "The gift was transferred from another owner."

    RESALE = auto()
    "The gift was bought from another user."

    BLOCKCHAIN = auto()
    "The gift was assigned from blockchain and isn't owned by the current user. The gift can't be transferred, resold or withdrawn to blockchain."

    GIFTED_UPGRADE = auto()
    "The sender or receiver of the message has paid for upgraid of the gift, which has been completed."

    OFFER = auto()
    "The gift was bought through an offer."

    CRAFT = auto()
    "The gift was crafted from other gifts."
