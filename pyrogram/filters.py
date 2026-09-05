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

import inspect
import re
from typing import Callable, Final, FrozenSet, List, Optional, Pattern, Tuple, Type, Union

import pyrogram
from pyrogram import enums
from pyrogram.types import (
    BusinessConnection,
    CallbackQuery,
    Chat,
    ChatBoostUpdated,
    ChatJoinRequest,
    ChatMemberUpdated,
    ChosenInlineResult,
    InlineKeyboardMarkup,
    InlineQuery,
    ManagedBotUpdated,
    Message,
    MessageGenerationStopped,
    MessageReactionCountUpdated,
    MessageReactionUpdated,
    PreCheckoutQuery,
    PurchasedPaidMedia,
    ReplyKeyboardMarkup,
    ShippingQuery,
    Story,
    Update,
    User,
)


class Filter:
    async def __call__(self, client: "pyrogram.Client", update: Update):
        raise NotImplementedError

    def __invert__(self):
        return InvertFilter(self)

    def __and__(self, other):
        return AndFilter(self, other)

    def __or__(self, other):
        return OrFilter(self, other)


class InvertFilter(Filter):
    def __init__(self, base):
        self.base = base

    async def __call__(self, client: "pyrogram.Client", update: Update):
        if inspect.iscoroutinefunction(self.base.__call__):
            x = await self.base(client, update)
        else:
            x = await client.loop.run_in_executor(
                client.executor,
                self.base,
                client, update
            )

        return not x


class AndFilter(Filter):
    def __init__(self, base, other):
        self.base = base
        self.other = other

    async def __call__(self, client: "pyrogram.Client", update: Update):
        if inspect.iscoroutinefunction(self.base.__call__):
            x = await self.base(client, update)
        else:
            x = await client.loop.run_in_executor(
                client.executor,
                self.base,
                client, update
            )

        # short circuit
        if not x:
            return False

        if inspect.iscoroutinefunction(self.other.__call__):
            y = await self.other(client, update)
        else:
            y = await client.loop.run_in_executor(
                client.executor,
                self.other,
                client, update
            )

        return x and y


class OrFilter(Filter):
    def __init__(self, base, other):
        self.base = base
        self.other = other

    async def __call__(self, client: "pyrogram.Client", update: Update):
        if inspect.iscoroutinefunction(self.base.__call__):
            x = await self.base(client, update)
        else:
            x = await client.loop.run_in_executor(
                client.executor,
                self.base,
                client, update
            )

        # short circuit
        if x:
            return True

        if inspect.iscoroutinefunction(self.other.__call__):
            y = await self.other(client, update)
        else:
            y = await client.loop.run_in_executor(
                client.executor,
                self.other,
                client, update
            )

        return x or y


CUSTOM_FILTER_NAME: Final[str] = "CustomFilter"

# Aliases for the client account itself, the same pair `resolve_peer` accepts.
# `__init__` stores `_ME`, but the container is public and `filters.user().add("self")`
# skips it, so membership goes against the aliases rather than against the stored one.
_ME: Final[str] = "me"
_SELF: Final[str] = "self"
_ME_ALIASES: Final[FrozenSet[str]] = frozenset({_ME, _SELF})


# `Update` declares none of these (an inline query happens in no chat, a poll update
#  has no sender), so each field names the types that carry it. Kept in sync by
#  `test_the_filters_name_every_update_type_that_carries_the_field`.
_WITH_A_SENDER: Final[Tuple[Type[Update], ...]] = (
    CallbackQuery,
    ChatJoinRequest,
    ChatMemberUpdated,
    ChosenInlineResult,
    InlineQuery,
    Message,
    PreCheckoutQuery,
    PurchasedPaidMedia,
    ShippingQuery,
    Story,
)

_WITH_A_CHAT: Final[Tuple[Type[Update], ...]] = (
    CallbackQuery,
    ChatBoostUpdated,
    ChatJoinRequest,
    ChatMemberUpdated,
    Message,
    MessageGenerationStopped,
    MessageReactionCountUpdated,
    MessageReactionUpdated,
    Story,
)

_WITH_A_SENDER_CHAT: Final[Tuple[Type[Update], ...]] = (Message, Story)

_CAN_BE_OUTGOING: Final[Tuple[Type[Update], ...]] = (Message, Story)

