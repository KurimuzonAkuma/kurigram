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

import logging
import re

import pyrogram
from pyrogram import raw, types

log = logging.getLogger(__name__)


class ChangePhoneNumber:
    async def change_phone_number(
        self: "pyrogram.Client", phone_number: str, phone_code_hash: str, phone_code: str
    ) -> "types.User":
        """Change a user phone number in Telegram with a valid confirmation code.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            phone_number (``str``):
                Phone number in international format (includes the country prefix).

            phone_code_hash (``str``):
                Code identifier taken from the result of :meth:`~pyrogram.Client.send_phone_number_code`.

            phone_code (``str``):
                The valid confirmation code you received from SMS in your phone number.

        Returns:
            :obj:`~pyrogram.types.User`: On success, in case the change completed, the user is returned.
        """
        phone_number = re.sub(r"\D", "", phone_number)

        r = await self.invoke(
            raw.functions.account.ChangePhone(
                phone_number=phone_number,
                phone_code_hash=phone_code_hash,
                phone_code=phone_code
            )
        )

        return types.User._parse(self, r)
