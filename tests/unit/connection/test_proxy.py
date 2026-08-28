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

import base64
from typing import Final, Optional

import pytest

from pyrogram.connection.proxy import (
    HTTPS_PORT,
    HTTPProxy,
    MTProxy,
    Proxy,
    ProxyAddress,
    SOCKS4Proxy,
    SOCKS5Proxy,
    WebProxy,
    canonicalize_web_hostname,
    client_proxy_address,
    normalize_proxy,
)
from pyrogram.enums import ProxyScheme

from tests.unit.proxy_values import DD_SECRET_HEX, PLAIN_SECRET_HEX, SNI_DOMAIN

# TDLib's `MAX_DOMAIN_LENGTH`, written out rather than imported: what the two
#  tests below pin is the number TDLib publishes, and importing ours would only
#  make them agree with whatever it happens to say.
#  https://github.com/tdlib/td/blob/d1085f9cebc5a62379991ae1652673954f229c1f/td/mtproto/ProxySecret.h#L18
_MAX_SNI_DOMAIN_SIZE: Final[int] = 182


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
        normalize_proxy(
            {
                "scheme": "web",
                "hostname": "relay.example.com",
                "secret": "ee" + PLAIN_SECRET_HEX + SNI_DOMAIN.encode("ascii").hex(),
            }
        )


def test_normalize_proxy_mtproxy_ee_secret_splits_key_from_sni_domain() -> None:
    proxy = normalize_proxy(
        {
            "scheme": "mtproxy",
            "hostname": "1.2.3.4",
            "port": 443,
            "secret": "ee" + PLAIN_SECRET_HEX + SNI_DOMAIN.encode("ascii").hex(),
        }
    )

    assert proxy == MTProxy(
        hostname="1.2.3.4",
        port=443,
        secret=bytes.fromhex(PLAIN_SECRET_HEX),
        sni_hostname=SNI_DOMAIN,
    )


def test_normalize_proxy_mtproxy_ee_secret_takes_a_domain_of_the_maximum_length() -> None:
    domain = "a" * _MAX_SNI_DOMAIN_SIZE

    proxy = normalize_proxy(
        {
            "scheme": "mtproxy",
            "hostname": "1.2.3.4",
            "port": 443,
            "secret": "ee" + PLAIN_SECRET_HEX + domain.encode("ascii").hex(),
        }
    )

    assert proxy.sni_hostname == domain


def test_normalize_proxy_mtproxy_sixteen_byte_secret_is_plain_whatever_its_first_byte() -> None:
    # A marker byte only marks anything at 17 bytes and up, so roughly one plain
    #  secret in 256 opens with a byte that would otherwise read as one.
    secret_hex = "ee" + PLAIN_SECRET_HEX[:-2]

    proxy = normalize_proxy({"scheme": "mtproxy", "hostname": "1.2.3.4", "port": 443, "secret": secret_hex})

    assert proxy.secret == bytes.fromhex(secret_hex)
    assert proxy.sni_hostname is None


@pytest.mark.parametrize(
    "secret_hex",
    [
        pytest.param("ee" + PLAIN_SECRET_HEX, id="ee-no-domain"),
        pytest.param("ee" + PLAIN_SECRET_HEX + "ff", id="ee-non-ascii-domain"),
        pytest.param(
            "ee" + PLAIN_SECRET_HEX + ("a" * (_MAX_SNI_DOMAIN_SIZE + 1)).encode("ascii").hex(),
            id="ee-over-long-domain",
        ),
        pytest.param("dd" + PLAIN_SECRET_HEX + "61", id="dd-with-a-trailing-domain"),
    ],
)
def test_normalize_proxy_mtproxy_malformed_secret_raises(secret_hex: str) -> None:
    with pytest.raises(ValueError):
        normalize_proxy({"scheme": "mtproxy", "hostname": "1.2.3.4", "port": 443, "secret": secret_hex})


@pytest.mark.parametrize("secret_hex", [PLAIN_SECRET_HEX, DD_SECRET_HEX])
def test_normalize_proxy_mtproxy_secret_without_ee_marker_has_no_sni(secret_hex: str) -> None:
    # Only fake-TLS needs a domain, so nothing else may invent one - the transport
    #  decides whether to speak TLS by this field being set.
    proxy = normalize_proxy(
        {"scheme": "mtproxy", "hostname": "1.2.3.4", "port": 443, "secret": secret_hex}
    )

    assert proxy.sni_hostname is None


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


def test_client_proxy_address_reports_an_mtproxy() -> None:
    mtproxy = MTProxy(hostname="1.2.3.4", port=443, secret=bytes.fromhex(PLAIN_SECRET_HEX))

    assert client_proxy_address(mtproxy) == ProxyAddress(hostname="1.2.3.4", port=443)


def test_client_proxy_address_reports_a_web_proxy_on_the_https_port() -> None:
    web_proxy = WebProxy(hostname="relay.example.com", secret=bytes.fromhex(PLAIN_SECRET_HEX))

    assert client_proxy_address(web_proxy) == ProxyAddress(hostname="relay.example.com", port=HTTPS_PORT)