# Three more shapes that the tuples above cannot express: the attribute is there, but not
#  under the name the tuples read.
#
#  `UpdateUserStatus` is parsed into the `User` whose status changed and nothing else
#  (`User._parse_user_status`), so that update *is* its own sender; `MessageReactionUpdated`,
#  `BusinessConnection` and `ManagedBotUpdated` spell the sender `user`, and the first also
#  spells the anonymous one `actor_chat`; `ChatBoostUpdated` keeps the booster one level
#  down, in `boost.from_user`.
#
#  Reading them here rather than renaming the attributes leaves the public API untouched.
_IS_ITS_OWN_SENDER: Final[Tuple[Type[Update], ...]] = (User,)

_WITH_A_SENDER_NAMED_USER: Final[Tuple[Type[Update], ...]] = (
    BusinessConnection,
    ManagedBotUpdated,
    MessageReactionUpdated,
)

_WITH_A_SENDER_CHAT_NAMED_ACTOR_CHAT: Final[Tuple[Type[Update], ...]] = (MessageReactionUpdated,)

_WITH_A_BOOSTER: Final[Tuple[Type[Update], ...]] = (ChatBoostUpdated,)


def _sender_of(update: Update) -> Optional[User]:
    if isinstance(update, _IS_ITS_OWN_SENDER):
        return update

    if isinstance(update, _WITH_A_SENDER_NAMED_USER):
        return update.user

    if isinstance(update, _WITH_A_BOOSTER):
        return update.boost.from_user if update.boost else None

    return update.from_user if isinstance(update, _WITH_A_SENDER) else None


def _chat_of(update: Update) -> Optional[Chat]:
    return update.chat if isinstance(update, _WITH_A_CHAT) else None


def _sender_chat_of(update: Update) -> Optional[Chat]:
    if isinstance(update, _WITH_A_SENDER_CHAT):
        return update.sender_chat

    if isinstance(update, _WITH_A_SENDER_CHAT_NAMED_ACTOR_CHAT):
        return update.actor_chat

    # A callback query carries no sender chat of its own, but the message the button sits
    #  under does, by the same route `business`, `linked_channel` and `topic` take below.
    message = _message_of(update)
    return message.sender_chat if message else None


def _is_outgoing(update: Update) -> bool:
    return bool(update.outgoing) if isinstance(update, _CAN_BE_OUTGOING) else False


# `business_connection_id`, `forward_origin` and `topic` live on `Message` alone, so the
#  filters that read them cannot take the field off the update the way the ones above do.
#  They go through the message the update is about instead, which is the same message the
#  user is looking at when a button under it is pressed.
_WITH_A_MESSAGE: Final[Tuple[Type[Update], ...]] = (CallbackQuery,)


def _message_of(update: Update) -> Optional[Message]:
    if isinstance(update, Message):
        return update

    return update.message if isinstance(update, _WITH_A_MESSAGE) else None


def create(func: Callable, name: Optional[str] = None, **kwargs) -> Filter:
    """Easily create a custom filter.

    Custom filters give you extra control over which updates are allowed or not to be processed by your handlers.

    Parameters:
        func (``Callable``):
            A function that accepts three positional arguments *(filter, client, update)* and returns a boolean: True if the
            update should be handled, False otherwise.
            The *filter* argument refers to the filter itself and can be used to access keyword arguments (read below).
            The *client* argument refers to the :obj:`~pyrogram.Client` that received the update.
            The *update* argument type will vary depending on which `Handler <handlers>`_ is coming from.
            For example, in a :obj:`~pyrogram.handlers.MessageHandler` the *update* argument will be a :obj:`~pyrogram.types.Message`; in a :obj:`~pyrogram.handlers.CallbackQueryHandler` the *update* will be a :obj:`~pyrogram.types.CallbackQuery`.
            Your function body can then access the incoming update attributes and decide whether to allow it or not.

        name (``str``, *optional*):
            Your filter's name. Can be anything you like.
            Defaults to "CustomFilter".

        **kwargs (``any``, *optional*):
            Any keyword argument you would like to pass. Useful when creating parameterized custom filters, such as
            :meth:`~pyrogram.filters.command` or :meth:`~pyrogram.filters.regex`.
    """
    return type(
        name or func.__name__ or CUSTOM_FILTER_NAME,
        (Filter,),
        {"__call__": func, **kwargs}
    )()


