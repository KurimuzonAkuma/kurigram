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
from typing import Literal, Optional, TypedDict, Union
from urllib.parse import parse_qs, urlsplit

from pyrogram.enums import ProxyScheme

# --- canonical internal representation ------------------------------------
# One frozen dataclass per proxy kind. Connection, TCP and the transports
# take only these - never a raw dict or string.


@dataclass(frozen=True)
class Socks4Proxy:
    hostname: str
    port: int
    username: Optional[str] = None
    password: Optional[str] = None
    scheme: Literal[ProxyScheme.SOCKS4] = ProxyScheme.SOCKS4


@dataclass(frozen=True)
class Socks5Proxy:
    hostname: str
    port: int
    username: Optional[str] = None
    password: Optional[str] = None
    scheme: Literal[ProxyScheme.SOCKS5] = ProxyScheme.SOCKS5


@dataclass(frozen=True)
class HttpProxy:
    hostname: str
    port: int
    username: Optional[str] = None
    password: Optional[str] = None
    scheme: Literal[ProxyScheme.HTTP] = ProxyScheme.HTTP


@dataclass(frozen=True)
class MtProxy:
    # Classic MTProxy: obfuscated2 straight to (hostname, port), no relay.
    # Not connected yet - TCP raises a clear NotImplementedError for it
    # until #325 lands. The type exists now so that landing doesn't need
    # another round of proxy-shape changes.
    hostname: str
    port: int
    secret: bytes  # decoded, dd marker kept when present
    scheme: Literal[ProxyScheme.MTPROXY] = ProxyScheme.MTPROXY


@dataclass(frozen=True)
class WebProxy:
    hostname: str  # canonical lowercase ASCII/IDNA A-label
    secret: bytes  # decoded, dd marker kept when present
    scheme: Literal[ProxyScheme.WEB] = ProxyScheme.WEB


Proxy = Union[Socks4Proxy, Socks5Proxy, HttpProxy, MtProxy, WebProxy]


# --- dict form accepted at the public boundary (Client(proxy={...})) ------

class _Socks4ProxyDictRequired(TypedDict):
    scheme: Literal["socks4"]
    hostname: str
    port: int


class Socks4ProxyDict(_Socks4ProxyDictRequired, total=False):
    username: str
    password: str


class _Socks5ProxyDictRequired(TypedDict):
    scheme: Literal["socks5"]
    hostname: str
    port: int


class Socks5ProxyDict(_Socks5ProxyDictRequired, total=False):
    username: str
    password: str


class _HttpProxyDictRequired(TypedDict):
    scheme: Literal["http"]
    hostname: str
    port: int


class HttpProxyDict(_HttpProxyDictRequired, total=False):
    username: str
    password: str


class MtProxyDict(TypedDict):
    scheme: Literal["mtproxy"]
    hostname: str
    port: int
    secret: str


class WebProxyDict(TypedDict):
    scheme: Literal["web"]
    hostname: str
    secret: str


ProxyDict = Union[Socks4ProxyDict, Socks5ProxyDict, HttpProxyDict, MtProxyDict, WebProxyDict]


# --- hostname canonicalization (WEB only) ----------------------------------

def canonicalize_web_hostname(hostname: str) -> str:
    # Best-effort mirror of tdesktop's WEB `host` validation (§2.4): the
    # canonical lowercase ASCII/IDNA A-label. Different normalizations of
    # the same hostname derive different bridge capabilities, so this must
    # run once, at normalization time, before the hostname is used for
    # anything.
    hostname = hostname.strip().rstrip(".")
    if not hostname:
        raise ValueError("WEB proxy hostname is empty")

    try:
        ipaddress.ip_address(hostname)
    except ValueError:
        pass
    else:
        raise ValueError(f"WEB proxy hostname must not be an IP literal: {hostname!r}")

    try:
        canonical = hostname.encode("idna").decode("ascii").lower()
    except UnicodeError as e:
        raise ValueError(f"WEB proxy hostname is not a valid DNS name: {hostname!r}") from e

    if "." not in canonical:
        raise ValueError(f"WEB proxy hostname must not be a single-label name: {hostname!r}")

    return canonical


def _decode_mtproxy_secret(secret_hex: str, *, allow_dd: bool) -> bytes:
    try:
        full_secret = bytes.fromhex(secret_hex)
    except ValueError as e:
        raise ValueError(f"proxy 'secret' must be a hex string: {e}") from e

    if full_secret[:1] == b"\xee":
        raise ValueError(
            "proxy secret uses TLS-emulation ('ee') framing: the relay would need to add the "
            "inner fake-TLS record stock MTProxy expects, and it deliberately does not "
            "(web-proxy-plan.md §3). Use a plain 16-byte or dd-prefixed secret instead."
        )

    if allow_dd and len(full_secret) == 17 and full_secret[0] == 0xDD:
        return full_secret
    if len(full_secret) == 16:
        return full_secret

    expected = "16 bytes (plain) or 17 bytes (dd-prefixed)" if allow_dd else "16 bytes"
    raise ValueError(f"proxy secret must decode to {expected}, got {len(full_secret)}")