@pytest.mark.parametrize(
    "proxy",
    [
        None,
        SOCKS4Proxy(hostname="1.2.3.4", port=1080),
        SOCKS5Proxy(hostname="1.2.3.4", port=1080),
        HTTPProxy(hostname="1.2.3.4", port=8080),
    ],
)
def test_client_proxy_address_reports_nothing_for_a_proxy_telegram_does_not_own(proxy: Optional[Proxy]) -> None:
    assert client_proxy_address(proxy) is None


def _base64url(secret_hex: str) -> str:
    # Telegram's own links drop the padding, so the tests carry the same shape.
    return base64.urlsafe_b64encode(bytes.fromhex(secret_hex)).decode("ascii").rstrip("=")


@pytest.mark.parametrize(
    "link",
    [
        "tg://proxy?server=1.2.3.4&port=443&secret=" + PLAIN_SECRET_HEX,
        "https://t.me/proxy?server=1.2.3.4&port=443&secret=" + PLAIN_SECRET_HEX,
        "t.me/proxy?server=1.2.3.4&port=443&secret=" + PLAIN_SECRET_HEX,
        "https://telegram.me/proxy?server=1.2.3.4&port=443&secret=" + _base64url(PLAIN_SECRET_HEX),
    ],
)
def test_normalize_proxy_mtproxy_string_link_forms(link: str) -> None:
    proxy = normalize_proxy(link)

    assert proxy == MTProxy(hostname="1.2.3.4", port=443, secret=bytes.fromhex(PLAIN_SECRET_HEX))


def test_normalize_proxy_mtproxy_link_carries_a_dd_secret_whole() -> None:
    proxy = normalize_proxy("tg://proxy?server=1.2.3.4&port=443&secret=" + DD_SECRET_HEX)

    assert proxy == MTProxy(hostname="1.2.3.4", port=443, secret=bytes.fromhex(DD_SECRET_HEX))


def test_normalize_proxy_mtproxy_link_splits_a_base64url_ee_secret() -> None:
    # The form an ee proxy is actually shared in: base64url, no padding.
    ee_secret_hex = "ee" + PLAIN_SECRET_HEX + SNI_DOMAIN.encode("ascii").hex()
    proxy = normalize_proxy("tg://proxy?server=1.2.3.4&port=443&secret=" + _base64url(ee_secret_hex))

    assert proxy == MTProxy(
        hostname="1.2.3.4",
        port=443,
        secret=bytes.fromhex(PLAIN_SECRET_HEX),
        sni_hostname=SNI_DOMAIN,
    )


@pytest.mark.parametrize(
    "link",
    [
        "tg://proxy?server=1.2.3.4&port=443",
        "tg://proxy?server=1.2.3.4&secret=" + PLAIN_SECRET_HEX,
        "tg://proxy?port=443&secret=" + PLAIN_SECRET_HEX,
    ],
)
def test_normalize_proxy_mtproxy_link_missing_a_param_raises(link: str) -> None:
    with pytest.raises(ValueError):
        normalize_proxy(link)


def test_normalize_proxy_webproxy_link_is_not_read_as_an_mtproxy_one() -> None:
    # `/proxy?` is a suffix of `/webproxy?`, so the two patterns can collide.
    proxy = normalize_proxy("https://t.me/webproxy?server=relay.example.com&secret=" + PLAIN_SECRET_HEX)

    assert isinstance(proxy, WebProxy)


# Not `PLAIN_SECRET_HEX`: its base64 and base64url forms come out byte-identical,
#  so two of the three vectors below would be the same string and only one
#  alphabet would ever be exercised. This one ends `/w` under base64 and `_w`
#  under base64url.
_ALPHABET_SENSITIVE_SECRET_HEX: Final[str] = "00112233445566778899aabbccddeeff"


@pytest.mark.parametrize(
    "encoded_secret",
    [
        _ALPHABET_SENSITIVE_SECRET_HEX,
        _base64url(_ALPHABET_SENSITIVE_SECRET_HEX),
        base64.b64encode(bytes.fromhex(_ALPHABET_SENSITIVE_SECRET_HEX)).decode("ascii"),
    ],
)
def test_normalize_proxy_mtproxy_accepts_every_encoding_tdlib_accepts(encoded_secret: str) -> None:
    proxy = normalize_proxy({"scheme": "mtproxy", "hostname": "1.2.3.4", "port": 443, "secret": encoded_secret})

    assert isinstance(proxy, MTProxy)
    assert proxy.secret == bytes.fromhex(_ALPHABET_SENSITIVE_SECRET_HEX)


def test_normalize_proxy_mtproxy_rejects_a_secret_in_no_known_encoding() -> None:
    with pytest.raises(ValueError):
        normalize_proxy({"scheme": "mtproxy", "hostname": "1.2.3.4", "port": 443, "secret": "not a secret!"})
