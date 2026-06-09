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

from ..object import Object


class KeyboardButtonRequestManagedBot(Object):
    """This object defines the parameters for the creation of a managed bot.

    Parameters:
        button_id (``int``):
            Identifier of button.

        suggested_name (``str``):
            Suggested name for the bot.

        suggested_username (``str``):
            Suggested username for the bot.
    """

    def __init__(
        self, *,
        button_id: int,
        suggested_name: str,
        suggested_username: str
    ):
        super().__init__()

        self.button_id = button_id
        self.suggested_name = suggested_name
        self.suggested_username = suggested_username
