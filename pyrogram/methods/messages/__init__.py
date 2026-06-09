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

from .add_checklist_tasks import AddChecklistTasks
from .add_poll_option import AddPollOption
from .add_to_gifs import AddToGifs
from .approve_suggested_post import ApproveSuggestedPost
from .compose_text_with_ai import ComposeTextWithAI
from .copy_media_group import CopyMediaGroup
from .copy_message import CopyMessage
from .decline_suggested_post import DeclineSuggestedPost
from .delete_chat_history import DeleteChatHistory
from .delete_direct_messages_chat_topic_history import DeleteDirectMessagesChatTopicHistory
from .delete_messages import DeleteMessages
from .delete_poll_option import DeletePollOption
from .download_media import DownloadMedia
from .edit_inline_caption import EditInlineCaption
from .edit_inline_media import EditInlineMedia
from .edit_inline_reply_markup import EditInlineReplyMarkup
from .edit_inline_text import EditInlineText
from .edit_message_caption import EditMessageCaption
from .edit_message_checklist import EditMessageChecklist
from .edit_message_media import EditMessageMedia
from .edit_message_reply_markup import EditMessageReplyMarkup
from .edit_message_text import EditMessageText
from .fix_text_with_ai import FixTextWithAI
from .forward_media_group import ForwardMediaGroup
from .forward_messages import ForwardMessages
from .get_available_effects import GetAvailableEffects
from .get_chat_history import GetChatHistory
from .get_chat_history_count import GetChatHistoryCount
from .get_custom_emoji_stickers import GetCustomEmojiStickers
from .get_direct_messages_chat_topic_history import GetDirectMessagesChatTopicHistory
from .get_discussion_message import GetDiscussionMessage
from .get_discussion_replies import GetDiscussionReplies
from .get_discussion_replies_count import GetDiscussionRepliesCount
from .get_main_web_app import GetMainWebApp
from .get_media_group import GetMediaGroup
from .get_messages import GetMessages
from .get_scheduled_messages import GetScheduledMessages
from .get_stickers import GetStickers
from .get_user_personal_chat_messages import GetUserPersonalChatMessages
from .get_web_app_link_url import GetWebAppLinkUrl
from .get_web_app_url import GetWebAppUrl
from .mark_checklist_tasks_as_done import MarkChecklistTasksAsDone
from .open_web_app import OpenWebApp
from .read_chat_history import ReadChatHistory
from .read_mentions import ReadMentions
from .read_reactions import ReadReactions
from .retract_vote import RetractVote
from .search_global import SearchGlobal
from .search_global_count import SearchGlobalCount
from .search_messages import SearchMessages
from .search_messages_count import SearchMessagesCount
from .search_posts import SearchPosts
from .search_posts_count import SearchPostsCount
from .send_animation import SendAnimation
from .send_audio import SendAudio
from .send_cached_media import SendCachedMedia
from .send_chat_action import SendChatAction
from .send_checklist import SendChecklist
from .send_contact import SendContact
from .send_dice import SendDice
from .send_document import SendDocument
from .send_location import SendLocation
from .send_media_group import SendMediaGroup
from .send_message_draft import SendMessageDraft
from .send_message import SendMessage
from .send_paid_media import SendPaidMedia
from .send_paid_reaction import SendPaidReaction
from .send_photo import SendPhoto
from .send_poll import SendPoll
from .send_reaction import SendReaction
from .send_screenshot_notification import SendScreenshotNotification
from .send_sticker import SendSticker
from .send_venue import SendVenue
from .send_video import SendVideo
from .send_video_note import SendVideoNote
from .send_voice import SendVoice
from .send_web_page import SendWebPage
from .set_direct_messages_chat_topic_is_marked_as_unread import SetDirectMessagesChatTopicIsMarkedAsUnread
from .start_bot import StartBot
from .stop_poll import StopPoll
from .stream_media import StreamMedia
from .summarize_message import SummarizeMessage
from .translate_message_text import TranslateMessageText
from .translate_text import TranslateText
from .view_messages import ViewMessages
from .vote_poll import VotePoll


class Messages(
    AddChecklistTasks,
    AddPollOption,
    AddToGifs,
    ApproveSuggestedPost,
    ComposeTextWithAI,
    DeclineSuggestedPost,
    DeleteMessages,
    DeletePollOption,
    EditMessageCaption,
    EditMessageChecklist,
    EditMessageReplyMarkup,
    EditMessageMedia,
    EditMessageText,
    FixTextWithAI,
    ForwardMediaGroup,
    ForwardMessages,
    GetAvailableEffects,
    GetMediaGroup,
    GetMessages,
    GetScheduledMessages,
    GetStickers,
    GetUserPersonalChatMessages,
    GetWebAppLinkUrl,
    GetWebAppUrl,
    MarkChecklistTasksAsDone,
    OpenWebApp,
    SendAudio,
    SendChatAction,
    SendChecklist,
    SendContact,
    SendDocument,
    SendAnimation,
    SendLocation,
    SendMediaGroup,
    SendMessageDraft,
    SendMessage,
    SendPaidMedia,
    SendPaidReaction,
    SendPhoto,
    SendScreenshotNotification,
    SendSticker,
    SendVenue,
    SendVideo,
    SendVideoNote,
    SendVoice,
    SendPoll,
    SendWebPage,
    SetDirectMessagesChatTopicIsMarkedAsUnread,
    ViewMessages,
    VotePoll,
    StartBot,
    StopPoll,
    RetractVote,
    DownloadMedia,
    GetChatHistory,
    SendCachedMedia,
    GetChatHistoryCount,
    ReadChatHistory,
    ReadMentions,
    ReadReactions,
    EditInlineText,
    EditInlineCaption,
    EditInlineMedia,
    EditInlineReplyMarkup,
    SendDice,
    SearchMessages,
    SearchGlobal,
    CopyMessage,
    DeleteChatHistory,
    DeleteDirectMessagesChatTopicHistory,
    CopyMediaGroup,
    SearchMessagesCount,
    SearchPosts,
    SearchPostsCount,
    SearchGlobalCount,
    GetDiscussionMessage,
    SendReaction,
    GetDiscussionReplies,
    GetDiscussionRepliesCount,
    GetMainWebApp,
    StreamMedia,
    SummarizeMessage,
    TranslateMessageText,
    TranslateText,
    GetCustomEmojiStickers,
    GetDirectMessagesChatTopicHistory
):
    pass
