import argparse
import os.path
import re
from typing import Optional, Sequence

PYTHON_EXTENSION = (".py", ".ipynb")
EXCLUDE_FILES = ("__init__.py", "conftest.py")
EXCLUDE_DIRS = ("build", ".env", ".venv", ".virtual_env")
TEST_NAME_PATTERN = r"test_.*.py"
TEST_DIR_NAME = ("test", "tests", "unit_test")


def validate_file_name(filename) -> int:
    result_code = 0
    if filename != filename.lower():
        result_code = 1
        print(f'"{filename}" contain uppercase characters.')

    if " " in filename:
        result_code = 1
        print(f'"{filename}" contain space characters.')

    if "-" in filename:
        result_code = 1
        print(f'"{filename}" contain hyphen characters.')

    return result_code


def validate_test_file_name(file_name) -> int:
    base_name = os.path.basename(file_name)
    if not re.match(TEST_NAME_PATTERN, base_name):
        print(f'"{file_name}" does not match pattern "{TEST_NAME_PATTERN}"')
        return 1

    return 0


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("filenames", nargs="*")
    args = parser.parse_args(argv)

    result_code = 0
    for file_name in args.filenames:
        is_in_exclude_dir = len(set(file_name.split("/")) & set(EXCLUDE_DIRS)) != 0
        if is_in_exclude_dir:
            continue

        if os.path.basename(file_name) in EXCLUDE_FILES:
            continue

        if os.path.splitext(file_name)[1] not in PYTHON_EXTENSION:
            continue

        result_code += validate_file_name(file_name)

        is_in_test_dir = len(set(file_name.split("/")) & set(TEST_DIR_NAME)) != 0
        if is_in_test_dir:
            result_code += validate_test_file_name(file_name)

    return result_code


if __name__ == "__main__":
    raise SystemExit(main())
