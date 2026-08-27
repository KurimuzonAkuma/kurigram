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

import asyncio
import hashlib
from typing import Final, NamedTuple, Tuple, Type

import pytest

from python_socks import ProxyType

from pyrogram.connection.proxy import HTTPProxy, MTProxy, SOCKS5Proxy, WebProxy
from pyrogram.connection.transport.tcp import TCPAbridged, TCPIntermediatePadded
from pyrogram.connection.transport.tcp.tcp import (
    ABRIDGED_OBFUSCATE_TAG,
    INTERMEDIATE_PADDED_OBFUSCATE_TAG,
    TCP,
)
from pyrogram.crypto import aes

from tests.web_proxy_values import DD_SECRET_HEX, PLAIN_SECRET_HEX

# The obfuscated2 handshake is one fixed-size buffer; only its last 8 bytes are
#  encrypted.
_OBFUSCATED2_HEADER_SIZE: Final[int] = 64

# An address the transport must never dial when a proxy is configured. TEST-NET-2
#  is unroutable, so a connect that reaches for it fails instead of passing.
_UNREACHABLE_DC_ADDRESS: Final[Tuple[str, int]] = ("198.51.100.1", 443)

_DC_ID: Final[int] = 2


def _web_proxy(secret_hex: str = PLAIN_SECRET_HEX) -> WebProxy:
    return WebProxy(hostname="relay.example.com", secret=bytes.fromhex(secret_hex))


class _ProxyStub(NamedTuple):
    server: asyncio.AbstractServer
    port: int
    received: "asyncio.Future[bytes]"


async def _start_proxy_stub(*, read_bytes: int) -> _ProxyStub:
    """A local server standing in for an MTProxy: reads `read_bytes` and stops."""
    received: "asyncio.Future[bytes]" = asyncio.get_running_loop().create_future()

    # `asyncio.start_server` calls its handler with two positional arguments, so
    #  this signature is the stdlib's rather than ours.
    async def serve(reader: asyncio.StreamReader, _writer: asyncio.StreamWriter) -> None:
        received.set_result(await reader.readexactly(read_bytes))

    server = await asyncio.start_server(serve, host="127.0.0.1", port=0)

    return _ProxyStub(server=server, port=server.sockets[0].getsockname()[1], received=received)


def test_tcp_takes_an_already_normalized_proxy_dataclass() -> None:
    web_proxy = _web_proxy()

    transport = TCP(proxy=web_proxy, dc_id=2)

    assert transport.is_web_proxy
    assert transport.proxy is web_proxy


def test_tcp_is_not_web_proxy_for_a_socks_proxy() -> None:
    transport = TCP(proxy=SOCKS5Proxy(hostname="1.2.3.4", port=1080), dc_id=2)

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


async def test_connect_via_mtproxy_rejects_a_dd_secret_on_the_wrong_class() -> None:
    # The same check the WEB scheme makes, reached through the shared helper.
    mtproxy = MTProxy(hostname="1.2.3.4", port=443, secret=bytes.fromhex(DD_SECRET_HEX))
    transport = TCPAbridged(proxy=mtproxy, dc_id=_DC_ID)

    with pytest.raises(ValueError, match="TCPIntermediatePadded"):
        await transport._connect_via_mtproxy()


async def test_connect_via_mtproxy_rejects_a_fake_tls_secret_for_now() -> None:
    mtproxy = MTProxy(
        hostname="1.2.3.4",
        port=443,
        secret=bytes.fromhex(PLAIN_SECRET_HEX),
        sni_hostname="www.example.com",
    )
    transport = TCPAbridged(proxy=mtproxy, dc_id=_DC_ID)

    with pytest.raises(NotImplementedError):
        await transport._connect_via_mtproxy()


