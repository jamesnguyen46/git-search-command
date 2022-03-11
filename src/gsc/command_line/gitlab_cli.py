import click
from gsc.utils import is_valid_environment_name
from gsc.command_line import keep_main_thread_running
from gsc.command_line.print_observer import (
    ConsoleGroupResultObserver,
    ConsoleProjectResultObserver,
)
from gsc.config import Env, EnvConfig, GitlabConfig
from gsc.use_cases.gitlab_search_proj_use_case import GitLabSearchProjUseCase
from gsc.use_cases.gitlab_search_group_use_case import GitLabSearchGroupUseCase


@click.group("gl", help="Search in GitLab repositories.")
def gitlab_cli():
    pass


@gitlab_cli.command(
    "env", help="Configure the environment variable, support multiple environments."
)
@click.option(
    "-n",
    "--new",
    type=str,
    metavar="<environment>",
    help="Create new or update its information if it was created.",
)
@click.option(
    "-d",
    "--default",
    type=str,
    metavar="<environment>",
    help="Set the environment as default.",
)
@click.option(
    "-r",
    "--remove",
    type=str,
    metavar="<environment>",
    help="Remove a environments.",
)
@click.option(
    "-i",
    "--info",
    type=str,
    metavar="<environment>",
    help="Show the detail of a environment.",
)
@click.option(
    "-l",
    "--list",
    "show_list",
    is_flag=True,
    default=False,
    help="List the environment.",
)
@click.pass_context
def environment(ctx, **kwargs):
    config = GitlabConfig()
    if kwargs.get("show_list"):
        __show_list_envs(config)
    elif kwargs.get("new"):
        __create_new_environment(config, kwargs.get("new"))
    elif kwargs.get("default"):
        __set_default_environment(config, kwargs.get("default"))
    elif kwargs.get("remove"):
        __remove_environment(config, kwargs.get("remove"))
    elif kwargs.get("info"):
        __show_detail_environment(config, kwargs.get("info"))
    else:
        click.secho(environment.get_help(ctx))


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
    "-e",
    "--environment",
    "env",
    type=str,
    metavar="<string>",
    help="Select the environment to search.",
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
def search(ctx, **kwargs):
    config = GitlabConfig()
    config.set_session_env("")
    if not config.get_default_env():
        click.secho("There is no environment.")
        click.secho("Try `gsc gl env --new <environment_name>` before searching.")
        return

    if kwargs.get("keyword"):
        keyword = kwargs.get("keyword")
        env = kwargs.get("env")
        output = kwargs.get("output")
        if env:
            config.set_session_env(env)

        click.clear()
        if kwargs.get("project"):
            project = kwargs.get("project")
            show_preview = kwargs.get("show_preview")
            __search_in_project(keyword, project, show_preview, output)
        elif kwargs.get("group"):
            group = kwargs.get("group")
            __search_in_group(keyword, group, output)
    else:
        click.secho(search.get_help(ctx))


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


def __show_list_envs(config: EnvConfig):
    envs = config.get_all_envs()
    if not envs:
        click.secho("There is no environment.")
        return

    for env in envs:
        name = env.name
        if config.is_default_env(name):
            click.secho(f"* {name}")
        else:
            click.secho(f"  {name}")


def __create_new_environment(config: EnvConfig, name: str):
    if not is_valid_environment_name(name):
        click.secho(
            "Environment name only contains letters, numbers, underscores, dashes..., not space"
        )
        return

    new_env = Env(name=name)

    host = click.prompt(f'Please input host name for "{name}" environment ', type=str)
    if host:
        new_env.host_name = host

    token = click.prompt(f'Please input token for "{name}" environment ', type=str)
    if token:
        new_env.private_token = token

    config.set_env(new_env)


def __remove_environment(config: EnvConfig, env_name: str):
    config.remove_env(env_name)


def __show_detail_environment(config: EnvConfig, name: str):
    if not config.is_env_existed(name):
        click.secho(f'"{name}" environment is not found.')
        return

    environ = config.get_env(name)
    click.secho(f'"{name}" environment :')
    click.secho(f"Host name : {environ.host_name}")
    click.secho(f"Private token : {environ.private_token}")


def __set_default_environment(config: EnvConfig, env_name: str):
    config.set_default_env(env_name)
