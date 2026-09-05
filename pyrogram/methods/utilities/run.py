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

import inspect
from typing import List

import pyrogram
from pyrogram.methods.utilities.idle import idle


class Run:
    def run(
        self: "pyrogram.Client", *,
        use_qr: bool = False,
        except_ids: List[int] = [],
    ):
        """Start the client, idle the main script and finally stop the client.

        When calling this method without any argument it acts as a convenience method that calls
        :meth:`~pyrogram.Client.start`, :meth:`~pyrogram.idle` and :meth:`~pyrogram.Client.stop` in sequence.
        It makes running a single client less verbose.

        If you want to run multiple clients at once, see :meth:`pyrogram.compose`.

        Parameters:
            use_qr (``bool``, *optional*):
                Use QR code authorization instead of the interactive prompt.
                For new authorizations only.
                Defaults to False.

            except_ids (List of ``int``, *optional*):
                List of already logged-in user IDs, to prevent logging in twice with the same user.

        Raises:
            ConnectionError: In case you try to run an already started client.

        Example:
            .. code-block:: python

                from pyrogram import Client

                app = Client("my_account")
                ...  # Set handlers up
                app.run()
        """
        run = self.loop.run_until_complete

        if inspect.iscoroutinefunction(self.start):
            run(self.start(use_qr=use_qr, except_ids=except_ids))
            run(idle())
            run(self.stop())
        else:
            # `self.start`/`self.stop` are declared `async def`, so `ty` sees a plain
            #  coroutine function here: it can't know `pyrogram.sync` (pyrogram/sync.py)
            #  may have patched them into blocking sync wrappers, which is exactly what
            #  the `iscoroutinefunction` check above is testing for.
            self.start(use_qr=use_qr, except_ids=except_ids)  # ty: ignore[unused-awaitable]
            run(idle())
            self.stop()  # ty: ignore[unused-awaitable]
