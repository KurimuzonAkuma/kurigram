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


import re
from importlib import import_module
from pathlib import Path
from types import ModuleType
from typing import Type

import pytest

from pyrogram.errors import (
    BadRequest,
    ChannelPrivate,
    ChannelPrivate406,
    ChatWriteForbidden,
    ChatWriteForbidden403,
    EmailUnconfirmed,
    EmailUnconfirmedX,
    Forbidden,
    InternalServerError,
    NotAcceptable,
    RPCError,
    ServiceUnavailable,
    Timeout,
    Timeout503,
    UnknownError,
    UnknownError400
)
from pyrogram.errors.exceptions.all import exceptions
from tests.unit.errors import raise_it


@pytest.mark.parametrize(
    ("code", "message", "error_type", "category"),
    [
        pytest.param(400, "CHAT_WRITE_FORBIDDEN", ChatWriteForbidden, BadRequest, id="400-write-forbidden"),
        pytest.param(403, "CHAT_WRITE_FORBIDDEN", ChatWriteForbidden403, Forbidden, id="403-write-forbidden"),
        pytest.param(400, "CHANNEL_PRIVATE", ChannelPrivate, BadRequest, id="400-channel-private"),
        pytest.param(406, "CHANNEL_PRIVATE", ChannelPrivate406, NotAcceptable, id="406-channel-private"),
        pytest.param(500, "TIMEOUT", Timeout, InternalServerError, id="500-timeout"),
        pytest.param(-503, "Timeout", Timeout503, ServiceUnavailable, id="503-timeout")
    ]
)
def test_an_error_under_two_codes_is_caught_by_the_category_of_the_one_it_came_from(
    code: int,
    message: str,
    error_type: Type[RPCError],
    category: Type[RPCError]
) -> None:
    with pytest.raises(error_type) as raised:
        raise_it(code, message=message)

    error = raised.value

    assert type(error) is error_type
    assert isinstance(error, category)
    assert error.CODE == abs(code)
    assert error.NAME == category.NAME
    assert error.ID == message


@pytest.mark.parametrize(
    ("code", "message", "shared_type"),
    [
        pytest.param(403, "CHAT_WRITE_FORBIDDEN", ChatWriteForbidden, id="write-forbidden"),
        pytest.param(406, "CHANNEL_PRIVATE", ChannelPrivate, id="channel-private"),
        pytest.param(-503, "Timeout", Timeout, id="timeout")
    ]
)
def test_the_name_the_two_codes_share_still_catches_both(
    code: int,
    message: str,
    shared_type: Type[RPCError]
) -> None:
    with pytest.raises(shared_type):
        raise_it(code, message=message)


def test_two_ids_under_one_code_keep_their_own_message() -> None:
    with pytest.raises(EmailUnconfirmedX) as raised:
        raise_it(400, message="EMAIL_UNCONFIRMED_6")

    error = raised.value

    # The parameterised id is the one that gets marked, and it subclasses the plain one, so
    # `except EmailUnconfirmed` catches both while each keeps its own message.
    assert isinstance(error, EmailUnconfirmed)
    assert error.ID == "EMAIL_UNCONFIRMED_X"
    assert error.value == 6
    assert EmailUnconfirmed.MESSAGE != EmailUnconfirmedX.MESSAGE


def test_an_error_named_after_a_hand_written_one_is_still_a_bad_request(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)

    with pytest.raises(UnknownError400) as raised:
        raise_it(400, message="UNKNOWN_ERROR")

    error = raised.value

    assert isinstance(error, BadRequest)
    assert error.CODE == 400
    assert not isinstance(error, UnknownError)
    assert not (tmp_path / "unknown_errors.txt").exists()


def test_every_error_in_the_table_reports_the_code_it_came_from() -> None:
    errors: ModuleType = import_module("pyrogram.errors")
    categories = {code: getattr(errors, table["_"]) for code, table in exceptions.items()}
    checked: int = 0

    for code, table in exceptions.items():
        for error_id, class_name in table.items():
            if error_id == "_":
                continue

            normalised = re.sub(r"_\d+", "_X", error_id)

            # `FILE_PART_0_MISSING` normalises to `FILE_PART_X_MISSING`, so nothing ever resolves
            # to it. It is a row of the table no answer can reach, not a class to check.
            if normalised != error_id and normalised in table:
                continue

            with pytest.raises(getattr(errors, class_name)) as raised:
                raise_it(code, message=error_id.replace("_X", "_7").replace("XMIN", "7MIN"))

            error = raised.value

            assert type(error).__name__ == class_name
            assert error.CODE == code
            assert error.ID == error_id
            assert isinstance(error, categories[code])

            checked += 1

    assert checked == 936
