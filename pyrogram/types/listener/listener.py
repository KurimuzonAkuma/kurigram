from asyncio import Future
from dataclasses import dataclass
from typing import Callable, Optional, Union

from pyrogram.filters import Filter

from .identifier import Identifier
from .listener_types import ListenerTypes


@dataclass
class Listener:
    listener_type: ListenerTypes
    filters: Optional[Filter]
    unallowed_click_alert: Union[bool, str]
    identifier: Identifier
    future: Optional[Future] = None
    callback: Optional[Callable] = None
