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

"""Every handler names the type it is handed, and that type is an `Update`.

A callback handed something that is not an `Update` can neither be filtered on its sender
nor stop the chain, because both live on `Update`. Neither failure announces itself: the
sender filters answer `False`, which reads as "no sender" rather than "never looked".
"""

import inspect
import re
import typing
from typing import Any, Final, FrozenSet, Iterator, List, Optional, Pattern, Set, Tuple, Type

from pyrogram import handlers, types
from pyrogram.types import Update

# The `Other parameters:` block of a handler docstring names the type the callback is
#  handed, which is the same claim the annotation makes a few lines below it.
_DOCUMENTED_TYPE: Final[Pattern[str]] = re.compile(r":obj:`~pyrogram\.types\.([A-Za-z]+)`")

_OTHER_PARAMETERS: Final[str] = "Other parameters:"

# The callbacks handed something other than a parsed update: `Handler` takes a bare
#  `Callable`, `Start`/`Stop` the client, `Connect`/`Disconnect` the session it opened, and
#  `Error`/`RawUpdate` the TL object before anything has parsed it.
_TAKES_NO_PARSED_UPDATE: Final[FrozenSet[str]] = frozenset(
    {
        "ConnectHandler",
        "DisconnectHandler",
        "ErrorHandler",
        "Handler",
        "RawUpdateHandler",
        "StartHandler",
        "StopHandler",
    }
)


def handler_classes() -> Iterator[Type[handlers.Handler]]:
    """Every handler the package exports, the base class included."""
    for name in sorted(vars(handlers)):
        one = getattr(handlers, name)

        if inspect.isclass(one) and issubclass(one, handlers.Handler):
            yield one


def name_of(annotation: Any) -> str:
    """The last component of what an annotation names, whether or not it is still a string.

    Handler modules import `types` under `TYPE_CHECKING` only, so their annotations survive
    as `ForwardRef`s and `typing.get_type_hints` cannot evaluate them.
    """
    written = getattr(annotation, "__forward_arg__", None)

    return (written or annotation.__name__).split(".")[-1]


def handed_to(handler: Type[handlers.Handler]) -> Optional[str]:
    """The type the callback of `handler` is handed, or `None` when it is handed no update.

    `List[X]` reads as `X`: the two deleted-message handlers are given the whole batch at
    once. The element is what a sender filter would read, and the list carries neither that
    nor `stop_propagation()`: a separate shape, and a separate decision.
    """
    callback = inspect.signature(handler.__init__).parameters["callback"].annotation
    arguments = typing.get_args(callback)

    if not arguments or len(arguments[0]) < 2:
        return None

    update = arguments[0][1]

    return name_of(typing.get_args(update)[0] if typing.get_origin(update) is list else update)


def documented_by(handler: Type[handlers.Handler]) -> Set[str]:
    """The `pyrogram.types` names the handler's `Other parameters:` block points at."""
    documentation: str = handler.__doc__ or ""

    if _OTHER_PARAMETERS not in documentation:
        return set()

    return set(_DOCUMENTED_TYPE.findall(documentation.split(_OTHER_PARAMETERS)[-1]))


def handlers_with_an_update() -> List[Tuple[str, str]]:
    return [
        (handler.__name__, handed_to(handler))
        for handler in handler_classes()
        if handler.__name__ not in _TAKES_NO_PARSED_UPDATE
    ]


def test_every_handler_is_handed_an_update() -> None:
    """A type that reaches a handler without being an `Update` is filtered against silently.

    `PurchasedPaidMedia`, `ManagedBotUpdated` and `BusinessConnection` were `Object` alone,
    so `filters.me` answered `False` for all three and their callbacks could not call
    `stop_propagation()` at all.
    """
    not_updates = sorted(
        "{}: {}".format(name, handed)
        for name, handed in handlers_with_an_update()
        if not issubclass(getattr(types, handed), Update)
    )

    assert not not_updates, "handlers handed something that is not an `Update` ({}):\n{}".format(
        len(not_updates),
        "\n".join(not_updates),
    )


def test_every_handler_documents_the_type_it_annotates() -> None:
    """The docstring and the annotation are two copies of one claim, so they drift apart.

    `BusinessConnectionHandler` documented `BusinessConnection` while annotating
    `ManagedBotUpdated`, which is what an IDE showed the caller.
    """
    disagreeing = sorted(
        "{}: documents {}, annotates {}".format(name, sorted(documented) or "nothing", handed)
        for name, handed, documented in (
            (name, handed, documented_by(getattr(handlers, name)))
            for name, handed in handlers_with_an_update()
        )
        if documented != {handed}
    )

    assert not disagreeing, "handlers documenting a type they do not annotate ({}):\n{}".format(
        len(disagreeing),
        "\n".join(disagreeing),
    )


def test_the_sweep_reads_the_handlers_it_claims_to() -> None:
    """A signature this stops being able to read would leave both rules passing over nothing."""
    handed = dict(handlers_with_an_update())

    assert len(handed) > 20
    assert handed["PurchasedPaidMediaHandler"] == "PurchasedPaidMedia"
    assert handed["DeletedMessagesHandler"] == "Message"
    assert handed["UserStatusHandler"] == "User"


def test_every_exemption_names_a_handler_that_exists() -> None:
    """An exemption left behind by a rename exempts nothing and hides the next omission."""
    exported = {handler.__name__ for handler in handler_classes()}

    assert _TAKES_NO_PARSED_UPDATE <= exported, sorted(_TAKES_NO_PARSED_UPDATE - exported)
