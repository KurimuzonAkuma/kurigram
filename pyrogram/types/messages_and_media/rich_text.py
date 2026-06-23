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
from typing import Dict, List, Optional, Union

import pyrogram
from pyrogram import raw, types, utils

from ..object import Object


class RichText(Object):
    """This object represents a rich formatted text.

    It can be one of:

    - ``str``
    - List of :obj:`~pyrogram.types.RichText`
    - :obj:`~pyrogram.types.RichTextBold`
    - :obj:`~pyrogram.types.RichTextItalic`
    - :obj:`~pyrogram.types.RichTextUnderline`
    - :obj:`~pyrogram.types.RichTextStrikethrough`
    - :obj:`~pyrogram.types.RichTextSpoiler`
    - :obj:`~pyrogram.types.RichTextDateTime`
    - :obj:`~pyrogram.types.RichTextTextMention`
    - :obj:`~pyrogram.types.RichTextSubscript`
    - :obj:`~pyrogram.types.RichTextSuperscript`
    - :obj:`~pyrogram.types.RichTextMarked`
    - :obj:`~pyrogram.types.RichTextCode`
    - :obj:`~pyrogram.types.RichTextCustomEmoji`
    - :obj:`~pyrogram.types.RichTextMathematicalExpression`
    - :obj:`~pyrogram.types.RichTextUrl`
    - :obj:`~pyrogram.types.RichTextEmailAddress`
    - :obj:`~pyrogram.types.RichTextPhoneNumber`
    - :obj:`~pyrogram.types.RichTextBankCardNumber`
    - :obj:`~pyrogram.types.RichTextMention`
    - :obj:`~pyrogram.types.RichTextHashtag`
    - :obj:`~pyrogram.types.RichTextCashtag`
    - :obj:`~pyrogram.types.RichTextBotCommand`
    - :obj:`~pyrogram.types.RichTextAnchor`
    - :obj:`~pyrogram.types.RichTextAnchorLink`
    - :obj:`~pyrogram.types.RichTextReference`
    - :obj:`~pyrogram.types.RichTextReferenceLink`
    """

    def __init__(self):
        super().__init__()

    @staticmethod
    async def _parse(
        client: "pyrogram.Client",
        rich_text: "raw.base.RichText",
        users: Dict[int, "raw.base.User"] = {},
        chats: Dict[int, "raw.base.Chat"] = {},
    ) -> Optional[Union[str, List["RichText"], "RichText"]]:
        # TODO: fix anchors and references
        if isinstance(rich_text, raw.types.TextPlain):
            return rich_text.text

        if isinstance(rich_text, raw.types.TextConcat):
            return types.List([await RichText._parse(client, text) for text in rich_text.texts])

        if isinstance(rich_text, raw.types.TextBold):
            return RichTextBold(text=await RichText._parse(client, rich_text.text))

        if isinstance(rich_text, raw.types.TextItalic):
            return RichTextItalic(text=await RichText._parse(client, rich_text.text))

        if isinstance(rich_text, raw.types.TextUnderline):
            return RichTextUnderline(text=await RichText._parse(client, rich_text.text))

        if isinstance(rich_text, raw.types.TextStrike):
            return RichTextStrikethrough(text=await RichText._parse(client, rich_text.text))

        if isinstance(rich_text, raw.types.TextSpoiler):
            return RichTextSpoiler(text=await RichText._parse(client, rich_text.text))

        if isinstance(rich_text, raw.types.TextDate):
            if rich_text.relative:
                date_time_format = "r"
            else:
                date_time_format = ""

                if rich_text.day_of_week:
                    date_time_format += "w"

                if rich_text.short_date:
                    date_time_format += "d"
                elif rich_text.long_date:
                    date_time_format += "D"

                if rich_text.short_time:
                    date_time_format += "t"
                elif rich_text.long_time:
                    date_time_format += "T"

            return RichTextDateTime(
                text=await RichText._parse(client, rich_text.text),
                date=utils.timestamp_to_datetime(rich_text.date),
                date_time_format=date_time_format or None,
            )

        if isinstance(rich_text, raw.types.TextMentionName):
            return RichTextTextMention(
                text=await RichText._parse(client, rich_text.text),
                user=types.User._parse(client, users.get(rich_text.user_id)),
            )

        if isinstance(rich_text, raw.types.TextSubscript):
            return RichTextSubscript(text=await RichText._parse(client, rich_text.text))

        if isinstance(rich_text, raw.types.TextSuperscript):
            return RichTextSuperscript(text=await RichText._parse(client, rich_text.text))

        if isinstance(rich_text, raw.types.TextMarked):
            return RichTextMarked(text=await RichText._parse(client, rich_text.text))

        if isinstance(rich_text, raw.types.TextFixed):
            return RichTextCode(text=await RichText._parse(client, rich_text.text))

        if isinstance(rich_text, raw.types.TextCustomEmoji):
            return RichTextCustomEmoji(
                custom_emoji_id=str(rich_text.document_id), alternative_text=rich_text.alt
            )

        if isinstance(rich_text, raw.types.TextMath):
            return RichTextMathematicalExpression(expression=rich_text.source)

        if isinstance(rich_text, raw.types.TextUrl):
            content = await RichText._parse(client, rich_text.text)

            if rich_text.url.startswith("#"):
                anchor = rich_text.url[1:]

                return RichTextReferenceLink(
                    text=content,
                    reference_name=anchor,
                )

                # TODO: RichTextAnchorLink

            return RichTextUrl(text=content, url=rich_text.url)

        if isinstance(rich_text, raw.types.TextAutoUrl):
            return RichTextUrl(
                text=await RichText._parse(client, rich_text.text),
                url=await RichText._parse(client, rich_text.text),
            )

        if isinstance(rich_text, raw.types.TextEmail):
            return RichTextEmailAddress(
                text=await RichText._parse(client, rich_text.text), email_address=rich_text.email
            )

        if isinstance(rich_text, raw.types.TextAutoEmail):
            return RichTextEmailAddress(
                text=await RichText._parse(client, rich_text.text),
                email_address=await RichText._parse(client, rich_text.text),
            )

        if isinstance(rich_text, raw.types.TextPhone):
            return RichTextPhoneNumber(
                text=await RichText._parse(client, rich_text.text), phone_number=rich_text.phone
            )

        if isinstance(rich_text, raw.types.TextAutoPhone):
            return RichTextPhoneNumber(
                text=await RichText._parse(client, rich_text.text),
                phone_number=await RichText._parse(client, rich_text.text),
            )

        if isinstance(rich_text, raw.types.TextBankCard):
            return RichTextBankCardNumber(
                text=await RichText._parse(client, rich_text.text),
                bank_card_number=await RichText._parse(client, rich_text.text),
            )

        if isinstance(rich_text, raw.types.TextMention):
            content = await RichText._parse(client, rich_text.text)

            return RichTextMention(
                text=content,
                username=content.lstrip("@"),
            )

        if isinstance(rich_text, raw.types.TextHashtag):
            content = await RichText._parse(client, rich_text.text)

            return RichTextHashtag(
                text=content,
                hashtag=content.lstrip("#"),
            )

        if isinstance(rich_text, raw.types.TextCashtag):
            content = await RichText._parse(client, rich_text.text)

            return RichTextCashtag(
                text=content,
                cashtag=content.lstrip("$"),
            )

        if isinstance(rich_text, raw.types.TextBotCommand):
            content = await RichText._parse(client, rich_text.text)

            return RichTextBotCommand(
                text=content,
                bot_command=content.lstrip("/"),
            )

        if isinstance(rich_text, raw.types.TextAnchor):
            if isinstance(rich_text.text, raw.types.TextEmpty):
                return RichTextAnchor(
                    text=await RichText._parse(client, rich_text.text), name=rich_text.name
                )

            return RichTextReference(
                text=await RichText._parse(client, rich_text.text), name=rich_text.name
            )

        # TODO: if isinstance(rich_text, raw.types.TextImage):


