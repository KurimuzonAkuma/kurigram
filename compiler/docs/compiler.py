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

import ast
import os
import re
import shutil
from dataclasses import dataclass
from typing import Literal

HOME = "compiler/docs"
DESTINATION = "docs/source/telegram"
PYROGRAM_API_DEST = "docs/source/api"

FUNCTIONS_PATH = "pyrogram/raw/functions"
TYPES_PATH = "pyrogram/raw/types"
BASE_PATH = "pyrogram/raw/base"

FUNCTIONS_BASE = "functions"
TYPES_BASE = "types"
BASE_BASE = "base"


def snek(s: str):
    s = re.sub(r"(.)([A-Z][a-z]+)", r"\1_\2", s)
    return re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", s).lower()


def _extract_union_name(node: ast.AST) -> str | None:
    """Extract the name of a variable that is assigned a Union type.

    :param node: The AST node to extract the variable name from.
    :return: The variable name if it is assigned a Union type, otherwise None.

    >>> import ast
    >>> parsed_ast = ast.parse("User = Union[raw.types.UserEmpty]")
    >>> _extract_union_name(parsed_ast.body[0])
    'User'
    """

    # Check if the assigned value is a Union type
    if isinstance(node, ast.Assign) and isinstance(node.value, ast.Subscript):
        if isinstance(node.value.value, ast.Name) and node.value.value.id == "Union":
            # Extract variable name
            if isinstance(node.targets[0], ast.Name):
                return node.targets[0].id  # Variable name


def _extract_class_name(node: ast.AST) -> str | None:
    """Extract the name of a class.

    :param node: The AST node to extract the class name from.
    :return: The class name if it is a class, otherwise None.

    >>> import ast
    >>> parsed_ast = ast.parse("class User: pass")
    >>> _extract_class_name(parsed_ast.body[0])
    'User'
    """

    if isinstance(node, ast.ClassDef):
        return node.name  # Class name


NodeType = Literal["class", "union"]


@dataclass
class NodeInfo:
    name: str
    type: NodeType


def parse_node_info(node: ast.AST) -> NodeInfo | None:
    """Parse an AST node and extract the class or variable name."""
    class_name = _extract_class_name(node)
    if class_name:
        return NodeInfo(name=class_name, type="class")

    union_name = _extract_union_name(node)
    if union_name:
        return NodeInfo(name=union_name, type="union")

    return None


def generate(source_path, base):
    all_entities = {}

    def build(path, level=0):
        last = path.split("/")[-1]

        for i in os.listdir(path):
            try:
                if not i.startswith("__"):
                    build("/".join([path, i]), level=level + 1)
            except NotADirectoryError:
                with open(path + "/" + i, encoding="utf-8") as f:
                    p = ast.parse(f.read())

                for node in ast.walk(p):
                    node_info = parse_node_info(node)
                    if node_info:
                        break
                else:
                    continue

                full_path = os.path.basename(path) + "/" + snek(node_info.name).replace("_", "-") + ".rst"

                if level:
                    full_path = base + "/" + full_path

                namespace = path.split("/")[-1]
                if namespace in ["base", "types", "functions"]:
                    namespace = ""

                full_name = f"{(namespace + '.') if namespace else ''}{node_info.name}"

                os.makedirs(os.path.dirname(DESTINATION + "/" + full_path), exist_ok=True)

                with open(DESTINATION + "/" + full_path, "w", encoding="utf-8") as f:
                    title_markup = "=" * len(full_name)
                    full_class_path = "pyrogram.raw.{}".format(
                        ".".join(full_path.split("/")[:-1]) + "." + node_info.name
                    )

                    if node_info.type == "class":
                        directive_type = "autoclass"
                        directive_suffix = "()"
                        directive_option = "members"
                    elif node_info.type == "union":
                        directive_type = "autodata"
                        directive_suffix = ""
                        directive_option = "annotation"
                    else:
                        raise ValueError(f"Unknown node type: `{node_info.type}`")

                    f.write(
                        page_template.format(
                            title=full_name,
                            title_markup=title_markup,
                            directive_type=directive_type,
                            full_class_path=full_class_path,
                            directive_suffix=directive_suffix,
                            directive_option=directive_option,
                        )
                    )

                if last not in all_entities:
                    all_entities[last] = []

                all_entities[last].append(node_info.name)

    build(source_path)

    for k, v in sorted(all_entities.items()):
        v = sorted(v)
        entities = []

        for i in v:
            entities.append(f'{i} <{snek(i).replace("_", "-")}>')

        if k != base:
            inner_path = base + "/" + k + "/index" + ".rst"
            module = "pyrogram.raw.{}.{}".format(base, k)
        else:
            for i in sorted(list(all_entities), reverse=True):
                if i != base:
                    entities.insert(0, "{0}/index".format(i))

            inner_path = base + "/index" + ".rst"
            module = "pyrogram.raw.{}".format(base)

        with open(DESTINATION + "/" + inner_path, "w", encoding="utf-8") as f:
            if k == base:
                f.write(":tocdepth: 1\n\n")
                k = "Raw " + k

            f.write(
                toctree.format(
                    title=k.title(),
                    title_markup="=" * len(k),
                    module=module,
                    entities="\n    ".join(entities)
                )
            )

            f.write("\n")


