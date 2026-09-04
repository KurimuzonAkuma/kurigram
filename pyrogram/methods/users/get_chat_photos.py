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

from typing import AsyncGenerator, List, Union

import pyrogram
from pyrogram import raw, types, utils


async def get_chunk(
    client: "pyrogram.Client",
    peer: raw.types.InputPeerChannel,
    peer_id: int,
    peer_access_hash: int,
    offset: int = 0,
    limit: int = 100,
) -> List["types.ChatPhoto"]:
    r = await client.invoke(
        raw.functions.messages.Search(
            peer=peer,
            q="",
            filter=raw.types.InputMessagesFilterChatPhotos(),
            min_date=0,
            max_date=0,
            offset_id=0,
            add_offset=offset,
            limit=limit,
            max_id=0,
            min_id=0,
            hash=0,
        ),
        sleep_threshold=60,
    )

    photos = []

    for message in r.messages:
        if not isinstance(message, raw.types.MessageService):
            continue

        if not isinstance(message.action, raw.types.MessageActionChatEditPhoto):
            continue

        photos.append(
            await types.ChatPhoto._parse(
                client=client,
                chat_photo=message.action.photo,
                peer_id=peer_id,
                peer_access_hash=peer_access_hash,
            )
        )

    return photos


class GetChatPhotos:
    async def get_chat_photos(
        self: "pyrogram.Client",
        chat_id: Union[int, str],
        limit: int = 0,
    ) -> AsyncGenerator["types.ChatPhoto", None]:
        """Get a chat or a user profile photos sequentially.
        Personal and public photo aren't returned.

        .. include:: /_includes/usable-by/users-bots.rst

        Parameters:
            chat_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target chat.
                For your personal cloud (Saved Messages) you can simply use "me" or "self".

            limit (``int``, *optional*):
                Limits the number of profile photos to be retrieved.
                By default, no limit is applied and all profile photos are returned.

        Returns:
            ``Generator``: A generator yielding :obj:`~pyrogram.types.ChatPhoto` objects.

        Example:
            .. code-block:: python

                async for photo in app.get_chat_photos("me"):
                    print(photo)
        """
        peer = await self.resolve_peer(chat_id)

        if isinstance(peer, raw.types.InputPeerSelf):
            peer_id = self.me.id if self.me else None
            peer_access_hash = 0
        else:
            peer_id = utils.get_raw_peer_id(peer)
            peer_access_hash = peer.access_hash

        current = 0
        total = limit or (1 << 31)
        limit = min(100, total)
        offset = 0

        if isinstance(peer, raw.types.InputPeerChannel):
            current_photo = None

            r = await self.invoke(raw.functions.channels.GetFullChannel(channel=peer))

            if not isinstance(r.full_chat.chat_photo, raw.types.PhotoEmpty):
                current_photo = await types.ChatPhoto._parse(
                    client=self,
                    chat_photo=r.full_chat.chat_photo,
                    peer_id=peer_id,
                    peer_access_hash=peer_access_hash,
                )

                yield current_photo

                current += 1

                if current >= total:
                    return

            if self.me and not self.me.is_bot:
                while True:
                    photos = await get_chunk(
                        client=self,
                        peer=peer,
                        peer_id=peer_id,
                        peer_access_hash=peer_access_hash,
                        offset=offset,
                        limit=limit,
                    )

                    if not photos:
                        return

                    offset += len(photos)

                    for photo in photos:
                        if current_photo and current_photo.big_file_id == photo.big_file_id:
                            continue

                        yield photo

                        current += 1

                        if current >= total:
                            return

                    if len(photos) < limit:
                        return

        else:
            while True:
                r = await self.invoke(
                    raw.functions.photos.GetUserPhotos(
                        user_id=peer, offset=offset, max_id=0, limit=limit
                    )
                )

                photos = [
                    await types.ChatPhoto._parse(
                        client=self,
                        chat_photo=photo,
                        peer_id=peer_id,
                        peer_access_hash=peer_access_hash,
                    )
                    for photo in r.photos
                ]

                if not photos:
                    return

                offset += len(photos)

                for photo in photos:
                    yield photo

                    current += 1

                    if current >= total:
                        return
