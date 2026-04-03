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

from pyrogram import raw, types

from ..object import Object


class PhoneNumberAuthenticationSettings(Object):
    """Contains settings for the authentication of the user's phone number.

    Parameters:
        allow_flash_call (``bool``, *optional*):
            Pass True if the authentication code may be sent via a flash call to the specified phone number.

        allow_missed_call (``bool``, *optional*):
            Pass True if the authentication code may be sent via a missed call to the specified phone number.

        is_current_phone_number (``bool``, *optional*):
            Pass True if the authenticated phone number is used on the current device.

        has_unknown_phone_number (``bool``, *optional*):
            Pass True if there is a SIM card in the current device, but it is not possible to check whether phone number matches.

        allow_sms_retriever_api (``bool``, *optional*):
            For official applications only.
            True, if the application can use Android SMS Retriever API (requires Google Play Services >= 10.2) to automatically receive the authentication code from the SMS.
            See https://developers.google.com/identity/sms-retriever/ for more details.

        firebase_authentication_settings (:obj:`~pyrogram.types.FirebaseAuthenticationSettings`, *optional*):
            For official Android and iOS applications only.
            Settings for Firebase Authentication.

        authentication_tokens (List of ``bytes``, *optional*)
            List of up to 20 authentication tokens, recently received in previously logged out sessions.
    """

    def __init__(
        self,
        *,
        allow_flash_call: Optional[bool] = None,
        allow_missed_call: Optional[bool] = None,
        is_current_phone_number: Optional[bool] = None,
        has_unknown_phone_number: Optional[bool] = None,
        allow_sms_retriever_api: Optional[bool] = None,
        firebase_authentication_settings: Optional["types.FirebaseAuthenticationSettings"] = None,
        authentication_tokens: Optional[List[bytes]] = None,
    ):
        super().__init__()

        self.allow_flash_call = allow_flash_call
        self.allow_missed_call = allow_missed_call
        self.is_current_phone_number = is_current_phone_number
        self.has_unknown_phone_number = has_unknown_phone_number
        self.allow_sms_retriever_api = allow_sms_retriever_api
        self.firebase_authentication_settings = firebase_authentication_settings
        self.authentication_tokens = authentication_tokens

    def write(self):
        return raw.types.CodeSettings(
            allow_flashcall=self.allow_flash_call,
            current_number=self.is_current_phone_number,
            allow_app_hash=self.allow_sms_retriever_api,
            allow_missed_call=self.allow_missed_call,
            allow_firebase=bool(self.firebase_authentication_settings),
            unknown_number=self.has_unknown_phone_number,
            logout_tokens=self.authentication_tokens,
            token=getattr(self.firebase_authentication_settings, "device_token", None),
            app_sandbox=getattr(self.firebase_authentication_settings, "is_app_sandbox", None),
        )
