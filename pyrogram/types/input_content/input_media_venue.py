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

from .input_media import InputMedia


class InputMediaVenue(InputMedia):
    """Represents a venue to be sent.

    Parameters:
        latitude (``float``):
            Latitude of the location.

        longitude (``float``):
            Longitude of the location.

        title (``str``):
            Name of the venue.

        address (``str``):
            Address of the venue.

        foursquare_id (``str``, *optional*):
            Foursquare identifier of the venue.

        foursquare_type (``str``, *optional*):
            Foursquare type of the venue, if known.
            (For example, “arts_entertainment/default”, “arts_entertainment/aquarium” or “food/icecream”.)

        google_place_id (``str``, *optional*):
            Google Places identifier of the venue.

        google_place_type (``str``, *optional*):
            Google Places type of the venue.
            Google Places type of the venue. (See `supported types <https://developers.google.com/places/web-service/supported_types>`__.)
    """

    def __init__(
        self,
        latitude: float,
        longitude: float,
        title: str,
        address: str,
        *,
        foursquare_id: Optional[str] = None,
        foursquare_type: Optional[str] = None,
        google_place_id: Optional[str] = None,
        google_place_type: Optional[str] = None,
    ):
        super().__init__()

        self.latitude = latitude
        self.longitude = longitude
        self.title = title
        self.address = address
        self.foursquare_id = foursquare_id
        self.foursquare_type = foursquare_type
        self.google_place_id = google_place_id
        self.google_place_type = google_place_type

    async def write(self, **kwargs) -> "raw.types.InputMediaVenue":
        venue_id = ""
        venue_type = ""
        provider = ""

        if any(
            [
                self.google_place_id,
                self.google_place_type,
            ]
        ):
            provider = "gplaces"
            venue_id = self.google_place_id
            venue_type = self.google_place_type
        elif any(
            [
                self.foursquare_id,
                self.foursquare_type,
            ]
        ):
            provider = "foursquare"
            venue_id = self.foursquare_id
            venue_type = self.foursquare_type

        return raw.types.InputMediaVenue(
            geo_point=raw.types.InputGeoPoint(
                lat=self.latitude,
                long=self.longitude,
            ),
            title=self.title,
            address=self.address,
            provider=provider,
            venue_id=venue_id,
            venue_type=venue_type,
        )
