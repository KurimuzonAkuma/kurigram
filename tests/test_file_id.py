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

import struct

import pytest

from pyrogram.file_id import (
    FILE_REFERENCE_FLAG,
    FileId,
    FileUniqueId,
    FileType,
    FileUniqueType,
    ThumbnailSource,
    b64_encode,
    rle_encode,
)
from pyrogram.raw.core import Bytes

# Arbitrary, only has to survive the round trip.
DC_ID = 2
MEDIA_ID = 5399953792058913798
ACCESS_HASH = 478576178729576621
FILE_REFERENCE = b"\x01\x02\x03\x04"

VOLUME_ID = 1234567890123456789
LOCAL_ID = 42
SECRET = 987654321098765432
CHAT_ID = -1001234567890
CHAT_ACCESS_HASH = 1122334455667788990
STICKER_SET_ID = 2233445566778899001
STICKER_SET_ACCESS_HASH = 3344556677889900112
STICKER_SET_VERSION = 7


def photo_file_id(*, minor: int, thumbnail_source: int, tail: bytes) -> str:
    """Assemble a photo file id byte for byte the way TDLib's `FullRemoteFileLocation::store` does.

    Built by hand rather than through `FileId.encode()`, so that what a case asserts is the layout
    TDLib writes and not merely that our own two halves agree with each other.
    """
    payload = (
        struct.pack("<ii", FileType.PHOTO | FILE_REFERENCE_FLAG, DC_ID)
        + Bytes(FILE_REFERENCE)
        + struct.pack("<qq", MEDIA_ID, ACCESS_HASH)
        + struct.pack("<i", thumbnail_source)
        + tail
        + struct.pack("<bb", minor, 4)
    )

    return b64_encode(rle_encode(payload))


def check(file_id: str, expected_file_type: FileType):
    decoded = FileId.decode(file_id)

    assert decoded.file_type == expected_file_type
    assert decoded.encode() == file_id


def check_unique(file_unique_id: str, expected_file_unique_type: FileUniqueType):
    decoded = FileUniqueId.decode(file_unique_id)

    assert decoded.file_unique_type == expected_file_unique_type
    assert decoded.encode() == file_unique_id


def test_audio():
    audio = "CQACAgIAAx0CAAGgr9AAAgmQX7b4XPBstC1fFUuJBooHTHFd7HMAAgUAA4GkuUnVOGG5P196yR4E"
    audio_unique = "AgADBQADgaS5SQ"
    audio_thumb = "AAMCAgADHQIAAaCv0AACCZBftvhc8Gy0LV8VS4kGigdMcV3scwACBQADgaS5SdU4Ybk_X3rJIH3qihAAAwEAB20AA_OeAQABHgQ"
    audio_thumb_unique = "AQADIH3qihAAA_OeAQAB"

    check(audio, FileType.AUDIO)
    check_unique(audio_unique, FileUniqueType.DOCUMENT)
    check(audio_thumb, FileType.THUMBNAIL)
    check_unique(audio_thumb_unique, FileUniqueType.PHOTO)


def test_video():
    video = "BAACAgIAAx0CAAGgr9AAAgmRX7b4Xv9f-4BK5VR_5ppIOF6UIp0AAgYAA4GkuUmhnZz2xC37wR4E"
    video_unique = "AgADBgADgaS5SQ"
    video_thumb = "AAMCAgADHQIAAaCv0AACCZFftvhe_1_7gErlVH_mmkg4XpQinQACBgADgaS5SaGdnPbELfvBIH3qihAAAwEAB20AA_WeAQABHgQ"
    video_thumb_unique = "AQADIH3qihAAA_WeAQAB"

    check(video, FileType.VIDEO)
    check_unique(video_unique, FileUniqueType.DOCUMENT)
    check(video_thumb, FileType.THUMBNAIL)
    check_unique(video_thumb_unique, FileUniqueType.PHOTO)


def test_document():
    document = "BQACAgIAAx0CAAGgr9AAAgmPX7b4UxbjNoFEO_L0I4s6wrXNJA8AAgQAA4GkuUm9FFvIaOhXWR4E"
    document_unique = "AgADBAADgaS5SQ"
    document_thumb = "AAMCAgADHQIAAaCv0AACCY9ftvhTFuM2gUQ78vQjizrCtc0kDwACBAADgaS5Sb0UW8ho6FdZIH3qihAAAwEAB3MAA_GeAQABHgQ"
    document_thumb_unique = "AQADIH3qihAAA_GeAQAB"

    check(document, FileType.DOCUMENT)
    check_unique(document_unique, FileUniqueType.DOCUMENT)
    check(document_thumb, FileType.THUMBNAIL)
    check_unique(document_thumb_unique, FileUniqueType.PHOTO)


