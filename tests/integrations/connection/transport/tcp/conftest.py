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


"""Live-relay fixtures. Every value is required and comes from the environment
(see .env.test.example); a test that asks for one of these is skipped, by name,
when the environment does not carry it."""

import asyncio
import os
import shutil
import struct
import time
from contextlib import asynccontextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import AsyncIterator, Final, Type

import pytest

from pyrogram import Client
from pyrogram.connection.proxy import MTProxy, Proxy, WebProxy, normalize_proxy
from pyrogram.connection.transport.tcp import TCP, TCPAbridged, TCPIntermediatePadded

# Any secret past the plain 16 bytes - dd-prefixed or ee-prefixed - asks for
#  random padding, which only the padded intermediate transport speaks.
#  https://github.com/tdlib/td/blob/d1085f9cebc5a62379991ae1652673954f229c1f/td/mtproto/ProxySecret.h#L44-L46
_PADDED_SECRET_MIN_LENGTH: Final[int] = 17

# Every integration test shares one session name, so a stray session file left
#  behind by a crashed run is always the same one.
_SESSION_NAME: Final[str] = "test_client"

# Session file suffix `Client` appends to its `name`.
_SESSION_SUFFIX: Final[str] = ".session"


@dataclass(frozen=True)
class RelayConfig:
    hostname: str
    secret: bytes  # decoded, dd marker kept when present
    dc_id: int


def _skip_unless_set(*names: str) -> None:
    missing = [name for name in names if not os.environ.get(name)]

    if missing:
        pytest.skip("set {} in .env.test to run this test".format(", ".join(missing)))


@pytest.fixture(scope="session")
def relay_config() -> RelayConfig:
    _skip_unless_set("WEB_PROXY_TEST_HOSTNAME", "WEB_PROXY_TEST_SECRET", "WEB_PROXY_TEST_DC_ID")

    return RelayConfig(
        hostname=os.environ["WEB_PROXY_TEST_HOSTNAME"],
        secret=bytes.fromhex(os.environ["WEB_PROXY_TEST_SECRET"]),
        dc_id=int(os.environ["WEB_PROXY_TEST_DC_ID"]),
    )


def _transport_class_for(secret: bytes) -> Type[TCP]:
    if len(secret) >= _PADDED_SECRET_MIN_LENGTH:
        return TCPIntermediatePadded

    return TCPAbridged


@pytest.fixture(scope="session")
def relay_transport_class(relay_config: RelayConfig) -> Type[TCP]:
    return _transport_class_for(relay_config.secret)


@pytest.fixture()
def relay_proxy(relay_config: RelayConfig) -> WebProxy:
    return WebProxy(hostname=relay_config.hostname, secret=relay_config.secret)


@pytest.fixture(scope="session")
def mtproxy_proxy() -> MTProxy:
    # One variable rather than three, because a proxy is shared as a link and
    #  the link is what carries the secret flavour - plain, dd or ee.
    _skip_unless_set("MTPROXY_TEST_LINK")

    proxy = normalize_proxy(os.environ["MTPROXY_TEST_LINK"])

    if not isinstance(proxy, MTProxy):
        pytest.skip("MTPROXY_TEST_LINK parses as {}, not an MTProxy".format(type(proxy).__name__))

    return proxy


@pytest.fixture(scope="session")
def mtproxy_dc_id() -> int:
    _skip_unless_set("MTPROXY_TEST_DC_ID")

    return int(os.environ["MTPROXY_TEST_DC_ID"])


@pytest.fixture(scope="session")
def mtproxy_transport_class(mtproxy_proxy: MTProxy) -> Type[TCP]:
    return _transport_class_for(mtproxy_proxy.secret)


@pytest.fixture(scope="session")
def session_path() -> Path:
    _skip_unless_set("SESSION_PATH")

    path = Path(os.environ["SESSION_PATH"]).expanduser()

    if not path.is_file():
        pytest.skip("SESSION_PATH points at {}, which is not a file".format(path))

    return path


@pytest.fixture()
def session_copy(session_path: Path, tmp_path: Path) -> Path:
    # The run works on a copy: `Client` writes update state and peer cache back
    #  into whatever session it opens, and `SESSION_PATH` is not ours to modify.
    copy = tmp_path / (_SESSION_NAME + _SESSION_SUFFIX)
    shutil.copy(session_path, copy)

    return copy


