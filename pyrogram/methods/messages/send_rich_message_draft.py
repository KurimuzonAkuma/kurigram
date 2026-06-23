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

from typing import Optional, Union

import pyrogram
from pyrogram import raw, types


class SendRichMessageDraft:
    async def send_rich_message_draft(
        self: "pyrogram.Client",
        chat_id: Union[int, str],
        draft_id: int,
        rich_message: "types.InputRichMessage",
        message_thread_id: Optional[int] = None,
    ) -> bool:
        """Use this method to stream a partial rich message to a user while the message is being generated.

        .. note::

            The streamed draft is ephemeral and acts as a temporary 30-second preview - once the output is finalized,
            you must call :meth:`~pyrogram.Client.send_rich_message` with the complete message to persist it in the user's chat.

        .. include:: /_includes/usable-by/bots.rst

        Parameters:
            chat_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target chat.

            draft_id (``int``):
                Unique identifier of the message draft, must be non-zero.
                Changes of drafts with the same identifier are animated.

            rich_message (:obj:`pyrogram.types.InputRichMessage`):
                The partial message to be streamed.

            message_thread_id (``int``, *optional*):
                Unique identifier for the target message thread.

        Returns:
            ``bool``: On success, True is returned.

        Example:
            .. code-block:: python


                text = "Hello! I'm your <b>Pyrogram bot</b>! How can I help you?"
                words = text.split()
                draft_id = app.rnd_id()

                # Send thinking placeholder
                await app.send_rich_message_draft(chat_id, draft_id)

                await asyncio.sleep(5)

                for i, word in enumerate(words):
                    await app.send_rich_message_draft(
                        chat_id=chat_id,
                        draft_id=draft_id,
                        rich_message=types.InputRichMessage(html=" ".join(words[:i+1])),
                    )

                    await asyncio.sleep(0.33)

                await app.send_rich_message(chat_id, text)

        """
        return await self.invoke(
            raw.functions.messages.SetTyping(
                peer=await self.resolve_peer(chat_id),
                action=raw.types.InputSendMessageRichMessageDraftAction(
                    random_id=draft_id,
                    rich_message=rich_message.write(),
                ),
                top_msg_id=message_thread_id,
            )
        )
