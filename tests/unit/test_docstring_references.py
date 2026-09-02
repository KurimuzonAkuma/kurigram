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

"""Every Sphinx cross-reference in a docstring points at something that exists.

Sphinx does not fail on a target it cannot resolve: it renders the text as a plain literal
and carries on, so a dead reference looks almost right and nothing reports it.
"""

import ast
import importlib
import pathlib
import re
from typing import Final, Iterator, List, NamedTuple, Pattern, Set, Tuple

_REPOSITORY_ROOT: Final[pathlib.Path] = pathlib.Path(__file__).resolve().parents[2]
_PACKAGE_ROOT: Final[pathlib.Path] = _REPOSITORY_ROOT / "pyrogram"

# The generated tree is rewritten wholesale by `make api` from the TL schema, so a repair
#  there lives until the next schema update and no longer.
_GENERATED_TREE: Final[pathlib.Path] = _PACKAGE_ROOT / "raw"

# `:obj:`Message`` and `:py:obj:`Message`` are the same role, the second one naming the
#  domain the first one inherits.
#  https://www.sphinx-doc.org/en/master/usage/domains/python.html#cross-referencing-python-objects
_CROSS_REFERENCE: Final[Pattern[str]] = re.compile(r":(?:py:)?(?:obj|class|meth|func|attr|data|mod|exc):`([^`]+)`")

_DOCUMENTED_NODES: Final[Tuple[type, ...]] = (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)


class Reference(NamedTuple):
    target: str
    path: pathlib.Path
    line: int

    def __str__(self) -> str:
        return "{}:{}: {}".format(self.path.relative_to(_REPOSITORY_ROOT), self.line, self.target)


def targets_in(text: str) -> Iterator[str]:
    """Take the target out of every cross-reference in `text`, both of its two forms."""
    for body in _CROSS_REFERENCE.findall(text):
        # A reference is either a target with the text to print in front of it, or a bare
        #  target that is both at once.
        target = body.rpartition("<")[2].rstrip(">") if "<" in body else body

        # A leading `~` prints the last component only and a leading `.` asks Sphinx to
        #  search; neither is part of the name. Trailing `()` marks a callable.
        yield target.strip().lstrip("~.").rstrip("()")


def docstrings_of(path: pathlib.Path) -> Iterator[Tuple[str, int]]:
    lines = path.read_text(encoding="utf-8").splitlines()

    for node in ast.walk(ast.parse("\n".join(lines))):
        if not isinstance(node, _DOCUMENTED_NODES) or not ast.get_docstring(node):
            continue

        literal = node.body[0].value
        yield "\n".join(lines[literal.lineno - 1 : literal.end_lineno]), literal.lineno


def hand_written_references() -> List[Reference]:
    references: List[Reference] = []

    for path in sorted(_PACKAGE_ROOT.rglob("*.py")):
        if _GENERATED_TREE in path.parents:
            continue

        for docstring, first_line in docstrings_of(path):
            for offset, line in enumerate(docstring.splitlines()):
                for target in targets_in(line):
                    references.append(Reference(target, path, first_line + offset))

    return references


def resolves(target: str) -> bool:
    """Import the longest prefix of `target`, then walk the rest of it with `getattr`."""
    parts = target.split(".")

    for cut in range(len(parts), 0, -1):
        try:
            resolved = importlib.import_module(".".join(parts[:cut]))
        except ImportError:
            continue

        for name in parts[cut:]:
            if not hasattr(resolved, name):
                return False

            resolved = getattr(resolved, name)

        return True

    return False


def test_every_cross_reference_in_a_docstring_resolves() -> None:
    """A docstring is rendered on whichever page includes it, so its targets are absolute.

    An unqualified target is resolved against the `currentmodule` of that page, which the
    docstring cannot see: `Client.forward_messages` links on a method page and dies on a
    type page.
    """
    dead = sorted({str(one) for one in hand_written_references() if not resolves(one.target)})

    assert not dead, "{} cross-references point at nothing:\n{}".format(len(dead), "\n".join(dead))


def test_the_sweep_reads_the_docstrings_it_claims_to() -> None:
    """A regex that stopped matching would leave the test above passing over nothing."""
    references = hand_written_references()
    targets: Set[str] = {one.target for one in references}

    assert len(targets) > 500
    assert "pyrogram.types.Message" in targets
    assert any(one.path.name == "get_chat_history.py" for one in references)


def test_a_target_that_does_not_exist_does_not_resolve() -> None:
    assert resolves("pyrogram.types.Message")
    assert resolves("pyrogram.Client.forward_messages")
    assert resolves("datetime.datetime")

    assert not resolves("pyrogram.types.Message.no_such_method")
    assert not resolves("pyrogram.types.NoSuchType")
    assert not resolves("Message.reply")
