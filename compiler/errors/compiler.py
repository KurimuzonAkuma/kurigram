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
import os
import re
import shutil
from dataclasses import dataclass
from typing import Dict, Final, List, Optional, Set, Tuple

HOME = "compiler/errors"
DEST = "pyrogram/errors/exceptions"
NOTICE_PATH = "NOTICE"

# The name an error carries its value under when its own message names none. `value` is the
# attribute `RPCError` assigns, so a property of that name would shadow it and none is written.
_PLAIN_VALUE_NAME: Final[str] = "value"

# `pyrogram/errors/__init__.py` imports the hand-written errors after the generated ones, so a
# generated class of either name never reaches the caller: a 400 `UNKNOWN_ERROR` used to arrive as
# the hand-written `UnknownError`, which reports code 520 and is no `BadRequest`.
_RESERVED_CLASS_NAMES: Final[Tuple[str, ...]] = ("RPCError", "UnknownError")

# Two blocks that a class body carries only under a condition, spelled out here rather than in
# `template/`: a file there stands for a whole module or a whole class, while each of these is the
# handful of lines that one kind of error gets and the rest do not.

# A sub class answers with the code and the category of the class it subclasses, and an error that
# arrived under a code of its own has to say so, or `except Forbidden` would miss the 403 that
# shares its name with a 400.
_CODE_AND_NAME: Final[str] = '''
    CODE = {code}
    """``int``: RPC Error Code"""
    NAME = "{name}"
    """``str``: RPC Error Name"""'''

# An error that carries nothing inherits the name of a value it never has when the error it
# subclasses names one. `ALLOW_PAYMENT_REQUIRED` at 406 is the only one: the 403 it shares a name
# with is the parameterised `ALLOW_PAYMENT_REQUIRED_X`, whose message carries `{star_count}`.
_INHERITED_VALUE_NAME_RESET: Final[str] = '''

    # Unlike the `{primary}` it subclasses, this error carries nothing.
    VALUE_NAME = RPCError.VALUE_NAME'''


@dataclass(frozen=True)
class Table:
    """A source table, and the module it compiles to."""
    file_name: str
    code: int
    module_name: str
    super_class: str
    title: str


@dataclass(frozen=True)
class Row:
    """A line of a source table."""
    table: Table
    error_id: str
    message: str
    value_name: str
    base_name: str


@dataclass(frozen=True)
class Error:
    """A row, once every claimant of the name it asks for is known and it has one of its own."""
    row: Row
    class_name: str
    bases: List[str]
    primary: Optional["Error"]

    @property
    def table(self) -> Table:
        return self.row.table


@dataclass(frozen=True)
class Templates:
    """The three files in `template/`. `class.txt` is the whole module: a category and its errors."""
    module: str
    sub_class: str
    value_property: str


def snek(name: str) -> str:
    # https://stackoverflow.com/questions/1175208/elegant-python-function-to-convert-camelcase-to-snake-case
    name = re.sub(r"(.)([A-Z][a-z]+)", r"\1_\2", name)
    return re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", name).lower()


def caml(name: str) -> str:
    return "".join([word.title() for word in snek(name).split("_")])


def read_notice() -> str:
    with open(NOTICE_PATH, encoding="utf-8") as notice_file:
        return "\n".join(["# {}".format(line).strip() for line in notice_file.readlines()])


def read_templates() -> Templates:
    return Templates(
        module=read_template("class"),
        sub_class=read_template("sub_class"),
        value_property=read_template("value_property")
    )


def read_template(template_name: str) -> str:
    with open("{}/template/{}.txt".format(HOME, template_name), encoding="utf-8") as template_file:
        return template_file.read()


def read_table(file_name: str) -> Table:
    code, name = re.search(r"(\d+)_([A-Z_]+)", file_name).groups()
    words = re.sub(r"_", " ", name).lower().split(" ")

    return Table(
        file_name=file_name,
        code=int(code),
        module_name="{}_{}".format(name.lower(), code),
        super_class=caml(name),
        title=" ".join([word.capitalize() for word in words])
    )


