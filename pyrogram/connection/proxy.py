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


import ipaddress
import re
from dataclasses import dataclass
from typing import ClassVar, Dict, Final, List, Literal, Optional, Pattern, Tuple, Type, TypedDict, Union
from urllib.parse import parse_qs, urlsplit

from pyrogram.enums import ProxyScheme

# One frozen dataclass per proxy kind. Connection, TCP and the transports take
#  only these - never a raw dict or string.


@dataclass(frozen=True)
class SOCKS4Proxy:
    scheme: ClassVar[Literal[ProxyScheme.SOCKS4]] = ProxyScheme.SOCKS4

    hostname: str
    port: int
    username: Optional[str] = None
    password: Optional[str] = None


@dataclass(frozen=True)
class SOCKS5Proxy:
    scheme: ClassVar[Literal[ProxyScheme.SOCKS5]] = ProxyScheme.SOCKS5

    hostname: str
    port: int
    username: Optional[str] = None
    password: Optional[str] = None


@dataclass(frozen=True)
class HTTPProxy:
    scheme: ClassVar[Literal[ProxyScheme.HTTP]] = ProxyScheme.HTTP

    hostname: str
    port: int
    username: Optional[str] = None
    password: Optional[str] = None


@dataclass(frozen=True)
class MTProxy:
    # Classic MTProxy: obfuscated2 straight to (hostname, port), no relay. Not
    #  implemented yet - TCP raises a clear NotImplementedError for it. The type
    #  exists now so implementing it needs no further proxy-shape changes.
    scheme: ClassVar[Literal[ProxyScheme.MTPROXY]] = ProxyScheme.MTPROXY

    hostname: str
    port: int
    secret: bytes  # decoded, dd marker kept when present


@dataclass(frozen=True)
class WebProxy:
    scheme: ClassVar[Literal[ProxyScheme.WEB]] = ProxyScheme.WEB

    hostname: str  # canonical lowercase ASCII/IDNA A-label
    secret: bytes  # decoded, dd marker kept when present


Proxy = Union[SOCKS4Proxy, SOCKS5Proxy, HTTPProxy, MTProxy, WebProxy]

_PROXY_TYPES: Final[Tuple[type, ...]] = (SOCKS4Proxy, SOCKS5Proxy, HTTPProxy, MTProxy, WebProxy)

# Schemes python_socks dials for us; the rest need a transport of their own.
_DIALED_PROXY_TYPES: Final[Dict[ProxyScheme, Type[Union[SOCKS4Proxy, SOCKS5Proxy, HTTPProxy]]]] = {
    ProxyScheme.SOCKS4: SOCKS4Proxy,
    ProxyScheme.SOCKS5: SOCKS5Proxy,
    ProxyScheme.HTTP: HTTPProxy,
}


# The dict form accepted at the public boundary, Client(proxy={...}).

class _SOCKS4ProxyDictRequired(TypedDict):
    scheme: Literal["socks4"]
    hostname: str
    port: int


class SOCKS4ProxyDict(_SOCKS4ProxyDictRequired, total=False):
    username: str
    password: str


class _SOCKS5ProxyDictRequired(TypedDict):
    scheme: Literal["socks5"]
    hostname: str
    port: int


class SOCKS5ProxyDict(_SOCKS5ProxyDictRequired, total=False):
    username: str
    password: str


class _HTTPProxyDictRequired(TypedDict):
    scheme: Literal["http"]
    hostname: str
    port: int


class HTTPProxyDict(_HTTPProxyDictRequired, total=False):
    username: str
    password: str


class MTProxyDict(TypedDict):
    scheme: Literal["mtproxy"]
    hostname: str
    port: int
    secret: str


class WebProxyDict(TypedDict):
    scheme: Literal["web"]
    hostname: str
    secret: str


ProxyDict = Union[SOCKS4ProxyDict, SOCKS5ProxyDict, HTTPProxyDict, MTProxyDict, WebProxyDict]


