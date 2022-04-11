import click
import gsc
from gsc.utils import is_valid_environment_name
from gsc.command_line import keep_main_thread_running
from gsc.command_line.observer.gitlab_observer import (
    GitLabParam,
    GitLabPrintProjectObserver,
    GitLabPrintGroupObserver,
)
from gsc.config import Env, EnvConfig, GitLabConfig
from gsc.use_cases.gitlab_search_use_case import (
    GitLabSearchProjectUseCase,
    GitLabSearchGroupUseCase,
)


@click.group("gl", help="Search in GitLab repositories.")
def gitlab_cli():
    pass


@gitlab_cli.command(
    "env", help="Setup the environment for searching, support multiple environments."
)
@click.option(
    "-n",
    "--new",
    type=str,
    metavar="<environment>",
    help="Create new or override the env information if it was existed.",
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
    help="Remove the environment.",
)
@click.option(
    "-i",
    "--info",
    type=str,
    metavar="<environment>",
    help="Display the environment info.",
)
@click.option(
    "-l",
    "--list",
    "show_list",
    is_flag=True,
    default=False,
    help="List all environment.",
)
@click.pass_context
def environment(ctx, **kwargs):
    config = GitLabConfig()
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
    help="Export the search result to file, support txt and markdown file.",
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
def search(ctx, **kwargs):
    config = GitLabConfig()
    config.set_session_env("")
    if not config.get_default_env():
        click.secho("There is no environment.")
        click.secho("Try `gsc gl env --new <environment_name>` before searching.")
        return

    if kwargs.get("keyword"):
        param = GitLabParam(
            keyword=kwargs.get("keyword"),
            output_path=kwargs.get("output"),
            project_id=kwargs.get("project"),
            group=kwargs.get("group"),
        )

        session_env = kwargs.get("session_env")
        if session_env:
            param.env_name = session_env
            config.set_session_env(session_env)
        else:
            default_env = config.get_default_env()
            param.env_name = default_env.name
            config.set_session_env(default_env.name)

        if kwargs.get("debug"):
            gsc.__ID_DEBUG__ = True

        click.clear()
        if param.input_project:
            __search_in_project(param)
        elif param.input_group:
            __search_in_group(param)
    else:
        click.secho(search.get_help(ctx))


@keep_main_thread_running
def __search_in_group(param: GitLabParam):
    usecase = GitLabSearchGroupUseCase()
    usecase.on_searching().subscribe(GitLabPrintGroupObserver(param=param))
    usecase.search(param.input_group, param.keyword)


@keep_main_thread_running
def __search_in_project(param: GitLabParam):
    usecase = GitLabSearchProjectUseCase()
    usecase.on_searching().subscribe(GitLabPrintProjectObserver(param=param))
    usecase.search(param.input_project, param.keyword)


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
