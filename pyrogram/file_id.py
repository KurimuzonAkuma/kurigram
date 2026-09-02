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
import logging
import struct
from dataclasses import dataclass, replace
from enum import IntEnum
from io import BytesIO
from typing import Final, List, Optional

from pyrogram.raw.core import Bytes, String

log = logging.getLogger(__name__)


def b64_encode(s: bytes) -> str:
    """Encode bytes into a URL-safe Base64 string without padding

    Parameters:
        s (``bytes``):
            Bytes to encode

    Returns:
        ``str``: The encoded bytes
    """
    return base64.urlsafe_b64encode(s).decode().strip("=")


def b64_decode(s: str) -> bytes:
    """Decode a URL-safe Base64 string without padding to bytes

    Parameters:
        s (``str``):
            String to decode

    Returns:
        ``bytes``: The decoded string
    """
    return base64.urlsafe_b64decode(s + "=" * (-len(s) % 4))


def rle_encode(s: bytes) -> bytes:
    """Zero-value RLE encoder

    Parameters:
        s (``bytes``):
            Bytes to encode

    Returns:
        ``bytes``: The encoded bytes
    """
    r: List[int] = []
    n: int = 0

    for b in s:
        if not b:
            n += 1
        else:
            if n:
                r.extend((0, n))
                n = 0

            r.append(b)

    if n:
        r.extend((0, n))

    return bytes(r)


def rle_decode(s: bytes) -> bytes:
    """Zero-value RLE decoder

    Parameters:
        s (``bytes``):
            Bytes to decode

    Returns:
        ``bytes``: The decoded bytes
    """
    r: List[int] = []
    z: bool = False

    for b in s:
        if not b:
            z = True
            continue

        if z:
            r.extend((0,) * b)
            z = False
        else:
            r.append(b)

    return bytes(r)


class FileType(IntEnum):
    """Known file types"""
    THUMBNAIL = 0
    CHAT_PHOTO = 1  # ProfilePhoto
    PHOTO = 2
    VOICE = 3  # VoiceNote
    VIDEO = 4
    DOCUMENT = 5
    ENCRYPTED = 6
    TEMP = 7
    STICKER = 8
    AUDIO = 9
    ANIMATION = 10
    ENCRYPTED_THUMBNAIL = 11
    WALLPAPER = 12
    VIDEO_NOTE = 13
    SECURE_RAW = 14
    SECURE = 15
    BACKGROUND = 16
    DOCUMENT_AS_FILE = 17


class ThumbnailSource(IntEnum):
    """Known thumbnail sources.

    TDLib mints the file ids, so its ``PhotoSizeSource`` is the authority on the values:
    https://github.com/tdlib/td/blob/master/td/telegram/PhotoSizeSource.h
    """
    LEGACY = 0
    THUMBNAIL = 1
    CHAT_PHOTO_SMALL = 2  # DialogPhotoSmall
    CHAT_PHOTO_BIG = 3  # DialogPhotoBig
    STICKER_SET_THUMBNAIL = 4
    FULL_LEGACY = 5
    CHAT_PHOTO_SMALL_LEGACY = 6  # DialogPhotoSmallLegacy
    CHAT_PHOTO_BIG_LEGACY = 7  # DialogPhotoBigLegacy
    STICKER_SET_THUMBNAIL_LEGACY = 8
    STICKER_SET_THUMBNAIL_VERSION = 9


# TDLib's `Version::RemovePhotoVolumeAndLocalId`, the minor version from which photo file ids
#  carry neither `volume_id` nor `local_id`, the sources that still need them having become
#  values 5 to 9 above. Reading a current file id against the older layout takes the source tag
#  for `volume_id` and part of the tail for the source:
#
#    FileId.decode("AgACAgIAAxkBAAIENGfeY4AfRquwTL2LpDrzqvFMVNt_AAIG9DEbXX3wSq3o"
#                  "I7t_PqQGAQADAgADbQADNgQ")
#    # -> ValueError: Unknown thumbnail_source 109 of file_id AgACAgI...
#
#  https://github.com/tdlib/td/blob/master/td/telegram/files/FileLocation.hpp
NO_VOLUME_AND_LOCAL_ID_MINOR: Final[int] = 32


