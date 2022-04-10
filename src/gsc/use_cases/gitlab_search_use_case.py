from rx.core import Observable
from rx.subject import ReplaySubject
from rx import combine_latest, just, operators as ops
from gsc.entities.gitlab_model import Project
from gsc.use_cases.base_use_case import BaseUseCase
from gsc.data.request.rx_task import rx_pool_scheduler
from gsc.data.repository.gitlab_repository import (
    GitLabProjectRepository,
    GitLabSearchRepository,
)


class GitLabSearchProjectUseCase(BaseUseCase):
    def __init__(self) -> None:
        self._project_repo = GitLabProjectRepository()
        self._search_repo = GitLabSearchRepository()
        self._on_searching = ReplaySubject()

    def on_searching(self) -> Observable:
        return self._on_searching

    def search(self, project_id: int, keyword: str):
        combine_latest(
            self._project_repo.project_info(project_id),
            self._search_repo.search(project_id, keyword).pipe(ops.to_list()),
        ).pipe(
            ops.subscribe_on(rx_pool_scheduler()),
            ops.map(self.__update_file_url),
        ).subscribe(
            self._on_searching
        )

    def __update_file_url(self, value):
        project: Project = value[0]
        files: list = value[1]
        if files:
            for file in files:
                file.project_url = project.url
        return value


class GitLabSearchGroupUseCase(BaseUseCase):
    def __init__(self) -> None:
        self._project_repo = GitLabProjectRepository()
        self._on_searching = ReplaySubject()

    def on_searching(self) -> Observable:
        return self._on_searching

    def search(self, group_name: str, keyword: str) -> Observable:
        self._project_repo.project_list(group_name).pipe(
            ops.subscribe_on(rx_pool_scheduler()),
            ops.group_by(lambda proj: proj),
            ops.flat_map(
                lambda group: group.pipe(
                    ops.observe_on(rx_pool_scheduler()),
                    ops.map(lambda repo: self.__search_in_project(repo, keyword)),
                )
            ),
            ops.flat_map(lambda item: item),
        ).subscribe(self._on_searching)

    def __search_in_project(self, project: Project, keyword: str):
        return combine_latest(
            just(project),
            GitLabSearchRepository().search(project.id, keyword).pipe(ops.to_list()),
        ).pipe(
            ops.subscribe_on(rx_pool_scheduler()),
            ops.do_action(on_next=self.__update_file_url),
        )

    def __update_file_url(self, value):
        project: Project = value[0]
        files: list = value[1]
        if files:
            for file in files:
                file.project_url = project.url
        return value