def test_animation():
    animation = "CgACAgIAAx0CAAGgr9AAAgmSX7b4Y2g8_QW2XFd49iUmRnHOyG8AAgcAA4GkuUnry9gWDzF_5R4E"
    animation_unique = "AgADBwADgaS5SQ"

    check(animation, FileType.ANIMATION)
    check_unique(animation_unique, FileUniqueType.DOCUMENT)


def test_voice():
    voice = "AwACAgIAAx0CAAGgr9AAAgmUX7b4c1KQyHVwzffxC2EnSYWsMAQAAgkAA4GkuUlsZUZ4_I97AR4E"
    voice_unique = "AgADCQADgaS5SQ"

    check(voice, FileType.VOICE)
    check_unique(voice_unique, FileUniqueType.DOCUMENT)


def test_video_note():
    video_note = "DQACAgIAAx0CAAGgr9AAAgmVX7b53qrRzCEO13BaLQJaYuFbdlwAAgoAA4GkuUmlqIzDy_PCsx4E"
    video_note_unique = "AgADCgADgaS5SQ"
    video_note_thumb = "AAMCAgADHQIAAaCv0AACCZVftvneqtHMIQ7XcFotAlpi4Vt2XAACCgADgaS5SaWojMPL88KzIH3qihAAAwEAB20AA_meAQABHgQ"
    video_note_thumb_unique = "AQADIH3qihAAA_meAQAB"

    check(video_note, FileType.VIDEO_NOTE)
    check_unique(video_note_unique, FileUniqueType.DOCUMENT)
    check(video_note_thumb, FileType.THUMBNAIL)
    check_unique(video_note_thumb_unique, FileUniqueType.PHOTO)


def test_sticker():
    sticker = "CAACAgEAAx0CAAGgr9AAAgmWX7b6uFeLlhXEgYrM8pIbGaQKRQ0AAswBAALjeAQAAbeooNv_tb6-HgQ"
    sticker_unique = "AgADzAEAAuN4BAAB"
    sticker_thumb = "AAMCAQADHQIAAaCv0AACCZZftvq4V4uWFcSBiszykhsZpApFDQACzAEAAuN4BAABt6ig2_-1vr5gWNkpAAQBAAdtAAM0BQACHgQ"
    sticker_thumb_unique = "AQADYFjZKQAENAUAAg"

    check(sticker, FileType.STICKER)
    check_unique(sticker_unique, FileUniqueType.DOCUMENT)
    check(sticker_thumb, FileType.THUMBNAIL)
    check_unique(sticker_thumb_unique, FileUniqueType.PHOTO)


def test_photo():
    photo_small = "AgACAgIAAx0CAAGgr9AAAgmZX7b7IPLRl8NcV3EJkzHwI1gwT-oAAq2nMRuBpLlJPJY-URZfhTkgfeqKEAADAQADAgADbQADAZ8BAAEeBA"
    photo_small_unique = "AQADIH3qihAAAwGfAQAB"
    photo_medium = "AgACAgIAAx0CAAGgr9AAAgmZX7b7IPLRl8NcV3EJkzHwI1gwT-oAAq2nMRuBpLlJPJY-URZfhTkgfeqKEAADAQADAgADeAADAp8BAAEeBA"
    photo_medium_unique = "AQADIH3qihAAAwKfAQAB"
    photo_big = "AgACAgIAAx0CAAGgr9AAAgmZX7b7IPLRl8NcV3EJkzHwI1gwT-oAAq2nMRuBpLlJPJY-URZfhTkgfeqKEAADAQADAgADeQAD_54BAAEeBA"
    photo_big_unique = "AQADIH3qihAAA_-eAQAB"

    check(photo_small, FileType.PHOTO)
    check_unique(photo_small_unique, FileUniqueType.PHOTO)
    check(photo_medium, FileType.PHOTO)
    check_unique(photo_medium_unique, FileUniqueType.PHOTO)
    check(photo_big, FileType.PHOTO)
    check_unique(photo_big_unique, FileUniqueType.PHOTO)


