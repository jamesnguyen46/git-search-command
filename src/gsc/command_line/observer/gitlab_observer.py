from typing import Any, Optional
from rx.core import typing
from gsc.entities.gitlab_model import Project, File
from gsc.command_line.observer.base_observer import BasePrintObserver, PrintParam
from gsc.command_line import finish_main_thread


class GitLabParam(PrintParam):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.show_preview = kwargs.get("show_preview")
        self.input_project = kwargs.get("project_id")
        self.input_group = kwargs.get("group")


class GitLabPrintProjectObserver(BasePrintObserver):
    def __init__(
        self,
        on_next: Optional[typing.OnNext] = None,
        on_error: Optional[typing.OnError] = None,
        on_completed: Optional[typing.OnCompleted] = None,
        param: GitLabParam = None,
    ) -> None:
        self.file_count = 0
        super().__init__(on_next, on_error, on_completed, param)

    def on_print_start(self) -> None:
        msg = f'[GitLab] ("{self.param.env_name}" env) Searching for "{self.param.keyword}" ...'
        self.echo(msg)

    def on_print_result(self, value: Any) -> None:
        # Print project
        project: Project = value[0]
        self.echo("------------------------")
        self.echo(
            f"[{project.id}] {project.name}",
            url=project.url,
            fg="bright_magenta",
        )

        # Print files
        files: File = value[1]
        if files:
            self.file_count = len(files)
            for file in files:
                self.echo(f"{file.path}", url=file.url)

    @finish_main_thread
    def on_print_end(self) -> None:
        if self.file_count == 0:
            self.echo("------------------------")
            self.echo(f'There is NO file containing "{self.param.keyword}".')
            return

        self.echo("------------------------")
        self.echo(
            f'There are {self.file_count} file(s) containing "{self.param.keyword}".'
        )
        self.file_count = 0

    @finish_main_thread
    def on_print_error(self, error: Exception) -> None:
        self.echo(f"[Error] {error}", fg="bright_red")


class GitLabPrintGroupObserver(BasePrintObserver):
    def __init__(
        self,
        on_next: Optional[typing.OnNext] = None,
        on_error: Optional[typing.OnError] = None,
        on_completed: Optional[typing.OnCompleted] = None,
        param: GitLabParam = None,
    ) -> None:
        self.repo_count = 0
        super().__init__(on_next, on_error, on_completed, param)

    def on_print_start(self) -> None:
        msg = f'[GitLab] ("{self.param.env_name}" env) Searching for "{self.param.keyword}" ...'
        self.echo(msg)

    def on_print_result(self, value: Any) -> None:
        project: Project = value[0]
        files: File = value[1]
        if files:
            self.echo("------------------------")
            self.echo(
                f"[{project.id}] {project.name} ({len(files)}) file(s)",
                url=project.url,
                fg="bright_magenta",
            )
            for file in files:
                self.repo_count += 1
                self.echo(f"{file.path}", url=file.url)
        else:
            self.echo("------------------------")
            self.echo(
                f"[{project.id}] {project.name}",
                url=project.url,
                fg="bright_magenta",
                dim=True,
                strikethrough=True,
            )

    @finish_main_thread
    def on_print_end(self) -> None:
        if self.repo_count == 0:
            self.echo(f'There is NO repository containing "{self.param.keyword}".')
            return

        self.echo("------------------------")
        self.echo(
            f'There are {self.repo_count} repository(s) containing "{self.param.keyword}".'
        )
        self.repo_count = 0

    @finish_main_thread
    def on_print_error(self, error: Exception) -> None:
        self.echo(f"[Error] {error}", fg="bright_red")
