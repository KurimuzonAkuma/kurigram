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

"""Reading a dotted name against the package, shared by the docstring and annotation sweeps.

Both ask the same question of a different kind of text: does this name exist. Neither can
answer it statically, because the tree is one import cycle wide and half the names it
writes are only bound under `TYPE_CHECKING`, so both resolve against the imported package.
"""

import importlib
import pathlib
from typing import Any, Final, Iterator, Sequence

REPOSITORY_ROOT: Final[pathlib.Path] = pathlib.Path(__file__).resolve().parents[2]
PACKAGE_ROOT: Final[pathlib.Path] = REPOSITORY_ROOT / "pyrogram"

# The generated tree is rewritten wholesale by `make api` from the TL schema, so a repair
#  there lives until the next schema update and no longer.
GENERATED_TREE: Final[pathlib.Path] = PACKAGE_ROOT / "raw"


def hand_written_files() -> Iterator[pathlib.Path]:
    """Every module of the package a person wrote and a person can repair."""
    for path in sorted(PACKAGE_ROOT.rglob("*.py")):
        if GENERATED_TREE not in path.parents:
            yield path


def attribute_chain(root: Any, *, names: Sequence[str]) -> bool:
    """Walk `names` from `root` with `getattr`, answering whether every step exists."""
    resolved = root

    for name in names:
        if not hasattr(resolved, name):
            return False

        resolved = getattr(resolved, name)

    return True


def resolves(target: str) -> bool:
    """Import the longest prefix of `target`, then walk the rest of it with `getattr`."""
    parts = target.split(".")

    for cut in range(len(parts), 0, -1):
        try:
            resolved = importlib.import_module(".".join(parts[:cut]))
        except ImportError:
            continue

        return attribute_chain(resolved, names=parts[cut:])

    return False
