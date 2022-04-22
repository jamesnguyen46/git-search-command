from rx.core import Observable
from rx.subject import ReplaySubject
from rx import combine_latest, just, operators as ops
from gsc.entities.github_model import Repository
from gsc.use_cases.base_use_case import BaseUseCase
from gsc.core.rx_task import rx_pool_scheduler
from gsc.data.repository.github_repository import (
    GitHubRepoRepository,
    GitHubSearchRepository,
)


class GitHubSearchRepoUseCase(BaseUseCase):
    def __init__(
        self, get_repo: GitHubRepoRepository, search_repo: GitHubSearchRepository
    ) -> None:
        self._get_repo = get_repo
        self._search_repo = search_repo
        self._on_searching = ReplaySubject()

    def on_searching(self) -> Observable:
        return self._on_searching

    def search(self, repo_name: str, keyword: str):
        combine_latest(
            self._get_repo.get_repository_info(repo_name),
            self._search_repo.search(repo_name, keyword).pipe(ops.to_list()),
        ).subscribe(self._on_searching)


class GitHubSearchMultiRepoUseCase(BaseUseCase):
    def __init__(
        self, get_repo: GitHubRepoRepository, search_repo: GitHubSearchRepository
    ) -> None:
        self._get_repo = get_repo
        self._search_repo = search_repo
        self._on_searching = ReplaySubject()

    def on_searching(self) -> Observable:
        return self._on_searching

    def search(self, keyword: str) -> Observable:
        self._get_repo.get_repository_list().pipe(
            ops.group_by(lambda repo: repo),
            ops.flat_map(
                lambda group: group.pipe(
                    ops.observe_on(rx_pool_scheduler),
                    ops.map(lambda repo: self.__search_in_repository(repo, keyword)),
                )
            ),
            ops.flat_map(lambda item: item),
        ).subscribe(self._on_searching)

    def __search_in_repository(self, repo: Repository, keyword: str):
        return combine_latest(
            just(repo),
            self._search_repo.search(repo.full_name, keyword).pipe(ops.to_list()),
        )