# region all_filter
async def all_filter(_, __, ___):
    return True


all = create(all_filter)
"""Filter all messages."""


# endregion

# region me_filter
async def me_filter(_, __, update: Update):
    sender = _sender_of(update)
    return bool(sender and sender.is_self or _is_outgoing(update))


me = create(me_filter)
"""Filter updates generated by you yourself."""


# endregion

# region bot_filter
async def bot_filter(_, __, update: Update):
    sender = _sender_of(update)
    return bool(sender and sender.is_bot)


bot = create(bot_filter)
"""Filter updates coming from bots."""


# endregion

# region sender_chat_filter
async def sender_chat_filter(_, __, update: Update):
    return bool(_sender_chat_of(update))


sender_chat = create(sender_chat_filter)
"""Filter updates coming from sender chat."""


# endregion

# region incoming_filter
async def incoming_filter(_, __, update: Update):
    return not _is_outgoing(update)


incoming = create(incoming_filter)
"""Filter incoming updates. Messages sent to your own chat (Saved Messages) are also recognised as incoming."""


# endregion

# region outgoing_filter
async def outgoing_filter(_, __, update: Update):
    return _is_outgoing(update)


outgoing = create(outgoing_filter)
"""Filter outgoing updates. Messages sent to your own chat (Saved Messages) are not recognized as outgoing."""


# endregion

# region text_filter
async def text_filter(_, __, message: Message):
    return bool(message.text)


text = create(text_filter)
"""Filter text messages."""


# endregion

# region reply_filter
async def reply_filter(_, __, message: Message):
    return bool(message.reply_to_message_id or message.reply_to_story_id)


reply = create(reply_filter)
"""Filter messages that are replies to other messages or stories."""


# endregion

# region forwarded_filter
async def forwarded_filter(_, __, message: Message):
    return bool(message.forward_origin)


forwarded = create(forwarded_filter)
"""Filter messages that are forwarded."""


# endregion

# region caption_filter
async def caption_filter(_, __, message: Message):
    return bool(message.caption)


caption = create(caption_filter)
"""Filter media messages that contain captions."""


# endregion

# region self_destruction_filter
async def self_destruction_filter(_, __, message: Message):
    self_destructing = (message.photo, message.voice, message.video, message.video_note)
    return any(media and media.ttl_seconds for media in self_destructing)


self_destruction = create(self_destruction_filter)
"""Filter self-destruction media messages."""


# endregion

# region audio_filter
async def audio_filter(_, __, message: Message):
    return bool(message.audio)


audio = create(audio_filter)
"""Filter messages that contain :obj:`~pyrogram.types.Audio` objects."""


# endregion

# region document_filter
async def document_filter(_, __, message: Message):
    return bool(message.document)


document = create(document_filter)
"""Filter messages that contain :obj:`~pyrogram.types.Document` objects."""


# endregion

# region photo_filter
async def photo_filter(_, __, message: Message):
    return bool(message.photo)


photo = create(photo_filter)
"""Filter messages that contain :obj:`~pyrogram.types.Photo` objects."""


# endregion

# region sticker_filter
async def sticker_filter(_, __, message: Message):
    return bool(message.sticker)


sticker = create(sticker_filter)
"""Filter messages that contain :obj:`~pyrogram.types.Sticker` objects."""


# endregion

# region animation_filter
async def animation_filter(_, __, message: Message):
    return bool(message.animation)


animation = create(animation_filter)
"""Filter messages that contain :obj:`~pyrogram.types.Animation` objects."""


# endregion

# region game_filter
async def game_filter(_, __, message: Message):
    return bool(message.game)


game = create(game_filter)
"""Filter messages that contain :obj:`~pyrogram.types.Game` objects."""


# endregion

# region giveaway_filter
async def giveaway_filter(_, __, message: Message):
    return bool(message.giveaway)


giveaway = create(giveaway_filter)
"""Filter messages that contain :obj:`~pyrogram.types.Giveaway` objects."""


# endregion

# region giveaway_winners_filter
async def giveaway_winners_filter(_, __, message: Message):
    return bool(message.giveaway_winners)


giveaway_winners = create(giveaway_winners_filter)
"""Filter messages that contain :obj:`~pyrogram.types.GiveawayWinners` objects."""


