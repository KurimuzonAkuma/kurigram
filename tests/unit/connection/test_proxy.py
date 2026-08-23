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
    HttpProxy,
    MtProxy,
    Socks4Proxy,
    Socks5Proxy,
    WebProxy,
    canonicalize_web_hostname,
    normalize_proxy,
)
from pyrogram.enums import ProxyScheme

from tests.web_proxy_values import DD_SECRET_HEX, PLAIN_SECRET_HEX

# --- hostname canonicalization ----------------------------------------

def test_hostname_canonicalization_matches_normative_vector_host():
    # §2.4/§10: different normalizations of the same host derive different
    # capabilities, so a mixed-case hostname must still hit the vector for
    # its lowercase form.
    assert canonicalize_web_hostname("Proxy.Example.com") == "proxy.example.com"


@pytest.mark.parametrize("hostname", ["203.0.113.5", "relay", "", "  "])
def test_invalid_web_hostname_forms_are_rejected(hostname):
    with pytest.raises(ValueError):
        canonicalize_web_hostname(hostname)


# --- normalize_proxy: dict form ----------------------------------------

def test_normalize_proxy_none_passes_through():
    assert normalize_proxy(None) is None


def test_normalize_proxy_is_idempotent_on_a_dataclass():
    web = WebProxy(hostname="relay.example.com", secret=bytes.fromhex(PLAIN_SECRET_HEX))
    assert normalize_proxy(web) is web


def test_normalize_proxy_web_dict_form():
    web = normalize_proxy({"scheme": "web", "hostname": "RELAY.Example.COM", "secret": PLAIN_SECRET_HEX})
    assert isinstance(web, WebProxy)
    assert web.scheme is ProxyScheme.WEB
    assert web.hostname == "relay.example.com"
    assert web.secret == bytes.fromhex(PLAIN_SECRET_HEX)


def test_normalize_proxy_web_dict_form_keeps_dd_marker():
    web = normalize_proxy({"scheme": "web", "hostname": "relay.example.com", "secret": DD_SECRET_HEX})
    assert web.secret == bytes.fromhex(DD_SECRET_HEX)


def test_normalize_proxy_scheme_is_case_insensitive():
    web = normalize_proxy({"scheme": "WEB", "hostname": "relay.example.com", "secret": PLAIN_SECRET_HEX})
    assert isinstance(web, WebProxy)


def test_normalize_proxy_socks5_dict_form():
    p = normalize_proxy({"scheme": "socks5", "hostname": "1.2.3.4", "port": 1080, "username": "u", "password": "p"})
    assert p == Socks5Proxy(hostname="1.2.3.4", port=1080, username="u", password="p")


def test_normalize_proxy_socks4_dict_form_without_credentials():
    p = normalize_proxy({"scheme": "socks4", "hostname": "1.2.3.4", "port": 1080})
    assert p == Socks4Proxy(hostname="1.2.3.4", port=1080)


def test_normalize_proxy_http_dict_form():
    p = normalize_proxy({"scheme": "http", "hostname": "1.2.3.4", "port": 8080})
    assert isinstance(p, HttpProxy)


def test_normalize_proxy_mtproxy_dict_form():
    p = normalize_proxy({"scheme": "mtproxy", "hostname": "1.2.3.4", "port": 443, "secret": PLAIN_SECRET_HEX})
    assert isinstance(p, MtProxy)
    assert p.port == 443
    assert p.secret == bytes.fromhex(PLAIN_SECRET_HEX)


def test_normalize_proxy_unknown_scheme_raises():
    with pytest.raises(ValueError):
        normalize_proxy({"scheme": "quic", "hostname": "1.2.3.4", "port": 443})


def test_normalize_proxy_missing_scheme_raises():
    with pytest.raises(ValueError):
        normalize_proxy({"hostname": "1.2.3.4", "port": 443})


@pytest.mark.parametrize("field", ["hostname", "port"])
def test_normalize_proxy_socks_missing_required_field_raises(field):
    proxy = {"scheme": "socks5", "hostname": "1.2.3.4", "port": 1080}
    del proxy[field]
    with pytest.raises(ValueError):
        normalize_proxy(proxy)


def test_normalize_proxy_web_missing_secret_raises():
    with pytest.raises(ValueError):
        normalize_proxy({"scheme": "web", "hostname": "relay.example.com"})


def test_normalize_proxy_ee_secret_is_rejected_with_explanation():
    with pytest.raises(ValueError, match="TLS-emulation"):
        normalize_proxy({"scheme": "web", "hostname": "relay.example.com", "secret": "ee" + PLAIN_SECRET_HEX})


def test_normalize_proxy_invalid_secret_length_raises():
    with pytest.raises(ValueError):
        normalize_proxy({"scheme": "web", "hostname": "relay.example.com", "secret": "aabbcc"})


def test_normalize_proxy_wrong_type_raises():
    with pytest.raises(TypeError):
        normalize_proxy(12345)


# --- normalize_proxy: string form ---------------------------------------

@pytest.mark.parametrize("link", [
    f"tg://webproxy?server=relay.example.com&secret={PLAIN_SECRET_HEX}",
    f"https://t.me/webproxy?server=relay.example.com&secret={PLAIN_SECRET_HEX}",
    f"tg://webproxy?host=relay.example.com&secret={PLAIN_SECRET_HEX}",  # Android-fork compat alias
])
def test_normalize_proxy_web_string_link_forms(link):
    web = normalize_proxy(link)
    assert isinstance(web, WebProxy)
    assert web.hostname == "relay.example.com"
    assert web.secret == bytes.fromhex(PLAIN_SECRET_HEX)


def test_normalize_proxy_web_string_link_missing_secret_raises():
    with pytest.raises(ValueError):
        normalize_proxy("tg://webproxy?server=relay.example.com")


def test_normalize_proxy_socks_telegram_link_form():
    p = normalize_proxy("tg://socks?server=1.2.3.4&port=1080&user=u&pass=p")
    assert p == Socks5Proxy(hostname="1.2.3.4", port=1080, username="u", password="p")


def test_normalize_proxy_generic_url_form():
    p = normalize_proxy("socks5://user:pass@1.2.3.4:1080")
    assert p == Socks5Proxy(hostname="1.2.3.4", port=1080, username="user", password="pass")


def test_normalize_proxy_generic_url_form_without_port_raises():
    with pytest.raises(ValueError):
        normalize_proxy("socks5://1.2.3.4")