def test_chat_photo():
    user_photo_small = "AQADAgADrKcxGylBBQAJIH3qihAAAwIAAylBBQAF7bDHYwABnc983KcAAh4E"
    user_photo_small_unique = "AQADIH3qihAAA9ynAAI"
    user_photo_big = "AQADAgADrKcxGylBBQAJIH3qihAAAwMAAylBBQAF7bDHYwABnc983qcAAh4E"
    user_photo_big_unique = "AQADIH3qihAAA96nAAI"

    chat_photo_small = "AQADAgATIH3qihAAAwIAA3t3-P______AAjhngEAAR4E"
    chat_photo_small_unique = "AQADIH3qihAAA-GeAQAB"
    chat_photo_big = "AQADAgATIH3qihAAAwMAA3t3-P______AAjjngEAAR4E"
    chat_photo_big_unique = "AQADIH3qihAAA-OeAQAB"

    channel_photo_small = "AQADAgATIH3qihAAAwIAA-fFwCoX____MvARg8nvpc3RpwACHgQ"
    channel_photo_small_unique = "AQADIH3qihAAA9GnAAI"
    channel_photo_big = "AQADAgATIH3qihAAAwMAA-fFwCoX____MvARg8nvpc3TpwACHgQ"
    channel_photo_big_unique = "AQADIH3qihAAA9OnAAI"

    check(user_photo_small, FileType.CHAT_PHOTO)
    check_unique(user_photo_small_unique, FileUniqueType.PHOTO)
    check(user_photo_big, FileType.CHAT_PHOTO)
    check_unique(user_photo_big_unique, FileUniqueType.PHOTO)

    check(chat_photo_small, FileType.CHAT_PHOTO)
    check_unique(chat_photo_small_unique, FileUniqueType.PHOTO)
    check(chat_photo_big, FileType.CHAT_PHOTO)
    check_unique(chat_photo_big_unique, FileUniqueType.PHOTO)

    check(channel_photo_small, FileType.CHAT_PHOTO)
    check_unique(channel_photo_small_unique, FileUniqueType.PHOTO)
    check(channel_photo_big, FileType.CHAT_PHOTO)
    check_unique(channel_photo_big_unique, FileUniqueType.PHOTO)


def test_old_file_id():
    old = "BQADBAADQNKSZqjl5DcROGn_eu5JtgAEAgAEAg"
    check(old, FileType.DOCUMENT)


def test_unknown_file_type():
    unknown = "RQACAgIAAx0CAAGgr9AAAgmPX7b4UxbjNoFEO_L0I4s6wrXNJA8AAgQAA4GkuUm9FFvIaOhXWR4E"

    with pytest.raises(ValueError, match=r"Unknown file_type \d+ of file_id \w+"):
        check(unknown, FileType.DOCUMENT)


def test_unknown_thumbnail_source():
    unknown = "AAMCAgADHQIAAaCv0AACCY9ftvhTFuM2gUQ78vQjizrCtc0kDwACBAADgaS5Sb0UW8ho6FdZIH3qihAAA6QBAAIeBA"

    with pytest.raises(ValueError, match=r"Unknown thumbnail_source \d+ of file_id \w+"):
        check(unknown, FileType.THUMBNAIL)


def test_photo_from_a_current_client():
    """The file id from #178, minted at minor 54, which `decode()` used to reject.

    Twelve bytes trail `access_hash`: `01000000 02000000 6d000000`. Read against the pre-32 layout
    the first eight become `volume_id` and `6d000000` becomes the source, hence the reported
    `ValueError: Unknown thumbnail_source 109`. Read against the current one they are the source,
    the thumbnail's own file type, and `chr(109)` — the size letter `m`.
    """
    photo = "AgACAgIAAxkBAAIENGfeY4AfRquwTL2LpDrzqvFMVNt_AAIG9DEbXX3wSq3oI7t_PqQGAQADAgADbQADNgQ"

    decoded = FileId.decode(photo)

    assert decoded.minor == 54
    assert decoded.thumbnail_source == ThumbnailSource.THUMBNAIL
    assert decoded.thumbnail_file_type == FileType.PHOTO
    assert decoded.thumbnail_size == "m"
    assert decoded.volume_id is None
    assert decoded.local_id is None

    check(photo, FileType.PHOTO)


