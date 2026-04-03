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

import asyncio
from collections import OrderedDict
import inspect
import logging
from typing import Dict

import pyrogram
from pyrogram import utils
from pyrogram.handlers import (
    Handler,
    ErrorHandler, CallbackQueryHandler, MessageHandler, EditedMessageHandler, DeletedMessagesHandler,
    UserStatusHandler, RawUpdateHandler, InlineQueryHandler, PollHandler, PreCheckoutQueryHandler,
    ChosenInlineResultHandler, ChatMemberUpdatedHandler, ChatJoinRequestHandler, StoryHandler,
    ShippingQueryHandler, MessageReactionHandler, MessageReactionCountHandler, ChatBoostHandler,
    PurchasedPaidMediaHandler, BusinessConnectionHandler, BusinessMessageHandler,
    EditedBusinessMessageHandler, DeletedBusinessMessagesHandler
)
from pyrogram.raw.types import (
    UpdateNewMessage, UpdateNewChannelMessage, UpdateNewScheduledMessage,
    UpdateBotNewBusinessMessage, UpdateBotEditBusinessMessage, UpdateBotDeleteBusinessMessage,
    UpdateEditMessage, UpdateEditChannelMessage,
    UpdateDeleteMessages, UpdateDeleteChannelMessages,
    UpdateBotCallbackQuery, UpdateInlineBotCallbackQuery, UpdateBotPrecheckoutQuery,
    UpdateUserStatus, UpdateBotInlineQuery, UpdateMessagePoll,
    UpdateBotInlineSend, UpdateChatParticipant, UpdateChannelParticipant,
    UpdateBotChatInviteRequester, UpdateStory, UpdateBotShippingQuery, UpdateBotMessageReaction,
    UpdateBotMessageReactions, UpdateBotChatBoost, UpdateBusinessBotCallbackQuery,
    UpdateBotPurchasedPaidMedia, UpdateMessagePollVote, UpdateBotBusinessConnect
)

log = logging.getLogger(__name__)


