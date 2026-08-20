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

import csv
import re
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Final, List, Optional, Set, Tuple

# Resolved from this file rather than from the working directory, which is the repository root
# under `hatch_build.py` and `compiler/errors` under `make errors`.
_HOME: Final[Path] = Path(__file__).resolve().parent
_DEST: Final[Path] = _HOME.parents[1] / "pyrogram" / "errors" / "exceptions"
_NOTICE: Final[Path] = _HOME.parents[1] / "NOTICE"

# The name an error carries its value under when its own message names none. `value` is the
# attribute `RPCError` assigns, so a property of that name would shadow it and none is written.
_PLAIN_VALUE_NAME: Final[str] = "value"

# `pyrogram/errors/__init__.py` imports the hand-written errors after the generated ones, so a
# generated class of either name never reaches the caller: a 400 `UNKNOWN_ERROR` used to arrive as
# the hand-written `UnknownError`, which reports code 520 and is no `BadRequest`.
_RESERVED_CLASS_NAMES: Final[Tuple[str, ...]] = ("RPCError", "UnknownError")

# A class name may not start with a digit. `2FA_CONFIRM_WAIT_X` is the only id that does, and any
# other would need a word of its own here rather than a module Python cannot import.
_LEADING_DIGIT_WORDS: Final[Dict[str, str]] = {"2": "Two"}


@dataclass(frozen=True)
class _Table:
    """A source table, and the module it compiles to."""
    path: Path
    code: int
    module_name: str
    super_class: str
    title: str


@dataclass(frozen=True)
class _Row:
    """A line of a source table."""
    table: _Table
    error_id: str
    message: str
    value_name: str
    base_name: str


@dataclass(frozen=True)
class _Error:
    """A row, once every claimant of the name it asks for is known and it has one of its own."""
    row: _Row
    class_name: str
    bases: List[str]
    primary: Optional["_Error"]

    @property
    def table(self) -> _Table:
        return self.row.table


@dataclass(frozen=True)
class _Templates:
    """
    The files under `template/`. `class.txt` is a whole module: a category and the errors under it,
    each of them written from `sub_class.txt`, and each of the three blocks below written into the
    body of a sub class that asks for it.

    The newlines that join a block to that body are spelled out where the block is written, rather
    than left to whichever ones a template file happens to begin and end with.
    """
    module: str
    sub_class: str
    code_and_name: str
    value_property: str
    value_name_reset: str


def _to_snake_case(name: str) -> str:
    # https://stackoverflow.com/questions/1175208/elegant-python-function-to-convert-camelcase-to-snake-case
    name = re.sub(r"(.)([A-Z][a-z]+)", r"\1_\2", name)
    return re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", name).lower()


def _to_pascal_case(name: str) -> str:
    return "".join([word.title() for word in _to_snake_case(name).split("_")])


def _read_notice() -> str:
    lines = _NOTICE.read_text(encoding="utf-8").splitlines()

    return "\n".join(["# {}".format(line).strip() for line in lines])


def _read_templates() -> _Templates:
    return _Templates(
        module=_read_template("class"),
        sub_class=_read_template("sub_class"),
        code_and_name=_read_template("code_and_name"),
        value_property=_read_template("value_property"),
        value_name_reset=_read_template("value_name_reset")
    )


def _read_template(template_name: str) -> str:
    return (_HOME / "template" / "{}.txt".format(template_name)).read_text(encoding="utf-8")


def _read_table(path: Path) -> _Table:
    code, name = re.search(r"(\d+)_([A-Z_]+)", path.name).groups()
    words = re.sub(r"_", " ", name).lower().split(" ")

    return _Table(
        path=path,
        code=int(code),
        module_name="{}_{}".format(name.lower(), code),
        super_class=_to_pascal_case(name),
        title=" ".join([word.capitalize() for word in words])
    )


def _read_rows(table: _Table) -> List[_Row]:
    with table.path.open(encoding="utf-8", newline="") as table_file:
        reader = csv.reader(table_file, delimiter="\t")
        next(reader)  # The header.

        # A blank line is no error of the table.
        return [_read_row(table, line=line) for line in reader if line]


def _read_row(table: _Table, *, line: List[str]) -> _Row:
    error_id, message = line

    return _Row(
        table=table,
        error_id=error_id,
        message=message,
        value_name=_value_name_of(error_id=error_id, message=message),
        base_name=_base_name_of(error_id)
    )


