import click
from gsc import settings
from gsc.constants import GITLAB_KEY_LIST, GITLAB_HOST_NAME, GITLAB_PRIVATE_TOKEN
from gsc.command_line import keep_main_thread_running
from gsc.command_line.print_observer import (
    ConsoleGroupResultObserver,
    ConsoleProjectResultObserver,
)
from gsc.use_cases.gitlab_search_proj_use_case import GitLabSearchProjUseCase
from gsc.use_cases.gitlab_search_group_use_case import GitLabSearchGroupUseCase


@click.group("gl", help="Search in GitLab repositories.")
def gitlab_cli():
    pass


@gitlab_cli.command(
    "config", help="Display or change configuration variables for GitLab."
)
@click.option("-u", "--url", type=str, metavar="<string>", help="Set GitLab host name.")
@click.option(
    "-t", "--token", type=str, metavar="<string>", help="Set GitLab private token."
)
@click.option(
    "-a",
    "--all",
    "show_all",
    is_flag=True,
    help="Show all GitLab environment variables.",
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


@gitlab_cli.command("search", help="Search the content in GitLab repositories.")
@click.argument("keyword", type=str, metavar="<keyword>")
@click.option(
    "-g", "--group", type=str, metavar="<string>", help="Search in the specified group."
)
@click.option(
    "-p",
    "--project",
    type=int,
    metavar="<int>",
    help="Search in the specified project.",
)
@click.option(
    "-v",
    "show_preview",
    is_flag=True,
    default=False,
    help="Show result preview, available only when searching project, not in group.",
)
@click.option(
    "-o",
    "--output",
    type=str,
    metavar="<string>",
    help="Export the search result to file, only support text file.",
)
@click.pass_context
def search(
    ctx, keyword: str, group: str, project: int, output: str, show_preview: bool
):
    click.clear()

    if not __validate_environment_variables():
        click.secho("`GITLAB_HOST_NAME` or `GITLAB_PRIVATE_TOKEN` has no value.")
        click.secho("Try `gsc gl config [OPTIONS]` before searching.")
        return

    if keyword and group:
        __search_in_group(keyword, group, output)
    elif keyword and project:
        __search_in_project(keyword, project, show_preview, output)
    else:
        click.secho(search.get_help(ctx))


def __validate_environment_variables():
    if not settings.value(GITLAB_HOST_NAME) or not settings.value(GITLAB_PRIVATE_TOKEN):
        return False

    return True


@keep_main_thread_running
def __search_in_group(keyword: str, group_name: str, output_path: str):
    usecase = GitLabSearchGroupUseCase()
    usecase.on_searching().subscribe(
        ConsoleGroupResultObserver(
            group=group_name, keyword=keyword, output_path=output_path
        )
    )
    usecase.search(group_name, keyword)


@keep_main_thread_running
def __search_in_project(
    keyword: str, project_id: int, show_preview: bool, output_path: str
):
    usecase = GitLabSearchProjUseCase()
    usecase.on_searching().subscribe(
        ConsoleProjectResultObserver(
            id=project_id,
            keyword=keyword,
            preview=show_preview,
            output_path=output_path,
        )
    )
    usecase.search(project_id, keyword)
