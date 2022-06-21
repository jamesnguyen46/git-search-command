import os
import sys
import re

if sys.version_info[:2] >= (3, 8):
    from importlib import metadata
else:
    import importlib_metadata as metadata

DISTRIBUTION_NAME = "git-search-command"
EXTENSION_SUPPORTED = (".md", ".markdown")


def get_project_name():
    return __get_project_metadata()["Name"]


def get_project_summary():
    return __get_project_metadata()["Summary"]


def get_project_author():
    return __get_project_metadata()["Author"]


def get_project_author_email():
    return __get_project_metadata()["Author-email"]


def get_project_home_page():
    return __get_project_metadata()["Home-page"]


def get_project_version():
    __version__ = metadata.version(DISTRIBUTION_NAME)
    return __version__


def get_project_license():
    return __get_project_metadata()["License"]


def is_valid_environment_name(name: str):
    return re.match(r"^[^_-][\w\d_-][^\s\.]*[^_-]$", name)


def is_supported_extension_output_file(output_path: str):
    try:
        return os.path.splitext(output_path)[1] in EXTENSION_SUPPORTED
    except Exception as _:
        return False


def __get_project_metadata():
    return metadata.metadata(DISTRIBUTION_NAME)
