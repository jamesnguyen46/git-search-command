import click
from gsc.config import Env, EnvConfig
from gsc.utils import is_valid_environment_name


@click.command(
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
    help="List all environments.",
)
@click.pass_context
def environment(
    ctx,
    **kwargs,
):
    config = ctx.obj[0]
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
        click.secho("Environment name is invalid.", fg="bright_red")
        click.secho(
            "Environment name only contains letters, numbers, underscores, dashes...",
            fg="bright_red",
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
