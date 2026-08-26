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

from pyrogram.connection.connection import Connection, _protocol_dc_id


def test_protocol_dc_id_plain() -> None:
    assert _protocol_dc_id(2, test_mode=False, media=False) == 2


def test_protocol_dc_id_media_is_negated() -> None:
    assert _protocol_dc_id(2, test_mode=False, media=True) == -2


def test_protocol_dc_id_test_mode_is_shifted() -> None:
    assert _protocol_dc_id(2, test_mode=True, media=False) == 10002


def test_protocol_dc_id_test_mode_media_shifts_then_negates() -> None:
    assert _protocol_dc_id(2, test_mode=True, media=True) == -10002


def test_connection_computes_protocol_dc_id_from_media_and_test_mode() -> None:
    connection = Connection(dc_id=5, server_address="unused", port=443, test_mode=True, media=True)
    assert connection._protocol_dc_id == -10005