def read_rows(table: Table) -> List[Row]:
    rows = []

    with open("{}/source/{}".format(HOME, table.file_name), encoding="utf-8") as table_file:
        reader = csv.reader(table_file, delimiter="\t")
        next(reader)  # The header.

        for row in reader:
            if not row:  # A blank line.
                continue

            error_id, message = row

            rows.append(Row(
                table=table,
                error_id=error_id,
                message=message,
                value_name=value_name_of(error_id=error_id, message=message),
                base_name=base_name_of(error_id)
            ))

    return rows


def base_name_of(error_id: str) -> str:
    # The `_X` suffix marks the ids whose message carries a value. It is not part of the name: an
    # id spelled both ways is one error, and the two are told apart by a suffix further down.
    name = caml(re.sub(r"_X", "_", error_id))

    # `2FA_CONFIRM_WAIT_X` is the one id that starts with a digit, which a class name may not.
    name = re.sub(r"^2", "Two", name)

    # `No workers running`, at 500, is a sentence rather than an id.
    return name.replace(" ", "")


def value_name_of(*, error_id: str, message: str) -> str:
    # The placeholder in a message is Telegram's own word for what the error carries: from the
    # descriptions in https://corefork.telegram.org/api/errors.json, from the schema's word for the
    # same thing (`dc_id` is `auth.exportAuthorization.dc_id`), or from Telethon, which named a
    # number of them first:
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


def name_errors(rows: List[Row]) -> List[Error]:
    claimants: Dict[str, List[Row]] = {}

    for row in rows:
        claimants.setdefault(row.base_name, []).append(row)

    for reserved_name in _RESERVED_CLASS_NAMES:
        for row in claimants.pop(reserved_name, []):
            claimants.setdefault("{}{}".format(reserved_name, row.table.code), []).append(row)

    named: Dict[Row, Error] = {}

    for base_name, group in claimants.items():
        group.sort(key=lambda claimant: (claimant.table.code, claimant.error_id))

        primary = Error(
            row=group[0],
            class_name=base_name,
            bases=[group[0].table.super_class],
            primary=None
        )

        named[primary.row] = primary

        for row in group[1:]:
            named[row] = subclass_of(primary, row=row)

    class_names = [error.class_name for error in named.values()]

    if len(class_names) != len(set(class_names)):
        raise AssertionError("two errors compile to the same class name")

    return [named[row] for row in rows]


def subclass_of(primary: Error, *, row: Row) -> Error:
    if row.table.code != primary.table.code:
        # The very same error under a second code. It keeps the name it shares, so that
        # `except PeerIdInvalid` still catches every one of them, and takes the category of its own
        # code as a second base, so that `except Forbidden` catches the 403 too.
        return Error(
            row=row,
            class_name="{}{}".format(primary.class_name, row.table.code),
            bases=[primary.class_name, row.table.super_class],
            primary=primary
        )

    # Two ids under one code that only differ by the value they carry, such as `EMAIL_UNCONFIRMED`
    # and `EMAIL_UNCONFIRMED_X`. The parameterised one is the one that gets marked, and subclasses
    # the other so both are caught by the plain name.
    return Error(
        row=row,
        class_name="{}X".format(primary.class_name),
        bases=[primary.class_name],
        primary=primary
    )


def by_table(errors: List[Error]) -> Dict[Table, List[Error]]:
    grouped: Dict[Table, List[Error]] = {}

    for error in errors:
        grouped.setdefault(error.table, []).append(error)

    return grouped


def code_and_name_block(error: Error) -> str:
    if error.primary is None or error.primary.table.code == error.table.code:
        return ""

    return _CODE_AND_NAME.format(code=error.table.code, name=error.table.title)


