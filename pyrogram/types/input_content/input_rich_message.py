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


class InputRichMessage(Object):
    """Describes a checklist to create.

    Parameters:
        html (``str``, *optional*):
            Content of the rich message to send described using HTML formatting.
            See `rich message formatting options <https://core.telegram.org/bots/api#rich-message-formatting-options>`__ for more details.

        markdown (``str``, *optional*):
            Content of the rich message to send described using Markdown formatting.
            See `rich message formatting options <https://core.telegram.org/bots/api#rich-message-formatting-options>`__ for more details.

        is_rtl (``bool``, *optional*):
            Pass *True* if the rich message must be shown right-to-left.

        skip_entity_detection (``bool``, *optional*):
            Pass *True* to skip automatic detection of entities
            (e.g., URLs, email addresses, username mentions, hashtags, cashtags, bot commands, or phone numbers) in the text.
    """

    def __init__(
        self,
        html: Optional[str] = None,
        markdown: Optional[str] = None,
        is_rtl: Optional[bool] = None,
        skip_entity_detection: Optional[bool] = None,
    ):
        super().__init__()

        self.html = html
        self.markdown = markdown
        self.is_rtl = is_rtl
        self.skip_entity_detection = skip_entity_detection

    def write(self) -> "raw.base.InputRichMessage":
        if self.html:
            input_rich_message = raw.types.InputRichMessageHTML(
                html=self.html,
                rtl=self.is_rtl,
                noautolink=self.skip_entity_detection
            )
        elif self.markdown:
            input_rich_message = raw.types.InputRichMessageMarkdown(
                markdown=self.markdown,
                rtl=self.is_rtl,
                noautolink=self.skip_entity_detection
            )
        else:
            raise ValueError("You must provide either markdown or html in the rich message")

        return input_rich_message
