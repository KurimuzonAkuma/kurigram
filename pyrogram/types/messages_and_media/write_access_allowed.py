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

from typing import Optional

from pyrogram import raw
from ..object import Object


class WriteAccessAllowed(Object):
    """This object represents a service message about a user allowing a bot to write messages after adding it to the attachment menu, launching a Web App from a link, or accepting an explicit request from a Web App sent by the method `requestWriteAccess <https://core.telegram.org/bots/webapps#initializing-mini-apps>`__.

    Parameters:
        from_request (``bool``, *optional*):
            True, if the access was granted after the user accepted an explicit request from a Web App sent by the method `requestWriteAccess <https://core.telegram.org/bots/webapps#initializing-mini-apps>`__

        web_app_name (``str``, *optional*):
            Name of the Web App, if the access was granted when the Web App was launched from a link

        from_attachment_menu (``bool``, *optional*):
            True, if the access was granted when the bot was added to the attachment or side menu

    """

    def __init__(
        self,
        *,
        from_request: Optional[bool] = None,
        web_app_name: Optional[str] = None,
        from_attachment_menu: Optional[bool] = None,
    ):
        super().__init__()

        self.from_request = from_request
        self.web_app_name = web_app_name
        self.from_attachment_menu = from_attachment_menu

    @staticmethod
    def _parse(action: "raw.types.MessageActionBotAllowed"):
        return WriteAccessAllowed(
            from_request=getattr(action, "from_request", None),
            web_app_name=getattr(getattr(action, "app", None), "short_name", None),
            from_attachment_menu=getattr(action, "attach_menu", None),
        )
