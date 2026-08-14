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

import pytest

from pyrogram import raw
from pyrogram.errors import (
    BadRequest,
    FloodWait,
    PeerIdInvalid,
    PhoneMigrate,
    RPCError,
    UnknownError
)

RPC_NAME = "messages.GetHistory"


def raise_it(code, *, message):
    RPCError.raise_it(
        raw.types.RpcError(error_code=code, error_message=message),
        raw.functions.messages.GetHistory
    )


@pytest.mark.parametrize(
    ("code", "message", "error_type", "value"),
    [
        pytest.param(420, "FLOOD_WAIT_42", FloodWait, 42, id="a-number-in-the-message"),
        pytest.param(303, "PHONE_MIGRATE_2", PhoneMigrate, 2, id="another-number"),
        pytest.param(400, "PEER_ID_INVALID", PeerIdInvalid, None, id="no-number-at-all")
    ]
)
def test_a_known_error_takes_its_number_from_the_message(code, message, error_type, value):
    with pytest.raises(error_type) as raised:
        raise_it(code, message=message)

    error = raised.value

    assert error.value == value
    assert type(error.value) is type(value)


def test_a_negative_code_keeps_its_sign_in_the_text_only():
    with pytest.raises(FloodWait) as raised:
        raise_it(-420, message="FLOOD_WAIT_42")

    error = raised.value

    assert error.CODE == 420
    assert error.value == 42
    assert str(error).startswith("Telegram says: [-420 FLOOD_WAIT_X]")


def test_the_message_template_is_filled_in_with_the_value():
    with pytest.raises(FloodWait) as raised:
        raise_it(420, message="FLOOD_WAIT_42")

    text = str(raised.value)

    assert "Please wait 42 seconds before repeating the action." in text
    assert f'(caused by "{RPC_NAME}")' in text


def test_an_unknown_message_falls_back_to_the_class_of_its_code(tmp_path, monkeypatch):
    # NOTE: An unknown error appends to `unknown_errors.txt` in the working directory
    #       (`rpc_error.py:60-62`), which is why every unknown case runs somewhere disposable.
    monkeypatch.chdir(tmp_path)

    with pytest.raises(BadRequest) as raised:
        raise_it(400, message="SOMETHING_THE_SCHEMA_DOES_NOT_KNOW")

    error = raised.value

    assert error.value == "[400 SOMETHING_THE_SCHEMA_DOES_NOT_KNOW]"
    assert type(error.value) is str


def test_an_unknown_code_becomes_an_unknown_error(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    with pytest.raises(UnknownError) as raised:
        raise_it(999, message="A_CODE_THAT_IS_NOT_IN_THE_SCHEMA")

    error = raised.value

    assert error.CODE == 520
    assert error.value == "[999 A_CODE_THAT_IS_NOT_IN_THE_SCHEMA]"

    # `UnknownError` sets no `ID`, so the text has to fall back to `NAME`.
    assert error.ID is None
    assert str(error).startswith("Telegram says: [520 Unknown error]")


def test_an_unknown_error_is_recorded_in_a_file(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    with pytest.raises(UnknownError):
        raise_it(999, message="A_CODE_THAT_IS_NOT_IN_THE_SCHEMA")

    written = (tmp_path / "unknown_errors.txt").read_text(encoding="utf-8")

    assert "[999 A_CODE_THAT_IS_NOT_IN_THE_SCHEMA]" in written
    assert RPC_NAME in written


def test_a_known_error_records_nothing(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    with pytest.raises(FloodWait):
        raise_it(420, message="FLOOD_WAIT_42")

    assert not (tmp_path / "unknown_errors.txt").exists()


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        pytest.param("42", 42, id="digits-become-a-number"),
        pytest.param(42, 42, id="a-number-stays-one"),
        pytest.param("FLOOD_WAIT_X", "FLOOD_WAIT_X", id="text-is-kept"),
        pytest.param(None, None, id="nothing-stays-nothing")
    ]
)
def test_value_keeps_whatever_is_not_a_number(value, expected):
    error = FloodWait(value)

    assert error.value == expected
    assert type(error.value) is type(expected)


def test_value_can_also_hold_the_raw_error_object():
    rpc_error = raw.types.RpcError(error_code=400, error_message="PEER_ID_INVALID")

    assert RPCError(rpc_error).value is rpc_error


def test_the_base_class_renders_without_any_of_its_attributes_set():
    assert RPCError.ID is None
    assert RPCError.CODE is None
    assert RPCError.NAME is None
    assert RPCError.MESSAGE == "{value}"
    assert str(RPCError("something")).startswith("Telegram says: [None None] - something")


def test_a_generated_subclass_carries_all_four_attributes():
    assert FloodWait.ID == "FLOOD_WAIT_X"
    assert FloodWait.CODE == 420
    assert FloodWait.NAME == "Flood"
    assert FloodWait.MESSAGE == "Please wait {value} seconds before repeating the action."
