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

from typing import List, Optional, Union

import pyrogram
from pyrogram import raw


class MarkChecklistTasksAsDone:
    async def mark_checklist_tasks_as_done(
        self: "pyrogram.Client",
        chat_id: Union[int, str],
        message_id: int,
        *,
        marked_as_done_task_ids: Optional[List[int]] = None,
        marked_as_not_done_task_ids: Optional[List[int]] = None,
    ) -> int:
        """Add tasks of a checklist in a message as done or not done.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            chat_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target chat.
                For your personal cloud (Saved Messages) you can simply use "me" or "self".
                For a contact that exists in your Telegram address book you can use his phone number (str).

            message_id (``int``):
                Identifier of the message containing the checklist.

            marked_as_done_task_ids (List of ``int``):
                Identifiers of tasks that were marked as done.

            marked_as_not_done_task_ids (List of ``int``):
                Identifiers of tasks that were marked as not done.

        Returns:
            ``bool``: On success, True is returned.

        Example:
            .. code-block:: python

                await app.mark_checklist_tasks_as_done(
                    chat_id,
                    message_id,
                    marked_as_done_task_ids=[1, 2, 3]
                )
        """
        await self.invoke(
            raw.functions.messages.ToggleTodoCompleted(
                peer=await self.resolve_peer(chat_id),
                msg_id=message_id,
                completed=marked_as_done_task_ids or [],
                incompleted=marked_as_not_done_task_ids or [],
            )
        )

        return True
