from click.testing import CliRunner

# pylint: disable=redefined-outer-name
import pytest
from gsc.presentation.command_line import cli


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def set_up_mock_data(mocker):
    mocker.patch("gsc.utils.get_project_name", return_value="git-search-command")
    mocker.patch("gsc.utils.get_project_summary", return_value="Project Summary")
    mocker.patch("gsc.utils.get_project_author", return_value="James")
    mocker.patch("gsc.utils.get_project_author_email", return_value="james@gmail.com")
    mocker.patch(
        "gsc.utils.get_project_home_page", return_value="https://git-search-command.com"
    )
    mocker.patch("gsc.utils.get_project_version", return_value="2.2.2")
    mocker.patch("gsc.utils.get_project_license", return_value="Apache")


@pytest.mark.parametrize("arguments", [[], ["-h"], ["--help"]])
def test_app_help(runner, arguments):
    expected_msg = [
        "A simple tool to search the content in the project scope for GitLab and GitHub repositories.",
        "-i, --info",
        "Show the information of gsc.",
        "-h, --help",
        "Show this message and exit.",
        "gh",
        "Search in GitHub repositories.",
        "gl",
        "Search in GitLab repositories.",
    ]
    result = runner.invoke(cli.app, arguments, terminal_width=100)
    assert result.exit_code == 0
    assert all(x in result.output for x in expected_msg)


@pytest.mark.parametrize("arguments", ["-i", "--info"])
@pytest.mark.usefixtures("set_up_mock_data")
def test_app_param_info(runner, arguments):
    expected_msg = [
        "Name",
        "GSC - Git Search Command",
        "Description",
        "Project Summary",
        "Author",
        "James <james@gmail.com>",
        "Source",
        "https://git-search-command.com",
        "Version",
        "2.2.2",
        "License",
        "Apache",
    ]
    result = runner.invoke(cli.app, arguments, terminal_width=100)
    assert result.exit_code == 0
    assert all(x in result.output for x in expected_msg)
