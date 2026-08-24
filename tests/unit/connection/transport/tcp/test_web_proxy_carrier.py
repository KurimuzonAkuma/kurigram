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

from pyrogram.connection.transport.tcp.web_proxy_carrier import (
    FrameType,
    parse_frame_message,
    parse_frames,
    serialize_frame,
)


def test_large_legal_batch_is_not_rejected():
    # §7.1: the relay may legally batch up to 2 MiB of small frames into one
    # response. A frame-count cap would make that batch a parse error even
    # though every frame in it is well-formed.
    frames = b"".join(serialize_frame(FrameType.PING, 0, b"") for _ in range(20_000))

    parsed, consumed = parse_frames(frames)

    assert consumed == len(frames)
    assert len(parsed) == 20_000


def test_window_frame_round_trips_as_four_byte_big_endian_delta():
    wire = serialize_frame(FrameType.WINDOW, 1, (256 * 1024).to_bytes(4, "big"))

    frame = parse_frame_message(wire)[0]

    assert frame.type == FrameType.WINDOW
    assert int.from_bytes(frame.payload, "big") == 256 * 1024
