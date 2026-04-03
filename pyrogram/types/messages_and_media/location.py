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

from typing import Optional, Union

from pyrogram import raw
from ..object import Object


class Location(Object):
    """A point on the map.

    Parameters:
        longitude (``float``, *optional*):
            Longitude as defined by sender.

        latitude (``float``, *optional*):
            Latitude as defined by sender.

        accuracy_radius (``int``, *optional*):
            The estimated horizontal accuracy of the location, in meters as defined by the sender.

        address (``str``, *optional*):
            Textual description of the address (mandatory).

        live_period (``int``, *optional*):
            For live locations, the time relative to the message send date, for which the location can be updated, in seconds.

        heading (``int``, *optional*):
            For live locations, a direction in which the location moves, in degrees; 1-360.

        proximity_alert_radius (``int``, *optional*):
            For live locations, a maximum distance to another chat member for proximity alerts, in meters (0-100000).
    """

    def __init__(
        self,
        *,
        longitude: Optional[float] = None,
        latitude: Optional[float] = None,
        accuracy_radius: Optional[int] = None,
        address: Optional[str] = None,
        live_period: Optional[int] = None,
        heading: Optional[int] = None,
        proximity_alert_radius: Optional[int] = None
    ):
        super().__init__()

        self.longitude = longitude
        self.latitude = latitude
        self.accuracy_radius = accuracy_radius
        self.address = address
        self.live_period = live_period
        self.heading = heading
        self.proximity_alert_radius = proximity_alert_radius

    @staticmethod
    def _parse(geo_point: "raw.types.GeoPoint") -> Optional["Location"]:
        if isinstance(geo_point, raw.types.GeoPoint):
            return Location(
                longitude=geo_point.long,
                latitude=geo_point.lat,
                accuracy_radius=geo_point.accuracy_radius,
            )

    @staticmethod
    def _parse_business(location: "raw.types.BusinessLocation") -> "Location":
        if isinstance(location, raw.types.BusinessLocation):
            longitude = None
            latitude = None
            accuracy_radius = None

            if isinstance(location.geo_point, raw.types.GeoPoint):
                longitude = location.geo_point.long
                latitude = location.geo_point.lat
                accuracy_radius = location.geo_point.accuracy_radius

            return Location(
                longitude=longitude,
                latitude=latitude,
                accuracy_radius=accuracy_radius,
                address=location.address
            )

    @staticmethod
    def _parse_media(media: "raw.types.MessageMediaGeoLive") -> Optional["Location"]:
        if isinstance(media, raw.types.MessageMediaGeoLive):
            parsed_location = Location._parse(media.geo)

            parsed_location.live_period = media.period
            parsed_location.heading = media.heading
            parsed_location.proximity_alert_radius = media.proximity_notification_radius

            return parsed_location
