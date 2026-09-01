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

from ..object import Object


class EphemeralMessageParameters(Object):
    """Describes reply parameters for the message that is being sent.

    Parameters:
        receiver_user_id (``int`` | ``str``):
            Identifier (int) or username (str) of the user who will receive the message.
            It is not guaranteed that the user will receive the message, especially if they are offline.
            See `here <https://core.telegram.org/bots/api#ephemeral-messages-and-commands>`__ for more details.

        callback_query_id (``str``, *optional*):
            Identifier of the callback query which triggered the message, if any.

        replace_callback_query_message (``bool``, *optional*):
            Pass *True* if the ephemeral message must be shown in place of the original message.
            Must be *False* for callback queries from ephemeral messages, which must be edited using regular *edit_ephemeral_message…* methods.
    """

    def __init__(
        self,
        *,
        receiver_user_id: Union[int, str],
        callback_query_id: Optional[str] = None,
        replace_callback_query_message: Optional[bool] = None,
    ):
        super().__init__()

        self.receiver_user_id = receiver_user_id
        self.callback_query_id = callback_query_id
        self.replace_callback_query_message = replace_callback_query_message
