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

from pyrogram.connection.proxy import MtProxy, Socks5Proxy, WebProxy
from pyrogram.connection.transport.tcp import TCPAbridged
from pyrogram.connection.transport.tcp.tcp import TCP

from tests.web_proxy_values import DD_SECRET_HEX, PLAIN_SECRET_HEX


def _web_proxy(secret_hex: str = PLAIN_SECRET_HEX) -> WebProxy:
    return WebProxy(hostname="relay.example.com", secret=bytes.fromhex(secret_hex))


def test_tcp_takes_an_already_normalized_proxy_dataclass() -> None:
    web_proxy = _web_proxy()

    transport = TCP(proxy=web_proxy, dc_id=2)

    assert transport.is_web_proxy
    assert transport.proxy is web_proxy


def test_tcp_is_not_web_proxy_for_a_socks_proxy() -> None:
    transport = TCP(proxy=Socks5Proxy(hostname="1.2.3.4", port=1080), dc_id=2)

    assert not transport.is_web_proxy


def test_tcp_is_not_web_proxy_when_no_proxy_is_set() -> None:
    assert not TCP(dc_id=2).is_web_proxy


async def test_connect_via_web_proxy_requires_dc_id() -> None:
    transport = TCPAbridged(proxy=_web_proxy(), dc_id=None)

    with pytest.raises(ValueError, match="dc_id"):
        await transport._connect_via_web_proxy()


async def test_connect_via_web_proxy_requires_an_obfuscate_tag() -> None:
    # Bare `TCP` leaves `OBFUSCATE_TAG` unset; only its packet-framing
    #  subclasses define one.
    transport = TCP(proxy=_web_proxy(), dc_id=2)

    with pytest.raises(ValueError, match="OBFUSCATE_TAG"):
        await transport._connect_via_web_proxy()


async def test_connect_via_web_proxy_rejects_dd_secret_on_the_wrong_class() -> None:
    # A dd-prefixed secret asks for padded intermediate framing, which only
    #  `TCPIntermediatePadded` speaks.
    transport = TCPAbridged(proxy=_web_proxy(DD_SECRET_HEX), dc_id=2)

    with pytest.raises(ValueError, match="TCPIntermediatePadded"):
        await transport._connect_via_web_proxy()


async def test_connect_rejects_mtproxy_as_not_implemented() -> None:
    mtproxy = MtProxy(hostname="1.2.3.4", port=443, secret=bytes.fromhex(PLAIN_SECRET_HEX))
    transport = TCPAbridged(proxy=mtproxy, dc_id=2)

    with pytest.raises(NotImplementedError):
        await transport._connect(("unused", 0))
