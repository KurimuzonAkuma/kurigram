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

import html
import re
import urllib.parse
from typing import List, Optional, Tuple, Union

import pyrogram
from pyrogram import types
from pyrogram.enums import MessageEntityType

from . import utils
from .html import HTML

BOLD_DELIM = "**"
ITALIC_DELIM = "__"
UNDERLINE_DELIM = "--"
STRIKE_DELIM = "~~"
SPOILER_DELIM = "||"
CODE_DELIM = "`"
PRE_DELIM = "```"
BLOCKQUOTE_DELIM = ">"
BLOCKQUOTE_EXPANDABLE_DELIM = "**>"
BLOCKQUOTE_EXPANDABLE_END_DELIM = "||"

MARKDOWN_RE = re.compile(r"({d})|(!?)\[(.+?)\]\((.+?)\)".format(
    d="|".join(
        ["".join(i) for i in [
            [rf"\{j}" for j in i]
            for i in [
                PRE_DELIM,
                CODE_DELIM,
                STRIKE_DELIM,
                UNDERLINE_DELIM,
                ITALIC_DELIM,
                BOLD_DELIM,
                SPOILER_DELIM
            ]
        ]]
    )))

OPENING_TAG = "<{}>"
CLOSING_TAG = "</{}>"
URL_MARKUP = '<a href="{}">{}</a>'
EMOJI_MARKUP = '<tg-emoji emoji-id="{}">{}</tg-emoji>'
DATE_TIME_MARKUP = '<tg-time unix="{}">{}</tg-time>'
FORMATTED_DATE_TIME_MARKUP = '<tg-time unix="{}" format="{}">{}</tg-time>'
FIXED_WIDTH_DELIMS = [CODE_DELIM, PRE_DELIM]


