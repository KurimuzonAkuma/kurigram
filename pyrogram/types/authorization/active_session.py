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
from typing import Optional

from pyrogram import raw, utils

from ..object import Object


class ActiveSession(Object):
    """Contains information about one session in a Telegram application used by the current user. Sessions must be shown to the user in the returned order.

    Parameters:
        id (``int``):
            Session identifier.

        device_model (``str``):
            Model of the device the application has been run or is running on, as provided by the application.

        platform (``str``):
            Operating system the application has been run or is running on, as provided by the application.

        system_version (``str``):
            Version of the operating system the application has been run or is running on, as provided by the application.

        api_id (``int``):
            Telegram API identifier, as provided by the application.

        application_name (``str``):
            Name of the application, as provided by the application.

        application_version (``str``):
            The version of the application, as provided by the application.

        log_in_date (:py:obj:`~datetime.datetime`, *optional*):
            Point in time (Unix timestamp) when the user has logged in.

        last_active_date (:py:obj:`~datetime.datetime`, *optional*):
            Point in time (Unix timestamp) when the session was last used.

        ip_address (``str``):
            IP address from which the session was created, in human-readable format.

        location (``str``):
            A human-readable description of the location from which the session was created, based on the IP address.

        country (``str``):
            Country determined from IP.

        region (``str``):
            Region determined from IP.

        can_accept_secret_chats (``bool``):
            True, if incoming secret chats can be accepted by the session.

        can_accept_calls (``bool``):
            True, if incoming calls can be accepted by the session.

        is_current (``bool``):
            True, if this session is the current session.

        is_password_pending (``bool``):
            True, if a 2-step verification password is needed to complete authorization of the session.

        is_unconfirmed (``bool``):
            True, if the session wasn't confirmed from another session.

        is_official_application (``bool``):
            True, if the application is an official application or uses the api_id of an official application.

    """

    def __init__(
        self,
        *,
        id: Optional[int] = None,
        device_model: Optional[str] = None,
        platform: Optional[str] = None,
        system_version: Optional[str] = None,
        api_id: Optional[int] = None,
        application_name: Optional[str] = None,
        application_version: Optional[str] = None,
        log_in_date: Optional[datetime] = None,
        last_active_date: Optional[datetime] = None,
        ip_address: Optional[str] = None,
        location: Optional[str] = None,
        country: Optional[str] = None,
        region: Optional[str] = None,
        can_accept_secret_chats: Optional[bool] = None,
        can_accept_calls: Optional[bool] = None,
        is_current: Optional[bool] = None,
        is_password_pending: Optional[bool] = None,
        is_unconfirmed: Optional[bool] = None,
        is_official_application: Optional[bool] = None
    ):
        super().__init__()

        self.id = id
        self.device_model = device_model
        self.platform = platform
        self.system_version = system_version
        self.api_id = api_id
        self.application_name = application_name
        self.application_version = application_version
        self.log_in_date = log_in_date
        self.last_active_date = last_active_date
        self.ip_address = ip_address
        self.location = location
        self.country = country
        self.region = region
        self.can_accept_secret_chats = can_accept_secret_chats
        self.can_accept_calls = can_accept_calls
        self.is_current = is_current
        self.is_password_pending = is_password_pending
        self.is_unconfirmed = is_unconfirmed
        self.is_official_application = is_official_application

    @staticmethod
    def _parse(session: "raw.types.Authorization") -> "ActiveSession":
        return ActiveSession(
            id=session.hash,
            device_model=session.device_model,
            platform=session.platform or None,
            system_version=session.system_version,
            api_id=session.api_id,
            application_name=session.app_name,
            application_version=session.app_version,
            log_in_date=utils.timestamp_to_datetime(session.date_created),
            last_active_date=utils.timestamp_to_datetime(session.date_active),
            ip_address=session.ip or None,
            location=session.region or None,
            country=session.country or None,
            region=session.region or None,
            can_accept_secret_chats=not getattr(session, "encrypted_requests_disabled", False),
            can_accept_calls=not getattr(session, "call_requests_disabled", False),
            is_current=getattr(session, "current", None),
            is_password_pending=getattr(session, "password_pending", None),
            is_unconfirmed=getattr(session, "unconfirmed", None),
            is_official_application=getattr(session, "official_app", None)
        )

    async def reset(self):
        """Bound method *reset* of :obj:`~pyrogram.types.ActiveSession`.

        Use as a shortcut for:

        .. code-block:: python

            await client.reset_session(123456789)

        Example:
            .. code-block:: python

                await session.reset()

        Returns:
            True on success.

        Raises:
            RPCError: In case of a Telegram RPC error.
        """

        return await self._client.reset_session(self.id)