# endregion

# region gift_code_filter
async def gift_code_filter(_, __, message: Message):
    return bool(message.premium_gift_code)


gift_code = create(gift_code_filter)
"""Filter messages that contain :obj:`~pyrogram.types.GiftCode` objects."""


# endregion

# region gift_filter
async def gift_filter(_, __, message: Message):
    return bool(message.gift)


gift = create(gift_filter)
"""Filter messages that contain :obj:`~pyrogram.types.Gift` objects."""


# endregion

# region users_shared_filter
async def users_shared_filter(_, __, message: Message):
    return bool(message.users_shared)


users_shared = create(users_shared_filter)
"""Filter service messages for shared users."""


# endregion

# region chat_shared_filter
async def chat_shared_filter(_, __, message: Message):
    return bool(message.chat_shared)


chat_shared = create(chat_shared_filter)
"""Filter service messages for shared chat."""


# endregion

# region video_filter
async def video_filter(_, __, message: Message):
    return bool(message.video)


video = create(video_filter)
"""Filter messages that contain :obj:`~pyrogram.types.Video` objects."""


# endregion

# region media_group_filter
async def media_group_filter(_, __, message: Message):
    return bool(message.media_group_id)


media_group = create(media_group_filter)
"""Filter messages containing photos or videos being part of an album."""


# endregion

# region voice_filter
async def voice_filter(_, __, message: Message):
    return bool(message.voice)


voice = create(voice_filter)
"""Filter messages that contain :obj:`~pyrogram.types.Voice` note objects."""


# endregion

# region video_note_filter
async def video_note_filter(_, __, message: Message):
    return bool(message.video_note)


video_note = create(video_note_filter)
"""Filter messages that contain :obj:`~pyrogram.types.VideoNote` objects."""


# endregion

# region contact_filter
async def contact_filter(_, __, message: Message):
    return bool(message.contact)


contact = create(contact_filter)
"""Filter messages that contain :obj:`~pyrogram.types.Contact` objects."""


# endregion

# region location_filter
async def location_filter(_, __, message: Message):
    return bool(message.location and not message.location.live_period)


location = create(location_filter)
"""Filter messages that contain :obj:`~pyrogram.types.Location` objects."""


# endregion

# region live_location_filter
async def live_location_filter(_, __, message: Message):
    return bool(message.location and message.location.live_period)


live_location = create(live_location_filter)
"""Filter messages that contain :obj:`~pyrogram.types.Location` objects with a live period."""


# endregion

# region venue_filter
async def venue_filter(_, __, message: Message):
    return bool(message.venue)


venue = create(venue_filter)
"""Filter messages that contain :obj:`~pyrogram.types.Venue` objects."""


# endregion

# region web_page_filter
async def web_page_filter(_, __, message: Message):
    return bool(message.web_page)


web_page = create(web_page_filter)
"""Filter messages sent with a webpage preview."""


# endregion

# region poll_filter
async def poll_filter(_, __, message: Message):
    return bool(message.poll)


poll = create(poll_filter)
"""Filter messages that contain :obj:`~pyrogram.types.Poll` objects."""


# endregion

# region dice_filter
async def dice_filter(_, __, message: Message):
    return bool(message.dice)


dice = create(dice_filter)
"""Filter messages that contain :obj:`~pyrogram.types.Dice` objects."""


# endregion

# region quote_filter
async def quote_filter(_, __, message: Message):
    return bool(message.quote)


quote = create(quote_filter)
"""Filter quote messages."""


# endregion

# region media_spoiler
async def media_spoiler_filter(_, __, message: Message):
    return bool(message.has_media_spoiler)


media_spoiler = create(media_spoiler_filter)
"""Filter media messages that contain a spoiler."""


# endregion

# region private_filter
async def private_filter(_, __, update: Update):
    chat_of_update = _chat_of(update)
    return bool(chat_of_update and chat_of_update.type in {enums.ChatType.PRIVATE, enums.ChatType.BOT})


private = create(private_filter)
"""Filter updates sent in private chats."""


# endregion

# region group_filter
async def group_filter(_, __, update: Update):
    chat_of_update = _chat_of(update)
    return bool(
        chat_of_update
        and chat_of_update.type in {enums.ChatType.GROUP, enums.ChatType.SUPERGROUP, enums.ChatType.FORUM}
    )


