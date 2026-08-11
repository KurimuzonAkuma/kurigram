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
from pyrogram import raw, types, utils

log = logging.getLogger(__name__)

class SendGame:
    async def send_game(
        self: "pyrogram.Client",
        chat_id: Union[int, str],
        game_short_name: str,
        disable_notification: Optional[bool] = None,
        message_thread_id: Optional[int] = None,
        effect_id: Optional[int] = None,
        reply_parameters: Optional["types.ReplyParameters"] = None,
        protect_content: Optional[bool] = None,
        allow_paid_broadcast: Optional[bool] = None,
        reply_markup: Optional[Union[
            "types.InlineKeyboardMarkup",
            "types.ReplyKeyboardMarkup",
            "types.ReplyKeyboardRemove",
            "types.ForceReply",
        ]] = None,

        reply_to_message_id: Optional[int] = None,
        reply_to_chat_id: Optional[Union[int, str]] = None,
    ) -> "types.Message":
        """Send a game.

        .. include:: /_includes/usable-by/bots.rst

        Parameters:
            chat_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target chat.
                For your personal cloud (Saved Messages) you can simply use "me" or "self".
                For a contact that exists in your Telegram address book you can use his phone number (str).

            game_short_name (``str``):
                Short name of the game, serves as the unique identifier for the game. Set up your games via Botfather.

            disable_notification (``bool``, *optional*):
                Sends the message silently.
                Users will receive a notification with no sound.

            message_thread_id (``int``, *optional*):
                Unique identifier of a message thread to which the message belongs.
                For supergroups only.

            effect_id (``int``, *optional*):
                Unique identifier of the message effect.
                For private chats only.

            reply_parameters (:obj:`~pyrogram.types.ReplyParameters`, *optional*):
                Describes reply parameters for the message that is being sent.

            protect_content (``bool``, *optional*):
                Protects the contents of the sent message from forwarding and saving.

            allow_paid_broadcast (``bool``, *optional*):
                If True, you will be allowed to send up to 1000 messages per second.
                Ignoring broadcasting limits for a fee of 0.1 Telegram Stars per message.
                The relevant Stars will be withdrawn from the bot's balance.
                For bots only.

            reply_markup (:obj:`~pyrogram.types.InlineKeyboardMarkup`, *optional*):
                An object for an inline keyboard. If empty, one ‘Play game_title’ button will be shown automatically.
                If not empty, the first button must launch the game.

        Returns:
            :obj:`~pyrogram.types.Message`: On success, the sent game message is returned.

        Example:
            .. code-block:: python

                await app.send_game(chat_id, "gamename")
        """
        if reply_to_message_id is not None or reply_to_chat_id is not None:
            if reply_to_message_id is not None:
                log.warning(
                    "`reply_to_message_id` is deprecated and will be removed in future updates. Use `reply_parameters` instead."
                )

            if reply_to_chat_id is not None:
                log.warning(
                    "`reply_to_chat_id` is deprecated and will be removed in future updates. Use `reply_parameters` instead."
                )

            reply_parameters = types.ReplyParameters(
                chat_id=reply_to_chat_id,
                message_id=reply_to_message_id
            )

        r = await self.invoke(
            raw.functions.messages.SendMedia(
                peer=await self.resolve_peer(chat_id),
                media=raw.types.InputMediaGame(
                    id=raw.types.InputGameShortName(
                        bot_id=raw.types.InputUserSelf(),
                        short_name=game_short_name
                    ),
                ),
                message="",
                silent=disable_notification or None,
                reply_to=await utils.get_reply_to(
                    self,
                    reply_parameters,
                    message_thread_id
                ),
                random_id=self.rnd_id(),
                noforwards=protect_content,
                allow_paid_floodskip=allow_paid_broadcast,
                reply_markup=await reply_markup.write(self) if reply_markup else None,
                effect=effect_id
            )
        )

        messages = await utils.parse_messages(client=self, messages=r)

        return messages[0] if messages else None
