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

from .on_error import OnError
from .on_business_connection import OnBusinessConnection
from .on_business_message import OnBusinessMessage
from .on_callback_query import OnCallbackQuery
from .on_chat_boost import OnChatBoost
from .on_chat_join_request import OnChatJoinRequest
from .on_chat_member_updated import OnChatMemberUpdated
from .on_chosen_inline_result import OnChosenInlineResult
from .on_deleted_business_messages import OnDeletedBusinessMessages
from .on_deleted_messages import OnDeletedMessages
from .on_start import OnStart
from .on_stop import OnStop
from .on_connect import OnConnect
from .on_disconnect import OnDisconnect
from .on_edited_business_message import OnEditedBusinessMessage
from .on_edited_message import OnEditedMessage
from .on_inline_query import OnInlineQuery
from .on_message_reaction_count import OnMessageReactionCount
from .on_message_reaction import OnMessageReaction
from .on_message import OnMessage
from .on_poll import OnPoll
from .on_pre_checkout_query import OnPreCheckoutQuery
from .on_purchased_paid_media import OnPurchasedPaidMedia
from .on_raw_update import OnRawUpdate
from .on_shipping_query import OnShippingQuery
from .on_user_status import OnUserStatus
from .on_story import OnStory


class Decorators(
    OnError,
    OnBusinessConnection,
    OnBusinessMessage,
    OnMessage,
    OnEditedBusinessMessage,
    OnEditedMessage,
    OnDeletedBusinessMessages,
    OnDeletedMessages,
    OnCallbackQuery,
    OnChatBoost,
    OnRawUpdate,
    OnStart,
    OnStop,
    OnConnect,
    OnDisconnect,
    OnShippingQuery,
    OnUserStatus,
    OnInlineQuery,
    OnMessageReactionCount,
    OnMessageReaction,
    OnPoll,
    OnChosenInlineResult,
    OnChatMemberUpdated,
    OnChatJoinRequest,
    OnStory,
    OnPreCheckoutQuery,
    OnPurchasedPaidMedia
):
    pass
