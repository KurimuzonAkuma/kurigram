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

import hashlib
import hmac
from typing import Dict, Final, FrozenSet, List, NamedTuple

from pyrogram.crypto import faketls

from tests.unit.proxy_values import SNI_DOMAIN

_SECRET: Final[bytes] = bytes.fromhex("0123456789abcdef0123456789abcdef")
_UNIX_TIME: Final[int] = 1756000000

_RANDOM_OFFSET: Final[int] = 11
_RANDOM_SIZE: Final[int] = 32
_TIMESTAMP_SIZE: Final[int] = 4

_X25519_GROUP: Final[int] = 0x001D
_ML_KEM_768_X25519_GROUP: Final[int] = 0x11EC

_CURVE25519_PRIME: Final[int] = 2**255 - 19
_CURVE25519_KEY_SIZE: Final[int] = 32
_ML_KEM_768_KEY_SIZE: Final[int] = 1184

# The prime order of the Curve25519 base point. The full curve is eight times it.
#  https://www.rfc-editor.org/rfc/rfc7748#section-4.1
_CURVE25519_ORDER: Final[int] = 2**252 + 27742317777372353535851937790883648493

# The extension types the ClientHello carries, whatever order the permutation
#  puts them in. Read off TDLib's op list, so a dropped extension shows up here.
#  https://github.com/tdlib/td/blob/d1085f9cebc5a62379991ae1652673954f229c1f/td/mtproto/TlsInit.cpp#L211-L230
_EXPECTED_EXTENSIONS: Final[FrozenSet[int]] = frozenset(
    {
        0x0000,
        0x0005,
        0x000A,
        0x000B,
        0x000D,
        0x0010,
        0x0012,
        0x0017,
        0x001B,
        0x0023,
        0x002B,
        0x002D,
        0x0033,
        0x44CD,
        0xFE0D,
        0xFF01,
    }
)


def _is_grease(extension_type: int) -> bool:
    high, low = extension_type >> 8, extension_type & 0xFF

    return high == low and low & 0x0F == 0x0A


def _parse_extensions(record: bytes) -> Dict[int, bytes]:
    """Every length field in the greeting, checked on the way to the extensions."""
    assert record[:3] == b"\x16\x03\x01"

    record_length = int.from_bytes(record[3:5], "big")
    assert len(record) == 5 + record_length

    assert record[5] == 0x01
    handshake_length = int.from_bytes(record[6:9], "big")
    assert len(record) == 9 + handshake_length

    assert record[9:11] == b"\x03\x03"

    cursor = _RANDOM_OFFSET + _RANDOM_SIZE
    cursor += 1 + record[cursor]  # Legacy session id.
    cursor += 2 + int.from_bytes(record[cursor : cursor + 2], "big")  # Cipher suites.
    cursor += 1 + record[cursor]  # Compression methods.

    extensions_length = int.from_bytes(record[cursor : cursor + 2], "big")
    cursor += 2
    assert cursor + extensions_length == len(record)

    extensions: Dict[int, bytes] = {}

    while cursor < len(record):
        extension_type = int.from_bytes(record[cursor : cursor + 2], "big")
        body_length = int.from_bytes(record[cursor + 2 : cursor + 4], "big")
        cursor += 4

        assert extension_type not in extensions, f"extension {extension_type:#06x} written twice"
        extensions[extension_type] = record[cursor : cursor + body_length]
        cursor += body_length

    assert cursor == len(record)

    return extensions


def _build_client_hello() -> faketls.FakeTlsHello:
    return faketls.build_client_hello(domain=SNI_DOMAIN, secret=_SECRET, unix_time=_UNIX_TIME)


def test_client_hello_length_fields_all_agree() -> None:
    _parse_extensions(_build_client_hello().record)


def test_client_hello_names_the_domain_in_its_sni_extension() -> None:
    server_name = _parse_extensions(_build_client_hello().record)[0x0000]

    # `ServerNameList` length, one `ServerName` of type 0, then the host length.
    assert server_name[5:] == SNI_DOMAIN.encode("ascii")


