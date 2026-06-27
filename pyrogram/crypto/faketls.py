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

import os
import struct
import random


MAX_GREASE = 8
P25519 = 2 ** 255 - 19


def _get_y2(x, mod):
    y = (x + 486662) % mod
    y = (y * x) % mod
    y = (y + 1) % mod
    y = (y * x) % mod
    return y


def _get_double_x(x, mod):
    denominator = (_get_y2(x, mod) * 4) % mod
    numerator = (x * x - 1) % mod
    numerator = (numerator * numerator) % mod
    denominator_inv = pow(denominator, mod - 2, mod)
    return (numerator * denominator_inv) % mod


def generate_public_key():
    mod = P25519
    pw = (mod - 1) // 2
    while True:
        key = bytearray(os.urandom(32))
        key[31] &= 127
        x = int.from_bytes(key, "big")
        x = (x * x) % mod
        if pow(_get_y2(x, mod), pw, mod) == 1:
            break
    for _ in range(3):
        x = _get_double_x(x, mod)
    return x.to_bytes(32, "big")[::-1]


def generate_key_ml_kem_768():
    Q = 3329
    N = 384
    key = bytearray(1184)
    values = struct.unpack("<%dI" % (N * 2), os.urandom(N * 2 * 4))
    for i in range(N):
        a = values[i * 2] % Q
        b = values[i * 2 + 1] % Q
        key[i * 3 + 0] = a & 0xFF
        key[i * 3 + 1] = ((a >> 8) | ((b & 0x0F) << 4)) & 0xFF
        key[i * 3 + 2] = (b >> 4) & 0xFF
    key[1152:1184] = os.urandom(32)
    return bytes(key)


def _gen_grease():
    g = bytearray(os.urandom(MAX_GREASE))
    for a in range(MAX_GREASE):
        g[a] = (g[a] & 0xf0) + 0x0A
    for i in range(1, MAX_GREASE, 2):
        if i + 1 < MAX_GREASE and g[i] == g[i + 1]:
            g[i] ^= 0x10
    return g


def _write_op(op, out, scopes, grease, domain):
    t = op[0]
    if t == 'str':
        out += op[1]
    elif t == 'rand':
        out += os.urandom(op[1])
    elif t == 'K':
        out += generate_public_key()
    elif t == 'M':
        out += generate_key_ml_kem_768()
    elif t == 'zero':
        out += b"\x00" * op[1]
    elif t == 'domain':
        d = domain.encode("ascii", "ignore")[:253]
        out += d
    elif t == 'grease':
        g = grease[op[1]]
        out += bytes([g, g])
    elif t == 'begin':
        scopes.append(len(out))
        out += b"\x00\x00"
    elif t == 'end':
        begin = scopes.pop()
        size = len(out) - begin - 2
        out[begin] = (size >> 8) & 0xFF
        out[begin + 1] = size & 0xFF
    elif t == 'E':
        length = (144, 176, 208, 240)[random.randrange(4)]
        out += os.urandom(length)
    elif t == 'P':
        length = len(out)
        if length <= 513:
            _write_op(('str', b"\x00\x15"), out, scopes, grease, domain)
            _write_op(('begin',), out, scopes, grease, domain)
            _write_op(('zero', 513 - length), out, scopes, grease, domain)
            _write_op(('end',), out, scopes, grease, domain)
    elif t == 'perm':
        parts = list(op[1])
        n = len(parts)
        for i in range(n - 1):
            j = i + random.randrange(n - i)
            if i != j:
                parts[i], parts[j] = parts[j], parts[i]
        for part in parts:
            for o in part:
                _write_op(o, out, scopes, grease, domain)
    else:
        raise ValueError("unknown op %r" % (t,))


def _default_ops():
    s = lambda b: ('str', b)
    return [
        s(b"\x16\x03\x01"),
        ('begin',),
        s(b"\x01\x00"),
        ('begin',),
        s(b"\x03\x03"),
        ('zero', 32),
        s(b"\x20"),
        ('rand', 32),
        s(b"\x00\x20"),
        ('grease', 0),
        s(b"\x13\x01\x13\x02\x13\x03\xc0\x2b\xc0\x2f\xc0\x2c\xc0\x30\xcc\xa9\xcc\xa8\xc0\x13\xc0\x14\x00\x9c\x00\x9d\x00\x2f\x00\x35\x01\x00"),
        ('begin',),
        ('grease', 2),
        s(b"\x00\x00"),
        ('perm', [
            [
                s(b"\x00\x00"),
                ('begin',),
                ('begin',),
                s(b"\x00"),
                ('begin',),
                ('domain',),
                ('end',),
                ('end',),
                ('end',),
            ],
            [s(b"\x00\x05\x00\x05\x01\x00\x00\x00\x00")],
            [
                s(b"\x00\x0a\x00\x0c\x00\x0a"),
                ('grease', 4),
                s(b"\x11\xec\x00\x1d\x00\x17\x00\x18"),
            ],
            [s(b"\x00\x0b\x00\x02\x01\x00")],
            [s(b"\x00\x0d\x00\x12\x00\x10\x04\x03\x08\x04\x04\x01\x05\x03\x08\x05\x05\x01\x08\x06\x06\x01")],
            [s(b"\x00\x10\x00\x0e\x00\x0c\x02\x68\x32\x08\x68\x74\x74\x70\x2f\x31\x2e\x31")],
            [s(b"\x00\x12\x00\x00")],
            [s(b"\x00\x17\x00\x00")],
            [s(b"\x00\x1b\x00\x03\x02\x00\x02")],
            [s(b"\x00\x23\x00\x00")],
            [
                s(b"\x00\x2b\x00\x07\x06"),
                ('grease', 6),
                s(b"\x03\x04\x03\x03"),
            ],
            [s(b"\x00\x2d\x00\x02\x01\x01")],
            [
                s(b"\x00\x33\x04\xef\x04\xed"),
                ('grease', 4),
                s(b"\x00\x01\x00\x11\xec\x04\xc0"),
                ('M',),
                ('K',),
                s(b"\x00\x1d\x00\x20"),
                ('K',),
            ],
            [s(b"\x44\xcd\x00\x05\x00\x03\x02\x68\x32")],
            [
                s(b"\xfe\x0d"),
                ('begin',),
                s(b"\x00\x00\x01\x00\x01"),
                ('rand', 1),
                s(b"\x00\x20"),
                ('rand', 32),
                ('begin',),
                ('E',),
                ('end',),
                ('end',),
            ],
            [s(b"\xff\x01\x00\x01\x00")],
        ]),
        ('grease', 3),
        s(b"\x00\x01\x00"),
        ('P',),
        ('end',),
        ('end',),
        ('end',),
    ]


def build_fake_tls_client_hello(domain: str) -> bytearray:
    grease = _gen_grease()
    out = bytearray()
    scopes = []
    for op in _default_ops():
        _write_op(op, out, scopes, grease, domain)
    return out
