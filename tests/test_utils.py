import sys
import pytest
from gsc import utils

mock_data = {
    "Name": "git-search-command",
    "Summary": "This is the project summary.",
    "Author": "Author name",
    "Author-email": "Author's email",
    "Home-page": "https://project.com",
    "License": "Apache",
}
MOCK_VERSION = "2.2.2"


@pytest.fixture
def setup_mock_metadata(mocker):
    if sys.version_info[:2] >= (3, 8):
        mocker.patch("importlib.metadata.metadata", return_value=mock_data)
    else:
        mocker.patch("importlib_metadata.metadata", return_value=mock_data)


@pytest.fixture
def setup_mock_version(mocker):
    if sys.version_info[:2] >= (3, 8):
        mocker.patch("importlib.metadata.version", return_value=MOCK_VERSION)
    else:
        mocker.patch("importlib_metadata.version", return_value=MOCK_VERSION)


@pytest.mark.usefixtures("setup_mock_metadata")
def test_get_project_name():
    assert mock_data["Name"] in utils.get_project_name()


@pytest.mark.usefixtures("setup_mock_metadata")
def test_get_project_summary():
    assert mock_data["Summary"] in utils.get_project_summary()


@pytest.mark.usefixtures("setup_mock_metadata")
def test_get_project_author():
    assert mock_data["Author"] in utils.get_project_author()


@pytest.mark.usefixtures("setup_mock_metadata")
def test_get_project_author_email():
    assert mock_data["Author-email"] in utils.get_project_author_email()


@pytest.mark.usefixtures("setup_mock_metadata")
def test_get_project_home_page():
    assert mock_data["Home-page"] in utils.get_project_home_page()


@pytest.mark.usefixtures("setup_mock_version")
def test_get_project_version():
    assert MOCK_VERSION in utils.get_project_version()


@pytest.mark.usefixtures("setup_mock_metadata")
def test_get_project_license():
    assert mock_data["License"] in utils.get_project_license()


@pytest.mark.parametrize(
    "env_name",
    [
        "ValidEnv",
        "valid_env",
        "valid-env",
        "validenv",
        "valid_env_123",
        "123-valid-env",
        "0123456789",
    ],
)
def test_environment_name_is_valid(env_name):
    assert utils.is_valid_environment_name(env_name)


@pytest.mark.parametrize(
    "env_name",
    [
        "invalid.env",
        "invalid env",
        "!@#$%^&*()",
        "-invalid_env",
        "invalid_env_",
    ],
)
def test_environment_name_is_invalid(env_name):
    assert not utils.is_valid_environment_name(env_name)


@pytest.mark.parametrize(
    "file_path",
    [
        "/Users/abc/Desktop/output.md",
        "/Users/abc/Desktop/output.markdown",
        "C:\\Desktop\\output.md",
        "C:\\Desktop\\output.markdown",
    ],
)
def test_is_supported_extension_output_file_valid(file_path):
    assert utils.is_supported_extension_output_file(file_path)


@pytest.mark.parametrize(
    "file_path",
    [
        "/Users/abc/Desktop/output.html",
        "C:\\Desktop\\output.html",
        ".markdown",
        "abcxyz",
    ],
)
def test_is_supported_extension_output_file_invalid(file_path):
    assert not utils.is_supported_extension_output_file(file_path)


def test_is_supported_extension_output_file_throw_exception(mocker):
    mocker.patch("os.path.splitext", return_value=Exception("Error"))
    assert not utils.is_supported_extension_output_file("/Users/abc/Desktop/output.md")
