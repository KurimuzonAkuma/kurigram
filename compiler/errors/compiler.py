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


def start():
    shutil.rmtree(DEST, ignore_errors=True)
    os.makedirs(DEST)

    with open(NOTICE_PATH, encoding="utf-8") as f:
        notice = "\n".join(["# {}".format(line).strip() for line in f.readlines()])

    templates = {}

    for template_name in ("class", "sub_class", "sub_class_code"):
        with open("{}/template/{}.txt".format(HOME, template_name), encoding="utf-8") as f:
            templates[template_name] = f.read()

    modules = []
    errors = []
    count = 0

    # A first pass over every table. The name an error compiles to is not unique: 52 of them are
    # claimed by more than one error, and a name can only be handed out once all of its claimants
    # are known.
    for file_name in sorted(os.listdir("{}/source".format(HOME))):
        code, name = re.search(r"(\d+)_([A-Z_]+)", file_name).groups()

        module = {
            "code": int(code),
            "name": "{}_{}".format(name.lower(), code),
            "super_class": caml(name),
            "title": " ".join([str(i.capitalize()) for i in re.sub(r"_", " ", name).lower().split(" ")]),
            "errors": []
        }

        modules.append(module)

        with open("{}/source/{}".format(HOME, file_name), encoding="utf-8") as f_csv:
            for j, row in enumerate(csv.reader(f_csv, delimiter="\t")):
                if j == 0:
                    continue

                count += 1

                if not row:  # Row is empty (blank line)
                    continue

                error_id, error_message = row

                base_name = caml(re.sub(r"_X", "_", error_id))
                base_name = re.sub(r"^2", "Two", base_name)
                base_name = re.sub(r" ", "", base_name)

                error = {
                    "module": module,
                    "id": error_id,
                    "message": error_message,
                    "base_name": base_name
                }

                module["errors"].append(error)
                errors.append(error)

    by_base_name = {}

    for error in errors:
        by_base_name.setdefault(error["base_name"], []).append(error)

    # `pyrogram/errors/__init__.py` imports these after the generated ones, so a generated class of
    # the same name never reaches the caller: a 400 `UNKNOWN_ERROR` used to arrive as the
    # hand-written `UnknownError`, which reports code 520 and is no `BadRequest`.
    for reserved in ("RPCError", "UnknownError"):
        for error in by_base_name.pop(reserved, []):
            by_base_name.setdefault("{}{}".format(reserved, error["module"]["code"]), []).append(error)

    for base_name, group in by_base_name.items():
        group.sort(key=lambda item: (item["module"]["code"], item["id"]))

        primary, rest = group[0], group[1:]

        primary["class_name"] = base_name
        primary["bases"] = [primary["module"]["super_class"]]
        primary["primary"] = None

        for error in rest:
            error["primary"] = primary

            if error["module"]["code"] != primary["module"]["code"]:
                # The very same error under a second code. It keeps the name it shares, so that
                # `except PeerIdInvalid` still catches every one of them, and takes the category of
                # its own code as a second base, so that `except Forbidden` catches the 403 too.
                error["class_name"] = "{}{}".format(base_name, error["module"]["code"])
                error["bases"] = [base_name, error["module"]["super_class"]]
            else:
                # Two ids under one code that only differ by the value they carry, such as
                # `EMAIL_UNCONFIRMED` and `EMAIL_UNCONFIRMED_X`. The parameterised one is the one
                # that gets marked, and subclasses the other so both are caught by the plain name.
                error["class_name"] = "{}X".format(base_name)
                error["bases"] = [base_name]

    class_names = [error["class_name"] for error in errors]

    if len(class_names) != len(set(class_names)):
        raise AssertionError("two errors compile to the same class name")

    with open("{}/__init__.py".format(DEST), "w", encoding="utf-8") as f_init:
        f_init.write(notice + "\n\n")

        for module in modules:
            f_init.write("from .{} import *\n".format(module["name"]))

    with open("{}/all.py".format(DEST), "w", encoding="utf-8") as f_all:
        f_all.write(notice + "\n\n")
        f_all.write("count = {}\n\n".format(count))
        f_all.write("exceptions = {\n")

        for module in modules:
            f_all.write("    {}: {{\n".format(module["code"]))
            f_all.write("        \"_\": \"{}\",\n".format(module["super_class"]))

            for error in module["errors"]:
                f_all.write("        \"{}\": \"{}\",\n".format(error["id"], error["class_name"]))

            f_all.write("    },\n")

        f_all.write("}\n")

    for module in modules:
        imports = {}

        for error in module["errors"]:
            primary = error["primary"]

            if primary is not None and primary["module"] is not module:
                imports.setdefault(primary["module"]["name"], set()).add(primary["class_name"])

        # An error only ever subclasses one of a lower code, so these imports run downwards and
        # can never form a cycle.
        import_lines = "".join([
            "\nfrom .{} import (\n{}\n)".format(
                module_name,
                "".join(["    {},\n".format(class_name) for class_name in sorted(names)]).rstrip("\n")
            )
            for module_name, names in sorted(imports.items())
        ])

        sub_classes = []
        written = set()

        for error in module["errors"]:
            primary = error["primary"]

            if primary is not None and primary["module"] is module and primary["class_name"] not in written:
                raise AssertionError("{} is written before the {} it subclasses".format(
                    error["class_name"], primary["class_name"]
                ))

            code_and_name = "" if len(error["bases"]) == 1 else templates["sub_class_code"].format(
                code=module["code"],
                name=module["title"]
            )

            sub_classes.append(templates["sub_class"].format(
                sub_class=error["class_name"],
                bases=", ".join(error["bases"]),
                id="\"{}\"".format(error["id"]),
                docstring='"""{}"""'.format(error["message"]),
                code_and_name=code_and_name
            ))

            written.add(error["class_name"])

        with open("{}/{}.py".format(DEST, module["name"]), "w", encoding="utf-8") as f_class:
            f_class.write(templates["class"].format(
                notice=notice,
                imports=import_lines,
                super_class=module["super_class"],
                code=module["code"],
                docstring='"""{}"""'.format(module["title"]),
                sub_classes="".join(sub_classes)
            ))


if "__main__" == __name__:
    HOME = "."
    DEST = "../../pyrogram/errors/exceptions"
    NOTICE_PATH = "../../NOTICE"

    start()
