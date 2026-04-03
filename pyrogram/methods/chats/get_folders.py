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

from typing import List

import pyrogram
from pyrogram import raw, types, utils


class GetFolders:
    async def get_folders(
        self: "pyrogram.Client"
    ) -> List["types.Folder"]:
        """Return information about a chat folders.

        .. include:: /_includes/usable-by/users.rst

        Returns:
            List of :obj:`~pyrogram.types.Folder`: On success, a list of folders is returned.

        Example:
            .. code-block:: python

                # Get all folders
                await app.get_folders()
        """
        dialog_filters = await self.invoke(raw.functions.messages.GetDialogFilters())

        raw_folders = [
            folder for folder in dialog_filters.filters
            if isinstance(folder, (raw.types.DialogFilter, raw.types.DialogFilterChatlist))
        ]

        if not raw_folders:
            return types.List()

        raw_peers = {}

        for folder in raw_folders:
            for peer in folder.pinned_peers + folder.include_peers + getattr(folder, "exclude_peers", []):
                raw_peers[utils.get_raw_peer_id(peer)] = peer

        users = {}
        chats = {}

        for i in range(0, len(raw_peers), 100):
            chunk = list(raw_peers.values())[i:i + 100]
            r = await self.invoke(
                raw.functions.messages.GetPeerDialogs(
                    peers=[raw.types.InputDialogPeer(peer=peer) for peer in chunk]
                )
            )
            users.update({i.id: i for i in r.users})
            chats.update({i.id: i for i in r.chats})

        return types.List(
            [
                await types.Folder._parse(self, folder, users, chats)
                for folder in raw_folders
            ]
        )
