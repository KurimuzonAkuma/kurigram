import io
import os
import re
from typing import Union

import pyrogram
from pyrogram import raw
from pyrogram import types
from pyrogram import utils
from pyrogram.file_id import FileType

from pyrogram.raw.types.input_media_document import InputMediaDocument
from pyrogram.raw.types.input_media_document_external import InputMediaDocumentExternal
from pyrogram.raw.types.input_media_photo import InputMediaPhoto
from pyrogram.raw.types.input_media_photo_external import InputMediaPhotoExternal

async def resolve_to_raw_photo(
    client: "pyrogram.Client",
    media: "types.InputMediaPhoto",
    chat_id: Union[int, str, None] = None,
) -> Union[InputMediaPhoto, InputMediaPhotoExternal, InputMediaDocument]:
    if isinstance(media.media, io.BytesIO) or os.path.isfile(media.media):
        if chat_id is None:
            raise ValueError("chat_id is required for uploading files")
        uploaded_media = await client.invoke(
            raw.functions.messages.UploadMedia(
                peer=await client.resolve_peer(chat_id),
                media=raw.types.InputMediaUploadedPhoto(
                    file=await client.save_file(media.media),
                    spoiler=media.has_spoiler,
                ),
            ),
        )

        return raw.types.InputMediaPhoto(
            id=raw.types.InputPhoto(
                id=uploaded_media.photo.id,
                access_hash=uploaded_media.photo.access_hash,
                file_reference=uploaded_media.photo.file_reference,
            ),
            spoiler=media.has_spoiler,
        )
    if re.match("^https?://", media.media):
        return raw.types.InputMediaPhotoExternal(
            url=media.media,
            spoiler=media.has_spoiler,
        )
    return utils.get_input_media_from_file_id(
        media.media,
        FileType.PHOTO,
        has_spoiler=media.has_spoiler,
    )


async def resolve_to_raw_video(
    client: "pyrogram.Client",
    media: "types.InputMediaVideo",
    file_name: Union[str, None] = None,
    chat_id: Union[int, str, None] = None,
) -> Union[InputMediaDocument, InputMediaDocumentExternal, InputMediaPhoto]:
    if isinstance(media.media, io.BytesIO) or os.path.isfile(media.media):
        if chat_id is None:
            raise ValueError("chat_id is required for uploading files")
        uploaded_media = await client.invoke(
            raw.functions.messages.UploadMedia(
                peer=await client.resolve_peer(chat_id),
                media=raw.types.InputMediaUploadedDocument(
                    mime_type=client.guess_mime_type(media.media) or "video/mp4",
                    thumb=await client.save_file(media.thumb),
                    spoiler=media.has_spoiler,
                    file=await client.save_file(media.media),
                    attributes=[
                        raw.types.DocumentAttributeVideo(
                            supports_streaming=media.supports_streaming or None,
                            duration=media.duration,
                            w=media.width,
                            h=media.height,
                        ),
                        raw.types.DocumentAttributeFilename(
                            file_name=file_name or os.path.basename(media.media),
                        ),
                    ],
                ),
            ),
        )

        return raw.types.InputMediaDocument(
            id=raw.types.InputDocument(
                id=uploaded_media.document.id,
                access_hash=uploaded_media.document.access_hash,
                file_reference=uploaded_media.document.file_reference,
            ),
            spoiler=media.has_spoiler,
        )
    if re.match("^https?://", media.media):
        return raw.types.InputMediaDocumentExternal(
            url=media.media,
            spoiler=media.has_spoiler,
        )
    return utils.get_input_media_from_file_id(
        media.media,
        FileType.VIDEO,
        has_spoiler=media.has_spoiler,
    )