class RichTextBold(RichText):
    """A bold text.

    Parameters:
        text (:obj:`~pyrogram.types.RichText`):
            The text.
    """

    def __init__(
        self,
        text: "types.RichText",
    ):
        super().__init__()

        self.text = text


class RichTextItalic(RichText):
    """A italicized text.

    Parameters:
        text (:obj:`~pyrogram.types.RichText`):
            The text.
    """

    def __init__(
        self,
        text: "types.RichText",
    ):
        super().__init__()

        self.text = text


class RichTextUnderline(RichText):
    """A underlined text.

    Parameters:
        text (:obj:`~pyrogram.types.RichText`):
            The text.
    """

    def __init__(
        self,
        text: "types.RichText",
    ):
        super().__init__()

        self.text = text


class RichTextStrikethrough(RichText):
    """A strikethrough text.

    Parameters:
        text (:obj:`~pyrogram.types.RichText`):
            The text.
    """

    def __init__(
        self,
        text: "types.RichText",
    ):
        super().__init__()

        self.text = text


class RichTextSpoiler(RichText):
    """A text covered by a spoiler.

    Parameters:
        text (:obj:`~pyrogram.types.RichText`):
            The text.
    """

    def __init__(
        self,
        text: "types.RichText",
    ):
        super().__init__()

        self.text = text


