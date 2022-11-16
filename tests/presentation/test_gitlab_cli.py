import re
from unittest import mock
from click import testing

# pylint: disable=redefined-outer-name
import pytest

from gsc.config import GitLabConfig
from gsc.presentation.command_line import cli, gitlab_cli
from gsc.di.application_container import ApplicationContainer


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
    mocker.patch.object(GitLabConfig, "get_default_env", return_value=env)
    mocker.patch.object(GitLabConfig, "get_session_env", return_value=env)
    mocker.patch.object(GitLabConfig, "is_env_existed", return_value=True)


@pytest.mark.parametrize("arguments", ["gl", "gl -h", "gl --help"])
def test_gitlab_help(runner, arguments):
    expected_msg = [
        "Search in GitLab repositories.",
        "-h, --help",
        "Show this message and exit.",
        "env",
        "Setup the environment for searching, support multiple environments.",
        "search",
        "Search the content in GitLab repositories.",
    ]
    result = runner.invoke(cli.app, arguments)
    assert result.exit_code == 0
    assert all(x in result.output for x in expected_msg)


def test_gitlab_search_wo_keyword(runner):
    expected_msg = [
        "Usage: gsc gl search [OPTIONS] <keyword>",
        "Try 'gsc gl search -h' for help.",
        "Error: Missing required argument <keyword>",
    ]
    result = runner.invoke(gitlab_cli.search, [])
    assert result.exit_code == 2
    assert all(x in result.output for x in expected_msg)


@pytest.mark.parametrize("arguments", ["gl search -h", "gl search --help"])
def test_gitlab_search_help(runner, arguments):
    # pylint: disable=C0301
    expected_msg = [
        "Search the content in GitLab repositories.",
        "-p, --project <int>",
        "Search in the specified project, input project id [required at least one of --project and --group].",
        "-g, --group <string>",
        "Search in the specified project group, input group id or group path [required at least one of --project and --group].",
        "-e, --environment <string>",
        "Select the environment for searching, if not declare, default environment has been used.",
        "-o, --output <file_path>",
        "Export the search result to markdown file with extension .md or .markdown.",
        "-d, --debug",
        "Enable debug logging of HTTP request.",
        "--code-preview",
        "Show code preview.",
        "--ignore-no-result",
        "Do not show the project which has no result (for searching group).",
    ]
    result = runner.invoke(cli.app, arguments, terminal_width=500)
    assert result.exit_code == 0
    assert all(x in result.output for x in expected_msg)


@pytest.mark.parametrize("arguments", ["keyword", "123456789"])
def test_gitlab_search_w_keyword_wo_project_or_group(runner, arguments):
    expected_msg = [
        "Usage: gsc gl search [OPTIONS] <keyword>",
        "Try 'gsc gl search -h' for help.",
        "Error: Missing option --project <int> or --group <string>",
    ]
    result = runner.invoke(gitlab_cli.search, arguments)
    assert result.exit_code == 2
    assert all(x in result.output for x in expected_msg)


@pytest.mark.parametrize(
    "arguments",
    [
        "keyword -p",
        "keyword -p=",
        "keyword -p python",
        "keyword -p=python",
        "keyword -p=123456",
        "keyword --project",
        "keyword --project=",
        "keyword --project python",
        "keyword --project=python",
    ],
)
def test_gitlab_search_w_keyword_w_project_invalid_value(runner, arguments):
    result = runner.invoke(gitlab_cli.search, arguments)
    assert result.exception
    assert result.exit_code == 2


@pytest.mark.parametrize(
    "arguments",
    [
        "keyword -p 123456",
        "keyword --project 123456",
        "keyword --project=123456",
    ],
)
@pytest.mark.usefixtures("set_up_mock_env")
def test_gitlab_search_w_keyword_w_project_valid_value(mocker, runner, arguments):
    mock_func = mocker.patch(
        "gsc.presentation.command_line.gitlab_cli.__search_in_project"
    )
    result = runner.invoke(gitlab_cli.search, arguments)
    assert result.exit_code == 0
    assert mock_func.assert_called_once


@pytest.mark.parametrize(
    "arguments",
    [
        "keyword -g",
        "keyword --group",
    ],
)
def test_gitlab_search_w_keyword_w_group_invalid_value(runner, arguments):
    result = runner.invoke(gitlab_cli.search, arguments)
    assert result.exception
    assert result.exit_code == 2