# Photo-like file ids are longer and contain extra info, the rest are all documents
PHOTO_TYPES = {FileType.THUMBNAIL, FileType.CHAT_PHOTO, FileType.PHOTO, FileType.WALLPAPER,
               FileType.ENCRYPTED_THUMBNAIL}
DOCUMENT_TYPES = set(FileType) - PHOTO_TYPES

# Since the file type values are small enough to fit them in few bits, Telegram thought it would be a good idea to
# encode extra information about web url and file reference existence as flag inside the 4 bytes allocated for the field
WEB_LOCATION_FLAG = 1 << 24
FILE_REFERENCE_FLAG = 1 << 25


@dataclass(frozen=True)
class PhotoTail:
    """What a photo file id carries after its source tag, one field per `FileId` argument.

    Which of them are filled is decided by the source; the rest keep the default `FileId` gives them.
    """
    volume_id: Optional[int] = None
    local_id: Optional[int] = None
    secret: Optional[int] = None
    thumbnail_file_type: Optional[int] = None
    thumbnail_size: str = ""
    chat_id: Optional[int] = None
    chat_access_hash: Optional[int] = None
    sticker_set_id: Optional[int] = None
    sticker_set_access_hash: Optional[int] = None
    sticker_set_version: Optional[int] = None


def read_photo_tail(buffer: BytesIO, *, thumbnail_source: ThumbnailSource) -> PhotoTail:
    """Each layout is the matching `store()` in TDLib's `PhotoSizeSource.hpp` read backwards.

    https://github.com/tdlib/td/blob/master/td/telegram/PhotoSizeSource.hpp
    """
    if thumbnail_source == ThumbnailSource.LEGACY:
        secret, = struct.unpack("<q", buffer.read(8))

        return PhotoTail(secret=secret)

    # `thumbnail_size` is the `type` of the `PhotoSize` the file id points at: one letter,
    #  whose character code the file id stores as an int32 while
    #  `inputPhotoFileLocation.thumb_size` takes a `string`. It is a `str` from here on:
    #  `chr()` in, `ord()` back out in `write_photo_tail()`, `get_file()` passes it through.
    #
    #  What the letters mean: https://core.telegram.org/api/files#image-thumbnail-types, and
    #  the same table with the order Telegram Desktop picks them in:
    #  https://github.com/telegramdesktop/tdesktop/blob/8e18cb71103d83d7d98994ff27f0a2bca55c489c/Telegram/SourceFiles/data/data_session.cpp#L102-L114
    if thumbnail_source == ThumbnailSource.THUMBNAIL:
        thumbnail_file_type, thumbnail_size = struct.unpack("<ii", buffer.read(8))

        return PhotoTail(thumbnail_file_type=thumbnail_file_type, thumbnail_size=chr(thumbnail_size))

    if thumbnail_source in (ThumbnailSource.CHAT_PHOTO_SMALL, ThumbnailSource.CHAT_PHOTO_BIG):
        chat_id, chat_access_hash = struct.unpack("<qq", buffer.read(16))

        return PhotoTail(chat_id=chat_id, chat_access_hash=chat_access_hash)

    if thumbnail_source == ThumbnailSource.STICKER_SET_THUMBNAIL:
        sticker_set_id, sticker_set_access_hash = struct.unpack("<qq", buffer.read(16))

        return PhotoTail(sticker_set_id=sticker_set_id, sticker_set_access_hash=sticker_set_access_hash)

    # `secret` sits between the other two, where `inputPhotoLegacyFileLocation` lists them as
    #  `volume_id local_id secret`. The file id follows `FullLegacy::store`, not the schema.
    if thumbnail_source == ThumbnailSource.FULL_LEGACY:
        volume_id, secret, local_id = struct.unpack("<qqi", buffer.read(20))

        return PhotoTail(volume_id=volume_id, secret=secret, local_id=local_id)

    if thumbnail_source in (ThumbnailSource.CHAT_PHOTO_SMALL_LEGACY, ThumbnailSource.CHAT_PHOTO_BIG_LEGACY):
        chat_id, chat_access_hash, volume_id, local_id = struct.unpack("<qqqi", buffer.read(28))

        return PhotoTail(
            chat_id=chat_id,
            chat_access_hash=chat_access_hash,
            volume_id=volume_id,
            local_id=local_id
        )

    if thumbnail_source == ThumbnailSource.STICKER_SET_THUMBNAIL_LEGACY:
        sticker_set_id, sticker_set_access_hash, volume_id, local_id = struct.unpack("<qqqi", buffer.read(28))

        return PhotoTail(
            sticker_set_id=sticker_set_id,
            sticker_set_access_hash=sticker_set_access_hash,
            volume_id=volume_id,
            local_id=local_id
        )

    if thumbnail_source == ThumbnailSource.STICKER_SET_THUMBNAIL_VERSION:
        sticker_set_id, sticker_set_access_hash, sticker_set_version = struct.unpack("<qqi", buffer.read(20))

        return PhotoTail(
            sticker_set_id=sticker_set_id,
            sticker_set_access_hash=sticker_set_access_hash,
            sticker_set_version=sticker_set_version
        )

    msg = f"No layout for thumbnail_source: {thumbnail_source!r}"
    raise ValueError(msg)


