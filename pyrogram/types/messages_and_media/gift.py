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

from datetime import datetime
from typing import Dict, List, Optional, Union

import pyrogram
from pyrogram import raw, types, utils, enums

from ..object import Object


class Gift(Object):
    """Describes a gift or an upgraded gift that can be transferred to another owner or transferred to the TON blockchain as an NFT.

    Parameters:
        id (``int``):
            Unique identifier of the gift.

        type (:obj:`~pyrogram.enums.GiftType`):
            Type of the gift.

        origin (:obj:`~pyrogram.enums.UpgradedGiftOrigin`, *optional*):
            Origin of the gift.

        received_gift_id (``str``, *optional*):
            Unique identifier of the received gift for the current user.

        regular_gift_id (``int``, *optional*):
            Unique identifier of the regular gift from which the gift was upgraded.

        publisher_chat (:obj:`~pyrogram.types.Chat`, *optional*):
            Information about the chat that published the gift.

        sticker (:obj:`~pyrogram.types.Sticker`, *optional*):
            The sticker that represents the gift.

        text (:obj:`~pyrogram.types.FormattedText`, *optional*):
            Message added to the gift.

        date (:py:obj:`~datetime.datetime`, *optional*):
            Date when the gift was sent or received.

        first_sale_date (:py:obj:`~datetime.datetime`, *optional*):
            Date when the gift was sent for the first time.
            For sold out gifts only.

        last_sale_date (:py:obj:`~datetime.datetime`, *optional*):
            Date when the gift was sent for the last time.
            For sold out gifts only.

        locked_until_date (:py:obj:`~datetime.datetime`, *optional*):
            Date when the gift will be available for purchase.

        craft_date (:py:obj:`~datetime.datetime`, *optional*):
            Date when the gift can be used to craft another gift can be in the past.

        sender (:obj:`~pyrogram.types.Chat`, *optional*):
            User or a chat that sent the gift.

        receiver (:obj:`~pyrogram.types.Chat`, *optional*):
            User or a chat that received the gift.

        host (:obj:`~pyrogram.types.Chat`, *optional*):
            User or the chat to which the upgraded gift was assigned from blockchain.

        owner (:obj:`~pyrogram.types.Chat`, *optional*):
            User or the chat that owns the gift.

        owner_address (``str``, *optional*):
            Address of the gift owner in TON blockchain.

        owner_name (``str``, *optional*):
            Name of the user who received the star gift.

        gift_address (``str``, *optional*):
            Address of the gift in TON blockchain.

        title (``str``, *optional*):
            The title of the upgraded gift.

        name (``str``, *optional*):
            Unique name of the upgraded gift.

        model (:obj:`~pyrogram.types.GiftAttribute`, *optional*):
            Model of the upgraded gift.

        symbol (:obj:`~pyrogram.types.GiftAttribute`, *optional*):
            Symbol of the upgraded gift.

        backdrop (:obj:`~pyrogram.types.GiftAttribute`, *optional*):
            Backdrop of the upgraded gift.

        original_details (:obj:`~pyrogram.types.UpgradedGiftOriginalDetails`, *optional*):
            Information about the originally sent gift.

        total_upgraded_count (``int``, *optional*):
            Total number of gifts that were upgraded from the same gift.

        max_upgraded_count (``int``, *optional*):
            The maximum number of gifts that can be upgraded from the same gift.

        available_resale_count (``int``, *optional*):
            Total number of gifts that can be bought from other users on the market.

        unique_gift_number (``int``, *optional*):
            Unique number of the gift among gifts upgraded from the same gift after upgrade.

        unique_gift_variant_count (``int``, *optional*):
            The total number of different unique gifts that can be obtained by upgrading the gift.

        star_count (``int``, *optional*):
            Number of Telegram Stars that must be paid for the gift.

        default_sell_star_count (``int``, *optional*):
            Number of Telegram Stars that can be claimed by the receiver instead of the regular gift by default.

        convert_star_count (``int``, *optional*):
            Number of Telegram Stars that can be claimed by the receiver instead of the gift; omitted if the gift cannot be converted to Telegram Stars.

        upgrade_star_count (``int``, *optional*):
            Number of Telegram Stars that must be paid to upgrade the gift.

        transfer_star_count (``int``, *optional*):
            Number of Telegram Stars that must be paid to transfer the upgraded gift.

        drop_original_details_star_count (``int``, *optional*):
            Number of Telegram Stars that must be paid to drop original details of the upgraded gift.

        minimum_resell_star_count (``int``, *optional*):
            Number of Telegram Stars for which sales begin on the market for the gift.

        minimum_offer_star_count (``int``, *optional*):
            Number of Telegram Stars required to make an offer for the gift.

        prepaid_upgrade_star_count (``int``, *optional*):
            Number of Telegram Stars that were paid by the sender for the ability to upgrade the gift.

        prepaid_upgrade_hash (``str``, *optional*):
            If non-empty, then the user can pay for an upgrade of the gift using :meth:`~pyrogram.Client.buy_gift_upgrade`.

        auction_info (:obj:`~pyrogram.types.GiftAuction`, *optional*):
            Information about the auction on which the gift can be purchased.

        resale_parameters (:obj:`~pyrogram.types.GiftResaleParameters`, *optional*):
            Resale parameters of the gift.

        user_limits (:obj:`~pyrogram.types.GiftPurchaseLimit`, *optional*):
            Number of times the gift can be purchased by the current user.

        overall_limits (:obj:`~pyrogram.types.GiftPurchaseLimit`, *optional*):
            Number of times the gift can be purchased all users.

        value_currency (``str``, *optional*):
            ISO 4217 currency code of the currency in which value of the gift is represented.

        value_amount (``int``, *optional*):
            Estimated value of the gift; in the smallest units of the currency.

        value_usd_amount (``int``, *optional*):
            Estimated value of the gift in USD cents.

        last_resale_currency (``str``, *optional*):
            For gifts bought from other users, the currency in which the payment for the gift was done.
            Currently, one of “XTR” for Telegram Stars or “TON” for toncoins.

        last_resale_amount (``int``, *optional*):
            For gifts bought from other users, the price paid for the gift in either Telegram Stars or nanotoncoins.

        next_send_date (:py:obj:`~datetime.datetime`, *optional*):
            Date when the gift can be sent next time by the current user.

        next_transfer_date (:py:obj:`~datetime.datetime`, *optional*):
            Date when the gift can be transferred to another owner.

        next_resale_date (:py:obj:`~datetime.datetime`, *optional*):
            Date when the gift can be resold to another user.

        export_date (:py:obj:`~datetime.datetime`, *optional*):
            Date when the gift can be transferred to the TON blockchain as an NFT.

        collection_ids (List of ``int``, *optional*):
            Identifiers of collections to which the gift is added.
            Only for the receiver of the gift.

        used_theme_chat_id (``int``, *optional*):
            Identifier of the chat for which the gift is used to set a theme.

        craft_probability_per_mille (``int``, *optional*):
            Probability that the gift adds to the chance of successful crafting of a new gift.

        has_colors (``bool``, *optional*):
            True, if the gift can be used to customize user's name and backgrounds.

        is_auction (``bool``, *optional*):
            True, if the gift can be purchased only on an auction.

        is_private (``bool``, *optional*):
            True, if the sender and gift text are shown only to the gift receiver.

        is_saved (``bool``, *optional*):
            True, if the gift is displayed on the chat's profile page.

        is_pinned (``bool``, *optional*):
            True, if the gift is pinned to the top of the chat's profile page.

        is_limited (``bool``, *optional*):
            True, if the number of gifts is limited.

        is_limited_per_user (``bool``, *optional*):
            True, if the number of gifts per user is limited.

        is_sold_out (``bool``, *optional*):
            True, if the gift is sold out.

        is_burned (``bool``, *optional*):
            True, if the gift was used to craft another gift.

        is_crafted (``bool``, *optional*):
            True, if the gift was craft from another gifts.

        is_premium (``bool``, *optional*):
            True, if the gift can be bought only by Telegram Premium subscribers.

        is_for_birthday (``bool``, *optional*):
            True, if the gift is a birthday gift.

        is_theme_available (``bool``, *optional*):
            True, if the gift can be used to set a theme in a chat.

        is_upgrade_separate (``bool``, *optional*):
            True, if the upgrade was bought after the gift was sent.

        is_name_hidden (``bool``, *optional*):
            True, if the owner name of the gift is hidden.

        can_be_upgraded (``bool``, *optional*):
            True, if the gift can be upgraded to a unique gift.

        can_be_transferred (``bool``, *optional*):
            True, if the upgraded gift can be transferred to another owner.

        can_send_purchase_offer (``bool``, *optional*):
            True, if an offer to purchase the gift can be sent using :meth:`~pyrogram.Client.send_gift_purchase_offer`.

        was_converted (``bool``, *optional*):
            True, if the gift was converted to Telegram Stars.
            Only for the receiver of the gift.

        was_upgraded (``bool``, *optional*):
            True, if the gift was upgraded to a unique gift.

        was_refunded (``bool``, *optional*):
            True, if the gift was refunded and isn't available anymore.

        raw (:obj:`~pyrogram.raw.base.StarGift` | :obj:`~pyrogram.raw.base.SavedStarGift`):
            The raw object as received from the server.

        link (``str``, *property*):
            A link to the gift.

        owned_gift_id (``str``, *property*):
            Unique identifier of the gift.
    """
    # TODO: background, colors

    def __init__(
        self,
        *,
        client: "pyrogram.Client" = None,
        id: int,
        type: "enums.GiftType",
        origin: Optional["enums.UpgradedGiftOrigin"] = None,
        received_gift_id: Optional[str] = None,
        regular_gift_id: Optional[int] = None,
        publisher_chat: Optional["types.Chat"] = None,
        sticker: Optional["types.Sticker"] = None,
        text: Optional["types.FormattedText"] = None,
        date: Optional[datetime] = None,
        first_sale_date: Optional[datetime] = None,
        last_sale_date: Optional[datetime] = None,
        locked_until_date: Optional[datetime] = None,
        craft_date: Optional[datetime] = None,
        sender: Optional["types.Chat"] = None,
        receiver: Optional["types.Chat"] = None,
        host: Optional["types.Chat"] = None,
        owner: Optional["types.Chat"] = None,
        owner_address: Optional[str] = None,
        owner_name: Optional[str] = None,
        gift_address: Optional[str] = None,
        title: Optional[str] = None,
        name: Optional[str] = None,
        model: Optional["types.GiftAttribute"] = None,
        symbol: Optional["types.GiftAttribute"] = None,
        backdrop: Optional["types.GiftAttribute"] = None,
        original_details: Optional["types.UpgradedGiftOriginalDetails"] = None,
        total_upgraded_count: Optional[int] = None,
        max_upgraded_count: Optional[int] = None,
        available_resale_count: Optional[int] = None,
        unique_gift_variant_count: Optional[int] = None,
        unique_gift_number: Optional[int] = None,
        star_count: Optional[int] = None,
        default_sell_star_count: Optional[int] = None,
        convert_star_count: Optional[int] = None,
        upgrade_star_count: Optional[int] = None,
        transfer_star_count: Optional[int] = None,
        drop_original_details_star_count: Optional[int] = None,
        minimum_resell_star_count: Optional[int] = None,
        minimum_offer_star_count: Optional[int] = None,
        prepaid_upgrade_star_count: Optional[int] = None,
        prepaid_upgrade_hash: Optional[str] = None,
        auction_info: Optional["types.GiftAuction"] = None,
        resale_parameters: Optional["types.GiftResaleParameters"] = None,
        user_limits: Optional["types.GiftPurchaseLimit"] = None,
        overall_limits: Optional["types.GiftPurchaseLimit"] = None,
        value_currency: Optional[str] = None,
        value_amount: Optional[int] = None,
        value_usd_amount: Optional[int] = None,
        last_resale_currency: Optional[str] = None,
        last_resale_amount: Optional[int] = None,
        next_send_date: Optional[datetime] = None,
        next_transfer_date: Optional[datetime] = None,
        next_resale_date: Optional[datetime] = None,
        export_date: Optional[datetime] = None,
        collection_ids: Optional[List[int]] = None,
        used_theme_chat_id: Optional[int] = None,
        craft_probability_per_mille: Optional[int] = None,
        has_colors: Optional[bool] = None,
        is_auction: Optional[bool] = None,
        is_private: Optional[bool] = None,
        is_saved: Optional[bool] = None,
        is_pinned: Optional[bool] = None,
        is_limited: Optional[bool] = None,
        is_limited_per_user: Optional[bool] = None,
        is_sold_out: Optional[bool] = None,
        is_burned: Optional[bool] = None,
        is_crafted: Optional[bool] = None,
        is_premium: Optional[bool] = None,
        is_for_birthday: Optional[bool] = None,
        is_theme_available: Optional[bool] = None,
        is_upgrade_separate: Optional[bool] = None,
        is_name_hidden: Optional[bool] = None,
        can_be_upgraded: Optional[bool] = None,
        can_be_transferred: Optional[bool] = None,
        can_send_purchase_offer: Optional[bool] = None,
        was_converted: Optional[bool] = None,
        was_upgraded: Optional[bool] = None,
        was_refunded: Optional[bool] = None,
        raw: Optional[
            Union[
                "raw.base.StarGift",
                "raw.base.SavedStarGift"
            ]
        ]
    ):
        super().__init__(client)

        self.id = id
        self.type = type
        self.origin = origin
        self.received_gift_id = received_gift_id
        self.regular_gift_id = regular_gift_id
        self.publisher_chat = publisher_chat
        self.sticker = sticker
        self.text = text
        self.date = date
        self.first_sale_date = first_sale_date
        self.last_sale_date = last_sale_date
        self.locked_until_date = locked_until_date
        self.craft_date = craft_date
        self.sender = sender
        self.receiver = receiver
        self.host = host
        self.owner = owner
        self.owner_address = owner_address
        self.owner_name = owner_name
        self.gift_address = gift_address
        self.title = title
        self.name = name
        self.model = model
        self.symbol = symbol
        self.backdrop = backdrop
        self.original_details = original_details
        self.total_upgraded_count = total_upgraded_count
        self.max_upgraded_count = max_upgraded_count
        self.available_resale_count = available_resale_count
        self.unique_gift_variant_count = unique_gift_variant_count
        self.unique_gift_number = unique_gift_number
        self.star_count = star_count
        self.default_sell_star_count = default_sell_star_count
        self.convert_star_count = convert_star_count
        self.upgrade_star_count = upgrade_star_count
        self.transfer_star_count = transfer_star_count
        self.drop_original_details_star_count = drop_original_details_star_count
        self.minimum_resell_star_count = minimum_resell_star_count
        self.minimum_offer_star_count = minimum_offer_star_count
        self.prepaid_upgrade_star_count = prepaid_upgrade_star_count
        self.prepaid_upgrade_hash = prepaid_upgrade_hash
        self.auction_info = auction_info
        self.resale_parameters = resale_parameters
        self.user_limits = user_limits
        self.overall_limits = overall_limits
        self.value_currency = value_currency
        self.value_amount = value_amount
        self.value_usd_amount = value_usd_amount
        self.last_resale_currency = last_resale_currency
        self.last_resale_amount = last_resale_amount
        self.next_send_date = next_send_date
        self.next_transfer_date = next_transfer_date
        self.next_resale_date = next_resale_date
        self.export_date = export_date
        self.collection_ids = collection_ids
        self.used_theme_chat_id = used_theme_chat_id
        self.craft_probability_per_mille = craft_probability_per_mille
        self.has_colors = has_colors
        self.is_auction = is_auction
        self.is_private = is_private
        self.is_saved = is_saved
        self.is_pinned = is_pinned
        self.is_limited = is_limited
        self.is_limited_per_user = is_limited_per_user
        self.is_sold_out = is_sold_out
        self.is_burned = is_burned
        self.is_crafted = is_crafted
        self.is_premium = is_premium
        self.is_for_birthday = is_for_birthday
        self.is_theme_available = is_theme_available
        self.is_upgrade_separate = is_upgrade_separate
        self.is_name_hidden = is_name_hidden
        self.can_be_upgraded = can_be_upgraded
        self.can_be_transferred = can_be_transferred
        self.can_send_purchase_offer = can_send_purchase_offer
        self.was_converted = was_converted
        self.was_upgraded = was_upgraded
        self.was_refunded = was_refunded
        self.raw = raw

    @staticmethod
    async def _parse(
        client: "pyrogram.Client",
        gift: Union[
            "raw.base.StarGift",
            "raw.base.SavedStarGift",
            "raw.types.MessageActionStarGift",
            "raw.types.MessageActionStarGiftUnique"
        ],
        receiver: Optional[Union["raw.base.User", "raw.base.Chat"]] = None,
        users: Dict[int, "raw.base.User"] = {},
        chats: Dict[int, "raw.base.Chat"] = {}
    ):
        if isinstance(gift, raw.types.StarGift):
            return await Gift._parse_regular(client, gift, receiver, users, chats)
        elif isinstance(gift, raw.types.StarGiftUnique):
            return await Gift._parse_upgraded(client, gift, receiver, users, chats)
        elif isinstance(gift, raw.types.SavedStarGift):
            return await Gift._parse_received(client, gift, receiver, users, chats)
        elif isinstance(gift, (raw.types.MessageActionStarGift, raw.types.MessageActionStarGiftUnique)):
            return await Gift._parse_action(client, gift, receiver, users, chats)

    @staticmethod
    async def _parse_regular(
        client: "pyrogram.Client",
        star_gift: "raw.types.StarGift",
        receiver: Optional[Union["raw.base.User", "raw.base.Chat"]] = None,
        users: Dict[int, "raw.base.User"] = {},
        chats: Dict[int, "raw.base.Chat"] = {}
    ) -> "Gift":
        if not isinstance(star_gift, raw.types.StarGift):
            return

        doc = star_gift.sticker
        attributes = {type(i): i for i in doc.attributes}

        # TODO?
        # auction_slug
        # background

        return Gift(
            id=star_gift.id,
            type=enums.GiftType.REGULAR,
            sticker=await types.Sticker._parse(client, doc, attributes),
            star_count=star_gift.stars,
            convert_star_count=star_gift.convert_stars,
            upgrade_star_count=star_gift.upgrade_stars,
            title=star_gift.title,
            available_resale_count=star_gift.availability_resale,
            user_limits=types.GiftPurchaseLimit._parse(star_gift.per_user_total, star_gift.per_user_remains),
            overall_limits=types.GiftPurchaseLimit._parse(star_gift.availability_total, star_gift.availability_remains),
            is_auction=star_gift.auction,
            is_limited=star_gift.limited,
            is_sold_out=star_gift.sold_out,
            is_for_birthday=star_gift.birthday,
            is_premium=star_gift.require_premium,
            is_limited_per_user=star_gift.limited_per_user,
            has_colors=star_gift.peer_color_available,
            first_sale_date=utils.timestamp_to_datetime(star_gift.first_sale_date),
            last_sale_date=utils.timestamp_to_datetime(star_gift.last_sale_date),
            locked_until_date=utils.timestamp_to_datetime(star_gift.locked_until_date),
            publisher_chat=types.Chat._parse_chat(client, chats.get(utils.get_raw_peer_id(star_gift.released_by))),
            auction_info=types.GiftAuction._parse(star_gift),
            unique_gift_variant_count=star_gift.upgrade_variants,
            minimum_resell_star_count=star_gift.resell_min_stars,
            raw=star_gift,
            client=client
        )

    @staticmethod
    async def _parse_upgraded(
        client: "pyrogram.Client",
        star_gift: "raw.types.StarGiftUnique",
        receiver: Optional[Union["raw.base.User", "raw.base.Chat"]] = None,
        users: Dict[int, "raw.base.User"] = {},
        chats: Dict[int, "raw.base.Chat"] = {}
    ) -> "Gift":
        if not isinstance(star_gift, raw.types.StarGiftUnique):
            return

        raw_host_id = utils.get_raw_peer_id(star_gift.host_id)
        raw_owner_id = utils.get_raw_peer_id(star_gift.owner_id)

        model = None
        symbol = None
        backdrop = None
        original_details = None

        for attr in star_gift.attributes:
            if isinstance(attr, raw.types.StarGiftAttributeModel):
                model = await types.GiftAttribute._parse(client, attr, users, chats)
            elif isinstance(attr, raw.types.StarGiftAttributePattern):
                symbol = await types.GiftAttribute._parse(client, attr, users, chats)
            elif isinstance(attr, raw.types.StarGiftAttributeBackdrop):
                backdrop = await types.GiftAttribute._parse(client, attr, users, chats)
            elif isinstance(attr, raw.types.StarGiftAttributeOriginalDetails):
                original_details = await types.UpgradedGiftOriginalDetails._parse(client, attr, users, chats)

        # TODO?
        # peer_color

        return Gift(
            id=star_gift.id,
            type=enums.GiftType.UPGRADED,
            can_send_purchase_offer=star_gift.offer_min_stars is not None,
            gift_address=star_gift.gift_address,
            host=types.Chat._parse_chat(client, users.get(raw_host_id) or chats.get(raw_host_id)),
            is_burned=star_gift.burned,
            is_crafted=star_gift.crafted,
            is_premium=star_gift.require_premium,
            is_theme_available=star_gift.theme_available,
            max_upgraded_count=star_gift.availability_total,
            minimum_offer_star_count=star_gift.offer_min_stars,
            model=model,
            symbol=symbol,
            backdrop=backdrop,
            title=star_gift.title,
            name=star_gift.slug,
            unique_gift_number=star_gift.num,
            original_details=original_details,
            owner=types.Chat._parse_chat(client, users.get(raw_owner_id) or chats.get(raw_owner_id)),
            owner_address=star_gift.owner_address,
            owner_name=star_gift.owner_name,
            publisher_chat=types.Chat._parse_chat(client, chats.get(utils.get_raw_peer_id(star_gift.released_by))),
            regular_gift_id=star_gift.gift_id,
            resale_parameters=types.GiftResaleParameters._parse(star_gift.resell_amount, star_gift.resale_ton_only),
            total_upgraded_count=star_gift.availability_issued,
            used_theme_chat_id=utils.get_peer_id(star_gift.theme_peer) if star_gift.theme_peer else None,
            craft_probability_per_mille=star_gift.craft_chance_permille,
            value_amount=star_gift.value_amount,
            value_currency=star_gift.value_currency,
            value_usd_amount=star_gift.value_usd_amount,
            raw=star_gift,
            client=client
        )

    @staticmethod
    async def _parse_received(
        client,
        saved_gift: "raw.types.SavedStarGift",
        receiver: Optional[Union["raw.base.User", "raw.base.Chat"]] = None,
        users: Dict[int, "raw.base.User"] = {},
        chats: Dict[int, "raw.base.Chat"] = {}
    ) -> "Gift":
        if not isinstance(saved_gift, raw.types.SavedStarGift):
            return

        if isinstance(saved_gift.gift, raw.types.StarGift):
            parsed_gift = await Gift._parse_regular(client, saved_gift.gift, users=users, chats=chats)
        elif isinstance(saved_gift.gift, raw.types.StarGiftUnique):
            parsed_gift = await Gift._parse_upgraded(client, saved_gift.gift, users=users, chats=chats)

        raw_from_id = utils.get_raw_peer_id(saved_gift.from_id)

        if saved_gift.msg_id:
            parsed_gift.received_gift_id = str(saved_gift.msg_id)
        elif saved_gift.saved_id:
            parsed_gift.received_gift_id = str(saved_gift.saved_id)

        parsed_gift.date = utils.timestamp_to_datetime(saved_gift.date) or parsed_gift.date
        parsed_gift.receiver = types.Chat._parse_chat(client, receiver) or parsed_gift.receiver
        parsed_gift.is_name_hidden = saved_gift.name_hidden or parsed_gift.is_name_hidden
        parsed_gift.is_saved = not saved_gift.unsaved or parsed_gift.is_saved
        parsed_gift.was_refunded = saved_gift.refunded or parsed_gift.was_refunded
        parsed_gift.can_be_upgraded = saved_gift.can_upgrade or parsed_gift.can_be_upgraded
        parsed_gift.is_pinned = saved_gift.pinned_to_top or parsed_gift.is_pinned
        parsed_gift.is_upgrade_separate = saved_gift.upgrade_separate or parsed_gift.is_upgrade_separate
        parsed_gift.sender = types.Chat._parse_chat(client, users.get(raw_from_id) or chats.get(raw_from_id)) or parsed_gift.sender
        parsed_gift.text = types.FormattedText._parse(client, saved_gift.message) or parsed_gift.text
        parsed_gift.convert_star_count = saved_gift.convert_stars or parsed_gift.convert_star_count
        parsed_gift.upgrade_star_count = saved_gift.upgrade_stars or parsed_gift.upgrade_star_count
        parsed_gift.export_date = utils.timestamp_to_datetime(saved_gift.can_export_at) or parsed_gift.export_date
        parsed_gift.transfer_star_count = saved_gift.transfer_stars or parsed_gift.transfer_star_count
        parsed_gift.next_transfer_date = utils.timestamp_to_datetime(saved_gift.can_transfer_at) or parsed_gift.next_transfer_date
        parsed_gift.next_resale_date = utils.timestamp_to_datetime(saved_gift.can_resell_at) or parsed_gift.next_resale_date
        parsed_gift.craft_date = utils.timestamp_to_datetime(saved_gift.can_craft_at) or parsed_gift.craft_date
        parsed_gift.collection_ids = list(saved_gift.collection_id) if saved_gift.collection_id else parsed_gift.collection_ids
        parsed_gift.prepaid_upgrade_hash = saved_gift.prepaid_upgrade_hash or parsed_gift.prepaid_upgrade_hash
        parsed_gift.drop_original_details_star_count = saved_gift.drop_original_details_stars or parsed_gift.drop_original_details_star_count
        parsed_gift.unique_gift_number = saved_gift.gift_num or parsed_gift.unique_gift_number
        parsed_gift.raw = saved_gift

        return parsed_gift

    @staticmethod
    async def _parse_action(
        client,
        action_gift: Union[
            "raw.types.MessageActionStarGift",
            "raw.types.MessageActionStarGiftUnique"
        ],
        receiver: Optional[Union["raw.base.User", "raw.base.Chat"]] = None,
        users: Dict[int, "raw.base.User"] = {},
        chats: Dict[int, "raw.base.Chat"] = {}
    ) -> "Gift":
        # TODO: fix receiver
        if isinstance(action_gift, raw.types.MessageActionStarGift):
            # auction_acquired
            # upgrade_msg_id
            # peer
            # gift_msg_id

            raw_sender_id = utils.get_raw_peer_id(action_gift.from_id)
            raw_receiver_id = utils.get_raw_peer_id(action_gift.peer)

            parsed_gift = await Gift._parse_regular(client, action_gift.gift, users=users, chats=chats)

            if action_gift.saved_id:
                parsed_gift.received_gift_id = str(action_gift.saved_id)

            parsed_gift.is_name_hidden = action_gift.name_hidden or parsed_gift.is_name_hidden
            parsed_gift.is_saved = action_gift.saved or parsed_gift.is_saved
            parsed_gift.was_converted = action_gift.converted or parsed_gift.was_converted
            parsed_gift.was_upgraded = action_gift.upgraded or parsed_gift.was_upgraded
            parsed_gift.was_refunded = action_gift.refunded or parsed_gift.was_refunded
            parsed_gift.can_be_upgraded = action_gift.can_upgrade or parsed_gift.can_be_upgraded
            parsed_gift.is_upgrade_separate = action_gift.upgrade_separate or parsed_gift.is_upgrade_separate
            parsed_gift.text = types.FormattedText._parse(client, action_gift.message) or parsed_gift.text
            parsed_gift.convert_star_count = action_gift.convert_stars or parsed_gift.convert_star_count
            parsed_gift.upgrade_star_count = action_gift.upgrade_stars or parsed_gift.upgrade_star_count
            parsed_gift.sender = types.Chat._parse_chat(client, users.get(raw_sender_id) or chats.get(raw_sender_id)) or parsed_gift.sender
            parsed_gift.receiver = types.Chat._parse_chat(client, users.get(raw_receiver_id) or chats.get(raw_receiver_id)) or parsed_gift.receiver
            parsed_gift.prepaid_upgrade_hash = action_gift.prepaid_upgrade_hash or parsed_gift.prepaid_upgrade_hash
            parsed_gift.unique_gift_number = action_gift.gift_num or parsed_gift.unique_gift_number
            parsed_gift.raw = action_gift

            return parsed_gift
        elif isinstance(action_gift, raw.types.MessageActionStarGiftUnique):
            # peer

            raw_sender_id = utils.get_raw_peer_id(action_gift.from_id)
            raw_receiver_id = utils.get_raw_peer_id(action_gift.peer)

            parsed_gift = await Gift._parse_upgraded(client, action_gift.gift, users=users, chats=chats)

            if action_gift.from_offer:
                parsed_gift.origin = enums.UpgradedGiftOrigin.OFFER
            elif action_gift.assigned:
                parsed_gift.origin = enums.UpgradedGiftOrigin.BLOCKCHAIN
            elif action_gift.prepaid_upgrade:
                parsed_gift.origin = enums.UpgradedGiftOrigin.GIFTED_UPGRADE
            elif action_gift.resale_amount:
                parsed_gift.origin = enums.UpgradedGiftOrigin.RESALE
            elif action_gift.upgrade:
                parsed_gift.origin = enums.UpgradedGiftOrigin.UPGRADE
            elif action_gift.transferred:
                parsed_gift.origin = enums.UpgradedGiftOrigin.TRANSFER
            elif action_gift.craft:
                parsed_gift.origin = enums.UpgradedGiftOrigin.CRAFT

            if action_gift.saved_id:
                parsed_gift.received_gift_id = str(action_gift.saved_id)

            if isinstance(action_gift.resale_amount, raw.types.StarsAmount):
                parsed_gift.last_resale_currency = "XTR"
                parsed_gift.last_resale_amount = action_gift.resale_amount.amount
            elif isinstance(action_gift.resale_amount, raw.types.StarsTonAmount):
                parsed_gift.last_resale_currency = "TON"
                parsed_gift.last_resale_amount = action_gift.resale_amount.amount

            parsed_gift.was_upgraded = action_gift.upgrade or parsed_gift.was_upgraded
            parsed_gift.is_saved = action_gift.saved or parsed_gift.is_saved
            parsed_gift.was_refunded = action_gift.refunded or parsed_gift.was_refunded
            parsed_gift.export_date = utils.timestamp_to_datetime(action_gift.can_export_at) or parsed_gift.export_date
            parsed_gift.transfer_star_count = action_gift.transfer_stars or parsed_gift.transfer_star_count
            parsed_gift.sender = types.Chat._parse_chat(client, users.get(raw_sender_id) or chats.get(raw_sender_id)) or parsed_gift.sender
            parsed_gift.receiver = types.Chat._parse_chat(client, users.get(raw_receiver_id) or chats.get(raw_receiver_id)) or parsed_gift.receiver
            parsed_gift.next_transfer_date = utils.timestamp_to_datetime(action_gift.can_transfer_at) or parsed_gift.next_transfer_date
            parsed_gift.next_resale_date = utils.timestamp_to_datetime(action_gift.can_resell_at) or parsed_gift.next_resale_date
            parsed_gift.craft_date = utils.timestamp_to_datetime(action_gift.can_craft_at) or parsed_gift.craft_date
            parsed_gift.drop_original_details_star_count = action_gift.drop_original_details_stars or parsed_gift.drop_original_details_star_count
            parsed_gift.raw = action_gift

            return parsed_gift

    @property
    def link(self) -> Optional[str]:
        if not self.name:
            return None

        return f"https://t.me/nft/{self.name}"

    @property
    def owned_gift_id(self) -> Optional[str]:
        if not self.received_gift_id:
            return None

        if self.receiver and self.receiver.type != enums.ChatType.PRIVATE:
            return f"{self.receiver.id}_{self.received_gift_id}"

        return self.received_gift_id

    async def show(self) -> bool:
        """Bound method *show* of :obj:`~pyrogram.types.Gift`.

        Use as a shortcut for:

        .. code-block:: python

            await client.show_gift(
                owned_gift_id="message_id"
            )

        Example:
            .. code-block:: python

                await gift.show()

        Returns:
            ``bool``: On success, True is returned.
        """
        return await self._client.show_gift(
            owned_gift_id=self.owned_gift_id
        )

    async def hide(self) -> bool:
        """Bound method *hide* of :obj:`~pyrogram.types.Gift`.

        Use as a shortcut for:

        .. code-block:: python

            await client.hide_gift(
                owned_gift_id="message_id"
            )

        Example:
            .. code-block:: python

                await gift.hide()

        Returns:
            ``bool``: On success, True is returned.
        """
        return await self._client.hide_gift(
            owned_gift_id=self.owned_gift_id
        )

    async def convert(self) -> bool:
        """Bound method *convert* of :obj:`~pyrogram.types.Gift`.

        .. note::

            For regular gifts only.

        Use as a shortcut for:

        .. code-block:: python

            await client.convert_gift_to_stars(
                owned_gift_id="message_id"
            )

        Example:
            .. code-block:: python

                await gift.convert()

        Returns:
            ``bool``: On success, True is returned.
        """
        return await self._client.convert_gift_to_stars(
            owned_gift_id=self.owned_gift_id
        )

    async def upgrade(self, keep_original_details: Optional[bool] = None, star_count: Optional[int] = None) -> Optional["types.Message"]:
        """Bound method *upgrade* of :obj:`~pyrogram.types.Gift`.

        .. note::

            For regular gifts only.

        Use as a shortcut for:

        .. code-block:: python

            await client.upgrade_gift(
                owned_gift_id="message_id"
            )

        Example:
            .. code-block:: python

                await gift.upgrade()

        Returns:
            :obj:`~pyrogram.types.Message`: On success, the sent message is returned.
        """
        return await self._client.upgrade_gift(
            owned_gift_id=self.owned_gift_id,
            keep_original_details=keep_original_details,
            star_count=star_count
        )

    async def transfer(self, to_chat_id: Union[int, str]) -> Optional["types.Message"]:
        """Bound method *transfer* of :obj:`~pyrogram.types.Gift`.

        .. note::

            For upgraded gifts only.

        Use as a shortcut for:

        .. code-block:: python

            await client.transfer_gift(
                owned_gift_id="message_id",
                new_owner_chat_id=to_chat_id
            )

        Example:
            .. code-block:: python

                await gift.transfer(to_chat_id=123)

        Returns:
            :obj:`~pyrogram.types.Message`: On success, the sent message is returned.
        """
        return await self._client.transfer_gift(
            owned_gift_id=self.owned_gift_id,
            new_owner_chat_id=to_chat_id
        )

    async def wear(self) -> bool:
        """Bound method *wear* of :obj:`~pyrogram.types.Gift`.

        .. note::

            For upgraded gifts only.

        Use as a shortcut for:

        .. code-block:: python

            await client.set_emoji_status(types.EmojiStatus(gift_id=123))

        Example:
            .. code-block:: python

                await gift.wear()

        Returns:
            ``bool``: On success, True is returned.
        """
        return await self._client.set_emoji_status(
            emoji_status=types.EmojiStatus(
                gift_id=self.id
            )
        )

    async def buy(self, new_owner_chat_id: Optional[Union[int, str]] = None, price: Optional["types.GiftResalePrice"] = None) -> Optional["types.Message"]:
        """Bound method *buy* of :obj:`~pyrogram.types.Gift`.

        .. note::

            For upgraded gifts from market only.

        Use as a shortcut for:

        .. code-block:: python

            await app.send_resold_gift(gift_link="https://t.me/nft/NekoHelmet-9215", new_owner_chat_id="me")

        Example:
            .. code-block:: python

                await gift.buy()

        Returns:
            :obj:`~pyrogram.types.Message`: On success, the sent message is returned.
        """
        if new_owner_chat_id is None:
            new_owner_chat_id = "me"

        if price is None:
            if self.resale_parameters.toncoin_only:
                price = types.GiftResalePriceTon(toncoin_cent_count=self.resale_parameters.toncoin_cent_count)
            else:
                price = types.GiftResalePriceStar(star_count=self.resale_parameters.star_count)

        return await self._client.send_resold_gift(
            gift_link=self.link,
            new_owner_chat_id=new_owner_chat_id,
            price=price
        )

    async def send(
        self,
        chat_id: Union[int, str],
        text: Optional[str] = None,
        parse_mode: Optional["enums.ParseMode"] = None,
        entities: Optional[List["types.MessageEntity"]] = None,
        is_private: Optional[bool] = None,
        pay_for_upgrade: Optional[bool] = None,
    ) -> Optional["types.Message"]:
        """Bound method *send* of :obj:`~pyrogram.types.Gift`.

        .. note::

            For regular gifts only.
            May return an error with a message "STARGIFT_USAGE_LIMITED" if the gift was sold out.

        Use as a shortcut for:

        .. code-block:: python

            await client.send_gift(
                chat_id="me",
                gift_id=gift.id
            )

        Example:
            .. code-block:: python

                await gift.send("me")

        Returns:
            :obj:`~pyrogram.types.Message`: On success, the sent message is returned.
        """
        return await self._client.send_gift(
            chat_id=chat_id,
            gift_id=self.id,
            text=text,
            parse_mode=parse_mode,
            entities=entities,
            is_private=is_private,
            pay_for_upgrade=pay_for_upgrade
        )

    async def get_auction_state(self) -> "types.GiftAuctionState":
        """Bound method *get_auction_state* of :obj:`~pyrogram.types.Gift`.

        .. note::

            For regular gifts only.

        Use as a shortcut for:

        .. code-block:: python

            await client.get_gift_auction_state(
                auction_id=gift.id
            )

        Returns:
            :obj:`~pyrogram.types.GiftAuctionState`: The auction state of the gift.
        """

        return await self._client.get_gift_auction_state(auction_id=self.id)

    async def send_purchase_offer(
        self,
        price: "types.GiftResalePrice",
        duration: int,
        paid_message_star_count: Optional[int] = None
    ) -> Optional["types.Message"]:
        """Shortcut for method :obj:`~pyrogram.Client.send_gift_purchase_offer` will automatically fill method attributes:

        * owner_id
        * gift_id

        Parameters:
            price (:obj:`~pyrogram.types.GiftResalePrice`):
                The price that the user agreed to pay for the gift.

            duration (``int``):
                Duration of the offer, in seconds.
                Must be one of 21600, 43200, 86400, 129600, 172800, or 259200.

            paid_message_star_count (``int``, *optional*):
                The number of Telegram Stars the user agreed to pay additionally for sending of the offer message to the current gift owner.
                Pass User.paid_message_star_count for users and None otherwise.

        Returns:
            :obj:`~pyrogram.types.Message`: On success, the sent Message is returned.
        """
        if not self.can_send_purchase_offer:
            raise ValueError("This gift cannot be purchased via offer.")

        if not self.owner:
            raise ValueError("Gift owner not found.")

        return await self._client.send_gift_purchase_offer(
            owner_id=self.owner.id,
            gift_name=self.name,
            price=price,
            duration=duration,
            paid_message_star_count=paid_message_star_count
        )
