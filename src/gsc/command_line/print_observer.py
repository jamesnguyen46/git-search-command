from typing import Any, Optional
import click
from rx.core import typing, Observer
from gsc.data.response.project import Project
from gsc.data.response.file_name import FileName
from gsc.command_line import finish_main_thread


class PrintObserver(Observer):
    def __init__(
        self,
        on_next: Optional[typing.OnNext] = None,
        on_error: Optional[typing.OnError] = None,
        on_completed: Optional[typing.OnCompleted] = None,
        **kwargs,
    ) -> None:
        super().__init__(on_next, on_error, on_completed)
        self._keyword = kwargs.get("keyword")
        self._output_path = kwargs.get("output_path")
        self._export_file = (
            click.open_file(self._output_path, "w") if self._output_path else None
        )
        self._project = None
        self._on_print_start()

    def _on_print_start(self) -> None:
        pass

    def _on_print_project(self, project: Project) -> None:
        pass

    def _on_print_file(self, file: FileName) -> None:
        pass

    def _on_print_end(self) -> None:
        pass

    def _on_print_error(self, error: Exception) -> None:
        pass

    def _echo(self, msg, **styles):
        click.secho(msg, **styles)
        if self._export_file:
            self._export_file.write(msg + "\n")

    def on_next(self, value: Any) -> None:
        if isinstance(value, Project):
            # Save project object to print it later
            self._project = value
        elif isinstance(value, FileName):
            # Ensure that searching is not empty
            if self._project is not None:
                self._on_print_project(self._project)
                self._project = None
            self._on_print_file(value)
        else:
            pass

    def on_completed(self) -> None:
        self._on_print_end()
        if self._export_file:
            self._export_file.close()
            self._export_file = None

    def on_error(self, error: Exception) -> None:
        self._on_print_error(error)
        if self._export_file:
            self._export_file.close()
            self._export_file = None

    def dispose(self) -> None:
        self._keyword = None
        return super().dispose()


class ConsoleProjectResultObserver(PrintObserver):
    def __init__(
        self,
        on_next: Optional[typing.OnNext] = None,
        on_error: Optional[typing.OnError] = None,
        on_completed: Optional[typing.OnCompleted] = None,
        **kwargs,
    ) -> None:
        self._project_id = kwargs.get("id")
        self._show_code_preview = kwargs.get("preview")
        self._file_count = 0
        super().__init__(on_next, on_error, on_completed, **kwargs)

    def _on_print_start(self) -> None:
        self._echo(
            f'Searching for "{self._keyword}" in project with id "{self._project_id}" ...'
        )

    def _on_print_project(self, project: Project) -> None:
        self._file_count = 0
        self._echo("*************************")
        self._echo(f"[{project.id}] {project.name}", fg="bright_magenta")

    def _on_print_file(self, file: FileName) -> None:
        self._file_count += 1
        self._echo(f"{file.path}")
        if self._show_code_preview:
            self._echo(f"{file.data_preview}", dim=True)

    @finish_main_thread
    def _on_print_end(self) -> None:
        if self._file_count == 0:
            self._echo(f'There is NO file containing "{self._keyword}".')
            return

        self._echo("*************************")
        self._echo(
            f'There are {self._file_count} file(s) containing "{self._keyword}".'
        )
        self._file_count = 0

    @finish_main_thread
    def _on_print_error(self, error: Exception) -> None:
        self._echo(f"[Error] {error}", fg="bright_red")

    def dispose(self) -> None:
        self._file_count = 0
        return super().dispose()


class ConsoleGroupResultObserver(ConsoleProjectResultObserver):
    def __init__(
        self,
        on_next: Optional[typing.OnNext] = None,
        on_error: Optional[typing.OnError] = None,
        on_completed: Optional[typing.OnCompleted] = None,
        **kwargs,
    ) -> None:
        self._group_name = kwargs.get("group")
        self._project_count = 0
        super().__init__(on_next, on_error, on_completed, **kwargs)

    def _on_print_start(self) -> None:
        self._echo(f'Searching for "{self._keyword}" in "{self._group_name}" group ...')

    def _on_print_project(self, project: Project) -> None:
        self._project_count += 1
        return super().on_print_project(project)

    @finish_main_thread
    def _on_print_end(self) -> None:
        if self._project_count == 0:
            self._echo(f'There is NO project containing "{self._keyword}".')
            return

        self._echo("*************************")
        self._echo(
            f'There are {self._project_count} project(s) containing "{self._keyword}".'
        )
        self._project_count = 0

    def dispose(self) -> None:
        self._project_count = 0
        return super().dispose()