def write_photo_tail(file_id: "FileId") -> bytes:
    """The counterpart of `read_photo_tail()`: same layout per source, same order."""
    if file_id.thumbnail_source == ThumbnailSource.LEGACY:
        return struct.pack("<q", file_id.secret)

    if file_id.thumbnail_source == ThumbnailSource.THUMBNAIL:
        return struct.pack("<ii", file_id.thumbnail_file_type, ord(file_id.thumbnail_size))

    if file_id.thumbnail_source in (ThumbnailSource.CHAT_PHOTO_SMALL, ThumbnailSource.CHAT_PHOTO_BIG):
        return struct.pack("<qq", file_id.chat_id, file_id.chat_access_hash)

    if file_id.thumbnail_source == ThumbnailSource.STICKER_SET_THUMBNAIL:
        return struct.pack("<qq", file_id.sticker_set_id, file_id.sticker_set_access_hash)

    if file_id.thumbnail_source == ThumbnailSource.FULL_LEGACY:
        return struct.pack("<qqi", file_id.volume_id, file_id.secret, file_id.local_id)

    if file_id.thumbnail_source in (ThumbnailSource.CHAT_PHOTO_SMALL_LEGACY, ThumbnailSource.CHAT_PHOTO_BIG_LEGACY):
        return struct.pack("<qqqi", file_id.chat_id, file_id.chat_access_hash, file_id.volume_id, file_id.local_id)

    if file_id.thumbnail_source == ThumbnailSource.STICKER_SET_THUMBNAIL_LEGACY:
        return struct.pack(
            "<qqqi",
            file_id.sticker_set_id,
            file_id.sticker_set_access_hash,
            file_id.volume_id,
            file_id.local_id
        )

    if file_id.thumbnail_source == ThumbnailSource.STICKER_SET_THUMBNAIL_VERSION:
        return struct.pack(
            "<qqi",
            file_id.sticker_set_id,
            file_id.sticker_set_access_hash,
            file_id.sticker_set_version
        )

    msg = f"No layout for thumbnail_source: {file_id.thumbnail_source!r}"
    raise ValueError(msg)