def canonicalize_web_hostname(hostname: str) -> str:
    # Best-effort mirror of tdesktop's WEB `host` validation (web-proxy-plan.md
    #  §2.4): the canonical lowercase ASCII/IDNA A-label. Different
    #  normalizations of the same hostname derive different bridge
    #  capabilities, so this must run once, at normalization time, before the
    #  hostname is used for anything.
    hostname = hostname.strip().rstrip(".")

    if not hostname:
        msg = "WEB proxy hostname is empty"
        raise ValueError(msg)

    try:
        ipaddress.ip_address(hostname)
    except ValueError:
        pass
    else:
        msg = f"WEB proxy hostname must not be an IP literal: {hostname!r}"
        raise ValueError(msg)

    try:
        canonical = hostname.encode("idna").decode("ascii").lower()
    except UnicodeError as e:
        msg = f"WEB proxy hostname is not a valid DNS name: {hostname!r}"
        raise ValueError(msg) from e

    if "." not in canonical:
        msg = f"WEB proxy hostname must not be a single-label name: {hostname!r}"
        raise ValueError(msg)

    return canonical


# An `ee` secret asks for the fake-TLS record layer tdesktop wraps around the
#  obfuscated2 stream, and neither kind here can carry it. The reason differs per
#  kind, so the two messages do too - a WEB user who is told about an unimplemented
#  record layer will go looking for it in this library, and an MTProxy user who is
#  told about a relay never configured one.
_WEB_FAKE_TLS_REJECTION: Final[str] = (
    "proxy secret uses TLS-emulation ('ee') framing: the relay would need to add the "
    "inner fake-TLS record stock MTProxy expects, and it deliberately does not "
    "(web-proxy-plan.md §3). Use a plain 16-byte or dd-prefixed secret instead."
)

_MTPROXY_FAKE_TLS_REJECTION: Final[str] = (
    "proxy secret uses TLS-emulation ('ee') framing, which needs a TLS record layer "
    "under the obfuscated2 stream that this library does not implement. Use a plain "
    "16-byte or dd-prefixed secret instead."
)


def _decode_mtproxy_secret(secret_hex: str, *, scheme: ProxyScheme) -> bytes:
    try:
        full_secret = bytes.fromhex(secret_hex)
    except ValueError as e:
        msg = f"proxy 'secret' must be a hex string: {e}"
        raise ValueError(msg) from e

    if full_secret[:1] == b"\xee":
        msg = _WEB_FAKE_TLS_REJECTION if scheme is ProxyScheme.WEB else _MTPROXY_FAKE_TLS_REJECTION
        raise ValueError(msg)

    if len(full_secret) == 17 and full_secret[0] == 0xDD:
        return full_secret

    if len(full_secret) == 16:
        return full_secret

    msg = f"proxy secret must decode to 16 bytes (plain) or 17 bytes (dd-prefixed), got {len(full_secret)}"
    raise ValueError(msg)


# The one place each kind is built, so the dict form and the string form below
#  cannot validate differently.

def _build_web_proxy(*, hostname: str, secret_hex: str) -> WebProxy:
    return WebProxy(
        hostname=canonicalize_web_hostname(hostname),
        secret=_decode_mtproxy_secret(secret_hex, scheme=ProxyScheme.WEB),
    )


def _build_mtproxy(*, hostname: str, port: Union[int, str], secret_hex: str) -> MTProxy:
    return MTProxy(
        hostname=hostname,
        port=int(port),
        secret=_decode_mtproxy_secret(secret_hex, scheme=ProxyScheme.MTPROXY),
    )


def _build_dialed_proxy(
    *,
    scheme: ProxyScheme,
    hostname: str,
    port: Union[int, str],
    username: Optional[str] = None,
    password: Optional[str] = None,
) -> Union[SOCKS4Proxy, SOCKS5Proxy, HTTPProxy]:
    proxy_type = _DIALED_PROXY_TYPES[scheme]

    return proxy_type(hostname=hostname, port=int(port), username=username, password=password)


def _parse_scheme(scheme_value: Optional[str]) -> ProxyScheme:
    if not scheme_value:
        msg = "proxy dict must contain 'scheme'"
        raise ValueError(msg)

    try:
        return ProxyScheme(str(scheme_value).lower())
    except ValueError as e:
        msg = f"unknown proxy scheme: {scheme_value!r}"
        raise ValueError(msg) from e


