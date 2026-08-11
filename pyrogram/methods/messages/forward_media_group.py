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

from datetime import datetime
from typing import List, Optional, Union

import pyrogram
from pyrogram import raw, types, utils


class ForwardMediaGroup:
    async def forward_media_group(
        self: "pyrogram.Client",
        chat_id: Union[int, str],
        from_chat_id: Union[int, str],
        message_id: int,
        message_thread_id: Optional[int] = None,
        disable_notification: Optional[bool] = None,
        schedule_date: Optional[datetime] = None,
        hide_sender_name: Optional[bool] = None,
        hide_captions: Optional[bool] = None,
        protect_content: Optional[bool] = None,
        allow_paid_broadcast: Optional[bool] = None,
        reply_parameters: Optional["types.ReplyParameters"] = None,
        paid_message_star_count: Optional[int] = None
    ) -> List["types.Message"]:
        """Forward a media group by providing one of the message ids.

        .. include:: /_includes/usable-by/users-bots.rst

        Parameters:
            chat_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target chat.
                For your personal cloud (Saved Messages) you can simply use "me" or "self".
                For a contact that exists in your Telegram address book you can use his phone number (str).

            from_chat_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the source chat where the original message was sent.
                For your personal cloud (Saved Messages) you can simply use "me" or "self".
                For a contact that exists in your Telegram address book you can use his phone number (str).

            message_id (``int``):
                Message identifier in the chat specified in *from_chat_id*.

            message_thread_id (``int``, *optional*):
                Unique identifier of a message thread to which the message belongs.
                For supergroups only.

            disable_notification (``bool``, *optional*):
                Sends the message silently.
                Users will receive a notification with no sound.

            schedule_date (:py:obj:`~datetime.datetime`, *optional*):
                Date when the message will be automatically sent.

            hide_sender_name (``bool``, *optional*):
                If True, the original author of the message will not be shown.

            hide_captions (``bool``, *optional*):
                If True, the original media captions will be removed.

            protect_content (``bool``, *optional*):
                Protects the contents of the sent message from forwarding and saving.

            allow_paid_broadcast (``bool``, *optional*):
                If True, you will be allowed to send up to 1000 messages per second.
                Ignoring broadcasting limits for a fee of 0.1 Telegram Stars per message.
                The relevant Stars will be withdrawn from the bot's balance.
                For bots only.

            reply_parameters (:obj:`~pyrogram.types.ReplyParameters`, *optional*):
                Describes reply parameters for the message that is being sent.

            paid_message_star_count (``int``, *optional*):
                The number of Telegram Stars the user agreed to pay to send the messages.

        Returns:
            List of :obj:`~pyrogram.types.Message`: On success, a list of forwarded messages is returned.

        Example:
            .. code-block:: python

                # Forward a media group
                await app.forward_media_group(to_chat, from_chat, 123)
        """
        message_ids = [i.id for i in await self.get_media_group(from_chat_id, message_id)]

        r = await self.invoke(
            raw.functions.messages.ForwardMessages(
                to_peer=await self.resolve_peer(chat_id),
                from_peer=await self.resolve_peer(from_chat_id),
                id=message_ids,
                silent=disable_notification or None,
                random_id=[self.rnd_id() for _ in message_ids],
                schedule_date=utils.datetime_to_timestamp(schedule_date),
                drop_author=hide_sender_name,
                drop_media_captions=hide_captions,
                noforwards=protect_content,
                allow_paid_floodskip=allow_paid_broadcast,
                reply_to=await utils.get_reply_to(
                    client=self,
                    reply_parameters=reply_parameters,
                    message_thread_id=message_thread_id
                ),
                allow_paid_stars=paid_message_star_count
            )
        )

        return await utils.parse_messages(client=self, messages=r)