class FileId:
    MAJOR = 4
    MINOR = 30

    def __init__(
        self, *,
        major: int = MAJOR,
        minor: int = MINOR,
        file_type: FileType,
        dc_id: int,
        file_reference: bytes = b"",
        url: Optional[str] = None,
        media_id: Optional[int] = None,
        access_hash: Optional[int] = None,
        volume_id: Optional[int] = None,
        thumbnail_source: Optional[ThumbnailSource] = None,
        thumbnail_file_type: Optional[FileType] = None,
        thumbnail_size: str = "",
        secret: Optional[int] = None,
        local_id: Optional[int] = None,
        chat_id: Optional[int] = None,
        chat_access_hash: Optional[int] = None,
        sticker_set_id: Optional[int] = None,
        sticker_set_access_hash: Optional[int] = None,
        sticker_set_version: Optional[int] = None
    ):
        self.major = major
        self.minor = minor
        self.file_type = file_type
        self.dc_id = dc_id
        self.file_reference = file_reference
        self.url = url
        self.media_id = media_id
        self.access_hash = access_hash
        self.volume_id = volume_id
        self.thumbnail_source = thumbnail_source
        self.thumbnail_file_type = thumbnail_file_type
        self.thumbnail_size = thumbnail_size
        self.secret = secret
        self.local_id = local_id
        self.chat_id = chat_id
        self.chat_access_hash = chat_access_hash
        self.sticker_set_id = sticker_set_id
        self.sticker_set_access_hash = sticker_set_access_hash
        self.sticker_set_version = sticker_set_version

    @staticmethod
    def decode(file_id: str):
        decoded = rle_decode(b64_decode(file_id))

        # region read version
        # File id versioning. Major versions lower than 4 don't have a minor version
        major = decoded[-1]

        if major < 4:
            minor = 0
            buffer = BytesIO(decoded[:-1])
        else:
            minor = decoded[-2]
            buffer = BytesIO(decoded[:-2])
        # endregion

        file_type, dc_id = struct.unpack("<ii", buffer.read(8))

        # region media type flags
        # Check for flags existence
        has_web_location = bool(file_type & WEB_LOCATION_FLAG)
        has_file_reference = bool(file_type & FILE_REFERENCE_FLAG)

        # Remove flags to restore the actual type id value
        file_type &= ~WEB_LOCATION_FLAG
        file_type &= ~FILE_REFERENCE_FLAG
        # endregion

        try:
            file_type = FileType(file_type)
        except ValueError:
            raise ValueError(f"Unknown file_type {file_type} of file_id {file_id}")

        if has_web_location:
            url = String.read(buffer)
            access_hash, = struct.unpack("<q", buffer.read(8))

            return FileId(
                major=major,
                minor=minor,
                file_type=file_type,
                dc_id=dc_id,
                url=url,
                access_hash=access_hash
            )

        file_reference = Bytes.read(buffer) if has_file_reference else b""
        media_id, access_hash = struct.unpack("<qq", buffer.read(16))

        if file_type in PHOTO_TYPES:
            has_volume_and_local_id = minor < NO_VOLUME_AND_LOCAL_ID_MINOR
            volume_id = struct.unpack("<q", buffer.read(8))[0] if has_volume_and_local_id else None

            thumbnail_source, = (0,) if major < 4 else struct.unpack("<i", buffer.read(4))

            try:
                thumbnail_source = ThumbnailSource(thumbnail_source)
            except ValueError:
                raise ValueError(f"Unknown thumbnail_source {thumbnail_source} of file_id {file_id}")

            tail = read_photo_tail(buffer, thumbnail_source=thumbnail_source)

            # Before minor 32 every source shared one layout, with `local_id` last.
            if has_volume_and_local_id:
                local_id, = struct.unpack("<i", buffer.read(4))
                tail = replace(tail, volume_id=volume_id, local_id=local_id)

            return FileId(
                major=major,
                minor=minor,
                file_type=file_type,
                dc_id=dc_id,
                file_reference=file_reference,
                media_id=media_id,
                access_hash=access_hash,
                thumbnail_source=thumbnail_source,
                volume_id=tail.volume_id,
                local_id=tail.local_id,
                secret=tail.secret,
                thumbnail_file_type=tail.thumbnail_file_type,
                thumbnail_size=tail.thumbnail_size,
                chat_id=tail.chat_id,
                chat_access_hash=tail.chat_access_hash,
                sticker_set_id=tail.sticker_set_id,
                sticker_set_access_hash=tail.sticker_set_access_hash,
                sticker_set_version=tail.sticker_set_version
            )

        if file_type in DOCUMENT_TYPES:
            return FileId(
                major=major,
                minor=minor,
                file_type=file_type,
                dc_id=dc_id,
                file_reference=file_reference,
                media_id=media_id,
                access_hash=access_hash
            )

    def encode(self, *, major: Optional[int] = None, minor: Optional[int] = None):
        major = major if major is not None else self.major
        minor = minor if minor is not None else self.minor

        buffer = BytesIO()

        file_type = self.file_type

        if self.url:
            file_type |= WEB_LOCATION_FLAG

        if self.file_reference:
            file_type |= FILE_REFERENCE_FLAG

        buffer.write(struct.pack("<ii", file_type, self.dc_id))

        if self.url:
            buffer.write(String(self.url))

        if self.file_reference:
            buffer.write(Bytes(self.file_reference))

        buffer.write(struct.pack("<qq", self.media_id, self.access_hash))

        if self.file_type in PHOTO_TYPES:
            has_volume_and_local_id = minor < NO_VOLUME_AND_LOCAL_ID_MINOR

            if has_volume_and_local_id:
                buffer.write(struct.pack("<q", self.volume_id))

            if major >= 4:
                buffer.write(struct.pack("<i", self.thumbnail_source))

            buffer.write(write_photo_tail(self))

            if has_volume_and_local_id:
                buffer.write(struct.pack("<i", self.local_id))
        elif file_type in DOCUMENT_TYPES:
            buffer.write(struct.pack("<ii", minor, major))

        buffer.write(struct.pack("<bb", minor, major))

        return b64_encode(rle_encode(buffer.getvalue()))

    def __str__(self):
        return str({k: v for k, v in self.__dict__.items() if v is not None})


