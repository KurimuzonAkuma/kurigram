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


class FirebaseAuthenticationSettings(Object):
    """Contains settings for Firebase Authentication in the official applications.

    It can be one of:

    - :obj:`~pyrogram.types.FirebaseAuthenticationSettingsAndroid`
    - :obj:`~pyrogram.types.FirebaseAuthenticationSettingsIos`
    """

    def __init__(self):
        super().__init__()


class FirebaseAuthenticationSettingsAndroid(FirebaseAuthenticationSettings):
    """Settings for Firebase Authentication in the official Android application."""

    def __init__(self):
        super().__init__()


class FirebaseAuthenticationSettingsIos(FirebaseAuthenticationSettings):
    """Settings for Firebase Authentication in the official iOS application.

    Parameters:
        device_token (``str``):
            Device token from Apple Push Notification service.

        is_app_sandbox (``str``):
            True, if App Sandbox is enabled.
    """

    def __init__(self, device_token: str, is_app_sandbox: str):
        super().__init__()

        self.device_token = device_token
        self.is_app_sandbox = is_app_sandbox
