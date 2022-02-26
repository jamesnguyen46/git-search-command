import click
from gsc.command_line.gitlab_cli import gitlab_cli

CONTEXT_SETTINGS = dict(help_option_names=["-h", "--help"])


@click.group(context_settings=CONTEXT_SETTINGS)
def app():
    """
    A simple tool to search the expression in the project scope for GitLab and GitHub service.
    """


app.add_command(gitlab_cli)


if __name__ == "__main__":
    app()
