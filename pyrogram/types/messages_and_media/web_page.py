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

from typing import Optional

import pyrogram
from pyrogram import raw, types

from ..object import Object


class WebPage(Object):
    # TODO: hash, cached_page
    """A webpage preview

    Parameters:
        id (``str``):
            Unique identifier for this webpage.

        url (``str``):
            Full URL for this webpage.

        display_url (``str``, *optional*):
            Display URL for this webpage.

        type (``str``, *optional*):
            Type of webpage preview.
            One of the following:
            
            - video
            - gif
            - photo
            - document
            - profile
            - telegram_background
            - telegram_theme
            - telegram_story
            - telegram_channel
            - telegram_channel_request
            - telegram_megagroup
            - telegram_chat
            - telegram_megagroup_request
            - telegram_chat_request
            - telegram_album
            - telegram_message
            - telegram_bot
            - telegram_voicechat
            - telegram_livestream
            - telegram_user
            - telegram_botapp
            - telegram_channel_boost
            - telegram_group_boost
            - telegram_giftcode
            - telegram_stickerset

        site_name (``str``, *optional*):
            Webpage site name.

        title (``str``, *optional*):
            Title of this webpage.

        description (``str``, *optional*):
            Description of this webpage.

        audio (:obj:`~pyrogram.types.Audio`, *optional*):
            Webpage preview is an audio file, information about the file.

        document (:obj:`~pyrogram.types.Document`, *optional*):
            Webpage preview is a general file, information about the file.

        photo (:obj:`~pyrogram.types.Photo`, *optional*):
            Webpage preview is a photo, information about the photo.

        animation (:obj:`~pyrogram.types.Animation`, *optional*):
            Webpage preview is an animation, information about the animation.

        video (:obj:`~pyrogram.types.Video`, *optional*):
            Webpage preview is a video, information about the video.

        embed_url (``str``, *optional*):
            Embedded content URL.

        embed_type (``str``, *optional*):
            Embedded content type, like `iframe`

        embed_width (``int``, *optional*):
            Embedded content width.

        embed_height (``int``, *optional*):
            Embedded content height.

        has_large_media (``bool``, *optional*):
            Whether the webpage preview is large.

        prefer_large_media (``bool``, *optional*):
            Whether the webpage preview is large.

        prefer_small_media (``bool``, *optional*):
            Whether the webpage preview is small.

        manual (``bool``, *optional*):
            Whether the webpage preview was changed by the user.

        safe (``bool``, *optional*):
            Whether the webpage preview is safe.

        duration (``int``, *optional*):
            Unknown at the time of writing.

        author (``str``, *optional*):
            Author of the webpage, eg the Twitter user for a tweet, or the author in an article.

        raw (:obj:`~pyrogram.raw.types.MessageMediaWebPage`):
            The raw version of this object.
    """

    def __init__(
        self,
        *,
        client: Optional["pyrogram.Client"] = None,
        id: str,
        url: str,
        display_url: Optional[str] = None,
        type: Optional[str] = None,
        site_name: Optional[str] = None,
        title: Optional[str] = None,
        description: Optional[str] = None,
        audio: Optional["types.Audio"] = None,
        document: Optional["types.Document"] = None,
        photo: Optional["types.Photo"] = None,
        animation: Optional["types.Animation"] = None,
        video: Optional["types.Video"] = None,
        embed_url: Optional[str] = None,
        embed_type: Optional[str] = None,
        embed_width: Optional[int] = None,
        embed_height: Optional[int] = None,
        has_large_media: Optional[bool] = None,
        prefer_large_media: Optional[bool] = None,
        prefer_small_media: Optional[bool] = None,
        manual: Optional[bool] = None,
        safe: Optional[bool] = None,
        duration: Optional[int] = None,
        author: Optional[str] = None,
        raw: Optional["raw.types.MessageMediaWebPage"] = None
    ):
        super().__init__(client)

        self.id = id
        self.url = url
        self.display_url = display_url
        self.type = type
        self.site_name = site_name
        self.title = title
        self.description = description
        self.audio = audio
        self.document = document
        self.photo = photo
        self.animation = animation
        self.video = video
        self.embed_url = embed_url
        self.embed_type = embed_type
        self.embed_width = embed_width
        self.embed_height = embed_height
        self.has_large_media = has_large_media
        self.prefer_large_media = prefer_large_media
        self.prefer_small_media = prefer_small_media
        self.manual = manual
        self.safe = safe
        self.duration = duration
        self.author = author
        self.raw = raw

    @staticmethod
    def _parse(
        client,
        media: "raw.types.MessageMediaWebPage"
    ) -> Optional["WebPage"]:
        if not media:
            return None

        if isinstance(media.webpage, raw.types.WebPageNotModified):
            return None

        audio = None
        document = None
        photo = None
        animation = None
        video = None

        webpage = media.webpage

        if isinstance(webpage, raw.types.WebPage):
            if isinstance(webpage.photo, raw.types.Photo):
                photo = types.Photo._parse(client, webpage.photo)

            doc = webpage.document

            if isinstance(doc, raw.types.Document):
                attributes = {type(i): i for i in doc.attributes}

                file_name = getattr(
                    attributes.get(
                        raw.types.DocumentAttributeFilename, None
                    ), "file_name", None
                )

                if raw.types.DocumentAttributeAudio in attributes:
                    audio_attributes = attributes[raw.types.DocumentAttributeAudio]
                    audio = types.Audio._parse(client, doc, audio_attributes, file_name)

                elif raw.types.DocumentAttributeAnimated in attributes:
                    video_attributes = attributes.get(raw.types.DocumentAttributeVideo, None)
                    animation = types.Animation._parse(client, doc, video_attributes, file_name)

                elif raw.types.DocumentAttributeVideo in attributes:
                    video_attributes = attributes[raw.types.DocumentAttributeVideo]
                    video = types.Video._parse(client, doc, video_attributes, file_name)

                else:
                    document = types.Document._parse(client, doc, file_name)

        return WebPage(
            id=str(webpage.id),
            url=webpage.url,
            display_url=getattr(webpage, "display_url", None),
            type=getattr(webpage, "type", None),
            site_name=getattr(webpage, "site_name", None),
            title=getattr(webpage, "title", None),
            description=getattr(webpage, "description", None),
            audio=audio,
            document=document,
            photo=photo,
            animation=animation,
            video=video,
            embed_url=getattr(webpage, "embed_url", None),
            embed_type=getattr(webpage, "embed_type", None),
            embed_width=getattr(webpage, "embed_width", None),
            embed_height=getattr(webpage, "embed_height", None),
            has_large_media=getattr(webpage, "has_large_media", None),
            prefer_large_media=media.force_large_media,
            prefer_small_media=media.force_small_media,
            manual=media.manual,
            safe=media.safe,
            duration=getattr(webpage, "duration", None),
            author=getattr(webpage, "author", None),
            raw=media
        )
