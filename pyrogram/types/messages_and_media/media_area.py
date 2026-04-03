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

from typing import Optional, Union

import pyrogram
from pyrogram import enums, raw, types
from pyrogram.errors import ChannelInvalid, ChannelPrivate

from ..object import Object


class MediaArea(Object):
    """Describes the media area added to a story.

    Parameters:
        x (``float``):
            The abscissa of the rectangle's center, as a percentage of the media width (0-100).

        y (``float``):
            The ordinate of the rectangle's center, as a percentage of the media height (0-100).

        width (``float``):
            The width of the rectangle, as a percentage of the media width (0-100).

        height (``float``):
            The height of the rectangle, as a percentage of the media height (0-100).

        rotation (``float``):
            Clockwise rotation angle of the rectangle, in degrees (0-360).

        type (:obj:`~pyrogram.enums.MediaAreaType`):
            The type of the media area.

        radius (``float``, *optional*):
            The radius of the rectangle corner rounding, as a percentage of the media width.

        sender_chat (:obj:`~pyrogram.types.Chat`, *optional*):
            The channel that posted the message.
            For post type only.

        message_id (``int``, *optional*):
            Identifier of the message in channel.
            For post type only.

        message (:obj:`~pyrogram.types.Message`, *optional*):
            Message attached to the story.
            Can be empty if the message was deleted or unavailable (channel is private).
            For post type only.

        location (:obj:`~pyrogram.types.Location`, *optional*):
            Represents a location tag attached to a story.
            For location type only.

        reaction (:obj:`~pyrogram.types.Reaction`, *optional*):
            The reaction that should be sent when this area is clicked.
            For reaction type only.

        is_dark (``bool``, *optional*):
            True if the reaction bubble has a dark background.
            For reaction type only.

        is_flipped (``bool``, *optional*):
            True if the reaction bubble is mirrored.
            For reaction type only.

        url (``str``, *optional*):
            URL to open when clicked.
            For url type only.

        emoji (``str``, *optional*):
            Weather emoji, should be rendered as an animated emoji.
            For weather type only.

        temperature (``float``, *optional*):
            Temperature in degrees Celsius.
            For weather type only.

        color (``int``, *optional*):
            The argb color in decimal format.
            For weather type only.

        gift (:obj:`~pyrogram.types.Gift`, *optional*):
            Information about this gift.
    """

    def __init__(
        self,
        *,
        client: "pyrogram.Client" = None,
        x: float,
        y: float,
        width: float,
        height: float,
        rotation: float,
        type: "enums.MediaAreaType",
        radius: float = None,
        sender_chat: Optional["types.Chat"] = None,
        message_id: Optional[int] = None,
        message: Optional["types.Message"] = None,
        location: Optional["types.Location"] = None,
        reaction: Optional["types.Reaction"] = None,
        is_dark: Optional[bool] = None,
        is_flipped: Optional[bool] = None,
        url: Optional[str] = None,
        venue: Optional["types.Venue"] = None,
        emoji: Optional[str] = None,
        temperature: Optional[float] = None,
        color: Optional[int] = None,
        gift: Optional["types.Gift"] = None
    ):
        super().__init__(client)

        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.rotation = rotation
        self.type = type
        self.radius = radius
        self.sender_chat = sender_chat
        self.message_id = message_id
        self.message = message
        self.location = location
        self.reaction = reaction
        self.is_dark = is_dark
        self.is_flipped = is_flipped
        self.url = url
        self.venue = venue
        self.emoji = emoji
        self.temperature = temperature
        self.color = color
        self.gift = gift

    @staticmethod
    async def _parse(
        client: "pyrogram.Client",
        area: "raw.base.MediaArea",
        chats: dict = None
    ) -> "MediaArea":
        sender_chat = None
        message_id = None
        message = None
        location = None
        reaction = None
        is_dark = None
        is_flipped = None
        url = None
        venue = None
        emoji = None
        temperature = None
        color = None
        gift = None

        if isinstance(area, raw.types.MediaAreaChannelPost):
            sender_chat = types.Chat._parse_channel_chat(client, chats.get(area.channel_id))
            message_id = area.msg_id

            try:
                message = await client.get_messages(chat_id=sender_chat.id, message_ids=message_id)
            except (ChannelPrivate, ChannelInvalid):
                pass
        elif isinstance(area, raw.types.MediaAreaGeoPoint):
            location = types.Location._parse(area.geo)
        elif isinstance(area, raw.types.MediaAreaSuggestedReaction):
            reaction = types.Reaction._parse(client, area.reaction)
            is_dark = getattr(area, "dark", None)
            is_flipped = getattr(area, "flipped", None)
        elif isinstance(area, raw.types.MediaAreaUrl):
            url = area.url
        elif isinstance(area, raw.types.MediaAreaVenue):
            venue = types.Venue._parse(client, area)
        elif isinstance(area, raw.types.MediaAreaWeather):
            emoji = area.emoji
            temperature = area.temperature_c
            color = area.color
        elif isinstance(area, raw.types.MediaAreaStarGift):
            gift = await client.get_upgraded_gift(area.slug)

        return MediaArea(
            x=area.coordinates.x,
            y=area.coordinates.y,
            width=area.coordinates.w,
            height=area.coordinates.h,
            rotation=area.coordinates.rotation,
            type=enums.MediaAreaType(type(area)),
            radius=getattr(area.coordinates, "radius", None),
            sender_chat=sender_chat,
            message_id=message_id,
            message=message,
            location=location,
            reaction=reaction,
            is_dark=is_dark,
            is_flipped=is_flipped,
            url=url,
            venue=venue,
            emoji=emoji,
            temperature=temperature,
            color=color,
            gift=gift,
            client=client
        )

    async def write(
        self, client: "pyrogram.Client"
    ) -> Optional[
        Union[
            "raw.types.InputMediaAreaChannelPost",
            "raw.types.MediaAreaGeoPoint",
            "raw.types.MediaAreaSuggestedReaction",
            "raw.types.MediaAreaUrl",
            "raw.types.MediaAreaWeather",
            "raw.types.MediaAreaStarGift"
        ]
    ]:
        coordinates = raw.types.MediaAreaCoordinates(
            x=self.x,
            y=self.y,
            w=self.width,
            h=self.height,
            rotation=self.rotation,
            radius=self.radius
        )

        if self.type == enums.MediaAreaType.POST:
            return raw.types.InputMediaAreaChannelPost(
                coordinates=coordinates,
                channel=await client.resolve_peer(self.sender_chat.id),
                msg_id=self.message_id
            )
        elif self.type == enums.MediaAreaType.LOCATION:
            return raw.types.MediaAreaGeoPoint(
                coordinates=coordinates,
                geo=raw.types.InputGeoPoint(
                    lat=self.location.latitude,
                    long=self.location.longitude,
                    accuracy_radius=self.location.accuracy_radius
                )
            )
        elif self.type == enums.MediaAreaType.REACTION:
            if self.reaction.custom_emoji_id:
                reaction = raw.types.ReactionCustomEmoji(
                    document_id=self.reaction.custom_emoji_id
                )
            else:
                reaction = raw.types.ReactionEmoji(
                    emoticon=self.reaction.emoji
                )

            return raw.types.MediaAreaSuggestedReaction(
                coordinates=coordinates,
                reaction=reaction,
                dark=self.is_dark,
                flipped=self.is_flipped
            )
        elif self.type == enums.MediaAreaType.URL:
            return raw.types.MediaAreaUrl(
                coordinates=coordinates,
                url=self.url
            )
        elif self.type == enums.MediaAreaType.WEATHER:
            return raw.types.MediaAreaWeather(
                coordinates=coordinates,
                emoji=self.emoji,
                temperature_c=self.temperature,
                color=self.color
            )
        elif self.type == enums.MediaAreaType.GIFT:
            return raw.types.MediaAreaStarGift(
                coordinates=coordinates,
                slug=self.gift.name
            )
