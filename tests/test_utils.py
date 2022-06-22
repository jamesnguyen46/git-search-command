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
def setup_metadata(mocker):
    if sys.version_info[:2] >= (3, 8):
        mocker.patch("importlib.metadata.metadata", return_value=mock_data)
    else:
        mocker.patch("importlib_metadata.metadata", return_value=mock_data)


@pytest.fixture
def setup_version(mocker):
    if sys.version_info[:2] >= (3, 8):
        mocker.patch("importlib.metadata.version", return_value=MOCK_VERSION)
    else:
        mocker.patch("importlib_metadata.version", return_value=MOCK_VERSION)


@pytest.mark.usefixtures("setup_metadata")
def test_get_project_name():
    assert mock_data["Name"] in utils.get_project_name()


@pytest.mark.usefixtures("setup_metadata")
def test_get_project_summary():
    assert mock_data["Summary"] in utils.get_project_summary()


@pytest.mark.usefixtures("setup_metadata")
def test_get_project_author():
    assert mock_data["Author"] in utils.get_project_author()


@pytest.mark.usefixtures("setup_metadata")
def test_get_project_author_email():
    assert mock_data["Author-email"] in utils.get_project_author_email()


@pytest.mark.usefixtures("setup_metadata")
def test_get_project_home_page():
    assert mock_data["Home-page"] in utils.get_project_home_page()


@pytest.mark.usefixtures("setup_version")
def test_get_project_version():
    assert MOCK_VERSION in utils.get_project_version()


@pytest.mark.usefixtures("setup_metadata")
def test_get_project_license():
    assert mock_data["License"] in utils.get_project_license()


def test_is_valid_environment_name():
    valid_name = [
        "ValidEnv",
        "valid_env",
        "valid-env",
        "validenv",
        "valid_env_123",
        "123-valid-env",
        "0123456789",
    ]
    invalid_name = [
        "invalid.env",
        "invalid env",
        "!@#$%^&*()",
        "-invalid_env",
        "invalid_env_",
    ]

    for name in valid_name:
        assert utils.is_valid_environment_name(name) is not None

    for name in invalid_name:
        assert utils.is_valid_environment_name(name) is None


def test_is_supported_extension_output_file():
    assert utils.is_supported_extension_output_file("/Users/abc/Desktop/output.md")
    assert utils.is_supported_extension_output_file(
        "/Users/abc/Desktop/output.markdown"
    )
    assert utils.is_supported_extension_output_file("C:\\Desktop\\output.md")
    assert utils.is_supported_extension_output_file("C:\\Desktop\\output.markdown")
    assert not utils.is_supported_extension_output_file(
        "/Users/abc/Desktop/output.html"
    )
    assert not utils.is_supported_extension_output_file("C:\\Desktop\\output.html")
    assert not utils.is_supported_extension_output_file(".markdown")
    assert not utils.is_supported_extension_output_file("abcxyz")
    assert not utils.is_supported_extension_output_file(123456)
