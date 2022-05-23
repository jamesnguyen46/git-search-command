import sys
import click
from gsc.command_line.gitlab_cli import gitlab_cli
from gsc.command_line.github_cli import github_cli

if sys.version_info[:2] >= (3, 8):
    from importlib import metadata
else:
    import importlib_metadata as metadata

CONTEXT_SETTINGS = dict(help_option_names=["-h", "--help"])


@click.group(
    invoke_without_command=True,
    context_settings=CONTEXT_SETTINGS,
    help="A simple tool to search the expression in the project scope for GitLab and GitHub repositories.",
)
@click.option(
    "-v",
    "--version",
    "show_version",
    is_flag=True,
    help="Show the current gsc version.",
)
@click.pass_context
def app(ctx=None, show_version: bool = False):
    if ctx.invoked_subcommand is not None:
        return

    if show_version:
        __version__ = metadata.version("git-search-command")
        click.secho(__version__)
    else:
        click.secho(app.get_help(ctx))


app.add_command(gitlab_cli)
app.add_command(github_cli)
