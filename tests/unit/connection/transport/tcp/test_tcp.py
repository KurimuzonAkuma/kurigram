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


def test_tcp_takes_an_already_normalized_proxy_dataclass():
    web = WebProxy(hostname="relay.example.com", secret=bytes.fromhex(PLAIN_SECRET_HEX))
    t = TCP(proxy=web, dc_id=2)
    assert t.is_web_proxy
    assert t.proxy is web


def test_tcp_is_not_web_proxy_for_a_socks_proxy():
    t = TCP(proxy=Socks5Proxy(hostname="1.2.3.4", port=1080), dc_id=2)
    assert not t.is_web_proxy


def test_tcp_is_not_web_proxy_when_no_proxy_is_set():
    assert not TCP(dc_id=2).is_web_proxy


async def test_connect_via_web_proxy_requires_dc_id():
    web = WebProxy(hostname="relay.example.com", secret=bytes.fromhex(PLAIN_SECRET_HEX))
    t = TCPAbridged(proxy=web, dc_id=None)
    with pytest.raises(ValueError, match="dc_id"):
        await t._connect_via_web_proxy()


async def test_connect_via_web_proxy_requires_an_obfuscate_tag():
    web = WebProxy(hostname="relay.example.com", secret=bytes.fromhex(PLAIN_SECRET_HEX))
    t = TCP(proxy=web, dc_id=2)  # bare TCP: OBFUSCATE_TAG is None
    with pytest.raises(ValueError, match="OBFUSCATE_TAG"):
        await t._connect_via_web_proxy()


async def test_connect_via_web_proxy_rejects_dd_secret_on_the_wrong_class():
    web = WebProxy(hostname="relay.example.com", secret=bytes.fromhex(DD_SECRET_HEX))
    t = TCPAbridged(proxy=web, dc_id=2)  # dd secrets need TCPIntermediatePadded
    with pytest.raises(ValueError, match="TCPIntermediatePadded"):
        await t._connect_via_web_proxy()


async def test_connect_rejects_mtproxy_as_not_implemented():
    mtproxy = MtProxy(hostname="1.2.3.4", port=443, secret=bytes.fromhex(PLAIN_SECRET_HEX))
    t = TCPAbridged(proxy=mtproxy, dc_id=2)
    with pytest.raises(NotImplementedError):
        await t._connect(("unused", 0))