async def resolve_to_raw_audio(
    client: "pyrogram.Client",
    media: "types.InputMediaAudio",
    file_name: Union[str, None] = None,
    chat_id: Union[int, str, None] = None,
) -> Union[InputMediaDocument, InputMediaDocumentExternal, InputMediaPhoto]:
    if isinstance(media.media, io.BytesIO) or os.path.isfile(media.media):
        if chat_id is None:
            raise ValueError("chat_id is required for uploading files")
        uploaded_media = await client.invoke(
            raw.functions.messages.UploadMedia(
                peer=await client.resolve_peer(chat_id),
                media=raw.types.InputMediaUploadedDocument(
                    mime_type=client.guess_mime_type(media.media) or "audio/mpeg",
                    thumb=await client.save_file(media.thumb),
                    file=await client.save_file(media.media),
                    attributes=[
                        raw.types.DocumentAttributeAudio(
                            duration=media.duration,
                            performer=media.performer,
                            title=media.title,
                        ),
                        raw.types.DocumentAttributeFilename(
                            file_name=file_name or os.path.basename(media.media),
                        ),
                    ],
                ),
            ),
        )

        return raw.types.InputMediaDocument(
            id=raw.types.InputDocument(
                id=uploaded_media.document.id,
                access_hash=uploaded_media.document.access_hash,
                file_reference=uploaded_media.document.file_reference,
            ),
        )
    if re.match("^https?://", media.media):
        return raw.types.InputMediaDocumentExternal(
            url=media.media,
        )
    return utils.get_input_media_from_file_id(media.media, FileType.AUDIO)


async def resolve_to_raw_animation(
    client: "pyrogram.Client",
    media: "types.InputMediaAnimation",
    file_name: Union[str, None] = None,
    chat_id: Union[int, str, None] = None,
) -> Union[InputMediaDocument, InputMediaDocumentExternal, InputMediaPhoto]:
    if isinstance(media.media, io.BytesIO) or os.path.isfile(media.media):
        if chat_id is None:
            raise ValueError("chat_id is required for uploading files")
        uploaded_media = await client.invoke(
            raw.functions.messages.UploadMedia(
                peer=await client.resolve_peer(chat_id),
                media=raw.types.InputMediaUploadedDocument(
                    mime_type=client.guess_mime_type(media.media) or "video/mp4",
                    thumb=await client.save_file(media.thumb),
                    spoiler=media.has_spoiler,
                    file=await client.save_file(media.media),
                    attributes=[
                        raw.types.DocumentAttributeVideo(
                            supports_streaming=True,
                            duration=media.duration,
                            w=media.width,
                            h=media.height,
                        ),
                        raw.types.DocumentAttributeFilename(
                            file_name=file_name or os.path.basename(media.media),
                        ),
                        raw.types.DocumentAttributeAnimated(),
                    ],
                ),
            ),
        )

        return raw.types.InputMediaDocument(
            id=raw.types.InputDocument(
                id=uploaded_media.document.id,
                access_hash=uploaded_media.document.access_hash,
                file_reference=uploaded_media.document.file_reference,
            ),
            spoiler=media.has_spoiler,
        )
    if re.match("^https?://", media.media):
        return raw.types.InputMediaDocumentExternal(
            url=media.media,
            spoiler=media.has_spoiler,
        )
    return utils.get_input_media_from_file_id(
        media.media,
        FileType.ANIMATION,
        has_spoiler=media.has_spoiler,
    )


async def resolve_to_raw_document(
    client: "pyrogram.Client",
    media: "types.InputMediaDocument",
    file_name: Union[str, None] = None,
    chat_id: Union[int, str, None] = None,
) -> Union[InputMediaDocument, InputMediaDocumentExternal, InputMediaPhoto]:
    if isinstance(media.media, io.BytesIO) or os.path.isfile(media.media):
        if chat_id is None:
            raise ValueError("chat_id is required for uploading files")
        uploaded_media = await client.invoke(
            raw.functions.messages.UploadMedia(
                peer=await client.resolve_peer(chat_id),
                media=raw.types.InputMediaUploadedDocument(
                    mime_type=client.guess_mime_type(media.media) or "application/zip",
                    thumb=await client.save_file(media.thumb),
                    file=await client.save_file(media.media),
                    attributes=[
                        raw.types.DocumentAttributeFilename(
                            file_name=file_name or os.path.basename(media.media),
                        ),
                    ],
                ),
            ),
        )

        return raw.types.InputMediaDocument(
            id=raw.types.InputDocument(
                id=uploaded_media.document.id,
                access_hash=uploaded_media.document.access_hash,
                file_reference=uploaded_media.document.file_reference,
            ),
        )
    if re.match("^https?://", media.media):
        return raw.types.InputMediaDocumentExternal(
            url=media.media,
        )
    return utils.get_input_media_from_file_id(media.media, FileType.DOCUMENT)
