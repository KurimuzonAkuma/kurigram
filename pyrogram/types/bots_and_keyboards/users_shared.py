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

from typing import Dict, List, Union

import pyrogram
from pyrogram import raw, types, utils

from ..object import Object


class UsersShared(Object):
    """Contains information about a users shared with a bot.

    Parameters:
        button_id (``int``):
            Identifier of button.

        users (List of :obj:`~pyrogram.types.User`):
            List of requested users.
    """
    def __init__(
        self, *,
        button_id: int,
        users: List["types.User"],
    ):
        super().__init__()

        self.button_id = button_id
        self.users = users

    @staticmethod
    async def _parse(
        client: "pyrogram.Client",
        action: Union[
            "raw.types.MessageActionRequestedPeer",
            "raw.types.MessageActionRequestedPeerSentMe"
        ],
        users: Dict[int, "raw.base.User"] = {}
    ) -> "UsersShared":
        requested_users = types.List()

        for peer in action.peers:
            peer_id = utils.get_peer_id(peer)

            if isinstance(action, raw.types.MessageActionRequestedPeer):
                raw_user = users.get(utils.get_raw_peer_id(peer))

                if raw_user:
                    requested_users.append(await types.User._parse(client, raw_user))
                else:
                    requested_users.append(types.User(id=peer_id, client=client))
            elif isinstance(action, raw.types.MessageActionRequestedPeerSentMe):
                requested_users.append(
                    types.User(
                        id=peer_id,
                        first_name=getattr(peer, "first_name", None),
                        last_name=getattr(peer, "last_name", None),
                        username=getattr(peer, "username", None),
                        photo=types.Photo._parse(client, getattr(peer, "photo", None)),
                        client=client
                    )
                )

        return UsersShared(
            button_id=action.button_id,
            users=requested_users
        )
