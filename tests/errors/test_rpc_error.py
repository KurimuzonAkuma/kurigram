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

from pathlib import Path
from typing import Dict, Final, Optional, Tuple, Type, Union

import pytest

from pyrogram import raw
from pyrogram.errors import (
    ApnsVerifyCheck,
    BadRequest,
    FloodWait,
    IntegrityCheckClassic,
    PeerIdInvalid,
    PhoneMigrate,
    RecaptchaCheck,
    RPCError,
    UnknownError
)

RPC_NAME: Final[str] = "messages.GetHistory"
ATTRIBUTES: Final[Tuple[str, ...]] = ("ID", "CODE", "NAME", "MESSAGE")


def raise_it(code: int, *, message: str) -> None:
    RPCError.raise_it(
        raw.types.RpcError(error_code=code, error_message=message),
        raw.functions.messages.GetHistory
    )


def attributes_of(error_type: Type[RPCError]) -> Dict[str, Union[int, str, None]]:
    return {name: getattr(error_type, name) for name in ATTRIBUTES}


@pytest.mark.parametrize(
    ("code", "message", "error_type", "value"),
    [
        pytest.param(420, "FLOOD_WAIT_42", FloodWait, 42, id="a-number-in-the-message"),
        pytest.param(303, "PHONE_MIGRATE_2", PhoneMigrate, 2, id="another-number"),
        pytest.param(400, "PEER_ID_INVALID", PeerIdInvalid, None, id="no-number-at-all")
    ]
)
def test_a_known_error_takes_its_number_from_the_message(
    code: int,
    message: str,
    error_type: Type[RPCError],
    value: Optional[int]
) -> None:
    with pytest.raises(error_type) as raised:
        raise_it(code, message=message)

    error = raised.value

    assert error.value == value
    assert type(error.value) is type(value)


def test_a_negative_code_keeps_its_sign_in_the_text_only() -> None:
    with pytest.raises(FloodWait) as raised:
        raise_it(-420, message="FLOOD_WAIT_42")

    error = raised.value

    assert error.CODE == 420
    assert str(error) == (
        "Telegram says: [-420 FLOOD_WAIT_X] - Please wait 42 seconds before repeating the action."
        f' (caused by "{RPC_NAME}")'
    )


def test_the_message_template_is_filled_in_with_the_value() -> None:
    with pytest.raises(FloodWait) as raised:
        raise_it(420, message="FLOOD_WAIT_42")

    assert str(raised.value) == (
        "Telegram says: [420 FLOOD_WAIT_X] - Please wait 42 seconds before repeating the action."
        f' (caused by "{RPC_NAME}")'
    )


def test_an_unknown_message_falls_back_to_the_class_of_its_code(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch
) -> None:
    # An unknown error appends to `unknown_errors.txt` in the working directory
    # (`RPCError.__init__`), which is why every unknown case runs somewhere disposable.
    monkeypatch.chdir(tmp_path)

    with pytest.raises(BadRequest) as raised:
        raise_it(400, message="SOMETHING_THE_SCHEMA_DOES_NOT_KNOW")

    error = raised.value

    assert error.value == "[400 SOMETHING_THE_SCHEMA_DOES_NOT_KNOW]"
    assert type(error.value) is str


def test_an_unknown_code_becomes_an_unknown_error(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)

    with pytest.raises(UnknownError) as raised:
        raise_it(999, message="A_CODE_THAT_IS_NOT_IN_THE_SCHEMA")

    # `UnknownError` sets no `ID`, so the text falls back to `NAME`, and its `MESSAGE` is the
    # inherited `"{value}"`, so the whole payload is what it renders.
    assert str(raised.value) == (
        "Telegram says: [520 Unknown error] - [999 A_CODE_THAT_IS_NOT_IN_THE_SCHEMA]"
        f' (caused by "{RPC_NAME}")'
    )


def test_an_unknown_error_is_recorded_in_a_file(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)

    with pytest.raises(UnknownError):
        raise_it(999, message="A_CODE_THAT_IS_NOT_IN_THE_SCHEMA")

    written = (tmp_path / "unknown_errors.txt").read_text(encoding="utf-8")

    assert "[999 A_CODE_THAT_IS_NOT_IN_THE_SCHEMA]" in written
    assert RPC_NAME in written


