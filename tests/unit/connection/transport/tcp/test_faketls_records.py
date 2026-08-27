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

from typing import Final, List, Optional

import pytest

from pyrogram.connection.transport.tcp.faketls_records import (
    APPLICATION_DATA_PREFIX,
    CHANGE_CIPHER_SPEC,
    RECORD_HEADER_SIZE,
    RECORD_LENGTH_SIZE,
    FakeTlsRecords,
    _MAX_RECORD_PAYLOAD,
)

# Stands in for the obfuscated2 header, which is what the transport hands over as
#  the prologue.
_PROLOGUE: Final[bytes] = bytes(range(64))


class _Wire:
    """Serves `read_exactly` out of a fixed buffer, then reports the end as `None`."""

    def __init__(self, data: bytes) -> None:
        self._data = data
        self._offset = 0

    async def __call__(self, length: int) -> Optional[bytes]:
        if self._offset + length > len(self._data):
            return None

        chunk = self._data[self._offset : self._offset + length]
        self._offset += length

        return chunk


def _records(payload: bytes) -> FakeTlsRecords:
    return FakeTlsRecords(_Wire(payload), prologue=b"")


def _record(payload: bytes) -> bytes:
    return APPLICATION_DATA_PREFIX + len(payload).to_bytes(RECORD_LENGTH_SIZE, "big") + payload


def _record_payloads(wire: bytes) -> List[bytes]:
    payloads: List[bytes] = []
    offset = 0

    while offset < len(wire):
        assert wire[offset : offset + len(APPLICATION_DATA_PREFIX)] == APPLICATION_DATA_PREFIX

        length = int.from_bytes(wire[offset + len(APPLICATION_DATA_PREFIX) : offset + RECORD_HEADER_SIZE], "big")
        payloads.append(wire[offset + RECORD_HEADER_SIZE : offset + RECORD_HEADER_SIZE + length])
        offset += RECORD_HEADER_SIZE + length

    return payloads


def test_wrap_sends_one_change_cipher_spec_and_never_a_second() -> None:
    records = _records(b"")

    first = records.wrap(b"one")
    second = records.wrap(b"two")

    assert first.startswith(CHANGE_CIPHER_SPEC)
    assert CHANGE_CIPHER_SPEC not in second


def test_wrap_puts_the_prologue_in_front_of_the_first_payload_only() -> None:
    records = FakeTlsRecords(_Wire(b""), prologue=_PROLOGUE)

    first = records.wrap(b"one")
    second = records.wrap(b"two")

    assert _record_payloads(first[len(CHANGE_CIPHER_SPEC) :]) == [_PROLOGUE + b"one"]
    assert _record_payloads(second) == [b"two"]


def test_wrap_cuts_a_payload_no_single_record_can_hold() -> None:
    # One byte past what a single 2-byte length field can describe. The whole
    #  payload used to go into one record, so this size raised `struct.error`.
    payload = bytes(0x10000 + 1)
    records = _records(b"")

    payloads = _record_payloads(records.wrap(payload)[len(CHANGE_CIPHER_SPEC) :])

    assert len(payloads) > 1
    assert max(len(one) for one in payloads) <= _MAX_RECORD_PAYLOAD
    assert b"".join(payloads) == payload


async def test_recv_joins_records_into_the_requested_length() -> None:
    records = _records(_record(b"abc") + _record(b"de") + _record(b"f"))

    assert await records.recv(6) == b"abcdef"


async def test_recv_serves_a_short_read_out_of_the_buffered_record() -> None:
    records = _records(_record(b"abcdef"))

    assert await records.recv(2) == b"ab"
    assert await records.recv(4) == b"cdef"


async def test_recv_reports_a_stream_that_ended_as_none() -> None:
    records = _records(_record(b"abc"))

    assert await records.recv(4) is None


async def test_recv_rejects_a_record_that_is_not_application_data() -> None:
    handshake_record = b"\x16\x03\x03" + (3).to_bytes(RECORD_LENGTH_SIZE, "big") + b"abc"
    records = _records(handshake_record)

    with pytest.raises(OSError, match="application-data"):
        await records.recv(3)
