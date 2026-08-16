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
from typing import Union, AsyncIterator

import pyrogram
from pyrogram import types, raw, utils


class GetChatPhotos:
    async def get_chat_photos(
        self: "pyrogram.Client",
        chat_id: Union[int, str],
        limit: int = 0,
    ) -> AsyncIterator[Union["types.Photo", "types.Animation"]]:
        """Get a chat or a user profile photos sequentially.

        .. include:: /_includes/usable-by/users-bots.rst

        Parameters:
            chat_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target chat.
                For your personal cloud (Saved Messages) you can simply use "me" or "self".
                For a contact that exists in your Telegram address book you can use his phone number (str).

            limit (``int``, *optional*):
                Limits the number of profile photos to be retrieved.
                By default, no limit is applied and all profile photos are returned.

        Returns:
            ``Generator``: A generator yielding :obj:`~pyrogram.types.Photo` | :obj:`~pyrogram.types.Animation` objects.

        Example:
            .. code-block:: python

                async for photo in app.get_chat_photos("me"):
                    print(photo)
        """
        peer_id = await self.resolve_peer(chat_id)
        total = limit or (1 << 31)

        if isinstance(peer_id, raw.types.InputPeerChannel):
            r = await self.invoke(
                raw.functions.channels.GetFullChannel(
                    channel=peer_id
                )
            )

            photos = []
            current = (types.Animation._parse_chat_animation(
                self,
                r.full_chat.chat_photo,
                f"photo_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.mp4"
            ) or types.Photo._parse(self, r.full_chat.chat_photo))

            if current:
                photos.append(current)

            if not self.me.is_bot:
                search_limit = min(100, total)
                r = await utils.parse_messages(
                    self,
                    await self.invoke(
                        raw.functions.messages.Search(
                            peer=peer_id,
                            q="",
                            filter=raw.types.InputMessagesFilterChatPhotos(),
                            min_date=0,
                            max_date=0,
                            offset_id=0,
                            add_offset=0,
                            limit=search_limit,
                            max_id=0,
                            min_id=0,
                            hash=0
                        )
                    )
                )

                extra = [message.new_chat_photo for message in r]

                if extra:
                    if photos and photos[0].file_id == extra[0].file_id:
                        photos = extra
                    else:
                        photos.extend(extra)

            if not photos:
                return

            for i, photo in enumerate(photos):
                if i >= total:
                    return

                yield photo

            return

        current = 0
        offset = 0

        while current < total:
            _limit = min(100, total - current)
            r = await self.invoke(
                raw.functions.photos.GetUserPhotos(
                    user_id=peer_id,
                    offset=offset,
                    max_id=0,
                    limit=_limit,
                )
            )

            photos = [
                types.Animation._parse_chat_animation(
                    self,
                    photo,
                    f"photo_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.mp4"
                ) or types.Photo._parse(self, photo)
                for photo in r.photos
            ]

            if not photos:
                return

            offset += len(r.photos)

            for photo in photos:
                yield photo

                current += 1

                if current >= total:
                    return
