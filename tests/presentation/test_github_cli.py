import re
from unittest import mock
from click import testing

# pylint: disable=redefined-outer-name
import pytest

from gsc.config import GitHubConfig
from gsc.presentation.command_line import cli, github_cli
from gsc.di.application_container import ApplicationContainer

REGEX_MISSING_ARGUMENT = r"Error: Option (\'(\-|\-\-).*[a-z]\') requires an argument."


@pytest.fixture(scope="module", autouse=True)
def container():
    app_container = ApplicationContainer()
    app_container.init_resources()
    app_container.wire(packages=["gsc"])
    return app_container


@pytest.fixture
def runner():
    return testing.CliRunner()


@pytest.fixture
def set_up_mock_env(mocker):
    env = mock.MagicMock()
    env.configure_mock(name="mock_env")
    env.configure_mock(host_name="https://hostname")
    env.configure_mock(private_token="XXXYYYZZZ")
    mocker.patch.object(GitHubConfig, "get_default_env", return_value=env)
    mocker.patch.object(GitHubConfig, "get_session_env", return_value=env)
    mocker.patch.object(GitHubConfig, "is_env_existed", return_value=True)


@pytest.mark.parametrize("arguments", ["gh", "gh -h", "gh --help"])
def test_github_help(runner, arguments):
    expected_msg = [
        "Search in GitHub repositories.",
        "-h, --help",
        "Show this message and exit.",
        "env",
        "Setup the environment for searching, support multiple environments.",
        "search",
        "Search the content in all GitHub repositories that you owned, not including fork repository.",
    ]
    result = runner.invoke(cli.app, arguments, terminal_width=5000)
    assert result.exit_code == 0
    assert all(x in result.output for x in expected_msg)


def test_github_search_wo_keyword(runner):
    expected_msg = [
        "Usage: gsc gh search [OPTIONS] <keyword>",
        "Try 'gsc gh search -h' for help.",
        "Error: Missing required argument <keyword>",
    ]
    result = runner.invoke(github_cli.search, [])
    assert result.exit_code == 2
    assert all(x in result.output for x in expected_msg)


@pytest.mark.parametrize("arguments", ["gh search -h", "gh search --help"])
def test_github_search_help(runner, arguments):
    # pylint: disable=C0301
    expected_msg = [
        "Search the content in all GitHub repositories that you owned, not including fork repository.",
        "-p, --repository <string>",
        'Search in the specified repository, input the full name of repository, example : "username/repository_name".',
        "-e, --environment <string>",
        "Select the environment for searching, if not declare, default environment has been used.",
        "-o, --output <file_path>",
        "Export the search result to markdown file with extension .md or .markdown.",
        "-d, --debug",
        "Enable debug logging of HTTP request.",
    ]
    result = runner.invoke(cli.app, arguments, terminal_width=500)
    assert result.exit_code == 0
    assert all(x in result.output for x in expected_msg)


@pytest.mark.parametrize("arguments", ["123456789", "keyword"])
@pytest.mark.usefixtures("set_up_mock_env")
def test_github_search_w_keyword(mocker, runner, arguments):
    mock_func = mocker.patch(
        "gsc.presentation.command_line.github_cli.__search_in_multiple_repo"
    )
    result = runner.invoke(github_cli.search, arguments)
    assert result.exit_code == 0
    assert mock_func.assert_called_once


@pytest.mark.parametrize(
    "arguments",
    [
        "keyword -p",
        "keyword --repository",
    ],
)
def test_github_search_w_keyword_w_repository_invalid_value(runner, arguments):
    result = runner.invoke(github_cli.search, arguments)
    assert result.exception
    assert result.exit_code == 2
    assert re.match(REGEX_MISSING_ARGUMENT, result.output)


@pytest.mark.parametrize(
    "arguments",
    [
        "keyword -p username/repository_name",
        "keyword --repository username/repository_name",
        "keyword --repository=username/repository_name",
    ],
)
@pytest.mark.usefixtures("set_up_mock_env")
def test_github_search_w_keyword_w_repository_valid_value(mocker, runner, arguments):
    mock_func = mocker.patch(
        "gsc.presentation.command_line.github_cli.__search_in_single_repo"
    )
    result = runner.invoke(github_cli.search, arguments)
    assert result.exit_code == 0
    assert mock_func.assert_called_once


@pytest.mark.parametrize("arguments", ["keyword -e", "keyword --environment"])
def test_github_search_w_keyword_w_session_env_invalid_value(runner, arguments):
    result = runner.invoke(github_cli.search, arguments)
    assert result.exception
    assert result.exit_code == 2
    assert re.match(REGEX_MISSING_ARGUMENT, result.output)


@pytest.mark.parametrize("arguments", ["keyword"])
def test_github_search_w_keyword_w_session_env_list_no_value(mocker, runner, arguments):
    expected_msg = [
        "There is no environment.",
        "Try `gsc gh env --new <environment_name>` before searching.",
    ]
    mocker.patch.object(GitHubConfig, "get_default_env", return_value=None)
    result = runner.invoke(github_cli.search, arguments)
    assert result.exit_code == 2
    assert all(x in result.output for x in expected_msg)


@pytest.mark.parametrize(
    "arguments",
    [
        "keyword -e personal",
        "keyword --environment personal",
    ],
)
def test_github_search_w_keyword_w_session_env_not_existed(mocker, runner, arguments):
    expected_msg = [
        '"personal" is not existed in your environment list.',
        "Try `gsc gh env --new <environment_name>` before searching.",
    ]
    mocker.patch.object(GitHubConfig, "is_env_existed", return_value=False)
    result = runner.invoke(github_cli.search, arguments)
    assert result.exit_code == 2
    assert all(x in result.output for x in expected_msg)


@pytest.mark.parametrize(
    "arguments",
    [
        "keyword -o",
        "keyword --output",
    ],
)
def test_github_search_w_keyword_w_output_invalid_value(runner, arguments):
    result = runner.invoke(github_cli.search, arguments)
    assert result.exception
    assert result.exit_code == 2
    assert re.match(REGEX_MISSING_ARGUMENT, result.output)


@pytest.mark.parametrize(
    "arguments",
    [
        "keyword -o=",
        "keyword -o result",
        "keyword -o result.txt",
        "keyword -o ~/Desktop/result.txt",
        "keyword --output result",
        "keyword --output result.txt",
        "keyword --output ~/Desktop/result.txt",
    ],
)
def test_github_search_w_keyword_w_output_ext_file_not_supported(runner, arguments):
    expected_msg = [
        "Usage: gsc gh search [OPTIONS] <keyword>",
        "Try 'gsc gh search -h' for help.",
        "Error: Output file type is not supported.",
    ]
    result = runner.invoke(github_cli.search, arguments)
    assert result.exit_code == 2
    assert all(x in result.output for x in expected_msg)


@pytest.mark.parametrize(
    "arguments",
    [
        "keyword -o result.md",
        "keyword -o result.markdown",
        "keyword -o ~/Desktop/result.markdown",
        "keyword --output result.md",
        "keyword --output result.markdown",
        "keyword --output ~/Desktop/result.markdown",
    ],
)
@pytest.mark.usefixtures("set_up_mock_env")
def test_github_search_w_keyword_w_output_valid_value(mocker, runner, arguments):
    mock_func = mocker.patch(
        "gsc.presentation.command_line.github_cli.__search_in_multiple_repo"
    )
    result = runner.invoke(github_cli.search, arguments)
    assert result.exit_code == 0
    assert mock_func.assert_called_once
