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

import logging
from typing import BinaryIO, Optional, Union

import pyrogram
from pyrogram import raw, types

log = logging.getLogger(__name__)

class SetProfilePhoto:
    async def set_profile_photo(
        self: "pyrogram.Client",
        photo: Optional["types.InputChatPhoto"] = None,
        is_public: Optional[bool] = None,
        *,
        video: Optional[Union[str, BinaryIO]] = None
    ) -> bool:
        """Changes a profile photo for the current user.

        .. include:: /_includes/usable-by/users-bots.rst

        Parameters:
            photo (:obj:`~pyrogram.types.InputChatPhoto`, *optional*):
                Profile photo to set.

            is_public (``bool``, *optional*):
                Pass True to set the public photo, which will be visible even if the main photo is hidden by privacy settings.

        Returns:
            ``bool``: True on success.

        Example:
            .. code-block:: python

                # Set a new profile photo
                await app.set_profile_photo(photo=types.InputChatPhotoStatic("new_photo.jpg"))

                # Set a new profile video
                await app.set_profile_photo(photo=types.InputChatPhotoAnimation("new_video.mp4"))

                # Set a previous profile photo
                await app.set_profile_photo(photo=types.InputChatPhotoPrevious(file_id))

                # Set/update your account's public profile photo
                await app.set_profile_photo(photo=types.InputChatPhotoStatic("new_photo.jpg"), is_public=True)
        """
        if video is not None:
            log.warning(
                "`video` is deprecated and will be removed in future updates. Use `photo` instead."
            )

            photo = types.InputChatPhotoAnimation(animation=video)

        if photo is not None and not isinstance(photo, types.InputChatPhoto):
            log.warning(
                "You must pass `photo` as `types.InputChatPhoto`. Passing `photo` as a string "
                "or binary object is deprecated and will be removed in future updates."
            )

            photo = types.InputChatPhotoStatic(photo=photo)

        if isinstance(photo, types.InputChatPhotoPrevious):
            return bool(
                await self.invoke(
                    raw.functions.photos.UpdateProfilePhoto(
                        fallback=is_public,
                        id=await photo.write(self),
                    )
                )
            )
        else:
            return bool(
                await self.invoke(
                    raw.functions.photos.UploadProfilePhoto(
                        fallback=is_public,
                        file=await photo.write(self) if isinstance(photo, types.InputChatPhotoStatic) else None,
                        video=await photo.write(self) if isinstance(photo, types.InputChatPhotoAnimation) else None,
                        video_start_ts=getattr(photo, "main_frame_timestamp", None),
                    )
                )
            )


class SetBotProfilePhoto:
    async def set_bot_profile_photo(
        self: "pyrogram.Client",
        bot_user_id: Union[int, str],
        photo: Optional["types.InputChatPhoto"] = None,
    ) -> bool:
        """Changes a profile photo for a bot.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            bot_user_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target bot.

            photo (:obj:`~pyrogram.types.InputChatPhoto`, *optional*):
                Profile photo to set.
                Pass None to remove the profile photo.

        Returns:
            ``bool``: True on success.

        Example:
            .. code-block:: python

                # Set a new bot profile photo
                await app.set_bot_profile_photo(bot_user_id="@KurigramBot", photo=types.InputChatPhotoStatic("new_photo.jpg"))

                # Set a new bot profile video
                await app.set_bot_profile_photo(bot_user_id="@KurigramBot", photo=types.InputChatPhotoAnimation("new_video.mp4"))

                # Remove bot profile photo
                await app.set_bot_profile_photo(bot_user_id="@KurigramBot")
        """
        if isinstance(photo, types.InputChatPhotoPrevious):
            return bool(
                await self.invoke(
                    raw.functions.photos.UpdateProfilePhoto(
                        id=await photo.write(self) if photo else raw.types.InputPhotoEmpty(),
                        bot=await self.resolve_peer(bot_user_id),
                    )
                )
            )
        else:
            return bool(
                await self.invoke(
                    raw.functions.photos.UploadProfilePhoto(
                        bot=await self.resolve_peer(bot_user_id),
                        file=await photo.write(self) if isinstance(photo, types.InputChatPhotoStatic) else None,
                        video=await photo.write(self) if isinstance(photo, types.InputChatPhotoAnimation) else None,
                        video_start_ts=getattr(photo, "main_frame_timestamp", None),
                    )
                )
            )
