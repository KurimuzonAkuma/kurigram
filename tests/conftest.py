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

from pathlib import Path
from typing import Dict, Final, List

import pytest

_TESTS_DIR: Final[Path] = Path(__file__).parent

# The marker comes from the directory a test file lives in, not from a decorator
#  on each test - a path cannot be forgotten the way a decorator can. The
#  environment `.env.test` carries is loaded by the runner (see `Makefile`), not
#  from here: a test process that reads files of its own has two config sources.
_LAYER_MARKERS: Final[Dict[str, str]] = {
    "unit": "unit",
    "integrations": "integration",
}


def pytest_collection_modifyitems(items: List[pytest.Item]) -> None:
    for item in items:
        relative = Path(item.fspath).relative_to(_TESTS_DIR)
        top_directory = relative.parts[0] if len(relative.parts) > 1 else None

        if top_directory in _LAYER_MARKERS:
            item.add_marker(getattr(pytest.mark, _LAYER_MARKERS[top_directory]))
