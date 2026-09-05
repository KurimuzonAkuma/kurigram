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

from typing import Callable, Dict, Final, Optional, Union

import pyrogram
from pyrogram import raw, enums

# Every `enums.ChatAction` member maps to exactly one raw constructor here, so
#  building the raw action never has to inspect the enum member's name at
#  runtime, and each lambda is checked against its own concrete raw type
#  instead of the `raw.base.SendMessageAction` union `action.value` carries.
_ACTIONS: Final[Dict["enums.ChatAction", Callable[[], "raw.base.SendMessageAction"]]] = {
    enums.ChatAction.TYPING: raw.types.SendMessageTypingAction,
    enums.ChatAction.UPLOAD_PHOTO: lambda: raw.types.SendMessageUploadPhotoAction(progress=0),
    enums.ChatAction.RECORD_VIDEO: raw.types.SendMessageRecordVideoAction,
    enums.ChatAction.UPLOAD_VIDEO: lambda: raw.types.SendMessageUploadVideoAction(progress=0),
    enums.ChatAction.RECORD_AUDIO: raw.types.SendMessageRecordAudioAction,
    enums.ChatAction.UPLOAD_AUDIO: lambda: raw.types.SendMessageUploadAudioAction(progress=0),
    enums.ChatAction.UPLOAD_DOCUMENT: lambda: raw.types.SendMessageUploadDocumentAction(progress=0),
    enums.ChatAction.FIND_LOCATION: raw.types.SendMessageGeoLocationAction,
    enums.ChatAction.RECORD_VIDEO_NOTE: raw.types.SendMessageRecordRoundAction,
    enums.ChatAction.UPLOAD_VIDEO_NOTE: lambda: raw.types.SendMessageUploadRoundAction(progress=0),
    enums.ChatAction.PLAYING: raw.types.SendMessageGamePlayAction,
    enums.ChatAction.CHOOSE_CONTACT: raw.types.SendMessageChooseContactAction,
    enums.ChatAction.SPEAKING: raw.types.SpeakingInGroupCallAction,
    enums.ChatAction.IMPORT_HISTORY: lambda: raw.types.SendMessageHistoryImportAction(progress=0),
    enums.ChatAction.CHOOSE_STICKER: raw.types.SendMessageChooseStickerAction,
    enums.ChatAction.CANCEL: raw.types.SendMessageCancelAction,
}


class SendChatAction:
    async def send_chat_action(
        self: "pyrogram.Client",
        chat_id: Union[int, str],
        action: "enums.ChatAction",
        business_connection_id: Optional[str] = None
    ) -> bool:
        """Tell the other party that something is happening on your side.

        .. include:: /_includes/usable-by/users-bots.rst

        Parameters:
            chat_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target chat.
                For your personal cloud (Saved Messages) you can simply use "me" or "self".
                For a contact that exists in your Telegram address book you can use his phone number (str).

            action (:obj:`~pyrogram.enums.ChatAction`):
                Type of action to broadcast.

            business_connection_id (``str``, *optional*):
                Unique identifier of the business connection on behalf of which the message will be sent.

        Returns:
            ``bool``: On success, True is returned.

        Raises:
            ValueError: In case the provided string is not a valid chat action.

        Example:
            .. code-block:: python

                from pyrogram import enums

                # Send "typing" chat action
                await app.send_chat_action(chat_id, enums.ChatAction.TYPING)

                # Send "upload_video" chat action
                await app.send_chat_action(chat_id, enums.ChatAction.UPLOAD_VIDEO)

                # Send "playing" chat action
                await app.send_chat_action(chat_id, enums.ChatAction.PLAYING)

                # Cancel any current chat action
                await app.send_chat_action(chat_id, enums.ChatAction.CANCEL)
        """

        return await self.invoke(
            raw.functions.messages.SetTyping(
                peer=await self.resolve_peer(chat_id),
                action=_ACTIONS[action]()
            ),
            business_connection_id=business_connection_id
        )
