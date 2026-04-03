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
from typing import Tuple

import pyrogram
from pyrogram import raw
from pyrogram.errors import ChannelInvalid, ChannelPrivate, PersistentTimestampInvalid, PersistentTimestampOutdated
from pyrogram.utils import ZERO_CHANNEL_ID

log = logging.getLogger(__name__)


class RecoverGaps:
    async def recover_gaps(self: "pyrogram.Client") -> Tuple[int, int]:
        """Restores updates for the time while the client was offline.

        .. note::

            To use this method, you must set the ``Client.skip_updates`` and ``Client.in_memory`` parameter to False, otherwise updates state saving and recovery will not work.

        .. include:: /_includes/usable-by/users-bots.rst

        Returns:
            ``tuple``: The number of messages and updates recovered is returned.
        """
        message_updates_counter = 0
        other_updates_counter = 0

        if self.skip_updates:
            log.debug("Recover gaps disabled in client params. Skipping recovery")
            return (message_updates_counter, other_updates_counter)

        states = await self.storage.update_state()

        if not states:
            log.info("No states found, skipping recovery")
            return (message_updates_counter, other_updates_counter)

        log.info("Started gaps recovering...")

        for local_state in states:
            id, local_pts, local_qts, local_date, local_seq = local_state

            prev_pts = 0

            while True:
                try:
                    diff = await self.invoke(
                        raw.functions.updates.GetChannelDifference(
                            channel=await self.resolve_peer(id),
                            filter=raw.types.ChannelMessagesFilterEmpty(),
                            pts=local_pts,
                            limit=10000,
                            force=False
                        ) if id < ZERO_CHANNEL_ID else
                        raw.functions.updates.GetDifference(
                            pts=local_pts,
                            date=local_date,
                            qts=0
                        )
                    )
                except (ChannelPrivate, ChannelInvalid):
                    await self.storage.update_state(id)
                    break
                except (PersistentTimestampOutdated, PersistentTimestampInvalid):
                    continue

                if isinstance(diff, raw.types.updates.DifferenceEmpty):
                    await self.storage.update_state(
                        (
                            id,
                            local_pts,
                            None,
                            diff.date,
                            diff.seq
                        )
                    )
                    break
                elif isinstance(diff, raw.types.updates.DifferenceTooLong):
                    local_pts = diff.pts
                    await self.storage.update_state(
                        (
                            id,
                            local_pts,
                            None,
                            local_date,
                            local_seq
                        )
                    )
                    continue
                elif isinstance(diff, raw.types.updates.Difference):
                    local_pts = diff.state.pts
                    local_date = diff.state.date
                    local_seq = diff.state.seq
                elif isinstance(diff, raw.types.updates.DifferenceSlice):
                    local_pts = diff.intermediate_state.pts
                    local_date = diff.intermediate_state.date
                    local_seq = diff.intermediate_state.seq

                    if prev_pts == local_pts:
                        break

                    prev_pts = local_pts
                elif isinstance(diff, raw.types.updates.ChannelDifferenceEmpty):
                    await self.storage.update_state(
                        (
                            id,
                            diff.pts,
                            None,
                            local_date,
                            local_seq
                        )
                    )
                    break
                elif isinstance(diff, raw.types.updates.ChannelDifferenceTooLong):
                    local_pts = diff.dialog.pts
                    await self.storage.update_state(
                        (
                            id,
                            local_pts,
                            None,
                            local_date,
                            local_seq
                        )
                    )
                    continue
                elif isinstance(diff, raw.types.updates.ChannelDifference):
                    local_pts = diff.pts

                users = {i.id: i for i in diff.users}
                chats = {i.id: i for i in diff.chats}

                for message in diff.new_messages:
                    message_updates_counter += 1
                    self.dispatcher.updates_queue.put_nowait(
                        (
                            raw.types.UpdateNewMessage(
                                message=message,
                                pts=local_pts,
                                pts_count=-1
                            ),
                            users,
                            chats
                        )
                    )

                for update in diff.other_updates:
                    other_updates_counter += 1
                    self.dispatcher.updates_queue.put_nowait(
                        (update, users, chats)
                    )

                if isinstance(diff, (raw.types.updates.Difference, raw.types.updates.ChannelDifference)):
                    break

            await self.storage.update_state(
                (
                    id,
                    local_pts,
                    None,
                    local_date,
                    local_seq
                )
            )

        log.info("Recovered %s messages and %s updates", message_updates_counter, other_updates_counter)
        return (message_updates_counter, other_updates_counter)
