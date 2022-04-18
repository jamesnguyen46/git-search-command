from gsc.command_line import cli, gitlab_cli
from gsc.di.application_container import ApplicationContainer


def main():
    app_container = ApplicationContainer()
    app_container.wire(modules=[gitlab_cli])
    cli.app()


if __name__ == "__main__":
    main()
