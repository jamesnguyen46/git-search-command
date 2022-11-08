import click
from tabulate import tabulate
from gsc import utils
from gsc.presentation.command_line.gitlab_cli import gitlab_cli
from gsc.presentation.command_line.github_cli import github_cli

CONTEXT_SETTINGS = dict(help_option_names=["-h", "--help"])


# pylint: disable=W0613
def print_app_info(ctx, param, value):
    if not value:
        return False

    table = [
        ["Name", f"GSC - {utils.get_project_name().title().replace('-', ' ')}"],
        ["Description", utils.get_project_summary()],
        [
            "Author",
            f"{utils.get_project_author()} <{utils.get_project_author_email()}>",
        ],
        ["Source", utils.get_project_home_page()],
        ["Version", utils.get_project_version()],
        ["License", utils.get_project_license()],
    ]
    click.echo(tabulate(table, tablefmt="fancy_grid"))
    return True


@click.group(
    invoke_without_command=True,
    context_settings=CONTEXT_SETTINGS,
    help="A simple tool to search the content in the project scope for GitLab and GitHub repositories.",
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
