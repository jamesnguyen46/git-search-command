from gsc.presentation.command_line import cli
from gsc.di.application_container import ApplicationContainer


def main():
    app_container = ApplicationContainer()
    app_container.wire(packages=["gsc"])
    cli.app()


if __name__ == "__main__":
    main()
