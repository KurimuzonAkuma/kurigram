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

from typing import List, Optional

import pyrogram
from pyrogram import enums, raw, types

from ..object import Object


class PaymentForm(Object):
    """Contains information about an invoice payment form.

    Parameters:
        id (``int``):
            Form id.

        type (:obj:`~pyrogram.enums.PaymentFormType`):
            Type of the payment form.

        title (``str``, *optional*):
            Form title.

        description (``str``, *optional*):
            Form description.

        photo (:obj:`~pyrogram.types.Photo`, *optional*):
            Product photo.

        seller_bot_user_id (``int``, *optional*):
            User identifier of the seller bot.

        seller_bot (:obj:`~pyrogram.types.User`, *optional*):
            Information about the seller bot.

        payment_provider_user_id (``int``, *optional*):
            User identifier of the payment provider bot.

        payment_provider (:obj:`~pyrogram.types.User`, *optional*):
            Information about the payment provider.

        additional_payment_options (List of :obj:`~pyrogram.types.PaymentOption`, *optional*):
            The list of additional payment options.

        saved_credentials (List of :obj:`~pyrogram.types.SavedCredentials`, *optional*):
            The list of saved payment credentials.

        invoice (:obj:`~pyrogram.types.Invoice`, *optional*):
            Full information about the invoice.

        url (``str``, *optional*):
            Payment form URL.

        can_save_credentials (``bool``, *optional*):
            True, if the user can choose to save credentials.

        need_password (``bool``, *optional*):
            True, if the user will be able to save credentials, if sets up a 2-step verification password.

        native_provider (``str``, *optional*):
            Payment provider name.

        raw (:obj:`~pyrogram.raw.base.payments.PaymentForm`, *optional*):
            The raw object, as received from the Telegram API.
    """

    def __init__(
        self,
        *,
        client: Optional["pyrogram.Client"] = None,
        id: int,
        type: "enums.PaymentFormType",
        title: Optional[str] = None,
        description: Optional[str] = None,
        photo: Optional["types.Photo"] = None,
        seller_bot_user_id: Optional[int] = None,
        seller_bot: Optional["types.User"] = None,
        payment_provider_user_id: Optional[int] = None,
        payment_provider: Optional["types.User"] = None,
        additional_payment_options: Optional[List["types.PaymentOption"]] = None,
        saved_credentials: Optional[List["types.SavedCredentials"]] = None,
        invoice: Optional["types.Invoice"] = None,
        url: Optional[str] = None,
        can_save_credentials: Optional[bool] = None,
        need_password: Optional[bool] = None,
        native_provider: Optional[str] = None,
        raw: Optional["raw.base.payments.PaymentForm"] = None,
    ):
        super().__init__(client)

        self.id = id
        self.type = type
        self.seller_bot_user_id = seller_bot_user_id
        self.seller_bot = seller_bot
        self.payment_provider_user_id = payment_provider_user_id
        self.payment_provider = payment_provider
        self.additional_payment_options = additional_payment_options
        self.saved_credentials = saved_credentials
        self.title = title
        self.description = description
        self.photo = photo
        self.invoice = invoice
        self.url = url
        self.can_save_credentials = can_save_credentials
        self.need_password = need_password
        self.native_provider = native_provider
        self.raw = raw

    @staticmethod
    async def _parse(client, form: "raw.base.payments.PaymentForm") -> "PaymentForm":
        users = {i.id: i for i in getattr(form, "users", [])}

        if isinstance(form, raw.types.payments.PaymentForm):
            return PaymentForm(
                id=form.form_id,
                type=enums.PaymentFormType.REGULAR,
                title=form.title,
                description=form.description,
                photo=types.Photo._parse(client, form.photo),
                seller_bot_user_id=form.bot_id,
                seller_bot=await types.User._parse(client, users.get(form.bot_id)),
                payment_provider_user_id=form.provider_id,
                payment_provider=await types.User._parse(client, users.get(form.provider_id)),
                invoice=types.Invoice._parse(client, form.invoice),
                url=form.url,
                can_save_credentials=form.can_save_credentials,
                need_password=form.password_missing,
                native_provider=form.native_provider,
                # native_params,
                additional_payment_options=types.List([types.PaymentOption._parse(option) for option in getattr(form, "additional_methods", [])]) or None,
                # saved_info,
                saved_credentials=types.List([types.SavedCredentials._parse(credential) for credential in getattr(form, "saved_credentials", [])]) or None,
                raw=form
            )
        elif isinstance(form, raw.types.payments.PaymentFormStarGift):
            return PaymentForm(
                id=form.form_id,
                type=enums.PaymentFormType.STAR_SUBSCRIPTION,
                invoice=types.Invoice._parse(client, form.invoice),
                raw=form
            )
        elif isinstance(form, raw.types.payments.PaymentFormStars):
            return PaymentForm(
                id=form.form_id,
                type=enums.PaymentFormType.STARS,
                title=form.title,
                description=form.description,
                photo=types.Photo._parse(client, form.photo),
                seller_bot_user_id=form.bot_id,
                seller_bot=await types.User._parse(client, users.get(form.bot_id)),
                invoice=types.Invoice._parse(client, form.invoice),
                raw=form
            )
