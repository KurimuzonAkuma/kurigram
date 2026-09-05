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
from pathlib import Path
from typing import Callable, Final, List, Set

import pytest

import pyrogram
from pyrogram import filters
from pyrogram.methods import decorators
from pyrogram.methods.decorators.handler_type import HandlerType


def _decorator_names() -> List[str]:
    names: Set[str] = set()

    for _, decorator_class in inspect.getmembers(decorators, inspect.isclass):
        for method_name, _ in inspect.getmembers(decorator_class, inspect.isfunction):
            if method_name.startswith("on_"):
                names.add(method_name)

    return sorted(names)


# `on_error` takes an `exceptions` argument between the two, so it shifts differently
#  and is covered on its own below.
_FILTERED_SIGNATURE: Final[List[str]] = ["self", "filters", "group"]


def _filtered_decorator_names() -> List[str]:
    return [
        name
        for name in _decorator_names()
        if list(inspect.signature(getattr(pyrogram.Client, name)).parameters) == _FILTERED_SIGNATURE
    ]


def _module_names() -> List[str]:
    package_directory = Path(decorators.__file__).parent

    return sorted(path.stem for path in package_directory.glob("on_*.py"))


def test_every_module_contributes_the_decorator_named_after_it() -> None:
    assert _decorator_names() == _module_names()


@pytest.mark.parametrize("decorator_name", _decorator_names())
def test_decorator_gives_back_the_function_it_was_handed(decorator_name: str) -> None:
    async def handler(client: pyrogram.Client, update: pyrogram.types.Update) -> None: ...

    decorated = getattr(pyrogram.Client, decorator_name)()(handler)

    assert decorated is handler
    assert len(handler.handlers) == 1


@pytest.mark.parametrize("decorator_name", _decorator_names())
def test_decorator_binds_the_callback_signature_to_one_type_variable(decorator_name: str) -> None:
    # A module added later starts from a sibling that still reads `-> Callable`, and the two
    #  tests above pass either way: they check what the decorator returns, not what it promises.
    decorator = getattr(pyrogram.Client, decorator_name)

    assert inspect.signature(decorator).return_annotation == Callable[[HandlerType], HandlerType]


@pytest.fixture
def handler() -> HandlerType:
    async def callback(client: pyrogram.Client, update: pyrogram.types.Update) -> None: ...

    return callback


# The decorators are methods, so an unbound call shifts the arguments one slot to the left
#  and a call by keyword does not. All three forms are documented, so all three are checked.
@pytest.mark.parametrize("decorator_name", _filtered_decorator_names())
def test_the_positional_form_stores_the_filter_and_the_group(
    decorator_name: str,
    handler: HandlerType,
) -> None:
    getattr(pyrogram.Client, decorator_name)(filters.text, 1)(handler)

    (built, group), = handler.handlers

    assert group == 1
    assert built.filters is filters.text


@pytest.mark.parametrize("decorator_name", _filtered_decorator_names())
def test_the_mixed_form_stores_the_filter_and_the_group(
    decorator_name: str,
    handler: HandlerType,
) -> None:
    getattr(pyrogram.Client, decorator_name)(filters.text, group=1)(handler)

    (built, group), = handler.handlers

    assert group == 1
    assert built.filters is filters.text


@pytest.mark.parametrize("decorator_name", _filtered_decorator_names())
def test_the_keyword_form_stores_the_filter_and_the_group(
    decorator_name: str,
    handler: HandlerType,
) -> None:
    getattr(pyrogram.Client, decorator_name)(filters=filters.text, group=1)(handler)

    (built, group), = handler.handlers

    assert group == 1
    assert built.filters is filters.text


@pytest.mark.parametrize("decorator_name", sorted(set(_decorator_names()) - set(_filtered_decorator_names())))
def test_a_decorator_called_with_no_arguments_stores_the_default_group(
    decorator_name: str,
    handler: HandlerType,
) -> None:
    getattr(pyrogram.Client, decorator_name)()(handler)

    (_, group), = handler.handlers

    assert group == 0


# `on_error` carries an `exceptions` argument its siblings do not, so an unbound call
#  shifts three slots instead of two.
def test_on_error_reads_the_positional_form(handler: HandlerType) -> None:
    pyrogram.Client.on_error(ValueError, filters.text, 1)(handler)

    (built, group), = handler.handlers

    assert group == 1
    assert built.exceptions == (ValueError,)
    assert built.filters is filters.text


def test_on_error_reads_the_keyword_form(handler: HandlerType) -> None:
    pyrogram.Client.on_error(exceptions=ValueError, filters=filters.text, group=1)(handler)

    (built, group), = handler.handlers

    assert group == 1
    assert built.exceptions == (ValueError,)
    assert built.filters is filters.text


def test_on_error_keeps_the_only_exception_it_was_given(handler: HandlerType) -> None:
    pyrogram.Client.on_error(ValueError)(handler)

    (built, group), = handler.handlers

    assert group == 0
    assert built.exceptions == (ValueError,)
    assert built.filters is None