def _base_name_of(error_id: str) -> str:
    # The `_X` suffix marks the ids whose message carries a value. It is not part of the name: an
    # id spelled both ways is one error, and the two are told apart by a suffix further down.
    name = _to_pascal_case(re.sub(r"_X", "_", error_id))

    # `No workers running`, at 500, is a sentence rather than an id.
    return _spell_out_leading_digit(name.replace(" ", ""), error_id=error_id)


def _spell_out_leading_digit(name: str, *, error_id: str) -> str:
    if not name[:1].isdigit():
        return name

    word = _LEADING_DIGIT_WORDS.get(name[0])

    if word is None:
        msg = "{} starts with a digit that no word is spelled out for: {}".format(error_id, name[0])
        raise ValueError(msg)

    return word + name[1:]


def _value_name_of(*, error_id: str, message: str) -> str:
    # The placeholder in a message is Telegram's own word for what the error carries, taken from
    # the descriptions in the error list Telegram publishes, https://core.telegram.org/api/errors,
    # in machine-readable form at https://core.telegram.org/api/errors.json, or from the schema's
    # word for the same thing (`dc_id` is `auth.exportAuthorization.dc_id`), or from Telethon,
    # which named a number of them first:
    # https://github.com/LonamiWebs/Telethon/blob/v1.36.0/telethon_generator/data/errors.csv
    #
    # One placeholder per message, at most. `RPCError.raise_it()` reads a single number out of an
    # error message and renders the message with it, so a second placeholder could never be filled
    # in - `str.format()` would raise `KeyError` on the error nobody can catch.
    placeholders = re.findall(r"\{(\w*)\}", message)

    if len(placeholders) > 1:
        msg = "{} carries more than one placeholder: {}".format(error_id, message)
        raise ValueError(msg)

    if not placeholders:
        return _PLAIN_VALUE_NAME

    return placeholders[0]


def _name_errors(rows: List[_Row]) -> List[_Error]:
    claimants: Dict[str, List[_Row]] = {}

    for row in rows:
        claimants.setdefault(row.base_name, []).append(row)

    for reserved_name in _RESERVED_CLASS_NAMES:
        for row in claimants.pop(reserved_name, []):
            claimants.setdefault("{}{}".format(reserved_name, row.table.code), []).append(row)

    named: Dict[_Row, _Error] = {}

    for base_name, group in claimants.items():
        group.sort(key=lambda claimant: (claimant.table.code, claimant.error_id))

        primary = _Error(
            row=group[0],
            class_name=base_name,
            bases=[group[0].table.super_class],
            primary=None
        )

        named[primary.row] = primary

        for row in group[1:]:
            named[row] = _subclass_of(primary, row=row)

    class_names = [error.class_name for error in named.values()]

    if len(class_names) != len(set(class_names)):
        msg = "two errors compile to the same class name"
        raise RuntimeError(msg)

    return [named[row] for row in rows]


def _subclass_of(primary: _Error, *, row: _Row) -> _Error:
    if row.table.code != primary.table.code:
        # The very same error under a second code. It keeps the name it shares, so that
        # `except PeerIdInvalid` still catches every one of them, and takes the category of its own
        # code as a second base, so that `except Forbidden` catches the 403 too.
        return _Error(
            row=row,
            class_name="{}{}".format(primary.class_name, row.table.code),
            bases=[primary.class_name, row.table.super_class],
            primary=primary
        )

    # Two ids under one code that only differ by the value they carry, such as `EMAIL_UNCONFIRMED`
    # and `EMAIL_UNCONFIRMED_X`. The parameterised one is the one that gets marked, and subclasses
    # the other so both are caught by the plain name.
    return _Error(
        row=row,
        class_name="{}X".format(primary.class_name),
        bases=[primary.class_name],
        primary=primary
    )


def _by_table(errors: List[_Error]) -> Dict[_Table, List[_Error]]:
    grouped: Dict[_Table, List[_Error]] = {}

    for error in errors:
        grouped.setdefault(error.table, []).append(error)

    return grouped


def _code_and_name_block(templates: _Templates, *, error: _Error) -> str:
    # A sub class answers with the code and the category of the class it subclasses, and an error
    # that arrived under a code of its own has to say so, or `except Forbidden` would miss the 403
    # that shares its name with a 400.
    if error.primary is None or error.primary.table.code == error.table.code:
        return ""

    return "\n" + templates.code_and_name.format(
        code=error.table.code,
        name=error.table.title
    ).rstrip("\n")


