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


"""End-to-end smoke test for the classic MTProxy scheme against a real,
already-deployed proxy and a real Telegram datacenter.

The proxy comes from the environment as an ordinary
``tg://proxy?server=...&port=...&secret=...`` link, so which secret flavour is
under test is a property of the environment rather than of the code; the
``_MTPROXY_LINK_PARAMETERS`` comment in ``conftest.py`` says why it is one
variable. The layers exercised are the same three the WEB proxy test drives,
for the same reasons; see ``test_web_proxy_live.py`` for what each of them
proves.

Skipped unless the environment carries a proxy to run against. Fill in
.env.test from .env.test.example, then::

    make test-integration
"""

from typing import Final, Type

from pyrogram import Client
from pyrogram.connection.proxy import MTProxy
from pyrogram.connection.transport.tcp import TCP
from pyrogram.session.auth import Auth

from tests.integrations.connection.transport.tcp.conftest import (
    AUTH_KEY_SIZE,
    MTPROTO_PORT,
    round_trip_req_pq_multi,
)

# `Auth` dials the proxy rather than this address, but the signature still
#  requires both halves.
_UNUSED_DC_ADDRESS: Final[str] = "unused"


async def test_req_pq_multi_round_trip_through_live_mtproxy(
    mtproxy_proxy: MTProxy,
    mtproxy_dc_id: int,
    mtproxy_transport_class: Type[TCP],
) -> None:
    transport = mtproxy_transport_class(ipv6=False, proxy=mtproxy_proxy, dc_id=mtproxy_dc_id)

    try:
        await transport.connect((_UNUSED_DC_ADDRESS, MTPROTO_PORT))
        await round_trip_req_pq_multi(transport)
    finally:
        await transport.close()


async def test_full_auth_key_exchange_through_live_mtproxy(
    mtproxy_dc_id: int,
    unauthorized_mtproxy_client: Client,
) -> None:
    auth_key = await Auth(
        unauthorized_mtproxy_client,
        dc_id=mtproxy_dc_id,
        server_address=_UNUSED_DC_ADDRESS,
        port=MTPROTO_PORT,
        test_mode=False,
    ).create()

    assert isinstance(auth_key, bytes)
    assert len(auth_key) == AUTH_KEY_SIZE


async def test_high_level_api_call_through_live_mtproxy(mtproxy_client: Client) -> None:
    me = await mtproxy_client.get_me()

    assert me.is_self
    assert me.id > 0
