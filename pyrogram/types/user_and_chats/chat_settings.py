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

from datetime import datetime
from typing import Optional

import pyrogram
from pyrogram import raw, types, utils

from ..object import Object


class ChatSettings(Object):
    """A list of actions that are possible when interacting with this user, to be shown as suggested actions in the chat action bar.

    Parameters:
        can_report_spam (``bool``, *optional*):
            True, if we can still report this chat for spam.

        can_add_contact (``bool``, *optional*):
            True, if we can add this user as contact.

        can_block_contact (``bool``, *optional*):
            True, if we can block this user.

        can_share_contact (``bool``, *optional*):
            True, if we can share user's contact.

        can_report_geo (``bool``, *optional*):
            True, if we can report a geogroup as irrelevant for this location.

        can_invite_members (``bool``, *optional*):
            True, if this is a recently created group chat to which new members can be invited.

        is_autoarchived (``bool``, *optional*):
            True, if this chat was automatically archived according to privacy settings and can be unarchived.

        is_business_bot_paused (``bool``, *optional*):
            True, if the business bot is currently paused.

        is_business_bot_can_reply (``bool``, *optional*):
            True, if the business bot can reply to messages.

        need_contacts_exception (``bool``, *optional*):
            True, if special exception for contacts is needed.

        request_chat_broadcast (``bool``, *optional*):
            This flag is set if request_chat_title and request_chat_date fields are set
            and the join request is related to a channel (otherwise if only the request
            fields are set, the join request is related to a chat).

        geo_distance (``int``, *optional*):
            Distance in meters between us and this chat.

        request_chat_title (``str``, *optional*):
            Title of the chat for which join request was sent.

        request_chat_date (:py:obj:`~datetime.datetime`, *optional*):
            Date when join request was sent.

        business_bot (:obj:`~pyrogram.types.User`, *optional*):
            Business bot that manages this chat.

        business_bot_manage_url (``str``, *optional*):
            Contains a deep link used to open a management menu in the business bot.

        charge_paid_message_stars (``int``, *optional*):
            Number of stars for the paid message.

        registration_date (``str``, *optional*):
            Date when the user registered on Telegram, in format MM.YYYY.

        phone_number_country_code (``str``, *optional*):
            A two-letter ISO 3166-1 alpha-2 country code based on the phone number of the user

        last_name_change_date (:py:obj:`~datetime.datetime`, *optional*):
            Date when the user's name was changed.

        last_photo_change_date (:py:obj:`~datetime.datetime`, *optional*):
            Date when the user's photo was changed.
    """

    def __init__(
        self,
        *,
        can_report_spam: Optional[bool] = None,
        can_add_contact: Optional[bool] = None,
        can_block_contact: Optional[bool] = None,
        can_share_contact: Optional[bool] = None,
        can_report_geo: Optional[bool] = None,
        can_invite_members: Optional[bool] = None,
        is_autoarchived: Optional[bool] = None,
        is_business_bot_paused: Optional[bool] = None,
        is_business_bot_can_reply: Optional[bool] = None,
        need_contacts_exception: Optional[bool] = None,
        request_chat_broadcast: Optional[bool] = None,
        geo_distance: Optional[int] = None,
        request_chat_title: Optional[str] = None,
        request_chat_date: Optional[datetime] = None,
        business_bot: Optional["types.User"] = None,
        business_bot_manage_url: Optional[str] = None,
        charge_paid_message_stars: Optional[int] = None,
        registration_date: Optional[str] = None,
        phone_number_country_code: Optional[str] = None,
        last_name_change_date: Optional[datetime] = None,
        last_photo_change_date: Optional[datetime] = None
    ):
        super().__init__()

        self.can_report_spam = can_report_spam
        self.can_add_contact = can_add_contact
        self.can_block_contact = can_block_contact
        self.can_share_contact = can_share_contact
        self.can_report_geo = can_report_geo
        self.can_invite_members = can_invite_members
        self.is_autoarchived = is_autoarchived
        self.is_business_bot_paused = is_business_bot_paused
        self.is_business_bot_can_reply = is_business_bot_can_reply
        self.need_contacts_exception = need_contacts_exception
        self.request_chat_broadcast = request_chat_broadcast
        self.geo_distance = geo_distance
        self.request_chat_title = request_chat_title
        self.request_chat_date = request_chat_date
        self.business_bot = business_bot
        self.business_bot_manage_url = business_bot_manage_url
        self.charge_paid_message_stars = charge_paid_message_stars
        self.registration_date = registration_date
        self.phone_number_country_code = phone_number_country_code
        self.last_name_change_date = last_name_change_date
        self.last_photo_change_date = last_photo_change_date

    @staticmethod
    async def _parse(client, chat_settings: "raw.types.PeerSettings", users) -> Optional["ChatSettings"]:
        if not chat_settings:
            return None

        return ChatSettings(
            can_report_spam=getattr(chat_settings, "report_spam", None),
            can_add_contact=getattr(chat_settings, "add_contact", None),
            can_block_contact=getattr(chat_settings, "block_contact", None),
            can_share_contact=getattr(chat_settings, "share_contact", None),
            can_report_geo=getattr(chat_settings, "report_geo", None),
            can_invite_members=getattr(chat_settings, "invite_members", None),
            is_autoarchived=getattr(chat_settings, "autoarchived", None),
            is_business_bot_paused=getattr(chat_settings, "business_bot_paused", None),
            is_business_bot_can_reply=getattr(chat_settings, "business_bot_can_reply", None),
            need_contacts_exception=getattr(chat_settings, "need_contacts_exception", None),
            request_chat_broadcast=getattr(chat_settings, "request_chat_broadcast", None),
            geo_distance=getattr(chat_settings, "geo_distance", None),
            request_chat_title=getattr(chat_settings, "request_chat_title", None),
            request_chat_date=utils.timestamp_to_datetime(getattr(chat_settings, "request_chat_date", None)),
            business_bot=await types.User._parse(client, users.get(getattr(chat_settings, "business_bot_id", None))),
            business_bot_manage_url=getattr(chat_settings, "business_bot_manage_url", None),
            charge_paid_message_stars=getattr(chat_settings, "charge_paid_message_stars", None),
            registration_date=getattr(chat_settings, "registration_month", None),
            phone_number_country_code=getattr(chat_settings, "phone_country", None),
            last_name_change_date=utils.timestamp_to_datetime(getattr(chat_settings, "name_change_date", None)),
            last_photo_change_date=utils.timestamp_to_datetime(getattr(chat_settings, "photo_change_date", None)),
        )
