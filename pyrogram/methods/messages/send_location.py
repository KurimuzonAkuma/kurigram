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

class SendLocation:
    async def send_location(
        self: "pyrogram.Client",
        chat_id: Union[int, str],
        latitude: float,
        longitude: float,
        horizontal_accuracy: float = None,
        live_period: int = None,
        heading: int = None,
        proximity_alert_radius: int = None,
        disable_notification: bool = None,
        message_thread_id: int = None,
        direct_messages_topic_id: int = None,
        effect_id: int = None,
        reply_parameters: "types.ReplyParameters" = None,
        suggested_post_parameters: "types.SuggestedPostParameters" = None,
        schedule_date: datetime = None,
        protect_content: bool = None,
        business_connection_id: str = None,
        allow_paid_broadcast: bool = None,
        paid_message_star_count: int = None,
        reply_markup: Union[
            "types.InlineKeyboardMarkup",
            "types.ReplyKeyboardMarkup",
            "types.ReplyKeyboardRemove",
            "types.ForceReply"
        ] = None,

        reply_to_message_id: int = None,
        reply_to_chat_id: Union[int, str] = None,
        quote_text: str = None,
        parse_mode: Optional["enums.ParseMode"] = None,
        quote_entities: List["types.MessageEntity"] = None,
        quote_offset: int = None,
    ) -> "types.Message":
        """Send points on the map.

        .. include:: /_includes/usable-by/users-bots.rst

        Parameters:
            chat_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target chat.
                For your personal cloud (Saved Messages) you can simply use "me" or "self".
                For a contact that exists in your Telegram address book you can use his phone number (str).

            latitude (``float``):
                Latitude of the location.

            longitude (``float``):
                Longitude of the location.

            horizontal_accuracy (``float``, *optional*):
                The radius of uncertainty for the location, measured in meters, 0-1500.

            live_period (``int``, *optional*):
                For live locations, a period for which the location can be updated, in seconds.
                Must be between 60 and 86400 for a temporary live location, 0x7FFFFFFF for permanent live location.

            heading (``int``, *optional*):
                For live locations, a direction in which the user is moving, in degrees.
                Must be between 1 and 360 if specified.

            proximity_alert_radius (``int``, *optional*):
                For live locations, a maximum distance for proximity alerts about approaching another chat member, in meters.
                Must be between 1 and 100000 if specified.
                Can't be enabled in channels and Saved Messages.

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
            :obj:`~pyrogram.types.Message`: On success, the sent location message is returned.

        Example:
            .. code-block:: python

                await app.send_location("me", latitude, longitude)
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

        if live_period is not None:
            media = raw.types.InputMediaGeoLive(
                geo_point=raw.types.InputGeoPoint(
                    lat=latitude,
                    long=longitude,
                    accuracy_radius=horizontal_accuracy
                ),
                heading=heading,
                period=live_period,
                proximity_notification_radius=proximity_alert_radius
            )
        else:
            media = raw.types.InputMediaGeoPoint(
                geo_point=raw.types.InputGeoPoint(
                    lat=latitude,
                    long=longitude,
                    accuracy_radius=horizontal_accuracy
                )
            )

        r = await self.invoke(
            raw.functions.messages.SendMedia(
                peer=await self.resolve_peer(chat_id),
                media=media,
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
            ),
            business_connection_id=business_connection_id
        )

        messages = await utils.parse_messages(client=self, messages=r)

        return messages[0] if messages else None
