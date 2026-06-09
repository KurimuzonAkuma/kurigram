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
from typing import Optional, Union

import pyrogram
from pyrogram import raw, types, utils


class BanChatMember:
    async def ban_chat_member(
        self: "pyrogram.Client",
        chat_id: Union[int, str],
        user_id: Union[int, str],
        until_date: datetime = utils.zero_datetime(),
        revoke_messages: Optional[bool] = None,
        revoke_reactions: Optional[bool] = None,
    ) -> Union["types.Message", bool]:
        """Ban a user from a group, a supergroup or a channel.
        In the case of supergroups and channels, the user will not be able to return to the group on their own using
        invite links, etc., unless unbanned first. You must be an administrator in the chat for this to work and must
        have the appropriate admin rights.

        .. include:: /_includes/usable-by/users-bots.rst

        Parameters:
            chat_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target chat.

            user_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target user.
                For a contact that exists in your Telegram address book you can use his phone number (str).

            until_date (:py:obj:`~datetime.datetime`, *optional*):
                Date when the user will be unbanned.
                If user is banned for more than 366 days or less than 30 seconds from the current time they are
                considered to be banned forever. Defaults to epoch (ban forever).

            revoke_messages (``bool``, *optional*):
                Pass True to delete all messages in the chat for the user who is being removed.

            revoke_reactions (``bool``, *optional*):
                Pass True to delete all reactions in the chat for the user who is being removed.

        Returns:
            :obj:`~pyrogram.types.Message` | ``bool``: On success, a service message will be returned (when applicable),
            otherwise, in case a message object couldn't be returned, True is returned.

        Example:
            .. code-block:: python

                from datetime import datetime, timedelta

                # Ban chat member forever
                await app.ban_chat_member(chat_id, user_id)

                # Ban chat member and automatically unban after 24h
                await app.ban_chat_member(chat_id, user_id, datetime.now() + timedelta(days=1))
        """
        chat_peer = await self.resolve_peer(chat_id)
        user_peer = await self.resolve_peer(user_id)

        if isinstance(chat_peer, (raw.types.InputPeerSelf, raw.types.InputPeerUser)):
            raise ValueError("Can't ban members in private chats")

        if isinstance(chat_peer, raw.types.InputPeerChannel):
            r = await self.invoke(
                raw.functions.channels.EditBanned(
                    channel=chat_peer,
                    participant=user_peer,
                    banned_rights=raw.types.ChatBannedRights(
                        until_date=utils.datetime_to_timestamp(until_date),
                        view_messages=True,
                        send_messages=True,
                        send_media=True,
                        send_stickers=True,
                        send_gifs=True,
                        send_games=True,
                        send_inline=True,
                        embed_links=True,
                    ),
                )
            )

            if revoke_messages:
                await self.invoke(
                    raw.functions.channels.DeleteParticipantHistory(
                        channel=chat_peer, participant=user_peer
                    )
                )
        else:
            if not isinstance(user_peer, raw.types.InputPeerUser):
                raise ValueError("Can't ban chats in basic groups")

            r = await self.invoke(
                raw.functions.messages.DeleteChatUser(
                    chat_id=abs(chat_id), user_id=user_peer, revoke_history=revoke_messages
                )
            )

        if revoke_reactions:
            await self.invoke(
                raw.functions.messages.DeleteParticipantReactions(
                    peer=chat_peer, participant=user_peer
                )
            )

        return next(iter(await utils.parse_messages(client=self, messages=r)), True)
