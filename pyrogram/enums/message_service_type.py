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

from enum import auto

from .auto_name import AutoName


class MessageServiceType(AutoName):
    """Message service type enumeration used in :obj:`~pyrogram.types.Message`."""

    UNSUPPORTED = auto()
    "A message content that is not supported in the current pyrogram version"

    CUSTOM_ACTION = auto()
    "Custom action"

    NEW_CHAT_MEMBERS = auto()
    "New members join"

    LEFT_CHAT_MEMBER = auto()
    "Left chat member"

    CHAT_OWNER_LEFT = auto()
    "Chat owner left"

    CHAT_OWNER_CHANGED = auto()
    "Chat owner changed"

    NEW_CHAT_TITLE = auto()
    "New chat title"

    NEW_CHAT_PHOTO = auto()
    "New chat photo"

    DELETE_CHAT_PHOTO = auto()
    "Deleted chat photo"

    FORUM_TOPIC_CREATED = auto()
    "a new forum topic created in the chat"

    FORUM_TOPIC_CLOSED = auto()
    "a new forum topic closed in the chat"

    FORUM_TOPIC_REOPENED = auto()
    "a new forum topic reopened in the chat"

    FORUM_TOPIC_EDITED = auto()
    "a new forum topic renamed in the chat"

    GENERAL_FORUM_TOPIC_HIDDEN = auto()
    "a general forum topic hidden in the chat"

    GENERAL_FORUM_TOPIC_UNHIDDEN = auto()
    "a general forum topic unhidden in the chat"

    GROUP_CHAT_CREATED = auto()
    "Group chat created"

    CHANNEL_CHAT_CREATED = auto()
    "Channel chat created"

    SUPERGROUP_CHAT_CREATED = auto()
    "Supergroup chat created"

    MIGRATE_TO_CHAT_ID = auto()
    "Migrated to chat id"

    MIGRATE_FROM_CHAT_ID = auto()
    "Migrated from chat id"

    PINNED_MESSAGE = auto()
    "Pinned message"

    GAME_HIGH_SCORE = auto()
    "Game high score"

    GIVEAWAY_CREATED = auto()
    "Giveaway created"

    GIVEAWAY_COMPLETED = auto()
    "Giveaway completed"

    MANAGED_BOT_CREATED = auto()
    "Managed bot created"

    POLL_OPTION_ADDED = auto()
    "Poll option added"

    POLL_OPTION_DELETED = auto()
    "Poll option deleted"

    PREMIUM_GIFT_CODE = auto()
    "Gift code"

    GIFTED_PREMIUM = auto()
    "Gifted Telegram Premium"

    GIFTED_STARS = auto()
    "Gifted stars"

    GIFTED_TON = auto()
    "Gifted TON"

    VIDEO_CHAT_STARTED = auto()
    "Video chat started"

    VIDEO_CHAT_ENDED = auto()
    "Video chat ended"

    VIDEO_CHAT_SCHEDULED = auto()
    "Video chat scheduled"

    VIDEO_CHAT_MEMBERS_INVITED = auto()
    "Video chat members invited"

    PHONE_CALL_STARTED = auto()
    "Phone call started"

    PHONE_CALL_ENDED = auto()
    "Phone call ended"

    WEB_APP_DATA = auto()
    "Web app data"

    USERS_SHARED = auto()
    "Requested users"

    CHAT_SHARED = auto()
    "Requested chat"

    SUCCESSFUL_PAYMENT = auto()
    "Successful payment"

    REFUNDED_PAYMENT = auto()
    "Refunded payment"

    SUGGESTED_POST_APPROVAL_FAILED = auto()
    "Suggested post approval failed"

    SUGGESTED_POST_APPROVED = auto()
    "Suggested post approved"

    SUGGESTED_POST_DECLINED = auto()
    "Suggested post declined"

    SUGGESTED_POST_PAID = auto()
    "Suggested post paid"

    SUGGESTED_POST_REFUNDED = auto()
    "Suggested post refunded"

    SET_MESSAGE_AUTO_DELETE_TIME = auto()
    "Chat TTL changed"

    CHAT_BOOST = auto()
    "Boost applied to the chat"

    GIFT = auto()
    "Star gift"

    CONNECTED_WEBSITE = auto()
    "Connected website"

    WRITE_ACCESS_ALLOWED = auto()
    "Write access allowed"

    SCREENSHOT_TAKEN = auto()
    "Screenshot taken"

    CONTACT_REGISTERED = auto()
    "Contact registered"

    PROXIMITY_ALERT_TRIGGERED = auto()
    "Proximity alert triggered"

    HISTORY_CLEARED = auto()
    "Chat history cleared"

    SUGGEST_PROFILE_PHOTO = auto()
    "Suggest profile photo"

    SUGGEST_BIRTHDAY = auto()
    "Suggest birthday"

    CHAT_SET_BACKGROUND = auto()
    "Set chat background"

    CHAT_SET_THEME = auto()
    "Set chat theme"

    GIVEAWAY_PRIZE_STARS = auto()
    "Giveaway prize stars"

    PAID_MESSAGES_REFUNDED = auto()
    "Refunded paid messages"

    PAID_MESSAGES_PRICE_CHANGED = auto()
    "Paid messages price"

    DIRECT_MESSAGE_PRICE_CHANGED = auto()
    "Direct message price"

    CHECKLIST_TASKS_DONE = auto()
    "Checklist tasks done"

    CHECKLIST_TASKS_ADDED = auto()
    "Checklist tasks added"

    UPGRADED_GIFT_PURCHASE_OFFER = auto()
    "Upgraded gift purchase offer"

    UPGRADED_GIFT_PURCHASE_OFFER_REJECTED = auto()
    "Upgraded gift purchase offer declined"

    CHAT_HAS_PROTECTED_CONTENT_TOGGLED = auto()
    "Chat has protected content toggled"

    CHAT_HAS_PROTECTED_CONTENT_DISABLE_REQUESTED = auto()
    "Chat has protected content disable requested"
