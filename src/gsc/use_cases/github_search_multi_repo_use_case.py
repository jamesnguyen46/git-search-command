import time
from rx.core import Observable
from rx.subject import ReplaySubject
from rx import create, operators as ops
from gsc.entities.github_model import Repository, SearchResult
from gsc.use_cases.base_use_case import BaseUseCase
from gsc.core.rx_task import rx_pool_scheduler
from gsc.data.repository.github_search_repository import GitHubSearchRepository
from gsc.data.repository.github_repo_repository import GitHubRepoRepository


class GitHubSearchMultiRepoUseCase(BaseUseCase):
    def __init__(self) -> None:
        self._get_repositories = GitHubRepoRepository()
        self._on_searching = ReplaySubject()

    def on_searching(self) -> Observable:
        return self._on_searching

    def search(self, keyword: str) -> Observable:
        # Get the repository list
        self._get_repositories.repository_list().pipe(
            ops.group_by(lambda repo: repo),
            ops.flat_map(
                lambda group: group.pipe(
                    # Search in each repository
                    ops.map(lambda repo: self.__do_search_in_repository(repo, keyword)),
                    ops.flat_map(lambda item: item),
                )
            ),
        ).subscribe(self._on_searching)

    def __do_search_in_repository(self, repo: Repository, keyword: str):
        response = GitHubSearchRepository().do_search(repo.full_name, keyword)
        if response and repo is not None:
            response.insert(0, repo)
        return response


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
        usecase = GitHubSearchMultiRepoUseCase()
        usecase.on_searching().subscribe(
            on_completed=print_completed, on_error=print_error, on_next=print_result
        )

        usecase.search("object_mapping")

    run()
