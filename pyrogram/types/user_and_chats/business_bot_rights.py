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

from pyrogram import raw

from ..object import Object


class BusinessBotRights(Object):
    """Describes actions that a connected business bot is allowed to take in a chat.

    Parameters:
        can_reply (``bool``, *optional*):
            True, if the bot can send and edit messages in the private chats that had incoming messages in the last 24 hours.

        can_read_messages (``bool``, *optional*):
            True, if the bot can mark incoming private messages as read.

        can_delete_sent_messages (``bool``, *optional*):
            True, if the bot is allowed to delete sent messages.

        can_delete_all_messages (``bool``, *optional*):
            True, if the bot is allowed to delete any message.

        can_edit_name (``bool``, *optional*):
            True, if the bot can edit name of the business account.

        can_edit_bio (``bool``, *optional*):
            True, if the bot can edit bio of the business account.

        can_edit_profile_photo (``bool``, *optional*):
            True, if the bot can edit profile photo of the business account.

        can_edit_username (``bool``, *optional*):
            True, if the bot can edit username of the business account.

        can_view_gifts_and_stars (``bool``, *optional*):
            True, if the bot can view gifts and amount of Telegram Stars owned by the business account.

        can_sell_gifts (``bool``, *optional*):
            True, if the bot can sell regular gifts received by the business account.

        can_change_gift_settings (``bool``, *optional*):
            True, if the bot can change gift receiving settings of the business account.

        can_transfer_and_upgrade_gifts (``bool``, *optional*):
            True, if the bot can transfer and upgrade gifts received by the business account.

        can_transfer_stars (``bool``, *optional*):
            True, if the bot can transfer Telegram Stars received by the business account to account of the bot,
            or use them to upgrade and transfer gifts.

        can_manage_stories (``bool``, *optional*):
            True, if the bot can send, edit and delete stories.
    """

    def __init__(
        self,
        *,
        can_reply: Optional[bool] = None,
        can_read_messages: Optional[bool] = None,
        can_delete_sent_messages: Optional[bool] = None,
        can_delete_all_messages: Optional[bool] = None,
        can_edit_name: Optional[bool] = None,
        can_edit_bio: Optional[bool] = None,
        can_edit_profile_photo: Optional[bool] = None,
        can_edit_username: Optional[bool] = None,
        can_view_gifts: Optional[bool] = None,
        can_sell_gifts: Optional[bool] = None,
        can_change_gift_settings: Optional[bool] = None,
        can_transfer_and_upgrade_gifts: Optional[bool] = None,
        can_transfer_stars: Optional[bool] = None,
        can_manage_stories: Optional[bool] = None
    ):
        super().__init__(None)

        self.can_reply = can_reply
        self.can_read_messages = can_read_messages
        self.can_delete_sent_messages = can_delete_sent_messages
        self.can_delete_all_messages = can_delete_all_messages
        self.can_edit_name = can_edit_name
        self.can_edit_bio = can_edit_bio
        self.can_edit_profile_photo = can_edit_profile_photo
        self.can_edit_username = can_edit_username
        self.can_view_gifts = can_view_gifts
        self.can_sell_gifts = can_sell_gifts
        self.can_change_gift_settings = can_change_gift_settings
        self.can_transfer_and_upgrade_gifts = can_transfer_and_upgrade_gifts
        self.can_transfer_stars = can_transfer_stars
        self.can_manage_stories = can_manage_stories

    @staticmethod
    def _parse(permissions: "raw.types.BusinessBotRights") -> "BusinessBotRights":
        if isinstance(permissions, raw.types.BusinessBotRights):
            return BusinessBotRights(
                can_reply=permissions.reply,
                can_read_messages=permissions.read_messages,
                can_delete_sent_messages=permissions.delete_sent_messages,
                can_delete_all_messages=permissions.delete_received_messages,
                can_edit_name=permissions.edit_name,
                can_edit_bio=permissions.edit_bio,
                can_edit_profile_photo=permissions.edit_profile_photo,
                can_edit_username=permissions.edit_username,
                can_view_gifts=permissions.view_gifts,
                can_sell_gifts=permissions.sell_gifts,
                can_change_gift_settings=permissions.change_gift_settings,
                can_transfer_and_upgrade_gifts=permissions.transfer_and_upgrade_gifts,
                can_transfer_stars=permissions.transfer_stars,
                can_manage_stories=permissions.manage_stories,
            )
