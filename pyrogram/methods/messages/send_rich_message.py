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

import logging
from typing import Optional, Union

import pyrogram
from pyrogram import enums, raw, types, utils

log = logging.getLogger(__name__)


class SendRichMessage:
    async def send_rich_message(
        self: "pyrogram.Client",
        chat_id: Union[int, str],
        rich_message: "types.InputRichMessage",
        disable_notification: Optional[bool] = None,
        message_thread_id: Optional[int] = None,
        direct_messages_topic_id: Optional[int] = None,
        effect_id: Optional[int] = None,
        reply_parameters: Optional["types.ReplyParameters"] = None,
        protect_content: Optional[bool] = None,
        business_connection_id: Optional[str] = None,
        allow_paid_broadcast: Optional[bool] = None,
        suggested_post_parameters: Optional["types.SuggestedPostParameters"] = None,
        reply_markup: Optional[
            Union[
                "types.InlineKeyboardMarkup",
                "types.ReplyKeyboardMarkup",
                "types.ReplyKeyboardRemove",
                "types.ForceReply",
            ]
        ] = None,
    ) -> "types.Message":
        """Send text messages.

        .. include:: /_includes/usable-by/bots.rst

        Parameters:
            chat_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target chat.
                For your personal cloud (Saved Messages) you can simply use "me" or "self".
                For a contact that exists in your Telegram address book you can use his phone number (str).

            rich_message (:obj:`~pyrogram.types.InputRichMessage`):
                The message to be sent.

            disable_notification (``bool``, *optional*):
                Sends the message silently.
                Users will receive a notification with no sound.

            message_thread_id (``int``, *optional*):
                Unique identifier for the target message thread (topic) of the forum.
                For forums only.

            direct_messages_topic_id (``int``, *optional*):
                Unique identifier of the topic in a channel direct messages chat administered by the current user.
                For directs only only.

            effect_id (``int``, *optional*):
                Unique identifier of the message effect.
                For private chats only.

            reply_parameters (:obj:`~pyrogram.types.ReplyParameters`, *optional*):
                Describes reply parameters for the message that is being sent.

            protect_content (``bool``, *optional*):
                Protects the contents of the sent message from forwarding and saving.

            business_connection_id (``str``, *optional*):
                Unique identifier of the business connection on behalf of which the message will be sent.

            allow_paid_broadcast (``bool``, *optional*):
                If True, you will be allowed to send up to 1000 messages per second.
                Ignoring broadcasting limits for a fee of 0.1 Telegram Stars per message.
                The relevant Stars will be withdrawn from the bot's balance.
                For bots only.

            suggested_post_parameters (:obj:`~pyrogram.types.SuggestedPostParameters`, *optional*):
                Information about the suggested post.

            reply_markup (:obj:`~pyrogram.types.InlineKeyboardMarkup` | :obj:`~pyrogram.types.ReplyKeyboardMarkup` | :obj:`~pyrogram.types.ReplyKeyboardRemove` | :obj:`~pyrogram.types.ForceReply`, *optional*):
                Additional interface options. An object for an inline keyboard, custom reply keyboard,
                instructions to remove reply keyboard or to force a reply from the user.

        Returns:
            :obj:`~pyrogram.types.Message`: On success, the sent text message is returned.

        Example:
            .. code-block:: python

                from pyrogram import types

                await app.send_rich_message(
                    chat_id=chat_id,
                    rich_message=types.InputRichMessage(html="Hello <b>World</b>"),
                    reply_markup=types.InlineKeyboardMarkup(
                        [
                            [types.InlineKeyboardButton("Data", callback_data="callback_data")],
                            [types.InlineKeyboardButton("Docs", url="https://docs.pyrogram.org")],
                        ]
                    ),
                )
        """
        r = await self.invoke(
            raw.functions.messages.SendMessage(
                peer=await self.resolve_peer(chat_id),
                silent=disable_notification or None,
                reply_to=await utils.get_reply_to(
                    self, reply_parameters, message_thread_id, direct_messages_topic_id
                ),
                random_id=self.rnd_id(),
                allow_paid_floodskip=allow_paid_broadcast,
                suggested_post=suggested_post_parameters.write()
                if suggested_post_parameters
                else None,
                reply_markup=await reply_markup.write(self) if reply_markup else None,
                message="",
                noforwards=protect_content,
                rich_message=rich_message.write(),
                effect=effect_id,
            ),
            business_connection_id=business_connection_id,
        )

        if isinstance(r, raw.types.UpdateShortSentMessage):
            peer = await self.resolve_peer(chat_id)

            peer_id = peer.user_id if isinstance(peer, raw.types.InputPeerUser) else -peer.chat_id

            return types.Message(
                id=r.id,
                chat=types.Chat(id=peer_id, type=enums.ChatType.PRIVATE, client=self),
                date=utils.timestamp_to_datetime(r.date),
                outgoing=r.out,
                reply_markup=reply_markup,
                client=self,
            )

        return next(iter(await utils.parse_messages(client=self, messages=r)), None)
