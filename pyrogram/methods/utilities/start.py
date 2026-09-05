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
from typing import List

import pyrogram
from pyrogram import raw
from pyrogram.storage import UpdateState

log = logging.getLogger(__name__)


class Start:
    async def start(
        self: "pyrogram.Client", *,
        use_qr: bool = False,
        except_ids: List[int] = [],
    ) -> "pyrogram.Client":
        """Start the client.

        This method connects the client to Telegram and, in case of new sessions, automatically manages the
        authorization process using an interactive prompt.

        .. note::

            You should install ``qrcode`` package if you want to use QR code authorization.

        Parameters:
            use_qr (``bool``, *optional*):
                Use QR code authorization instead of the interactive prompt.
                For new authorizations only.
                Defaults to False.

            except_ids (List of ``int``, *optional*):
                List of already logged-in user IDs, to prevent logging in twice with the same user.

        Returns:
            :obj:`~pyrogram.Client`: The started client itself.

        Raises:
            ConnectionError: In case you try to start an already started client.

        Example:
            .. code-block:: python

                import asyncio

                from pyrogram import Client


                async def main():
                    app = Client("my_account")

                    await app.start()
                    ...  # Invoke API methods
                    await app.stop()

                asyncio.run(main())
        """
        self.load_plugins()

        is_authorized = await self.connect()

        try:
            if not is_authorized:
                if use_qr:
                    try:
                        import qrcode  # ty: ignore[unresolved-import] - optional, not a project dependency
                        await self.authorize_qr(except_ids=except_ids)
                    except ImportError:
                        log.warning("qrcode package not found, falling back to authorization prompt")
                        await self.authorize()
                else:
                    await self.authorize()

            if self.takeout and not await self.storage.is_bot():
                self.takeout_id = (await self.invoke(raw.functions.account.InitTakeoutSession())).id
                log.info("Takeout session %s initiated", self.takeout_id)

            state = await self.invoke(raw.functions.updates.GetState())
            local_state = await self.storage.get_update_states(0)

            if not local_state:
                await self.storage.set_update_state(
                    UpdateState(0, state.pts, state.qts, state.date, state.seq)
                )
                await self.storage.save()
        except (Exception, KeyboardInterrupt):
            await self.disconnect()
            raise
        else:
            self.me = await self.get_me()
            await self.initialize()

            return self