class RichTextDateTime(RichText):
    """Formatted date and time.

    Parameters:
        text (:obj:`~pyrogram.types.RichText`):
            The text.

        date (:py:obj:`datetime.datetime`):
            The date associated with the entity.

        date_time_format (``str``, *optional*):
            The string that defines the formatting of the date and time.
            See `date-time entity formatting <https://core.telegram.org/bots/api#date-time-entity-formatting>`__ for more details.
    """

    def __init__(
        self,
        text: "types.RichText",
        date: datetime,
        date_time_format: Optional[str] = None,
    ):
        super().__init__()

        self.text = text
        self.date = date
        self.date_time_format = date_time_format


class RichTextTextMention(RichText):
    """A mention of a Telegram user by their identifier.

    Parameters:
        text (:obj:`~pyrogram.types.RichText`):
            The text.

        user (:obj:`~pyrogram.types.User`):
            The mentioned user.
    """

    def __init__(
        self,
        text: "types.RichText",
        user: "types.User",
    ):
        super().__init__()

        self.text = text
        self.user = user


class RichTextSubscript(RichText):
    """A subscript text.

    Parameters:
        text (:obj:`~pyrogram.types.RichText`):
            The text.
    """

    def __init__(
        self,
        text: "types.RichText",
    ):
        super().__init__()

        self.text = text


class RichTextSuperscript(RichText):
    """A superscript text.

    Parameters:
        text (:obj:`~pyrogram.types.RichText`):
            The text.
    """

    def __init__(
        self,
        text: "types.RichText",
    ):
        super().__init__()

        self.text = text


class RichTextMarked(RichText):
    """A marked text.

    Parameters:
        text (:obj:`~pyrogram.types.RichText`):
            The text.
    """

    def __init__(
        self,
        text: "types.RichText",
    ):
        super().__init__()

        self.text = text


class RichTextCode(RichText):
    """A monowidth text.

    Parameters:
        text (:obj:`~pyrogram.types.RichText`):
            The text.
    """

    def __init__(
        self,
        text: "types.RichText",
    ):
        super().__init__()

        self.text = text


class RichTextCustomEmoji(RichText):
    """A custom emoji.

    Parameters:
        custom_emoji_id (``str``):
            Unique identifier of the custom emoji.
            Use :meth:`pyrogram.Client.get_custom_emoji_stickers` to get full information about the sticker.

        alternative_text (``str``):
            Alternative emoji for the custom emoji.
    """

    def __init__(self, custom_emoji_id: str, alternative_text: str):
        super().__init__()

        self.custom_emoji_id = custom_emoji_id
        self.alternative_text = alternative_text


class RichTextMathematicalExpression(RichText):
    """A mathematical expression.

    Parameters:
        expression (``str``):
            The expression in LaTeX format.
    """

    def __init__(
        self,
        expression: str,
    ):
        super().__init__()

        self.expression = expression


