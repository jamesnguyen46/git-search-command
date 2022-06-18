from pathlib import Path
import os
import sys
import re

if sys.version_info[:2] >= (3, 8):
    from importlib import metadata
else:
    import importlib_metadata as metadata


def get_app_version():
    __version__ = metadata.version("git-search-command")
    return __version__


def is_valid_environment_name(name: str):
    return re.match("^[A-Za-z0-9_-]*$", name)


def get_pyproject_path():
    root_path = Path(__file__).parent.parent.parent
    return os.path.join(root_path, "pyproject.toml")
