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
from typing import Dict, List, Optional, Union

import pyrogram
from pyrogram import enums, raw, types, utils

from ..object import Object
from ..update import Update
from .message import Str

log = logging.getLogger(__name__)


class EphemeralMessage(Object, Update):
    """An ephemeral message.

    Ephemeral messages are lightweight, transient messages exchanged between a bot and a single
    receiving user. Unlike regular messages, they are not part of the chat history: they can't be
    forwarded, searched or fetched later on, and only exist for as long as Telegram keeps them around.

    Parameters:
        id (``int``):
            Unique identifier of the ephemeral message.

        from_user (:obj:`~pyrogram.types.User`, *optional*):
            Sender of the message.

        chat (:obj:`~pyrogram.types.Chat`, *optional*):
            Conversation the message was exchanged in.

        receiver (:obj:`~pyrogram.types.User`, *optional*):
            The only user allowed to see this message.

        date (:py:obj:`~datetime.datetime`, *optional*):
            Date the message was sent.

        outgoing (``bool``, *optional*):
            True, if the message is outgoing.

        message_thread_id (``int``, *optional*):
            Unique identifier of the forum topic the message belongs to, for forums only.

        text (``str``, *optional*):
            Text of the message, for text messages.

        caption (``str``, *optional*):
            Caption for the media, for media messages.

        entities (List of :obj:`~pyrogram.types.MessageEntity`, *optional*):
            For text messages, special entities like usernames, URLs, bot commands, etc. that appear
            in the text.

        caption_entities (List of :obj:`~pyrogram.types.MessageEntity`, *optional*):
            For messages with a caption, special entities like usernames, URLs, bot commands, etc.
            that appear in the caption.

        media (:obj:`~pyrogram.enums.MessageMediaType`, *optional*):
            The media type of the message, if it is a media message.

        photo (:obj:`~pyrogram.types.Photo`, *optional*):
            Message is a photo, information about the photo.

        animation (:obj:`~pyrogram.types.Animation`, *optional*):
            Message is an animation, information about the animation.

        audio (:obj:`~pyrogram.types.Audio`, *optional*):
            Message is an audio file, information about the file.

        document (:obj:`~pyrogram.types.Document`, *optional*):
            Message is a general file, information about the file.

        sticker (:obj:`~pyrogram.types.Sticker`, *optional*):
            Message is a sticker, information about the sticker.

        video (:obj:`~pyrogram.types.Video`, *optional*):
            Message is a video, information about the video.

        video_note (:obj:`~pyrogram.types.VideoNote`, *optional*):
            Message is a video note, information about the video message.

        voice (:obj:`~pyrogram.types.Voice`, *optional*):
            Message is a voice message, information about the file.

        has_media_spoiler (``bool``, *optional*):
            True, if the message media is covered by a spoiler animation.

        reply_markup (:obj:`~pyrogram.types.InlineKeyboardMarkup`, *optional*):
            Additional interface options attached to the message.

        reply_to_message_id (``int``, *optional*):
            The id of the ephemeral message this message is replying to, if any.
    """

    def __init__(
        self,
        *,
        client: "pyrogram.Client" = None,
        id: int,
        from_user: "types.User" = None,
        chat: "types.Chat" = None,
        receiver: "types.User" = None,
        date: datetime = None,
        outgoing: bool = None,
        message_thread_id: int = None,
        text: Str = None,
        caption: Str = None,
        entities: List["types.MessageEntity"] = None,
        caption_entities: List["types.MessageEntity"] = None,
        media: "enums.MessageMediaType" = None,
        photo: "types.Photo" = None,
        animation: "types.Animation" = None,
        audio: "types.Audio" = None,
        document: "types.Document" = None,
        sticker: "types.Sticker" = None,
        video: "types.Video" = None,
        video_note: "types.VideoNote" = None,
        voice: "types.Voice" = None,
        has_media_spoiler: bool = None,
        reply_markup: Union[
            "types.InlineKeyboardMarkup",
            "types.ReplyKeyboardMarkup",
            "types.ReplyKeyboardRemove",
            "types.ForceReply",
        ] = None,
        reply_to_message_id: int = None,
        raw: "raw.types.EphemeralMessage" = None,
    ):
        super().__init__(client)

        self.id = id
        self.from_user = from_user
        self.chat = chat
        self.receiver = receiver
        self.date = date
        self.outgoing = outgoing
        self.message_thread_id = message_thread_id
        self.text = text
        self.caption = caption
        self.entities = entities
        self.caption_entities = caption_entities
        self.media = media
        self.photo = photo
        self.animation = animation
        self.audio = audio
        self.document = document
        self.sticker = sticker
        self.video = video
        self.video_note = video_note
        self.voice = voice
        self.has_media_spoiler = has_media_spoiler
        self.reply_markup = reply_markup
        self.reply_to_message_id = reply_to_message_id
        self.raw = raw

    @staticmethod
    async def _parse(
        client: "pyrogram.Client",
        message: "raw.types.EphemeralMessage",
        users: Dict[int, "raw.base.User"],
        chats: Dict[int, "raw.base.Chat"],
    ) -> "EphemeralMessage":
        entities = types.List(
            filter(
                lambda x: x is not None,
                [types.MessageEntity._parse(client, entity, users) for entity in message.entities or []]
            )
        )

        media_type = None
        media = message.media
        photo = None
        animation = None
        audio = None
        document = None
        sticker = None
        video = None
        video_note = None
        voice = None
        has_media_spoiler = None

        if media:
            if isinstance(media, raw.types.MessageMediaPhoto):
                media_type = enums.MessageMediaType.PHOTO
                photo = types.Photo._parse(client, media.photo, media.ttl_seconds)
                has_media_spoiler = media.spoiler
            elif isinstance(media, raw.types.MessageMediaDocument):
                doc = media.document
                has_media_spoiler = media.spoiler

                if isinstance(doc, raw.types.Document):
                    attributes = {type(i): i for i in doc.attributes}

                    file_name = getattr(
                        attributes.get(raw.types.DocumentAttributeFilename, None),
                        "file_name",
                        None
                    )

                    if raw.types.DocumentAttributeAnimated in attributes:
                        video_attributes = attributes.get(raw.types.DocumentAttributeVideo, None)
                        animation = types.Animation._parse(client, doc, video_attributes, file_name)
                        media_type = enums.MessageMediaType.ANIMATION
                    elif raw.types.DocumentAttributeSticker in attributes:
                        sticker = await types.Sticker._parse(client, doc, attributes)
                        media_type = enums.MessageMediaType.STICKER
                    elif raw.types.DocumentAttributeVideo in attributes:
                        video_attributes = attributes[raw.types.DocumentAttributeVideo]

                        if video_attributes.round_message:
                            video_note = types.VideoNote._parse(client, doc, video_attributes, media.ttl_seconds)
                            media_type = enums.MessageMediaType.VIDEO_NOTE
                        else:
                            video = types.Video._parse(
                                client, doc, video_attributes, file_name, media.ttl_seconds,
                                getattr(media, "video_cover", None),
                                getattr(media, "video_timestamp", None),
                                getattr(media, "alt_documents", None),
                            )
                            media_type = enums.MessageMediaType.VIDEO
                    elif raw.types.DocumentAttributeAudio in attributes:
                        audio_attributes = attributes[raw.types.DocumentAttributeAudio]

                        if audio_attributes.voice:
                            voice = types.Voice._parse(client, doc, audio_attributes, media.ttl_seconds)
                            media_type = enums.MessageMediaType.VOICE
                        else:
                            audio = types.Audio._parse(client, doc, audio_attributes, file_name)
                            media_type = enums.MessageMediaType.AUDIO
                    else:
                        document = types.Document._parse(client, doc, file_name)
                        media_type = enums.MessageMediaType.DOCUMENT
            else:
                media_type = enums.MessageMediaType.UNSUPPORTED
                media = None

        reply_markup = message.reply_markup

        if reply_markup:
            if isinstance(reply_markup, raw.types.ReplyKeyboardForceReply):
                reply_markup = types.ForceReply.read(reply_markup)
            elif isinstance(reply_markup, raw.types.ReplyKeyboardMarkup):
                reply_markup = types.ReplyKeyboardMarkup.read(reply_markup)
            elif isinstance(reply_markup, raw.types.ReplyInlineMarkup):
                reply_markup = types.InlineKeyboardMarkup.read(reply_markup)
            elif isinstance(reply_markup, raw.types.ReplyKeyboardHide):
                reply_markup = types.ReplyKeyboardRemove.read(reply_markup)
            else:
                reply_markup = None

        return EphemeralMessage(
            id=message.id,
            from_user=types.User._parse(client, users.get(utils.get_raw_peer_id(message.from_id))),
            chat=types.Chat._parse(client, message, users, chats, is_chat=True),
            receiver=types.User._parse(client, users.get(message.receiver_id)),
            date=utils.timestamp_to_datetime(message.date),
            outgoing=message.out,
            message_thread_id=message.top_msg_id,
            text=Str(message.message).init(entities) or None if media_type is None else None,
            caption=Str(message.message).init(entities) or None if media_type is not None else None,
            entities=entities or None if media_type is None else None,
            caption_entities=entities or None if media_type is not None else None,
            media=media_type,
            photo=photo,
            animation=animation,
            audio=audio,
            document=document,
            sticker=sticker,
            video=video,
            video_note=video_note,
            voice=voice,
            has_media_spoiler=has_media_spoiler,
            reply_markup=reply_markup,
            reply_to_message_id=getattr(message.reply_to, "reply_to_msg_id", None) or getattr(message.reply_to, "id", None),
            raw=message,
            client=client,
        )

    @staticmethod
    def _parse_deleted(
        client: "pyrogram.Client",
        update: "raw.types.UpdateDeleteEphemeralMessages",
        users: Dict[int, "raw.base.User"],
        chats: Dict[int, "raw.base.Chat"],
    ) -> List["EphemeralMessage"]:
        peer = getattr(update, "peer", None)
        chat = None

        if peer:
            chat_id = utils.get_raw_peer_id(peer)

            if isinstance(peer, raw.types.PeerUser):
                chat = types.Chat._parse_user_chat(client, users.get(chat_id))
            elif isinstance(peer, raw.types.PeerChat):
                chat = types.Chat._parse_chat_chat(client, chats.get(chat_id))
            else:
                chat = types.Chat._parse_channel_chat(client, chats.get(chat_id))

        return types.List(
            EphemeralMessage(id=message_id, chat=chat, client=client)
            for message_id in update.ids
        )

    @property
    def content(self) -> Str:
        return self.text or self.caption or Str("").init([])

    async def reply(
        self,
        text: str = "",
        entities: List["types.MessageEntity"] = None,
        media: "types.InputMedia" = None,
        reply_markup: Union[
            "types.InlineKeyboardMarkup",
            "types.ReplyKeyboardMarkup",
            "types.ReplyKeyboardRemove",
            "types.ForceReply",
        ] = None,
    ) -> "EphemeralMessage":
        """Bound method *reply* of :obj:`~pyrogram.types.EphemeralMessage`.

        Use this method as a shortcut for:

        .. code-block:: python

            await client.send_ephemeral_message(
                chat_id=message.chat.id,
                receiver_id=message.receiver.id,
                text="hello",
                reply_to_message_id=message.id
            )

        Example:
            .. code-block:: python

                await message.reply("hello")

        Parameters:
            text (``str``, *optional*):
                Text of the message to be sent.

            entities (List of :obj:`~pyrogram.types.MessageEntity`, *optional*):
                List of special entities that appear in the message text, which can be specified
                instead of *parse_mode*.

            media (:obj:`~pyrogram.types.InputMedia`, *optional*):
                Media to attach to the message.

            reply_markup (:obj:`~pyrogram.types.InlineKeyboardMarkup`, *optional*):
                Additional interface options.

        Returns:
            :obj:`~pyrogram.types.EphemeralMessage`: On success, the sent ephemeral message is returned.
        """
        return await self._client.send_ephemeral_message(
            chat_id=self.chat.id,
            receiver_id=self.receiver.id,
            text=text,
            entities=entities,
            media=media,
            reply_markup=reply_markup,
            reply_to_message_id=self.id,
        )

    async def edit_text(
        self,
        text: str,
        entities: List["types.MessageEntity"] = None,
        reply_markup: "types.InlineKeyboardMarkup" = None,
    ) -> "EphemeralMessage":
        """Bound method *edit_text* of :obj:`~pyrogram.types.EphemeralMessage`.

        Use this method as a shortcut for:

        .. code-block:: python

            await client.edit_ephemeral_message_text(
                chat_id=message.chat.id,
                receiver_id=message.receiver.id,
                message_id=message.id,
                text="new text"
            )

        Example:
            .. code-block:: python

                await message.edit_text("new text")

        Parameters:
            text (``str``):
                New text of the message.

            entities (List of :obj:`~pyrogram.types.MessageEntity`, *optional*):
                List of special entities that appear in the message text, which can be specified
                instead of *parse_mode*.

            reply_markup (:obj:`~pyrogram.types.InlineKeyboardMarkup`, *optional*):
                An InlineKeyboardMarkup object.

        Returns:
            :obj:`~pyrogram.types.EphemeralMessage`: On success, the edited message is returned.
        """
        return await self._client.edit_ephemeral_message_text(
            chat_id=self.chat.id,
            receiver_id=self.receiver.id,
            message_id=self.id,
            text=text,
            entities=entities,
            reply_markup=reply_markup,
        )

    async def edit_media(
        self,
        media: "types.InputMedia",
        reply_markup: "types.InlineKeyboardMarkup" = None,
    ) -> "EphemeralMessage":
        """Bound method *edit_media* of :obj:`~pyrogram.types.EphemeralMessage`.

        Use this method as a shortcut for:

        .. code-block:: python

            await client.edit_ephemeral_message_media(
                chat_id=message.chat.id,
                receiver_id=message.receiver.id,
                message_id=message.id,
                media=media
            )

        Parameters:
            media (:obj:`~pyrogram.types.InputMedia`):
                One of the InputMedia objects describing an animation, audio, document, photo or video.

            reply_markup (:obj:`~pyrogram.types.InlineKeyboardMarkup`, *optional*):
                An InlineKeyboardMarkup object.

        Returns:
            :obj:`~pyrogram.types.EphemeralMessage`: On success, the edited message is returned.
        """
        return await self._client.edit_ephemeral_message_media(
            chat_id=self.chat.id,
            receiver_id=self.receiver.id,
            message_id=self.id,
            media=media,
            reply_markup=reply_markup,
        )

    async def delete(self) -> bool:
        """Bound method *delete* of :obj:`~pyrogram.types.EphemeralMessage`.

        Use this method as a shortcut for:

        .. code-block:: python

            await client.delete_ephemeral_messages(
                chat_id=message.chat.id,
                receiver_id=message.receiver.id,
                message_ids=message.id
            )

        Example:
            .. code-block:: python

                await message.delete()

        Returns:
            ``bool``: True on success.
        """
        return await self._client.delete_ephemeral_messages(
            chat_id=self.chat.id,
            receiver_id=self.receiver.id,
            message_ids=self.id,
        )

    async def report(self, option: bytes, message: str = "") -> "raw.base.ReportResult":
        """Bound method *report* of :obj:`~pyrogram.types.EphemeralMessage`.

        Use this method as a shortcut for:

        .. code-block:: python

            await client.report_ephemeral_message(
                chat_id=message.chat.id,
                message_id=message.id,
                option=option
            )

        Parameters:
            option (``bytes``):
                The option chosen from a previously received :obj:`~pyrogram.raw.base.ReportResult`.

            message (``str``, *optional*):
                An optional free-form message describing the report.

        Returns:
            :obj:`~pyrogram.raw.base.ReportResult`
        """
        return await self._client.report_ephemeral_message(
            chat_id=self.chat.id,
            message_id=self.id,
            option=option,
            message=message,
        )
