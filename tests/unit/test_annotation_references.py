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

"""Every name an annotation writes exists where the annotation is written.

Almost every annotation in this tree is a string, so nothing evaluates it: a name that does
not exist reaches an IDE and a type checker as though it did, and no part of the build says
otherwise.
"""

import ast
import builtins
import importlib
import pathlib
from dataclasses import dataclass
from types import ModuleType
from typing import Any, Dict, Iterator, List, Optional, Sequence, Set, Tuple

import pyrogram
from tests.unit.name_resolution import REPOSITORY_ROOT, attribute_chain, hand_written_files


@dataclass(frozen=True)
class Annotation:
    name: Tuple[str, ...]
    path: pathlib.Path
    line: int

    def __str__(self) -> str:
        return "{}:{}: {}".format(self.path.relative_to(REPOSITORY_ROOT), self.line, ".".join(self.name))


def module_name_of(path: pathlib.Path) -> str:
    parts = list(path.relative_to(REPOSITORY_ROOT).with_suffix("").parts)

    if parts[-1] == "__init__":
        parts.pop()

    return ".".join(parts)


def annotations_of(tree: ast.Module) -> Iterator[ast.expr]:
    """Every annotation a module writes: on a parameter, on a return, on an assignment."""
    for node in ast.walk(tree):
        if isinstance(node, ast.AnnAssign):
            yield node.annotation
            continue

        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue

        arguments = node.args
        every: List[Optional[ast.arg]] = [
            *arguments.posonlyargs,
            *arguments.args,
            *arguments.kwonlyargs,
            arguments.vararg,
            arguments.kwarg,
        ]

        for argument in every:
            if argument is not None and argument.annotation is not None:
                yield argument.annotation

        if node.returns is not None:
            yield node.returns


def dotted_name(node: ast.expr) -> Optional[Tuple[str, ...]]:
    """The components of `a.b.c`, or `None` for anything that is not a plain dotted name."""
    parts: List[str] = []

    while isinstance(node, ast.Attribute):
        parts.append(node.attr)
        node = node.value

    if not isinstance(node, ast.Name):
        return None

    parts.append(node.id)

    return tuple(reversed(parts))


def subscript_of(node: ast.Subscript) -> ast.expr:
    """What sits inside `X[...]`, whichever way this Python spells it.

    Python 3.9 stopped wrapping a subscript in `ast.Index`, and 3.8 is still supported.
    The wrapper is read by name rather than by `isinstance`, because `ast.Index` has been
    deprecated since 3.9 and touching it raises a `DeprecationWarning`.
    https://docs.python.org/3/whatsnew/3.9.html#deprecated
    """
    inner = node.slice

    return getattr(inner, "value", inner) if inner.__class__.__name__ == "Index" else inner


def names_in(node: ast.expr, *, line: int) -> Iterator[Tuple[Tuple[str, ...], int]]:
    """Every name an annotation mentions, with the line it was written on.

    A string annotation holds a whole type expression rather than a bare name, so it is
    parsed and walked like any other: `Optional[List["types.Chat"]]` names `types.Chat`.
    """
    if isinstance(node, ast.Subscript):
        head = dotted_name(node.value)

        yield from names_in(node.value, line=line)

        # `Literal["png", "jpg"]` holds values, and a value is not a name.
        #  https://docs.python.org/3/library/typing.html#typing.Literal
        if head is not None and head[-1] == "Literal":
            return

        yield from names_in(subscript_of(node), line=line)
        return

    if isinstance(node, (ast.Tuple, ast.List)):
        for element in node.elts:
            yield from names_in(element, line=line)

        return

    if isinstance(node, ast.BinOp):
        yield from names_in(node.left, line=line)
        yield from names_in(node.right, line=line)
        return

    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        try:
            inner = ast.parse(node.value.strip(), mode="eval").body

        # A string annotation is not required to be an expression, and one that is not is
        #  a defect of its own rather than a dead name.
        except SyntaxError:
            return

        yield from names_in(inner, line=node.lineno)
        return

    parts = dotted_name(node)

    if parts is not None:
        yield parts, line


def type_checking_imports(tree: ast.Module, *, package: str) -> Dict[str, Any]:
    """The names a module binds under `if TYPE_CHECKING:`, imported for real.

    Most of this package imports `pyrogram`, `types`, `raw` and `enums` only there, to break
    the import cycle they would otherwise close. Those names are absent from the imported
    module at runtime, so a namespace built from it alone reports every annotation that uses
    one as dead.
    """
    bindings: Dict[str, Any] = {}

    for node in ast.walk(tree):
        if not isinstance(node, ast.If) or (dotted_name(node.test) or ("",))[-1] != "TYPE_CHECKING":
            continue

        for statement in ast.walk(node):
            if isinstance(statement, ast.Import):
                for alias in statement.names:
                    root = alias.name.split(".")[0]
                    bindings[alias.asname or root] = importlib.import_module(root)

            elif isinstance(statement, ast.ImportFrom):
                source = importlib.import_module("." * statement.level + (statement.module or ""), package)

                for alias in statement.names:
                    bindings[alias.asname or alias.name] = getattr(source, alias.name)

    return bindings


