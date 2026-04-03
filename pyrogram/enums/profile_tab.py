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

from pyrogram import raw
from .auto_name import AutoName


class ProfileTab(AutoName):
    """Profile tab enumeration used in :obj:`~pyrogram.types.Chat`."""

    POSTS = raw.types.ProfileTabPosts
    "A tab with stories posted by the user or the channel chat and saved to profile."

    GIFTS = raw.types.ProfileTabGifts
    "A tab with gifts received by the user or the channel chat."

    MEDIA = raw.types.ProfileTabMedia
    "A tab with photos and videos posted by the channel."

    FILES = raw.types.ProfileTabFiles
    "A tab with documents posted by the channel."

    LINKS = raw.types.ProfileTabLinks
    "A tab with messages posted by the channel and containing links."

    MUSIC = raw.types.ProfileTabMusic
    "A tab with audio messages posted by the channel."

    VOICE = raw.types.ProfileTabVoice
    "A tab with voice notes posted by the channel."

    GIFS = raw.types.ProfileTabGifs
    "A tab with animations posted by the channel."