def test_client_hello_carries_every_extension_whatever_the_permutation_does() -> None:
    # The extension order is randomized per greeting, so this runs enough times
    #  that a dropped or duplicated block cannot hide behind one lucky ordering.
    for _ in range(16):
        present = _parse_extensions(_build_client_hello().record)
        grease = {extension for extension in present if _is_grease(extension)}

        # Two more extensions carry a GREASE value as their type, so their number
        #  is not fixed and they are counted rather than named.
        assert len(grease) == 2
        assert frozenset(present) - grease == _EXPECTED_EXTENSIONS


def test_client_hello_extension_order_actually_varies() -> None:
    # GREASE types are drawn fresh per greeting, so an order that kept them
    #  would vary on those values alone and still pass with the permutation
    #  removed entirely.
    orders = {
        tuple(
            extension
            for extension in _parse_extensions(_build_client_hello().record)
            if not _is_grease(extension)
        )
        for _ in range(16)
    }

    assert len(orders) > 1


def test_ech_payload_length_is_one_of_the_four_tdlib_draws_between() -> None:
    # The four lengths TDLib's `Op::ech_payload()` picks between, written out as
    #  `Random::fast(0, 3) * 32 + 144` gives them.
    #  https://github.com/tdlib/td/blob/d1085f9cebc5a62379991ae1652673954f229c1f/td/mtproto/TlsInit.cpp#L126-L131
    assert faketls._ECH_PAYLOAD_SIZE in {144, 176, 208, 240}


def test_client_hello_length_is_the_same_for_every_greeting() -> None:
    # The ECH payload is the only part of the hello whose length is drawn at all,
    #  and TDLib draws it once for the process - so a length that changed from one
    #  connection to the next would be a fingerprint no browser produces.
    lengths = {len(_build_client_hello().record) for _ in range(16)}

    assert len(lengths) == 1


def test_client_hello_random_is_the_secret_hmac_with_the_clock_folded_in() -> None:
    hello = _build_client_hello()

    zeroed = hello.record[:_RANDOM_OFFSET] + bytes(_RANDOM_SIZE) + hello.record[_RANDOM_OFFSET + _RANDOM_SIZE :]
    digest = bytearray(hmac.new(_SECRET, zeroed, hashlib.sha256).digest())
    timestamp = _UNIX_TIME.to_bytes(_TIMESTAMP_SIZE, "little")

    for index in range(_TIMESTAMP_SIZE):
        digest[_RANDOM_SIZE - _TIMESTAMP_SIZE + index] ^= timestamp[index]

    assert hello.random == bytes(digest)
    assert hello.record[_RANDOM_OFFSET : _RANDOM_OFFSET + _RANDOM_SIZE] == bytes(digest)


def _server_hello_for(client_random: bytes, *, secret: bytes) -> bytes:
    """What a proxy holding `secret` answers with, per TDLib's own check."""
    body = b"\x16\x03\x03\x00\x50\x02\x00\x00\x4c\x03\x03" + bytes(_RANDOM_SIZE) + b"\x00" * 25
    digest = hmac.new(secret, client_random + body, hashlib.sha256).digest()

    return body[:_RANDOM_OFFSET] + digest + body[_RANDOM_OFFSET + _RANDOM_SIZE :]


def test_server_hello_is_authentic_accepts_a_reply_built_with_the_secret() -> None:
    hello = _build_client_hello()
    response = _server_hello_for(hello.random, secret=_SECRET)

    assert faketls.server_hello_is_authentic(response, secret=_SECRET, client_random=hello.random)


def test_server_hello_is_authentic_rejects_a_reply_built_with_another_secret() -> None:
    hello = _build_client_hello()
    response = _server_hello_for(hello.random, secret=bytes(16))

    assert not faketls.server_hello_is_authentic(response, secret=_SECRET, client_random=hello.random)


def test_server_hello_is_authentic_rejects_a_tampered_reply() -> None:
    hello = _build_client_hello()
    response = bytearray(_server_hello_for(hello.random, secret=_SECRET))
    response[-1] ^= 0xFF

    assert not faketls.server_hello_is_authentic(bytes(response), secret=_SECRET, client_random=hello.random)


