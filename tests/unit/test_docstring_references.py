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
from typing import Final, Iterator, List, NamedTuple, Optional, Pattern, Set, Tuple

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

# A label is free text as often as it is a name, and prose is a suffix of nothing: a label
#  reading "send a message" over `pyrogram.Client.send_message` is correct Sphinx.
_LABEL_THAT_IS_A_PATH: Final[Pattern[str]] = re.compile(r"^[\w.]+(?:\(\))?$")


class Reference(NamedTuple):
    target: str
    path: pathlib.Path
    line: int
    label: Optional[str] = None

    def __str__(self) -> str:
        body = self.target if self.label is None else "{} <{}>".format(self.label, self.target)

        return "{}:{}: {}".format(self.path.relative_to(_REPOSITORY_ROOT), self.line, body)


def components(dotted: str) -> List[str]:
    """Split a dotted name the way Sphinx reads one, with the decoration taken off.

    A leading `~` prints the last component only and a leading `.` asks Sphinx to search;
    neither is part of the name. Trailing `()` marks a callable.
    """
    return dotted.strip().lstrip("~.").rstrip("()").split(".")


def references_in(text: str) -> Iterator[Tuple[Optional[str], str]]:
    """Take the label and the target out of every cross-reference in `text`."""
    for body in _CROSS_REFERENCE.findall(text):
        # A reference is either a target with the text to print in front of it, or a bare
        #  target that is both at once. Sphinx tells them apart with `^(.+?)\s*(?<!\x00)<([^<]*?)>$`,
        #  so the split is at the last `<` and only when the body ends in `>`.
        #  https://github.com/sphinx-doc/sphinx/blob/cc7c6f435ad37bb12264f8118c8461b230e6830c/sphinx/util/nodes.py#L35
        if not body.endswith(">"):
            yield None, ".".join(components(body))
            continue

        label, _, target = body[:-1].rpartition("<")

        yield label.strip(), ".".join(components(target))


def label_agrees_with_target(label: str, *, target: str) -> bool:
    """A label written as a path names the tail of the target, or it names something else.

    Only the label decides whether this applies: prose is exempt, because a sentence is
    not a shortened name and cannot be a suffix of one.
    """
    if not _LABEL_THAT_IS_A_PATH.match(label):
        return True

    label_parts = components(label)

    return label_parts == components(target)[-len(label_parts):]


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
                for label, target in references_in(line):
                    references.append(Reference(target, path, first_line + offset, label))

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


def test_every_label_that_looks_like_a_path_names_the_target_it_points_at() -> None:
    """`:obj:`Filters.regex <pyrogram.filters.regex>`` prints a name the link does not lead to.

    Sphinx prints the label and links the target without comparing them, so a label left
    behind by a rename reads as a working reference to a name that moved.
    """
    disagreeing = sorted(
        {
            str(one)
            for one in hand_written_references()
            if one.label is not None and not label_agrees_with_target(one.label, target=one.target)
        }
    )

    assert not disagreeing, "{} labels name something other than their target:\n{}".format(
        len(disagreeing),
        "\n".join(disagreeing),
    )


def test_a_label_is_checked_only_when_it_is_written_as_a_path() -> None:
    assert label_agrees_with_target("filters.regex", target="pyrogram.filters.regex")
    assert label_agrees_with_target("create()", target="pyrogram.filters.create")
    assert label_agrees_with_target("pyrogram.filters.regex", target="pyrogram.filters.regex")

    assert not label_agrees_with_target("Filters.regex", target="pyrogram.filters.regex")
    assert not label_agrees_with_target("types.Folder", target="pyrogram.types.Chat")
    assert not label_agrees_with_target("regex.filters", target="pyrogram.filters.regex")

    # Prose is exempt, whatever it says.
    assert label_agrees_with_target("send a message", target="pyrogram.Client.send_message")
    assert label_agrees_with_target("the chat itself", target="pyrogram.types.Chat")


def test_a_reference_carries_the_label_it_was_written_with() -> None:
    """The rule above passes over everything if the label stops being read."""
    assert list(references_in(":obj:`~pyrogram.types.Message`")) == [(None, "pyrogram.types.Message")]
    assert list(references_in(":meth:`filters.create() <pyrogram.filters.create>`")) == [
        ("filters.create()", "pyrogram.filters.create")
    ]

    labelled = [one for one in hand_written_references() if one.label is not None]

    assert labelled, "the explicit-title form is gone from the tree, and this rule with it"
