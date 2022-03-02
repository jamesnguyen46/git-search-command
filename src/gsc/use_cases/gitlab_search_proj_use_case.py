from rx.core import Observable
from rx.subject import ReplaySubject
from rx import concat, operators as ops
from gsc.use_cases.base_use_case import BaseUseCase
from gsc.request.rx_task import rx_pool_scheduler
from gsc.data.repository.gitlab_search_repository import GitLabSearchRepository
from gsc.data.repository.gitlab_project_repository import GitLabProjectRepository


class GitLabSearchProjUseCase(BaseUseCase):
    def __init__(self) -> None:
        self._project_repo = GitLabProjectRepository()
        self._search_repo = GitLabSearchRepository()
        self._on_searching = ReplaySubject()

    def on_searching(self) -> Observable:
        return self._on_searching

    def search(self, project_id: int, keyword: str) -> Observable:
        concat(
            self._project_repo.project_info(project_id),
            self._search_repo.search(project_id, keyword),
        ).pipe(ops.subscribe_on(rx_pool_scheduler())).subscribe(self._on_searching)
