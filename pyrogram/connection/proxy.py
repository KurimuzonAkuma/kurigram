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
import ipaddress
import re
from dataclasses import dataclass
from typing import (
    ClassVar,
    Dict,
    Final,
    List,
    Literal,
    NamedTuple,
    Optional,
    Pattern,
    Tuple,
    Type,
    TypedDict,
    Union,
)
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


# The obfuscated2 key is 16 bytes, and a dd or ee marker prefixes it with one
#  more. The transport reads both from here, so the two sizes have one home.
#  TDLib accepts exactly these shapes: 16 bare, 17 behind `dd`, 18 or more
#  behind `ee`.
#  https://github.com/tdlib/td/blob/d1085f9cebc5a62379991ae1652673954f229c1f/td/mtproto/ProxySecret.cpp#L37-L39
OBFUSCATED2_SECRET_SIZE: Final[int] = 16
MARKED_SECRET_SIZE: Final[int] = OBFUSCATED2_SECRET_SIZE + 1


@dataclass(frozen=True)
class MTProxy:
    # Classic MTProxy: obfuscated2 straight to (hostname, port), no relay.
    scheme: ClassVar[Literal[ProxyScheme.MTPROXY]] = ProxyScheme.MTPROXY

    hostname: str
    port: int
    secret: bytes  # decoded, dd marker kept when present
    # Only an ee secret sets this: the domain its fake-TLS ClientHello presents
    #  as SNI, and the one the proxy checks the connection against.
    sni_hostname: Optional[str] = None


# The relay is always reached over HTTPS, so a WEB proxy carries no port field.
HTTPS_PORT: Final[int] = 443


@dataclass(frozen=True)
class WebProxy:
    scheme: ClassVar[Literal[ProxyScheme.WEB]] = ProxyScheme.WEB
    port: ClassVar[int] = HTTPS_PORT

    hostname: str  # canonical lowercase ASCII/IDNA A-label
    secret: bytes  # decoded, dd marker kept when present


Proxy = Union[SOCKS4Proxy, SOCKS5Proxy, HTTPProxy, MTProxy, WebProxy]


class ProxyAddress(NamedTuple):
    hostname: str
    port: int


def client_proxy_address(proxy: Optional[Proxy]) -> Optional[ProxyAddress]:
    """The address `initConnection` reports, or None when there is nothing to report.

    tdesktop reports one for the MTProxy and WEB schemes and for no other, since a
    SOCKS or HTTP proxy is not one of Telegram's own.
    https://github.com/telegramdesktop/tdesktop/blob/23dff657fc857c3223fa20472aa8614b9ab2c7eb/Telegram/SourceFiles/mtproto/session_private.cpp#L689-L700
    """
    if isinstance(proxy, (MTProxy, WebProxy)):
        return ProxyAddress(hostname=proxy.hostname, port=proxy.port)

    return None


def uses_random_padding(proxy: Optional[Proxy]) -> bool:
    """Whether a proxy's secret asks for random padding on every packet.

    TDLib reads the same answer off the encoded secret's length, before the
    marker byte comes off: 17 bytes or more means padding.
    https://github.com/tdlib/td/blob/d1085f9cebc5a62379991ae1652673954f229c1f/td/mtproto/ProxySecret.h#L44-L46
    """
    if not isinstance(proxy, (MTProxy, WebProxy)):
        return False

    # An ee secret is longer still, and `sni_hostname` is what survives its
    #  marker and domain coming off - the remaining key is a bare 16 bytes.
    if isinstance(proxy, MTProxy) and proxy.sni_hostname is not None:
        return True

    return len(proxy.secret) == MARKED_SECRET_SIZE


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


# The three secret forms, by their first byte. A plain secret carries no marker
#  and is the bare 16-byte obfuscated2 key; dd asks for random padding on every
#  packet; ee asks for the fake-TLS record layer, and appends the SNI domain
#  after the key.
#  https://core.telegram.org/mtproto/mtproto-transports#transport-obfuscation
_PADDED_MARKER: Final[int] = 0xDD
_FAKE_TLS_MARKER: Final[int] = 0xEE