NEW_LAYOUT_SOURCES = [
    pytest.param(
        ThumbnailSource.LEGACY,
        struct.pack("<q", SECRET),
        {"secret": SECRET},
        id="legacy",
    ),
    pytest.param(
        ThumbnailSource.THUMBNAIL,
        struct.pack("<ii", FileType.PHOTO, ord("m")),
        {"thumbnail_file_type": FileType.PHOTO, "thumbnail_size": "m"},
        id="thumbnail",
    ),
    pytest.param(
        ThumbnailSource.CHAT_PHOTO_SMALL,
        struct.pack("<qq", CHAT_ID, CHAT_ACCESS_HASH),
        {"chat_id": CHAT_ID, "chat_access_hash": CHAT_ACCESS_HASH},
        id="chat_photo_small",
    ),
    pytest.param(
        ThumbnailSource.CHAT_PHOTO_BIG,
        struct.pack("<qq", CHAT_ID, CHAT_ACCESS_HASH),
        {"chat_id": CHAT_ID, "chat_access_hash": CHAT_ACCESS_HASH},
        id="chat_photo_big",
    ),
    pytest.param(
        ThumbnailSource.STICKER_SET_THUMBNAIL,
        struct.pack("<qq", STICKER_SET_ID, STICKER_SET_ACCESS_HASH),
        {"sticker_set_id": STICKER_SET_ID, "sticker_set_access_hash": STICKER_SET_ACCESS_HASH},
        id="sticker_set_thumbnail",
    ),
    pytest.param(
        ThumbnailSource.FULL_LEGACY,
        struct.pack("<qqi", VOLUME_ID, SECRET, LOCAL_ID),
        {"volume_id": VOLUME_ID, "secret": SECRET, "local_id": LOCAL_ID},
        id="full_legacy",
    ),
    pytest.param(
        ThumbnailSource.CHAT_PHOTO_SMALL_LEGACY,
        struct.pack("<qqqi", CHAT_ID, CHAT_ACCESS_HASH, VOLUME_ID, LOCAL_ID),
        {
            "chat_id": CHAT_ID,
            "chat_access_hash": CHAT_ACCESS_HASH,
            "volume_id": VOLUME_ID,
            "local_id": LOCAL_ID,
        },
        id="chat_photo_small_legacy",
    ),
    pytest.param(
        ThumbnailSource.CHAT_PHOTO_BIG_LEGACY,
        struct.pack("<qqqi", CHAT_ID, CHAT_ACCESS_HASH, VOLUME_ID, LOCAL_ID),
        {
            "chat_id": CHAT_ID,
            "chat_access_hash": CHAT_ACCESS_HASH,
            "volume_id": VOLUME_ID,
            "local_id": LOCAL_ID,
        },
        id="chat_photo_big_legacy",
    ),
    pytest.param(
        ThumbnailSource.STICKER_SET_THUMBNAIL_LEGACY,
        struct.pack("<qqqi", STICKER_SET_ID, STICKER_SET_ACCESS_HASH, VOLUME_ID, LOCAL_ID),
        {
            "sticker_set_id": STICKER_SET_ID,
            "sticker_set_access_hash": STICKER_SET_ACCESS_HASH,
            "volume_id": VOLUME_ID,
            "local_id": LOCAL_ID,
        },
        id="sticker_set_thumbnail_legacy",
    ),
    pytest.param(
        ThumbnailSource.STICKER_SET_THUMBNAIL_VERSION,
        struct.pack("<qqi", STICKER_SET_ID, STICKER_SET_ACCESS_HASH, STICKER_SET_VERSION),
        {
            "sticker_set_id": STICKER_SET_ID,
            "sticker_set_access_hash": STICKER_SET_ACCESS_HASH,
            "sticker_set_version": STICKER_SET_VERSION,
        },
        id="sticker_set_thumbnail_version",
    ),
]


@pytest.mark.parametrize("thumbnail_source, tail, expected", NEW_LAYOUT_SOURCES)
def test_every_source_of_the_current_layout(thumbnail_source, tail, expected):
    file_id = photo_file_id(minor=32, thumbnail_source=thumbnail_source, tail=tail)

    decoded = FileId.decode(file_id)

    assert decoded.thumbnail_source == thumbnail_source
    assert decoded.media_id == MEDIA_ID
    assert decoded.access_hash == ACCESS_HASH
    assert decoded.file_reference == FILE_REFERENCE

    assert {name: vars(decoded)[name] for name in expected} == expected
    assert decoded.encode() == file_id


