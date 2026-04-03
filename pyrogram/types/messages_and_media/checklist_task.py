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
from typing import Dict, List, Optional

import pyrogram
from pyrogram import raw, types, utils

from ..object import Object


class ChecklistTask(Object):
    """Describes a task in a checklist.

    Parameters:
        id (``int``):
            Unique identifier of the task.

        text (``str``):
            Text of the task.

        entities (List of :obj:`~pyrogram.types.MessageEntity`, *optional*):
            Entities in the text of the task.
            May contain only Bold, Italic, Underline, Strikethrough, Spoiler, CustomEmoji, Url, EmailAddress, Mention, Hashtag, Cashtag and PhoneNumber entities.

        completed_by (:obj:`~pyrogram.types.Chat`, *optional*):
            The user or chat that completed the task.
            None if the task isn't completed.

        completion_date (:py:obj:`~datetime.datetime`, *optional*):
            Date when the task was completed.
            None if the task isn't completed.
    """

    def __init__(
        self,
        *,
        id: int,
        text: str,
        entities: Optional[List["types.MessageEntity"]] = None,
        completed_by: Optional["types.Chat"] = None,
        completion_date: Optional[datetime] = None,
    ):
        super().__init__()

        self.id = id
        self.text = text
        self.entities = entities
        self.completed_by = completed_by
        self.completion_date = completion_date

    @staticmethod
    def _parse(
        client: "pyrogram.Client",
        item: "raw.types.TodoItem",
        completion: Optional["raw.types.TodoCompletion"],
        users: Dict[int, "raw.base.User"],
        chats: Dict[int, "raw.base.Chat"],
    ) -> "ChecklistTask":
        text, entities = (
            utils.parse_text_with_entities(client, item.title, users)
        ).values()

        completed_by_peer_id = utils.get_raw_peer_id(getattr(completion, "completed_by", None))

        return ChecklistTask(
            id=item.id,
            text=text,
            entities=entities,
            completed_by=types.Chat._parse_chat(client, users.get(completed_by_peer_id) or chats.get(completed_by_peer_id)),
            completion_date=utils.timestamp_to_datetime(getattr(completion, "date", None))
        )