def pyrogram_api():
    def get_title_list(s: str) -> list:
        return [i.strip() for i in [j.strip() for j in s.split("\n") if j] if i]

    # Methods

    categories = dict(  # noqa: C408
        utilities="""
        Utilities
            start
            stop
            run
            restart
            add_handler
            remove_handler
            stop_transmission
            export_session_string
            set_parse_mode
            set_dc
            get_dc_option
            get_session
            get_file
        """,
        messages="""
        Messages
            send_message
            forward_media_group
            forward_messages
            copy_message
            copy_media_group
            send_photo
            send_audio
            send_document
            send_screenshot_notification
            send_sticker
            send_video
            send_animation
            send_voice
            send_video_note
            send_media_group
            send_message_draft
            send_location
            send_venue
            send_contact
            send_cached_media
            send_reaction
            edit_message_text
            fix_text_with_ai
            edit_message_caption
            edit_message_checklist
            edit_message_media
            edit_message_reply_markup
            edit_inline_text
            edit_inline_caption
            edit_inline_media
            edit_inline_reply_markup
            send_chat_action
            send_checklist
            delete_messages
            get_available_effects
            get_messages
            get_scheduled_messages
            get_stickers
            get_user_personal_chat_messages
            get_web_app_link_url
            get_web_app_url
            mark_checklist_tasks_as_done
            open_web_app
            get_media_group
            get_chat_history
            get_chat_history_count
            read_mentions
            read_reactions
            read_chat_history
            send_poll
            view_messages
            vote_poll
            stop_poll
            retract_vote
            send_dice
            search_messages
            search_messages_count
            search_posts
            search_posts_count
            search_global
            search_global_count
            download_media
            stream_media
            translate_message_text
            translate_text
            get_discussion_message
            get_discussion_replies
            get_discussion_replies_count
            get_main_web_app
            get_custom_emoji_stickers
            get_direct_messages_chat_topic_history
            delete_direct_messages_chat_topic_history
            set_direct_messages_chat_topic_is_marked_as_unread
            start_bot
            delete_chat_history
            send_paid_media
            send_paid_reaction
            add_to_gifs
            approve_suggested_post
            compose_text_with_ai
            decline_suggested_post
            add_checklist_tasks
            add_poll_option
            delete_poll_option
            summarize_message
        """,
        folders="""
        Folders
            check_chat_folder_invite_link
        """,
        chats="""
        Chats
            join_chat
            leave_chat
            ban_chat_member
            unban_chat_member
            restrict_chat_member
            promote_chat_member
            set_administrator_title
            set_chat_photo
            delete_chat_photo
            delete_message_reaction
            delete_all_message_reactions
            set_chat_title
            set_chat_description
            set_chat_direct_messages_group
            set_chat_permissions
            pin_chat_message
            unpin_chat_message
            pin_forum_topic
            process_chat_has_protected_content_disable_request
            unpin_forum_topic
            unpin_all_chat_messages
            get_chat
            get_chat_member
            get_chat_members
            get_chat_members_count
            get_dialogs
            get_dialogs_count
            get_direct_messages_topics_by_id
            get_direct_messages_topics
            set_chat_username
            archive_chats
            unarchive_chats
            add_chat_members
            create_channel
            create_group
            create_supergroup
            delete_channel
            delete_folder_invite_link
            get_folder_invite_links
            delete_supergroup
            delete_user_history
            set_slow_mode
            mark_chat_unread
            get_chat_event_log
            get_chat_online_count
            get_send_as_chats
            set_send_as_chat
            set_chat_protected_content
            close_forum_topic
            create_forum_topic
            delete_forum_topic
            edit_forum_topic
            get_forum_topics
            get_forum_topics_by_id
            update_color
            set_upgraded_gift_colors
            update_chat_notifications
            toggle_forum_topics
            create_folder_invite_link
            get_chats_for_folder_invite_link
            get_folders
            create_folder
            delete_folder
            reorder_folders
            edit_folder
            get_similar_channels
            join_folder
            leave_folder
            toggle_join_to_send
            toggle_folder_tags
            set_chat_ttl
            get_personal_channels
            get_chat_settings
            transfer_chat_ownership
            get_suitable_discussion_chats
            get_top_chats
            set_chat_discussion_group
            set_chat_member_tag
            set_main_profile_tab
        """,
        users="""
        Users
            get_me
            get_users
            get_chat_photos
            get_chat_audios
            get_chat_photos_count
            get_chat_audios_count
            set_profile_photo
            set_personal_channel
            delete_profile_photos
            set_username
            update_profile
            block_user
            unblock_user
            get_common_chats
            get_default_emoji_statuses
            set_emoji_status
            update_status
            check_username
            update_birthday
        """,
        invite_links="""
        Invite Links
            get_chat_invite_link
            export_chat_invite_link
            create_chat_invite_link
            edit_chat_invite_link
            revoke_chat_invite_link
            delete_chat_invite_link
            get_chat_invite_link_joiners
            get_chat_invite_link_joiners_count
            get_chat_admin_invite_links
            get_chat_admin_invite_links_count
            get_chat_admins_with_invite_links
            get_chat_join_requests
            delete_chat_admin_invite_links
            approve_chat_join_request
            approve_all_chat_join_requests
            decline_chat_join_request
            decline_all_chat_join_requests
        """,
        contacts="""
        Contacts
            add_contact
            delete_contacts
            import_contacts
            get_blocked_message_senders
            get_contacts
            get_contacts_count
            search_contacts
            set_contact_note
        """,
        payments="""
        Payments
            apply_gift_code
            buy_gift_upgrade
            check_gift_code
            convert_gift_to_stars
            get_available_gifts
            get_chat_gifts
            get_gift_auction_state
            get_chat_gifts_count
            add_collection_gifts
            create_gift_collection
            delete_gift_collection
            drop_gift_original_details
            edit_star_subscription
            get_gift_collections
            remove_collection_gifts
            reorder_collection_gifts
            reorder_gift_collections
            reuse_star_subscription
            set_gift_collection_name
            get_gift_upgrade_preview
            get_gift_upgrade_variants
            get_gifts_for_crafting
            craft_gift
            get_payment_form
            get_stars_balance
            get_ton_balance
            get_upgraded_gift_value_info
            get_upgraded_gift
            gift_premium_with_stars
            hide_gift
            increase_gift_auction_bid
            place_gift_auction_bid
            search_gifts_for_resale
            send_gift
            send_payment_form
            send_resold_gift
            set_gift_resale_price
            set_pinned_gifts
            show_gift
            suggest_birthday
            transfer_gift
            upgrade_gift
            process_gift_purchase_offer
            send_gift_purchase_offer
        """,
        phone="""
        Phone
            get_call_members
        """,
        password="""
        Password
            enable_cloud_password
            change_cloud_password
            remove_cloud_password
        """,
        bots="""
        Bots
            get_inline_bot_results
            send_inline_bot_result
            get_managed_bot_access_settings
            set_managed_bot_access_settings
            send_invoice
            answer_callback_query
            answer_guest_query
            answer_inline_query
            request_callback_answer
            send_game
            set_game_score
            get_game_high_scores
            set_bot_commands
            get_bot_commands
            delete_bot_commands
            edit_user_star_subscription
            set_bot_default_privileges
            get_bot_default_privileges
            set_chat_menu_button
            get_chat_menu_button
            answer_web_app_query
            check_bot_username
            create_bot
            answer_pre_checkout_query
            answer_shipping_query
            create_invoice_link
            refund_star_payment
            set_bot_info_description
            get_bot_info_description
            set_bot_info_short_description
            get_bot_info_short_description
            set_bot_name
            get_bot_name
            get_managed_bot_token
            replace_managed_bot_token
            get_owned_bots
        """,
        business="""
        Business
            delete_business_messages
            get_business_account_gifts
            get_business_account_star_balance
            get_business_connection
            transfer_business_account_stars
        """,
        authorization="""
        Authorization
            connect
            disconnect
            initialize
            terminate
            send_phone_number_code
            resend_phone_number_code
            sign_in
            sign_in_bot
            sign_up
            get_password_hint
            check_password
            change_phone_number
            send_recovery_code
            recover_password
            accept_terms_of_service
            log_out
            get_active_sessions
            reset_session
            reset_sessions
        """,
        advanced="""
        Advanced
            invoke
            recover_gaps
            resolve_peer
            save_file
        """,
        stories="""
        Stories
            can_post_stories
            copy_story
            delete_stories
            edit_story_caption
            edit_story_media
            edit_story_privacy
            forward_story
            get_all_stories
            get_chat_stories
            get_pinned_stories
            get_archived_stories
            get_stories
            hide_chat_stories
            show_chat_stories
            view_stories
            pin_chat_stories
            unpin_chat_stories
            read_chat_stories
            send_story
            enable_stealth_mode
            get_story_views
        """,
        premium="""
        Premium
            apply_boost
            get_boosts
            get_boosts_status
        """,
        account="""
        Account
            add_profile_audio
            remove_profile_audio
            set_profile_audio_position
            get_account_ttl
            set_account_ttl
            set_privacy
            get_privacy
            set_global_privacy_settings
            set_inactive_session_ttl
            get_global_privacy_settings
        """
    )

    root = PYROGRAM_API_DEST + "/methods"

    shutil.rmtree(root, ignore_errors=True)
    os.mkdir(root)

    with open(HOME + "/template/methods.rst") as f:
        template = f.read()

    with open(root + "/index.rst", "w") as f:
        fmt_keys = {}

        for k, v in categories.items():
            name, *methods = get_title_list(v)
            fmt_keys.update({k: "\n    ".join("{0} <{0}>".format(m) for m in methods)})

            for method in methods:
                with open(root + "/{}.rst".format(method), "w") as f2:
                    title = "{}()".format(method)

                    f2.write(title + "\n" + "=" * len(title) + "\n\n")
                    f2.write(".. automethod:: pyrogram.Client.{}()".format(method))

            functions = ["idle", "compose"]

            for func in functions:
                with open(root + "/{}.rst".format(func), "w") as f2:
                    title = "{}()".format(func)

                    f2.write(title + "\n" + "=" * len(title) + "\n\n")
                    f2.write(".. autofunction:: pyrogram.{}()".format(func))

        f.write(template.format(**fmt_keys))

    # Types

    categories = dict(
        users_chats="""
        Users & Chats
            AcceptedGiftTypes
            Birthday
            BusinessConnection
            BusinessIntro
            BusinessRecipients
            BusinessWeeklyOpen
            BusinessWorkingHours
            User
            Username
            VerificationStatus
            Chat
            ChatPhoto
            ChatMember
            ChatPermissions
            ChatAdministratorRights
            ChatInviteLink
            ChatAdminWithInviteLinks
            ChatEvent
            ChatEventFilter
            ChatMemberUpdated
            ChatJoinRequest
            ChatJoiner
            Dialog
            Restriction
            EmojiStatus
            FailedToAddMember
            Folder
            GroupCallMember
            ChatColor
            FoundContacts
            PrivacyRule
            StoriesStealthMode
            UserRating
            BotVerification
            BusinessBotRights
            ChatSettings
            GlobalPrivacySettings
            HistoryCleared
            ChatFolderInviteLinkInfo
        """,
        messages_media="""
        Messages & Media
            BusinessMessage
            Message
            MessageEntity
            MessageOriginChannel
            MessageOriginChat
            MessageOriginHiddenUser
            MessageOriginImport
            MessageOriginUser
            MessageOrigin
            Photo
            LivePhoto
            PollOptionAdded
            PollOptionDeleted
            Thumbnail
            StrippedThumbnail
            Audio
            AvailableEffect
            Document
            ExternalReplyInfo
            FactCheck
            FormattedText
            ForumTopic
            ForumTopicClosed
            ForumTopicCreated
            ForumTopicEdited
            ForumTopicReopened
            GeneralForumTopicHidden
            GeneralForumTopicUnhidden
            Animation
            Video
            Voice
            VideoNote
            Contact
            CraftGiftResult
            CraftGiftResultSuccess
            CraftGiftResultFail
            Location
            ManagedBotCreated
            MaskPosition
            MediaArea
            MessageContent
            Venue
            Sticker
            Game
            WebPage
            Poll
            ProximityAlertTriggered
            PollOption
            Dice
            Reaction
            RestrictionReason
            Gift
            VideoChatScheduled
            VideoChatStarted
            VideoChatEnded
            VideoChatMembersInvited
            PhoneCallStarted
            PhoneCallEnded
            WebAppData
            MessageReactions
            ChatReactions
            Story
            MyBoost
            BoostsStatus
            Giveaway
            InputChecklistTask
            GiveawayCreated
            GiveawayPrizeStars
            GiveawayCompleted
            GiveawayWinners
            Invoice
            LinkPreviewOptions
            GiftCollection
            PremiumGiftCode
            GiftPurchaseLimit
            GiftResaleParameters
            GiftResalePrice
            GiftResalePriceStar
            GiftResalePriceTon
            GiftUpgradePreview
            GiftUpgradePrice
            GiftUpgradeVariants
            CheckedGiftCode
            ChecklistTask
            ChecklistTasksAdded
            ChecklistTasksDone
            Checklist
            RefundedPayment
            ReplyParameters
            SuccessfulPayment
            SuggestedPostParameters
            SuggestedPostInfo
            SuggestedPostPaid
            SuggestedPostPrice
            SuggestedPostPriceStar
            SuggestedPostPriceTon
            SuggestedPostApprovalFailed
            SuggestedPostApproved
            SuggestedPostDeclined
            SuggestedPostRefunded
            TextQuote
            PaidMediaInfo
            PaidMediaPreview
            PaidMessagesRefunded
            PaidReactor
            PaidMessagesPriceChanged
            DirectMessagePriceChanged
            DirectMessagesTopic
            PaymentForm
            PaymentOption
            SavedCredentials
            PaymentResult
            ChatBoost
            ChatOwnerChanged
            ChatOwnerLeft
            ChatHasProtectedContentToggled
            ChatHasProtectedContentDisableRequested
            ContactRegistered
            ScreenshotTaken
            StarAmount
            WriteAccessAllowed
            GiftAttribute
            StoryView
            GiftedPremium
            ChatBackground
            ChatTheme
            GiftedStars
            GiftedTon
            UpgradedGiftValueInfo
            UpgradedGiftAttributeId
            UpgradedGiftPurchaseOffer
            UpgradedGiftPurchaseOfferRejected
            UpgradedGiftAttributeIdModel
            UpgradedGiftAttributeIdSymbol
            UpgradedGiftAttributeIdBackdrop
            UpgradedGiftAttributeRarity
            UpgradedGiftAttributeRarityPerMille
            UpgradedGiftAttributeRarityUncommon
            UpgradedGiftAttributeRarityRare
            UpgradedGiftAttributeRarityEpic
            UpgradedGiftAttributeRarityLegendary
            UpgradedGiftOriginalDetails
            InputChatPhoto
            InputChatPhotoPrevious
            InputChatPhotoStatic
            InputChatPhotoAnimation
            AuctionBid
            AuctionRound
            AuctionState
            AuctionStateActive
            AuctionStateFinished
            GiftAuctionState
            GiftAuction
        """,
        bot_keyboards="""
        Bot keyboards
            ReplyKeyboardMarkup
            KeyboardButton
            ReplyKeyboardRemove
            SentGuestMessage
            InlineKeyboardMarkup
            InlineKeyboardButton
            LoginUrl
            ForceReply
            CallbackQuery
            GameHighScore
            CallbackGame
            WebAppInfo
            MenuButton
            MenuButtonCommands
            MenuButtonWebApp
            MenuButtonDefault
            SentWebAppMessage
            KeyboardButtonRequestChat
            KeyboardButtonRequestManagedBot
            KeyboardButtonRequestUsers
            KeyboardButtonPollType
            ManagedBotUpdated
            OrderInfo
            PreCheckoutQuery
            ShippingAddress
            ShippingQuery
            MessageReactionUpdated
            MessageReactionCountUpdated
            ChatBoostUpdated
            ShippingOption
            PurchasedPaidMedia
            ChatShared
            UsersShared
        """,
        bot_commands="""
        Bot commands
            BotAccessSettings
            BotCommand
            BotCommandScope
            BotCommandScopeDefault
            BotCommandScopeAllPrivateChats
            BotCommandScopeAllGroupChats
            BotCommandScopeAllChatAdministrators
            BotCommandScopeChat
            BotCommandScopeChatAdministrators
            BotCommandScopeChatMember
        """,
        input_content="""
        Input Content
            InputChecklist
            InputContactMessageContent
            InputCredentials
            InputCredentialsApplePay
            InputCredentialsGooglePay
            InputCredentialsNew
            InputCredentialsSaved
            InputInvoice
            InputInvoiceMessage
            InputInvoiceMessageContent
            InputInvoiceName
            InputLocationMessageContent
            InputMedia
            InputMediaAnimation
            InputMediaAudio
            InputMediaDocument
            InputMediaLocation
            InputMediaVenue
            InputMediaPhoto
            InputMediaLivePhoto
            InputMediaVideo
            InputMediaSticker
            InputMessageContent
            InputPhoneContact
            InputPollOption
            InputPollMedia
            InputPollOptionMedia
            InputPrivacyRule
            InputPrivacyRuleAllowAll
            InputPrivacyRuleAllowBots
            InputPrivacyRuleAllowChats
            InputPrivacyRuleAllowCloseFriends
            InputPrivacyRuleAllowContacts
            InputPrivacyRuleAllowPremium
            InputPrivacyRuleAllowUsers
            InputPrivacyRuleDisallowAll
            InputPrivacyRuleDisallowBots
            InputPrivacyRuleDisallowChats
            InputPrivacyRuleDisallowContacts
            InputPrivacyRuleDisallowUsers
            InputTextMessageContent
            InputVenueMessageContent
        """,
        inline_mode="""
        Inline Mode
            InlineQuery
            InlineQueryResult
            InlineQueryResultCachedAudio
            InlineQueryResultCachedDocument
            InlineQueryResultCachedAnimation
            InlineQueryResultCachedPhoto
            InlineQueryResultCachedSticker
            InlineQueryResultCachedVideo
            InlineQueryResultCachedVoice
            InlineQueryResultArticle
            InlineQueryResultAudio
            InlineQueryResultContact
            InlineQueryResultDocument
            InlineQueryResultAnimation
            InlineQueryResultLocation
            InlineQueryResultPhoto
            InlineQueryResultVenue
            InlineQueryResultVideo
            InlineQueryResultVoice
            ChosenInlineResult
        """,
        authorization="""
        Authorization
            ActiveSession
            ActiveSessions
            FirebaseAuthenticationSettings
            FirebaseAuthenticationSettingsAndroid
            FirebaseAuthenticationSettingsIos
            PhoneNumberAuthenticationSettings
            SentCode
            TermsOfService
        """
    )

    root = PYROGRAM_API_DEST + "/types"

    shutil.rmtree(root, ignore_errors=True)
    os.mkdir(root)

    with open(HOME + "/template/types.rst") as f:
        template = f.read()

    with open(root + "/index.rst", "w") as f:
        fmt_keys = {}

        for k, v in categories.items():
            name, *types = get_title_list(v)

            fmt_keys.update({k: "\n    ".join(types)})

            # noinspection PyShadowingBuiltins
            for type in types:
                with open(root + "/{}.rst".format(type), "w") as f2:
                    title = "{}".format(type)

                    f2.write(title + "\n" + "=" * len(title) + "\n\n")
                    f2.write(".. autoclass:: pyrogram.types.{}()\n".format(type))

        f.write(template.format(**fmt_keys))

    # Bound Methods

    categories = dict(
        message="""
        Message
            Message.reply_animation
            Message.answer_animation
            Message.reply_audio
            Message.answer_audio
            Message.reply_contact
            Message.answer_contact
            Message.reply_document
            Message.answer_document
            Message.reply_game
            Message.answer_game
            Message.reply_invoice
            Message.answer_invoice
            Message.reply_location
            Message.answer_location
            Message.reply_media_group
            Message.answer_media_group
            Message.reply
            Message.reply_text
            Message.answer
            Message.reply_photo
            Message.answer_photo
            Message.reply_poll
            Message.answer_poll
            Message.reply_dice
            Message.answer_dice
            Message.reply_sticker
            Message.answer_sticker
            Message.reply_venue
            Message.answer_venue
            Message.reply_video
            Message.answer_video
            Message.reply_video_note
            Message.answer_video_note
            Message.reply_voice
            Message.answer_voice
            Message.reply_paid_media
            Message.answer_paid_media
            Message.reply_cached_media
            Message.answer_cached_media
            Message.get_media_group
            Message.reply_chat_action
            Message.reply_inline_bot_result
            Message.answer_inline_bot_result
            Message.reply_checklist
            Message.answer_checklist
            Message.edit_text
            Message.edit
            Message.edit_caption
            Message.edit_media
            Message.edit_checklist
            Message.edit_reply_markup
            Message.edit_live_location
            Message.stop_live_location
            Message.forward
            Message.copy
            Message.copy_media_group
            Message.delete
            Message.click
            Message.react
            Message.retract_vote
            Message.download
            Message.vote
            Message.pin
            Message.unpin
            Message.read
            Message.view
            Message.pay
            Message.accept_gift_purchase_offer
            Message.reject_gift_purchase_offer
            Message.summarize
        """,
        chat="""
        Chat
            Chat.archive
            Chat.unarchive
            Chat.set_title
            Chat.set_description
            Chat.set_photo
            Chat.set_ttl
            Chat.ban_member
            Chat.unban_member
            Chat.restrict_member
            Chat.promote_member
            Chat.join
            Chat.leave
            Chat.export_invite_link
            Chat.get_member
            Chat.get_members
            Chat.add_members
            Chat.mark_unread
            Chat.set_protected_content
            Chat.unpin_all_messages
            Chat.mute
            Chat.unmute
        """,
        user="""
        User
            User.archive
            User.unarchive
            User.block
            User.unblock
            User.get_common_chats
        """,
        callback_query="""
        Callback Query
            CallbackQuery.answer
            CallbackQuery.edit_message_text
            CallbackQuery.edit_message_caption
            CallbackQuery.edit_message_media
            CallbackQuery.edit_message_reply_markup
        """,
        inline_query="""
        InlineQuery
            InlineQuery.answer
        """,
        pre_checkout_query="""
        PreCheckoutQuery
            PreCheckoutQuery.answer
        """,
        shipping_query="""
        ShippingQuery
            ShippingQuery.answer
        """,
        chat_join_request="""
        ChatJoinRequest
            ChatJoinRequest.approve
            ChatJoinRequest.decline
        """,
        story="""
        Story
            Story.reply
            Story.reply_text
            Story.reply_animation
            Story.reply_audio
            Story.reply_cached_media
            Story.reply_media_group
            Story.reply_photo
            Story.reply_sticker
            Story.reply_video
            Story.reply_video_note
            Story.reply_voice
            Story.copy
            Story.delete
            Story.edit_media
            Story.edit_caption
            Story.edit_privacy
            Story.react
            Story.forward
            Story.download
            Story.read
            Story.view
        """,
        folder="""
        Folder
            Folder.delete
            Folder.edit
            Folder.include_chat
            Folder.exclude_chat
            Folder.update_color
            Folder.pin_chat
            Folder.remove_chat
            Folder.create_invite_link
        """,
        active_session="""
        ActiveSession
            ActiveSession.reset
        """,
        gift="""
        Gift
            Gift.show
            Gift.hide
            Gift.convert
            Gift.upgrade
            Gift.transfer
            Gift.wear
            Gift.buy
            Gift.send
            Gift.get_auction_state
            Gift.send_purchase_offer
        """,
        animation="""
        Animation
            Animation.add_to_gifs
        """
    )

    root = PYROGRAM_API_DEST + "/bound-methods"

    shutil.rmtree(root, ignore_errors=True)
    os.mkdir(root)

    with open(HOME + "/template/bound-methods.rst") as f:
        template = f.read()

    with open(root + "/index.rst", "w") as f:
        fmt_keys = {}

        for k, v in categories.items():
            name, *bound_methods = get_title_list(v)

            fmt_keys.update({"{}_hlist".format(k): "\n    ".join("- :meth:`~{}`".format(bm) for bm in bound_methods)})

            fmt_keys.update(
                {"{}_toctree".format(k): "\n    ".join("{} <{}>".format(bm.split(".")[1], bm) for bm in bound_methods)})

            # noinspection PyShadowingBuiltins
            for bm in bound_methods:
                with open(root + "/{}.rst".format(bm), "w") as f2:
                    title = "{}()".format(bm)

                    f2.write(title + "\n" + "=" * len(title) + "\n\n")
                    f2.write(".. automethod:: pyrogram.types.{}()".format(bm))

        f.write(template.format(**fmt_keys))


    # Enumerations

    categories = dict(
        enums="""
        Enumerations
            BlockList
            BusinessSchedule
            ButtonStyle
            ChatAction
            ChatEventAction
            ChatJoinType
            ChatMemberStatus
            ChatMembersFilter
            ChatType
            ClientPlatform
            FolderColor
            MessageEntityType
            MessageMediaType
            MessageOriginType
            MessageServiceType
            MessagesFilter
            NextCodeType
            PaidReactionPrivacy
            ParseMode
            PhoneCallDiscardReason
            PhoneNumberCodeType
            PollType
            PrivacyKey
            ProfileColor
            ProfileTab
            ReplyColor
            SentCodeType
            StoriesPrivacyRules
            UserStatus
            UpgradedGiftOrigin
            GiftAttributeType
            MediaAreaType
            PrivacyRuleType
            GiftForResaleOrder
            GiftPurchaseOfferState
            GiftType
            PaymentFormType
            StickerType
            MaskPointType
            SuggestedPostRefundReason
            SuggestedPostState
            TopChatCategory
        """,
    )

    root = PYROGRAM_API_DEST + "/enums"

    shutil.rmtree(root, ignore_errors=True)
    os.mkdir(root)

    with open(HOME + "/template/enums.rst") as f:
        template = f.read()

    with open(root + "/cleanup.html", "w") as f:
        f.write("""<script>
  document
    .querySelectorAll("em.property")
    .forEach((elem, i) => i !== 0 ? elem.remove() : true)

  document
    .querySelectorAll("a.headerlink")
    .forEach((elem, i) => [0, 1].includes(i) ? true : elem.remove())
</script>""")

    with open(root + "/index.rst", "w") as f:
        fmt_keys = {}

        for k, v in categories.items():
            name, *enums = get_title_list(v)

            fmt_keys.update({"{}_hlist".format(k): "\n    ".join("{}".format(enum) for enum in enums)})

            fmt_keys.update(
                {"{}_toctree".format(k): "\n    ".join("{}".format(enum) for enum in enums)})

            # noinspection PyShadowingBuiltins
            for enum in enums:
                with open(root + "/{}.rst".format(enum), "w") as f2:
                    title = "{}".format(enum)

                    f2.write(title + "\n" + "=" * len(title) + "\n\n")
                    f2.write(".. autoclass:: pyrogram.enums.{}()".format(enum))
                    f2.write("\n    :members:\n")

                    f2.write("\n.. raw:: html\n    :file: ./cleanup.html\n")

        f.write(template.format(**fmt_keys))


def start():
    global page_template
    global toctree

    shutil.rmtree(DESTINATION, ignore_errors=True)

    with open(HOME + "/template/page.txt", encoding="utf-8") as f:
        page_template = f.read()

    with open(HOME + "/template/toctree.txt", encoding="utf-8") as f:
        toctree = f.read()

    generate(TYPES_PATH, TYPES_BASE)
    generate(FUNCTIONS_PATH, FUNCTIONS_BASE)
    generate(BASE_PATH, BASE_BASE)
    pyrogram_api()


if "__main__" == __name__:
    FUNCTIONS_PATH = "../../pyrogram/raw/functions"
    TYPES_PATH = "../../pyrogram/raw/types"
    BASE_PATH = "../../pyrogram/raw/base"
    HOME = "."
    DESTINATION = "../../docs/source/telegram"
    PYROGRAM_API_DEST = "../../docs/source/api"

    start()
