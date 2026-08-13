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
from datetime import datetime
from typing import List, Optional, Union

import pyrogram
from pyrogram import enums, raw, types, utils

log = logging.getLogger(__name__)

class SendVenue:
    async def send_venue(
        self: "pyrogram.Client",
        chat_id: Union[int, str],
        latitude: float,
        longitude: float,
        title: str,
        address: str,
        foursquare_id: str = "",
        foursquare_type: str = "",
        disable_notification: Optional[bool] = None,
        message_thread_id: Optional[int] = None,
        direct_messages_topic_id: Optional[int] = None,
        receiver_user_id: Optional[Union[int, str]] = None,
        callback_query_id: Optional[str] = None,
        effect_id: Optional[int] = None,
        reply_parameters: Optional["types.ReplyParameters"] = None,
        suggested_post_parameters: Optional["types.SuggestedPostParameters"] = None,
        schedule_date: Optional[datetime] = None,
        protect_content: Optional[bool] = None,
        business_connection_id: Optional[str] = None,
        allow_paid_broadcast: Optional[bool] = None,
        paid_message_star_count: Optional[int] = None,
        reply_markup: Optional[Union[
            "types.InlineKeyboardMarkup",
            "types.ReplyKeyboardMarkup",
            "types.ReplyKeyboardRemove",
            "types.ForceReply"
        ]] = None,

        reply_to_message_id: Optional[int] = None,
        reply_to_chat_id: Optional[Union[int, str]] = None,
        quote_text: Optional[str] = None,
        parse_mode: Optional["enums.ParseMode"] = None,
        quote_entities: Optional[List["types.MessageEntity"]] = None,
        quote_offset: Optional[int] = None,
    ) -> Optional["types.Message"]:
        """Send information about a venue.

        .. include:: /_includes/usable-by/users-bots.rst

        Parameters:
            chat_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target chat.
                For your personal cloud (Saved Messages) you can simply use "me" or "self".
                For a contact that exists in your Telegram address book you can use his phone number (str).

            latitude (``float``):
                Latitude of the venue.

            longitude (``float``):
                Longitude of the venue.

            title (``str``):
                Name of the venue.

            address (``str``):
                Address of the venue.

            foursquare_id (``str``, *optional*):
                Foursquare identifier of the venue.

            foursquare_type (``str``, *optional*):
                Foursquare type of the venue, if known.
                (For example, "arts_entertainment/default", "arts_entertainment/aquarium" or "food/icecream".)

            disable_notification (``bool``, *optional*):
                Sends the message silently.
                Users will receive a notification with no sound.

            message_thread_id (``int``, *optional*):
                Unique identifier for the target message thread (topic) of the forum.
                For forums only.

            direct_messages_topic_id (``int``, *optional*):
                Unique identifier of the topic in a channel direct messages chat administered by the current user.
                For direct chats only.only.

            receiver_user_id (``int`` | ``str``, *optional*):
                For outgoing ephemeral messages, unique identifier (int) or username (str) of the user who will receive the message.
                For group and supergroup chats only.
                It is not guaranteed that the user will receive the message, especially if they are offline.
                See `ephemeral message sending <https://core.telegram.org/bots/api#ephemeral-messages-and-commands>`__ for more details.

            callback_query_id (``str``, *optional*):
                For outgoing ephemeral messages, identifier of the callback query which triggered the message if any.

            effect_id (``int``, *optional*):
                Unique identifier of the message effect.
                For private chats only.

            reply_parameters (:obj:`~pyrogram.types.ReplyParameters`, *optional*):
                Describes reply parameters for the message that is being sent.

            suggested_post_parameters (:obj:`~pyrogram.types.SuggestedPostParameters`, *optional*):
                Information about the suggested post.

            schedule_date (:py:obj:`~datetime.datetime`, *optional*):
                Date when the message will be automatically sent.

            protect_content (``bool``, *optional*):
                Protects the contents of the sent message from forwarding and saving.

            business_connection_id (``str``, *optional*):
                Unique identifier of the business connection on behalf of which the message will be sent.

            allow_paid_broadcast (``bool``, *optional*):
                If True, you will be allowed to send up to 1000 messages per second.
                Ignoring broadcasting limits for a fee of 0.1 Telegram Stars per message.
                The relevant Stars will be withdrawn from the bot's balance.
                For bots only.

            paid_message_star_count (``int``, *optional*):
                The number of Telegram Stars the user agreed to pay to send the messages.

            reply_markup (:obj:`~pyrogram.types.InlineKeyboardMarkup` | :obj:`~pyrogram.types.ReplyKeyboardMarkup` | :obj:`~pyrogram.types.ReplyKeyboardRemove` | :obj:`~pyrogram.types.ForceReply`, *optional*):
                Additional interface options. An object for an inline keyboard, custom reply keyboard,
                instructions to remove reply keyboard or to force a reply from the user.

        Returns:
            :obj:`~pyrogram.types.Message` | ``None``: On success, the sent venue message is returned,
            otherwise, in case the server answered with no message, None is returned.

        Example:
            .. code-block:: python

                await app.send_venue(
                    "me", latitude, longitude,
                    "Venue title", "Venue address")
        """
        if any(
            (
                reply_to_message_id is not None,
                reply_to_chat_id is not None,
                quote_text is not None,
                parse_mode is not None,
                quote_entities is not None,
                quote_offset is not None,
            )
        ):
            if reply_to_message_id is not None:
                log.warning(
                    "`reply_to_message_id` is deprecated and will be removed in future updates. Use `reply_parameters` instead."
                )

            if reply_to_chat_id is not None:
                log.warning(
                    "`reply_to_chat_id` is deprecated and will be removed in future updates. Use `reply_parameters` instead."
                )

            if quote_text is not None:
                log.warning(
                    "`quote_text` is deprecated and will be removed in future updates. Use `reply_parameters` instead."
                )

            if parse_mode is not None:
                log.warning(
                    "`parse_mode` is deprecated and will be removed in future updates. Use `reply_parameters` instead."
                )

            if quote_entities is not None:
                log.warning(
                    "`quote_entities` is deprecated and will be removed in future updates. Use `reply_parameters` instead."
                )

            if quote_offset is not None:
                log.warning(
                    "`quote_offset` is deprecated and will be removed in future updates. Use `reply_parameters` instead."
                )

            reply_parameters = types.ReplyParameters(
                message_id=reply_to_message_id,
                chat_id=reply_to_chat_id,
                quote=quote_text,
                quote_parse_mode=parse_mode,
                quote_entities=quote_entities,
                quote_position=quote_offset
            )

        if receiver_user_id:
            rpc = raw.functions.ephemeral.SendMessage(
                peer=await self.resolve_peer(chat_id),
                receiver_id=await self.resolve_peer(receiver_user_id),
                query_id=int(callback_query_id) if callback_query_id is not None else None,
                media=raw.types.InputMediaVenue(
                    geo_point=raw.types.InputGeoPoint(
                        lat=latitude,
                        long=longitude
                    ),
                    title=title,
                    address=address,
                    provider="",
                    venue_id=foursquare_id or "",
                    venue_type=foursquare_type or ""
                ),
                reply_to=await utils.get_reply_to(
                    self,
                    reply_parameters,
                    message_thread_id,
                    direct_messages_topic_id
                ),
                random_id=self.rnd_id(),
                reply_markup=await reply_markup.write(self) if reply_markup else None,
                message=""
            )
        else:
            rpc = raw.functions.messages.SendMedia(
                peer=await self.resolve_peer(chat_id),
                media=raw.types.InputMediaVenue(
                    geo_point=raw.types.InputGeoPoint(
                        lat=latitude,
                        long=longitude
                    ),
                    title=title,
                    address=address,
                    provider="",
                    venue_id=foursquare_id or "",
                    venue_type=foursquare_type or ""
                ),
                message="",
                silent=disable_notification or None,
                reply_to=await utils.get_reply_to(
                    self,
                    reply_parameters,
                    message_thread_id,
                    direct_messages_topic_id
                ),
                random_id=self.rnd_id(),
                schedule_date=utils.datetime_to_timestamp(schedule_date),
                noforwards=protect_content,
                allow_paid_floodskip=allow_paid_broadcast,
                allow_paid_stars=paid_message_star_count,
                reply_markup=await reply_markup.write(self) if reply_markup else None,
                effect=effect_id,
                suggested_post=suggested_post_parameters.write() if suggested_post_parameters else None
            )

        r = await self.invoke(rpc, business_connection_id=business_connection_id)

        messages = await utils.parse_messages(client=self, messages=r)

        return messages[0] if messages else None