def test_the_pre_32_layout_still_reads_as_before():
    """Minor 31 keeps `volume_id` ahead of the source and `local_id` after every tail."""
    payload = (
        struct.pack("<ii", FileType.PHOTO | FILE_REFERENCE_FLAG, DC_ID)
        + Bytes(FILE_REFERENCE)
        + struct.pack("<qq", MEDIA_ID, ACCESS_HASH)
        + struct.pack("<q", VOLUME_ID)
        + struct.pack("<i", ThumbnailSource.CHAT_PHOTO_SMALL)
        + struct.pack("<qq", CHAT_ID, CHAT_ACCESS_HASH)
        + struct.pack("<i", LOCAL_ID)
        + struct.pack("<bb", 31, 4)
    )
    file_id = b64_encode(rle_encode(payload))

    decoded = FileId.decode(file_id)

    assert decoded.volume_id == VOLUME_ID
    assert decoded.local_id == LOCAL_ID
    assert decoded.chat_id == CHAT_ID
    assert decoded.chat_access_hash == CHAT_ACCESS_HASH
    assert decoded.encode() == file_id


def test_the_library_still_mints_the_layout_it_always_did():
    """`FileId.MINOR` is untouched, so nothing this library hands out changes shape.

    Every file id built by `types/` passes `volume_id=0, local_id=0` because the pre-32 layout has
    nowhere to omit them. Should `MINOR` ever be raised past 32, those two arguments become dead and
    this test is the one that says so.
    """
    minted = FileId(
        file_type=FileType.PHOTO,
        dc_id=DC_ID,
        media_id=MEDIA_ID,
        access_hash=ACCESS_HASH,
        file_reference=FILE_REFERENCE,
        thumbnail_source=ThumbnailSource.THUMBNAIL,
        thumbnail_file_type=FileType.PHOTO,
        thumbnail_size="m",
        volume_id=0,
        local_id=0,
    ).encode()

    decoded = FileId.decode(minted)

    assert decoded.minor == 30
    assert decoded.volume_id == 0
    assert decoded.local_id == 0
    assert decoded.encode() == minted


def test_full_legacy_keeps_secret_between_volume_id_and_local_id():
    """The field order here is TDLib's `FullLegacy::store`, not the schema's.

    `inputPhotoLegacyFileLocation` lists the same three as `volume_id local_id secret`, so reading
    the schema alone would swap the last two and silently produce a wrong `local_id`.
    """
    file_id = photo_file_id(
        minor=32,
        thumbnail_source=ThumbnailSource.FULL_LEGACY,
        tail=struct.pack("<qqi", VOLUME_ID, SECRET, LOCAL_ID),
    )

    decoded = FileId.decode(file_id)

    assert decoded.volume_id == VOLUME_ID
    assert decoded.secret == SECRET
    assert decoded.local_id == LOCAL_ID


def test_a_source_past_the_known_ones_is_still_rejected():
    """Nine is the last source TDLib defines; ten has to stay an error rather than a bad read."""
    file_id = photo_file_id(minor=32, thumbnail_source=10, tail=struct.pack("<q", SECRET))

    with pytest.raises(ValueError, match=r"Unknown thumbnail_source 10 of file_id \w+"):
        FileId.decode(file_id)


def test_documents_are_unaffected_by_the_photo_layout():
    """Only `PHOTO_TYPES` carry a source, so a document must read the same at any minor."""
    for minor in (30, 32, 54):
        payload = (
            struct.pack("<ii", FileType.DOCUMENT | FILE_REFERENCE_FLAG, DC_ID)
            + Bytes(FILE_REFERENCE)
            + struct.pack("<qq", MEDIA_ID, ACCESS_HASH)
            + struct.pack("<bb", minor, 4)
        )
        file_id = b64_encode(rle_encode(payload))

        decoded = FileId.decode(file_id)

        assert decoded.file_type == FileType.DOCUMENT
        assert decoded.media_id == MEDIA_ID
        assert decoded.access_hash == ACCESS_HASH
        assert decoded.volume_id is None
        assert decoded.encode() == file_id


EXTREMES = [0, 1, -1, 2 ** 62, -(2 ** 62), 2 ** 63 - 1, -(2 ** 63)]

