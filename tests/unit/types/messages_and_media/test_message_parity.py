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

"""Every `Message.reply_*` and `Message.answer_*` shortcut accepts what its target accepts.

A shortcut that omits a parameter of the `Client.send_*` it wraps cannot reach that feature at
all, and nothing else reports the gap: both signatures are valid on their own, and the omission
only shows up as a caller wondering why the option has no effect.
"""

import inspect
import re
import sys
from types import ModuleType
from typing import Final, Iterator, List, NamedTuple, Set

import pytest

from pyrogram import Client, types


class Shortcut(NamedTuple):
    """A bound method on `Message` and the client method its docstring says it wraps."""

    name: str
    target_name: str


_TARGET: Final["re.Pattern[str]"] = re.compile(r"Shortcut for method :obj:`~pyrogram\.Client\.(\w+)`")

# The shortcut's own docstring lists what it fills from `self`, one bullet per attribute.
_FILLED_FROM_SELF: Final["re.Pattern[str]"] = re.compile(r"^\* (\w+)$", re.MULTILINE)

# Each `send_*` module warns about its own retired parameters with this exact wording, so which
#  ones are retired is read off the target rather than listed here. A name can be deprecated in
#  one target and current in another: `parse_mode` only feeds `quote_parse_mode` in
#  `send_contact`, while in `send_photo` it parses the caption.
_DEPRECATED: Final["re.Pattern[str]"] = re.compile(r"`(\w+)` is deprecated")


def shortcut_names() -> List[str]:
    return sorted(name for name in vars(types.Message) if name.startswith(("reply_", "answer_")))


def shortcuts() -> Iterator[Shortcut]:
    for name in shortcut_names():
        match = _TARGET.search(inspect.getdoc(vars(types.Message)[name]) or "")

        if match is not None:
            yield Shortcut(name, match.group(1))


_SHORTCUTS: Final[List[Shortcut]] = list(shortcuts())


def filled_from_self(shortcut: Shortcut) -> Set[str]:
    return set(_FILLED_FROM_SELF.findall(inspect.getdoc(getattr(types.Message, shortcut.name)) or ""))


def deprecated_in(module: ModuleType) -> Set[str]:
    return set(_DEPRECATED.findall(inspect.getsource(module)))


def parameters_the_caller_must_supply(shortcut: Shortcut) -> List[str]:
    target = getattr(Client, shortcut.target_name)
    ignored: Set[str] = filled_from_self(shortcut) | deprecated_in(sys.modules[target.__module__]) | {"self"}

    return [name for name in inspect.signature(target).parameters if name not in ignored]


def test_every_shortcut_is_discovered() -> None:
    # The scan reads the docstring, so a reworded first line would quietly drop a method from
    #  every check below and leave the suite green.
    discovered = {shortcut.name for shortcut in _SHORTCUTS}

    assert sorted(discovered) == shortcut_names()


@pytest.mark.parametrize("shortcut", _SHORTCUTS, ids=[shortcut.name for shortcut in _SHORTCUTS])
def test_a_shortcut_names_a_client_method_that_exists(shortcut: Shortcut) -> None:
    assert hasattr(Client, shortcut.target_name)


@pytest.mark.parametrize("shortcut", _SHORTCUTS, ids=[shortcut.name for shortcut in _SHORTCUTS])
def test_a_shortcut_accepts_everything_its_target_accepts(shortcut: Shortcut) -> None:
    accepted = set(inspect.signature(getattr(types.Message, shortcut.name)).parameters)
    missing = [name for name in parameters_the_caller_must_supply(shortcut) if name not in accepted]

    assert not missing


@pytest.mark.parametrize("shortcut", _SHORTCUTS, ids=[shortcut.name for shortcut in _SHORTCUTS])
def test_a_shortcut_forwards_everything_it_accepts(shortcut: Shortcut) -> None:
    # A parameter in the signature that the call never passes on is worse than a missing one:
    #  the caller gets no error and the option is dropped.
    source = inspect.getsource(getattr(types.Message, shortcut.name))
    accepted = inspect.signature(getattr(types.Message, shortcut.name)).parameters
    wanted = set(parameters_the_caller_must_supply(shortcut))

    dropped = [
        name
        for name in accepted
        if name in wanted and not re.search(rf"^\s+{name}={name},?$", source, re.MULTILINE)
    ]

    assert not dropped