@pytest.mark.parametrize(
    ("protocol_factory", "secret_hex", "expected_tag"),
    [
        pytest.param(TCPAbridged, PLAIN_SECRET_HEX, ABRIDGED_OBFUSCATE_TAG, id="plain-abridged"),
        pytest.param(
            TCPIntermediatePadded,
            DD_SECRET_HEX,
            INTERMEDIATE_PADDED_OBFUSCATE_TAG,
            id="dd-padded",
        ),
    ],
)
async def test_connect_via_mtproxy_sends_a_header_the_proxy_can_read(
    protocol_factory: Type[TCP],
    secret_hex: str,
    expected_tag: bytes,
) -> None:
    # Reads the handshake back exactly as stock MTProxy does: derive the keys from
    #  the cleartext half, then run the whole 64-byte buffer through CTR so the tag
    #  and dc id at 56-62 are decrypted at the keystream offset they were written at.
    stub = await _start_proxy_stub(read_bytes=_OBFUSCATED2_HEADER_SIZE)

    full_secret = bytes.fromhex(secret_hex)
    transport = protocol_factory(
        proxy=MTProxy(hostname="127.0.0.1", port=stub.port, secret=full_secret),
        dc_id=_DC_ID,
    )

    try:
        await transport.connect(_UNREACHABLE_DC_ADDRESS)
        header = await asyncio.wait_for(stub.received, timeout=TCP.TIMEOUT)
    finally:
        await transport.close()
        stub.server.close()
        await stub.server.wait_closed()

    bare_secret = full_secret[1:] if len(full_secret) == 17 else full_secret
    key = hashlib.sha256(header[8:40] + bare_secret).digest()
    decrypted = aes.ctr256_decrypt(header, key, bytearray(header[40:56]), bytearray(1))

    assert decrypted[56:60] == expected_tag
    assert int.from_bytes(decrypted[60:62], "little", signed=True) == _DC_ID


async def test_connect_via_mtproxy_leaves_no_bare_tag_before_the_first_packet() -> None:
    # TCPAbridged opens a plain connection with a bare 0xef byte. Over MTProxy the
    #  handshake already carries that tag, so sending it again would shift the whole
    #  stream by one byte and the proxy would read a 0xef-long packet.
    payload: Final[bytes] = b"\x01\x02\x03\x04"

    # The header, then the abridged length byte and the payload behind it.
    stub = await _start_proxy_stub(read_bytes=_OBFUSCATED2_HEADER_SIZE + 1 + len(payload))

    secret = bytes.fromhex(PLAIN_SECRET_HEX)
    transport = TCPAbridged(
        proxy=MTProxy(hostname="127.0.0.1", port=stub.port, secret=secret),
        dc_id=_DC_ID,
    )

    try:
        await transport.connect(_UNREACHABLE_DC_ADDRESS)
        await transport.send(payload)
        stream = await asyncio.wait_for(stub.received, timeout=TCP.TIMEOUT)
    finally:
        await transport.close()
        stub.server.close()
        await stub.server.wait_closed()

    key = hashlib.sha256(stream[8:40] + secret).digest()
    decrypted = aes.ctr256_decrypt(stream, key, bytearray(stream[40:56]), bytearray(1))

    # One 4-byte word, so the abridged length byte is 1 and the payload follows it.
    assert decrypted[_OBFUSCATED2_HEADER_SIZE:] == bytes([len(payload) // 4]) + payload


async def test_build_proxy_keeps_a_credential_a_url_would_mangle() -> None:
    # `SocksProxy.from_url` parses the credentials back out with `unquote()`,
    #  so a password holding `@`, `:` or `%` came out different from the one
    #  the caller passed, and the proxy rejected the login.
    socks_proxy = SOCKS5Proxy(
        hostname="1.2.3.4",
        port=1080,
        username="user@example.com",
        password="p:a%40ss",
    )
    transport = TCPAbridged(proxy=socks_proxy, dc_id=2)

    dialed = await transport._build_proxy()

    assert dialed._username == socks_proxy.username
    assert dialed._password == socks_proxy.password


async def test_build_proxy_keeps_a_username_that_comes_without_a_password() -> None:
    # `parse_proxy_url` resets both credentials to `''` when either is missing,
    #  so a username-only proxy was dialed anonymously.
    socks_proxy = SOCKS5Proxy(hostname="1.2.3.4", port=1080, username="user")
    transport = TCPAbridged(proxy=socks_proxy, dc_id=2)

    dialed = await transport._build_proxy()

    assert dialed._username == "user"


async def test_build_proxy_maps_each_scheme_to_its_dial_type() -> None:
    http_proxy = HTTPProxy(hostname="1.2.3.4", port=8080)
    transport = TCPAbridged(proxy=http_proxy, dc_id=2)

    dialed = await transport._build_proxy()

    assert dialed._proxy_type is ProxyType.HTTP


async def test_build_proxy_rejects_a_scheme_it_cannot_dial() -> None:
    transport = TCPAbridged(proxy=_web_proxy(), dc_id=2)

    with pytest.raises(ValueError, match="WebProxy"):
        await transport._build_proxy()
