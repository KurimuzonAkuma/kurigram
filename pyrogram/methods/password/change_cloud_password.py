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

import os
from typing import Optional

import pyrogram
from pyrogram import raw
from pyrogram.utils import compute_password_hash, compute_password_check, btoi, itob


class ChangeCloudPassword:
    async def change_cloud_password(
        self: "pyrogram.Client",
        current_password: str,
        new_password: Optional[str] = None,
        new_hint: str = "",
        new_email: Optional[str] = None
    ) -> bool:
        """Change your Two-Step Verification password and/or recovery email.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            current_password (``str``):
                Your current password.

            new_password (``str``, *optional*):
                Your new password.

            new_hint (``str``, *optional*):
                A new password hint.

            new_email (``str``, *optional*):
                New recovery email for the current cloud password.

        Returns:
            ``bool``: True on success.

        Raises:
            ValueError: In case there is no cloud password to change.

        Example:
            .. code-block:: python

                # Change password only
                await app.change_cloud_password("current_password", "new_password")

                # Change password and hint
                await app.change_cloud_password("current_password", "new_password", new_hint="hint")

                # Change only recovery email
                await app.change_cloud_password("current_password", new_email="user@email.com")
        """
        r = await self.invoke(raw.functions.account.GetPassword())

        if not r.has_password:
            raise ValueError("There is no cloud password to change")

        if not new_password and not new_email:
            raise ValueError("You must provide new_password or new_email")

        settings = {}

        if new_password:
            r.new_algo.salt1 += os.urandom(32)
            new_hash = btoi(compute_password_hash(r.new_algo, new_password))
            new_hash = itob(pow(r.new_algo.g, new_hash, btoi(r.new_algo.p)))
            settings.update(
                new_algo=r.new_algo,
                new_password_hash=new_hash,
                hint=new_hint
            )

        if new_email is not None:
            settings["email"] = new_email

        await self.invoke(
            raw.functions.account.UpdatePasswordSettings(
                password=compute_password_check(r, current_password),
                new_settings=raw.types.account.PasswordInputSettings(**settings)
            )
        )

        return True
