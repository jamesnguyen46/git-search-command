from typing import Any
import click
from gsc.command_line import block_main_thread, release_main_thread
from gsc.data.response.project import Project
from gsc.data.response.search_result import SearchResult
from gsc.use_cases.gitlab_search_proj_use_case import GitLabSearchProjUseCase
from gsc.use_cases.gitlab_search_group_use_case import GitLabSearchGroupUseCase


@click.group("gl", help="GITLAB")
def gitlab_cli():
    pass


@gitlab_cli.command("config", help="")
def config():
    pass


@gitlab_cli.command("search", help="")
@click.argument("keyword", type=str)
@click.option("--group", "-g", type=str, help="Gitlab project group")
@click.option("--project_id", "-p", type=int, help="Gitlab project id")
def search(keyword: str, group: str, project_id: int):
    if keyword and group:
        __search_in_group(keyword, group)
    elif keyword and project_id:
        __search_in_project(keyword, project_id)
    else:
        pass


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


def __handle_complete():
    click.secho("*************************")
    click.secho("Done")
    release_main_thread()


def __handle_error(error: Exception):
    click.secho(f"[Error] {error}", fg="bright_red")
    release_main_thread()


if __name__ == "__main__":
    gitlab_cli()
