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

import pyrogram
from pyrogram import raw
from pyrogram.utils import compute_password_check


class SetCloudPasswordEmail:
    async def set_cloud_password_email(
        self: "pyrogram.Client",
        current_password: str,
        email: str
    ) -> bool:
        """Set or change the recovery email for the current cloud password.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            current_password (``str``):
                Your current cloud password.

            email (``str``):
                The recovery email to attach to the current cloud password.

        Returns:
            ``bool``: True on success.

        Raises:
            ValueError: In case there is no cloud password to update.

        Example:
            .. code-block:: python

                await app.set_cloud_password_email("current_password", "user@email.com")

        Note:
            Telegram may send a verification code to the supplied email and return
            ``EMAIL_UNCONFIRMED_X``. In that case, use
            :meth:`~pyrogram.Client.confirm_cloud_password_email` to confirm it.
        """
        r = await self.invoke(raw.functions.account.GetPassword())

        if not r.has_password:
            raise ValueError("There is no cloud password to update")

        await self.invoke(
            raw.functions.account.UpdatePasswordSettings(
                password=compute_password_check(r, current_password),
                new_settings=raw.types.account.PasswordInputSettings(
                    email=email
                )
            )
        )

        return True
