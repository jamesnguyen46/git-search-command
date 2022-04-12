import os.path
from typing import Any, Optional
import click
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
        self.is_search_group = kwargs.get("is_search_group") or False


class GitLabExportObserver(BasePrintObserver):
    MARKDOWN_EXTENSION = (".md", ".markdown")

    def __init__(
        self,
        on_next: Optional[typing.OnNext] = None,
        on_error: Optional[typing.OnError] = None,
        on_completed: Optional[typing.OnCompleted] = None,
        param: GitLabParam = None,
    ) -> None:
        self._export_file = None
        self.repo_count = 0
        path = param.output_path
        if os.path.splitext(path)[1] not in self.MARKDOWN_EXTENSION:
            raise NotImplementedError("Only support markdown file.")
        if param.output_path:
            self._is_markdown = os.path.splitext(path)[1] in self.MARKDOWN_EXTENSION
            self._export_file = click.open_file(path, mode="w") if path else None
        super().__init__(on_next, on_error, on_completed, param)

    def on_print_start(self) -> None:
        self.write(
            f'# [GitLab] ("{self.param.env_name}" env) Searching for "{self.param.keyword}" ...'
        )

    def on_print_result(self, value: Any) -> None:
        project: Project = value[0]
        files: File = value[1]
        self.write_lines()
        if files:
            # Print project
            self.repo_count += 1
            proj_msg = f"## [[{project.id}] {project.name} - {len(files)} file(s)]({project.url})"
            if project.archived:
                proj_msg = f"## [[{project.id}] (❗Archived) {project.name} - {len(files)} file(s)]({project.url})"
            self.write(proj_msg)
            self.write_lines()
            # Print files
            for file in files:
                self.write(f"- [{file.path}]({file.url})")
        else:
            # Print project
            self.write(f"## [[{project.id}] {project.name}]({project.url})")
            self.write_lines()
            # Print files
            self.write("No results found")

    def on_print_error(self, error: Exception) -> None:
        self.write_lines()
        self.write(f"[Error] {error}")

    def on_print_end(self) -> None:
        if self.param.is_search_group:
            self.write("---")
            count_msg = self.repo_count if self.repo_count != 0 else "NO"
            msg = f'There are {count_msg} repository(s) containing "{self.param.keyword}".'
            self.write(msg)
        self.repo_count = 0

    def write(self, message):
        if self._export_file:
            self._export_file.write(message + "\n")

    def write_lines(self):
        self._export_file.write("\n")


class GitLabPrintObserver(BasePrintObserver):
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
        self.print(
            f'[GitLab] ("{self.param.env_name}" env) Searching for "{self.param.keyword}" ...'
        )

    def on_print_result(self, value: Any) -> None:
        project: Project = value[0]
        files: File = value[1]
        self.print("------------------------")
        if files:
            # Print project
            self.repo_count += 1
            proj_msg = f"[{project.id}] {project.name} - {len(files)} file(s)"
            if project.archived:
                proj_msg = (
                    f"[{project.id}] (❗Archived) {project.name} - {len(files)} file(s)"
                )
            self.print(
                proj_msg,
                fg="bright_magenta",
            )
            # Print files
            for file in files:
                self.print(f"{file.path}")
        else:
            # Print project
            self.print(
                f"[{project.id}] {project.name}",
                fg="bright_magenta",
                dim=True,
            )
            # Print files
            self.print("No results found", dim=True)

    @finish_main_thread
    def on_print_end(self) -> None:
        self.print("------------------------")
        if self.param.is_search_group:
            count_msg = self.repo_count if self.repo_count != 0 else "NO"
            msg = f'There are {count_msg} repository(s) containing "{self.param.keyword}".'
            self.print(msg)
        self.repo_count = 0

    @finish_main_thread
    def on_print_error(self, error: Exception) -> None:
        self.print(f"[Error] {error}", fg="bright_red")

    def print(self, msg, **styles):
        if self.param.is_debug:
            return
        
        click.secho(msg, **styles)
