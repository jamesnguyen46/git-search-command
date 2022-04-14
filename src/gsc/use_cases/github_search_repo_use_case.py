from rx.core import Observable
from rx.subject import ReplaySubject
from rx import operators as ops
from gsc.use_cases.base_use_case import BaseUseCase
from gsc.core.rx_task import rx_pool_scheduler
from gsc.data.repository.github_search_repository import GitHubSearchRepository


class GitHubSearchRepoUseCase(BaseUseCase):
    def __init__(self) -> None:
        self._search_repo = GitHubSearchRepository()
        self._on_searching = ReplaySubject()

    def on_searching(self) -> Observable:
        return self._on_searching

    def search(self, repo_name: str, keyword: str) -> Observable:
        self._search_repo.search(repo_name, keyword).pipe(
        ).subscribe(self._on_searching)


# TODO : remove it later
if __name__ == "__main__":
    from typing import Any
    from gsc.command_line import keep_main_thread_running, finish_main_thread

    @finish_main_thread
    def print_completed():
        print("Completed")

    def print_result(value: Any):
        print(f"- {value}")

    @finish_main_thread
    def print_error(value: Any):
        print(value)

    @keep_main_thread_running
    def run():
        usecase = GitHubSearchRepoUseCase()
        usecase.on_searching().subscribe(
            on_completed=print_completed, on_error=print_error, on_next=print_result
        )

        usecase.search("nguyen-ngoc-thach/git-search-command", "object_mapping")

    run()