def _value_block(templates: _Templates, *, error: _Error) -> str:
    if error.row.value_name != _PLAIN_VALUE_NAME:
        return "\n\n" + templates.value_property.format(value_name=error.row.value_name).rstrip("\n")

    # An error that carries nothing inherits the name of a value it never has when the error it
    # subclasses names one. `ALLOW_PAYMENT_REQUIRED` at 406 is the only one: the 403 it shares a
    # name with is the parameterised `ALLOW_PAYMENT_REQUIRED_X`, which carries `{star_count}`.
    if error.primary is not None and error.primary.row.value_name != _PLAIN_VALUE_NAME:
        return "\n\n" + templates.value_name_reset.format(primary=error.primary.class_name).rstrip("\n")

    return ""


def _typing_import(errors: List[_Error]) -> str:
    if all(error.row.value_name == _PLAIN_VALUE_NAME for error in errors):
        return ""

    return "from typing import Optional\n\n"


def _import_block(table: _Table, *, errors: List[_Error]) -> str:
    imports: Dict[str, Set[str]] = {}

    for error in errors:
        if error.primary is not None and error.primary.table != table:
            imports.setdefault(error.primary.table.module_name, set()).add(error.primary.class_name)

    # An error only ever subclasses one of a lower code, and the modules are written in that order,
    # so these imports run downwards and can never form a cycle.
    return "".join([
        "\nfrom .{} import (\n{}\n)".format(
            module_name,
            "".join(["    {},\n".format(class_name) for class_name in sorted(class_names)]).rstrip("\n")
        )
        for module_name, class_names in sorted(imports.items())
    ])


def _write_init(tables: List[_Table], *, notice: str) -> None:
    imports = ["from .{} import *".format(table.module_name) for table in tables]

    _write(_DEST / "__init__.py", lines=[notice, ""] + imports)


def _write_all(tables: Dict[_Table, List[_Error]], *, notice: str, count: int) -> None:
    lines: List[str] = [notice, "", "count = {}".format(count), "", "exceptions = {"]

    for table, errors in tables.items():
        lines.append("    {}: {{".format(table.code))
        lines.append("        \"_\": \"{}\",".format(table.super_class))
        lines.extend([
            "        \"{}\": \"{}\",".format(error.row.error_id, error.class_name)
            for error in errors
        ])
        lines.append("    },")

    lines.append("}")

    _write(_DEST / "all.py", lines=lines)


def _write(path: Path, *, lines: List[str]) -> None:
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_module(table: _Table, *, errors: List[_Error], notice: str, templates: _Templates) -> None:
    sub_classes: List[str] = []
    written: Set[str] = set()

    for error in errors:
        primary = error.primary

        if primary is not None and primary.table == table and primary.class_name not in written:
            msg = "{} is written before the {} it subclasses".format(error.class_name, primary.class_name)
            raise RuntimeError(msg)

        sub_class = templates.sub_class.format(
            sub_class=error.class_name,
            bases=", ".join(error.bases),
            id="\"{}\"".format(error.row.error_id),
            docstring='"""{}"""'.format(error.row.message),
            code_and_name=_code_and_name_block(templates, error=error),
            value_property=_value_block(templates, error=error)
        )

        sub_classes.append(sub_class)
        written.add(error.class_name)

    module = templates.module.format(
        notice=notice,
        typing_import=_typing_import(errors),
        imports=_import_block(table, errors=errors),
        super_class=table.super_class,
        code=table.code,
        docstring='"""{}"""'.format(table.title),
        sub_classes="".join(sub_classes)
    )

    (_DEST / "{}.py".format(table.module_name)).write_text(module, encoding="utf-8")


def start() -> None:
    shutil.rmtree(_DEST, ignore_errors=True)
    _DEST.mkdir(parents=True)

    notice = _read_notice()
    templates = _read_templates()

    # Every table is read before a single class is written. The name an error compiles to is not
    # its own to take - 52 of them are claimed by more than one error - and which claimant keeps
    # the plain name is only known once they all are.
    rows: List[_Row] = []

    for path in sorted((_HOME / "source").iterdir()):
        rows.extend(_read_rows(_read_table(path)))

    tables = _by_table(_name_errors(rows))

    _write_init(list(tables), notice=notice)
    _write_all(tables, notice=notice, count=len(rows))

    for table, errors in tables.items():
        _write_module(table, errors=errors, notice=notice, templates=templates)


if "__main__" == __name__:
    start()
