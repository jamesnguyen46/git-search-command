import argparse
import os.path
import json
from typing import Optional, Sequence

FILE_NAMES = ("settings.json", "test.env")
JSON_KEYS = (
    "project.debug.args_keyword",
    "project.debug.args_group_name",
    "project.debug.args_project_id",
)
ENV_KEYS = ("GITLAB_BASE_URL", "GITLAB_API_TOKEN")


def detect_private_env_value(file_name) -> int:
    result_code = 0
    result_msg = ""
    with open(file_name, "r", encoding="utf-8") as content:
        for line in content:
            name, var = line.partition("=")[::2]
            if (name.strip() in ENV_KEYS) and bool(var and not var.isspace()):
                result_code = 1
                result_msg += f' + "{var.strip()}" (in "{name}" key)\n'

    if result_code != 0:
        print(f'"{file_name}" file contains the private values :')
        print(result_msg)

    return result_code


def detect_private_config_value(file_name) -> int:
    result_code = 0
    result_msg = ""
    with open(file_name, "r", encoding="utf-8") as jsonfile:
        jsondata = ""
        # Remove all comments in config file
        for line in jsonfile:
            jsondata += line.split("//")[0]

        obj = json.loads(jsondata)
        for key in JSON_KEYS:
            value = obj[f"{key}"]
            if key in obj and len(value) != 0:
                result_code = 1
                result_msg += f' + "{value}" (in "{key}" key)\n'

    if result_code != 0:
        print(f'"{file_name}" file contains the private values :')
        print(result_msg)

    return result_code


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("filenames", nargs="*")
    args = parser.parse_args(argv)

    result_code = 0
    for file_name in args.filenames:
        base_name = os.path.basename(file_name)
        ext = os.path.splitext(file_name)[1]
        if base_name not in FILE_NAMES:
            continue

        if ext == ".json":
            result_code += detect_private_config_value(file_name)
        elif ext == ".env":
            result_code += detect_private_env_value(file_name)

    return result_code


if __name__ == "__main__":
    raise SystemExit(main())
