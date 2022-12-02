import click
from dependency_injector.wiring import Provide, inject
from gsc import utils
from gsc.di.application_container import ApplicationContainer
from gsc.constants import GitHubConstant
from gsc.presentation.command_line.env_cli import environment
from gsc.presentation.command_line import keep_main_thread_running
from gsc.presentation.observer.github_observer import (
    GitHubParam,
    GitHubPrintObserver,
)
from gsc.config import AppConfig, GitHubConfig
from gsc.domain.use_cases.github_search_use_case import (
    GitHubSearchRepoUseCase,
    GitHubSearchMultiRepoUseCase,
)

app_config: AppConfig = Provide[ApplicationContainer.github_module.app_config]
github_config: GitHubConfig = Provide[ApplicationContainer.github_module.config]


@click.group("gh", help=f"Search in {GitHubConstant.NAME} repositories.")
@click.pass_context
def github_cli(ctx):
    ctx.obj = [github_config]


github_cli.add_command(environment)


def __validate_required_keyword_argument(ctx, _, value):
    if value is None:
        click.secho("Usage: gsc gh search [OPTIONS] <keyword>")
        click.secho("Try 'gsc gh search -h' for help.")
        click.secho("\n", nl=False)
        click.secho("Error: Missing required argument <keyword>")
        ctx.exit(2)
    return value


def __validate_session_env_option(ctx, _, value):
    if not value:
        click.secho("There is no environment.")
        click.secho("Try `gsc gh env --new <environment_name>` before searching.")
        ctx.exit(2)
    elif not github_config.is_env_existed(value):
        click.secho(f'"{value}" is not existed in your environment list.')
        click.secho("Try `gsc gh env --new <environment_name>` before searching.")
        ctx.exit(2)
    else:
        pass

    github_config.set_session_env(value)
    return value


def __validate_output_option(ctx, _, value):
    if value and not utils.is_supported_extension_output_file(value):
        click.secho("Usage: gsc gh search [OPTIONS] <keyword>")
        click.secho("Try 'gsc gh search -h' for help.")
        click.secho("\n", nl=False)
        click.secho("Error: Output file type is not supported.")
        ctx.exit(2)

    return value


# pylint: disable=C0301
@github_cli.command(
    "search",
    help=f"Search the content in all {GitHubConstant.NAME} repositories that you owned, not including fork repository.",
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
    "--repository",
    type=str,
    metavar="<string>",
    help='Search in the specified repository, input the full name of repository, example : "username/repository_name".',
)
@click.option(
    "-e",
    "--environment",
    "session_env",
    type=str,
    metavar="<string>",
    default=lambda: github_config.get_default_env().name
    if github_config.get_default_env() is not None
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
def search(**kwargs):
    param = GitHubParam(
        keyword=kwargs.get("keyword"),
        env_name=kwargs.get("session_env"),
        output_path=kwargs.get("output"),
        repo_name=kwargs.get("repository"),
        is_debug=kwargs.get("debug") or False,
    )
    app_config.set_debug(param.is_debug)

    click.clear()
    if param.repo_name:
        __search_in_single_repo(param)
    else:
        __search_in_multiple_repo(param)


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