class FileUniqueType(IntEnum):
    """Known file unique types"""
    WEB = 0
    PHOTO = 1
    DOCUMENT = 2
    SECURE = 3
    ENCRYPTED = 4
    TEMP = 5


class FileUniqueId:
    def __init__(
        self, *,
        file_unique_type: FileUniqueType,
        url: Optional[str] = None,
        media_id: Optional[int] = None,
        volume_id: Optional[int] = None,
        local_id: Optional[int] = None
    ):
        self.file_unique_type = file_unique_type
        self.url = url
        self.media_id = media_id
        self.volume_id = volume_id
        self.local_id = local_id

    @staticmethod
    def decode(file_unique_id: str):
        buffer = BytesIO(rle_decode(b64_decode(file_unique_id)))
        file_unique_type, = struct.unpack("<i", buffer.read(4))

        try:
            file_unique_type = FileUniqueType(file_unique_type)
        except ValueError:
            raise ValueError(f"Unknown file_unique_type {file_unique_type} of file_unique_id {file_unique_id}")

        if file_unique_type == FileUniqueType.WEB:
            url = String.read(buffer)

            return FileUniqueId(
                file_unique_type=file_unique_type,
                url=url
            )

        if file_unique_type == FileUniqueType.PHOTO:
            volume_id, local_id = struct.unpack("<qi", buffer.read())

            return FileUniqueId(
                file_unique_type=file_unique_type,
                volume_id=volume_id,
                local_id=local_id
            )

        if file_unique_type == FileUniqueType.DOCUMENT:
            media_id, = struct.unpack("<q", buffer.read())

            return FileUniqueId(
                file_unique_type=file_unique_type,
                media_id=media_id
            )

        # TODO: Missing decoder for SECURE, ENCRYPTED and TEMP
        raise ValueError(f"Unknown decoder for file_unique_type {file_unique_type} of file_unique_id {file_unique_id}")

    def encode(self):
        if self.file_unique_type == FileUniqueType.WEB:
            string = struct.pack("<is", self.file_unique_type, String(self.url))
        elif self.file_unique_type == FileUniqueType.PHOTO:
            string = struct.pack("<iqi", self.file_unique_type, self.volume_id, self.local_id)
        elif self.file_unique_type == FileUniqueType.DOCUMENT:
            string = struct.pack("<iq", self.file_unique_type, self.media_id)
        else:
            # TODO: Missing encoder for SECURE, ENCRYPTED and TEMP
            raise ValueError(f"Unknown encoder for file_unique_type {self.file_unique_type}")

        return b64_encode(rle_encode(string))

    def __str__(self):
        return str({k: v for k, v in self.__dict__.items() if v is not None})