group = create(group_filter)
"""Filter updates sent in group or supergroup chats."""


# endregion

# region channel_filter
async def channel_filter(_, __, update: Update):
    chat_of_update = _chat_of(update)
    return bool(chat_of_update and chat_of_update.type == enums.ChatType.CHANNEL)


channel = create(channel_filter)
"""Filter updates sent in channels."""


# endregion

# region direct_filter
async def direct_filter(_, __, update: Update):
    chat_of_update = _chat_of(update)
    return bool(chat_of_update and chat_of_update.type == enums.ChatType.DIRECT)


direct = create(direct_filter)
"""Filter updates sent in direct."""


# endregion

# region forum_filter
async def forum_filter(_, __, update: Update):
    chat_of_update = _chat_of(update)
    return bool(chat_of_update and chat_of_update.is_forum)


forum = create(forum_filter)
"""Filter updates sent in forums."""


# endregion

# region story_filter
async def story_filter(_, __, message: Message):
    return bool(message.story)


story = create(story_filter)
"""Filter messages that contain :obj:`~pyrogram.types.Story` objects."""


# endregion

# region new_chat_members_filter
async def new_chat_members_filter(_, __, message: Message):
    return bool(message.new_chat_members)


new_chat_members = create(new_chat_members_filter)
"""Filter service messages for new chat members."""


# endregion

# region left_chat_member_filter
async def left_chat_member_filter(_, __, message: Message):
    return bool(message.left_chat_member)


left_chat_member = create(left_chat_member_filter)
"""Filter service messages for members that left the chat."""


# endregion

# region new_chat_title_filter
async def new_chat_title_filter(_, __, message: Message):
    return bool(message.new_chat_title)


new_chat_title = create(new_chat_title_filter)
"""Filter service messages for new chat titles."""


# endregion

# region new_chat_photo_filter
async def new_chat_photo_filter(_, __, message: Message):
    return bool(message.new_chat_photo)


new_chat_photo = create(new_chat_photo_filter)
"""Filter service messages for new chat photos."""


# endregion

# region delete_chat_photo_filter
async def delete_chat_photo_filter(_, __, message: Message):
    return bool(message.delete_chat_photo)


delete_chat_photo = create(delete_chat_photo_filter)
"""Filter service messages for deleted photos."""


# endregion

# region group_chat_created_filter
async def group_chat_created_filter(_, __, message: Message):
    return bool(message.group_chat_created)


group_chat_created = create(group_chat_created_filter)
"""Filter service messages for group chat creations."""


# endregion

# region supergroup_chat_created_filter
async def supergroup_chat_created_filter(_, __, message: Message):
    return bool(message.supergroup_chat_created)


supergroup_chat_created = create(supergroup_chat_created_filter)
"""Filter service messages for supergroup chat creations."""


# endregion

# region channel_chat_created_filter
async def channel_chat_created_filter(_, __, message: Message):
    return bool(message.channel_chat_created)


channel_chat_created = create(channel_chat_created_filter)
"""Filter service messages for channel chat creations."""


# endregion

# region migrate_to_chat_id_filter
async def migrate_to_chat_id_filter(_, __, message: Message):
    return bool(message.migrate_to_chat_id)


migrate_to_chat_id = create(migrate_to_chat_id_filter)
"""Filter service messages that contain migrate_to_chat_id."""


# endregion

# region migrate_from_chat_id_filter
async def migrate_from_chat_id_filter(_, __, message: Message):
    return bool(message.migrate_from_chat_id)


migrate_from_chat_id = create(migrate_from_chat_id_filter)
"""Filter service messages that contain migrate_from_chat_id."""


# endregion

# region pinned_message_filter
async def pinned_message_filter(_, __, message: Message):
    return bool(message.pinned_message)


pinned_message = create(pinned_message_filter)
"""Filter service messages for pinned messages."""


# endregion

# region game_high_score_filter
async def game_high_score_filter(_, __, message: Message):
    return bool(message.game_high_score)


game_high_score = create(game_high_score_filter)
"""Filter service messages for game high scores."""


# endregion

# region reply_keyboard_filter
async def reply_keyboard_filter(_, __, message: Message):
    return isinstance(message.reply_markup, ReplyKeyboardMarkup)


