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

from typing import Final, Optional, Type

import pytest

from pyrogram.connection.connection import Connection, _protocol_dc_id, transport_class_for
from pyrogram.connection.proxy import MTProxy, Proxy, SOCKS5Proxy, WebProxy
from pyrogram.connection.transport import TCP, TCPAbridged, TCPFull, TCPIntermediatePadded

from tests.unit.proxy_values import DD_SECRET_HEX, PLAIN_SECRET_HEX, SNI_DOMAIN

_PLAIN_MTPROXY: Final[MTProxy] = MTProxy(
    hostname="11.22.33.44",
    port=443,
    secret=bytes.fromhex(PLAIN_SECRET_HEX),
)
_DD_MTPROXY: Final[MTProxy] = MTProxy(
    hostname="11.22.33.44",
    port=443,
    secret=bytes.fromhex(DD_SECRET_HEX),
)
# An ee secret keeps a bare 16-byte key: its marker and domain came off in
#  `normalize_proxy`, and `sni_hostname` is what records that it was one.
_EE_MTPROXY: Final[MTProxy] = MTProxy(
    hostname="11.22.33.44",
    port=443,
    secret=bytes.fromhex(PLAIN_SECRET_HEX),
    sni_hostname=SNI_DOMAIN,
)


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


@pytest.mark.parametrize(
    ("proxy", "expected"),
    [
        pytest.param(None, TCPAbridged, id="no-proxy"),
        pytest.param(SOCKS5Proxy(hostname="11.22.33.44", port=1234), TCPAbridged, id="socks5"),
        pytest.param(_PLAIN_MTPROXY, TCPAbridged, id="mtproxy-plain"),
        pytest.param(_DD_MTPROXY, TCPIntermediatePadded, id="mtproxy-dd"),
        pytest.param(_EE_MTPROXY, TCPIntermediatePadded, id="mtproxy-ee"),
        pytest.param(
            WebProxy(hostname="relay.example.com", secret=bytes.fromhex(PLAIN_SECRET_HEX)),
            TCPAbridged,
            id="web-plain",
        ),
        pytest.param(
            WebProxy(hostname="relay.example.com", secret=bytes.fromhex(DD_SECRET_HEX)),
            TCPIntermediatePadded,
            id="web-dd",
        ),
    ],
)
def test_transport_class_for_reads_the_framing_off_the_secret(
    proxy: Optional[Proxy],
    expected: Type[TCP],
) -> None:
    assert transport_class_for(proxy) is expected


def test_transport_class_for_keeps_the_default_when_the_secret_asks_for_nothing() -> None:
    # A plain secret pads nothing, so whatever the caller picked still stands.
    assert transport_class_for(_PLAIN_MTPROXY, default=TCPFull) is TCPFull


def test_transport_class_for_overrides_a_default_the_secret_contradicts() -> None:
    assert transport_class_for(_EE_MTPROXY, default=TCPFull) is TCPIntermediatePadded


def test_connection_takes_its_transport_from_the_proxy_secret() -> None:
    connection = Connection(
        dc_id=2,
        server_address="unused",
        port=443,
        test_mode=False,
        proxy=_EE_MTPROXY,
    )

    assert connection.protocol_factory is TCPIntermediatePadded


def test_connection_keeps_the_requested_transport_without_a_padded_secret() -> None:
    connection = Connection(
        dc_id=2,
        server_address="unused",
        port=443,
        test_mode=False,
        proxy=_PLAIN_MTPROXY,
        protocol_factory=TCPFull,
    )

    assert connection.protocol_factory is TCPFull