def _unauthorized_client(proxy: Proxy, *, transport_class: Type[TCP]) -> Client:
    # Carries the proxy configuration and nothing else: `Auth.create()` reads
    #  only `ipv6`, `proxy`, the two factories and `loop` off the client, so no
    #  API key and no session are involved.
    return Client(
        _SESSION_NAME,
        in_memory=True,
        proxy=proxy,
        protocol_factory=transport_class,
    )


@asynccontextmanager
async def _started_client(
    session_copy: Path,
    *,
    proxy: Proxy,
    transport_class: Type[TCP],
) -> AsyncIterator[Client]:
    # No api_id/api_hash: both are read only when a new authorization has to be
    #  created, and this session already exists (`pyrogram/client.py:928`).
    client = Client(
        _SESSION_NAME,
        workdir=str(session_copy.parent),
        proxy=proxy,
        protocol_factory=transport_class,
    )

    await client.start()

    try:
        yield client

    finally:
        await client.stop()


@pytest.fixture()
def unauthorized_client(relay_proxy: WebProxy, relay_transport_class: Type[TCP]) -> Client:
    return _unauthorized_client(relay_proxy, transport_class=relay_transport_class)


@pytest.fixture()
async def client(
    session_copy: Path,
    relay_proxy: WebProxy,
    relay_transport_class: Type[TCP],
) -> AsyncIterator[Client]:
    async with _started_client(
        session_copy,
        proxy=relay_proxy,
        transport_class=relay_transport_class,
    ) as client:
        yield client


@pytest.fixture()
def unauthorized_mtproxy_client(mtproxy_proxy: MTProxy, mtproxy_transport_class: Type[TCP]) -> Client:
    return _unauthorized_client(mtproxy_proxy, transport_class=mtproxy_transport_class)


@pytest.fixture()
async def mtproxy_client(
    session_copy: Path,
    mtproxy_proxy: MTProxy,
    mtproxy_transport_class: Type[TCP],
) -> AsyncIterator[Client]:
    async with _started_client(
        session_copy,
        proxy=mtproxy_proxy,
        transport_class=mtproxy_transport_class,
    ) as client:
        yield client


_REQ_PQ_MULTI: Final[int] = 0xBE7E8EF1
_RES_PQ: Final[int] = 0x05162463
_RESPONSE_HEADER: Final[struct.Struct] = struct.Struct("<qQi")

# How long a real DC gets to answer the first handshake step.
_RES_PQ_TIMEOUT: Final[float] = 15.0


@dataclass(frozen=True)
class _ReqPqMulti:
    packet: bytes
    nonce: bytes


def _build_req_pq_multi() -> _ReqPqMulti:
    """A hand-built, unencrypted req_pq_multi query - MTProto's very first
    handshake step. No auth key exists yet, so this is the simplest possible
    real message to round-trip for a genuine correctness check of the whole
    transport.
    """
    nonce = os.urandom(16)
    body = struct.pack("<I", _REQ_PQ_MULTI) + nonce

    message_id = int(time.time() * 2 ** 32)
    message_id -= message_id % 4  # low bits must be clear for a client message

    packet = _RESPONSE_HEADER.pack(0, message_id, len(body)) + body

    return _ReqPqMulti(packet=packet, nonce=nonce)


async def round_trip_req_pq_multi(transport: TCP) -> None:
    """Send req_pq_multi over an already-connected transport and check the resPQ."""
    query = _build_req_pq_multi()
    await transport.send(query.packet)

    response = await asyncio.wait_for(transport.recv(), timeout=_RES_PQ_TIMEOUT)
    assert response is not None, "no response from the real DC through the proxy"

    auth_key_id, _message_id, length = _RESPONSE_HEADER.unpack(response[:_RESPONSE_HEADER.size])
    assert auth_key_id == 0, "expected an unencrypted resPQ, got an encrypted-looking reply"

    body = response[_RESPONSE_HEADER.size:_RESPONSE_HEADER.size + length]
    constructor = struct.unpack("<I", body[:4])[0]
    assert constructor == _RES_PQ, "expected resPQ (0x{:x}), got 0x{:x}".format(_RES_PQ, constructor)

    assert body[4:20] == query.nonce, "resPQ echoed a different nonce than the one we sent"