reply_keyboard = create(reply_keyboard_filter)
"""Filter messages containing reply keyboard markups"""


# endregion

# region inline_keyboard_filter
async def inline_keyboard_filter(_, __, message: Message):
    return isinstance(message.reply_markup, InlineKeyboardMarkup)


inline_keyboard = create(inline_keyboard_filter)
"""Filter messages containing inline keyboard markups"""


# endregion

# region mentioned_filter
async def mentioned_filter(_, __, message: Message):
    return bool(message.mentioned)


mentioned = create(mentioned_filter)
"""Filter messages containing mentions"""


# endregion

# region via_bot_filter
async def via_bot_filter(_, __, message: Message):
    return bool(message.via_bot)


via_bot = create(via_bot_filter)
"""Filter messages sent via inline bots"""


# endregion

# region admin_filter
async def admin_filter(_, __, update: Update):
    chat_of_update = _chat_of(update)
    return bool(chat_of_update and chat_of_update.is_admin)


admin = create(admin_filter)
"""Filter chats where you have admin rights"""


# endregion

# region video_chat_started_filter
async def video_chat_started_filter(_, __, message: Message):
    return bool(message.video_chat_started)


video_chat_started = create(video_chat_started_filter)
"""Filter messages for started video chats"""


# endregion

# region video_chat_ended_filter
async def video_chat_ended_filter(_, __, message: Message):
    return bool(message.video_chat_ended)


video_chat_ended = create(video_chat_ended_filter)
"""Filter messages for ended video chats"""


# endregion

# region business
async def business_filter(_, __, update: Update):
    message = _message_of(update)
    return bool(message and message.business_connection_id)


business = create(business_filter)
"""Filter updates sent via business bot"""


# endregion

# region video_chat_members_invited_filter
async def video_chat_members_invited_filter(_, __, message: Message):
    return bool(message.video_chat_members_invited)


video_chat_members_invited = create(video_chat_members_invited_filter)
"""Filter messages for voice chat invited members"""


# endregion

# region successful_payment_filter
async def successful_payment_filter(_, __, message: Message):
    return bool(message.successful_payment)


successful_payment = create(successful_payment_filter)
"""Filter messages for successful payments"""


# endregion

# region service_filter
async def service_filter(_, __, message: Message):
    return bool(message.service)


service = create(service_filter)
"""Filter service messages.

A service message contains any of the following fields set: *left_chat_member*,
*new_chat_title*, *new_chat_photo*, *delete_chat_photo*, *group_chat_created*, *supergroup_chat_created*,
*channel_chat_created*, *migrate_to_chat_id*, *migrate_from_chat_id*, *pinned_message*, *game_score*,
*video_chat_started*, *video_chat_ended*, *video_chat_members_invited*, *successful_payment*.
"""


# endregion

# region media_filter
async def media_filter(_, __, message: Message):
    return bool(message.media)


media = create(media_filter)
"""Filter media messages.

A media message contains any of the following fields set: *audio*, *document*, *photo*, *sticker*, *video*,
*animation*, *voice*, *video_note*, *contact*, *location*, *venue*, *poll*.
"""


# endregion

# region scheduled_filter
async def scheduled_filter(_, __, message: Message):
    return bool(message.scheduled)


scheduled = create(scheduled_filter)
"""Filter messages that have been scheduled (not yet sent)."""


# endregion

# region from_scheduled_filter
async def from_scheduled_filter(_, __, message: Message):
    return bool(message.from_scheduled)


from_scheduled = create(from_scheduled_filter)
"""Filter new automatically sent messages that were previously scheduled."""


# endregion

# region paid_message_filter
async def paid_message_filter(_, __, message: Message):
    return bool(message.send_paid_messages_stars)


paid_message = create(paid_message_filter)
"""Filter paid messages."""


# endregion

# region linked_channel_filter
async def linked_channel_filter(_, __, update: Update):
    message = _message_of(update)
    return bool(
        message and
        message.forward_origin and
        message.forward_origin.type == enums.MessageOriginType.CHANNEL and
        message.forward_origin.chat == message.sender_chat
    )


linked_channel = create(linked_channel_filter)
"""Filter updates about a message that was automatically forwarded from the linked channel to the group chat."""


# endregion

# region gift_offer_filter
async def gift_offer_filter(_, __, message: Message):
    return bool(
        message.upgraded_gift_purchase_offer and message.upgraded_gift_purchase_offer.state == enums.GiftPurchaseOfferState.PENDING
    )


