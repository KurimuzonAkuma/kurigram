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

import html
import logging
from datetime import datetime
from typing import List, Optional, Union

import pyrogram
from pyrogram import enums, raw, types, utils

from ..object import Object
from ..update import Update

log = logging.getLogger(__name__)


class Link(str):
    HTML = "<a href={url}>{text}</a>"
    MARKDOWN = "[{text}]({url})"

    def __init__(self, url: str, text: str, style: enums.ParseMode):
        super().__init__()

        self.url = url
        self.text = text
        self.style = style

    @staticmethod
    def format(url: str, text: str, style: enums.ParseMode):
        if style == enums.ParseMode.MARKDOWN:
            fmt = Link.MARKDOWN
        else:
            fmt = Link.HTML

        return fmt.format(url=url, text=html.escape(text))

    # noinspection PyArgumentList
    def __new__(cls, url, text, style):
        return str.__new__(cls, Link.format(url, text, style))

    def __call__(self, other: str = None, *, style: str = None):
        return Link.format(self.url, other or self.text, style or self.style)

    def __str__(self):
        return Link.format(self.url, self.text, self.style)


class User(Object, Update):
    """A Telegram user or bot.

    Parameters:
        id (``int``):
            Unique identifier for this user or bot.

        is_self(``bool``, *optional*):
            True, if this user is you yourself.

        is_contact(``bool``, *optional*):
            True, if this user is in your contacts.

        is_mutual_contact(``bool``, *optional*):
            True, if you both have each other's contact.

        is_deleted(``bool``, *optional*):
            True, if this user is deleted.

        is_bot (``bool``, *optional*):
            True, if this user is a bot.

        is_restricted (``bool``, *optional*):
            True, if this user has been restricted. Bots only.
            See *restriction_reason* for details.

        is_support (``bool``, *optional*):
            True, if this user is part of the Telegram support team.

        is_premium (``bool``, *optional*):
            True, if this user is a premium user.

        is_contact_require_premium (``bool``, *optional*):
            True, if this user requires premium to send messages to him.

        is_close_friend (``bool``, *optional*):
            True, if this user is a close friend.

        is_stories_hidden (``bool``, *optional*):
            True, if this user has hidden stories.

        is_stories_unavailable (``bool``, *optional*):
            True, if this user stories is unavailable.

        is_min (``bool``, *optional*):
            True, if this user have reduced set of fields.

        verification_status (:obj:`~pyrogram.types.VerificationStatus`, *optional*):
            Information about verification status of the user.

        first_name (``str``, *optional*):
            User's or bot's first name.

        last_name (``str``, *optional*):
            User's or bot's last name.

        status (:obj:`~pyrogram.enums.UserStatus`, *optional*):
            User's last seen & online status. ``None``, for bots.

        last_online_date (:py:obj:`~datetime.datetime`, *optional*):
            Last online date of a user. Only available in case status is :obj:`~pyrogram.enums.UserStatus.OFFLINE`.

        next_offline_date (:py:obj:`~datetime.datetime`, *optional*):
            Date when a user will automatically go offline. Only available in case status is :obj:`~pyrogram.enums.UserStatus.ONLINE`.

        username (``str``, *optional*):
            User's or bot's username.

        usernames (List of :obj:`~pyrogram.types.Username`, *optional*):
            The list of user's collectible (and basic) usernames if available.

        language_code (``str``, *optional*):
            IETF language tag of the user's language.

        emoji_status (:obj:`~pyrogram.types.EmojiStatus`, *optional*):
            Emoji status.

        dc_id (``int``, *optional*):
            User's or bot's assigned DC (data center). Available only in case the user has set a public profile photo.
            Note that this information is approximate; it is based on where Telegram stores a user profile pictures and
            does not by any means tell you the user location (i.e. a user might travel far away, but will still connect
            to its assigned DC). More info at `FAQs </faq#what-are-the-ip-addresses-of-telegram-data-centers>`_.

        phone_number (``str``, *optional*):
            User's phone number.

        personal_photo (:obj:`~pyrogram.types.ChatPhoto`, *optional*):
            Personal profile photo, to be shown instead of profile photo.
            This photo isn't returned in the list of user photos.
            Suitable for downloads only.

        photo (:obj:`~pyrogram.types.ChatPhoto`, *optional*):
            User's or bot's current profile photo.
            Suitable for downloads only.

        public_photo (:obj:`~pyrogram.types.ChatPhoto`, *optional*):
            Fallback profile photo, displayed if no photo is present in photo or personal_photo, due to privacy settings.
            This photo isn't returned in the list of user photos.
            Suitable for downloads only.

        restrictions (List of :obj:`~pyrogram.types.Restriction`, *optional*):
            The list of reasons why this bot might be unavailable to some users.
            This field is available only in case *is_restricted* is True.

        reply_color (:obj:`~pyrogram.types.ChatColor`, *optional*):
            Chat reply color.

        profile_color (:obj:`~pyrogram.types.ChatColor`, *optional*):
            Chat profile color.

        added_to_attachment_menu (``bool``, *optional*):
            True, if this user added the bot to the attachment menu.

        active_users_count (``int``, *optional*):
            The number of recently (monthly) active users of the bot.

        inline_need_location (``bool``, *optional*):
            True, if the bot supports inline `user location <https://core.telegram.org/bots/inline#location-based-results>`_ requests. Returned only in get_me.

        inline_query_placeholder (``str``, *optional*):
            Placeholder for inline queries (displayed on the application input field).

        can_be_edited (``bool``, *optional*):
            True, if the current user can edit this bot's profile picture.

        can_be_added_to_attachment_menu (``bool``, *optional*):
            True, if the bot can be added to attachment or side menu.

        can_join_groups (``bool``, *optional*):
            True, if the bot can be invited to groups. Returned only in :meth:`~pyrogram.Client.get_me`.

        can_read_all_group_messages (``bool``, *optional*):
            True, if privacy mode is disabled for the bot. Returned only in :meth:`~pyrogram.Client.get_me`.

        can_connect_to_business (``bool``, *optional*):
            True, if the bot can be connected to a Telegram Business account to receive its messages.

        can_manage_bots (``bool``, *optional*):
            True, if other bots can be created to be controlled by the bot. Returned only in :meth:`~pyrogram.Client.get_me`.

        has_main_web_app (``bool``, *optional*):
            True, if the bot has a main Web App. Returned only in :meth:`~pyrogram.Client.get_me`.

        has_topics (``bool``, *optional*):
            True, if the bot has topics.

        allows_users_to_create_topics (``bool``, *optional*):
            True, if users can create and delete topics in the chat with the bot.

        paid_message_star_count (``int``, *optional*):
            Number of Telegram Stars that must be paid by user for each sent message to the user.

        settings (:obj:`~pyrogram.types.ChatSettings`, *optional*):
            Chat settings.
            Returned only in :meth:`~pyrogram.Client.get_me`.

        common_chats (``int``, *optional*):
            Number of common chats with this user.
            Returned only in :meth:`~pyrogram.Client.get_me`

        is_blocked (``bool``, *optional*):
            True, if you have blocked this user.
            Returned only in :meth:`~pyrogram.Client.get_me`

        is_phone_calls_available (``bool``, *optional*):
            True, if this user can make VoIP calls.
            Returned only in :meth:`~pyrogram.Client.get_me`

        is_phone_calls_private (``bool``, *optional*):
            True, if this user's privacy settings allow you to call them.
            Returned only in :meth:`~pyrogram.Client.get_me`

        is_video_calls_available (``bool``, *optional*):
            True, if this user can receive video calls.
            Returned only in :meth:`~pyrogram.Client.get_me`

        is_wallpaper_overridden (``bool``, *optional*):
            True, if this user has a custom wallpaper.
            Returned only in :meth:`~pyrogram.Client.get_me`

        is_translations_disabled (``bool``, *optional*):
            True, if the real-time chat translation popup should be hidden.
            Returned only in :meth:`~pyrogram.Client.get_me`

        is_pinned_stories_available (``bool``, *optional*):
            True, if this user has some pinned stories.
            Returned only in :meth:`~pyrogram.Client.get_me`

        is_blocked_my_stories_from (``bool``, *optional*):
            True, if we've blocked this user, preventing them from seeing our stories.
            Returned only in :meth:`~pyrogram.Client.get_me`

        is_read_dates_available (``bool``, *optional*):
            True, if we cannot fetch the exact read date of messages we send to this user.
            Returned only in :meth:`~pyrogram.Client.get_me`

        is_ads_enabled (``bool``, *optional*):
            True, if ads were re-enabled for the current account (only accessible to the currently logged-in user).
            Returned only in :meth:`~pyrogram.Client.get_me`

        can_pin_message (``bool``, *optional*):
            True, if the current user can pin messages in this chat.
            Returned only in :meth:`~pyrogram.Client.get_me`

        can_schedule_messages (``bool``, *optional*):
            True, if the current user can schedule messages in this chat.
            Returned only in :meth:`~pyrogram.Client.get_me`

        can_send_voice_messages (``bool``, *optional*):
            True, if the current user can send voice messages in this chat.
            Returned only in :meth:`~pyrogram.Client.get_me`

        can_view_revenue (``bool``, *optional*):
            True, if the current user can view revenue in this chat.
            Returned only in :meth:`~pyrogram.Client.get_me`

        bot_can_manage_emoji_status (``bool``, *optional*):
            True, if the bot can change your emoji status.
            Returned only in :meth:`~pyrogram.Client.get_me`

        display_gifts_button (``bool``, *optional*):
            True, if the gift button should be shown in the message input field for both participants in all chats.
            Returned only in :meth:`~pyrogram.Client.get_me`

        uses_unofficial_app (``bool``, *optional*):
            True, if the user uses an unofficial application that poses a security risk.

        bio (``str``, *optional*):
            Bio of the other party in a private chat.
            Returned only in :meth:`~pyrogram.Client.get_me`.

        pinned_message (:obj:`~pyrogram.types.Message`, *optional*):
            Pinned message, for groups, supergroups channels and own chat.
            Returned only in :meth:`~pyrogram.Client.get_me`.

        folder_id (``int``, *optional*):
            The folder identifier where the chat is located.
            Returned only in :meth:`~pyrogram.Client.get_me`.

        message_auto_delete_time (``int``, *optional*):
            The time after which all messages sent to the chat will be automatically deleted; in seconds.
            Returned only in :meth:`~pyrogram.Client.get_me`.

        theme (:obj:`~pyrogram.types.ChatTheme`, *optional*):
            Theme set for the chat.
            Returned only in :meth:`~pyrogram.Client.get_me`

        private_forward_name (``str``, *optional*):
            Anonymized text to be shown instead of the user's name on forwarded messages.
            Returned only in :meth:`~pyrogram.Client.get_me`

        chat_admin_rights (:obj:`~pyrogram.types.ChatAdministratorRights`, *optional*):
            A suggested set of administrator rights for the bot, to be shown when adding the bot as admin to a group.
            Returned only in :meth:`~pyrogram.Client.get_me`

        channel_admin_rights (:obj:`~pyrogram.types.ChatAdministratorRights`, *optional*):
            A suggested set of administrator rights for the bot, to be shown when adding the bot as admin to a channel.
            Returned only in :meth:`~pyrogram.Client.get_me`

        chat_background (:obj:`~pyrogram.types.ChatBackground`, *optional*):
            Chat wallpaper.
            Returned only in :meth:`~pyrogram.Client.get_me`

        stories (List of :obj:`~pyrogram.types.Story`, *optional*):
            The list of chat's stories if available.
            Returned only in :meth:`~pyrogram.Client.get_me`

        business_away_message (:obj:`~pyrogram.types.BusinessMessage`, *optional*):
            For private chats with business accounts, the away message of the business.
            Returned only in :meth:`~pyrogram.Client.get_me`

        business_greeting_message (:obj:`~pyrogram.types.BusinessMessage`, *optional*):
            For private chats with business accounts, the greeting message of the business.
            Returned only in :meth:`~pyrogram.Client.get_me`

        business_work_hours (:obj:`~pyrogram.types.BusinessWorkingHours`, *optional*):
            For private chats with business accounts, the working hours of the business.
            Returned only in :meth:`~pyrogram.Client.get_me`

        business_location (:obj:`~pyrogram.types.Location`, *optional*):
            For private chats with business accounts, the location of the business.
            Returned only in :meth:`~pyrogram.Client.get_me`

        business_intro (:obj:`~pyrogram.types.BusinessIntro`, *optional*):
            For private chats with business accounts, the intro of the business.
            Returned only in :meth:`~pyrogram.Client.get_me`

        birthday (:obj:`~pyrogram.types.Birthday`, *optional*):
            Information about user birthday.
            Returned only in :meth:`~pyrogram.Client.get_me`

        personal_channel (:obj:`~pyrogram.types.Chat`, *optional*):
            The personal channel linked to this chat.
            Returned only in :meth:`~pyrogram.Client.get_me`.

        personal_channel_message (:obj:`~pyrogram.types.Message`, *optional*):
            The last message in the personal channel of this chat.
            Returned only in :meth:`~pyrogram.Client.get_me`.

        gift_count (``int``, *optional*):
            Number of saved to profile gifts for channels without `can_post_messages` administrator right, otherwise, the total number of received gifts.
            Returned only in :meth:`~pyrogram.Client.get_me`.

        bot_verification (:obj:`~pyrogram.types.BotVerification`, *optional*):
            Information about bot verification.
            Returned only in :meth:`~pyrogram.Client.get_me`.

        main_profile_tab (:obj:`~pyrogram.enums.ProfileTab`, *optional*):
            The main tab chosen by the user.
            Returned only in :meth:`~pyrogram.Client.get_me`

        first_profile_audio (:obj:`~pyrogram.types.Audio`, *optional*):
            The first audio file added to the user's profile.
            Returned only in :meth:`~pyrogram.Client.get_me`

        rating (:obj:`~pyrogram.types.UserRating`, *optional*):
            Description of the current rating of the user.

        pending_rating (:obj:`~pyrogram.types.UserRating`, *optional*):
            Description of the rating of the user after the next change.

        pending_rating_date (:py:obj:`~datetime.datetime`, *optional*):
            Date when rating of the user will change to pending_rating.

        accepted_gift_types (:obj:`~pyrogram.types.AcceptedGiftTypes`, *optional*):
            Information about gifts that can be received by the user.
            Returned only in :meth:`~pyrogram.Client.get_me`

        note (:obj:`~pyrogram.types.FormattedText`, *optional*):
            Note added to the user's contact.

        supports_guest_queries (``bool``, *optional*):
            True, if the bot supports guest queries from chats it is not a member of.
            Returned only in :meth:`~pyrogram.Client.get_me`

        raw (:obj:`~pyrogram.raw.base.User` | :obj:`~pyrogram.raw.base.UserStatus`, *optional*):
            The raw user or user status object, as received from the Telegram API.

        mention (``str``, *property*):
            Generate a text mention for this user.
            You can use ``user.mention()`` to mention the user using their first name (styled using html), or
            ``user.mention("another name")`` for a custom name. To choose a different style
            ("html" or "md"/"markdown") use ``user.mention(style="md")``.

        full_name (``str``, *property*):
            Full name of the other party in a private chat, for private chats and bots.
    """

    def __init__(
        self,
        *,
        client: "pyrogram.Client" = None,
        id: int,
        is_self: Optional[bool] = None,
        is_contact: Optional[bool] = None,
        is_mutual_contact: Optional[bool] = None,
        is_deleted: Optional[bool] = None,
        is_bot: Optional[bool] = None,
        is_restricted: Optional[bool] = None,
        is_support: Optional[bool] = None,
        is_premium: Optional[bool] = None,
        is_contact_require_premium: Optional[bool] = None,
        is_close_friend: Optional[bool] = None,
        is_stories_hidden: Optional[bool] = None,
        is_stories_unavailable: Optional[bool] = None,
        is_min: Optional[bool] = None,
        verification_status: Optional["types.VerificationStatus"] = None,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        status: Optional["enums.UserStatus"] = None,
        last_online_date: Optional[datetime] = None,
        next_offline_date: Optional[datetime] = None,
        username: Optional[str] = None,
        usernames: Optional[List["types.Username"]] = None,
        language_code: Optional[str] = None,
        emoji_status: Optional["types.EmojiStatus"] = None,
        dc_id: Optional[int] = None,
        phone_number: Optional[str] = None,
        personal_photo: Optional["types.ChatPhoto"] = None,
        photo: Optional["types.ChatPhoto"] = None,
        public_photo: Optional["types.ChatPhoto"] = None,
        restrictions: Optional[List["types.Restriction"]] = None,
        reply_color: Optional["types.ChatColor"] = None,
        profile_color: Optional["types.ChatColor"] = None,
        added_to_attachment_menu: Optional[bool] = None,
        active_users_count: Optional[int] = None,
        inline_need_location: Optional[bool] = None,
        inline_query_placeholder: Optional[str] = None,
        can_be_edited: Optional[bool] = None,
        can_be_added_to_attachment_menu: Optional[bool] = None,
        can_join_groups: Optional[bool] = None,
        can_read_all_group_messages: Optional[bool] = None,
        can_connect_to_business: Optional[bool] = None,
        can_manage_bots: Optional[bool] = None,
        has_main_web_app: Optional[bool] = None,
        has_topics: Optional[bool] = None,
        allows_users_to_create_topics: Optional[bool] = None,
        paid_message_star_count: Optional[int] = None,
        settings: Optional["types.ChatSettings"] = None,
        common_chats: Optional[int] = None,
        is_blocked: Optional[bool] = None,
        is_phone_calls_available: Optional[bool] = None,
        is_phone_calls_private: Optional[bool] = None,
        is_video_calls_available: Optional[bool] = None,
        is_wallpaper_overridden: Optional[bool] = None,
        is_translations_disabled: Optional[bool] = None,
        is_pinned_stories_available: Optional[bool] = None,
        is_blocked_my_stories_from: Optional[bool] = None,
        is_read_dates_available: Optional[bool] = None,
        is_ads_enabled: Optional[bool] = None,
        can_pin_message: Optional[bool] = None,
        can_schedule_messages: Optional[bool] = None,
        can_send_voice_messages: Optional[bool] = None,
        can_view_revenue: Optional[bool] = None,
        bot_can_manage_emoji_status: Optional[bool] = None,
        display_gifts_button: Optional[bool] = None,
        uses_unofficial_app: Optional[bool] = None,
        bio: Optional[str] = None,
        pinned_message: Optional["types.Message"] = None,
        folder_id: Optional[int] = None,
        message_auto_delete_time: Optional[int] = None,
        theme: Optional[str] = None,
        private_forward_name: Optional[str] = None,
        chat_admin_rights: Optional["types.ChatAdministratorRights"] = None,
        channel_admin_rights: Optional["types.ChatAdministratorRights"] = None,
        chat_background: Optional["types.ChatBackground"] = None,
        stories: Optional[List["types.Story"]] = None,
        business_away_message: Optional["types.BusinessMessage"] = None,
        business_greeting_message: Optional["types.BusinessMessage"] = None,
        business_work_hours: Optional["types.BusinessMessage"] = None,
        business_location: Optional["types.Location"] = None,
        business_intro: Optional["types.BusinessIntro"] = None,
        birthday: Optional["types.Birthday"] = None,
        personal_channel: Optional["types.Chat"] = None,
        personal_channel_message: Optional["types.Message"] = None,
        gift_count: Optional[int] = None,
        bot_verification: Optional["types.BotVerification"] = None,
        main_profile_tab: Optional["enums.ProfileTab"] = None,
        first_profile_audio: Optional["types.Audio"] = None,
        rating: Optional["types.UserRating"] = None,
        pending_rating: Optional["types.UserRating"] = None,
        pending_rating_date: Optional[datetime] = None,
        accepted_gift_types: Optional["types.AcceptedGiftTypes"] = None,
        note: Optional["types.FormattedText"] = None,
        supports_guest_queries: Optional[bool] = None,
        raw: Optional[Union["raw.base.User", "raw.base.UserStatus"]] = None
    ):
        super().__init__(client)

        self.id = id
        self.is_self = is_self
        self.is_contact = is_contact
        self.is_mutual_contact = is_mutual_contact
        self.is_deleted = is_deleted
        self.is_bot = is_bot
        self.is_restricted = is_restricted
        self.is_support = is_support
        self.is_premium = is_premium
        self.is_contact_require_premium = is_contact_require_premium
        self.is_close_friend = is_close_friend
        self.is_stories_hidden = is_stories_hidden
        self.is_stories_unavailable = is_stories_unavailable
        self.verification_status = verification_status
        self.is_min = is_min
        self.first_name = first_name
        self.last_name = last_name
        self.status = status
        self.last_online_date = last_online_date
        self.next_offline_date = next_offline_date
        self.username = username
        self.usernames = usernames
        self.language_code = language_code
        self.emoji_status = emoji_status
        self.dc_id = dc_id
        self.phone_number = phone_number
        self.personal_photo = personal_photo
        self.photo = photo
        self.public_photo = public_photo
        self.restrictions = restrictions
        self.reply_color = reply_color
        self.profile_color = profile_color
        self.added_to_attachment_menu = added_to_attachment_menu
        self.active_users_count = active_users_count
        self.inline_need_location = inline_need_location
        self.inline_query_placeholder = inline_query_placeholder
        self.can_be_edited = can_be_edited
        self.can_be_added_to_attachment_menu = can_be_added_to_attachment_menu
        self.can_join_groups = can_join_groups
        self.can_read_all_group_messages = can_read_all_group_messages
        self.can_connect_to_business = can_connect_to_business
        self.can_manage_bots = can_manage_bots
        self.has_main_web_app = has_main_web_app
        self.has_topics = has_topics
        self.allows_users_to_create_topics = allows_users_to_create_topics
        self.paid_message_star_count = paid_message_star_count
        self.settings = settings
        self.common_chats = common_chats
        self.is_blocked = is_blocked
        self.is_phone_calls_available = is_phone_calls_available
        self.is_phone_calls_private = is_phone_calls_private
        self.is_video_calls_available = is_video_calls_available
        self.is_wallpaper_overridden = is_wallpaper_overridden
        self.is_translations_disabled = is_translations_disabled
        self.is_pinned_stories_available = is_pinned_stories_available
        self.is_blocked_my_stories_from = is_blocked_my_stories_from
        self.is_read_dates_available = is_read_dates_available
        self.is_ads_enabled = is_ads_enabled
        self.can_pin_message = can_pin_message
        self.can_schedule_messages = can_schedule_messages
        self.can_send_voice_messages = can_send_voice_messages
        self.can_view_revenue = can_view_revenue
        self.bot_can_manage_emoji_status = bot_can_manage_emoji_status
        self.display_gifts_button = display_gifts_button
        self.uses_unofficial_app = uses_unofficial_app
        self.bio = bio
        self.pinned_message = pinned_message
        self.folder_id = folder_id
        self.message_auto_delete_time = message_auto_delete_time
        self.theme = theme
        self.private_forward_name = private_forward_name
        self.chat_admin_rights = chat_admin_rights
        self.channel_admin_rights = channel_admin_rights
        self.chat_background = chat_background
        self.stories = stories
        self.business_away_message = business_away_message
        self.business_greeting_message = business_greeting_message
        self.business_work_hours = business_work_hours
        self.business_location = business_location
        self.business_intro = business_intro
        self.birthday = birthday
        self.personal_channel = personal_channel
        self.personal_channel_message = personal_channel_message
        self.gift_count = gift_count
        self.bot_verification = bot_verification
        self.main_profile_tab = main_profile_tab
        self.first_profile_audio = first_profile_audio
        self.rating = rating
        self.pending_rating = pending_rating
        self.pending_rating_date = pending_rating_date
        self.accepted_gift_types = accepted_gift_types
        self.note = note
        self.supports_guest_queries = supports_guest_queries
        self.raw = raw

    @property
    def full_name(self) -> str:
        return " ".join(filter(None, [self.first_name, self.last_name])) or None

    @property
    def mention(self):
        return Link(
            f"tg://user?id={self.id}",
            self.first_name or "Deleted Account",
            self._client.parse_mode
        )

    # region Deprecated
    # TODO: Remove later

    @property
    def is_verified(self) -> Optional[bool]:
        log.warning(
            "`user.is_verified` is deprecated and will be removed in future updates. Use `user.verification_status.is_verified` instead."
        )
        return getattr(self.verification_status, "is_verified", None)

    @property
    def is_scam(self) -> Optional[bool]:
        log.warning(
            "`user.is_scam` is deprecated and will be removed in future updates. Use `user.verification_status.is_scam` instead."
        )
        return getattr(self.verification_status, "is_scam", None)

    @property
    def is_fake(self) -> Optional[bool]:
        log.warning(
            "`user.is_fake` is deprecated and will be removed in future updates. Use `user.verification_status.is_fake` instead."
        )
        return getattr(self.verification_status, "is_fake", None)

    # endregion

    @staticmethod
    def _parse(client, user: "raw.base.User") -> Optional["User"]:
        if not isinstance(user, raw.types.User):
            return None

        return User(
            id=user.id,
            is_self=user.is_self,
            is_contact=user.contact,
            is_mutual_contact=user.mutual_contact,
            is_deleted=user.deleted,
            is_bot=user.bot,
            is_restricted=user.restricted,
            is_support=user.support,
            is_premium=user.premium,
            is_contact_require_premium=user.contact_require_premium,
            is_close_friend=user.close_friend,
            is_stories_hidden=user.stories_hidden,
            is_stories_unavailable=user.stories_unavailable,
            is_min=user.min,
            verification_status=types.VerificationStatus._parse(user),
            first_name=user.first_name,
            last_name=user.last_name,
            **User._parse_status(user.status, user.bot),
            username=user.username or (user.usernames[0].username if user.usernames else None),
            usernames=types.List([types.Username._parse(r) for r in user.usernames]) or None,
            language_code=user.lang_code,
            emoji_status=types.EmojiStatus._parse(client, user.emoji_status),
            dc_id=getattr(user.photo, "dc_id", None),
            phone_number=user.phone,
            photo=types.ChatPhoto._parse(client, user.photo, user.id, user.access_hash),
            restrictions=types.List([types.Restriction._parse(r) for r in user.restriction_reason]) or None,
            reply_color=types.ChatColor._parse(user.color),
            profile_color=types.ChatColor._parse_profile_color(user.profile_color),
            added_to_attachment_menu=user.attach_menu_enabled,
            active_users_count=user.bot_active_users,
            inline_need_location=user.bot_inline_geo,
            inline_query_placeholder=user.bot_inline_placeholder,
            can_be_edited=user.bot_can_edit,
            can_be_added_to_attachment_menu=user.bot_attach_menu,
            can_join_groups=user.bot_nochats,
            can_read_all_group_messages=user.bot_chat_history,
            can_connect_to_business=user.bot_business,
            can_manage_bots=user.bot_can_manage_bots,
            has_main_web_app=user.bot_has_main_app,
            has_topics=user.bot_forum_view,
            allows_users_to_create_topics=user.bot_forum_can_manage_topics,
            paid_message_star_count=user.send_paid_messages_stars,
            supports_guest_queries=user.bot_guestchat,
            raw=user,
            client=client
        )

    @staticmethod
    async def _parse_full(client, user: "raw.types.UserFull", users: dict, chats: dict) -> Optional["User"]:
        parsed_user = User._parse(client, users[user.id])
        parsed_user.raw = user

        parsed_user.settings = types.ChatSettings._parse(client, user.settings, users)
        # parsed_user.notify_settings = user.notify_settings
        parsed_user.common_chats = user.common_chats_count
        parsed_user.is_blocked = user.blocked
        parsed_user.is_phone_calls_available = user.phone_calls_available
        parsed_user.is_phone_calls_private = user.phone_calls_private
        parsed_user.can_pin_message = user.can_pin_message
        parsed_user.can_schedule_messages = user.has_scheduled
        parsed_user.is_video_calls_available = user.video_calls_available
        parsed_user.can_send_voice_messages = not user.voice_messages_forbidden
        parsed_user.is_translations_disabled = user.translations_disabled
        parsed_user.is_pinned_stories_available = user.stories_pinned_available
        parsed_user.is_blocked_my_stories_from = user.blocked_my_stories_from
        parsed_user.is_wallpaper_overridden = user.wallpaper_overridden
        parsed_user.is_read_dates_available = not user.read_dates_private
        parsed_user.is_ads_enabled = user.sponsored_enabled
        parsed_user.can_view_revenue = user.can_view_revenue
        parsed_user.bot_can_manage_emoji_status = user.bot_can_manage_emoji_status
        parsed_user.display_gifts_button = user.display_gifts_button
        parsed_user.uses_unofficial_app = user.unofficial_security_risk
        parsed_user.bio = user.about or None
        parsed_user.personal_photo = types.ChatPhoto._parse(client, user.personal_photo, users[user.id].id, users[user.id].access_hash)
        # parsed_user.photo = types.ChatPhoto._parse(client, user.profile_photo, users[user.id].id, users[user.id].access_hash)
        parsed_user.public_photo = types.ChatPhoto._parse(client, user.fallback_photo, users[user.id].id, users[user.id].access_hash)
        # parsed_user.bot_info = user.bot_info
        # parsed_user.bot_forum_view

        if user.pinned_msg_id:
            parsed_user.pinned_message = await client.get_messages(chat_id=parsed_user.id, pinned=True)

        parsed_user.folder_id = user.folder_id
        parsed_user.message_auto_delete_time = user.ttl_period
        parsed_user.theme = await types.ChatTheme._parse(client, user.theme)
        parsed_user.private_forward_name = user.private_forward_name
        parsed_user.bot_group_admin_rights = types.ChatAdministratorRights._parse(user.bot_group_admin_rights)
        parsed_user.bot_broadcast_admin_rights = types.ChatAdministratorRights._parse(user.bot_broadcast_admin_rights)
        parsed_user.chat_background = types.ChatBackground._parse(client, user.wallpaper)

        if user.stories:
            parsed_user.stories = types.List(
                [
                    await types.Story._parse(
                        client, story, user.stories.peer, users, chats
                    )
                    for story in user.stories.stories
                ]
            ) or None

        parsed_user.business_work_hours = types.BusinessWorkingHours._parse(user.business_work_hours)
        parsed_user.business_location = types.Location._parse_business(user.business_location)
        parsed_user.business_greeting_message = types.BusinessMessage._parse(client, user.business_greeting_message, users)
        parsed_user.business_away_message = types.BusinessMessage._parse(client, user.business_away_message, users)
        parsed_user.business_intro = await types.BusinessIntro._parse(client, user.business_intro)
        parsed_user.birthday = types.Birthday._parse(user.birthday)

        if user.personal_channel_id:
            parsed_user.personal_channel = types.Chat._parse_channel_chat(client, chats[user.personal_channel_id])
            parsed_user.personal_channel_message = await client.get_messages(
                chat_id=parsed_user.personal_channel.id,
                message_ids=user.personal_channel_message
            )

        parsed_user.gift_count = user.stargifts_count
        # parsed_user.starref_program = user.starref_program
        parsed_user.bot_verification = types.BotVerification._parse(
            client,
            user.bot_verification,
            users
        )
        parsed_user.main_profile_tab = enums.ProfileTab(type(user.main_tab)) if user.main_tab else None

        if user.saved_music:
            attributes = {type(i): i for i in user.saved_music.attributes}

            if raw.types.DocumentAttributeAudio in attributes:
                parsed_user.first_profile_audio = types.Audio._parse(
                    client,
                    user.saved_music,
                    attributes[raw.types.DocumentAttributeAudio],
                    getattr(
                        attributes.get(raw.types.DocumentAttributeFilename, None),
                        "file_name",
                        None,
                    ),
                )

        parsed_user.rating = types.UserRating._parse(user.stars_rating)
        parsed_user.pending_rating = types.UserRating._parse(user.stars_my_pending_rating)
        parsed_user.pending_rating_date = utils.timestamp_to_datetime(user.stars_my_pending_rating_date)
        parsed_user.accepted_gift_types = types.AcceptedGiftTypes._parse(user.disallowed_gifts)
        parsed_user.note = types.FormattedText._parse(client, user.note)

        return parsed_user

    @staticmethod
    def _parse_status(user_status: "raw.base.UserStatus", is_bot: bool = False):
        if isinstance(user_status, raw.types.UserStatusOnline):
            status, date = enums.UserStatus.ONLINE, user_status.expires
        elif isinstance(user_status, raw.types.UserStatusOffline):
            status, date = enums.UserStatus.OFFLINE, user_status.was_online
        elif isinstance(user_status, raw.types.UserStatusRecently):
            status, date = enums.UserStatus.RECENTLY, None
        elif isinstance(user_status, raw.types.UserStatusLastWeek):
            status, date = enums.UserStatus.LAST_WEEK, None
        elif isinstance(user_status, raw.types.UserStatusLastMonth):
            status, date = enums.UserStatus.LAST_MONTH, None
        else:
            status, date = enums.UserStatus.LONG_AGO, None

        last_online_date = None
        next_offline_date = None

        if is_bot:
            status = None

        if status == enums.UserStatus.ONLINE:
            next_offline_date = utils.timestamp_to_datetime(date)

        if status == enums.UserStatus.OFFLINE:
            last_online_date = utils.timestamp_to_datetime(date)

        return {
            "status": status,
            "last_online_date": last_online_date,
            "next_offline_date": next_offline_date
        }

    @staticmethod
    def _parse_user_status(client, user_status: "raw.types.UpdateUserStatus"):
        return User(
            id=user_status.user_id,
            **User._parse_status(user_status.status),
            raw=user_status,
            client=client
        )

    async def archive(self):
        """Bound method *archive* of :obj:`~pyrogram.types.User`.

        Use as a shortcut for:

        .. code-block:: python

            await client.archive_chats(123456789)

        Example:
            .. code-block:: python

               await user.archive()

        Returns:
            True on success.

        Raises:
            RPCError: In case of a Telegram RPC error.
        """

        return await self._client.archive_chats(self.id)

    async def unarchive(self):
        """Bound method *unarchive* of :obj:`~pyrogram.types.User`.

        Use as a shortcut for:

        .. code-block:: python

            await client.unarchive_chats(123456789)

        Example:
            .. code-block:: python

                await user.unarchive()

        Returns:
            True on success.

        Raises:
            RPCError: In case of a Telegram RPC error.
        """

        return await self._client.unarchive_chats(self.id)

    async def block(self):
        """Bound method *block* of :obj:`~pyrogram.types.User`.

        Use as a shortcut for:

        .. code-block:: python

            await client.block_user(123456789)

        Example:
            .. code-block:: python

                await user.block()

        Returns:
            True on success.

        Raises:
            RPCError: In case of a Telegram RPC error.
        """

        return await self._client.block_user(self.id)

    async def unblock(self):
        """Bound method *unblock* of :obj:`~pyrogram.types.User`.

        Use as a shortcut for:

        .. code-block:: python

            await client.unblock_user(123456789)

        Example:
            .. code-block:: python

                await user.unblock()

        Returns:
            True on success.

        Raises:
            RPCError: In case of a Telegram RPC error.
        """

        return await self._client.unblock_user(self.id)

    async def get_common_chats(self):
        """Bound method *get_common_chats* of :obj:`~pyrogram.types.User`.

        Use as a shortcut for:

        .. code-block:: python

            await client.get_common_chats(123456789)

        Example:
            .. code-block:: python

                await user.get_common_chats()

        Returns:
            List of :obj:`~pyrogram.types.Chat`: On success, a list of the common chats is returned.

        Raises:
            RPCError: In case of a Telegram RPC error.
        """

        return await self._client.get_common_chats(self.id)
