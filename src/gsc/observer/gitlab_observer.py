from typing import Any
from gsc.entities.gitlab_model import Project, File
from gsc.observer.base_observer import BasePrintObserver, PrintParam
from gsc.command_line import finish_main_thread


class GitLabParam(PrintParam):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.show_preview = kwargs.get("show_preview")
        self.input_project = kwargs.get("project_id")
        self.input_group = kwargs.get("group")
        self.is_search_group = kwargs.get("is_search_group") or False


class GitLabPrintObserver(BasePrintObserver):
    def __init__(self, param: GitLabParam = None) -> None:
        self.repo_count = 0
        super().__init__(param)

    def on_print_start(self) -> None:
        msg = f'[GitLab] ("{self.param.env_name}" env) Searching for "{self.param.keyword}" ...'
        self.print(msg)
        self.write(f"# {msg}")

    def on_print_result(self, value: Any) -> None:
        project: Project = value[0]
        files: File = value[1]
        self.print("------------------------")
        self.write_lines()
        if files:
            # Print project
            self.repo_count += 1
            project_msg = f"[{project.id}] {project.name} - {len(files)} file(s)"
            if project.archived:
                project_msg = (
                    f"[{project.id}] (❗Archived) {project.name} - {len(files)} file(s)"
                )
            self.print(project_msg, fg="bright_magenta")
            self.write(f"## [{project_msg}]({project.url})")
            self.write_lines()
            # Print files
            for file in files:
                self.print(f"{file.path}")
                self.write(f"- [{file.path}]({file.url})")
        else:
            # Print project
            project_msg = f"[{project.id}] {project.name}"
            self.print(project_msg, fg="bright_magenta", dim=True)
            self.write(f"## [{project_msg}]({project.url})")
            self.write_lines()
            # Print files
            self.print("No results found", dim=True)
            self.write("No results found")

    @finish_main_thread
    def on_print_end(self, elapsed_time) -> None:
        self.print("------------------------")
        if self.param.is_search_group:
            self.write("---")
            count_msg = self.repo_count if self.repo_count != 0 else "NO"
            msg = f'[{elapsed_time}] There are {count_msg} repository(s) containing "{self.param.keyword}".'
            self.print(msg)
            self.write(msg)
        self.repo_count = 0

    @finish_main_thread
    def on_print_error(self, error: Exception) -> None:
        self.print(f"[Error] {error}", fg="bright_red")
        self.write_lines()
        self.write(f"[Error] {error}")