class Markdown:
    # TODO: Full refactor
    def __init__(self, client: Optional["pyrogram.Client"]):
        self.html = HTML(client)

    @staticmethod
    def escape_and_create_quotes(text: str, strict: bool):
        text_lines: List[Union[str, None]] = text.splitlines()

        # Indexes of Already escaped lines
        html_escaped_list: List[int] = []

        # Temporary Queue to hold lines to be quoted
        to_quote_list: List[Tuple[int, str]] = []

        def create_blockquote(expandable: bool = False) -> None:
            """
            Merges all lines in quote_queue into first line of queue
            Encloses that line in html quote
            Replaces rest of the lines with None placeholders to preserve indexes
            """
            if len(to_quote_list) == 0:
                return

            joined_lines = "\n".join([i[1] for i in to_quote_list])

            first_line_index, _ = to_quote_list[0]
            text_lines[first_line_index] = (
                f"<blockquote{' expandable' if expandable else ''}>{joined_lines}</blockquote>"
            )

            for line_to_remove in to_quote_list[1:]:
                text_lines[line_to_remove[0]] = None

            to_quote_list.clear()

        # Handle Expandable Quote
        inside_blockquote = False
        for index, line in enumerate(text_lines):
            if line.startswith(BLOCKQUOTE_EXPANDABLE_DELIM) and not inside_blockquote:
                delim_stripped_line = line[len(BLOCKQUOTE_EXPANDABLE_DELIM) + (1 if line.startswith(f"{BLOCKQUOTE_EXPANDABLE_DELIM} ") else 0) :]
                parsed_line = (
                    html.escape(delim_stripped_line) if strict else delim_stripped_line
                )

                to_quote_list.append((index, parsed_line))
                html_escaped_list.append(index)

                inside_blockquote = True
                continue

            elif line.endswith(BLOCKQUOTE_EXPANDABLE_END_DELIM) and inside_blockquote:
                if line.startswith(BLOCKQUOTE_DELIM):
                    line = line[len(BLOCKQUOTE_DELIM) + (1 if line.startswith(f"{BLOCKQUOTE_DELIM} ") else 0) :]

                delim_stripped_line = line[:-len(BLOCKQUOTE_EXPANDABLE_END_DELIM)]

                parsed_line = (
                    html.escape(delim_stripped_line) if strict else delim_stripped_line
                )

                to_quote_list.append((index, parsed_line))
                html_escaped_list.append(index)

                inside_blockquote = False

                create_blockquote(expandable=True)

            if inside_blockquote:
                parsed_line = line[len(BLOCKQUOTE_DELIM) + (1 if line.startswith(f"{BLOCKQUOTE_DELIM} ") else 0) :]
                parsed_line = html.escape(parsed_line) if strict else parsed_line
                to_quote_list.append((index, parsed_line))
                html_escaped_list.append(index)

        # Handle Single line/Continued Quote
        for index, line in enumerate(text_lines):
            if line is None:
                continue

            if line.startswith(BLOCKQUOTE_DELIM):
                delim_stripped_line = line[len(BLOCKQUOTE_DELIM) + (1 if line.startswith(f"{BLOCKQUOTE_DELIM} ") else 0) :]
                parsed_line = (
                    html.escape(delim_stripped_line) if strict else delim_stripped_line
                )

                to_quote_list.append((index, parsed_line))
                html_escaped_list.append(index)

            elif len(to_quote_list) > 0:
                create_blockquote()
        else:
            create_blockquote()

        if strict:
            for idx, line in enumerate(text_lines):
                if idx not in html_escaped_list:
                    text_lines[idx] = html.escape(line)

        return "\n".join(
            [valid_line for valid_line in text_lines if valid_line is not None]
        )

    async def parse(self, text: str, strict: bool = False):
        text = self.escape_and_create_quotes(text, strict=strict)
        delims = set()
        is_fixed_width = False

        for match in re.finditer(MARKDOWN_RE, text):
            start, _ = match.span()
            delim, is_emoji_like, text_url, url = match.groups()
            full = match.group(0)

            if delim in FIXED_WIDTH_DELIMS:
                is_fixed_width = not is_fixed_width

            if is_fixed_width and delim not in FIXED_WIDTH_DELIMS:
                continue

            if not is_emoji_like and text_url:
                text = utils.replace_once(text, full, URL_MARKUP.format(url, text_url), start)
                continue

            if is_emoji_like:
                parsed = urllib.parse.urlparse(url)
                params = urllib.parse.parse_qs(parsed.query)
                emoji_date = text_url

                if parsed.netloc == "time":
                    unix_time = params.get("unix", [""])[0]
                    date_time_format = params.get("format", [""])[0]

                    if date_time_format:
                        markup = FORMATTED_DATE_TIME_MARKUP.format(unix_time, date_time_format, emoji_date)
                    else:
                        markup = DATE_TIME_MARKUP.format(unix_time, emoji_date)
                    text = utils.replace_once(text, full, markup, start)
                elif parsed.netloc == "emoji":
                    emoji_id = params.get("id", [""])[0]
                    markup = EMOJI_MARKUP.format(emoji_id, emoji_date)
                    text = utils.replace_once(text, full, markup, start)

                continue

            if delim == BOLD_DELIM:
                tag = "b"
            elif delim == ITALIC_DELIM:
                tag = "i"
            elif delim == UNDERLINE_DELIM:
                tag = "u"
            elif delim == STRIKE_DELIM:
                tag = "s"
            elif delim == CODE_DELIM:
                tag = "code"
            elif delim == PRE_DELIM:
                tag = "pre"
            elif delim == SPOILER_DELIM:
                tag = "spoiler"
            else:
                continue

            if delim not in delims:
                delims.add(delim)
                tag = OPENING_TAG.format(tag)
            else:
                delims.remove(delim)
                tag = CLOSING_TAG.format(tag)

            if delim == PRE_DELIM and delim in delims:
                delim_and_language = text[text.find(PRE_DELIM):].split("\n")[0]
                language = delim_and_language[len(PRE_DELIM):]
                text = utils.replace_once(text, delim_and_language, f'<pre language="{language}">', start)
                continue

            text = utils.replace_once(text, delim, tag, start)

        return await self.html.parse(text)

    @staticmethod
    def unparse(text: str, entities: List["types.MessageEntity"]):
        text = utils.add_surrogates(text)

        entities_offsets = []

        for entity in entities:
            entity_type = entity.type
            start = entity.offset
            end = start + entity.length

            if entity_type == MessageEntityType.BOLD:
                start_tag = end_tag = BOLD_DELIM
            elif entity_type == MessageEntityType.ITALIC:
                start_tag = end_tag = ITALIC_DELIM
            elif entity_type == MessageEntityType.UNDERLINE:
                start_tag = end_tag = UNDERLINE_DELIM
            elif entity_type == MessageEntityType.STRIKETHROUGH:
                start_tag = end_tag = STRIKE_DELIM
            elif entity_type == MessageEntityType.CODE:
                start_tag = end_tag = CODE_DELIM
            elif entity_type == MessageEntityType.PRE:
                language = getattr(entity, "language", "") or ""
                start_tag = f"{PRE_DELIM}{language}\n"
                end_tag = f"\n{PRE_DELIM}"
            elif entity_type == MessageEntityType.BLOCKQUOTE:
                start_tag = BLOCKQUOTE_DELIM + " "
                end_tag = ""
                blockquote_text = text[start:end]
                lines = blockquote_text.split("\n")
                last_length = 0
                for line in lines:
                    if len(line) == 0 and last_length == end:
                        continue
                    start_offset = start+last_length
                    last_length = last_length+len(line)
                    end_offset = start_offset+last_length
                    entities_offsets.append((start_tag, start_offset,))
                    entities_offsets.append((end_tag, end_offset,))
                    last_length = last_length+1
                continue
            elif entity_type == MessageEntityType.SPOILER:
                start_tag = end_tag = SPOILER_DELIM
            elif entity_type == MessageEntityType.TEXT_LINK:
                url = entity.url
                start_tag = "["
                end_tag = f"]({url})"
            elif entity_type == MessageEntityType.TEXT_MENTION:
                user = entity.user
                start_tag = "["
                end_tag = f"](tg://user?id={user.id})"
            elif entity_type == MessageEntityType.CUSTOM_EMOJI:
                emoji_id = entity.custom_emoji_id
                start_tag = "!["
                end_tag = f"](tg://emoji?id={emoji_id})"
            elif entity_type == MessageEntityType.DATE_TIME:
                unix_time = entity.unix_time
                date_time_format = entity.date_time_format
                start_tag = "!["
                if date_time_format:
                    end_tag = f"](tg://time?unix={unix_time}&format={date_time_format})"
                else:
                    end_tag = f"](tg://time?unix={unix_time})"
            else:
                continue

            entities_offsets.append((start_tag, start,))
            entities_offsets.append((end_tag, end,))

        entities_offsets = map(
            lambda x: x[1],
            sorted(
                enumerate(entities_offsets),
                key=lambda x: (x[1][1], x[0]),
                reverse=True
            )
        )

        for entity, offset in entities_offsets:
            text = text[:offset] + entity + text[offset:]

        return utils.remove_surrogates(text)
