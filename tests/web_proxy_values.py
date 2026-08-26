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

"""Test values shared by more than one WEB proxy test module, so no module
declares its own copy."""

from typing import Final, Tuple

# A made-up value. Every test using it only parses or re-encodes it, so nothing
#  here needs a secret that belongs to a real deployment.
PLAIN_SECRET_HEX: Final[str] = "0123456789abcdef0123456789abcdef"
DD_SECRET_HEX: Final[str] = "dd" + PLAIN_SECRET_HEX

# Normative capability vectors, web-proxy-plan.md §10 - the same two the Go
#  relay's own suite (tproxy-server/internal/relay/bridge_test.go) is checked
#  against, so both sides agree with tdesktop's client byte for byte.
BRIDGE_CAPABILITY_VECTORS: Final[Tuple[Tuple[str, str, str], ...]] = (
    ("proxy.example.com", "000102030405060708090a0b0c0d0e0f", "MHLEY5PmW1GWqJkSrlmJpvJUiLhBH_QKy6yKg8a0JPk"),
    ("proxy.example.com", "dd000102030405060708090a0b0c0d0e0f", "IpJrt3e7sKtzPyoXy6w-Zj6GGEvsvclN66JzQEfPYLA"),
)

