import os.path
import click
from dependency_injector.wiring import Provide, inject
from gsc.di.application_container import ApplicationContainer
from gsc.constants import GitHubConstant
from gsc.command_line.env_cli import environment
from gsc.command_line import keep_main_thread_running
from gsc.observer.github_observer import (
    GitHubParam,
    GitHubPrintObserver,
)
from gsc.config import AppConfig, GitHubConfig
from gsc.observer.plugin import ExportPlugin
from gsc.use_cases.github_search_use_case import (
    GitHubSearchRepoUseCase,
    GitHubSearchMultiRepoUseCase,
)


@click.group("gh", help=f"Search in {GitHubConstant.NAME} repositories.")
@click.pass_context
@inject
def github_cli(
    ctx, config: GitHubConfig = Provide[ApplicationContainer.github_module.config]
):
    ctx.obj = config


github_cli.add_command(environment)


@github_cli.command(
    "search",
    help=f"Search the content in all {GitHubConstant.NAME} repositories that you owned.",
)
@click.argument("keyword", type=str, metavar="<keyword>")
@click.option(
    "-p",
    "--repository",
    type=str,
    metavar="<string>",
    help='Search in the specified repository, input the full name of repository, example : "username/repository_name"',
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
    github_config: GitHubConfig = Provide[ApplicationContainer.github_module.config],
    **kwargs,
):
    github_config.set_session_env("")
    if not github_config.get_default_env():
        click.secho("There is no environment.")
        click.secho("Try `gsc gl env --new <environment_name>` before searching.")
        return

    if kwargs.get("keyword"):
        output_path = kwargs.get("output")
        if output_path and not __is_validate_output_path(output_path):
            click.secho("Error: Output file type is not supported.")
            click.secho("Try 'gsc gl search -h' for help.")
            return

        param = GitHubParam(
            keyword=kwargs.get("keyword"),
            output_path=output_path,
            repo_name=kwargs.get("repository"),
            is_debug=kwargs.get("debug") or False,
        )
        app_config.set_debug(param.is_debug)

        session_env = kwargs.get("session_env")
        if session_env:
            param.env_name = session_env
            github_config.set_session_env(session_env)
        else:
            default_env = github_config.get_default_env()
            param.env_name = default_env.name
            github_config.set_session_env(default_env.name)

        click.clear()
        if param.repo_name:
            __search_in_single_repo(param)
        else:
            __search_in_multiple_repo(param)
    else:
        click.secho(search.get_help(ctx))


def __is_validate_output_path(path: str):
    return os.path.splitext(path)[1] in ExportPlugin.EXTENSION_SUPPORTED


@keep_main_thread_running
@inject
def __search_in_multiple_repo(
    param: GitHubParam,
    usecase: GitHubSearchMultiRepoUseCase = Provide[
        ApplicationContainer.github_module.search_multi_repo_use_case
    ],
):
    usecase.on_searching().subscribe(GitHubPrintObserver(param=param))
    usecase.search(param.keyword)


@keep_main_thread_running
@inject
def __search_in_single_repo(
    param: GitHubParam,
    usecase: GitHubSearchRepoUseCase = Provide[
        ApplicationContainer.github_module.search_repo_use_case
    ],
):
    usecase.on_searching().subscribe(GitHubPrintObserver(param=param))
    usecase.search(param.repo_name, param.keyword)
