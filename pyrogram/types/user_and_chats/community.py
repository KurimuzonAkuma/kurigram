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
from typing import Optional, Union

import pyrogram
from pyrogram import raw, types, utils

from ..object import Object

log = logging.getLogger(__name__)


class Community(Object):
    """Represents a community (a group of chats).

    Parameters:
        id (``int``):
            Unique identifier for this chat.

        have_access (``bool``):
            If false, the community is inaccessible, and the only information known about the community is inside this class.
            Identifier of the community can't be passed to any method

        name (``str``, *optional*):
            Unique identifier for this community.

        photo (:obj:`~pyrogram.types.ChatPhoto`, *optional*):
            Community photo.
            Suitable for downloads only.

        date (:py:obj:`~datetime.datetime`, *optional*):
            Date when the community was joined, or the point in time when the community was created, in case the user is not a member of any chat in the community.

        status (:obj:`~pyrogram.types.CommunityMemberStatus`, *optional*):
            Status of the current user in the community.

        permissions (:obj:`~pyrogram.types.CommunityPermissions`, *optional*):
            Actions that non-administrator community members are allowed to take in the community.
    """

    def __init__(
        self,
        *,
        client: Optional["pyrogram.Client"] = None,
        id: Optional[int] = None,
        have_access: Optional[bool] = None,
        name: Optional[str] = None,
        photo: Optional["types.ChatPhoto"] = None,
        date: Optional[datetime] = None,
        status: Optional["types.CommunityMemberStatus"] = None,
        permissions: Optional["types.CommunityPermissions"] = None,
        raw: "raw.base.Chat",
    ):
        super().__init__(client)

        self.id = id
        self.have_access = have_access
        self.name = name
        self.photo = photo
        self.date = date
        self.status = status
        self.permissions = permissions
        self.raw = raw

    @staticmethod
    def _parse(
        client: "pyrogram.Client", community: Union["raw.types.Community", "raw.types.CommunityForbidden"]
    ) -> Optional["Community"]:
        if isinstance(community, raw.types.CommunityForbidden):
            return Community(
                id=utils.get_channel_id(community.id),
                have_access=False,
                name=community.title,
                raw=community,
                client=client,
            )

        if isinstance(community, raw.types.Community):
            return Community(
                id=utils.get_channel_id(community.id),
                have_access=bool(community.access_hash),
                name=community.title,
                photo=types.ChatPhoto._parse(
                    client, community.photo, utils.get_channel_id(community.id), community.access_hash or 0
                ),
                date=utils.timestamp_to_datetime(community.date),
                status=types.CommunityMemberStatus._parse(community),
                permissions=types.CommunityPermissions._parse(community.default_banned_rights),
                raw=community,
                client=client,
            )
