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

from typing import Optional

from pyrogram import raw, types

from ..object import Object


class GlobalPrivacySettings(Object):
    """Birthday information of a user.

    Parameters:
        archive_and_mute_new_chats (``bool``, *optional*):
            Whether to archive and mute new chats from non-contacts,

        keep_unmuted_chats_archived (``bool``, *optional*):
            Whether unmuted chats will be kept in
            the Archive chat list when they get a new message.

        keep_chats_from_folders_archived (``bool``, *optional*):
            Whether unmuted chats, that are always included or pinned
            in a folder, will be kept in the Archive chat list when they get
            a new message. Ignored if keep_unmuted_chats_archived is set.

        show_read_date (``bool``, *optional*):
            True, if message read date is shown to other users in private chats.
            If false and the current user isn't a Telegram Premium user,
            then they will not be able to see other's message read date.

        allow_new_chats_from_unknown_users (``bool``, *optional*):
            True, if non-contacts users are able to write first to the current user.
            Telegram Premium subscribers are able to write first regardless of this setting.

        incoming_paid_message_star_count (``int``, *optional*):
            Number of Telegram Stars that must be paid for every incoming private message
            by non-contacts.
            Must be between 0-``paid_message_star_count_max``.
            If positive, then allow_new_chats_from_unknown_users must be true.
            The current user will receive ``paid_message_earnings_per_mille`` Telegram Stars
            for each 1000 Telegram Stars paid for message sending.

        show_gift_button (``bool``, *optional*):
            True, if a button for sending a gift to the user or by the user must be always shown in the input field.

        accepted_gift_types (:obj:`~pyrogram.types.AcceptedGiftTypes`, *optional*):
            Information about gifts that can be received by the user.
    """

    def __init__(
        self,
        *,
        archive_and_mute_new_chats: Optional[bool] = None,
        keep_unmuted_chats_archived: Optional[bool] = None,
        keep_chats_from_folders_archived: Optional[bool] = None,
        show_read_date: Optional[bool] = None,
        allow_new_chats_from_unknown_users: Optional[bool] = None,
        incoming_paid_message_star_count: Optional[int] = None,
        show_gift_button: Optional[bool] = None,
        accepted_gift_types: Optional["types.AcceptedGiftTypes"] = None
    ):
        self.archive_and_mute_new_chats = archive_and_mute_new_chats
        self.keep_unmuted_chats_archived = keep_unmuted_chats_archived
        self.keep_chats_from_folders_archived = keep_chats_from_folders_archived
        self.show_read_date = show_read_date
        self.allow_new_chats_from_unknown_users = allow_new_chats_from_unknown_users
        self.incoming_paid_message_star_count = incoming_paid_message_star_count
        self.show_gift_button = show_gift_button
        self.accepted_gift_types = accepted_gift_types

    @staticmethod
    def _parse(
        settings: Optional["raw.types.GlobalPrivacySettings"] = None
    ) -> Optional["GlobalPrivacySettings"]:
        if not settings:
            return

        return GlobalPrivacySettings(
            archive_and_mute_new_chats=getattr(settings, "archive_and_mute_new_noncontact_peers", None),
            keep_unmuted_chats_archived=getattr(settings, "keep_archived_unmuted", None),
            keep_chats_from_folders_archived=getattr(settings, "keep_archived_folders", None),
            show_read_date=getattr(settings, "hide_read_marks", None),
            allow_new_chats_from_unknown_users=getattr(settings, "new_noncontact_peers_require_premium", None),
            incoming_paid_message_star_count=getattr(settings, "noncontact_peers_paid_stars", None),
            show_gift_button=getattr(settings, "display_gifts_button", None),
            accepted_gift_types=types.AcceptedGiftTypes._parse(getattr(settings, "disallowed_gifts", None))
        )

    def write(self) -> "raw.types.GlobalPrivacySettings":
        return raw.types.GlobalPrivacySettings(
            archive_and_mute_new_noncontact_peers=self.archive_and_mute_new_chats,
            keep_archived_unmuted=self.keep_unmuted_chats_archived,
            keep_archived_folders=self.keep_chats_from_folders_archived,
            hide_read_marks=self.show_read_date,
            new_noncontact_peers_require_premium=self.allow_new_chats_from_unknown_users,
            noncontact_peers_paid_stars=self.incoming_paid_message_star_count,
            display_gifts_button=self.show_gift_button,
            disallowed_gifts=self.accepted_gift_types.write() if self.accepted_gift_types else None
        )
