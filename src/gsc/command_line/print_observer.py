import os.path
from typing import Any, Optional
import click
from rx.core import typing, Observer
from gsc.entities.gitlab_model import Project, FileName
from gsc.command_line import finish_main_thread


class PrintParam:
    def __init__(self, **kwargs) -> None:
        self.service_name = kwargs.get("service_name")
        self.env_name = kwargs.get("env_name")
        self.keyword = kwargs.get("keyword")
        self.output_path = kwargs.get("output_path")
        self.show_preview = kwargs.get("show_preview")
        self.input_project = kwargs.get("project_id")
        self.input_group = kwargs.get("group")


class PrintObserver(Observer):
    MARKDOWN_EXTENSION = (".md", ".markdown")

    def __init__(
        self,
        on_next: Optional[typing.OnNext] = None,
        on_error: Optional[typing.OnError] = None,
        on_completed: Optional[typing.OnCompleted] = None,
        param: PrintParam = None,
    ) -> None:
        super().__init__(on_next, on_error, on_completed)
        self.param = param
        self._is_markdown = False
        self._export_file = None
        if self.param.output_path:
            path = self.param.output_path
            self._is_markdown = os.path.splitext(path)[1] in self.MARKDOWN_EXTENSION
            self._export_file = click.open_file(path, mode="w") if path else None
        self._project = None
        self.on_print_start()

    def on_print_start(self) -> None:
        pass

    def on_print_project(self, project: Project) -> None:
        pass

    def on_print_file(self, file: FileName) -> None:
        pass

    def on_print_end(self) -> None:
        pass

    def on_print_error(self, error: Exception) -> None:
        pass

    def echo(self, msg, url=None, **styles):
        click.secho(msg, **styles)

        if self._export_file:
            message = f"[{msg}]({url})" if url and self._is_markdown else msg
            self._export_file.write(message + "\n")

    def on_next(self, value: Any) -> None:
        if isinstance(value, Project):
            # Save project object to print it later
            self._project = value
        elif isinstance(value, FileName):
            # Ensure that searching is not empty
            if self._project is not None:
                self.on_print_project(self._project)
                self._project = None
            self.on_print_file(value)
        else:
            pass

    def on_completed(self) -> None:
        self.on_print_end()
        if self._export_file:
            self._export_file.close()
            self._export_file = None

    def on_error(self, error: Exception) -> None:
        self.on_print_error(error)
        if self._export_file:
            self._export_file.close()
            self._export_file = None

    def dispose(self) -> None:
        self.param = None
        return super().dispose()


class ConsoleProjectResultObserver(PrintObserver):
    def __init__(
        self,
        on_next: Optional[typing.OnNext] = None,
        on_error: Optional[typing.OnError] = None,
        on_completed: Optional[typing.OnCompleted] = None,
        param: PrintParam = None,
    ) -> None:
        self._file_count = 0
        super().__init__(on_next, on_error, on_completed, param)

    def on_print_start(self) -> None:
        super().on_print_start()
        prefix_msg = f'[GitLab] ("{self.param.env_name}" env) '
        msg = f'Searching for "{self.param.keyword}" in project with id "{self.param.input_project}" ...'
        self.echo(prefix_msg + msg)

    def on_print_project(self, project: Project) -> None:
        super().on_print_project(project)
        self._file_count = 0
        self.echo("*************************")
        self.echo(
            f"[{project.id}] {project.name}",
            url=project.web_url,
            fg="bright_magenta",
        )

    def on_print_file(self, file: FileName) -> None:
        super().on_print_file(file)
        self._file_count += 1
        self.echo(f"{file.path}", url=file.web_url)
        if self.param.show_preview:
            self.echo(f"{file.data_preview}", dim=True)

    @finish_main_thread
    def on_print_end(self) -> None:
        super().on_print_end()
        if self._file_count == 0:
            self.echo(f'There is NO file containing "{self.param.keyword}".')
            return

        self.echo("*************************")
        self.echo(
            f'There are {self._file_count} file(s) containing "{self.param.keyword}".'
        )
        self._file_count = 0

    @finish_main_thread
    def on_print_error(self, error: Exception) -> None:
        super().on_print_error(error)
        self.echo(f"[Error] {error}", fg="bright_red")

    def dispose(self) -> None:
        self._file_count = 0
        return super().dispose()


class ConsoleGroupResultObserver(PrintObserver):
    def __init__(
        self,
        on_next: Optional[typing.OnNext] = None,
        on_error: Optional[typing.OnError] = None,
        on_completed: Optional[typing.OnCompleted] = None,
        param: PrintParam = None,
    ) -> None:
        self._project_count = 0
        super().__init__(on_next, on_error, on_completed, param)

    def on_print_start(self) -> None:
        super().on_print_start()
        prefix_msg = f'[GitLab] ("{self.param.env_name}" env) '
        msg = f'Searching for "{self.param.keyword}" in "{self.param.input_group}" group ...'
        self.echo(prefix_msg + msg)

    def on_print_project(self, project: Project) -> None:
        super().on_print_project(project)
        self._project_count += 1
        self.echo("*************************")
        self.echo(
            f"[{project.id}] {project.name}",
            url=project.web_url,
            fg="bright_magenta",
        )

    def on_print_file(self, file: FileName) -> None:
        super().on_print_file(file)
        self.echo(f"{file.path}", url=file.web_url)

    @finish_main_thread
    def on_print_end(self) -> None:
        super().on_print_end()
        if self._project_count == 0:
            self.echo(f'There is NO project containing "{self.param.keyword}".')
            return

        self.echo("*************************")
        self.echo(
            f'There are {self._project_count} project(s) containing "{self.param.keyword}".'
        )
        self._project_count = 0

    @finish_main_thread
    def on_print_error(self, error: Exception) -> None:
        super().on_print_error(error)
        self.echo(f"[Error] {error}", fg="bright_red")

    def dispose(self) -> None:
        self._project_count = 0
        return super().dispose()
