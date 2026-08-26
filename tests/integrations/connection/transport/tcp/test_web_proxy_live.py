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


"""End-to-end smoke test for the WEB proxy scheme against a real,
already-deployed relay + stock MTProxy + real Telegram DC.

This is deliberately NOT a mock: it drives the full chain - the obfuscated2
handshake TCP._connect_via_web_proxy performs, the long-poll carrier, the
hosted relay, a real stock MTProxy instance, and a real Telegram datacenter -
two ways:

1. A hand-built plaintext ``req_pq_multi`` query (MTProto's first,
   unencrypted handshake step, which needs no auth key), checking a genuine
   ``resPQ`` comes back with the nonce we sent. Deliberately low-level so a
   reviewer can see exactly which bytes cross the wire without needing to
   trust anything else in this codebase.
2. A full, real Diffie-Hellman key exchange via kurigram's own
   ``pyrogram.session.auth.Auth``, proving a *sustained*, multi-message,
   partially-encrypted exchange works end to end through the same transport -
   not just one request/response.

Both run through TCPAbridged (plain secrets) or TCPIntermediatePadded
(dd-prefixed secrets) unmodified - proxy={"scheme": "web", ...} is all that
changes; see tcp.py's TCP._connect_via_web_proxy.

Skipped unless the environment carries a relay to run against, which nobody
but its operator has. Fill in .env.test from .env.test.example, then::

    make test-integration
"""

import asyncio
import os
import struct
import time
from dataclasses import dataclass
from typing import Final, Type

from pyrogram import Client
from pyrogram.connection.proxy import Proxy, normalize_proxy
from pyrogram.connection.transport.tcp import TCP
from pyrogram.session.auth import Auth

from tests.integrations.connection.transport.tcp.conftest import RelayConfig, SessionConfig

_REQ_PQ_MULTI: Final[int] = 0xBE7E8EF1
_RES_PQ: Final[int] = 0x05162463
_RESPONSE_HEADER = struct.Struct("<qQi")


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


async def _round_trip_req_pq_multi(transport: TCP) -> None:
    query = _build_req_pq_multi()
    await transport.send(query.packet)

    response = await asyncio.wait_for(transport.recv(), timeout=15)
    assert response is not None, "no response from the real DC through the WEB proxy carrier"

    auth_key_id, _message_id, length = _RESPONSE_HEADER.unpack(response[:_RESPONSE_HEADER.size])
    assert auth_key_id == 0, "expected an unencrypted resPQ, got an encrypted-looking reply"

    body = response[_RESPONSE_HEADER.size:_RESPONSE_HEADER.size + length]
    constructor = struct.unpack("<I", body[:4])[0]
    assert constructor == _RES_PQ, f"expected resPQ (0x{_RES_PQ:x}), got 0x{constructor:x}"

    assert body[4:20] == query.nonce, "resPQ echoed a different nonce than the one we sent"


async def test_req_pq_multi_round_trip_through_live_relay(
    relay_config: RelayConfig,
    relay_proxy: Proxy,
    relay_transport_class: Type[TCP],
) -> None:
    transport = relay_transport_class(ipv6=False, proxy=relay_proxy, dc_id=relay_config.dc_id)

    try:
        await transport.connect(("unused", 0))
        await _round_trip_req_pq_multi(transport)
    finally:
        await transport.close()


async def test_string_link_form_connects_through_live_relay(
    relay_config: RelayConfig,
    relay_transport_class: Type[TCP],
) -> None:
    """Covers the tg://webproxy?server=...&secret=... / t.me/webproxy string
    form specifically (normalize_proxy's link parsing) - the other tests here
    only exercise the dict form.
    """
    link = f"tg://webproxy?server={relay_config.hostname}&secret={relay_config.secret}"
    transport = relay_transport_class(
        ipv6=False,
        proxy=normalize_proxy(link),
        dc_id=relay_config.dc_id,
    )

    try:
        await transport.connect(("unused", 0))
        await _round_trip_req_pq_multi(transport)
    finally:
        await transport.close()


async def test_full_auth_key_exchange_through_live_relay(
    relay_config: RelayConfig,
    relay_transport_class: Type[TCP],
    session_config: SessionConfig,
) -> None:
    client = Client(
        "test_client",
        api_id=session_config.api_id,
        api_hash=session_config.api_hash,
        in_memory=True,
        protocol_factory=relay_transport_class,
        proxy={"scheme": "web", "hostname": relay_config.hostname, "secret": relay_config.secret},
    )

    auth_key = await Auth(
        client,
        dc_id=relay_config.dc_id,
        server_address="unused",
        port=443,
        test_mode=False,
    ).create()

    assert isinstance(auth_key, bytes)
    assert len(auth_key) == 256
