from typing import Any
import click
from gsc import settings
from gsc.constants import GITLAB_KEY_LIST, GITLAB_HOST_NAME, GITLAB_PRIVATE_TOKEN
from gsc.command_line import block_main_thread, release_main_thread
from gsc.data.response.project import Project
from gsc.data.response.search_result import SearchResult
from gsc.use_cases.gitlab_search_proj_use_case import GitLabSearchProjUseCase
from gsc.use_cases.gitlab_search_group_use_case import GitLabSearchGroupUseCase


@click.group("gl", help="Search in GitLab repositories")
def gitlab_cli():
    pass


@gitlab_cli.command(
    "config", help="Display or change configuration variables for GitLab"
)
@click.option("-u", "--url", type=str, metavar="<string>", help="Set GitLab host name")
@click.option(
    "-t", "--token", type=str, metavar="<string>", help="Set GitLab private token"
)
@click.option(
    "-a",
    "--all",
    "show_all",
    is_flag=True,
    help="Show all GitLab environment variables",
)
@click.pass_context
def gitlab_config(ctx, url: str, token: str, show_all: bool):
    if url:
        settings.set(GITLAB_HOST_NAME, url)
    elif token:
        settings.set(GITLAB_PRIVATE_TOKEN, token)
    elif show_all:
        for idx, val in enumerate(settings.values(GITLAB_KEY_LIST)):
            click.secho(f"{GITLAB_KEY_LIST[idx]}={val}")
    else:
        click.secho(gitlab_config.get_help(ctx))


@gitlab_cli.command("search", help="Search the content in GitLab repositories")
@click.argument("keyword", type=str, metavar="<keyword>")
@click.option(
    "-g", "--group", type=str, metavar="<string>", help="Search in the specified group"
)
@click.option(
    "-p",
    "--project",
    type=int,
    metavar="<int>",
    help="Search in the specified project",
)
@click.pass_context
def search(ctx, keyword: str, group: str, project: int):
    if not __validate_environment_variables():
        click.secho("`GITLAB_HOST_NAME` or `GITLAB_PRIVATE_TOKEN` has no value.")
        click.secho("Try `gsc gl config [OPTIONS]` before searching.")
        return

    if keyword and group:
        __search_in_group(keyword, group)
    elif keyword and project:
        __search_in_project(keyword, project)
    else:
        click.secho(search.get_help(ctx))


def __validate_environment_variables():
    if not settings.value(GITLAB_HOST_NAME) or not settings.value(GITLAB_PRIVATE_TOKEN):
        return False

    return True


@block_main_thread
def __search_in_group(keyword: str, group_name: str):
    usecase = GitLabSearchGroupUseCase()
    usecase.on_searching().subscribe(
        on_next=__handle_success,
        on_completed=__handle_complete,
        on_error=__handle_error,
    )
    usecase.search(group_name, keyword)


@block_main_thread
def __search_in_project(keyword: str, project_id: int):
    usecase = GitLabSearchProjUseCase()
    usecase.on_searching().subscribe(
        on_next=__handle_success,
        on_completed=__handle_complete,
        on_error=__handle_error,
    )
    usecase.search(project_id, keyword)


def __handle_success(item: Any):
    if isinstance(item, Project):
        click.secho("*************************")
        click.secho(f"[{item.id}] {item.name}", fg="bright_magenta")
    elif isinstance(item, SearchResult):
        str_line = ", ".join(map(str, item.start_lines))
        click.secho(f"{item.path} (line {str_line})")
    else:
        pass


@release_main_thread
def __handle_complete():
    click.secho("*************************")
    click.secho("Done")


@release_main_thread
def __handle_error(error: Exception):
    click.secho(f"[Error] {error}", fg="bright_red")