# TDLib's `MAX_DOMAIN_LENGTH`, whose own comment reads "must be small enough to
#  not overflow TLS-hello length".
#  https://github.com/tdlib/td/blob/d1085f9cebc5a62379991ae1652673954f229c1f/td/mtproto/ProxySecret.h#L18
_MAX_SNI_DOMAIN_SIZE: Final[int] = 182

# An ee secret is shared base64url-encoded, the others as hex - but every client
#  accepts any of the three, so the alphabet does not identify the flavour.
_BASE64URL_ALTCHARS: Final[bytes] = b"-_"

# The WEB scheme cannot carry an ee secret whatever this library implements: the
#  relay speaks to a stock MTProxy over a plain obfuscated2 stream and never adds
#  the fake-TLS records, by design.
_WEB_FAKE_TLS_REJECTION: Final[str] = (
    "proxy secret uses TLS-emulation ('ee') framing: the relay would need to add the "
    "inner fake-TLS record stock MTProxy expects, and it deliberately does not "
    "(web-proxy-plan.md §3). Use a plain 16-byte or dd-prefixed secret instead."
)


class _DecodedSecret(NamedTuple):
    secret: bytes  # bare 16 bytes, or 17 with the dd marker kept
    sni_hostname: Optional[str]  # the domain an ee secret appends, else None


def _decode_fake_tls_secret(full_secret: bytes) -> _DecodedSecret:
    domain = full_secret[MARKED_SECRET_SIZE:]

    # TDLib rejects a longer secret outright rather than greeting with it.
    #  https://github.com/tdlib/td/blob/d1085f9cebc5a62379991ae1652673954f229c1f/td/mtproto/ProxySecret.cpp#L29-L36
    if len(domain) > _MAX_SNI_DOMAIN_SIZE:
        msg = (
            f"ee-prefixed proxy secret carries a {len(domain)}-byte SNI domain, over the "
            f"{_MAX_SNI_DOMAIN_SIZE}-byte maximum"
        )
        raise ValueError(msg)

    try:
        sni_hostname = domain.decode("ascii")
    except UnicodeDecodeError as e:
        msg = f"ee-prefixed proxy secret carries a non-ASCII SNI domain: {e}"
        raise ValueError(msg) from e

    return _DecodedSecret(secret=full_secret[1:MARKED_SECRET_SIZE], sni_hostname=sni_hostname)


def _base64_decoded(encoded_secret: str, *, altchars: bytes) -> Optional[bytes]:
    # Telegram's own links drop the `=` padding that `base64` still requires.
    padded = encoded_secret + "=" * (-len(encoded_secret) % 4)

    try:
        return base64.b64decode(padded, altchars=altchars, validate=True)

    # `binascii.Error` is a `ValueError`, and both mean the same thing here.
    except ValueError:
        return None


def _decode_proxy_secret(encoded_secret: str) -> bytes:
    """Hex, then base64 in either alphabet - the encodings TDLib accepts.

    https://github.com/tdlib/td/blob/d1085f9cebc5a62379991ae1652673954f229c1f/td/mtproto/ProxySecret.cpp#L15-L27
    """
    try:
        return bytes.fromhex(encoded_secret)
    except ValueError:
        pass

    # One call covers both alphabets, unlike TDLib, which needs two: `altchars`
    #  only rewrites `-_` into `+/` before validating, so a standard-base64
    #  secret passes through it untouched. A second pass over `b"+/"` would
    #  therefore never decode anything this one rejects.
    decoded = _base64_decoded(encoded_secret, altchars=_BASE64URL_ALTCHARS)

    if decoded is not None:
        return decoded

    msg = f"proxy 'secret' must be hex, base64url or base64: {encoded_secret!r}"
    raise ValueError(msg)


