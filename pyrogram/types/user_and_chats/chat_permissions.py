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
from typing import Optional

from pyrogram import raw, utils

from ..object import Object

log = logging.getLogger(__name__)

class ChatPermissions(Object):
    """Describes actions that a non-administrator user is allowed to take in a chat.

    Parameters:
        can_send_messages (``bool``, *optional*):
            True, if the user is allowed to send text messages, contacts, locations and venues.

        can_send_audios (``bool``, *optional*):
            True, if the user is allowed to send audios.
            Implies can_send_messages

        can_send_documents (``bool``, *optional*):
            True, if the user is allowed to send documents.
            Implies can_send_messages

        can_send_photos (``bool``, *optional*):
            True, if the user is allowed to send photos.
            Implies can_send_messages

        can_send_videos (``bool``, *optional*):
            True, if the user is allowed to send videos.
            Implies can_send_messages

        can_send_video_notes (``bool``, *optional*):
            True, if the user is allowed to send video notes.
            Implies can_send_messages

        can_send_voice_notes (``bool``, *optional*):
            True, if the user is allowed to send voice notes.
            Implies can_send_messages

        can_send_polls (``bool``, *optional*):
            True, if the user is allowed to send polls.
            Implies can_send_messages

        can_send_other_messages (``bool``, *optional*):
            True, if the user is allowed to send animations, games, stickers and use inline bots.

        can_add_web_page_previews (``bool``, *optional*):
            True, if the user is allowed to add web page previews to their messages.

        can_react_to_messages (``bool``, *optional*):
            True, if the user is allowed to react to messages.
            If omitted, defaults to the value of can_send_messages.

        can_edit_tag (``bool``, *optional*):
            True, if the user is allowed to edit their own tag.

        can_change_info (``bool``, *optional*):
            True, if the user is allowed to change the chat title, photo and other settings.
            Ignored in public supergroups

        can_invite_users (``bool``, *optional*):
            True, if the user is allowed to invite new users to the chat.

        can_pin_messages (``bool``, *optional*):
            True, if the user is allowed to pin messages.
            Ignored in public supergroups.

        can_manage_topics (``bool``, *optional*):
            True, if the user is allowed to create, rename, close, and reopen forum topics.
            Supergroups only.
    """

    def __init__(
        self,
        *,
        can_send_messages: Optional[bool] = None,  # Text, contacts, locations and venues
        can_send_audios: Optional[bool] = None,
        can_send_documents: Optional[bool] = None,
        can_send_photos: Optional[bool] = None,
        can_send_videos: Optional[bool] = None,
        can_send_video_notes: Optional[bool] = None,
        can_send_voice_notes: Optional[bool] = None,
        can_send_polls: Optional[bool] = None,
        can_send_other_messages: Optional[bool] = None,  # Stickers, animations, games, inline bots
        can_add_web_page_previews: Optional[bool] = None,
        can_react_to_messages: Optional[bool] = None,
        can_edit_tag: Optional[bool] = None,
        can_change_info: Optional[bool] = None,
        can_invite_users: Optional[bool] = None,
        can_pin_messages: Optional[bool] = None,
        can_manage_topics: Optional[bool] = None,

        can_send_media_messages: Optional[bool] = None,  # Audio files, documents, photos, videos, video notes and voice notes. Deprecated
    ):
        super().__init__(None)

        self.can_send_messages = can_send_messages
        self.can_send_audios = can_send_audios
        self.can_send_documents = can_send_documents
        self.can_send_photos = can_send_photos
        self.can_send_videos = can_send_videos
        self.can_send_video_notes = can_send_video_notes
        self.can_send_voice_notes = can_send_voice_notes
        self.can_send_polls = can_send_polls
        self.can_send_other_messages = can_send_other_messages
        self.can_add_web_page_previews = can_add_web_page_previews
        self.can_react_to_messages = can_react_to_messages
        self.can_edit_tag = can_edit_tag
        self.can_change_info = can_change_info
        self.can_invite_users = can_invite_users
        self.can_pin_messages = can_pin_messages
        self.can_manage_topics = can_manage_topics

        self.can_send_media_messages = can_send_media_messages

    @staticmethod
    def _parse(denied_permissions: "raw.base.ChatBannedRights") -> Optional["ChatPermissions"]:
        if isinstance(denied_permissions, raw.types.ChatBannedRights):
            return ChatPermissions(
                can_send_messages=not denied_permissions.send_messages,
                can_send_audios=not denied_permissions.send_audios,
                can_send_documents=not denied_permissions.send_docs,
                can_send_photos=not denied_permissions.send_photos,
                can_send_videos=not denied_permissions.send_videos,
                can_send_video_notes=not denied_permissions.send_roundvideos,
                can_send_voice_notes=not denied_permissions.send_voices,
                can_send_polls=not denied_permissions.send_polls,
                can_send_other_messages=any([
                    not denied_permissions.send_stickers,
                    not denied_permissions.send_gifs,
                    not denied_permissions.send_games,
                    not denied_permissions.send_inline
                ]),
                can_add_web_page_previews=not denied_permissions.embed_links,
                can_react_to_messages=not denied_permissions.send_reactions,
                can_edit_tag=not denied_permissions.edit_rank,
                can_change_info=not denied_permissions.change_info,
                can_invite_users=not denied_permissions.invite_users,
                can_pin_messages=not denied_permissions.pin_messages,
                can_manage_topics=not denied_permissions.manage_topics
            )

    def write(self, until_date: datetime = utils.zero_datetime()) -> "raw.types.ChatBannedRights":
        send_messages = not self.can_send_messages
        send_audios = not self.can_send_audios
        send_docs = not self.can_send_documents
        send_photos = not self.can_send_photos
        send_videos = not self.can_send_videos
        send_roundvideos = not self.can_send_video_notes
        send_voices = not self.can_send_voice_notes
        send_media = None

        # Because of backward compatibility
        if self.can_send_media_messages is not None:
            log.warning(
                "`can_send_media_messages` is deprecated and will be removed in future updates. "
                "Use `can_send_messages`, `can_send_audios`, `can_send_documents`, `can_send_photos`, `can_send_videos`, `can_send_video_notes`, `can_send_voice_notes`, `can_send_polls` instead."
            )

            send_media = not self.can_send_media_messages
            send_audios = None
            send_docs = None
            send_photos = None
            send_videos = None
            send_roundvideos = None
            send_voices = None

        return raw.types.ChatBannedRights(
            until_date=utils.datetime_to_timestamp(until_date),
            # view_messages
            send_messages=send_messages,
            send_audios=send_audios,
            send_docs=send_docs,
            send_photos=send_photos,
            send_videos=send_videos,
            send_roundvideos=send_roundvideos,
            send_voices=send_voices,
            send_polls=not self.can_send_polls,
            send_stickers=not self.can_send_other_messages,
            send_gifs=not self.can_send_other_messages,
            send_games=not self.can_send_other_messages,
            send_inline=not self.can_send_other_messages,
            embed_links=not self.can_add_web_page_previews,
            send_reactions=not self.can_react_to_messages if self.can_react_to_messages is not None else not self.can_send_messages,
            edit_rank=not self.can_edit_tag,
            change_info=not self.can_change_info,
            invite_users=not self.can_invite_users,
            pin_messages=not self.can_pin_messages,
            manage_topics=not self.can_manage_topics,
            # send_plain

            send_media=send_media
        )