class RichTextUrl(RichText):
    """A text with a link.

    Parameters:
        text (:obj:`~pyrogram.types.RichText`):
            The text.

        url (``str``):
            URL of the link.
    """

    def __init__(self, text: "types.RichText", url: str):
        super().__init__()

        self.text = text
        self.url = url


class RichTextEmailAddress(RichText):
    """A text with an email address.

    Parameters:
        text (:obj:`~pyrogram.types.RichText`):
            The text.

        email_address (``str``):
            The email address.
    """

    def __init__(self, text: "types.RichText", email_address: str):
        super().__init__()

        self.text = text
        self.email_address = email_address


class RichTextPhoneNumber(RichText):
    """A text with a phone number.

    Parameters:
        text (:obj:`~pyrogram.types.RichText`):
            The text.

        phone_number (``str``):
            The phone number.
    """

    def __init__(self, text: "types.RichText", phone_number: str):
        super().__init__()

        self.text = text
        self.phone_number = phone_number


class RichTextBankCardNumber(RichText):
    """A text with a bank card number.

    Parameters:
        text (:obj:`~pyrogram.types.RichText`):
            The text.

        bank_card_number (``str``):
            The bank card number.
    """

    def __init__(self, text: "types.RichText", bank_card_number: str):
        super().__init__()

        self.text = text
        self.bank_card_number = bank_card_number


class RichTextMention(RichText):
    """A mention by a username.

    Parameters:
        text (:obj:`~pyrogram.types.RichText`):
            The text.

        username (``str``):
            The username.
    """

    def __init__(self, text: "types.RichText", username: str):
        super().__init__()

        self.text = text
        self.username = username


class RichTextHashtag(RichText):
    """A hashtag.

    Parameters:
        text (:obj:`~pyrogram.types.RichText`):
            The text.

        hashtag (``str``):
            The hashtag.
    """

    def __init__(self, text: "types.RichText", hashtag: str):
        super().__init__()

        self.text = text
        self.hashtag = hashtag


class RichTextCashtag(RichText):
    """A cashtag.

    Parameters:
        text (:obj:`~pyrogram.types.RichText`):
            The text.

        cashtag (``str``):
            The cashtag.
    """

    def __init__(self, text: "types.RichText", cashtag: str):
        super().__init__()

        self.text = text
        self.cashtag = cashtag


class RichTextBotCommand(RichText):
    """A bot command.

    Parameters:
        text (:obj:`~pyrogram.types.RichText`):
            The text.

        bot_command (``str``):
            The bot command.
    """

    def __init__(self, text: "types.RichText", bot_command: str):
        super().__init__()

        self.text = text
        self.bot_command = bot_command


class RichTextAnchor(RichText):
    """An anchor.

    Parameters:
        text (:obj:`~pyrogram.types.RichText`):
            The text.

        name (``str``):
            The name of the anchor.
    """

    def __init__(self, text: "types.RichText", name: str):
        super().__init__()

        self.text = text
        self.name = name


class RichTextAnchorLink(RichText):
    """A link to an anchor.

    Parameters:
        text (:obj:`~pyrogram.types.RichText`):
            The text.

        anchor_name (``str``):
            The name of the anchor.
            If the name is empty, then the link brings back to the top of the message.
    """

    def __init__(self, text: "types.RichText", anchor_name: str):
        super().__init__()

        self.text = text
        self.anchor_name = anchor_name


class RichTextReference(RichText):
    """A reference.

    Parameters:
        text (:obj:`~pyrogram.types.RichText`):
            The text.

        name (``str``):
            The name of the reference.
    """

    def __init__(self, text: "types.RichText", name: str):
        super().__init__()

        self.text = text
        self.name = name


class RichTextReferenceLink(RichText):
    """A link to a reference.

    Parameters:
        text (:obj:`~pyrogram.types.RichText`):
            The text.

        reference_name (``str``):
            The name of the reference.
    """

    def __init__(self, text: "types.RichText", reference_name: str):
        super().__init__()

        self.text = text
        self.reference_name = reference_name
