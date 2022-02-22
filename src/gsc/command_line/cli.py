import click
from gsc.command_line.gitlab_cli import gitlab_cli


@click.group()
def app():
    pass


app.add_command(gitlab_cli)


if __name__ == "__main__":
    app()
