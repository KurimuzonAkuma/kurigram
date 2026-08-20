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


from importlib import import_module
from types import ModuleType
from typing import Final, Set, Type

import pytest

from pyrogram.errors import (
    AllowPaymentRequired,
    AuthRestart,
    EmailUnconfirmed,
    FilePartMissing,
    FileReferenceExpired,
    FloodWait,
    PeerIdInvalid,
    PhoneMigrate,
    PremiumSubActiveUntil,
    PreviousChatImportActiveWaitMin,
    RPCError,
    StoryLiveAlready
)
from pyrogram.errors.exceptions.all import exceptions
from tests.errors import RPC_NAME, raise_it

# Every class whose message names its value, counted once. One fewer than the 32 the tables produce:
# `FILE_MIGRATE_X` is listed under both 303 and 400, both rows compile to a class called
# `FileMigrate`, and `pyrogram.errors` keeps whichever was imported last.
NAMED_ERRORS: Final[int] = 31


@pytest.mark.parametrize(
    ("code", "message", "error_type", "value_name", "value"),
    [
        pytest.param(420, "FLOOD_WAIT_42", FloodWait, "seconds", 42, id="seconds"),
        pytest.param(303, "PHONE_MIGRATE_2", PhoneMigrate, "dc_id", 2, id="dc-id"),
        pytest.param(400, "FILE_PART_3_MISSING", FilePartMissing, "file_part", 3, id="file-part"),
        pytest.param(
            400,
            "FILE_REFERENCE_1_EXPIRED",
            FileReferenceExpired,
            "index",
            1,
            id="index"
        ),
        pytest.param(
            406,
            "PREVIOUS_CHAT_IMPORT_ACTIVE_WAIT_5MIN",
            PreviousChatImportActiveWaitMin,
            "minutes",
            5,
            id="minutes"
        ),
        pytest.param(
            400,
            "EMAIL_UNCONFIRMED_6",
            EmailUnconfirmed,
            "code_length",
            6,
            id="code-length"
        ),
        pytest.param(
            403,
            "ALLOW_PAYMENT_REQUIRED_25",
            AllowPaymentRequired,
            "star_count",
            25,
            id="star-count"
        ),
        pytest.param(
            400,
            "STORY_LIVE_ALREADY_9",
            StoryLiveAlready,
            "story_id",
            9,
            id="story-id"
        ),
        pytest.param(
            420,
            "PREMIUM_SUB_ACTIVE_UNTIL_1755561600",
            PremiumSubActiveUntil,
            "until_date",
            1755561600,
            id="until-date"
        ),
        pytest.param(500, "AUTH_RESTART_7", AuthRestart, "debug_info", 7, id="debug-info")
    ]
)
def test_an_error_says_what_its_value_means(
    code: int,
    message: str,
    error_type: Type[RPCError],
    value_name: str,
    value: int
) -> None:
    with pytest.raises(error_type) as raised:
        raise_it(code, message=message)

    error = raised.value

    assert error.VALUE_NAME == value_name
    assert getattr(error, value_name) == value
    assert error.value == value


def test_the_message_is_still_filled_in_with_the_value() -> None:
    with pytest.raises(FloodWait) as raised:
        raise_it(420, message="FLOOD_WAIT_42")

    assert str(raised.value) == (
        "Telegram says: [420 FLOOD_WAIT_X] - Please wait 42 seconds before repeating the action."
        f' (caused by "{RPC_NAME}")'
    )


def test_an_error_that_carries_nothing_names_nothing() -> None:
    with pytest.raises(PeerIdInvalid) as raised:
        raise_it(400, message="PEER_ID_INVALID")

    error = raised.value

    assert error.VALUE_NAME == "value"
    assert error.value is None


def test_a_named_value_cannot_be_written_to() -> None:
    error = FloodWait(42)

    with pytest.raises(AttributeError):
        error.seconds = 43


def test_the_base_class_still_speaks_of_a_plain_value() -> None:
    assert RPCError.VALUE_NAME == "value"
    assert RPCError.MESSAGE == "{value}"
    assert str(RPCError("something")) == "Telegram says: [None None] - something"


def test_no_message_asks_for_more_than_one_value() -> None:
    errors: ModuleType = import_module("pyrogram.errors")

    for table in exceptions.values():
        for class_name in table.values():
            error_type = getattr(errors, class_name)

            # `raise_it()` reads one number out of a message and renders the message with it, so a
            # second placeholder could never be filled in: `str.format()` would raise `KeyError`
            # while building the error, and the caller would catch that instead of the error.
            assert error_type.MESSAGE.count("{") <= 1
            assert error_type.MESSAGE.count("{") == error_type.MESSAGE.count("}")


def test_every_named_value_is_the_value_under_another_name() -> None:
    errors: ModuleType = import_module("pyrogram.errors")
    named: Set[Type[RPCError]] = set()

    for table in exceptions.values():
        for class_name in table.values():
            error_type = getattr(errors, class_name)

            if error_type.VALUE_NAME == "value":
                # `value` is the attribute itself, so nothing may sit on the class under that name.
                assert "value" not in vars(error_type)
                continue

            assert isinstance(vars(error_type)[error_type.VALUE_NAME], property)
            assert getattr(error_type(42), error_type.VALUE_NAME) == 42

            named.add(error_type)

    assert len(named) == NAMED_ERRORS
