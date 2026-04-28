import io
import os
import re
from typing import BinaryIO, Callable, Optional, Union, cast

import pyrogram
from pyrogram import raw, types, utils
from pyrogram.file_id import FileType


async def resolve_to_raw_photo(
    client: "pyrogram.Client",
    media: "types.InputMediaPhoto",
    chat_id: Optional[Union[int, str]] = None,
) -> Union[
    raw.types.InputMediaPhoto,
    raw.types.InputMediaPhotoExternal,
    raw.types.InputMediaDocument,
]:
    """
    Prepare the photo to be sent in raw.

    Parameters:
        client (:obj:`~pyrogram.Client`):
            The client instance.

        media (:obj:`~pyrogram.types.InputMediaPhoto`):
            The media to be sent.

        chat_id (``int`` | ``str``, *optional*):
            The chat id to send the media.

    Returns:
        :obj:`~pyrogram.raw.types.InputMediaPhoto`
        | :obj:`~pyrogram.raw.types.InputMediaPhotoExternal`: On success,
        the resolved media is returned in form of a proper object.

    Raises:
        RPCError: In case of a Telegram RPC error.
    """
    if isinstance(media.media, io.BytesIO) or os.path.isfile(media.media):
        uploaded_media = await client.invoke(
            raw.functions.messages.UploadMedia(
                peer=(
                    await client.resolve_peer(chat_id)
                    if chat_id
                    else raw.types.InputPeerSelf()
                ),
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
    file_name: Optional[str] = None,
    chat_id: Optional[Union[int, str]] = None,
) -> Union[raw.types.InputMediaDocument, raw.types.InputMediaDocumentExternal]:
    """
    Prepare the video to be sent in raw.

    Parameters:
        client (:obj:`~pyrogram.Client`):
            The client instance.

        media (:obj:`~pyrogram.types.InputMediaVideo`):
            The media to be sent.

        file_name (``str``, *optional*):
            The name of the file.

        chat_id (``int`` | ``str``, *optional*):
            The chat id to send the media.

    Returns:
        :obj:`~pyrogram.raw.types.InputMediaDocument`
        | :obj:`~pyrogram.raw.types.InputMediaDocumentExternal`: On success,
        the resolved media is returned in form of a proper object.

    Raises:
        RPCError: In case of a Telegram RPC error.
    """
    if isinstance(media.media, io.BytesIO) or os.path.isfile(media.media):
        uploaded_media = await client.invoke(
            raw.functions.messages.UploadMedia(
                peer=(
                    await client.resolve_peer(chat_id)
                    if chat_id
                    else raw.types.InputPeerSelf()
                ),
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
    file_name: Optional[str] = None,
    chat_id: Optional[Union[int, str]] = None,
) -> Union[raw.types.InputMediaDocument, raw.types.InputMediaDocumentExternal]:
    """
    Prepare the audio to be sent in raw.

    Parameters:
        client (:obj:`~pyrogram.Client`):
            The client instance.

        media (:obj:`~pyrogram.types.InputMediaAudio`):
            The media to be sent.

        file_name (``str``, *optional*):
            The name of the file.

        chat_id (``int`` | ``str``, *optional*):
            The chat id to send the media.

    Returns:
        :obj:`~pyrogram.raw.types.InputMediaDocument`
        | :obj:`~pyrogram.raw.types.InputMediaDocumentExternal`: On success,
        the resolved media is returned in form of a proper object.

    Raises:
        RPCError: In case of a Telegram RPC error.
    """
    if isinstance(media.media, io.BytesIO) or os.path.isfile(media.media):
        uploaded_media = await client.invoke(
            raw.functions.messages.UploadMedia(
                peer=(
                    await client.resolve_peer(chat_id)
                    if chat_id
                    else raw.types.InputPeerSelf()
                ),
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
    file_name: Optional[str] = None,
    chat_id: Optional[Union[int, str]] = None,
) -> Union[raw.types.InputMediaDocument, raw.types.InputMediaDocumentExternal]:
    """
    Prepare the animation to be sent in raw.

    Parameters:
        client (:obj:`~pyrogram.Client`):
            The client instance.

        media (:obj:`~pyrogram.types.InputMediaAnimation`):
            The media to be sent.

        file_name (``str``, *optional*):
            The name of the file.

        chat_id (``int`` | ``str``, *optional*):
            The chat id to send the media.

    Returns:
        :obj:`~pyrogram.raw.types.InputMediaDocument`
        | :obj:`~pyrogram.raw.types.InputMediaDocumentExternal`: On success,
        the resolved media is returned in form of a proper object.

    Raises:
        RPCError: In case of a Telegram RPC error.
    """
    if isinstance(media.media, io.BytesIO) or os.path.isfile(media.media):
        uploaded_media = await client.invoke(
            raw.functions.messages.UploadMedia(
                peer=(
                    await client.resolve_peer(chat_id)
                    if chat_id
                    else raw.types.InputPeerSelf()
                ),
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
    file_name: Optional[str] = None,
    chat_id: Optional[Union[int, str]] = None,
) -> Union[raw.types.InputMediaDocument, raw.types.InputMediaDocumentExternal]:
    """
    Prepare the document to be sent in raw.

    Parameters:
        client (:obj:`~pyrogram.Client`):
            The client instance.

        media (:obj:`~pyrogram.types.InputMediaDocument`):
            The media to be sent.

        file_name (``str``, *optional*):
            The name of the file.

        chat_id (``int`` | ``str``, *optional*):
            The chat id to send the media.

    Returns:
        :obj:`~pyrogram.raw.types.InputMediaDocument`
        | :obj:`~pyrogram.raw.types.InputMediaDocumentExternal`: On success,
        the resolved media is returned in form of a proper object.

    Raises:
        RPCError: In case of a Telegram RPC error.
    """
    if isinstance(media.media, io.BytesIO) or os.path.isfile(media.media):
        uploaded_media = await client.invoke(
            raw.functions.messages.UploadMedia(
                peer=(
                    await client.resolve_peer(chat_id)
                    if chat_id
                    else raw.types.InputPeerSelf()
                ),
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


async def resolve_to_raw_location(
    loc: "types.Location",
) -> Union[raw.types.InputMediaGeoLive, raw.types.InputMediaGeoPoint]:
    """
    Prepare the location to be sent in raw.

    Parameters:
        loc (:obj:`~pyrogram.types.Location`):
            The location to be sent.

    Returns:
        :obj:`~pyrogram.raw.types.InputMediaGeoLive`
        | :obj:`~pyrogram.raw.types.InputMediaGeoPoint`: On success,
        the resolved media is returned in form of a proper object.
    """
    if loc.live_period is not None:
        return raw.types.InputMediaGeoLive(
            geo_point=raw.types.InputGeoPoint(
                lat=loc.latitude or 0,
                long=loc.longitude or 0,
                accuracy_radius=loc.accuracy_radius,
            ),
            heading=loc.heading,
            period=loc.live_period,
            proximity_notification_radius=loc.proximity_alert_radius,
        )

    return raw.types.InputMediaGeoPoint(
        geo_point=raw.types.InputGeoPoint(
            lat=loc.latitude or 0,
            long=loc.longitude or 0,
            accuracy_radius=loc.accuracy_radius,
        ),
    )


async def resolve_to_raw_sticker(
    client: "pyrogram.Client",
    sticker: "types.InputMediaSticker",
    emoji: Optional[str] = "",
    progress: Optional[Callable] = None,
    progress_args: Optional[tuple] = (),
) -> Union[
    raw.types.InputMediaUploadedDocument,
    raw.types.InputMediaDocumentExternal,
    raw.types.InputMediaDocument,
]:
    """
    Prepare the sticker to be sent in raw.

    Parameters:
        client (:obj:`~pyrogram.Client`):
            The client instance.

        sticker (:obj:`~pyrogram.types.InputMediaSticker`):
            The media to be sent.

        emoji (``str``, *optional*):
            The emoji to be associated with the sticker.

        progress (``Callable``, *optional*):
            A callable to be called with the progress of the upload.

        progress_args (``tuple``, *optional*):
            The arguments to be passed to the progress callable.

    Returns:
        :obj:`~pyrogram.raw.types.InputMediaUploadedDocument`
        | :obj:`~pyrogram.raw.types.InputMediaDocumentExternal`
        | :obj:`~pyrogram.raw.types.InputMediaDocument`: On success, the resolved
        media is returned in form of a proper object.

    Raises:
        RPCError: In case of a Telegram RPC error.
    """
    media: Union[BinaryIO, str] = sticker.media

    if isinstance(media, str):
        if os.path.isfile(media):
            file = await client.save_file(
                media,
                progress=cast(Callable, progress),
                progress_args=progress_args,
            )

            if not file:
                raise ValueError("Failed to upload sticker")

            return raw.types.InputMediaUploadedDocument(
                mime_type=client.guess_mime_type(media) or "image/webp",
                file=file,
                attributes=[
                    raw.types.DocumentAttributeFilename(
                        file_name=os.path.basename(media),
                    ),
                    raw.types.DocumentAttributeSticker(
                        alt=emoji,
                        stickerset=raw.types.InputStickerSetEmpty(),
                    ),
                ],
            )

        if re.match("^https?://", media):
            return raw.types.InputMediaDocumentExternal(url=media)

        return utils.get_input_media_from_file_id(media, FileType.STICKER)

    file = await client.save_file(
        media,
        progress=cast(Callable, progress),
        progress_args=progress_args,
    )

    if not file:
        raise ValueError("Failed to upload sticker")

    return raw.types.InputMediaUploadedDocument(
        mime_type=client.guess_mime_type(media.name) or "image/webp",
        file=file,
        attributes=[
            raw.types.DocumentAttributeFilename(file_name=media.name),
            raw.types.DocumentAttributeSticker(
                alt=emoji,
                stickerset=raw.types.InputStickerSetEmpty(),
            ),
        ],
    )
