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

import pytest

from pyrogram import raw
from pyrogram.errors import (
    FilePartMissing,
    FloodWait,
    PeerIdInvalid,
    PhoneMigrate,
    PremiumSubActiveUntil,
    PreviousChatImportActiveWaitMin,
    RPCError
)
from pyrogram.errors.exceptions.all import exceptions


def raise_it(code, *, message):
    RPCError.raise_it(
        raw.types.RpcError(error_code=code, error_message=message),
        raw.functions.messages.GetHistory
    )


@pytest.mark.parametrize(
    ("code", "message", "error_type", "value_name", "value"),
    [
        pytest.param(420, "FLOOD_WAIT_42", FloodWait, "seconds", 42, id="seconds"),
        pytest.param(303, "PHONE_MIGRATE_2", PhoneMigrate, "dc_id", 2, id="dc-id"),
        pytest.param(400, "FILE_PART_3_MISSING", FilePartMissing, "part_number", 3, id="part-number"),
        pytest.param(
            406,
            "PREVIOUS_CHAT_IMPORT_ACTIVE_WAIT_5MIN",
            PreviousChatImportActiveWaitMin,
            "minutes",
            5,
            id="minutes"
        ),
        pytest.param(
            420,
            "PREMIUM_SUB_ACTIVE_UNTIL_1755561600",
            PremiumSubActiveUntil,
            "until_date",
            1755561600,
            id="until-date"
        )
    ]
)
def test_an_error_says_what_its_value_means(code, message, error_type, value_name, value):
    with pytest.raises(error_type) as raised:
        raise_it(code, message=message)

    error = raised.value

    assert error.VALUE_NAME == value_name
    assert getattr(error, value_name) == value
    assert error.value == value


def test_the_message_is_still_filled_in_with_the_value():
    with pytest.raises(FloodWait) as raised:
        raise_it(420, message="FLOOD_WAIT_42")

    assert "Please wait 42 seconds before repeating the action." in str(raised.value)


def test_an_error_that_carries_nothing_names_nothing():
    with pytest.raises(PeerIdInvalid) as raised:
        raise_it(400, message="PEER_ID_INVALID")

    error = raised.value

    assert error.VALUE_NAME == "value"
    assert error.value is None


def test_the_base_class_still_speaks_of_a_plain_value():
    assert RPCError.VALUE_NAME == "value"
    assert RPCError.MESSAGE == "{value}"
    assert str(RPCError("something")).startswith("Telegram says: [None None] - something")


def test_every_named_value_is_the_value_under_another_name():
    errors = import_module("pyrogram.errors")
    checked = 0

    for table in exceptions.values():
        for class_name in table.values():
            error_type = getattr(errors, class_name)

            # `value` is the attribute itself: a property of that name would shadow it.
            assert error_type.VALUE_NAME != "value" or "value" not in vars(error_type)

            if error_type.VALUE_NAME == "value":
                continue

            assert isinstance(vars(error_type)[error_type.VALUE_NAME], property)
            assert getattr(error_type(42), error_type.VALUE_NAME) == 42

            checked += 1

    assert checked
