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
three ways:

1. A hand-built plaintext ``req_pq_multi`` query (MTProto's first,
   unencrypted handshake step, which needs no auth key), checking a genuine
   ``resPQ`` comes back with the nonce we sent. Deliberately low-level so a
   reviewer can see exactly which bytes cross the wire without needing to
   trust anything else in this codebase.
2. A full, real Diffie-Hellman key exchange via kurigram's own
   ``pyrogram.session.auth.Auth``, proving a *sustained*, multi-message,
   partially-encrypted exchange works end to end through the same transport -
   not just one request/response.
3. An ordinary high-level API call on an existing, already-authorized session,
   which is the only one of the three that exercises a fully encrypted MTProto
   session with its own salt, acknowledgements and update loop on top.

All three run the stock transports unmodified - proxy={"scheme": "web", ...} is
all that changes, and the secret picks the framing; see tcp.py's
TCP._connect_via_web_proxy.

Skipped unless the environment carries a relay to run against, which nobody
but its operator has. Fill in .env.test from .env.test.example, then::

    make test-integration
"""

from typing import Type

from pyrogram import Client
from pyrogram.connection.proxy import WebProxy, normalize_proxy
from pyrogram.connection.transport.tcp import TCP
from pyrogram.session.auth import Auth

from tests.integrations.connection.transport.tcp.conftest import (
    AUTH_KEY_SIZE,
    MTPROTO_PORT,
    RelayConfig,
    round_trip_req_pq_multi,
)


async def test_req_pq_multi_round_trip_through_live_relay(
    relay_config: RelayConfig,
    relay_proxy: WebProxy,
    relay_transport_class: Type[TCP],
) -> None:
    transport = relay_transport_class(ipv6=False, proxy=relay_proxy, dc_id=relay_config.dc_id)

    try:
        await transport.connect(("unused", 0))
        await round_trip_req_pq_multi(transport)
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
    link = f"tg://webproxy?server={relay_config.hostname}&secret={relay_config.secret.hex()}"
    transport = relay_transport_class(
        ipv6=False,
        proxy=normalize_proxy(link),
        dc_id=relay_config.dc_id,
    )

    try:
        await transport.connect(("unused", 0))
        await round_trip_req_pq_multi(transport)
    finally:
        await transport.close()


async def test_full_auth_key_exchange_through_live_relay(
    relay_config: RelayConfig,
    unauthorized_client: Client,
) -> None:
    auth_key = await Auth(
        unauthorized_client,
        dc_id=relay_config.dc_id,
        server_address="unused",
        port=MTPROTO_PORT,
        test_mode=False,
    ).create()

    assert isinstance(auth_key, bytes)
    assert len(auth_key) == AUTH_KEY_SIZE


async def test_high_level_api_call_through_live_relay(client: Client) -> None:
    """The only test here that runs a fully encrypted MTProto session - salt,
    acknowledgements, update loop and all - over the carrier, on a real
    already-authorized account.
    """
    me = await client.get_me()

    assert me.is_self
    assert me.id > 0
