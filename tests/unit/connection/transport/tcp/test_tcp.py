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
import hmac
import time
from typing import Final, NamedTuple, Tuple, Type

import pytest

from python_socks import ProxyType

from pyrogram.connection.proxy import HTTPProxy, MTProxy, SOCKS5Proxy, WebProxy
from pyrogram.connection.transport.tcp import TCPAbridged, TCPIntermediatePadded
from pyrogram.connection.transport.tcp.faketls_records import (
    APPLICATION_DATA_PREFIX,
    CHANGE_CIPHER_SPEC,
    RECORD_HEADER_SIZE,
    RECORD_LENGTH_SIZE,
)
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

_SNI_DOMAIN: Final[str] = "www.example.com"

# The ClientHello record header, and the offset of the random field both sides
#  authenticate - 5 bytes of record header, 4 of handshake header, 2 of version.
_CLIENT_HELLO_PREFIX: Final[bytes] = b"\x16\x03\x01"
_RANDOM_OFFSET: Final[int] = 11
_RANDOM_SIZE: Final[int] = 32

# The last four bytes of the greeting's random carry the clock. How far the value
#  read back may sit from this machine's own clock before the test calls it wrong.
_TIMESTAMP_SIZE: Final[int] = 4
_CLOCK_SKEW_ALLOWANCE: Final[int] = 60

# The intermediate framing: a little-endian length, then up to 15 random bytes
#  of padding after the payload. A frame under 24 bytes is read as a quick ack
#  or an error code instead of a packet.
_LENGTH_PREFIX_SIZE: Final[int] = 4
_MAX_INTERMEDIATE_PADDING: Final[int] = 15
_MIN_INTERMEDIATE_PACKET_SIZE: Final[int] = 24


def _web_proxy(secret_hex: str = PLAIN_SECRET_HEX) -> WebProxy:
    return WebProxy(hostname="relay.example.com", secret=bytes.fromhex(secret_hex))


# Every `serve` below is an `asyncio.start_server` handler, which the stdlib calls
#  with two positional arguments - so those signatures are its shape, not ours.


class _ProxyStub(NamedTuple):
    server: asyncio.AbstractServer
    port: int
    received: "asyncio.Future[bytes]"


async def _start_proxy_stub(*, read_bytes: int) -> _ProxyStub:
    """A local server standing in for an MTProxy: reads `read_bytes` and stops."""
    received: "asyncio.Future[bytes]" = asyncio.get_running_loop().create_future()

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


async def test_connect_via_mtproxy_rejects_an_ee_secret_on_the_wrong_class() -> None:
    # An ee secret is 18 bytes or more before its marker and domain come off, so
    #  it asks for random padding the same way a dd one does.
    mtproxy = MTProxy(
        hostname="1.2.3.4",
        port=443,
        secret=bytes.fromhex(PLAIN_SECRET_HEX),
        sni_hostname=_SNI_DOMAIN,
    )
    transport = TCPAbridged(proxy=mtproxy, dc_id=_DC_ID)

    with pytest.raises(ValueError, match="TCPIntermediatePadded"):
        await transport._connect_via_mtproxy()


class _FakeTlsStub(NamedTuple):
    server: asyncio.AbstractServer
    port: int
    hello: "asyncio.Future[bytes]"
    received: "asyncio.Future[bytes]"


def _server_hello(client_random: bytes, *, secret: bytes) -> bytes:
    """The two segments a real proxy answers a greeting with, signed with `secret`."""
    # A ServerHello of the shape TDLib expects, then a change-cipher-spec glued
    #  to an empty application record.
    body = b"\x02\x00\x00\x4c\x03\x03" + bytes(_RANDOM_SIZE) + bytes(42)
    response = (
        b"\x16\x03\x03"
        + len(body).to_bytes(RECORD_LENGTH_SIZE, "big")
        + body
        + CHANGE_CIPHER_SPEC
        + APPLICATION_DATA_PREFIX
        + bytes(RECORD_LENGTH_SIZE)
    )
    digest = hmac.new(secret, client_random + response, hashlib.sha256).digest()

    return response[:_RANDOM_OFFSET] + digest + response[_RANDOM_OFFSET + _RANDOM_SIZE :]


def _client_decrypt_args(header: bytes, *, secret: bytes) -> Tuple[bytes, bytearray, bytearray]:
    # The proxy sends under the client's receive keys, which `build_obfuscated2_header`
    #  derives from the same nonce read backwards.
    tail = bytes(bytearray(header)[55:7:-1])

    return hashlib.sha256(tail[:32] + secret).digest(), bytearray(tail[32:48]), bytearray(1)


