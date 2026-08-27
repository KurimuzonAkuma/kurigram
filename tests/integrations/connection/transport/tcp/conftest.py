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
from typing import AsyncIterator, Final, List, NamedTuple, Optional, Type

import pytest

from pyrogram import Client
from pyrogram.connection.connection import transport_class_for
from pyrogram.connection.proxy import MTProxy, Proxy, WebProxy, normalize_proxy
from pyrogram.connection.transport.tcp import TCP

# Every integration test shares one session name, so a stray session file left
#  behind by a crashed run is always the same one.
_SESSION_NAME: Final[str] = "test_client"

# The port a DC speaks MTProto on. Neither live test dials it - the proxy is
#  what gets dialed - but `Auth` still has to be handed an address.
MTPROTO_PORT: Final[int] = 443

# An MTProto auth key is 2048 bits.
AUTH_KEY_SIZE: Final[int] = 256


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


@pytest.fixture()
def relay_proxy(relay_config: RelayConfig) -> WebProxy:
    return WebProxy(hostname=relay_config.hostname, secret=relay_config.secret)


@pytest.fixture()
def relay_transport_class(relay_proxy: WebProxy) -> Type[TCP]:
    # Only the tests that drive a transport directly need this; the ones that go
    #  through `Client` let `Connection` pick the same class from the same proxy.
    return transport_class_for(relay_proxy)


class _LinkParams(NamedTuple):
    links: List[Optional[str]]
    ids: List[str]


def _mtproxy_link_parameters() -> _LinkParams:
    """One parameter per configured link, or one that skips when none is.

    Read at import time because `params` has to exist before collection. The
    skipping parameter is what carries the reason: an empty list skips as well,
    but with pytest's own "got empty parameter set", which names no variable to
    go and set.
    """
    links = os.environ.get("MTPROXY_TEST_LINKS", "").split()

    if not links:
        return _LinkParams(links=[None], ids=["unset"])

    parameters = _LinkParams(links=[], ids=[])

    for link in links:
        proxy = normalize_proxy(link)
        parameters.links.append(link)
        # The link carries the secret, so the id names the address alone.
        parameters.ids.append("{}:{}".format(proxy.hostname, proxy.port))

    return parameters


# One variable rather than three per proxy, because a proxy is shared as a link
#  and the link is what carries the secret flavour - plain, dd or ee. Every test
#  below runs once per link, so one command covers every flavour configured.
_MTPROXY_LINK_PARAMETERS: Final[_LinkParams] = _mtproxy_link_parameters()


@pytest.fixture(scope="session", params=_MTPROXY_LINK_PARAMETERS.links, ids=_MTPROXY_LINK_PARAMETERS.ids)
def mtproxy_proxy(request: pytest.FixtureRequest) -> MTProxy:
    link = request.param

    if link is None:
        pytest.skip("set MTPROXY_TEST_LINKS in .env.test to run this test")

    proxy = normalize_proxy(link)

    if not isinstance(proxy, MTProxy):
        pytest.skip("MTPROXY_TEST_LINKS carries a {}, not an MTProxy".format(type(proxy).__name__))

    return proxy


@pytest.fixture(scope="session")
def mtproxy_dc_id() -> int:
    _skip_unless_set("MTPROXY_TEST_DC_ID")

    return int(os.environ["MTPROXY_TEST_DC_ID"])


@pytest.fixture(scope="session")
def mtproxy_transport_class(mtproxy_proxy: MTProxy) -> Type[TCP]:
    return transport_class_for(mtproxy_proxy)


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
    copy = tmp_path / (_SESSION_NAME + ".session")
    shutil.copy(session_path, copy)

    return copy


def _unauthorized_client(proxy: Proxy) -> Client:
    # Carries the proxy configuration and nothing else: `Auth.create()` reads
    #  only `ipv6`, `proxy`, the two factories and `loop` off the client, so no
    #  API key and no session are involved. No `protocol_factory` either - the
    #  proxy secret picks the transport.
    return Client(
        _SESSION_NAME,
        in_memory=True,
        proxy=proxy,
    )


@asynccontextmanager
async def _started_client(session_copy: Path, *, proxy: Proxy) -> AsyncIterator[Client]:
    # No api_id/api_hash: `Client.load_session` reads them only when the stored
    #  session is empty and a new authorization has to be created, and this one
    #  is not.
    client = Client(
        _SESSION_NAME,
        workdir=str(session_copy.parent),
        proxy=proxy,
    )

    await client.start()

    try:
        yield client

    finally:
        await client.stop()


@pytest.fixture()
def unauthorized_client(relay_proxy: WebProxy) -> Client:
    return _unauthorized_client(relay_proxy)


@pytest.fixture()
async def client(session_copy: Path, relay_proxy: WebProxy) -> AsyncIterator[Client]:
    async with _started_client(session_copy, proxy=relay_proxy) as client:
        yield client


@pytest.fixture()
def unauthorized_mtproxy_client(mtproxy_proxy: MTProxy) -> Client:
    return _unauthorized_client(mtproxy_proxy)


@pytest.fixture()
async def mtproxy_client(session_copy: Path, mtproxy_proxy: MTProxy) -> AsyncIterator[Client]:
    async with _started_client(session_copy, proxy=mtproxy_proxy) as client:
        yield client


_RES_PQ: Final[int] = 0x05162463
_RESPONSE_HEADER: Final[struct.Struct] = struct.Struct("<qQi")


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
    body = struct.pack("<I", 0xBE7E8EF1) + nonce  # req_pq_multi

    message_id = int(time.time() * 2 ** 32)
    message_id -= message_id % 4  # low bits must be clear for a client message

    packet = _RESPONSE_HEADER.pack(0, message_id, len(body)) + body

    return _ReqPqMulti(packet=packet, nonce=nonce)


async def round_trip_req_pq_multi(transport: TCP) -> None:
    """Send req_pq_multi over an already-connected transport and check the resPQ."""
    query = _build_req_pq_multi()
    await transport.send(query.packet)

    # How long a real DC gets to answer the first handshake step.
    response = await asyncio.wait_for(transport.recv(), timeout=15.0)
    assert response is not None, "no response from the real DC through the proxy"

    auth_key_id, _message_id, length = _RESPONSE_HEADER.unpack(response[:_RESPONSE_HEADER.size])
    assert auth_key_id == 0, "expected an unencrypted resPQ, got an encrypted-looking reply"

    body = response[_RESPONSE_HEADER.size:_RESPONSE_HEADER.size + length]
    constructor = struct.unpack("<I", body[:4])[0]
    assert constructor == _RES_PQ, "expected resPQ (0x{:x}), got 0x{:x}".format(_RES_PQ, constructor)

    assert body[4:20] == query.nonce, "resPQ echoed a different nonce than the one we sent"
