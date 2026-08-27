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

import pytest

from pyrogram.connection.proxy import (
    HTTPProxy,
    MTProxy,
    SOCKS4Proxy,
    SOCKS5Proxy,
    WebProxy,
    canonicalize_web_hostname,
    normalize_proxy,
)
from pyrogram.enums import ProxyScheme

from tests.web_proxy_values import DD_SECRET_HEX, PLAIN_SECRET_HEX


def test_hostname_canonicalization_matches_normative_vector_host() -> None:
    # §2.4/§10: different normalizations of the same host derive different
    #  capabilities, so a mixed-case hostname must still hit the vector for its
    #  lowercase form.
    assert canonicalize_web_hostname("Proxy.Example.com") == "proxy.example.com"


@pytest.mark.parametrize("hostname", ["203.0.113.5", "relay", "", "  "])
def test_invalid_web_hostname_forms_are_rejected(hostname: str) -> None:
    with pytest.raises(ValueError):
        canonicalize_web_hostname(hostname)


def test_normalize_proxy_none_passes_through() -> None:
    assert normalize_proxy(None) is None


def test_normalize_proxy_is_idempotent_on_a_dataclass() -> None:
    web_proxy = WebProxy(hostname="relay.example.com", secret=bytes.fromhex(PLAIN_SECRET_HEX))

    assert normalize_proxy(web_proxy) is web_proxy


def test_normalize_proxy_web_dict_form() -> None:
    web_proxy = normalize_proxy({"scheme": "web", "hostname": "RELAY.Example.COM", "secret": PLAIN_SECRET_HEX})

    assert isinstance(web_proxy, WebProxy)
    assert web_proxy.scheme is ProxyScheme.WEB
    assert web_proxy.hostname == "relay.example.com"
    assert web_proxy.secret == bytes.fromhex(PLAIN_SECRET_HEX)


def test_normalize_proxy_web_dict_form_keeps_dd_marker() -> None:
    web_proxy = normalize_proxy({"scheme": "web", "hostname": "relay.example.com", "secret": DD_SECRET_HEX})

    assert web_proxy.secret == bytes.fromhex(DD_SECRET_HEX)


def test_normalize_proxy_scheme_is_case_insensitive() -> None:
    web_proxy = normalize_proxy({"scheme": "WEB", "hostname": "relay.example.com", "secret": PLAIN_SECRET_HEX})

    assert isinstance(web_proxy, WebProxy)


def test_normalize_proxy_socks5_dict_form() -> None:
    proxy = normalize_proxy(
        {"scheme": "socks5", "hostname": "1.2.3.4", "port": 1080, "username": "user", "password": "pass"}
    )

    assert proxy == SOCKS5Proxy(hostname="1.2.3.4", port=1080, username="user", password="pass")


def test_normalize_proxy_socks4_dict_form_without_credentials() -> None:
    proxy = normalize_proxy({"scheme": "socks4", "hostname": "1.2.3.4", "port": 1080})

    assert proxy == SOCKS4Proxy(hostname="1.2.3.4", port=1080)


def test_normalize_proxy_http_dict_form() -> None:
    proxy = normalize_proxy({"scheme": "http", "hostname": "1.2.3.4", "port": 8080})

    assert isinstance(proxy, HTTPProxy)


def test_normalize_proxy_mtproxy_dict_form() -> None:
    proxy = normalize_proxy({"scheme": "mtproxy", "hostname": "1.2.3.4", "port": 443, "secret": PLAIN_SECRET_HEX})

    assert isinstance(proxy, MTProxy)
    assert proxy.port == 443
    assert proxy.secret == bytes.fromhex(PLAIN_SECRET_HEX)


def test_normalize_proxy_unknown_scheme_raises() -> None:
    with pytest.raises(ValueError):
        normalize_proxy({"scheme": "quic", "hostname": "1.2.3.4", "port": 443})


def test_normalize_proxy_missing_scheme_raises() -> None:
    with pytest.raises(ValueError):
        normalize_proxy({"hostname": "1.2.3.4", "port": 443})


@pytest.mark.parametrize("field_name", ["hostname", "port"])
def test_normalize_proxy_socks_missing_required_field_raises(field_name: str) -> None:
    proxy = {"scheme": "socks5", "hostname": "1.2.3.4", "port": 1080}
    del proxy[field_name]

    with pytest.raises(ValueError):
        normalize_proxy(proxy)


def test_normalize_proxy_web_missing_secret_raises() -> None:
    with pytest.raises(ValueError):
        normalize_proxy({"scheme": "web", "hostname": "relay.example.com"})


def test_normalize_proxy_web_ee_secret_names_the_relay() -> None:
    with pytest.raises(ValueError, match="the relay would need to add"):
        normalize_proxy({"scheme": "web", "hostname": "relay.example.com", "secret": "ee" + PLAIN_SECRET_HEX})


def test_normalize_proxy_mtproxy_ee_secret_does_not_name_the_relay() -> None:
    # A classic MTProxy user configures no relay, so the WEB explanation would send
    #  them looking for something they never set up.
    with pytest.raises(ValueError, match="TLS record layer") as raised:
        normalize_proxy(
            {"scheme": "mtproxy", "hostname": "1.2.3.4", "port": 443, "secret": "ee" + PLAIN_SECRET_HEX}
        )

    assert "relay" not in str(raised.value)


def test_normalize_proxy_invalid_secret_length_raises() -> None:
    with pytest.raises(ValueError):
        normalize_proxy({"scheme": "web", "hostname": "relay.example.com", "secret": "aabbcc"})


def test_normalize_proxy_wrong_type_raises() -> None:
    with pytest.raises(TypeError):
        normalize_proxy(12345)


@pytest.mark.parametrize(
    "link",
    [
        f"tg://webproxy?server=relay.example.com&secret={PLAIN_SECRET_HEX}",
        f"https://t.me/webproxy?server=relay.example.com&secret={PLAIN_SECRET_HEX}",
        # `host=` is the alias the Android fork's links use.
        f"tg://webproxy?host=relay.example.com&secret={PLAIN_SECRET_HEX}",
    ],
)
def test_normalize_proxy_web_string_link_forms(link: str) -> None:
    web_proxy = normalize_proxy(link)

    assert isinstance(web_proxy, WebProxy)
    assert web_proxy.hostname == "relay.example.com"
    assert web_proxy.secret == bytes.fromhex(PLAIN_SECRET_HEX)


def test_normalize_proxy_web_string_link_missing_secret_raises() -> None:
    with pytest.raises(ValueError):
        normalize_proxy("tg://webproxy?server=relay.example.com")


def test_normalize_proxy_socks_telegram_link_form() -> None:
    proxy = normalize_proxy("tg://socks?server=1.2.3.4&port=1080&user=user&pass=pass")

    assert proxy == SOCKS5Proxy(hostname="1.2.3.4", port=1080, username="user", password="pass")


def test_normalize_proxy_generic_url_form() -> None:
    proxy = normalize_proxy("socks5://user:pass@1.2.3.4:1080")

    assert proxy == SOCKS5Proxy(hostname="1.2.3.4", port=1080, username="user", password="pass")


def test_normalize_proxy_generic_url_form_without_port_raises() -> None:
    with pytest.raises(ValueError):
        normalize_proxy("socks5://1.2.3.4")
