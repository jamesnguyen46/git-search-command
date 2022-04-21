import os.path
import click
from dependency_injector.wiring import Provide, inject
from gsc.di.application_container import ApplicationContainer
from gsc.constants import GitLabConstant
from gsc.command_line.env_cli import environment
from gsc.command_line import keep_main_thread_running
from gsc.observer.gitlab_observer import (
    GitLabParam,
    GitLabPrintObserver,
)
from gsc.config import AppConfig, GitLabConfig
from gsc.observer.plugin import ExportPlugin
from gsc.use_cases.gitlab_search_use_case import (
    GitLabSearchGroupUseCase,
    GitLabSearchProjectUseCase,
)


@click.group("gl", help=f"Search in {GitLabConstant.NAME} repositories.")
@click.pass_context
@inject
def gitlab_cli(
    ctx, config: GitLabConfig = Provide[ApplicationContainer.gitlab_module.config]
):
    ctx.obj = config


gitlab_cli.add_command(environment)


@gitlab_cli.command(
    "search", help=f"Search the content in {GitLabConstant.NAME} repositories."
)
@click.argument("keyword", type=str, metavar="<keyword>")
@click.option(
    "-g",
    "--group",
    type=str,
    metavar="<string>",
    help="Search in the specified project group, input group id or group path.",
)
@click.option(
    "-p",
    "--project",
    type=int,
    metavar="<int>",
    help="Search in the specified project, input project id.",
)
@click.option(
    "-e",
    "--environment",
    "session_env",
    type=str,
    metavar="<string>",
    help="Select the environment for searching, if not declare, default environment has been used.",
)
@click.option(
    "-o",
    "--output",
    type=str,
    metavar="<file_path>",
    help="Export the search result to markdown file with extension .md or .markdown.",
)
@click.option(
    "-d",
    "--debug",
    "debug",
    is_flag=True,
    default=False,
    help="Enable debug logging of HTTP request.",
)
@click.pass_context
@inject
def search(
    ctx,
    app_config: AppConfig = Provide[ApplicationContainer.gitlab_module.app_config],
    gitlab_config: AppConfig = Provide[ApplicationContainer.gitlab_module.config],
    **kwargs,
):
    gitlab_config.set_session_env("")
    if not gitlab_config.get_default_env():
        click.secho("There is no environment.")
        click.secho("Try `gsc gl env --new <environment_name>` before searching.")
        return

    if kwargs.get("keyword"):
        output_path = kwargs.get("output")
        if output_path and not __is_validate_output_path(output_path):
            click.secho("Error: Output file type is not supported.")
            click.secho("Try 'gsc gl search -h' for help.")
            return

        param = GitLabParam(
            keyword=kwargs.get("keyword"),
            output_path=output_path,
            project_id=kwargs.get("project"),
            group=kwargs.get("group"),
            is_debug=kwargs.get("debug") or False,
        )
        app_config.set_debug(param.is_debug)

        session_env = kwargs.get("session_env")
        if session_env:
            param.env_name = session_env
            gitlab_config.set_session_env(session_env)
        else:
            default_env = gitlab_config.get_default_env()
            param.env_name = default_env.name
            gitlab_config.set_session_env(default_env.name)

        click.clear()
        if param.input_project:
            __search_in_project(param)
        elif param.input_group:
            __search_in_group(param)
    else:
        click.secho(search.get_help(ctx))


def __is_validate_output_path(path: str):
    return os.path.splitext(path)[1] in ExportPlugin.EXTENSION_SUPPORTED


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