# `local_id` is an int32 and TDLib notes it can be negative in secret chat thumbnails.
SMALL_EXTREMES = [0, 1, -1, 2 ** 31 - 1, -(2 ** 31)]


def photo_fields(*, thumbnail_source: ThumbnailSource, big: int, small: int) -> dict:
    """The fields a given source carries, filled with one value each."""
    if thumbnail_source == ThumbnailSource.LEGACY:
        return {"secret": big}

    if thumbnail_source == ThumbnailSource.THUMBNAIL:
        return {"thumbnail_file_type": FileType.PHOTO, "thumbnail_size": "y"}

    if thumbnail_source in (ThumbnailSource.CHAT_PHOTO_SMALL, ThumbnailSource.CHAT_PHOTO_BIG):
        return {"chat_id": big, "chat_access_hash": big}

    if thumbnail_source == ThumbnailSource.STICKER_SET_THUMBNAIL:
        return {"sticker_set_id": big, "sticker_set_access_hash": big}

    if thumbnail_source == ThumbnailSource.FULL_LEGACY:
        return {"volume_id": big, "secret": big, "local_id": small}

    if thumbnail_source in (
        ThumbnailSource.CHAT_PHOTO_SMALL_LEGACY,
        ThumbnailSource.CHAT_PHOTO_BIG_LEGACY
    ):
        return {"chat_id": big, "chat_access_hash": big, "volume_id": big, "local_id": small}

    if thumbnail_source == ThumbnailSource.STICKER_SET_THUMBNAIL_LEGACY:
        return {
            "sticker_set_id": big,
            "sticker_set_access_hash": big,
            "volume_id": big,
            "local_id": small,
        }

    return {"sticker_set_id": big, "sticker_set_access_hash": big, "sticker_set_version": small}


@pytest.mark.parametrize("thumbnail_source", list(ThumbnailSource))
def test_every_source_survives_a_round_trip_at_its_extremes(thumbnail_source):
    """Encode, decode, encode again for every source against the widest values each field holds.

    The hand-built fixtures pin the layout; this pins the widths. A `<q` typed as `<i` somewhere
    still round trips small numbers and only shows up at the ends of the range.
    """
    for big, small in zip(EXTREMES, SMALL_EXTREMES * 2):
        # Before minor 32 every source shared one layout, and the ones added for it cannot occur.
        minors = [32] if thumbnail_source >= ThumbnailSource.FULL_LEGACY else [30, 32]

        for minor in minors:
            fields = photo_fields(thumbnail_source=thumbnail_source, big=big, small=small)

            if minor < 32:
                fields.setdefault("volume_id", big)
                fields.setdefault("local_id", small)

            file_id = FileId(
                minor=minor,
                file_type=FileType.PHOTO,
                dc_id=DC_ID,
                media_id=MEDIA_ID,
                access_hash=ACCESS_HASH,
                file_reference=FILE_REFERENCE,
                thumbnail_source=thumbnail_source,
                **fields,
            ).encode()

            decoded = FileId.decode(file_id)

            assert decoded.minor == minor
            assert decoded.thumbnail_source == thumbnail_source

            assert {name: vars(decoded)[name] for name in fields} == fields, thumbnail_source.name
            assert decoded.encode() == file_id


def test_stringify_file_id():
    file_id = "BQACAgIAAx0CAAGgr9AAAgmPX7b4UxbjNoFEO_L0I4s6wrXNJA8AAgQAA4GkuUm9FFvIaOhXWR4E"
    string = "{'major': 4, 'minor': 30, 'file_type': <FileType.DOCUMENT: 5>, 'dc_id': 2, " \
             "'file_reference': b'\\x02\\x00\\xa0\\xaf\\xd0\\x00\\x00\\t\\x8f_\\xb6\\xf8S\\x16\\xe36\\x81D;\\xf2\\xf4#\\x8b:\\xc2\\xb5\\xcd$\\x0f', " \
             "'media_id': 5312458109417947140, 'access_hash': 6437869729085068477, 'thumbnail_size': ''}"

    assert str(FileId.decode(file_id)) == string


def test_stringify_file_unique_id():
    file_unique_id = "AgADBAADgaS5SQ"
    string = "{'file_unique_type': <FileUniqueType.DOCUMENT: 2>, 'media_id': 5312458109417947140}"

    assert str(FileUniqueId.decode(file_unique_id)) == string