gift_offer = create(gift_offer_filter)
"""Filter new gift offers."""


# endregion

# region gift_offer_accepted_filter
async def gift_offer_accepted_filter(_, __, message: Message):
    return bool(
        message.upgraded_gift_purchase_offer and message.upgraded_gift_purchase_offer.state == enums.GiftPurchaseOfferState.ACCEPTED
    )


gift_offer_accepted = create(gift_offer_accepted_filter)
"""Filter accepted gift offers."""


# endregion

# region gift_offer_rejected_filter
async def gift_offer_rejected_filter(_, __, message: Message):
    return bool(
        (message.upgraded_gift_purchase_offer and message.upgraded_gift_purchase_offer.state == enums.GiftPurchaseOfferState.REJECTED)
        or message.upgraded_gift_purchase_offer_rejected
    )


gift_offer_rejected = create(gift_offer_rejected_filter)
"""Filter rejected gift offers."""


# endregion

# region ephemeral_filter
ephemeral = create(lambda _, __, message: message.ephemeral_message_id is not None)
"""Filter ephemeral messages."""


# endregion

# region command_filter
def command(commands: Union[str, List[str]], prefixes: Optional[Union[str, List[str]]] = "/", case_sensitive: bool = False):
    """Filter commands, i.e.: text messages starting with "/" or any other custom prefix.

    Parameters:
        commands (``str`` | ``list``):
            The command or list of commands as string the filter should look for.
            Examples: "start", ["start", "help", "settings"]. When a message text containing
            a command arrives, the command itself and its arguments will be stored in the *command*
            field of the :obj:`~pyrogram.types.Message`.

        prefixes (``str`` | ``list``, *optional*):
            A prefix or a list of prefixes as string the filter should look for.
            Defaults to "/" (slash). Examples: ".", "!", ["/", "!", "."], list(".:!").
            Pass None or "" (empty string) to allow commands with no prefix at all.

        case_sensitive (``bool``, *optional*):
            Pass True if you want your command(s) to be case sensitive. Defaults to False.
            Examples: when True, command="Start" would trigger /Start but not /start.
    """
    command_re = re.compile(r"([\"'])(.*?)(?<!\\)\1|(\S+)")

    async def func(flt, client: pyrogram.Client, message: Message):
        username = client.me.username or ""
        text = message.text or message.caption
        message.command = None

        if not text:
            return False

        for prefix in flt.prefixes:
            if not text.startswith(prefix):
                continue

            without_prefix = text[len(prefix):]

            for cmd in flt.commands:
                if not re.match(rf"^(?:{cmd}(?:@?{username})?)(?:\s|$)", without_prefix,
                                flags=re.IGNORECASE if not flt.case_sensitive else 0):
                    continue

                without_command = re.sub(rf"{cmd}(?:@?{username})?\s?", "", without_prefix, count=1,
                                         flags=re.IGNORECASE if not flt.case_sensitive else 0)

                # match.groups are 1-indexed, group(1) is the quote, group(2) is the text
                # between the quotes, group(3) is unquoted, whitespace-split text

                # Remove the escape character from the arguments
                message.command = [cmd] + [
                    re.sub(r"\\([\"'])", r"\1", match.group(2) or match.group(3) or "")
                    for match in command_re.finditer(without_command)
                ]

                return True

        return False

    commands = commands if isinstance(commands, list) else [commands]
    commands = {c if case_sensitive else c.lower() for c in commands}

    prefixes = [] if prefixes is None else prefixes
    prefixes = prefixes if isinstance(prefixes, list) else [prefixes]
    prefixes = set(prefixes) if prefixes else {""}

    return create(
        func,
        "CommandFilter",
        commands=commands,
        prefixes=prefixes,
        case_sensitive=case_sensitive
    )


# endregion

