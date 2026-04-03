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

from pyrogram import raw
from .auto_name import AutoName


class PrivacyKey(AutoName):
    """Privacy key enumeration used in :meth:`~pyrogram.Client.set_privacy`."""

    ABOUT = raw.types.InputPrivacyKeyAbout
    "Whether people can see your bio"

    ADDED_BY_PHONE = raw.types.InputPrivacyKeyAddedByPhone
    "Whether people can add you to their contact list by your phone number"

    BIRTHDAY = raw.types.InputPrivacyKeyBirthday
    "Whether the user can see our birthday."

    CHAT_INVITE = raw.types.InputPrivacyKeyChatInvite
    "Whether people will be able to invite you to chats"

    FORWARDS = raw.types.InputPrivacyKeyForwards
    "Whether messages forwarded from you will be anonymous"

    PHONE_CALL = raw.types.InputPrivacyKeyPhoneCall
    "Whether you will accept phone calls"

    PHONE_NUMBER = raw.types.InputPrivacyKeyPhoneNumber
    "Whether people will be able to see your phone number"

    PHONE_P2P = raw.types.InputPrivacyKeyPhoneP2P
    "Whether to allow P2P communication during VoIP calls"

    PROFILE_PHOTO = raw.types.InputPrivacyKeyProfilePhoto
    "Whether people will be able to see your profile picture"

    STATUS = raw.types.InputPrivacyKeyStatusTimestamp
    "Whether people will be able to see our exact last online timestamp."

    VOICE_MESSAGES = raw.types.InputPrivacyKeyVoiceMessages
    "Whether people can send you voice messages or round videos (Premium users only)."

    GIFTS = raw.types.InputPrivacyKeyStarGiftsAutoSave
    "Whether received gifts will be automatically displayed on our profile"

    NO_PAID_MESSAGES = raw.types.InputPrivacyKeyNoPaidMessages
    "Whether people who won't have to pay to send you messages"

    SAVED_MUSIC = raw.types.InputPrivacyKeySavedMusic
    "Whether people can see your saved music list"
