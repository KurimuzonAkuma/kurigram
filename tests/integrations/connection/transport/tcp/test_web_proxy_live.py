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

This is deliberately NOT a mock: it drives the full chain - the
obfuscated2 handshake TCP._connect_via_web_proxy performs, the long-poll
carrier, the hosted relay, a real stock MTProxy instance, and a real
Telegram datacenter - two ways:

1. A hand-built plaintext ``req_pq_multi`` query (MTProto's first,
   unencrypted handshake step, which needs no auth key), checking a
   genuine ``resPQ`` comes back with the nonce we sent. Deliberately
   low-level so a reviewer can see exactly which bytes cross the wire
   without needing to trust anything else in this codebase.
2. A full, real Diffie-Hellman key exchange via kurigram's own
   ``pyrogram.session.auth.Auth``, proving a *sustained*, multi-message,
   partially-encrypted exchange works end to end through the same
   transport - not just one request/response.

Both run through TCPAbridged (plain secrets) or TCPIntermediatePadded
(dd-prefixed secrets) unmodified - proxy={"scheme": "web", ...} is all
that changes; see tcp.py's TCP._connect_via_web_proxy.

Skipped by default: it needs a real relay hostname and MTProxy secret,
which nobody but the operator running this test has, so it is entirely
driven by environment variables and never hardcodes any specific
deployment. Run it against your own relay with e.g.::

    WEB_PROXY_TEST_HOSTNAME=relay.example.com \\
    WEB_PROXY_TEST_SECRET=000102030405060708090a0b0c0d0e0f \\
    WEB_PROXY_TEST_DC_ID=2 \\
    pytest tests/integrations/connection/transport/tcp/test_web_proxy_live.py -v -s
"""

import asyncio
import os
import struct
import time
from dataclasses import dataclass

import pytest

from pyrogram import Client
from pyrogram.connection import normalize_proxy
from pyrogram.connection.transport.tcp import TCPAbridged, TCPIntermediatePadded
from pyrogram.session.auth import Auth

from tests.web_proxy_values import load_live_relay_config

_CONFIG = load_live_relay_config()

pytestmark = pytest.mark.skipif(
    not _CONFIG.is_configured,
    reason="set WEB_PROXY_TEST_HOSTNAME and WEB_PROXY_TEST_SECRET to run the live WEB proxy smoke test",
)

# No default anywhere: tdesktop's published example pair is Telegram Desktop's
# real credentials, and using them from a third-party client violates
# Telegram's ToS. Bring your own api_id/api_hash for this test.
_requires_api_credentials = pytest.mark.skipif(
    not _CONFIG.has_api_credentials,
    reason="set WEB_PROXY_TEST_API_ID and WEB_PROXY_TEST_API_HASH to run the auth key exchange test",
)

_REQ_PQ_MULTI = 0xBE7E8EF1
_RES_PQ = 0x05162463


@dataclass(frozen=True)
class _ReqPqMulti:
    packet: bytes
    nonce: bytes


def _build_req_pq_multi() -> _ReqPqMulti:
    """A hand-built, unencrypted req_pq_multi query - MTProto's very
    first handshake step. No auth key exists yet, so this is the
    simplest possible real message to round-trip for a genuine
    correctness check of the whole transport.
    """
    nonce = os.urandom(16)
    body = struct.pack("<I", _REQ_PQ_MULTI) + nonce

    message_id = int(time.time() * 2 ** 32)
    message_id -= message_id % 4  # low bits must be clear for a client message

    packet = struct.pack("<qQi", 0, message_id, len(body)) + body
    return _ReqPqMulti(packet=packet, nonce=nonce)


def _pick_transport_class():
    if len(bytes.fromhex(_CONFIG.secret)) == 17:
        return TCPIntermediatePadded
    return TCPAbridged


async def test_req_pq_multi_round_trip_through_live_relay():
    transport_cls = _pick_transport_class()
    proxy = normalize_proxy({"scheme": "web", "hostname": _CONFIG.hostname, "secret": _CONFIG.secret})

    transport = transport_cls(ipv6=False, proxy=proxy, dc_id=_CONFIG.dc_id)
    try:
        await transport.connect(("unused", 0))

        query = _build_req_pq_multi()
        await transport.send(query.packet)

        response = await asyncio.wait_for(transport.recv(), timeout=15)
        assert response is not None, "no response from the real DC through the WEB proxy carrier"

        auth_key_id, message_id, length = struct.unpack("<qQi", response[:20])
        assert auth_key_id == 0, "expected an unencrypted resPQ, got an encrypted-looking reply"

        body = response[20:20 + length]
        constructor = struct.unpack("<I", body[:4])[0]
        assert constructor == _RES_PQ, f"expected resPQ (0x{_RES_PQ:x}), got 0x{constructor:x}"

        echoed_nonce = body[4:20]
        assert echoed_nonce == query.nonce, "resPQ echoed a different nonce than the one we sent"
    finally:
        await transport.close()


@_requires_api_credentials
async def test_full_auth_key_exchange_through_live_relay():
    transport_cls = _pick_transport_class()

    client = Client(
        "test_client",
        api_id=int(_CONFIG.api_id),
        api_hash=_CONFIG.api_hash,
        in_memory=True,
        protocol_factory=transport_cls,
        proxy={"scheme": "web", "hostname": _CONFIG.hostname, "secret": _CONFIG.secret},
    )

    auth_key = await Auth(
        client, dc_id=_CONFIG.dc_id, server_address="unused", port=443, test_mode=False,
    ).create()

    assert isinstance(auth_key, bytes)
    assert len(auth_key) == 256


async def test_string_link_form_connects_through_live_relay():
    """Covers the tg://webproxy?server=...&secret=... / t.me/webproxy
    string form specifically (normalize_proxy's string-link parsing) - the
    other two tests above only exercise the dict form.
    """
    transport_cls = _pick_transport_class()
    link = f"tg://webproxy?server={_CONFIG.hostname}&secret={_CONFIG.secret}"

    transport = transport_cls(ipv6=False, proxy=normalize_proxy(link), dc_id=_CONFIG.dc_id)
    try:
        await transport.connect(("unused", 0))

        query = _build_req_pq_multi()
        await transport.send(query.packet)

        response = await asyncio.wait_for(transport.recv(), timeout=15)
        assert response is not None

        body = response[20:20 + struct.unpack("<qQi", response[:20])[2]]
        assert struct.unpack("<I", body[:4])[0] == _RES_PQ
        assert body[4:20] == query.nonce
    finally:
        await transport.close()