class _KeyShareEntry(NamedTuple):
    group: int
    key: bytes


def _key_share_entries(record: bytes) -> List[_KeyShareEntry]:
    body = _parse_extensions(record)[0x0033]  # the key_share extension
    assert int.from_bytes(body[:2], "big") == len(body) - 2

    entries: List[_KeyShareEntry] = []
    cursor = 2

    while cursor < len(body):
        group = int.from_bytes(body[cursor : cursor + 2], "big")
        key_length = int.from_bytes(body[cursor + 2 : cursor + 4], "big")
        cursor += 4

        entries.append(_KeyShareEntry(group=group, key=body[cursor : cursor + key_length]))
        cursor += key_length

    assert cursor == len(body)

    return entries


def _is_on_curve25519(key: bytes) -> bool:
    x = int.from_bytes(key, "little")
    # 486662 is the curve's `A`.
    y_squared = ((x + 486662) * x + 1) * x % _CURVE25519_PRIME

    return pow(y_squared, (_CURVE25519_PRIME - 1) // 2, _CURVE25519_PRIME) == 1


def _is_in_prime_order_subgroup(key: bytes) -> bool:
    """Whether the order of the point at `key` divides the base point's.

    The x-only Montgomery ladder of RFC 7748 section 5, run with the group order
    as the scalar: the identity is the only point whose projective z is zero.
    """
    prime = _CURVE25519_PRIME
    x_1 = int.from_bytes(key, "little")

    x_2, z_2, x_3, z_3 = 1, 0, x_1, 1
    swap = 0

    for bit_index in reversed(range(_CURVE25519_ORDER.bit_length())):
        bit = (_CURVE25519_ORDER >> bit_index) & 1

        if swap ^ bit:
            x_2, x_3, z_2, z_3 = x_3, x_2, z_3, z_2

        swap = bit

        a_sum = (x_2 + z_2) % prime
        b_difference = (x_2 - z_2) % prime
        a_squared = a_sum * a_sum % prime
        b_squared = b_difference * b_difference % prime
        e_difference = (a_squared - b_squared) % prime

        da = (x_3 - z_3) * a_sum % prime
        cb = (x_3 + z_3) * b_difference % prime

        x_3 = pow(da + cb, 2, prime)
        z_3 = x_1 * pow(da - cb, 2, prime) % prime
        x_2 = a_squared * b_squared % prime
        # 121665 is `a24`, the ladder constant of RFC 7748 section 4.1.
        z_2 = e_difference * (a_squared + 121665 * e_difference) % prime

    if swap:
        z_2 = z_3

    return z_2 == 0


def test_key_share_offers_x25519_alone_and_paired_with_ml_kem_768() -> None:
    entries = _key_share_entries(_build_client_hello().record)
    by_group = {entry.group: entry.key for entry in entries}

    assert len(by_group[_X25519_GROUP]) == _CURVE25519_KEY_SIZE
    assert len(by_group[_ML_KEM_768_X25519_GROUP]) == _ML_KEM_768_KEY_SIZE + _CURVE25519_KEY_SIZE


def test_key_share_keys_look_like_real_x25519_public_keys() -> None:
    # A real key is a point on the curve and in the base point's subgroup; a
    #  point on the twist, or one of full order, is exactly what a fingerprinter
    #  looks for. Both properties are per-key random, so this repeats.
    for _ in range(4):
        by_group = {entry.group: entry.key for entry in _key_share_entries(_build_client_hello().record)}
        keys = (by_group[_X25519_GROUP], by_group[_ML_KEM_768_X25519_GROUP][_ML_KEM_768_KEY_SIZE:])

        for key in keys:
            assert _is_on_curve25519(key)
            assert _is_in_prime_order_subgroup(key)


def test_client_hello_needs_no_padding_extension() -> None:
    # The padding op only fires below offset 513, and the ML-KEM key alone is 1184
    #  bytes - so the extension TDLib still lists is never reached in practice. The
    #  op stays because dropping it would make this file diverge from its source.
    assert 0x0015 not in _parse_extensions(_build_client_hello().record)