@pytest.mark.parametrize(
    "arguments",
    [
        "keyword -g python_grp",
        "keyword -g=python_grp",
        "keyword --group python_grp",
        "keyword --group=python_grp",
    ],
)
@pytest.mark.usefixtures("set_up_mock_env")
def test_gitlab_search_w_keyword_w_group_valid_value(mocker, runner, arguments):
    mock_func = mocker.patch(
        "gsc.presentation.command_line.gitlab_cli.__search_in_group"
    )
    result = runner.invoke(gitlab_cli.search, arguments)
    assert result.exit_code == 0
    assert mock_func.assert_called_once


@pytest.mark.parametrize(
    "arguments", ["keyword -p 123456 -e", "keyword -p 123456 --environment"]
)
def test_gitlab_search_w_keyword_w_project_w_session_env_invalid_value(
    runner, arguments
):
    result = runner.invoke(gitlab_cli.search, arguments)
    assert result.exception
    assert result.exit_code == 2


@pytest.mark.parametrize("arguments", ["keyword -p 123456"])
def test_gitlab_search_w_keyword_w_project_w_session_env_list_no_value(
    mocker, runner, arguments
):
    expected_msg = [
        "There is no environment.",
        "Try `gsc gl env --new <environment_name>` before searching.",
    ]
    mocker.patch.object(GitLabConfig, "get_default_env", return_value=None)
    result = runner.invoke(gitlab_cli.search, arguments)
    assert result.exit_code == 2
    assert all(x in result.output for x in expected_msg)


@pytest.mark.parametrize(
    "arguments",
    [
        "keyword -p 123456 -e personal",
        "keyword -p 123456 --environment personal",
    ],
)
def test_gitlab_search_w_keyword_w_project_w_session_env_not_existed(
    mocker, runner, arguments
):
    expected_msg = [
        '"personal" is not existed in your environment list.',
        "Try `gsc gl env --new <environment_name>` before searching.",
    ]
    mocker.patch.object(GitLabConfig, "is_env_existed", return_value=False)
    result = runner.invoke(gitlab_cli.search, arguments)
    assert result.exit_code == 2
    assert all(x in result.output for x in expected_msg)


@pytest.mark.parametrize(
    "arguments",
    [
        "keyword -p 123456 -o",
        "keyword -p 123456 --output",
    ],
)
def test_gitlab_search_w_keyword_w_project_w_output_invalid_value(runner, arguments):
    result = runner.invoke(gitlab_cli.search, arguments)
    assert result.exception
    assert result.exit_code == 2
    assert re.match(
        r"^Error: Option '\-(?:\-output|o)' requires an argument\.$", result.output
    )


@pytest.mark.parametrize(
    "arguments",
    [
        "keyword -p 123456 -o=",
        "keyword -p 123456 -o result",
        "keyword -p 123456 -o result.txt",
        "keyword -p 123456 -o ~/Desktop/result.txt",
        "keyword -p 123456 --output result",
        "keyword -p 123456 --output result.txt",
        "keyword -p 123456 --output ~/Desktop/result.txt",
    ],
)
def test_gitlab_search_w_keyword_w_project_w_output_ext_file_not_supported(
    runner, arguments
):
    expected_msg = [
        "Usage: gsc gl search [OPTIONS] <keyword>",
        "Try 'gsc gl search -h' for help.",
        "Error: Output file type is not supported.",
    ]
    result = runner.invoke(gitlab_cli.search, arguments)
    assert result.exit_code == 2
    assert all(x in result.output for x in expected_msg)


@pytest.mark.parametrize(
    "arguments",
    [
        "keyword -p 123456 -o result.md",
        "keyword -p 123456 -o result.markdown",
        "keyword -p 123456 -o ~/Desktop/result.markdown",
        "keyword -p 123456 --output result.md",
        "keyword -p 123456 --output result.markdown",
        "keyword -p 123456 --output ~/Desktop/result.markdown",
    ],
)
def test_gitlab_search_w_keyword_w_project_w_output_valid_value(
    mocker, runner, arguments
):
    mock_func = mocker.patch(
        "gsc.presentation.command_line.gitlab_cli.__search_in_project"
    )
    result = runner.invoke(gitlab_cli.search, arguments)
    assert result.exit_code == 0
    assert mock_func.assert_called_once
