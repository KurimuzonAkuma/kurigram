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

import pyrogram

from ..object import Object


class InputCredentials(Object):
    """Contains information about the payment method chosen by the user.

    It should be one of:

    - :obj:`~pyrogram.types.InputCredentialsApplePay`
    - :obj:`~pyrogram.types.InputCredentialsGooglePay`
    - :obj:`~pyrogram.types.InputCredentialsNew`
    - :obj:`~pyrogram.types.InputCredentialsSaved`
    """
    def __init__(self):
        super().__init__()

    async def write(self, client: "pyrogram.Client"):
        raise NotImplementedError