def namespace_of(module: ModuleType, *, tree: ast.Module) -> Dict[str, Any]:
    namespace = dict(vars(module))
    namespace.update(type_checking_imports(tree, package=module.__name__.rpartition(".")[0]))

    return namespace


def annotations_in(path: pathlib.Path) -> Iterator[Tuple[Annotation, Dict[str, Any]]]:
    module = importlib.import_module(module_name_of(path))
    tree = ast.parse(path.read_text(encoding="utf-8"))
    namespace = namespace_of(module, tree=tree)

    for annotation in annotations_of(tree):
        for name, line in names_in(annotation, line=annotation.lineno):
            yield Annotation(name, path, line), namespace


def resolves_where_written(name: Sequence[str], *, namespace: Dict[str, Any]) -> bool:
    # A builtin is in scope everywhere and in no module's namespace, so `int` and `str` would
    #  otherwise read as dead names.
    root = namespace.get(name[0], getattr(builtins, name[0], None))

    return root is not None and attribute_chain(root, names=name[1:])


def dead_annotations() -> List[Annotation]:
    return [
        annotation
        for path in hand_written_files()
        for annotation, namespace in annotations_in(path)
        if not resolves_where_written(annotation.name, namespace=namespace)
    ]


def test_every_name_in_an_annotation_resolves_where_it_is_written() -> None:
    """A dead name in an annotation is what an IDE offers the caller as the type to pass."""
    dead = sorted(str(one) for one in dead_annotations())

    assert not dead, "{} annotations name something that does not exist:\n{}".format(len(dead), "\n".join(dead))


def test_the_sweep_reads_the_annotations_it_claims_to() -> None:
    """A walk that stopped descending would leave the test above passing over nothing."""
    read: List[Annotation] = [annotation for path in hand_written_files() for annotation, _ in annotations_in(path)]
    names: Set[Tuple[str, ...]] = {one.name for one in read}

    assert len(read) > 5000
    assert ("types", "Message") in names
    assert ("raw", "base", "InputPeer") in names
    assert any(one.path.name == "shipping_query.py" for one in read)


def test_a_string_annotation_is_read_as_the_expression_it_holds() -> None:
    def names(source: str) -> List[Tuple[str, ...]]:
        return [name for name, _ in names_in(ast.parse(source, mode="eval").body, line=1)]

    assert names('"types.Chat"') == [("types", "Chat")]
    assert names('Optional[List["types.Chat"]]') == [("Optional",), ("List",), ("types", "Chat")]
    assert names('Union["types.Chat", int]') == [("Union",), ("types", "Chat"), ("int",)]
    assert names('"Optional[types.Chat]"') == [("Optional",), ("types", "Chat")]


def test_a_subscript_is_read_through_the_wrapper_python_38_puts_around_it() -> None:
    """The suite runs on 3.8, whose parser wraps `X[Y]` in a node 3.9 stopped emitting.

    The wrapper cannot be produced by parsing here, so the node is built the way the 3.8
    parser builds it. Without the unwrapping, every name inside a subscript is invisible
    on 3.8 alone and the sweep passes there over nothing.
    """
    inner = ast.parse('"types.Chat"', mode="eval").body

    # TODO: Delete this test and the unwrapping in `subscript_of()` when the floor moves
    #       off 3.8. Nothing else reads `ast.Index`, and 3.9 stopped emitting it.
    index = ast.Index(value=inner)  # ty: ignore[deprecated] - the 3.8 node is what this test is for
    wrapped = ast.Subscript(value=ast.Name(id="Optional", ctx=ast.Load()), slice=index, ctx=ast.Load())
    ast.fix_missing_locations(wrapped)

    assert subscript_of(wrapped) is inner
    assert [name for name, _ in names_in(wrapped, line=1)] == [("Optional",), ("types", "Chat")]


def test_a_literal_holds_values_rather_than_names() -> None:
    """Without this, every string a `Literal` lists would be read as a type that is missing."""
    def names(source: str) -> List[Tuple[str, ...]]:
        return [name for name, _ in names_in(ast.parse(source, mode="eval").body, line=1)]

    assert names('Literal["socks4", "socks5"]') == [("Literal",)]
    assert names('typing.Literal["a", "A"]') == [("typing", "Literal")]
    assert names('Optional[Literal["a"]]') == [("Optional",), ("Literal",)]


def test_a_name_resolves_against_the_namespace_it_was_written_in() -> None:
    namespace: Dict[str, Any] = {"types": pyrogram.types}

    assert resolves_where_written(("types", "Chat"), namespace=namespace)
    assert resolves_where_written(("int",), namespace=namespace)

    assert not resolves_where_written(("types", "NoSuchType"), namespace=namespace)
    assert not resolves_where_written(("enums", "ParseMode"), namespace=namespace)