def value_block(templates: Templates, *, error: Error) -> str:
    if error.row.value_name != _PLAIN_VALUE_NAME:
        # A blank line, then the block, appended to the `MESSAGE = __doc__` line the sub class
        # template ends its body with. Spelled out here rather than left to whichever newlines the
        # template file happens to begin and end with.
        return "\n\n" + templates.value_property.format(value_name=error.row.value_name).rstrip("\n")

    if error.primary is not None and error.primary.row.value_name != _PLAIN_VALUE_NAME:
        return _INHERITED_VALUE_NAME_RESET.format(primary=error.primary.class_name)

    return ""


def typing_import(errors: List[Error]) -> str:
    if all(error.row.value_name == _PLAIN_VALUE_NAME for error in errors):
        return ""

    return "from typing import Optional\n\n"


def import_block(table: Table, *, errors: List[Error]) -> str:
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


def write_init(tables: List[Table], *, notice: str) -> None:
    with open("{}/__init__.py".format(DEST), "w", encoding="utf-8") as init_module:
        init_module.write(notice + "\n\n")

        for table in tables:
            init_module.write("from .{} import *\n".format(table.module_name))


def write_all(tables: Dict[Table, List[Error]], *, notice: str, count: int) -> None:
    with open("{}/all.py".format(DEST), "w", encoding="utf-8") as all_module:
        all_module.write(notice + "\n\n")
        all_module.write("count = {}\n\n".format(count))
        all_module.write("exceptions = {\n")

        for table, errors in tables.items():
            all_module.write("    {}: {{\n".format(table.code))
            all_module.write("        \"_\": \"{}\",\n".format(table.super_class))

            for error in errors:
                all_module.write("        \"{}\": \"{}\",\n".format(error.row.error_id, error.class_name))

            all_module.write("    },\n")

        all_module.write("}\n")


def write_module(table: Table, *, errors: List[Error], notice: str, templates: Templates) -> None:
    sub_classes = []
    written: Set[str] = set()

    for error in errors:
        primary = error.primary

        if primary is not None and primary.table == table and primary.class_name not in written:
            msg = "{} is written before the {} it subclasses".format(error.class_name, primary.class_name)
            raise AssertionError(msg)

        sub_class = templates.sub_class.format(
            sub_class=error.class_name,
            bases=", ".join(error.bases),
            id="\"{}\"".format(error.row.error_id),
            docstring='"""{}"""'.format(error.row.message),
            code_and_name=code_and_name_block(error),
            value_property=value_block(templates, error=error)
        )

        sub_classes.append(sub_class)
        written.add(error.class_name)

    with open("{}/{}.py".format(DEST, table.module_name), "w", encoding="utf-8") as module:
        module.write(templates.module.format(
            notice=notice,
            typing_import=typing_import(errors),
            imports=import_block(table, errors=errors),
            super_class=table.super_class,
            code=table.code,
            docstring='"""{}"""'.format(table.title),
            sub_classes="".join(sub_classes)
        ))


def start() -> None:
    shutil.rmtree(DEST, ignore_errors=True)
    os.makedirs(DEST)

    notice = read_notice()
    templates = read_templates()

    # Every table is read before a single class is written. The name an error compiles to is not
    # its own to take - 52 of them are claimed by more than one error - and which claimant keeps
    # the plain name is only known once they all are.
    rows: List[Row] = []

    for file_name in sorted(os.listdir("{}/source".format(HOME))):
        rows.extend(read_rows(read_table(file_name)))

    tables = by_table(name_errors(rows))

    write_init(list(tables), notice=notice)
    write_all(tables, notice=notice, count=len(rows))

    for table, errors in tables.items():
        write_module(table, errors=errors, notice=notice, templates=templates)


if "__main__" == __name__:
    HOME = "."
    DEST = "../../pyrogram/errors/exceptions"
    NOTICE_PATH = "../../NOTICE"

    start()
