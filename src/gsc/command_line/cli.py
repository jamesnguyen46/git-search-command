import os
import click
import toml
from tabulate import tabulate
from gsc import utils
from gsc.command_line.gitlab_cli import gitlab_cli
from gsc.command_line.github_cli import github_cli

CONTEXT_SETTINGS = dict(help_option_names=["-h", "--help"])

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))


# pylint: disable=W0613
def print_app_info(ctx, param, value):
    if not value:
        return False

    info = toml.load(utils.get_pyproject_path())["tool"]["poetry"]
    table = [
        ["Name", "GSC - Git Search Command"],
        ["Description", info["description"]],
        ["Author", info["authors"][0]],
        ["Source", info["repository"]],
        ["Version", utils.get_app_version()],
        ["License", info["license"]],
    ]
    click.echo(tabulate(table, tablefmt="fancy_grid"))
    return True


@click.group(
    invoke_without_command=True,
    context_settings=CONTEXT_SETTINGS,
    help="A simple tool to search the expression in the project scope for GitLab and GitHub repositories.",
)
@click.option(
    "-i",
    "--info",
    "information",
    is_flag=True,
    default=False,
    callback=print_app_info,
    help="Show the information of gsc.",
)
@click.pass_context
def app(ctx: click.Context = None, information=False):
    if ctx.invoked_subcommand is not None:
        return

    if not information:
        click.secho(app.get_help(ctx))


app.add_command(gitlab_cli)
app.add_command(github_cli)
