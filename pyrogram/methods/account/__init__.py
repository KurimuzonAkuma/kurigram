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

from .add_profile_audio import AddProfileAudio
from .get_account_ttl import GetAccountTTL
from .get_global_privacy_settings import GetGlobalPrivacySettings
from .get_privacy import GetPrivacy
from .remove_profile_audio import RemoveProfileAudio
from .set_account_ttl import SetAccountTTL
from .set_global_privacy_settings import SetGlobalPrivacySettings
from .set_inactive_session_ttl import SetInactiveSessionTTL
from .set_privacy import SetPrivacy
from .set_profile_audio_position import SetProfileAudioPosition

class Account(
    AddProfileAudio,
    GetAccountTTL,
    GetGlobalPrivacySettings,
    GetPrivacy,
    RemoveProfileAudio,
    SetAccountTTL,
    SetGlobalPrivacySettings,
    SetInactiveSessionTTL,
    SetPrivacy,
    SetProfileAudioPosition
):
    pass
