from typing import Any
from gsc.domain.entities.github_model import Repository
from gsc.presentation.observer.base_observer import PrintObserver, PrintParam
from gsc.presentation.command_line import finish_main_thread
from gsc.constants import GitHubConstant


class GitHubParam(PrintParam):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.repo_name = kwargs.get("repo_name")


class GitHubPrintObserver(PrintObserver):
    def __init__(self, param: GitHubParam = None) -> None:
        self.repo_count = 0
        super().__init__(param)

    def on_print_start(self) -> None:
        msg = f'[{GitHubConstant.NAME}] ("{self.param.env_name}" env) Searching for "{self.param.keyword}" ...'
        self.print_title(msg)

    def on_print_result(self, value: Any) -> None:
        repo: Repository = value[0]
        files: list = value[1]
        self.print_separate_line()
        if files:
            # REPOSITORY
            self.repo_count += 1
            repo_msg = f"[{repo.id}] {repo.name} - {len(files)} file(s)"
            if repo.archived:
                repo_msg = f"[{repo.id}] (❗Archived) {repo.name} - {len(files)} file(s)"
            self.print_heading1(repo_msg)
            # FILES
            for file in files:
                self.print(f"{file.path}")
        else:
            # REPOSITORY
            repo_msg = f"[{repo.id}] {repo.name}"
            self.print_heading1(repo_msg, dim=True)
            # FILES
            self.print_no_result("No results found")

    @finish_main_thread
    def on_print_end(self, elapsed_time) -> None:
        self.print_separate_line()
        if not self.param.repo_name:
            count_msg = self.repo_count if self.repo_count != 0 else "NO"
            msg = f'[{elapsed_time}] There are {count_msg} repository(s) containing "{self.param.keyword}".'
            self.print(msg)
        self.repo_count = 0

    @finish_main_thread
    def on_print_error(self, error: Exception) -> None:
        self.print(f"[Error] {error}", color="bright_red")
