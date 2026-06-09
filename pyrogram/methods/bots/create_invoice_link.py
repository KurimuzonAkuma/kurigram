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

from typing import List, Optional, Union

import pyrogram
from pyrogram import raw, types


class CreateInvoiceLink:
    async def create_invoice_link(
        self: "pyrogram.Client",
        title: str,
        description: str,
        payload: Union[str, bytes],
        currency: str,
        prices: List["types.LabeledPrice"],
        provider_token: Optional[str] = None,
        subscription_period: Optional[int] = None,
        max_tip_amount: Optional[int] = None,
        suggested_tip_amounts: Optional[List[int]] = None,
        start_parameter: Optional[str] = None,
        provider_data: Optional[str] = None,
        photo_url: Optional[str] = None,
        photo_size: Optional[int] = None,
        photo_width: Optional[int] = None,
        photo_height: Optional[int] = None,
        need_name: Optional[bool] = None,
        need_phone_number: Optional[bool] = None,
        need_email: Optional[bool] = None,
        need_shipping_address: Optional[bool] = None,
        send_phone_number_to_provider: Optional[bool] = None,
        send_email_to_provider: Optional[bool] = None,
        is_flexible: Optional[bool] = None,
    ) -> str:
        """Create invoice link.

        .. include:: /_includes/usable-by/bots.rst

        Parameters:
            title (``str``):
                Product name, 1-32 characters.

            description (``str``):
                Product description, 1-255 characters

            payload (``str`` | ``bytes``):
                Bot-defined invoice payload, 1-128 bytes. This will not be displayed to the user, use for your internal processes.

            currency (``str``):
                Three-letter ISO 4217 currency code, see `more on currencies <https://core.telegram.org/bots/payments#supported-currencies>`_. Pass ``XTR`` for payments in `Telegram Stars <https://t.me/BotNews/90>`_.

            prices (List of :obj:`~pyrogram.types.LabeledPrice`):
                Price breakdown, a JSON-serialized list of components (e.g. product price, tax, discount, delivery cost, delivery tax, bonus, etc.). Must contain exactly one item for payments in `Telegram Stars <https://t.me/BotNews/90>`_.

            reply_to_message_id (``int``, *optional*):
                If the message is a reply, ID of the original message.

            provider_token (``str``, *optional*):
                Payment provider token, obtained via `@BotFather <https://t.me/botfather>`_. Pass an empty string for payments in `Telegram Stars <https://t.me/BotNews/90>`_.

            subscription_period (``int``, *optional*):
                The number of seconds the subscription will be active for before the next payment.
                The currency must be set to “XTR” (Telegram Stars) if the parameter is used.
                Currently, it must always be 2592000 (30 days) if specified.

            max_tip_amount (``int``, *optional*):
                The maximum accepted amount for tips in the smallest units of the currency (integer, **not** float/double). For example, for a maximum tip of ``US$ 1.45`` pass ``max_tip_amount = 145``. See the exp parameter in `currencies.json <https://core.telegram.org/bots/payments/currencies.json>`_, it shows the number of digits past the decimal point for each currency (2 for the majority of currencies). Defaults to 0. Not supported for payments in `Telegram Stars <https://t.me/BotNews/90>`_.

            suggested_tip_amounts (List of ``int``, *optional*):
                An array of suggested amounts of tips in the smallest units of the currency (integer, **not** float/double). At most 4 suggested tip amounts can be specified. The suggested tip amounts must be positive, passed in a strictly increased order and must not exceed ``max_tip_amount``.

            start_parameter (``str``, *optional*):
                Unique deep-linking parameter. If left empty, **forwarded copies** of the sent message will have a Pay button, allowing multiple users to pay directly from the forwarded message, using the same invoice. If non-empty, forwarded copies of the sent message will have a URL button with a deep link to the bot (instead of a Pay button), with the value used as the start parameter.

            provider_data (``str``, *optional*):
                JSON-serialized data about the invoice, which will be shared with the payment provider. A detailed description of required fields should be provided by the payment provider.

            photo_url (``str``, *optional*):
                URL of the product photo for the invoice. Can be a photo of the goods or a marketing image for a service. People like it better when they see what they are paying for.

            photo_size (``int``, *optional*):
                Photo size in bytes

            photo_width (``int``, *optional*):
                Photo width

            photo_height (``int``, *optional*):
                Photo height

            need_name (``bool``, *optional*):
                Pass True if you require the user's full name to complete the order. Ignored for payments in `Telegram Stars <https://t.me/BotNews/90>`_.

            need_phone_number (``bool``, *optional*):
                Pass True if you require the user's phone number to complete the order. Ignored for payments in `Telegram Stars <https://t.me/BotNews/90>`_.

            need_email (``bool``, *optional*):
                Pass True if you require the user's email address to complete the order. Ignored for payments in `Telegram Stars <https://t.me/BotNews/90>`_.

            need_shipping_address (``bool``, *optional*):
                Pass True if you require the user's shipping address to complete the order. Ignored for payments in `Telegram Stars <https://t.me/BotNews/90>`_.

            send_phone_number_to_provider (``bool``, *optional*):
                Pass True if the user's phone number should be sent to the provider. Ignored for payments in `Telegram Stars <https://t.me/BotNews/90>`_.

            send_email_to_provider (``bool``, *optional*):
                Pass True if the user's email address should be sent to the provider. Ignored for payments in `Telegram Stars <https://t.me/BotNews/90>`_.

            is_flexible (``bool``, *optional*):
                Pass True if the final price depends on the shipping method. Ignored for payments in `Telegram Stars <https://t.me/BotNews/90>`_.

        Returns:
            ``str``: On success, the invoice url is returned.

        """
        r = await self.invoke(
            raw.functions.payments.ExportInvoice(
                invoice_media=raw.types.InputMediaInvoice(
                    title=title,
                    description=description,
                    photo=raw.types.InputWebDocument(
                        url=photo_url,
                        mime_type="image/jpg",
                        size=photo_size,
                        attributes=[
                            raw.types.DocumentAttributeImageSize(w=photo_width, h=photo_height)
                        ],
                    ) if photo_url else None,
                    invoice=raw.types.Invoice(
                        currency=currency,
                        prices=[i.write() for i in prices],
                        test=self.test_mode,
                        name_requested=need_name,
                        phone_requested=need_phone_number,
                        email_requested=need_email,
                        shipping_address_requested=need_shipping_address,
                        flexible=is_flexible,
                        phone_to_provider=send_phone_number_to_provider,
                        email_to_provider=send_email_to_provider,
                        max_tip_amount=max_tip_amount,
                        suggested_tip_amounts=suggested_tip_amounts,
                        subscription_period=subscription_period,
                    ),
                    payload=payload.encode() if isinstance(payload, str) else payload,
                    provider=provider_token,
                    provider_data=raw.types.DataJSON(data=provider_data or "{}"),
                    start_param=start_parameter,
                )
            )
        )

        return r.url
