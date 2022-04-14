import re


def is_valid_environment_name(name: str):
    return re.match("^[A-Za-z0-9_-]*$", name)
