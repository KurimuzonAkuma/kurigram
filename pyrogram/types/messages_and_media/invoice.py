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

from typing import List, Union, Optional

import pyrogram
from pyrogram import raw, types
from ..object import Object


class Invoice(Object):
    """This object contains basic information about an invoice.

    Parameters:
        currency (``str``):
            Three-letter ISO 4217 `currency <https://core.telegram.org/bots/payments#supported-currencies>`_ code.

        is_test (``bool``):
            True, if the invoice is a test invoice.

        title (``str``, *optional*):
            Product name.

        description (``str``, *optional*):
            Product description.

        total_amount (``int``, *optional*):
            Total price in the smallest units of the currency (integer, **not** float/double). For example, for a price of ``US$ 1.45`` pass ``amount = 145``. See the exp parameter in `currencies.json <https://core.telegram.org/bots/payments/currencies.json>`_, it shows the number of digits past the decimal point for each currency (2 for the majority of currencies).

        start_parameter (``str``, *optional*):
            Unique bot deep-linking parameter that can be used to generate this invoice.

        prices (List of :obj:`~pyrogram.types.LabeledPrice`, *optional*):
            Price breakdown, a list of components (e.g. product price, tax, discount, delivery cost, delivery tax, bonus, etc.).

        is_name_requested (``bool``, *optional*):
            True, if the name should be specified.

        is_phone_requested (``bool``, *optional*):
            True, if the phone should be specified.

        is_email_requested (``bool``, *optional*):
            True, if the email address should be specified.

        is_shipping_address_requested (``bool``, *optional*):
            True, if the shipping address should be specified.

        is_flexible (``bool``, *optional*):
            True, if the final price depends on the shipping method.

        is_phone_to_provider (``bool``, *optional*):
            True, if user's phone should be sent to provider.

        is_email_to_provider (``bool``, *optional*):
            True, if user's email address should be sent to provider.

        is_recurring (``bool``, *optional*):
            Whether this is a recurring payment.

        max_tip_amount (``int``, *optional*):
            The maximum accepted amount for tips in the smallest units of the currency (integer, not float/double).
            For example, for a price of US$ 1.45 pass amount = 145.
            See the exp parameter in currencies.json, it shows the number of digits past the decimal point for each currency (2 for the majority of currencies).

        suggested_tip_amounts (List of ``int``, *optional*):
            A vector of suggested amounts of tips in the smallest units of the currency (integer, not float/double).
            At most 4 suggested tip amounts can be specified.
            The suggested tip amounts must be positive, passed in a strictly increased order and must not exceed max_tip_amount.

        terms_url (``str``, *optional*):
            Terms of service URL.

        raw (:obj:`~pyrogram.raw.types.MessageMediaInvoice` | :obj:`~pyrogram.raw.types.Invoice`, *optional*):
            The raw object, as received from the Telegram API.
    """

    def __init__(
        self,
        *,
        client: Optional["pyrogram.Client"] = None,
        currency: str,
        is_test: bool,
        title: Optional[str] = None,
        description: Optional[str] = None,
        total_amount: Optional[int] = None,
        start_parameter: Optional[str] = None,
        prices: Optional[List["types.LabeledPrice"]] = None,
        is_name_requested: Optional[bool] = None,
        is_phone_requested: Optional[bool] = None,
        is_email_requested: Optional[bool] = None,
        is_shipping_address_requested: Optional[bool] = None,
        is_flexible: Optional[bool] = None,
        is_phone_to_provider: Optional[bool] = None,
        is_email_to_provider: Optional[bool] = None,
        is_recurring: Optional[bool] = None,
        max_tip_amount: Optional[int] = None,
        suggested_tip_amounts: Optional[List[int]] = None,
        terms_url: Optional[str] = None,
        raw: Optional[Union["raw.types.MessageMediaInvoice", "raw.types.Invoice"]] = None
    ):
        super().__init__(client)

        self.currency = currency
        self.is_test = is_test
        self.title = title
        self.description = description
        self.total_amount = total_amount
        self.start_parameter = start_parameter
        self.prices = prices
        self.is_name_requested = is_name_requested
        self.is_phone_requested = is_phone_requested
        self.is_email_requested = is_email_requested
        self.is_shipping_address_requested = is_shipping_address_requested
        self.is_flexible = is_flexible
        self.is_phone_to_provider = is_phone_to_provider
        self.is_email_to_provider = is_email_to_provider
        self.is_recurring = is_recurring
        self.max_tip_amount = max_tip_amount
        self.suggested_tip_amounts = suggested_tip_amounts
        self.terms_url = terms_url
        self.raw = raw

    @staticmethod
    def _parse(client, invoice: Union["raw.types.MessageMediaInvoice", "raw.types.Invoice"]) -> "Invoice":
        return Invoice(
            currency=invoice.currency,
            is_test=invoice.test,
            title=getattr(invoice, "title", None),
            description=getattr(invoice, "description", None),
            total_amount=getattr(invoice, "total_amount", None),
            start_parameter=getattr(invoice, "start_param", None) or None,
            prices=types.List(types.LabeledPrice._parse(lp) for lp in invoice.prices) if getattr(invoice, "prices", None) else None,
            is_name_requested=getattr(invoice, "name_requested", None),
            is_phone_requested=getattr(invoice, "phone_requested", None),
            is_email_requested=getattr(invoice, "email_requested", None),
            is_shipping_address_requested=getattr(invoice, "shipping_address_requested", None),
            is_flexible=getattr(invoice, "flexible", None),
            is_phone_to_provider=getattr(invoice, "phone_to_provider", None),
            is_email_to_provider=getattr(invoice, "email_to_provider", None),
            is_recurring=getattr(invoice, "recurring", None),
            max_tip_amount=getattr(invoice, "max_tip_amount", None),
            suggested_tip_amounts=getattr(invoice, "suggested_tip_amounts", None) or None,
            terms_url=getattr(invoice, "terms_url", None),
            raw=invoice,
            client=client
            # TODO: Add photo and extended media
        )
