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

from typing import Optional

import pyrogram
from pyrogram import raw

from ..object import Object


class PaymentResult(Object):
    """Contains the result of a payment request.

    Parameters:
        success (``bool``):
            True, if the payment request was successful.
            Otherwise, the verification_url will be non-empty.

        verification_url (``str``, *optional*):
            URL for additional payment credentials verification.

        raw (:obj:`~pyrogram.raw.base.payments.PaymentResult`, *optional*):
            The raw result from the Telegram API.
    """
    def __init__(
        self,
        *,
        success: bool,
        verification_url: Optional[str] = None,
        raw: Optional["raw.base.payments.PaymentResult"] = None,
    ):
        super().__init__()

        self.success = success
        self.verification_url = verification_url
        self.raw = raw

    @staticmethod
    def _parse(payment_result: "raw.base.payments.PaymentResult") -> "PaymentResult":
        if isinstance(payment_result, raw.types.payments.PaymentVerificationNeeded):
            return PaymentResult(
                success=False,
                verification_url=payment_result.url,
                raw=payment_result
            )
        elif isinstance(payment_result, raw.types.payments.PaymentResult):
            return PaymentResult(
                success=True,
                raw=payment_result
            )
