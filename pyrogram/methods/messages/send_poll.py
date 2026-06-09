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

import logging
from datetime import datetime
from typing import List, Optional, Union

import pyrogram
from pyrogram import enums, raw, types, utils

log = logging.getLogger(__name__)

class SendPoll:
    async def send_poll(
        self: "pyrogram.Client",
        chat_id: Union[int, str],
        question: Union[str, "types.FormattedText"],
        options: List[Union[str, "types.InputPollOption"]],
        description: Optional[Union[str, "types.FormattedText"]] = None,
        description_media: Optional["types.InputPollMedia"] = None,
        message_thread_id: Optional[int] = None,
        business_connection_id: Optional[str] = None,
        is_anonymous: bool = True,
        type: "enums.PollType" = enums.PollType.REGULAR,
        allows_multiple_answers: Optional[bool] = None,
        allows_revoting: Optional[bool] = None,
        members_only: Optional[bool] = None,
        country_codes: Optional[List[str]] = None,
        shuffle_options: Optional[bool] = None,
        allow_adding_options: Optional[bool] = None,
        hide_results_until_closes: Optional[bool] = None,
        correct_option_ids: Optional[List[int]] = None,
        explanation: Optional[Union[str, "types.FormattedText"]] = None,
        explanation_media: Optional["types.InputPollMedia"] = None,
        open_period: Optional[int] = None,
        close_date: Optional[datetime] = None,
        is_closed: Optional[bool] = None,
        disable_notification: Optional[bool] = None,
        protect_content: Optional[bool] = None,
        allow_paid_broadcast: Optional[bool] = None,
        effect_id: Optional[int] = None,
        reply_parameters: Optional["types.ReplyParameters"] = None,
        schedule_date: Optional[datetime] = None,
        repeat_period: Optional[int] = None,
        paid_message_star_count: Optional[int] = None,
        reply_markup: Optional[
            Union[
                "types.InlineKeyboardMarkup",
                "types.ReplyKeyboardMarkup",
                "types.ReplyKeyboardRemove",
                "types.ForceReply"
            ]
        ] = None,
    ) -> "types.Message":
        """A message with a poll.

        .. note::

            Polls can't be sent to secret chats and channel direct messages chats.
            Polls can be sent to a private chat only if the chat is a chat with a bot or the Saved Messages chat.

        .. include:: /_includes/usable-by/users-bots.rst

        Parameters:
            chat_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target chat.
                For your personal cloud (Saved Messages) you can simply use "me" or "self".
                For a contact that exists in your Telegram address book you can use his phone number (str).

            question (``str`` | :obj:`~pyrogram.types.FormattedText`):
                Poll question, 1-255 characters (up to 300 characters for bots).
                Only custom emoji entities are allowed to be added and only by Premium users.

            options (List of :obj:`~pyrogram.types.InputPollOption`):
                List of 1-12 answer options.

            description (``str`` | :obj:`~pyrogram.types.FormattedText`, *optional*):
                Description of the poll to be sent, 0-1024 characters after entities parsing.

            description_media (:obj:`~pyrogram.types.InputPollMedia`, *optional*):
                Media attached to the poll.

            message_thread_id (``int``, *optional*):
                Unique identifier for the target message thread (topic) of the forum.
                For supergroups only.

            business_connection_id (``str``, *optional*):
                Unique identifier of the business connection on behalf of which the message will be sent.

            is_anonymous (``bool``, *optional*):
                True, if the poll needs to be anonymous.
                Defaults to True.

            type (:obj`~pyrogram.enums.PollType`, *optional*):
                Poll type, :obj:`~pyrogram.enums.PollType.QUIZ` or :obj:`~pyrogram.enums.PollType.REGULAR`.
                Defaults to :obj:`~pyrogram.enums.PollType.REGULAR`.

            allows_multiple_answers (``bool``, *optional*):
                Pass True, if the poll allows multiple answers.
                Defaults to False.

            allows_revoting (``bool``, *optional*):
                Pass True, if the poll allows to change chosen answer options.
                Defaults to False for quizzes and to True for regular polls.

            members_only (``bool``, *optional*):
                Pass True, if voting is limited to users who have been members of the chat where the poll is being sent for more than 24 hours.
                For channel chats only.

            country_codes (List of ``str``, *optional*):
                The list of 0-12 two-letter ISO 3166-1 alpha-2 country codes indicating the countries from which users can vote in the poll.
                For channel chats only.
                If omitted or empty, then users from any country can participate in the poll.

            shuffle_options (``bool``, *optional*):
                Pass True, if the poll options must be shown in random order.

            allow_adding_options (``bool``, *optional*):
                Pass True, if answer options can be added to the poll after creation, not supported for anonymous polls and quizzes.

            hide_results_until_closes (``bool``, *optional*):
                Pass True, if poll results must be shown only after the poll closes.

            correct_option_ids (List of ``int``, *optional*):
                List of monotonically increasing 0-based identifiers of the correct answer options, required for polls in quiz mode.

            explanation (``str`` | :obj:`~pyrogram.types.FormattedText`, *optional*):
                Text that is shown when a user chooses an incorrect answer or taps on the lamp icon in a quiz-style poll, 0-200 characters with at most 2 line feeds after entities parsing.

            explanation_media (:obj:`~pyrogram.types.InputPollMedia`, *optional*):
                Media attached to the explanation.

            open_period (``int``, *optional*):
                Amount of time in seconds the poll will be active after creation, 5-2628000.
                Can't be used together with *close_date*.

            close_date (:py:obj:`~datetime.datetime`, *optional*):
                Point in time when the poll will be automatically closed.
                Must be at least 5 and no more than 2628000 seconds in the future.
                Can't be used together with *open_period*.

            is_closed (``bool``, *optional*):
                Pass True, if the poll needs to be immediately closed.
                This can be useful for poll preview.
                For bots only.

            disable_notification (``bool``, *optional*):
                Sends the message silently.
                Users will receive a notification with no sound.

            protect_content (``bool``, *optional*):
                Protects the contents of the sent message from forwarding and saving.

            allow_paid_broadcast (``bool``, *optional*):
                If True, you will be allowed to send up to 1000 messages per second.
                Ignoring broadcasting limits for a fee of 0.1 Telegram Stars per message.
                The relevant Stars will be withdrawn from the bot's balance.
                For bots only.

            effect_id (``int``, *optional*):
                Unique identifier of the message effect.
                For private chats only.

            reply_parameters (:obj:`~pyrogram.types.ReplyParameters`, *optional*):
                Describes reply parameters for the message that is being sent.

            schedule_date (:py:obj:`~datetime.datetime`, *optional*):
                Date when the message will be automatically sent.

            repeat_period (``int``, *optional*):
                Period after which the message will be sent again in seconds.

            paid_message_star_count (``int``, *optional*):
                The number of Telegram Stars the user agreed to pay to send the messages.

            reply_markup (:obj:`~pyrogram.types.InlineKeyboardMarkup` | :obj:`~pyrogram.types.ReplyKeyboardMarkup` | :obj:`~pyrogram.types.ReplyKeyboardRemove` | :obj:`~pyrogram.types.ForceReply`, *optional*):
                Additional interface options. An object for an inline keyboard, custom reply keyboard,
                instructions to remove reply keyboard or to force a reply from the user.

        Returns:
            :obj:`~pyrogram.types.Message`: On success, the sent poll message is returned.

        Example:
            .. code-block:: python

                # Regular poll
                await app.send_poll(
                    chat_id=chat_id,
                    question="Is this a poll question?",
                    options=[
                        types.InputPollOption(text="Yes"),
                        types.InputPollOption(text="No"),
                        types.InputPollOption(text="Maybe")
                    ]
                )

                # Poll with media
                await app.send_poll(
                    chat_id=chat_id,
                    question="Where we are?",
                    description_media=types.InputMediaPhoto("photo.jpg"),
                    options=[
                        types.InputPollOption(
                            text="Maybe here?",
                            media=types.InputMediaPhoto("photo1.jpg")
                        ),
                        types.InputPollOption(
                            text="Or here?",
                            media=types.Location(
                                latitude=49.807760,
                                longitude=73.088504
                            ),
                        ),
                    ]
                )
        """
        if isinstance(question, str):
            question = types.FormattedText(text=question)

        if isinstance(explanation, str):
            explanation = types.FormattedText(text=explanation)

        if isinstance(description, str):
            description = types.FormattedText(text=description)

        answers = []

        for option in options:
            if isinstance(option, str):
                answers.append(
                    types.InputPollOption(
                        text=types.FormattedText(text=option)
                    )
                )
            else:
                answers.append(option)

        solution = None
        solution_entities = None
        message = None
        entities = None

        if explanation is not None:
            raw_solution = await explanation.write(self)
            solution = raw_solution.text
            solution_entities = raw_solution.entities

        if description is not None:
            raw_message = await description.write(self)
            message = raw_message.text
            entities = raw_message.entities

        r = await self.invoke(
            raw.functions.messages.SendMedia(
                peer=await self.resolve_peer(chat_id),
                media=raw.types.InputMediaPoll(
                    poll=raw.types.Poll(
                        id=self.rnd_id(),
                        question=await question.write(self),
                        answers=[await answer.write(self) for answer in answers],
                        hash=0,
                        closed=is_closed,
                        public_voters=not is_anonymous,
                        multiple_choice=True if correct_option_ids and len(correct_option_ids) > 1 else allows_multiple_answers,
                        quiz=type == enums.PollType.QUIZ or False,
                        open_answers=False if type == enums.PollType.QUIZ and allow_adding_options else allow_adding_options,
                        revoting_disabled=not allows_revoting if allows_revoting is not None else (type == enums.PollType.QUIZ),
                        subscribers_only=members_only,
                        countries_iso2=country_codes,
                        shuffle_answers=shuffle_options,
                        hide_results_until_close=hide_results_until_closes,
                        close_period=open_period,
                        close_date=utils.datetime_to_timestamp(close_date)
                    ),
                    correct_answers=correct_option_ids,
                    attached_media=await description_media.write(client=self) if description_media is not None else None,
                    solution=solution,
                    solution_entities=solution_entities,
                    solution_media=await explanation_media.write(client=self) if explanation_media is not None else None
                ),
                message=message or "",
                entities=entities or None,
                silent=disable_notification,
                reply_to=await utils.get_reply_to(
                    self,
                    reply_parameters,
                    message_thread_id
                ),
                random_id=self.rnd_id(),
                schedule_date=utils.datetime_to_timestamp(schedule_date),
                schedule_repeat_period=repeat_period,
                noforwards=protect_content,
                allow_paid_floodskip=allow_paid_broadcast,
                allow_paid_stars=paid_message_star_count,
                reply_markup=await reply_markup.write(self) if reply_markup else None,
                effect=effect_id
            ),
            business_connection_id=business_connection_id
        )

        return next(iter(await utils.parse_messages(client=self, messages=r)), None)