def _decode_mtproxy_secret(encoded_secret: str, *, scheme: ProxyScheme) -> _DecodedSecret:
    full_secret = _decode_proxy_secret(encoded_secret)

    # The length decides the flavour and is tested first, the order TDLib tests
    #  it in: 16 bytes is a bare key whatever its first byte happens to be, so a
    #  plain secret that starts with dd or ee is still plain.
    #  https://github.com/tdlib/td/blob/d1085f9cebc5a62379991ae1652673954f229c1f/td/mtproto/ProxySecret.cpp#L37-L39
    if len(full_secret) == OBFUSCATED2_SECRET_SIZE:
        return _DecodedSecret(secret=full_secret, sni_hostname=None)

    if len(full_secret) == MARKED_SECRET_SIZE and full_secret[0] == _PADDED_MARKER:
        return _DecodedSecret(secret=full_secret, sni_hostname=None)

    # Strictly longer than a dd secret, because the domain that follows the key
    #  may not be empty: TDLib refuses to build a ClientHello without one, so an
    #  ee secret carrying no domain is unusable rather than merely odd.
    #  https://github.com/tdlib/td/blob/d1085f9cebc5a62379991ae1652673954f229c1f/td/mtproto/TlsInit.cpp#L579
    if len(full_secret) > MARKED_SECRET_SIZE and full_secret[0] == _FAKE_TLS_MARKER:
        if scheme is ProxyScheme.WEB:
            raise ValueError(_WEB_FAKE_TLS_REJECTION)

        return _decode_fake_tls_secret(full_secret)

    msg = (
        "proxy secret must decode to 16 bytes (plain), 17 with a dd marker, or an ee "
        f"marker followed by a 16-byte key and a domain, got {len(full_secret)} bytes"
    )
    raise ValueError(msg)


# The one place each kind is built, so the dict form and the string form below
#  cannot validate differently.

def _build_web_proxy(*, hostname: str, encoded_secret: str) -> WebProxy:
    decoded = _decode_mtproxy_secret(encoded_secret, scheme=ProxyScheme.WEB)

    return WebProxy(
        hostname=canonicalize_web_hostname(hostname),
        secret=decoded.secret,
    )


def _build_mtproxy(*, hostname: str, port: Union[int, str], encoded_secret: str) -> MTProxy:
    decoded = _decode_mtproxy_secret(encoded_secret, scheme=ProxyScheme.MTPROXY)

    return MTProxy(
        hostname=hostname,
        port=int(port),
        secret=decoded.secret,
        sni_hostname=decoded.sni_hostname,
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
# `/webproxy?` above cannot also match here: the alternation anchors on `/proxy?`.
_MTPROXY_LINK_RE: Final[Pattern[str]] = re.compile(
    r"(?:https?://)?(?:www\.)?(?:t(?:elegram)?\.(?:org|me|dog)/proxy\?|tg://proxy\?)(.+)"
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
        encoded_secret = _query_param(query_parameters, name="secret")

        if not hostname or not encoded_secret:
            msg = "WEB proxy link must contain 'server' (or 'host') and 'secret' params"
            raise ValueError(msg)

        return _build_web_proxy(hostname=hostname, encoded_secret=encoded_secret)

    mtproxy_match = _MTPROXY_LINK_RE.match(link)

    if mtproxy_match:
        query_parameters = parse_qs(mtproxy_match.group(1))
        hostname = _query_param(query_parameters, name="server")
        port = _query_param(query_parameters, name="port")
        encoded_secret = _query_param(query_parameters, name="secret")

        if not hostname or not port or not encoded_secret:
            msg = "MTProxy link must contain 'server', 'port' and 'secret' params"
            raise ValueError(msg)

        return _build_mtproxy(hostname=hostname, port=port, encoded_secret=encoded_secret)

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
    encoded_secret = proxy.get("secret")
    username = proxy.get("username")
    password = proxy.get("password")

    if scheme is ProxyScheme.WEB:
        if not hostname or not encoded_secret:
            msg = "WEB proxy config requires both 'hostname' and 'secret'"
            raise ValueError(msg)

        return _build_web_proxy(hostname=hostname, encoded_secret=encoded_secret)

    if scheme is ProxyScheme.MTPROXY:
        if not hostname or not port or not encoded_secret:
            msg = "MTProxy config requires 'hostname', 'port', and 'secret'"
            raise ValueError(msg)

        return _build_mtproxy(hostname=hostname, port=port, encoded_secret=encoded_secret)

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