# --- string form: tg://…, https://t.me/…, scheme://user:pass@host:port ----

_WEB_PROXY_LINK_RE = re.compile(
    r"(?:https?://)?(?:www\.)?(?:t(?:elegram)?\.(?:org|me|dog)/webproxy\?|tg://webproxy\?)(.+)"
)
_SOCKS_LINK_RE = re.compile(
    r"(?:https?://)?(?:www\.)?(?:t(?:elegram)?\.(?:org|me|dog)/socks\?|tg://socks\?)(.+)"
)


def _parse_proxy_string(link: str) -> dict:
    match = _WEB_PROXY_LINK_RE.match(link)
    if match:
        params = parse_qs(match.group(1))
        hostname = params.get("server", [None])[0] or params.get("host", [None])[0]  # host: Android-fork alias
        secret = params.get("secret", [None])[0]
        if not hostname or not secret:
            raise ValueError("WEB proxy link must contain 'server' (or 'host') and 'secret' params")
        return {"scheme": "web", "hostname": hostname, "secret": secret}

    match = _SOCKS_LINK_RE.match(link)
    if match:
        params = parse_qs(match.group(1))
        server = params.get("server", [None])[0]
        port = params.get("port", [None])[0]
        user = params.get("user", [None])[0]
        password = params.get("pass", [None])[0]
        if not server or not port:
            raise ValueError("Telegram proxy link must contain 'server' and 'port' params")
        return {"scheme": "socks5", "hostname": server, "port": port, "username": user, "password": password}

    parts = urlsplit(link)
    if not parts.scheme or not parts.hostname or not parts.port:
        raise ValueError(f"proxy string is not a recognized proxy URL: {link!r}")
    return {
        "scheme": parts.scheme,
        "hostname": parts.hostname,
        "port": parts.port,
        "username": parts.username,
        "password": parts.password,
    }


# --- the normalizer: the one place that validates --------------------------

def normalize_proxy(proxy: Union[str, dict, "Proxy", None]) -> Optional["Proxy"]:
    if proxy is None:
        return None
    if isinstance(proxy, (Socks4Proxy, Socks5Proxy, HttpProxy, MtProxy, WebProxy)):
        return proxy

    if isinstance(proxy, str):
        proxy = _parse_proxy_string(proxy)
    if not isinstance(proxy, dict):
        raise TypeError(f"proxy must be a str, dict, or Proxy, got {type(proxy).__name__}")

    scheme_value = proxy.get("scheme")
    if not scheme_value:
        raise ValueError("proxy dict must contain 'scheme'")
    try:
        scheme = ProxyScheme(str(scheme_value).lower())
    except ValueError as e:
        raise ValueError(f"unknown proxy scheme: {scheme_value!r}") from e

    if scheme is ProxyScheme.WEB:
        hostname = proxy.get("hostname")
        secret_hex = proxy.get("secret")
        if not hostname or not secret_hex:
            raise ValueError("WEB proxy config requires both 'hostname' and 'secret'")
        return WebProxy(
            hostname=canonicalize_web_hostname(hostname),
            secret=_decode_mtproxy_secret(secret_hex, allow_dd=True),
        )
    elif scheme is ProxyScheme.MTPROXY:
        hostname = proxy.get("hostname")
        port = proxy.get("port")
        secret_hex = proxy.get("secret")
        if not hostname or not port or not secret_hex:
            raise ValueError("MTProxy config requires 'hostname', 'port', and 'secret'")
        return MtProxy(hostname=hostname, port=int(port), secret=_decode_mtproxy_secret(secret_hex, allow_dd=True))
    elif scheme in (ProxyScheme.SOCKS4, ProxyScheme.SOCKS5, ProxyScheme.HTTP):
        hostname = proxy.get("hostname")
        port = proxy.get("port")
        if not hostname or not port:
            raise ValueError(f"{scheme.value} proxy config requires 'hostname' and 'port'")
        kwargs = dict(hostname=hostname, port=int(port), username=proxy.get("username"), password=proxy.get("password"))
        if scheme is ProxyScheme.SOCKS4:
            return Socks4Proxy(**kwargs)
        if scheme is ProxyScheme.SOCKS5:
            return Socks5Proxy(**kwargs)
        return HttpProxy(**kwargs)
    else:
        raise AssertionError(f"unhandled proxy scheme: {scheme!r}")  # every ProxyScheme member is covered above
