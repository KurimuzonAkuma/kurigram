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
from typing import List

HOME = "compiler/errors"
DEST = "pyrogram/errors/exceptions"
NOTICE_PATH = "NOTICE"


def snek(s):
    # https://stackoverflow.com/questions/1175208/elegant-python-function-to-convert-camelcase-to-snake-case
    s = re.sub(r"(.)([A-Z][a-z]+)", r"\1_\2", s)
    return re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", s).lower()


def caml(s):
    s = snek(s).split("_")
    return "".join([str(i.title()) for i in s])


@dataclass(frozen=True)
class SubClass:
    name: str
    error_id: str
    message: str
    value_name: str


def value_property(template: str, *, value_name: str) -> str:
    if value_name == "value":
        return ""

    # A blank line, then the block, appended to the `MESSAGE = __doc__` line the sub class template
    # ends its body with. Spelled out here rather than left to whichever newlines the template file
    # happens to begin and end with.
    return "\n\n" + template.format(value_name=value_name).rstrip("\n")


def typing_import(sub_classes: List[SubClass]) -> str:
    if all(sub_class.value_name == "value" for sub_class in sub_classes):
        return ""

    return "from typing import Optional\n\n"


def start():
    shutil.rmtree(DEST, ignore_errors=True)
    os.makedirs(DEST)

    files = [i for i in os.listdir("{}/source".format(HOME))]

    with open(NOTICE_PATH, encoding="utf-8") as f:
        notice = []

        for line in f.readlines():
            notice.append("# {}".format(line).strip())

        notice = "\n".join(notice)

    with open("{}/all.py".format(DEST), "w", encoding="utf-8") as f_all:
        f_all.write(notice + "\n\n")
        f_all.write("count = {count}\n\n")
        f_all.write("exceptions = {\n")

        count = 0

        for i in files:
            code, name = re.search(r"(\d+)_([A-Z_]+)", i).groups()

            f_all.write("    {}: {{\n".format(code))

            init = "{}/__init__.py".format(DEST)

            if not os.path.exists(init):
                with open(init, "w", encoding="utf-8") as f_init:
                    f_init.write(notice + "\n\n")

            with open(init, "a", encoding="utf-8") as f_init:
                f_init.write("from .{}_{} import *\n".format(name.lower(), code))

            with open("{}/source/{}".format(HOME, i), encoding="utf-8") as f_csv, \
                open("{}/{}_{}.py".format(DEST, name.lower(), code), "w", encoding="utf-8") as f_class:
                reader = csv.reader(f_csv, delimiter="\t")

                super_class = caml(name)
                name = " ".join([str(i.capitalize()) for i in re.sub(r"_", " ", name).lower().split(" ")])

                sub_classes = []

                f_all.write("        \"_\": \"{}\",\n".format(super_class))

                for j, row in enumerate(reader):
                    if j == 0:
                        continue

                    count += 1

                    if not row:  # Row is empty (blank line)
                        continue

                    error_id, error_message = row

                    class_name = caml(re.sub(r"_X", "_", error_id))
                    class_name = re.sub(r"^2", "Two", class_name)
                    class_name = re.sub(r" ", "", class_name)

                    f_all.write("        \"{}\": \"{}\",\n".format(error_id, class_name))

                    # The placeholder in a message is what the value Telegram sends along with
                    # the error means, so it is also the name the error exposes it under. A
                    # message that still says "{value}" gets no property: `value` is the
                    # attribute itself, and a property of that name would shadow it.
                    #
                    # The names are Telegram's own words for each value, from the descriptions in
                    # https://corefork.telegram.org/api/errors.json, or the schema's word for the
                    # same thing (`dc_id` is `auth.exportAuthorization.dc_id`, `file_part` is
                    # `upload.saveFilePart.file_part`). Where Telethon already named one, the name
                    # is theirs:
                    # https://github.com/LonamiWebs/Telethon/blob/v1.36.0/telethon_generator/data/errors.csv
                    #
                    # One placeholder per message, at most. `RPCError.raise_it()` reads a single
                    # number out of an error message and renders the message with it, so a second
                    # placeholder could never be filled in - `str.format()` would raise `KeyError`
                    # on the error nobody can catch.
                    placeholders = re.findall(r"\{(\w*)\}", error_message)

                    if len(placeholders) > 1:
                        msg = "{} carries more than one placeholder: {}".format(error_id, error_message)
                        raise ValueError(msg)

                    value_name = placeholders[0] if placeholders else "value"

                    sub_class = SubClass(
                        name=class_name,
                        error_id=error_id,
                        message=error_message,
                        value_name=value_name
                    )

                    sub_classes.append(sub_class)

                with open("{}/template/class.txt".format(HOME), "r", encoding="utf-8") as f_class_template:
                    class_template = f_class_template.read()

                    with open("{}/template/sub_class.txt".format(HOME), "r", encoding="utf-8") as f_sub_class_template:
                        sub_class_template = f_sub_class_template.read()

                    with open("{}/template/value_property.txt".format(HOME), "r", encoding="utf-8") as f_value_property_template:
                        value_property_template = f_value_property_template.read()

                    class_template = class_template.format(
                        notice=notice,
                        typing_import=typing_import(sub_classes),
                        super_class=super_class,
                        code=code,
                        docstring='"""{}"""'.format(name),
                        sub_classes="".join([sub_class_template.format(
                            sub_class=sub_class.name,
                            super_class=super_class,
                            id="\"{}\"".format(sub_class.error_id),
                            docstring='"""{}"""'.format(sub_class.message),
                            value_property=value_property(
                                value_property_template,
                                value_name=sub_class.value_name
                            )
                        ) for sub_class in sub_classes])
                    )

                f_class.write(class_template)

            f_all.write("    },\n")

        f_all.write("}\n")

    with open("{}/all.py".format(DEST), encoding="utf-8") as f:
        content = f.read()

    with open("{}/all.py".format(DEST), "w", encoding="utf-8") as f:
        f.write(re.sub("{count}", str(count), content))


if "__main__" == __name__:
    HOME = "."
    DEST = "../../pyrogram/errors/exceptions"
    NOTICE_PATH = "../../NOTICE"

    start()
