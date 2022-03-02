from typing import Any, Optional
import click
from rx.core import typing, Observer
from gsc.data.response.project import Project
from gsc.data.response.file_name import FileName
from gsc.command_line import finish_main_thread


class PrintProjectResultObserver(Observer):
    def __init__(
        self,
        on_next: Optional[typing.OnNext] = None,
        on_error: Optional[typing.OnError] = None,
        on_completed: Optional[typing.OnCompleted] = None,
        keyword: str = None,
        show_code_preview: bool = True,
    ) -> None:
        super().__init__(on_next, on_error, on_completed)
        self._keyword = keyword
        self._show_code_preview = show_code_preview
        self._project = None
        self._file_count = 0

    def on_next(self, value: Any) -> None:
        if isinstance(value, Project):
            self._project = value
        elif isinstance(value, FileName):
            # Just print project if there is any file.
            if self._project:
                self._print_project(self._project)
                self._project = None
            self._print_file(value)
        else:
            pass

    @finish_main_thread
    def on_completed(self) -> None:
        if self._file_count == 0:
            click.secho(f'There is NO file containing "{self._keyword}".')
            return

        click.secho("*************************")
        click.secho(
            f'There are {self._file_count} file(s) containing "{self._keyword}".'
        )
        self._file_count = 0

    @finish_main_thread
    def on_error(self, error: Exception) -> None:
        click.secho(f"[Error] {error}", fg="bright_red")

    def _print_project(self, project: Project):
        self._file_count = 0
        click.secho("*************************")
        click.secho(f"[{project.id}] {project.name}", fg="bright_magenta")

    def _print_file(self, file: FileName):
        self._file_count += 1
        click.secho(f"{file.path}")
        if self._show_code_preview:
            click.secho(f"{file.data_preview}", dim=True)

    def dispose(self) -> None:
        self._keyword = None
        self._file_count = 0
        return super().dispose()


class PrintGroupResultObserver(PrintProjectResultObserver):
    def __init__(
        self,
        on_next: Optional[typing.OnNext] = None,
        on_error: Optional[typing.OnError] = None,
        on_completed: Optional[typing.OnCompleted] = None,
        keyword: str = None,
    ) -> None:
        super().__init__(on_next, on_error, on_completed, keyword, False)
        self._project_count = 0

    @finish_main_thread
    def on_completed(self) -> None:
        if self._project_count == 0:
            click.secho(f'There is NO project containing "{self._keyword}".')
            return

        click.secho("*************************")
        click.secho(
            f'There are {self._project_count} project(s) containing "{self._keyword}".'
        )
        self._project_count = 0

    def _print_project(self, project: Project):
        self._project_count += 1
        return super()._print_project(project)

    def dispose(self) -> None:
        self._project_count = 0
        return super().dispose()
