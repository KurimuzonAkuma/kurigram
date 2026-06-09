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

from .add_chat_members import AddChatMembers
from .archive_chats import ArchiveChats
from .ban_chat_member import BanChatMember
from .create_channel import CreateChannel
from .create_folder import CreateFolder
from .create_forum_topic import CreateForumTopic
from .create_group import CreateGroup
from .create_supergroup import CreateSupergroup
from .close_forum_topic import CloseForumTopic
from .delete_channel import DeleteChannel
from .delete_folder_invite_link import DeleteFolderInviteLink
from .delete_chat_photo import DeleteChatPhoto
from .delete_all_message_reactions import DeleteAllMessageReactions
from .delete_folder import DeleteFolder
from .delete_forum_topic import DeleteForumTopic
from .delete_supergroup import DeleteSupergroup
from .delete_user_history import DeleteUserHistory
from .edit_forum_topic import EditForumTopic
from .delete_message_reaction import DeleteMessageReaction
from .create_folder_invite_link import CreateFolderInviteLink
from .get_chat import GetChat
from .get_chats_for_folder_invite_link import GetChatsForFolderInviteLink
from .get_chat_event_log import GetChatEventLog
from .get_folder_invite_links import GetFolderInviteLinks
from .get_chat_member import GetChatMember
from .get_chat_members import GetChatMembers
from .get_chat_members_count import GetChatMembersCount
from .get_chat_online_count import GetChatOnlineCount
from .get_chat_settings import GetChatSettings
from .get_similar_channels import GetSimilarChannels
from .get_suitable_discussion_chats import GetSuitableDiscussionChats
from .get_top_chats import GetTopChats
from .get_dialogs import GetDialogs
from .get_direct_messages_topics_by_id import GetDirectMessagesTopicsByID
from .get_direct_messages_topics import GetDirectMessagesTopics
from .get_dialogs_count import GetDialogsCount
from .get_folders import GetFolders
from .get_forum_topics import GetForumTopics
from .get_forum_topics_by_id import GetForumTopicsByID
from .get_personal_channels import GetPersonalChannels
from .get_send_as_chats import GetSendAsChats
from .join_chat import JoinChat
from .join_folder import JoinFolder
from .leave_chat import LeaveChat
from .leave_folder import LeaveFolder
from .mark_chat_unread import MarkChatUnread
from .pin_chat_message import PinChatMessage
from .pin_forum_topic import PinForumTopic
from .process_chat_has_protected_content_disable_request import ProcessChatHasProtectedContentDisableRequest
from .promote_chat_member import PromoteChatMember
from .restrict_chat_member import RestrictChatMember
from .set_administrator_title import SetAdministratorTitle
from .set_chat_description import SetChatDescription
from .set_chat_direct_messages_group import SetChatDirectMessagesGroup
from .set_chat_permissions import SetChatPermissions
from .set_chat_discussion_group import SetChatDiscussionGroup
from .set_chat_member_tag import SetChatMemberTag
from .set_main_profile_tab import SetMainProfileTab
from .set_chat_photo import SetChatPhoto
from .set_chat_protected_content import SetChatProtectedContent
from .set_chat_title import SetChatTitle
from .set_chat_ttl import SetChatTTL
from .set_chat_username import SetChatUsername
from .set_send_as_chat import SetSendAsChat
from .set_slow_mode import SetSlowMode
from .set_upgraded_gift_colors import SetUpgradedGiftColors
from .toggle_folder_tags import ToggleFolderTags
from .toggle_forum_topics import ToggleForumTopics
from .toggle_join_to_send import ToggleJoinToSend
from .transfer_chat_ownership import TransferChatOwnership
from .unarchive_chats import UnarchiveChats
from .unban_chat_member import UnbanChatMember
from .unpin_all_chat_messages import UnpinAllChatMessages
from .unpin_chat_message import UnpinChatMessage
from .unpin_forum_topic import UnpinForumTopic
from .update_chat_notifications import UpdateChatNotifications
from .update_color import UpdateColor
from .edit_folder import EditFolder
from .reorder_folders import ReorderFolders


class Chats(
    GetChat,
    GetChatsForFolderInviteLink,
    LeaveChat,
    LeaveFolder,
    JoinChat,
    JoinFolder,
    BanChatMember,
    UnbanChatMember,
    RestrictChatMember,
    PromoteChatMember,
    GetChatMembers,
    GetChatMember,
    SetChatPhoto,
    DeleteChatPhoto,
    DeleteAllMessageReactions,
    DeleteFolder,
    SetChatTitle,
    SetChatTTL,
    SetChatDescription,
    SetChatDirectMessagesGroup,
    PinChatMessage,
    UnpinChatMessage,
    PinForumTopic,
    ProcessChatHasProtectedContentDisableRequest,
    UnpinForumTopic,
    UpdateChatNotifications,
    UpdateColor,
    EditFolder,
    GetDialogs,
    GetDirectMessagesTopicsByID,
    GetDirectMessagesTopics,
    GetChatMembersCount,
    SetChatUsername,
    SetChatPermissions,
    SetChatDiscussionGroup,
    SetChatMemberTag,
    SetMainProfileTab,
    GetDialogsCount,
    GetFolders,
    GetForumTopics,
    GetForumTopicsByID,
    ArchiveChats,
    UnarchiveChats,
    CreateGroup,
    CreateSupergroup,
    CreateChannel,
    CreateFolder,
    ReorderFolders,
    CreateForumTopic,
    CloseForumTopic,
    AddChatMembers,
    DeleteChannel,
    DeleteFolderInviteLink,
    DeleteForumTopic,
    DeleteSupergroup,
    EditForumTopic,
    DeleteMessageReaction,
    CreateFolderInviteLink,
    GetPersonalChannels,
    SetAdministratorTitle,
    SetSlowMode,
    SetUpgradedGiftColors,
    ToggleFolderTags,
    ToggleForumTopics,
    ToggleJoinToSend,
    TransferChatOwnership,
    DeleteUserHistory,
    UnpinAllChatMessages,
    MarkChatUnread,
    GetChatEventLog,
    GetFolderInviteLinks,
    GetChatOnlineCount,
    GetChatSettings,
    GetSimilarChannels,
    GetSuitableDiscussionChats,
    GetTopChats,
    GetSendAsChats,
    SetSendAsChat,
    SetChatProtectedContent
):
    pass
