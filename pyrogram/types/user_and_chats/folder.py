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

from typing import List, Optional, Union

import pyrogram
from pyrogram import enums, raw, types, utils

from ..object import Object


class Folder(Object):
    """Represents a folder for user chats.

    Parameters:
        id (``int``):
            Unique chat folder identifier.

        name (``str``):
            The text of the chat folder name, 1-12 characters without line feeds.

        entities (List of :obj:`~pyrogram.types.MessageEntity`, *optional*):
            Special entities like bold, italic, etc. that appear in the folder name.

        animate_custom_emoji (``bool``, *optional*):
            True, if custom emoji in the name must be animated.

        icon (``str``, *optional*):
            The chosen icon for the chat folder.

        color (:obj:`~pyrogram.enums.FolderColor`, *optional*)
            The identifier of the chosen color for the chat folder icon.
            Can't be changed if folder tags are disabled or the current user doesn't have Telegram Premium subscription.

        is_shareable (``bool``, *optional*):
            True, if at least one link has been created for the folder.

        pinned_chats (List of :obj:`~pyrogram.types.Chat`, *optional*):
            The pinned chats in the folder.
            There can be up to getOption("chat_folder_chosen_chat_count_max") pinned and always included non-secret chats and the same number of secret chats, but the limit can be increased with Telegram Premium.

        included_chats (List of :obj:`~pyrogram.types.Chat`, *optional*):
            The always included chats in the folder.
            There can be up to getOption("chat_folder_chosen_chat_count_max") pinned and always included non-secret chats and the same number of secret chats, but the limit can be increased with Telegram Premium.

        excluded_chats (List of :obj:`~pyrogram.types.Chat`, *optional*):
            The always excluded chats in the folder.
            There can be up to getOption("chat_folder_chosen_chat_count_max") always excluded non-secret chats and the same number of secret chats, but the limit can be increased with Telegram Premium.

        exclude_muted (``bool``, *optional*):
            True, if muted chats need to be excluded.

        exclude_read (``bool``, *optional*):
            True, if read chats need to be excluded.

        exclude_archived (``bool``, *optional*):
            True, if archived chats need to be excluded.

        include_contacts (``bool``, *optional*):
            True, if contacts need to be included.

        include_non_contacts (``bool``, *optional*):
            True, if non-contact users need to be included.

        include_bots (``bool``, *optional*):
            True, if bots need to be included.

        include_groups (``bool``, *optional*):
            True, if basic groups and supergroups need to be included.

        include_channels (``bool``, *optional*):
            True, if channels need to be included.

        raw (``raw.base.DialogFilter``, *optional*):
            The raw chat folder object.
    """

    def __init__(
        self,
        *,
        client: "pyrogram.Client" = None,
        id: int,
        name: str,
        entities: Optional[List["types.MessageEntity"]] = None,
        animate_custom_emoji: Optional[bool] = None,
        icon: Optional[str] = None,
        color: Optional["enums.FolderColor"] = None,
        is_shareable: Optional[bool] = None,
        pinned_chats: Optional[List["types.Chat"]] = None,
        included_chats: Optional[List["types.Chat"]] = None,
        excluded_chats: Optional[List["types.Chat"]] = None,
        exclude_muted: Optional[bool] = None,
        exclude_read: Optional[bool] = None,
        exclude_archived: Optional[bool] = None,
        include_contacts: Optional[bool] = None,
        include_non_contacts: Optional[bool] = None,
        include_bots: Optional[bool] = None,
        include_groups: Optional[bool] = None,
        include_channels: Optional[bool] = None,
        raw: Optional["raw.base.DialogFilter"] = None
    ):
        super().__init__(client)

        self.id = id
        self.name = name
        self.entities = entities
        self.animate_custom_emoji = animate_custom_emoji
        self.icon = icon
        self.color = color
        self.is_shareable = is_shareable
        self.pinned_chats = pinned_chats
        self.included_chats = included_chats
        self.excluded_chats = excluded_chats
        self.exclude_muted = exclude_muted
        self.exclude_read = exclude_read
        self.exclude_archived = exclude_archived
        self.include_contacts = include_contacts
        self.include_non_contacts = include_non_contacts
        self.include_bots = include_bots
        self.include_groups = include_groups
        self.include_channels = include_channels
        self.raw = raw

    @staticmethod
    async def _parse(client: "pyrogram.Client", folder: "raw.base.DialogFilter", users, chats) -> Optional["Folder"]:
        if not folder:
            return

        if isinstance(folder, raw.types.DialogFilterDefault):
            return

        pinned_chats = types.List()
        included_chats = types.List()
        excluded_chats = types.List()

        for peer in folder.pinned_peers:
            pinned_chats.append(types.Chat._parse_dialog(client, peer, users, chats))

        for peer in folder.include_peers:
            included_chats.append(types.Chat._parse_dialog(client, peer, users, chats))

        for peer in getattr(folder, "exclude_peers", []):
            excluded_chats.append(types.Chat._parse_dialog(client, peer, users, chats))

        name, entities = (utils.parse_text_with_entities(client, folder.title, {})).values()

        return Folder(
            id=folder.id,
            name=name,
            entities=entities,
            animate_custom_emoji=not folder.title_noanimate,
            icon=folder.emoticon or None,
            color=enums.FolderColor(folder.color),
            is_shareable=isinstance(folder, raw.types.DialogFilterChatlist),
            pinned_chats=pinned_chats or None,
            included_chats=included_chats or None,
            excluded_chats=excluded_chats or None,
            exclude_muted=getattr(folder, "exclude_muted", None),
            exclude_read=getattr(folder, "exclude_read", None),
            exclude_archived=getattr(folder, "exclude_archived", None),
            include_contacts=getattr(folder, "contacts", None),
            include_non_contacts=getattr(folder, "non_contacts", None),
            include_bots=getattr(folder, "bots", None),
            include_groups=getattr(folder, "groups", None),
            include_channels=getattr(folder, "broadcasts", None),
            raw=folder,
            client=client
        )

    async def delete(self) -> bool:
        """Bound method *delete* of :obj:`~pyrogram.types.Folder`.

        Use as a shortcut for:

        .. code-block:: python

            await client.delete_folder(123456789)

        Example:
            .. code-block:: python

               await folder.delete()

        Returns:
            True on success.
        """
        return await self._client.delete_folder(self.id)

    async def edit(
        self,
        name: Optional[str] = None,
        parse_mode: Optional["enums.ParseMode"] = None,
        entities: Optional[List["types.MessageEntity"]] = None,
        animate_custom_emoji: Optional[bool] = None,
        icon: Optional[str] = None,
        color: Optional["enums.FolderColor"] = None,
        pinned_chats: Optional[List[Union[int, str]]] = None,
        included_chats: Optional[List[Union[int, str]]] = None,
        excluded_chats: Optional[List[Union[int, str]]] = None,
        exclude_muted: Optional[bool] = None,
        exclude_read: Optional[bool] = None,
        exclude_archived: Optional[bool] = None,
        include_contacts: Optional[bool] = None,
        include_non_contacts: Optional[bool] = None,
        include_bots: Optional[bool] = None,
        include_groups: Optional[bool] = None,
        include_channels: Optional[bool] = None
    ) -> bool:
        """Bound method *update_peers* of :obj:`~pyrogram.types.Folder`.

        Use as a shortcut for:

        .. code-block:: python

            await client.edit_folder(
                folder_id,
                name="New folder",
                included_chats=["me"]
            )

        Example:
            .. code-block:: python

               await folder.update(included_chats=["me"])

        Parameters:
            name (``str``, *optional*):
                The text of the chat folder name, 1-12 characters without line feeds.

            entities (List of :obj:`~pyrogram.types.MessageEntity`, *optional*):
                Special entities like bold, italic, etc. that appear in the folder name.

            parse_mode (:obj:`~pyrogram.enums.ParseMode`, *optional*):
                By default, texts are parsed using both Markdown and HTML styles.
                You can combine both syntaxes together.

            animate_custom_emoji (``bool``, *optional*):
                True, if custom emoji in the name must be animated.

            icon (``str``, *optional*):
                The chosen icon for the chat folder.

            color (:obj:`~pyrogram.enums.FolderColor`, *optional*)
                The identifier of the chosen color for the chat folder icon.
                Can't be changed if folder tags are disabled or the current user doesn't have Telegram Premium subscription.

            is_shareable (``bool``, *optional*):
                True, if at least one link has been created for the folder.

            pinned_chats (List of ``int`` | ``str``, *optional*):
                The pinned chats in the folder.
                There can be up to getOption("chat_folder_chosen_chat_count_max") pinned and always included non-secret chats and the same number of secret chats, but the limit can be increased with Telegram Premium.

            included_chats (List of ``int`` | ``str``, *optional*):
                The always included chats in the folder.
                There can be up to getOption("chat_folder_chosen_chat_count_max") pinned and always included non-secret chats and the same number of secret chats, but the limit can be increased with Telegram Premium.

            excluded_chats (List of ``int`` | ``str``, *optional*):
                The always excluded chats in the folder.
                There can be up to getOption("chat_folder_chosen_chat_count_max") always excluded non-secret chats and the same number of secret chats, but the limit can be increased with Telegram Premium.

            exclude_muted (``bool``, *optional*):
                True, if muted chats need to be excluded.

            exclude_read (``bool``, *optional*):
                True, if read chats need to be excluded.

            exclude_archived (``bool``, *optional*):
                True, if archived chats need to be excluded.

            include_contacts (``bool``, *optional*):
                True, if contacts need to be included.

            include_non_contacts (``bool``, *optional*):
                True, if non-contact users need to be included.

            include_bots (``bool``, *optional*):
                True, if bots need to be included.

            include_groups (``bool``, *optional*):
                True, if basic groups and supergroups need to be included.

            include_channels (``bool``, *optional*):
                True, if channels need to be included.

        Returns:
            True on success.
        """
        if name:
            name, entities = (await utils.parse_text_entities(self, name, parse_mode, entities)).values()
            entities = entities or []

        return await self._client.edit_folder(
            folder_id=self.id,
            name=name or self.name,
            parse_mode=parse_mode,
            entities=entities or self.entities,
            animate_custom_emoji=animate_custom_emoji or self.animate_custom_emoji,
            icon=icon or self.icon,
            color=color or self.color,
            pinned_chats=[i.id for i in self.included_chats or []] if pinned_chats is None else pinned_chats,
            included_chats=[i.id for i in self.included_chats or []] if included_chats is None else included_chats,
            excluded_chats=[i.id for i in self.excluded_chats or []] if excluded_chats is None else excluded_chats,
            exclude_muted=exclude_muted or self.exclude_muted,
            exclude_read=exclude_read or self.exclude_read,
            exclude_archived=exclude_archived or self.exclude_archived,
            include_contacts=include_contacts or self.include_contacts,
            include_non_contacts=include_non_contacts or self.include_non_contacts,
            include_bots=include_bots or self.include_bots,
            include_groups=include_groups or self.include_groups,
            include_channels=include_channels or self.include_channels
        )

    async def include_chat(self, chat_id: Union[int, str]) -> bool:
        """Bound method *include_chat* of :obj:`~pyrogram.types.Folder`.

        Always include a chat in the folder.

        Use as a shortcut for:

        .. code-block:: python

            await client.edit_folder(
                folder_id=folder_id,
                included_chats=[chat_id]
            )

        Example:
            .. code-block:: python

               await folder.include_chat(chat_id)

        Parameters:
            chat_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target chat.
                For your personal cloud (Saved Messages) you can simply use "me" or "self".
                For a contact that exists in your Telegram address book you can use his phone number (str).

        Returns:
            True on success.
        """
        return await self.edit(
            included_chats=[i.id for i in self.included_chats or []] + [chat_id],
        )

    async def exclude_chat(self, chat_id: Union[int, str]) -> bool:
        """Bound method *exclude_chat* of :obj:`~pyrogram.types.Folder`.

        Always exclude a chat from the folder.

        Use as a shortcut for:

        .. code-block:: python

            await client.edit_folder(
                folder_id=folder_id,
                excluded_chats=[chat_id],
            )

        Example:
            .. code-block:: python

               await folder.exclude_chat(chat_id)

        Parameters:
            chat_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target chat.
                For your personal cloud (Saved Messages) you can simply use "me" or "self".
                For a contact that exists in your Telegram address book you can use his phone number (str).

        Returns:
            True on success.
        """
        return await self.edit(
            excluded_chats=[i.id for i in self.excluded_chats or []] + [chat_id],
        )

    async def pin_chat(self, chat_id: Union[int, str]):
        """Bound method *pin_chat* of :obj:`~pyrogram.types.Folder`.

        Use as a shortcut for:

        .. code-block:: python

            await client.edit_folder(
                folder_id=folder_id,
                included_chats=[chat_id],
                pinned_chats=[chat_id]
            )

        Example:
            .. code-block:: python

               await folder.pin_chat(chat_id)

        Parameters:
            chat_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target chat.
                For your personal cloud (Saved Messages) you can simply use "me" or "self".
                For a contact that exists in your Telegram address book you can use his phone number (str).

        Returns:
            True on success.
        """
        return await self.edit(
            included_chats=[i.id for i in self.included_chats or []] + [chat_id],
            pinned_chats=[i.id for i in self.pinned_chats or []] + [chat_id]
        )

    async def remove_chat(self, chat_id: Union[int, str]):
        """Bound method *remove_chat* of :obj:`~pyrogram.types.Folder`.

        Remove chat in folder from included/excluded/pinned chats.

        Example:
            .. code-block:: python

               await folder.remove_chat(chat_id)

        Parameters:
            chat_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target chat.
                For your personal cloud (Saved Messages) you can simply use "me" or "self".
                For a contact that exists in your Telegram address book you can use his phone number (str).

        Returns:
            True on success.
        """
        peer = await self._client.resolve_peer(chat_id)
        peer_id = utils.get_peer_id(peer)

        return await self.edit(
            pinned_chats=[i.id for i in self.pinned_chats or [] if peer_id != i.id],
            included_chats=[i.id for i in self.included_chats or [] if peer_id != i.id],
            excluded_chats=[i.id for i in self.excluded_chats or [] if peer_id != i.id]
        )


    async def update_color(self, color: "enums.FolderColor"):
        """Bound method *update_color* of :obj:`~pyrogram.types.Folder`.

        Use as a shortcut for:

        .. code-block:: python

            await client.edit_folder(
                folder_id=folder_id,
                color=color
            )

        Example:
            .. code-block:: python

               await folder.update_color(enums.FolderColor.RED)

        Parameters:
            color (:obj:`~pyrogram.enums.FolderColor`, *optional*):
                Color type.
                Pass :obj:`~pyrogram.enums.FolderColor` to set folder color.

        Returns:
            True on success.
        """
        return await self.edit(
            color=color
        )

    async def create_invite_link(self, name: str = None, chat_ids: List[Union[int, str]] = None) -> "types.FolderInviteLink":
        """Bound method *create_invite_link* of :obj:`~pyrogram.types.Folder`.

        Use as a shortcut for:

        .. code-block:: python

            await client.create_invite_link(123456789)

        Example:
            .. code-block:: python

               await folder.create_invite_link()

        Returns:
            :obj:`~pyrogram.types.FolderInviteLink`: On success, information about the invite link is returned.
        """
        if chat_ids is None:
            chat_ids = [i.id for i in self.included_chats]

        return await self._client.create_folder_invite_link(
            chat_folder_id=self.id,
            name=name,
            chat_ids=chat_ids
        )
