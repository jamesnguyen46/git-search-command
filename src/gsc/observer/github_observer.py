from typing import Any
from gsc.entities.github_model import Repository, File
from gsc.observer.base_observer import BasePrintObserver, PrintParam
from gsc.command_line import finish_main_thread
from gsc.constants import GitHubConstant


class GitHubParam(PrintParam):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.repo_name = kwargs.get("repo_name")


class GitHubPrintObserver(BasePrintObserver):
    def __init__(self, param: GitHubParam = None) -> None:
        self.repo_count = 0
        super().__init__(param)

    def on_print_start(self) -> None:
        msg = f'[{GitHubConstant.NAME}] ("{self.param.env_name}" env) Searching for "{self.param.keyword}" ...'
        self.print(msg)
        self.write(f"# {msg}")

    def on_print_result(self, value: Any) -> None:
        repo: Repository = value[0]
        files: File = value[1]
        self.print("------------------------")
        self.write_lines()
        if files:
            # Print repository
            self.repo_count += 1
            repo_msg = f"[{repo.id}] {repo.name} - {len(files)} file(s)"
            if repo.archived:
                repo_msg = f"[{repo.id}] (❗Archived) {repo.name} - {len(files)} file(s)"
            self.print(repo_msg, fg="bright_magenta")
            self.write(f"## [{repo_msg}]({repo.html_url})")
            self.write_lines()
            # Print files
            for file in files:
                self.print(f"{file.path}")
                self.write(f"- [{file.path}]({file.html_url})")
        else:
            # Print repository
            repo_msg = f"[{repo.id}] {repo.name}"
            self.print(repo_msg, fg="bright_magenta", dim=True)
            self.write(f"## [{repo_msg}]({repo.html_url})")
            self.write_lines()
            # Print files
            self.print("No results found", dim=True)
            self.write("No results found")

    @finish_main_thread
    def on_print_end(self, elapsed_time) -> None:
        self.print("------------------------")
        if not self.param.repo_name:
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