def _as_records(payload: bytes, *, record_size: int) -> bytes:
    wire = bytearray()

    for start in range(0, len(payload), record_size):
        piece = payload[start : start + record_size]
        wire += APPLICATION_DATA_PREFIX + len(piece).to_bytes(RECORD_LENGTH_SIZE, "big") + piece

    return bytes(wire)


async def _start_fake_tls_stub(
    *,
    secret: bytes,
    expects_packet: bool = False,
    reply: bytes = b"",
    reply_record_size: int = 1,
) -> _FakeTlsStub:
    """A local server standing in for a fake-TLS MTProxy that knows `secret`."""
    loop = asyncio.get_running_loop()
    hello: "asyncio.Future[bytes]" = loop.create_future()
    received: "asyncio.Future[bytes]" = loop.create_future()

    async def serve(reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
        head = await reader.readexactly(RECORD_HEADER_SIZE)
        greeting = head + await reader.readexactly(int.from_bytes(head[3:5], "big"))
        hello.set_result(greeting)

        writer.write(_server_hello(greeting[_RANDOM_OFFSET : _RANDOM_OFFSET + _RANDOM_SIZE], secret=secret))
        await writer.drain()

        if not expects_packet:
            return

        # Read what a real proxy reads - the change-cipher-spec and then one whole
        #  application record - rather than a byte count the random padding decides.
        prologue = await reader.readexactly(len(CHANGE_CIPHER_SPEC) + RECORD_HEADER_SIZE)
        body = await reader.readexactly(int.from_bytes(prologue[-RECORD_LENGTH_SIZE:], "big"))
        received.set_result(prologue + body)

        if not reply:
            return

        encrypted = aes.ctr256_encrypt(
            reply,
            *_client_decrypt_args(body[:_OBFUSCATED2_HEADER_SIZE], secret=secret),
        )

        writer.write(_as_records(encrypted, record_size=reply_record_size))
        await writer.drain()

    server = await asyncio.start_server(serve, host="127.0.0.1", port=0)

    return _FakeTlsStub(
        server=server,
        port=server.sockets[0].getsockname()[1],
        hello=hello,
        received=received,
    )


def _fake_tls_mtproxy(port: int, *, secret: bytes) -> MTProxy:
    return MTProxy(hostname="127.0.0.1", port=port, secret=secret, sni_hostname=_SNI_DOMAIN)


async def test_connect_via_mtproxy_greets_a_fake_tls_proxy_with_a_signed_client_hello() -> None:
    secret = bytes.fromhex(PLAIN_SECRET_HEX)
    stub = await _start_fake_tls_stub(secret=secret)
    transport = TCPIntermediatePadded(proxy=_fake_tls_mtproxy(stub.port, secret=secret), dc_id=_DC_ID)

    try:
        await transport.connect(_UNREACHABLE_DC_ADDRESS)
        greeting = await asyncio.wait_for(stub.hello, timeout=TCP.TIMEOUT)
    finally:
        await transport.close()
        stub.server.close()
        await stub.server.wait_closed()

    assert greeting[:3] == _CLIENT_HELLO_PREFIX
    assert _SNI_DOMAIN.encode("ascii") in greeting

    # The proxy authenticates the greeting exactly this way before answering it.
    zeroed = (
        greeting[:_RANDOM_OFFSET] + bytes(_RANDOM_SIZE) + greeting[_RANDOM_OFFSET + _RANDOM_SIZE :]
    )
    digest = bytearray(hmac.new(secret, zeroed, hashlib.sha256).digest())
    stamped = greeting[_RANDOM_OFFSET + _RANDOM_SIZE - _TIMESTAMP_SIZE : _RANDOM_OFFSET + _RANDOM_SIZE]
    stamp = int.from_bytes(bytes(digest[-_TIMESTAMP_SIZE:]), "little") ^ int.from_bytes(stamped, "little")

    assert greeting[_RANDOM_OFFSET : _RANDOM_OFFSET + _RANDOM_SIZE - _TIMESTAMP_SIZE] == bytes(
        digest[:-_TIMESTAMP_SIZE]
    )
    assert abs(stamp - int(time.time())) < _CLOCK_SKEW_ALLOWANCE


async def test_connect_via_mtproxy_wraps_the_handshake_in_application_records() -> None:
    # The change-cipher-spec, then one record holding the obfuscated2 header and
    #  the first framed packet - the header rides with that packet rather than in
    #  a record of its own.
    payload: Final[bytes] = b"\x01\x02\x03\x04"
    secret = bytes.fromhex(PLAIN_SECRET_HEX)

    stub = await _start_fake_tls_stub(secret=secret, expects_packet=True)
    transport = TCPIntermediatePadded(proxy=_fake_tls_mtproxy(stub.port, secret=secret), dc_id=_DC_ID)

    try:
        await transport.connect(_UNREACHABLE_DC_ADDRESS)
        await transport.send(payload)
        stream = await asyncio.wait_for(stub.received, timeout=TCP.TIMEOUT)
    finally:
        await transport.close()
        stub.server.close()
        await stub.server.wait_closed()

    assert stream[: len(CHANGE_CIPHER_SPEC)] == CHANGE_CIPHER_SPEC

    record = stream[len(CHANGE_CIPHER_SPEC) :]

    assert record[: len(APPLICATION_DATA_PREFIX)] == APPLICATION_DATA_PREFIX
    assert int.from_bytes(record[len(APPLICATION_DATA_PREFIX) : RECORD_HEADER_SIZE], "big") == len(
        record
    ) - RECORD_HEADER_SIZE

    framed = record[RECORD_HEADER_SIZE:]
    key = hashlib.sha256(framed[8:40] + secret).digest()
    decrypted = aes.ctr256_decrypt(framed, key, bytearray(framed[40:56]), bytearray(1))

    assert decrypted[56:60] == INTERMEDIATE_PADDED_OBFUSCATE_TAG
    assert int.from_bytes(decrypted[60:62], "little", signed=True) == _DC_ID

    packet = decrypted[_OBFUSCATED2_HEADER_SIZE:]
    framed_length = int.from_bytes(packet[:_LENGTH_PREFIX_SIZE], "little", signed=True)

    assert len(packet) == _LENGTH_PREFIX_SIZE + framed_length
    assert packet[_LENGTH_PREFIX_SIZE : _LENGTH_PREFIX_SIZE + len(payload)] == payload
    assert 0 <= framed_length - len(payload) <= _MAX_INTERMEDIATE_PADDING


async def test_connect_via_mtproxy_reads_a_reply_split_across_several_records() -> None:
    # A record boundary has nothing to do with a packet boundary, so a reply the
    #  proxy cut up must still arrive as the byte stream the transport asked for.
    payload: Final[bytes] = b"\x01\x02\x03\x04"

    # Shorter than 24 bytes and the padded transport reads the frame as a quick
    #  ack or an error code rather than as a packet.
    reply: Final[bytes] = bytes(range(_MIN_INTERMEDIATE_PACKET_SIZE))
    secret = bytes.fromhex(PLAIN_SECRET_HEX)

    stub = await _start_fake_tls_stub(
        secret=secret,
        expects_packet=True,
        reply=len(reply).to_bytes(_LENGTH_PREFIX_SIZE, "little", signed=True) + reply,
        reply_record_size=3,
    )
    transport = TCPIntermediatePadded(proxy=_fake_tls_mtproxy(stub.port, secret=secret), dc_id=_DC_ID)

    try:
        await transport.connect(_UNREACHABLE_DC_ADDRESS)
        await transport.send(payload)
        received = await asyncio.wait_for(transport.recv(), timeout=TCP.TIMEOUT)
    finally:
        await transport.close()
        stub.server.close()
        await stub.server.wait_closed()

    assert received == reply


async def test_connect_via_mtproxy_rejects_a_fake_tls_reply_signed_with_another_secret() -> None:
    # Without this check a censor could answer with any plausible ServerHello and
    #  watch what the client does next.
    stub = await _start_fake_tls_stub(secret=bytes(16))
    transport = TCPIntermediatePadded(
        proxy=_fake_tls_mtproxy(stub.port, secret=bytes.fromhex(PLAIN_SECRET_HEX)),
        dc_id=_DC_ID,
    )

    try:
        with pytest.raises(OSError, match="without knowing the proxy secret"):
            await transport.connect(_UNREACHABLE_DC_ADDRESS)
    finally:
        await transport.close()
        stub.server.close()
        await stub.server.wait_closed()


async def test_connect_via_mtproxy_rejects_a_fake_tls_reply_that_is_not_a_server_hello() -> None:
    # What a plain web server on the configured port answers with.
    async def serve(_reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
        writer.write(b"HTTP/1.1 400 Bad Request\r\n\r\n")
        await writer.drain()

    server = await asyncio.start_server(serve, host="127.0.0.1", port=0)
    transport = TCPIntermediatePadded(
        proxy=_fake_tls_mtproxy(server.sockets[0].getsockname()[1], secret=bytes.fromhex(PLAIN_SECRET_HEX)),
        dc_id=_DC_ID,
    )

    try:
        with pytest.raises(OSError, match="not answered with a ServerHello"):
            await transport.connect(_UNREACHABLE_DC_ADDRESS)
    finally:
        await transport.close()
        server.close()
        await server.wait_closed()


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
