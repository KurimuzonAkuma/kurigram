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
from dataclasses import dataclass
from datetime import datetime
from importlib import import_module
from typing import Final, Optional, Pattern, Tuple, Type, Union

from pyrogram import raw
from pyrogram.raw.core import TLObject
from .exceptions.all import exceptions

STRING_PARAMETER_PREFIXES: Final[Tuple[str, ...]] = (
    "APNS_VERIFY_CHECK_",
    "INTEGRITY_CHECK_CLASSIC_",
    "RECAPTCHA_CHECK_"
)
PARAMETER: Final[Pattern[str]] = re.compile(r"_(\d+)")

# Canonical: `compiler/errors/compiler.py`, which writes one row per code keyed `"_"`, holding the
# name of the category class that code's errors subclass: `BadRequest` for 400, `Forbidden` for
# 403. It is what an error whose message is not in the table falls back to.
CATEGORY: Final[str] = "_"


@dataclass(frozen=True)
class _MessageParts:
    error_id: str
    value: Optional[str]


def _split_error_message(error_message: str) -> _MessageParts:
    # The three verification errors are the only ones whose parameters are a string rather than a
    # number, so `PARAMETER` rewrites part of the payload and yields an id that matches no table
    # row: the caller gets a bare `Forbidden` instead of the error itself, and every occurrence
    # appends a line to `unknown_errors.txt`.
    #
    # Reproduce, without the loop below:
    #     RPCError.raise_it(
    #         raw.types.RpcError(
    #             error_code=403,
    #             error_message="RECAPTCHA_CHECK_signup__6LdcABcDEFghIJKlmnOP"
    #         ),
    #         raw.functions.auth.SendCode
    #     )
    #
    #     pyrogram.errors.exceptions.forbidden_403.Forbidden: Telegram says: [403 Forbidden]
    #     - [403 RECAPTCHA_CHECK_signup__6LdcABcDEFghIJKlmnOP] (caused by "auth.SendCode")
    #
    # TDLib splits the same three prefixes off before anything else looks at the message:
    # https://github.com/tdlib/td/blob/022d60202e446ad1287b9fb68e687c8a0760788b/td/telegram/net/NetQueryDispatcher.cpp#L112-L146
    for prefix in STRING_PARAMETER_PREFIXES:
        if error_message.startswith(prefix):
            return _MessageParts(
                error_id=f"{prefix}X",
                value=error_message[len(prefix):]
            )

    match = PARAMETER.search(error_message)
    if match is None:
        return _MessageParts(error_id=error_message, value=None)

    # The tables spell a parameter as `_X`, so the id of a message is the message with its numbers
    # blanked out: `FLOOD_WAIT_42` is listed as `FLOOD_WAIT_X`. `sub()` rather than the first match
    # alone, because the id is the shape of the whole message; no table id carries more than one
    # parameter, which is why the single `search()` above is enough to read the value back.
    return _MessageParts(
        error_id=PARAMETER.sub("_X", error_message),
        value=match.group(1)
    )


class RPCError(Exception):
    ID: Optional[str] = None
    CODE: Optional[int] = None
    NAME: Optional[str] = None
    MESSAGE: str = "{value}"
    VALUE_NAME: str = "value"

    def __init__(
        self,
        value: Optional[Union[int, str, raw.types.RpcError]] = None,
        rpc_name: Optional[str] = None,
        is_unknown: bool = False,
        is_signed: bool = False
    ):
        code = f"-{self.CODE}" if is_signed else self.CODE
        name = self.ID or self.NAME
        description = self.MESSAGE.format(**{self.VALUE_NAME: value})
        caused_by = f' (caused by "{rpc_name}")' if rpc_name else ""
        message = f"Telegram says: [{code} {name}] - {description}{caused_by}"

        super().__init__(message)

        self.value: Optional[Union[int, str, raw.types.RpcError]]

        # `isdecimal()`, not `isdigit()`: the latter is true for "²" too, and `int("²")` raises.
        if isinstance(value, str) and value.isdecimal():
            self.value = int(value)
        else:
            self.value = value

        if is_unknown:
            with open("unknown_errors.txt", "a", encoding="utf-8") as f:
                f.write(f"{datetime.now()}\t{value}\t{rpc_name}\n")

    @staticmethod
    def raise_it(rpc_error: "raw.types.RpcError", rpc_type: Type[TLObject]):
        error_code = rpc_error.error_code
        is_signed = error_code < 0
        error_message = rpc_error.error_message
        rpc_name = ".".join(rpc_type.QUALNAME.split(".")[1:])

        if is_signed:
            error_code = -error_code

        if error_code not in exceptions:
            raise UnknownError(
                value=f"[{error_code} {error_message}]",
                rpc_name=rpc_name,
                is_unknown=True,
                is_signed=is_signed
            )

        errors = import_module("pyrogram.errors")

        parts = _split_error_message(error_message)
        if parts.error_id not in exceptions[error_code]:
            error_type = getattr(errors, exceptions[error_code][CATEGORY])

            raise error_type(
                value=f"[{error_code} {error_message}]",
                rpc_name=rpc_name,
                is_unknown=True,
                is_signed=is_signed
            )

        error_type = getattr(errors, exceptions[error_code][parts.error_id])

        raise error_type(
            value=parts.value,
            rpc_name=rpc_name,
            is_unknown=False,
            is_signed=is_signed
        )


class UnknownError(RPCError):
    CODE = 520
    """:obj:`int`: Error code"""
    NAME = "Unknown error"
