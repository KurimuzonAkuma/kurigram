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
from typing import Dict, Optional

import pyrogram
from pyrogram import raw, types, utils
from ..object import Object


class GroupCallMember(Object):
    """Contains information about one member of a group call.

    Parameters:
        chat (:obj:`~pyrogram.types.Chat`, *optional*):
            Information about the user or chat.

        date (:py:obj:`~datetime.datetime`, *optional*):
            Date when this participant join this group call.

        active_date (:py:obj:`~datetime.datetime`, *optional*):
            Date when this participant last active in this group call.

        volume (``int``, *optional*):
            Volume, if not set the volume is set to 100%.

        can_self_unmute (``bool``, *optional*):
            Whether the participant can unmute themselves.

        is_muted (``bool``, *optional*):
            Whether the participant is muted.

        is_left (``bool``, *optional*):
            Whether the participant has left.

        is_just_joined (``bool``, *optional*):
            Whether the participant has just joined.

        is_muted_by_you (``bool``, *optional*):
            Whether this participant was muted by the current user.

        is_volume_by_admin (``bool``, *optional*):
            Whether our volume can only changed by an admin.

        is_self (``bool``, *optional*):
            Whether this participant is the current user.

        is_video_joined (``bool``, *optional*):
            Whether this participant is currently broadcasting video.

        is_hand_raised (``bool``, *optional*):
            Whether this participant is raised hand.

        is_video_enabled (``bool``, *optional*):
            Whether this participant is currently broadcasting video.

        is_screen_sharing_enabled (``bool``, *optional*):
            Whether this participant is currently shared screen.
    """

    def __init__(
        self,
        *,
        client: Optional["pyrogram.Client"] = None,
        chat: Optional["types.Chat"] = None,
        date: Optional[datetime] = None,
        active_date: Optional[datetime] = None,
        volume: Optional[int] = None,
        can_self_unmute: Optional[bool] = None,
        is_muted: Optional[bool] = None,
        is_left: Optional[bool] = None,
        is_just_joined: Optional[bool] = None,
        is_muted_by_you: Optional[bool] = None,
        is_volume_by_admin: Optional[bool] = None,
        is_self: Optional[bool] = None,
        is_video_joined: Optional[bool] = None,
        is_hand_raised: Optional[bool] = None,
        is_video_enabled: Optional[bool] = None,
        is_screen_sharing_enabled: Optional[bool] = None
    ):
        super().__init__(client)

        self.chat = chat
        self.date = date
        self.active_date = active_date
        self.volume = volume
        self.can_self_unmute = can_self_unmute
        self.is_muted = is_muted
        self.is_left = is_left
        self.is_just_joined = is_just_joined
        self.is_muted_by_you = is_muted_by_you
        self.is_volume_by_admin = is_volume_by_admin
        self.is_self = is_self
        self.is_video_joined = is_video_joined
        self.is_hand_raised = is_hand_raised
        self.is_video_enabled = is_video_enabled
        self.is_screen_sharing_enabled = is_screen_sharing_enabled

    @staticmethod
    def _parse(
        client: "pyrogram.Client",
        member: "raw.types.GroupCallParticipant",
        users: Dict[int, "raw.base.User"],
        chats: Dict[int, "raw.base.Chat"]
    ) -> "GroupCallMember":
        peer = member.peer
        peer_id = utils.get_raw_peer_id(peer)

        parsed_chat = types.Chat._parse_chat(
            client,
            users[peer_id] if isinstance(peer, raw.types.PeerUser) else chats[peer_id],
        )

        parsed_chat.bio = getattr(member, "about", None)

        return GroupCallMember(
            chat=parsed_chat,
            date=utils.timestamp_to_datetime(member.date),
            active_date=utils.timestamp_to_datetime(member.active_date),
            volume=getattr(member, "volume", None),
            can_self_unmute=member.can_self_unmute,
            is_muted=member.muted,
            is_left=member.left,
            is_just_joined=member.just_joined,
            is_muted_by_you=member.muted_by_you,
            is_volume_by_admin=member.volume_by_admin,
            is_self=member.is_self,
            is_video_joined=member.video_joined,
            is_hand_raised=bool(getattr(member, "raise_hand_rating", None)),
            is_video_enabled=bool(getattr(member, "video", None)),
            is_screen_sharing_enabled=bool(getattr(member, "presentation", None)),
            client=client
        )
