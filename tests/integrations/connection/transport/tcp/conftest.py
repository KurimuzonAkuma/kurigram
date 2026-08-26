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
from dataclasses import dataclass
from typing import Final, Type

import pytest

from pyrogram.connection.proxy import Proxy, normalize_proxy
from pyrogram.connection.transport.tcp import TCP, TCPAbridged, TCPIntermediatePadded

_DD_SECRET_LENGTH: Final[int] = 17


@dataclass(frozen=True)
class SessionConfig:
    api_id: int
    api_hash: str


@dataclass(frozen=True)
class RelayConfig:
    hostname: str
    secret: str
    dc_id: int


def _skip_unless_set(*names: str) -> None:
    missing = [name for name in names if not os.environ.get(name)]

    if missing:
        pytest.skip("set {} in .env.test to run this test".format(", ".join(missing)))


@pytest.fixture(scope="session")
def session_config() -> SessionConfig:
    _skip_unless_set("SESSION_API_ID", "SESSION_API_HASH")

    return SessionConfig(
        api_id=int(os.environ["SESSION_API_ID"]),
        api_hash=os.environ["SESSION_API_HASH"],
    )


@pytest.fixture(scope="session")
def relay_config() -> RelayConfig:
    _skip_unless_set("WEB_PROXY_TEST_HOSTNAME", "WEB_PROXY_TEST_SECRET", "WEB_PROXY_TEST_DC_ID")

    return RelayConfig(
        hostname=os.environ["WEB_PROXY_TEST_HOSTNAME"],
        secret=os.environ["WEB_PROXY_TEST_SECRET"],
        dc_id=int(os.environ["WEB_PROXY_TEST_DC_ID"]),
    )


@pytest.fixture(scope="session")
def relay_transport_class(relay_config: RelayConfig) -> Type[TCP]:
    # Telegram's protocol ties the framing to the secret: a dd-prefixed secret
    #  means random padding, which only the padded intermediate transport speaks.
    if len(bytes.fromhex(relay_config.secret)) == _DD_SECRET_LENGTH:
        return TCPIntermediatePadded

    return TCPAbridged


@pytest.fixture()
def relay_proxy(relay_config: RelayConfig) -> Proxy:
    return normalize_proxy(
        {
            "scheme": "web",
            "hostname": relay_config.hostname,
            "secret": relay_config.secret,
        }
    )
