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

from .answer_callback_query import AnswerCallbackQuery
from .answer_inline_query import AnswerInlineQuery
from .answer_pre_checkout_query import AnswerPreCheckoutQuery
from .answer_shipping_query import AnswerShippingQuery
from .answer_web_app_query import AnswerWebAppQuery
from .create_invoice_link import CreateInvoiceLink
from .delete_bot_commands import DeleteBotCommands
from .edit_user_star_subscription import EditUserStarSubscription
from .get_bot_commands import GetBotCommands
from .get_bot_default_privileges import GetBotDefaultPrivileges
from .get_bot_info_description import GetBotInfoDescription
from .get_bot_info_short_description import GetBotInfoShortDescription
from .get_bot_name import GetBotName
from .get_chat_menu_button import GetChatMenuButton
from .get_game_high_scores import GetGameHighScores
from .get_inline_bot_results import GetInlineBotResults
from .get_owned_bots import GetOwnedBots
from .refund_star_payment import RefundStarPayment
from .request_callback_answer import RequestCallbackAnswer
from .send_game import SendGame
from .send_inline_bot_result import SendInlineBotResult
from .send_invoice import SendInvoice
from .set_bot_commands import SetBotCommands
from .set_bot_default_privileges import SetBotDefaultPrivileges
from .set_bot_info_description import SetBotInfoDescription
from .set_bot_info_short_description import SetBotInfoShortDescription
from .set_bot_name import SetBotName
from .set_chat_menu_button import SetChatMenuButton
from .set_game_score import SetGameScore


class Bots(
    AnswerCallbackQuery,
    AnswerInlineQuery,
    AnswerPreCheckoutQuery,
    AnswerShippingQuery,
    CreateInvoiceLink,
    GetInlineBotResults,
    GetOwnedBots,
    RefundStarPayment,
    RequestCallbackAnswer,
    SendInlineBotResult,
    SendInvoice,
    SendGame,
    SetGameScore,
    GetGameHighScores,
    SetBotCommands,
    GetBotCommands,
    DeleteBotCommands,
    EditUserStarSubscription,
    SetBotDefaultPrivileges,
    SetBotInfoDescription,
    SetBotInfoShortDescription,
    SetBotName,
    GetBotDefaultPrivileges,
    GetBotInfoDescription,
    GetBotInfoShortDescription,
    GetBotName,
    SetChatMenuButton,
    GetChatMenuButton,
    AnswerWebAppQuery
):
    pass
