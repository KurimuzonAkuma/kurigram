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

import os
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import AsyncIterator, Final, Type

import pytest

from pyrogram import Client
from pyrogram.connection.proxy import WebProxy
from pyrogram.connection.transport.tcp import TCP, TCPAbridged, TCPIntermediatePadded

# A dd-prefixed secret is one marker byte plus the 16-byte secret proper.
_DD_SECRET_LENGTH: Final[int] = 17

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


@pytest.fixture(scope="session")
def relay_transport_class(relay_config: RelayConfig) -> Type[TCP]:
    # Telegram's protocol ties the framing to the secret: a dd-prefixed secret
    #  means random padding, which only the padded intermediate transport speaks.
    if len(relay_config.secret) == _DD_SECRET_LENGTH:
        return TCPIntermediatePadded

    return TCPAbridged


@pytest.fixture()
def relay_proxy(relay_config: RelayConfig) -> WebProxy:
    return WebProxy(hostname=relay_config.hostname, secret=relay_config.secret)


@pytest.fixture(scope="session")
def session_path() -> Path:
    _skip_unless_set("SESSION_PATH")

    path = Path(os.environ["SESSION_PATH"]).expanduser()

    if not path.is_file():
        pytest.skip("SESSION_PATH points at {}, which is not a file".format(path))

    return path


@pytest.fixture()
def unauthorized_client(relay_proxy: WebProxy, relay_transport_class: Type[TCP]) -> Client:
    # Carries the proxy configuration and nothing else: `Auth.create()` reads
    #  only `ipv6`, `proxy`, the two factories and `loop` off the client, so no
    #  API key and no session are involved.
    return Client(
        _SESSION_NAME,
        in_memory=True,
        proxy=relay_proxy,
        protocol_factory=relay_transport_class,
    )


@pytest.fixture()
def session_copy(session_path: Path, tmp_path: Path) -> Path:
    # The run works on a copy: `Client` writes update state and peer cache back
    #  into whatever session it opens, and `SESSION_PATH` is not ours to modify.
    copy = tmp_path / (_SESSION_NAME + _SESSION_SUFFIX)
    shutil.copy(session_path, copy)

    return copy


@pytest.fixture()
async def client(
    session_copy: Path,
    relay_proxy: WebProxy,
    relay_transport_class: Type[TCP],
) -> AsyncIterator[Client]:
    # No api_id/api_hash: both are read only when a new authorization has to be
    #  created, and this session already exists (`pyrogram/client.py:928`).
    client = Client(
        _SESSION_NAME,
        workdir=str(session_copy.parent),
        proxy=relay_proxy,
        protocol_factory=relay_transport_class,
    )

    await client.start()

    try:
        yield client

    finally:
        await client.stop()
