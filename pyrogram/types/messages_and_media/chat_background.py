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

from typing import Optional, Union

import pyrogram
from pyrogram import raw, types

from ..object import Object


class ChatBackground(Object):
    """Describes a background set for a specific chat.

    Parameters:
        id (``int``):
            Unique background identifier.

        document (:obj:`~pyrogram.types.Document`, *optional*):
            Document with the background.

        is_creator (``bool``, *optional*):
            True, if the background was created by the current user.

        is_default (``bool``, *optional*):
            True, if this is one of default backgrounds.

        is_pattern (``bool``, *optional*):
            True, if this is a pattern wallpaper.

        is_dark (``bool``, *optional*):
            True, if the background is dark and is recommended to be used with dark theme.

        is_blurred (``bool``, *optional*):
            True, if the wallpaper must be downscaled to fit in 450x450 square and then box-blurred with radius 12.

        is_moving (``bool``, *optional*):
            True, if the background needs to be slightly moved when device is tilted.

        is_same (``bool``, *optional*):
            True, if the set background is the same as the background of the current user.

        only_for_self (``bool``, *optional*):
            True, if the background was set only for self.

        background_color (``int``, *optional*):
            Used for solid, gradient and freeform gradient fills.

        second_background_color (``int``, *optional*):
            Used for gradient and freeform gradient fills.

        third_background_color (``int``, *optional*):
            Used for freeform gradient fills.

        fourth_background_color (``int``, *optional*):
            Used for freeform gradient fills.

        intensity (``int``, *optional*):
            Intensity of the pattern when it is shown above the filled background; 0-100.

        rotation_angle (``int``, *optional*):
            Clockwise rotation angle of the gradient, in degrees; 0-359. Must always be divisible by 45.

        emoji (``str``, *optional*):
            If set, this wallpaper can be used as a channel wallpaper and is represented by the specified UTF-8 emoji.

        raw (:obj:`~pyrogram.raw.base.WallPaper`, *optional*):
            Raw object.
    """

    def __init__(
        self,
        *,
        id: int,
        document: Optional["types.Document"] = None,
        is_creator: Optional[bool] = None,
        is_default: Optional[bool] = None,
        is_pattern: Optional[bool] = None,
        is_dark: Optional[bool] = None,
        is_blurred: Optional[bool] = None,
        is_moving: Optional[bool] = None,
        is_same: Optional[bool] = None,
        only_for_self: Optional[bool] = None,
        background_color: Optional[int] = None,
        second_background_color: Optional[int] = None,
        third_background_color: Optional[int] = None,
        fourth_background_color: Optional[int] = None,
        intensity: Optional[int] = None,
        rotation_angle: Optional[int] = None,
        emoji: Optional[str] = None,
        raw: Optional["raw.base.WallPaper"] = None
    ):
        super().__init__()

        self.id = id
        self.document = document
        self.is_creator = is_creator
        self.is_default = is_default
        self.is_pattern = is_pattern
        self.is_dark = is_dark
        self.is_blurred = is_blurred
        self.is_moving = is_moving
        self.is_same = is_same
        self.only_for_self = only_for_self
        self.background_color = background_color
        self.second_background_color = second_background_color
        self.third_background_color = third_background_color
        self.fourth_background_color = fourth_background_color
        self.intensity = intensity
        self.rotation_angle = rotation_angle
        self.emoji = emoji
        self.raw = raw

    @staticmethod
    def _parse(
        client: "pyrogram.Client",
        background: "raw.base.WallPaper",
        is_same: Optional[bool] = None,
        only_for_self: Optional[bool] = None
    ) -> Optional["ChatBackground"]:
        if not background:
            return None

        settings = getattr(background, "settings", None)
        document = None

        if getattr(background, "document", None):
            document = types.Document._parse(client, background.document, "wallpaper.jpg")

        if only_for_self is not None:
            only_for_self = not only_for_self

        return ChatBackground(
            id=background.id,
            document=document,
            is_creator=getattr(background, "creator", None),
            is_default=getattr(background, "default", None),
            is_pattern=getattr(background, "pattern", None),
            is_dark=getattr(background, "dark", None),
            is_blurred=getattr(settings, "blur", None),
            is_moving=getattr(settings, "motion", None),
            is_same=is_same,
            only_for_self=only_for_self,
            background_color=getattr(settings, "background_color", None),
            second_background_color=getattr(settings, "second_background_color", None),
            third_background_color=getattr(settings, "third_background_color", None),
            fourth_background_color=getattr(settings, "fourth_background_color", None),
            intensity=getattr(settings, "intensity", None),
            rotation_angle=getattr(settings, "rotation", None),
            emoji=getattr(settings, "emoticon", None),
            raw=background
        )
