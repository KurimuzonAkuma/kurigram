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

"""Shared WEB proxy test values - hostnames, secrets, normative vectors, and
the live-relay config every WEB proxy test file reads instead of declaring
its own copy."""

import os
from dataclasses import dataclass

# A made-up value. Every test using it only parses or re-encodes it, so nothing
# here needs a secret that belongs to a real deployment.
PLAIN_SECRET_HEX = "0123456789abcdef0123456789abcdef"
DD_SECRET_HEX = "dd" + PLAIN_SECRET_HEX

# Normative capability vectors, web-proxy-plan.md §10 - the same two the Go
# relay's own suite (tproxy-server/internal/relay/bridge_test.go) is checked
# against, so both sides agree with tdesktop's client byte for byte.
BRIDGE_CAPABILITY_VECTORS = (
    ("proxy.example.com", "000102030405060708090a0b0c0d0e0f", "MHLEY5PmW1GWqJkSrlmJpvJUiLhBH_QKy6yKg8a0JPk"),
    ("proxy.example.com", "dd000102030405060708090a0b0c0d0e0f", "IpJrt3e7sKtzPyoXy6w-Zj6GGEvsvclN66JzQEfPYLA"),
)


@dataclass(frozen=True)
class LiveRelayConfig:
    hostname: str = ""
    secret: str = ""
    dc_id: int = 2
    api_id: str = ""
    api_hash: str = ""

    @property
    def is_configured(self) -> bool:
        return bool(self.hostname and self.secret)

    @property
    def has_api_credentials(self) -> bool:
        return bool(self.api_id and self.api_hash)


def load_live_relay_config() -> LiveRelayConfig:
    return LiveRelayConfig(
        hostname=os.environ.get("WEB_PROXY_TEST_HOSTNAME", ""),
        secret=os.environ.get("WEB_PROXY_TEST_SECRET", ""),
        dc_id=int(os.environ.get("WEB_PROXY_TEST_DC_ID", "2")),
        api_id=os.environ.get("WEB_PROXY_TEST_API_ID", ""),
        api_hash=os.environ.get("WEB_PROXY_TEST_API_HASH", ""),
    )