def test_a_known_error_records_nothing(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
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
def test_value_keeps_whatever_is_not_a_number(
    value: Union[int, str, None],
    expected: Union[int, str, None]
) -> None:
    error = FloodWait(value)

    assert error.value == expected
    assert type(error.value) is type(expected)


def test_value_can_also_hold_the_raw_error_object() -> None:
    rpc_error = raw.types.RpcError(error_code=400, error_message="PEER_ID_INVALID")

    assert RPCError(rpc_error).value is rpc_error


@pytest.mark.parametrize(
    ("error_type", "attributes"),
    [
        pytest.param(
            RPCError,
            {"ID": None, "CODE": None, "NAME": None, "MESSAGE": "{value}"},
            id="the-base-class-sets-none-of-them"
        ),
        pytest.param(
            FloodWait,
            {
                "ID": "FLOOD_WAIT_X",
                "CODE": 420,
                "NAME": "Flood",
                "MESSAGE": "Please wait {value} seconds before repeating the action."
            },
            id="a-generated-subclass-sets-all-of-them"
        )
    ]
)
def test_an_error_class_declares_what_it_is(
    error_type: Type[RPCError],
    attributes: Dict[str, Union[int, str, None]]
) -> None:
    assert attributes_of(error_type) == attributes


def test_the_base_class_renders_the_value_on_its_own() -> None:
    assert str(RPCError("something")) == "Telegram says: [None None] - something"


@pytest.mark.parametrize(
    ("message", "error_type", "value", "text"),
    [
        pytest.param(
            "RECAPTCHA_CHECK_signup__6LdcABcDEFghIJKlmnOP",
            RecaptchaCheck,
            "signup__6LdcABcDEFghIJKlmnOP",
            "Telegram says: [403 RECAPTCHA_CHECK_X] - The request can't be completed unless "
            "reCAPTCHA verification signup__6LdcABcDEFghIJKlmnOP is performed.",
            id="the-shape-telegram-sends"
        ),
        # The two strings TDLib feeds its own verification tests with:
        # https://github.com/tdlib/td/blob/022d60202e446ad1287b9fb68e687c8a0760788b/td/telegram/net/NetQueryDispatcher.cpp#L73-L82
        #
        # The reCAPTCHA one carries an action with an underscore of its own, and TDLib splits it
        # off at the *last* `__` — its loop keeps overwriting rather than breaking, so `AB_CD` is
        # the action and `KEY` the site key id:
        # https://github.com/tdlib/td/blob/022d60202e446ad1287b9fb68e687c8a0760788b/td/telegram/net/NetQueryDispatcher.cpp#L124-L130
        #
        # Nothing here splits them apart; `value` keeps the payload whole.
        pytest.param(
            "RECAPTCHA_CHECK_AB_CD__KEY",
            RecaptchaCheck,
            "AB_CD__KEY",
            "Telegram says: [403 RECAPTCHA_CHECK_X] - The request can't be completed unless "
            "reCAPTCHA verification AB_CD__KEY is performed.",
            id="an-action-with-an-underscore"
        ),
        pytest.param(
            "RECAPTCHA_CHECK_signup",
            RecaptchaCheck,
            "signup",
            "Telegram says: [403 RECAPTCHA_CHECK_X] - The request can't be completed unless "
            "reCAPTCHA verification signup is performed.",
            id="no-key-at-all"
        ),
        # The template has nothing to put in its hole, hence the two spaces.
        pytest.param(
            "RECAPTCHA_CHECK_",
            RecaptchaCheck,
            "",
            "Telegram says: [403 RECAPTCHA_CHECK_X] - The request can't be completed unless "
            "reCAPTCHA verification  is performed.",
            id="no-parameters-at-all"
        ),
        pytest.param(
            "APNS_VERIFY_CHECK_ABCD",
            ApnsVerifyCheck,
            "ABCD",
            "Telegram says: [403 APNS_VERIFY_CHECK_X] - The request can't be completed unless "
            "the APNs verification ABCD is performed.",
            id="an-apns-nonce"
        ),
        pytest.param(
            "INTEGRITY_CHECK_CLASSIC_ABCD",
            IntegrityCheckClassic,
            "ABCD",
            "Telegram says: [403 INTEGRITY_CHECK_CLASSIC_X] - The request can't be completed "
            "unless the classic Play Integrity verification ABCD is performed.",
            id="a-play-integrity-nonce"
        )
    ]
)
def test_a_verification_error_keeps_its_parameters_whole(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    message: str,
    error_type: Type[RPCError],
    value: str,
    text: str
) -> None:
    # Run somewhere disposable: before the prefixes were split off these raised a bare `Forbidden`
    # and appended to `unknown_errors.txt`, which is what the next test asserts no longer happens.
    monkeypatch.chdir(tmp_path)

    with pytest.raises(error_type) as raised:
        raise_it(403, message=message)

    error = raised.value

    # The payload is what a caller acts on, the text is what a human reads. The text is spelled out
    # rather than rendered from `value` a second time, because both sides of such a comparison would
    # go through the same `MESSAGE` and neither would say anything about it.
    assert error.value == value
    assert str(error) == f'{text} (caused by "{RPC_NAME}")'


def test_a_verification_error_is_not_an_unknown_error(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)

    with pytest.raises(RecaptchaCheck):
        raise_it(403, message="RECAPTCHA_CHECK_signup__6LdcABcDEFghIJKlmnOP")

    assert not (tmp_path / "unknown_errors.txt").exists()
