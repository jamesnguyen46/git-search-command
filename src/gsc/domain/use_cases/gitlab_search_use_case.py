from rx.core import Observable
from rx.subject import ReplaySubject
from rx import combine_latest, just, operators as ops
from gsc.domain.entities.gitlab_model import Project
from gsc.domain.use_cases.base_use_case import BaseUseCase
from gsc.core.rx_task import rx_pool_scheduler
from gsc.data.repository.gitlab_repository import (
    GitLabProjectRepository,
    GitLabSearchRepository,
)


class GitLabSearchProjectUseCase(BaseUseCase):
    def __init__(
        self, project_repo: GitLabProjectRepository, search_repo: GitLabSearchRepository
    ) -> None:
        self._project_repo = project_repo
        self._search_repo = search_repo
        self._on_searching = ReplaySubject()

    def on_searching(self) -> Observable:
        return self._on_searching

    def search(self, project_id: int, keyword: str):
        combine_latest(
            self._project_repo.project_info(project_id),
            self._search_repo.search(project_id, keyword).pipe(ops.to_list()),
        ).pipe(ops.map(self.__update_file_url),).subscribe(self._on_searching)

    def __update_file_url(self, value):
        project: Project = value[0]
        files: list = value[1]
        if files:
            for file in files:
                file.project_url = project.url
        return value


class GitLabSearchGroupUseCase(BaseUseCase):
    def __init__(
        self, project_repo: GitLabProjectRepository, search_repo: GitLabSearchRepository
    ) -> None:
        self._project_repo = project_repo
        self._search_repo = search_repo
        self._on_searching = ReplaySubject()

    def on_searching(self) -> Observable:
        return self._on_searching

    def search(self, group_name: str, keyword: str) -> Observable:
        if group_name:
            self._project_repo.project_list(group_name).pipe(
                ops.group_by(lambda proj: proj),
                ops.flat_map(
                    lambda group: group.pipe(
                        ops.observe_on(rx_pool_scheduler),
                        ops.map(
                            lambda project: self.__search_in_project(project, keyword)
                        ),
                    )
                ),
                ops.flat_map(lambda item: item),
            ).subscribe(self._on_searching)
        else:
            self._project_repo.own_project_list().pipe(
                ops.group_by(lambda proj: proj),
                ops.flat_map(
                    lambda group: group.pipe(
                        ops.observe_on(rx_pool_scheduler),
                        ops.map(
                            lambda project: self.__search_in_project(project, keyword)
                        ),
                    )
                ),
                ops.flat_map(lambda item: item),
            ).subscribe(self._on_searching)

    def __search_in_project(self, project: Project, keyword: str):
        return combine_latest(
            just(project),
            self._search_repo.search(project.id, keyword).pipe(ops.to_list()),
        ).pipe(
            ops.do_action(on_next=self.__update_file_url),
        )

    def __update_file_url(self, value):
        project: Project = value[0]
        files: list = value[1]
        if files:
            for file in files:
                file.project_url = project.url
        return value
