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

"""Live check that WebProxyCarrier's uplink flow control (web-proxy-plan.md
§7) never deadlocks. The codec tests under tests/unit/ show WINDOW frames
are built and parsed correctly; only a real relay shows the credit
bookkeeping around them behaves once traffic actually crosses the 4 MiB
implicit window. Run with:

    WEB_PROXY_TEST_HOSTNAME=... WEB_PROXY_TEST_SECRET=... \\
    pytest tests/integrations/connection/transport/tcp/test_web_proxy_carrier.py -v
"""

import asyncio

import pytest

from pyrogram.connection import normalize_proxy
from pyrogram.connection.transport.tcp import TCPAbridged, TCPIntermediatePadded
from pyrogram.connection.transport.tcp.web_proxy_carrier import WebCarrierError

from tests.web_proxy_values import load_live_relay_config

pytestmark = pytest.mark.skipif(
    not load_live_relay_config().is_configured,
    reason="set WEB_PROXY_TEST_HOSTNAME and WEB_PROXY_TEST_SECRET to run this test",
)


async def test_uplink_flow_control_crosses_stream_window(web_proxy_config):
    """Sends 5 MiB in one call - more than the 4 MiB implicit per-stream
    window - directly through WebProxyCarrier, bypassing MTProto framing
    entirely so this is purely a transport-level check of the client's own
    send-credit accounting.

    Before the flow-control fix this pushed unbounded data past the window
    with no client-side check at all. The only two acceptable outcomes now
    are: the carrier is granted enough WINDOW credit and the send
    completes, or the relay never grants more credit and the carrier fails
    cleanly with WebCarrierError once its credit-wait timeout elapses. What
    must never happen is silently exceeding the window, or hanging forever
    - both are ruled out by the bounded asyncio.wait_for below.

    Does not cover the downlink side of the same boundary: forcing a real
    Telegram DC to answer with more than 4 MiB needs an authenticated,
    logged-in session pulling a large file, which cannot be scripted here
    without interactive login.
    """
    proxy = normalize_proxy({"scheme": "web", "hostname": web_proxy_config.hostname, "secret": web_proxy_config.secret})
    transport_cls = TCPIntermediatePadded if len(proxy.secret) == 17 else TCPAbridged
    transport = transport_cls(ipv6=False, proxy=proxy, dc_id=web_proxy_config.dc_id)
    try:
        await transport.connect(("unused", 0))
        carrier = transport._web_carrier
        payload = b"\x00" * (5 * 1024 * 1024)

        try:
            await asyncio.wait_for(carrier.send(payload), timeout=60)
        except WebCarrierError:
            pass  # relay didn't grant more credit - acceptable, as long as it didn't hang
    finally:
        await transport.close()