_WEB_PROXY_LINK_RE: Final[Pattern[str]] = re.compile(
    r"(?:https?://)?(?:www\.)?(?:t(?:elegram)?\.(?:org|me|dog)/webproxy\?|tg://webproxy\?)(.+)"
)
_SOCKS_LINK_RE: Final[Pattern[str]] = re.compile(
    r"(?:https?://)?(?:www\.)?(?:t(?:elegram)?\.(?:org|me|dog)/socks\?|tg://socks\?)(.+)"
)


def _query_param(query_parameters: Dict[str, List[str]], *, name: str) -> Optional[str]:
    values = query_parameters.get(name)

    return values[0] if values else None


def _parse_proxy_link(link: str) -> Proxy:
    web_match = _WEB_PROXY_LINK_RE.match(link)

    if web_match:
        query_parameters = parse_qs(web_match.group(1))
        # `host` is the alias the Android fork emits for the same field.
        hostname = _query_param(query_parameters, name="server") or _query_param(query_parameters, name="host")
        secret_hex = _query_param(query_parameters, name="secret")

        if not hostname or not secret_hex:
            msg = "WEB proxy link must contain 'server' (or 'host') and 'secret' params"
            raise ValueError(msg)

        return _build_web_proxy(hostname=hostname, secret_hex=secret_hex)

    socks_match = _SOCKS_LINK_RE.match(link)

    if socks_match:
        query_parameters = parse_qs(socks_match.group(1))
        hostname = _query_param(query_parameters, name="server")
        port = _query_param(query_parameters, name="port")

        if not hostname or not port:
            msg = "Telegram proxy link must contain 'server' and 'port' params"
            raise ValueError(msg)

        return _build_dialed_proxy(
            scheme=ProxyScheme.SOCKS5,
            hostname=hostname,
            port=port,
            username=_query_param(query_parameters, name="user"),
            password=_query_param(query_parameters, name="pass"),
        )

    parts = urlsplit(link)

    if not parts.scheme or not parts.hostname or not parts.port:
        msg = f"proxy string is not a recognized proxy URL: {link!r}"
        raise ValueError(msg)

    scheme = _parse_scheme(parts.scheme)

    if scheme not in _DIALED_PROXY_TYPES:
        msg = f"{scheme.value} proxy cannot be written as a plain URL; use the dict or tg:// form"
        raise ValueError(msg)

    return _build_dialed_proxy(
        scheme=scheme,
        hostname=parts.hostname,
        port=parts.port,
        username=parts.username,
        password=parts.password,
    )


def _parse_proxy_dict(proxy: ProxyDict) -> Proxy:
    scheme = _parse_scheme(proxy.get("scheme"))
    hostname = proxy.get("hostname")
    port = proxy.get("port")
    secret_hex = proxy.get("secret")
    username = proxy.get("username")
    password = proxy.get("password")

    if scheme is ProxyScheme.WEB:
        if not hostname or not secret_hex:
            msg = "WEB proxy config requires both 'hostname' and 'secret'"
            raise ValueError(msg)

        return _build_web_proxy(hostname=hostname, secret_hex=secret_hex)

    if scheme is ProxyScheme.MTPROXY:
        if not hostname or not port or not secret_hex:
            msg = "MTProxy config requires 'hostname', 'port', and 'secret'"
            raise ValueError(msg)

        return _build_mtproxy(hostname=hostname, port=port, secret_hex=secret_hex)

    if not hostname or not port:
        msg = f"{scheme.value} proxy config requires 'hostname' and 'port'"
        raise ValueError(msg)

    return _build_dialed_proxy(
        scheme=scheme,
        hostname=hostname,
        port=port,
        username=username,
        password=password,
    )


def normalize_proxy(proxy: Union[str, ProxyDict, Proxy, None]) -> Optional[Proxy]:
    if proxy is None:
        return None

    if isinstance(proxy, _PROXY_TYPES):
        return proxy

    if isinstance(proxy, str):
        return _parse_proxy_link(proxy)

    if isinstance(proxy, dict):
        return _parse_proxy_dict(proxy)

    msg = f"proxy must be a `str`, `dict`, or `Proxy`, got: `{proxy!r}`"
    raise TypeError(msg)
