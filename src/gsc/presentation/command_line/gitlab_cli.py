import click
from dependency_injector.wiring import Provide, inject
from gsc import utils
from gsc.di.application_container import ApplicationContainer
from gsc.constants import GitLabConstant
from gsc.presentation.command_line.env_cli import environment
from gsc.presentation.command_line import keep_main_thread_running
from gsc.presentation.observer.gitlab_observer import (
    GitLabParam,
    GitLabPrintObserver,
)
from gsc.config import AppConfig, GitLabConfig
from gsc.domain.use_cases.gitlab_search_use_case import (
    GitLabSearchGroupUseCase,
    GitLabSearchProjectUseCase,
)

app_config: AppConfig = Provide[ApplicationContainer.gitlab_module.app_config]
gitlab_config: GitLabConfig = Provide[ApplicationContainer.gitlab_module.config]


@click.group("gl", help=f"Search in {GitLabConstant.NAME} projects.")
def gitlab_cli():
    pass


gitlab_cli.add_command(environment)


def __validate_required_keyword_argument(ctx, _, value):
    if value is None:
        click.secho("Usage: gsc gl search [OPTIONS] <keyword>")
        click.secho("Try 'gsc gl search -h' for help.")
        click.secho("\n", nl=False)
        click.secho("Error: Missing required argument <keyword>")
        ctx.exit(2)
    return value


def __validate_session_env_option(ctx, _, value):
    if not value:
        click.secho("There is no environment.")
        click.secho("Try `gsc gl env --new <environment_name>` before searching.")
        ctx.exit(2)
    elif not gitlab_config.is_env_existed(value):
        click.secho(f'"{value}" is not existed in your environment list.')
        click.secho("Try `gsc gl env --new <environment_name>` before searching.")
        ctx.exit(2)
    else:
        pass

    gitlab_config.set_session_env(value)
    return value


def __validate_output_option(ctx, _, value):
    if value and not utils.is_supported_extension_output_file(value):
        click.secho("Usage: gsc gl search [OPTIONS] <keyword>")
        click.secho("Try 'gsc gl search -h' for help.")
        click.secho("\n", nl=False)
        click.secho("Error: Output file type is not supported.")
        ctx.exit(2)

    return value


@gitlab_cli.command(
    "search", help=f"Search the content in {GitLabConstant.NAME} projects."
)
@click.argument(
    "keyword",
    type=str,
    metavar="<keyword>",
    required=False,
    callback=__validate_required_keyword_argument,
)
@click.option(
    "-p",
    "--project",
    type=int,
    metavar="<int>",
    help="Search in the specified project, input project id [required at least one of --project and --group].",
)
@click.option(
    "-g",
    "--group",
    type=str,
    metavar="<string>",
    # pylint: disable=C0301
    help="Search in the specified project group, input group id or group path [required at least one of --project and --group].",
)
@click.option(
    "-e",
    "--environment",
    "session_env",
    type=str,
    metavar="<string>",
    default=lambda: gitlab_config.get_default_env().name
    if gitlab_config.get_default_env() is not None
    else "",
    callback=__validate_session_env_option,
    help="Select the environment for searching, if not declare, default environment has been used.",
)
@click.option(
    "-o",
    "--output",
    type=str,
    metavar="<file_path>",
    callback=__validate_output_option,
    help="Export the search result to markdown file with extension .md or .markdown.",
)
@click.option(
    "-d",
    "--debug",
    "debug",
    is_flag=True,
    show_default=True,
    default=False,
    help="Enable debug logging of HTTP request.",
)
@click.option(
    "--code-preview",
    "code_preview",
    is_flag=True,
    show_default=True,
    default=False,
    help="Show code preview.",
)
@click.option(
    "--ignore-no-result",
    "ignore_no_result",
    is_flag=True,
    show_default=True,
    default=False,
    help="Do not show the project which has no result (for searching group).",
)
def search(**kwargs):
    param = GitLabParam(
        keyword=kwargs.get("keyword"),
        env_name=kwargs.get("session_env"),
        output_path=kwargs.get("output"),
        project_id=kwargs.get("project"),
        group=kwargs.get("group"),
        is_debug=kwargs.get("debug"),
        code_preview=kwargs.get("code_preview"),
        ignore_no_result=kwargs.get("ignore_no_result"),
    )
    app_config.set_debug(param.is_debug)

    click.clear()
    if param.input_project:
        __search_in_project(param)
    else:
        __search_in_group(param)


@keep_main_thread_running
@inject
def __search_in_group(
    param: GitLabParam,
    usecase: GitLabSearchGroupUseCase = Provide[
        ApplicationContainer.gitlab_module.search_group_use_case
    ],
):
    param.is_search_group = True
    usecase.on_searching().subscribe(GitLabPrintObserver(param=param))
    usecase.search(param.input_group, param.keyword)


@keep_main_thread_running
@inject
def __search_in_project(
    param: GitLabParam,
    usecase: GitLabSearchProjectUseCase = Provide[
        ApplicationContainer.gitlab_module.search_proj_use_case
    ],
):
    usecase.on_searching().subscribe(GitLabPrintObserver(param=param))
    usecase.search(param.input_project, param.keyword)
