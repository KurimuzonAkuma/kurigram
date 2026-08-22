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

from pyrogram.connection.transport.tcp.tcp import (
    FRAME_HEADER_SIZE,
    FRAME_MAX_PAYLOAD,
    TCP,
    FrameParseError,
    FrameType,
    derive_bridge_capability,
    parse_frame_message,
    parse_frames,
    serialize_frame,
)

# --- wire frame codec -------------------------------------------------


def test_serialize_parse_round_trip():
    payload = b"hello mtproxy"
    wire = serialize_frame(FrameType.DATA, 42, payload)

    frames, consumed = parse_frames(wire)

    assert consumed == len(wire)
    assert len(frames) == 1
    assert frames[0].type == FrameType.DATA
    assert frames[0].stream_id == 42
    assert frames[0].payload == payload


def test_parse_concatenated_frames():
    a = serialize_frame(FrameType.HELLO, 0, b"\x01")
    b = serialize_frame(FrameType.OPEN, 7, b"")
    c = serialize_frame(FrameType.DATA, 7, b"payload")
    buf = a + b + c

    frames, consumed = parse_frames(buf)

    assert consumed == len(buf)
    assert [f.type for f in frames] == [FrameType.HELLO, FrameType.OPEN, FrameType.DATA]


def test_parse_trailing_partial_frame_not_consumed():
    full = serialize_frame(FrameType.PING, 0, b"")
    partial = bytes([FrameType.DATA, 0, 0, 1, 0, 0, 0])  # header alone, truncated
    buf = full + partial

    frames, consumed = parse_frames(buf)

    assert len(frames) == 1
    assert frames[0].type == FrameType.PING
    assert consumed == len(full)


def test_parse_unknown_type_rejected():
    buf = bytes([0x7F, 0, 0, 0, 0, 0, 0, 0])  # unknown type, zero-length payload
    with pytest.raises(FrameParseError):
        parse_frames(buf)


def test_parse_oversized_payload_rejected():
    buf = bytearray(FRAME_HEADER_SIZE)
    buf[0] = FrameType.DATA
    size = FRAME_MAX_PAYLOAD + 1
    buf[4:8] = size.to_bytes(4, "big")
    with pytest.raises(FrameParseError):
        parse_frames(bytes(buf))


def test_parse_message_rejects_empty_and_partial():
    with pytest.raises(FrameParseError):
        parse_frame_message(b"")

    full = serialize_frame(FrameType.PONG, 0, b"")
    trailing = full + b"\x01"
    with pytest.raises(FrameParseError):
        parse_frame_message(trailing)

    assert parse_frame_message(full)[0].type == FrameType.PONG


def test_serialize_stream_id_encoding():
    wire = serialize_frame(FrameType.WINDOW, 0x00ABCDEF, b"\x00\x00\x00\x01")
    assert wire[1:4] == b"\xab\xcd\xef"


def test_serialize_rejects_out_of_range_stream_id():
    with pytest.raises(ValueError):
        serialize_frame(FrameType.DATA, 0x01000000, b"")


def test_serialize_rejects_oversized_payload():
    with pytest.raises(ValueError):
        serialize_frame(FrameType.DATA, 1, b"\x00" * (FRAME_MAX_PAYLOAD + 1))


# --- bridge capability derivation --------------------------------------

# Normative vectors from docs/web-proxy-plan.md section 10 - the same two
# vectors the Go relay's own test suite (tproxy-server/internal/relay/
# bridge_test.go) is checked against, so both sides of the reference
# implementation agree with tdesktop's client byte-for-byte.
_VECTORS = [
    (
        "proxy.example.com",
        "000102030405060708090a0b0c0d0e0f",
        "MHLEY5PmW1GWqJkSrlmJpvJUiLhBH_QKy6yKg8a0JPk",
    ),
    (
        "proxy.example.com",
        "dd000102030405060708090a0b0c0d0e0f",
        "IpJrt3e7sKtzPyoXy6w-Zj6GGEvsvclN66JzQEfPYLA",
    ),
]


def test_derive_bridge_capability_normative_vectors():
    for host, secret_hex, expected in _VECTORS:
        secret = bytes.fromhex(secret_hex)
        assert derive_bridge_capability(host, secret) == expected


def test_derive_bridge_capability_is_sensitive_to_host_and_secret():
    secret = bytes.fromhex("000102030405060708090a0b0c0d0e0f")
    a = derive_bridge_capability("proxy.example.com", secret)
    b = derive_bridge_capability("other.example.com", secret)
    assert a != b

    other_secret = bytes.fromhex("0f0e0d0c0b0a09080706050403020100")
    c = derive_bridge_capability("proxy.example.com", other_secret)
    assert a != c


# --- proxy config parsing (dict and string link forms) ------------------

_SECRET_HEX = "cc1405e16163887494a4425d6925f218"


def test_web_proxy_dict_form_is_recognized():
    t = TCP(proxy={"scheme": "web", "hostname": "relay.example.com", "secret": _SECRET_HEX}, dc_id=2)
    assert t.is_web_proxy
    assert t._web_hostname == "relay.example.com"
    assert t._web_secret == bytes.fromhex(_SECRET_HEX)


def test_web_proxy_dict_form_is_case_insensitive_scheme():
    t = TCP(proxy={"scheme": "WEB", "hostname": "relay.example.com", "secret": _SECRET_HEX}, dc_id=2)
    assert t.is_web_proxy


@pytest.mark.parametrize("link", [
    f"tg://webproxy?server=relay.example.com&secret={_SECRET_HEX}",
    f"https://t.me/webproxy?server=relay.example.com&secret={_SECRET_HEX}",
    f"tg://webproxy?host=relay.example.com&secret={_SECRET_HEX}",  # Android-fork compat alias
])
def test_web_proxy_string_link_forms_are_recognized(link):
    t = TCP(proxy=link, dc_id=2)
    assert t.is_web_proxy
    assert t._web_hostname == "relay.example.com"
    assert t._web_secret == bytes.fromhex(_SECRET_HEX)


def test_web_proxy_string_link_missing_secret_raises():
    with pytest.raises(ValueError):
        TCP(proxy="tg://webproxy?server=relay.example.com", dc_id=2)


def test_ordinary_socks_link_is_not_mistaken_for_web_proxy():
    t = TCP(proxy="tg://socks?server=1.2.3.4&port=1080", dc_id=2)
    assert not t.is_web_proxy


def test_dd_prefixed_secret_keeps_marker_for_capability_but_not_for_obfuscated2():
    dd_hex = "dd" + _SECRET_HEX
    t = TCP(proxy={"scheme": "web", "hostname": "relay.example.com", "secret": dd_hex}, dc_id=2)
    assert t._web_full_secret == bytes.fromhex(dd_hex)
    assert t._web_secret == bytes.fromhex(_SECRET_HEX)  # marker stripped


def test_invalid_secret_length_raises():
    with pytest.raises(ValueError):
        TCP(proxy={"scheme": "web", "hostname": "relay.example.com", "secret": "aabbcc"}, dc_id=2)