def regex(pattern: Union[str, Pattern], flags: int = 0):
    """Filter updates that match a given regular expression pattern.

    Can be applied to handlers that receive one of the following updates:

    - :obj:`~pyrogram.types.Message`: The filter will match ``text`` or ``caption``.
    - :obj:`~pyrogram.types.CallbackQuery`: The filter will match ``data``.
    - :obj:`~pyrogram.types.ChosenInlineResult`: The filter will match ``query``.
    - :obj:`~pyrogram.types.InlineQuery`: The filter will match ``query``.
    - :obj:`~pyrogram.types.PreCheckoutQuery`: The filter will match ``payload``.

    When a pattern matches, all the `Match Objects <https://docs.python.org/3/library/re.html#match-objects>`_ are
    stored in the ``matches`` field of the update object itself.

    Parameters:
        pattern (``str`` | ``Pattern``):
            The regex pattern as string or as pre-compiled pattern.

        flags (``int``, *optional*):
            Regex flags.
    """

    async def func(flt, _, update: Update):
        if isinstance(update, Message):
            value = update.text or update.caption
        elif isinstance(update, CallbackQuery):
            value = update.data
        elif isinstance(update, (ChosenInlineResult, InlineQuery)):
            value = update.query
        elif isinstance(update, PreCheckoutQuery):
            value = update.invoice_payload
        else:
            raise ValueError(f"Regex filter doesn't work with {type(update)}")

        if value:
            update.matches = list(flt.p.finditer(value)) or None

        return bool(update.matches)

    return create(
        func,
        "RegexFilter",
        p=pattern if isinstance(pattern, Pattern) else re.compile(pattern, flags)
    )


# noinspection PyPep8Naming
class user(Filter, set):
    """Filter updates coming from one or more users.

    You can use `set bound methods <https://docs.python.org/3/library/stdtypes.html#set>`_ to manipulate the
    users container.

    Parameters:
        users (``int`` | ``str`` | ``list``):
            Pass one or more user ids/usernames to filter users.
            For you yourself, "me" or "self" can be used as well.
            Defaults to None (no users).
    """

    def __init__(self, users: Optional[Union[int, str, List[Union[int, str]]]] = None):
        users = [] if users is None else users if isinstance(users, list) else [users]

        super().__init__(
            _ME if u in _ME_ALIASES
            else u.lower().strip("@") if isinstance(u, str)
            else u for u in users
        )

    async def __call__(self, _, update: Update):
        sender = _sender_of(update)
        if not sender:
            return False
        if not self.isdisjoint(_ME_ALIASES) and sender.is_self:
            return True
        return bool(sender.id in self or (sender.username and sender.username.lower() in self))


# noinspection PyPep8Naming
class chat(Filter, set):
    """Filter updates coming from one or more chats.

    You can use `set bound methods <https://docs.python.org/3/library/stdtypes.html#set>`_ to manipulate the
    chats container.

    Parameters:
        chats (``int`` | ``str`` | ``list``):
            Pass one or more chat ids/usernames to filter chats.
            For your personal cloud (Saved Messages) you can simply use "me" or "self".
            Defaults to None (no chats).
    """

    def __init__(self, chats: Optional[Union[int, str, List[Union[int, str]]]] = None):
        chats = [] if chats is None else chats if isinstance(chats, list) else [chats]

        super().__init__(
            _ME if c in _ME_ALIASES
            else c.lower().strip("@") if isinstance(c, str)
            else c for c in chats
        )

    async def __call__(self, _, update: Update):
        chat_of_update = _chat_of(update)
        if not chat_of_update:
            return False
        if chat_of_update.id in self or (chat_of_update.username and chat_of_update.username.lower() in self):
            return True
        sender = _sender_of(update)

        # Saved Messages is the chat whose id is your own user id.
        #  `is_self` on its own is true of anything you caused, in any chat.
        return bool(
            not self.isdisjoint(_ME_ALIASES)
            and sender
            and sender.is_self
            and chat_of_update.id == sender.id
        )


# noinspection PyPep8Naming
class topic(Filter, set):
    """Filter updates coming from one or more topics.

    You can use `set bound methods <https://docs.python.org/3/library/stdtypes.html#set>`_ to manipulate the
    topics container.

    Parameters:
        topics (``int`` | ``list``):
            Pass one or more topic ids to filter updates in specific topics.
            Defaults to None (no topics).
    """

    def __init__(self, topics: Optional[Union[int, List[int]]] = None):
        topics = [] if topics is None else topics if isinstance(topics, list) else [topics]

        super().__init__(
            t for t in topics
        )

    async def __call__(self, _, update: Update):
        message = _message_of(update)

        return bool(message and message.topic and message.topic.id in self)