class Dispatcher:
    NEW_MESSAGE_UPDATES = (UpdateNewMessage, UpdateNewChannelMessage, UpdateNewScheduledMessage)
    EDIT_MESSAGE_UPDATES = (UpdateEditMessage, UpdateEditChannelMessage)
    DELETE_MESSAGES_UPDATES = (UpdateDeleteMessages, UpdateDeleteChannelMessages)
    CALLBACK_QUERY_UPDATES = (UpdateBotCallbackQuery, UpdateInlineBotCallbackQuery, UpdateBusinessBotCallbackQuery)
    CHAT_MEMBER_UPDATES = (UpdateChatParticipant, UpdateChannelParticipant)
    USER_STATUS_UPDATES = (UpdateUserStatus,)
    BOT_INLINE_QUERY_UPDATES = (UpdateBotInlineQuery,)
    POLL_UPDATES = (UpdateMessagePoll, UpdateMessagePollVote)
    CHOSEN_INLINE_RESULT_UPDATES = (UpdateBotInlineSend,)
    CHAT_JOIN_REQUEST_UPDATES = (UpdateBotChatInviteRequester,)
    NEW_STORY_UPDATES = (UpdateStory,)
    PRE_CHECKOUT_QUERY_UPDATES = (UpdateBotPrecheckoutQuery,)
    SHIPPING_QUERY_UPDATES = (UpdateBotShippingQuery,)
    MESSAGE_REACTION_UPDATES = (UpdateBotMessageReaction,)
    MESSAGE_REACTION_COUNT_UPDATES = (UpdateBotMessageReactions,)
    CHAT_BOOST_UPDATES = (UpdateBotChatBoost,)
    PURCHASED_PAID_MEDIA_UPDATES = (UpdateBotPurchasedPaidMedia,)
    BUSINESS_CONNECTION_UPDATES = (UpdateBotBusinessConnect,)
    NEW_BUSINESS_MESSAGE_UPDATES = (UpdateBotNewBusinessMessage,)
    EDITED_BUSINESS_MESSAGE_UPDATES = (UpdateBotEditBusinessMessage,)
    DELETED_BUSINESS_MESSAGES_UPDATES = (UpdateBotDeleteBusinessMessage,)

    def __init__(self, client: "pyrogram.Client"):
        self.client = client

        self.handler_worker_tasks = []
        self.locks_list = []

        self.updates_queue = asyncio.Queue()
        self.groups = OrderedDict()

        async def message_parser(update, users, chats):
            connection_id = getattr(update, "connection_id", None)

            return (
                await pyrogram.types.Message._parse(
                    self.client,
                    update.message,
                    users,
                    chats,
                    is_scheduled=isinstance(update, UpdateNewScheduledMessage),
                    replies=0 if getattr(update, "connection_id", None) else 1,
                    business_connection_id=connection_id,
                    raw_reply_to_message=getattr(update, "reply_to_message", None)
                ),
                MessageHandler
            )

        async def edited_message_parser(update, users, chats):
            # Edited messages are parsed the same way as new messages, but the handler is different
            parsed, _ = await message_parser(update, users, chats)

            return (
                parsed,
                EditedMessageHandler
            )

        async def deleted_messages_parser(update, users, chats):
            return (
                utils.parse_deleted_messages(self.client, update, users, chats),
                DeletedMessagesHandler,
            )

        async def callback_query_parser(update, users, chats):
            return (
                await pyrogram.types.CallbackQuery._parse(self.client, update, users, chats),
                CallbackQueryHandler
            )

        async def user_status_parser(update, users, chats):
            return (
                pyrogram.types.User._parse_user_status(self.client, update),
                UserStatusHandler
            )

        async def inline_query_parser(update, users, chats):
            return (
                pyrogram.types.InlineQuery._parse(self.client, update, users),
                InlineQueryHandler
            )

        async def poll_parser(update, users, chats):
            return (
                pyrogram.types.Poll._parse_update(self.client, update, users),
                PollHandler
            )

        async def chosen_inline_result_parser(update, users, chats):
            return (
                pyrogram.types.ChosenInlineResult._parse(self.client, update, users),
                ChosenInlineResultHandler
            )

        async def chat_member_updated_parser(update, users, chats):
            return (
                pyrogram.types.ChatMemberUpdated._parse(self.client, update, users, chats),
                ChatMemberUpdatedHandler
            )

        async def chat_join_request_parser(update, users, chats):
            return (
                pyrogram.types.ChatJoinRequest._parse(self.client, update, users, chats),
                ChatJoinRequestHandler
            )

        async def story_parser(update, users, chats):
            return (
                await pyrogram.types.Story._parse(self.client, update.story, update.peer, users, chats),
                StoryHandler
            )

        async def pre_checkout_query_parser(update, users, chats):
            return (
                await pyrogram.types.PreCheckoutQuery._parse(self.client, update, users),
                PreCheckoutQueryHandler
            )

        async def shipping_query_parser(update, users, chats):
            return (
                await pyrogram.types.ShippingQuery._parse(self.client, update, users),
                ShippingQueryHandler
            )

        async def message_reaction_parser(update, users, chats):
            return (
                pyrogram.types.MessageReactionUpdated._parse(self.client, update, users, chats),
                MessageReactionHandler
            )

        async def message_reaction_count_parser(update, users, chats):
            return (
                pyrogram.types.MessageReactionCountUpdated._parse(self.client, update, users, chats),
                MessageReactionCountHandler
            )

        async def chat_boost_parser(update, users, chats):
            return (
                pyrogram.types.ChatBoostUpdated._parse(self.client, update, users, chats),
                ChatBoostHandler
            )

        async def purchased_paid_media_parser(update, users, chats):
            return (
                pyrogram.types.PurchasedPaidMedia._parse(self.client, update, users),
                PurchasedPaidMediaHandler
            )

        async def business_connection_parser(update, users, chats):
            return (
                pyrogram.types.BusinessConnection._parse(self.client, update, users),
                BusinessConnectionHandler
            )

        async def business_message_parser(update, users, chats):
            # Business messages are parsed the same way as regular messages, but the handler is different
            parsed, _ = await message_parser(update, users, chats)

            return (
                parsed,
                BusinessMessageHandler
            )

        async def edited_business_message_parser(update, users, chats):
            # Edited messages are parsed the same way as regular messages, but the handler is different
            parsed, _ = await message_parser(update, users, chats)

            return (
                parsed,
                EditedBusinessMessageHandler
            )

        async def deleted_business_messages_parser(update, users, chats):
            # Deleted messages are parsed the same way as regular messages, but the handler is different
            parsed, _ = await deleted_messages_parser(update, users, chats)

            return (
                parsed,
                DeletedBusinessMessagesHandler,
            )

        self.update_parsers = {
            Dispatcher.NEW_MESSAGE_UPDATES: message_parser,
            Dispatcher.EDIT_MESSAGE_UPDATES: edited_message_parser,
            Dispatcher.DELETE_MESSAGES_UPDATES: deleted_messages_parser,
            Dispatcher.CALLBACK_QUERY_UPDATES: callback_query_parser,
            Dispatcher.USER_STATUS_UPDATES: user_status_parser,
            Dispatcher.BOT_INLINE_QUERY_UPDATES: inline_query_parser,
            Dispatcher.POLL_UPDATES: poll_parser,
            Dispatcher.CHOSEN_INLINE_RESULT_UPDATES: chosen_inline_result_parser,
            Dispatcher.CHAT_MEMBER_UPDATES: chat_member_updated_parser,
            Dispatcher.CHAT_JOIN_REQUEST_UPDATES: chat_join_request_parser,
            Dispatcher.NEW_STORY_UPDATES: story_parser,
            Dispatcher.PRE_CHECKOUT_QUERY_UPDATES: pre_checkout_query_parser,
            Dispatcher.SHIPPING_QUERY_UPDATES: shipping_query_parser,
            Dispatcher.MESSAGE_REACTION_UPDATES: message_reaction_parser,
            Dispatcher.MESSAGE_REACTION_COUNT_UPDATES: message_reaction_count_parser,
            Dispatcher.CHAT_BOOST_UPDATES: chat_boost_parser,
            Dispatcher.PURCHASED_PAID_MEDIA_UPDATES: purchased_paid_media_parser,
            Dispatcher.BUSINESS_CONNECTION_UPDATES: business_connection_parser,
            Dispatcher.NEW_BUSINESS_MESSAGE_UPDATES: business_message_parser,
            Dispatcher.EDITED_BUSINESS_MESSAGE_UPDATES: edited_business_message_parser,
            Dispatcher.DELETED_BUSINESS_MESSAGES_UPDATES: deleted_business_messages_parser
        }

        self.update_parsers = {key: value for key_tuple, value in self.update_parsers.items() for key in key_tuple}

    async def start(self):
        if callable(self.client.start_handler):
            try:
                await self.client.start_handler(self.client)
            except Exception as e:
                log.exception(e)

        if not self.client.no_updates:
            for i in range(self.client.workers):
                self.locks_list.append(asyncio.Lock())

                self.handler_worker_tasks.append(
                    self.client.loop.create_task(self.handler_worker(self.locks_list[-1]))
                )

            log.info("Started %s HandlerTasks", self.client.workers)

            if not self.client.skip_updates:
                await self.client.recover_gaps()

    async def stop(self, clear_handlers: bool = True):
        if callable(self.client.stop_handler):
            try:
                await self.client.stop_handler(self.client)
            except Exception as e:
                log.exception(e)

        if not self.client.no_updates:
            for i in range(self.client.workers):
                self.updates_queue.put_nowait(None)

            for i in self.handler_worker_tasks:
                await i

            if clear_handlers:
                self.handler_worker_tasks.clear()
                self.groups.clear()

            log.info("Stopped %s HandlerTasks", self.client.workers)

    def add_handler(self, handler: Handler, group: int):
        async def fn():
            for lock in self.locks_list:
                await lock.acquire()

            try:
                if group not in self.groups:
                    self.groups[group] = []
                    self.groups = OrderedDict(sorted(self.groups.items()))

                self.groups[group].append(handler)
            finally:
                for lock in self.locks_list:
                    lock.release()

        self.client.loop.create_task(fn())

    def remove_handler(self, handler: Handler, group: int):
        async def fn():
            for lock in self.locks_list:
                await lock.acquire()

            try:
                if group not in self.groups:
                    raise ValueError(
                        f"Group {group} does not exist. Handler was not removed."
                    )

                self.groups[group].remove(handler)

                if not self.groups[group]:
                    del self.groups[group]
            finally:
                for lock in self.locks_list:
                    lock.release()

        self.client.loop.create_task(fn())

    async def handler_worker(self, lock):
        while True:
            packet = await self.updates_queue.get()

            if packet is None:
                break

            try:
                update, users, chats = packet
                parser = self.update_parsers.get(type(update), None)

                parsed_update, handler_type = (
                    await parser(update, users, chats)
                    if parser is not None
                    else (None, type(None))
                )

                async with lock:
                    for group in self.groups.values():
                        for handler in group:
                            if isinstance(handler, ErrorHandler):
                                continue

                            args = None

                            if isinstance(handler, handler_type):
                                try:
                                    if await handler.check(self.client, parsed_update):
                                        args = (parsed_update,)
                                except Exception as e:
                                    log.exception(e)
                                    continue

                            elif isinstance(handler, RawUpdateHandler):
                                try:
                                    if await handler.check(self.client, update):
                                        args = (update, users, chats)
                                except Exception as e:
                                    log.exception(e)
                                    continue

                            if args is None:
                                continue

                            try:
                                if inspect.iscoroutinefunction(handler.callback):
                                    await handler.callback(self.client, *args)
                                else:
                                    await self.client.loop.run_in_executor(
                                        self.client.executor,
                                        handler.callback,
                                        self.client,
                                        *args
                                    )
                            except pyrogram.StopPropagation:
                                raise
                            except pyrogram.ContinuePropagation:
                                continue
                            except Exception as exc:
                                await self.handle_update_handler_exception(
                                    exc, handler, update, users, chats
                                )

                            break
            except pyrogram.StopPropagation:
                pass
            except Exception as e:
                log.exception(e)

    async def handle_update_handler_exception(
        self,
        exc: Exception,
        update_handler: Handler,
        update: "pyrogram.raw.base.Update",
        users: Dict[int, "pyrogram.raw.base.User"],
        chats: Dict[int, "pyrogram.raw.base.Chat"]
    ) -> None:
        handled = False
        try:
            for group in self.groups.values():
                for handler in group:
                    if not isinstance(handler, ErrorHandler):
                        continue

                    if not isinstance(exc, handler.exceptions):
                        continue

                    try:
                        if inspect.iscoroutinefunction(handler.callback):
                            await handler.callback(
                                self.client, exc, update_handler, update, users, chats
                            )
                        else:
                            await self.client.loop.run_in_executor(
                                self.client.executor, handler.callback,
                                self.client, exc, update_handler, update, users, chats
                            )
                    except pyrogram.StopPropagation:
                        handled = True
                        raise
                    except pyrogram.ContinuePropagation:
                        handled = True
                        continue
                    except Exception:
                        log.exception("Error handler raised an exception:")
                    else:
                        handled = True

                    break
        except pyrogram.StopPropagation:
            pass
        finally:
            if not handled:
                log.error(
                    f"Unexpected exception raised in {type(update_handler).__name__}:",
                    exc_info=(type(exc), exc, exc.__traceback__)
                )
