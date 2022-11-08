from rx import Observable, operators as ops
from gsc.constants import GitLabConstant
from gsc.data.repository.base_repository import BaseRepository
from gsc.data.request.gitlab_request import ProjectRequest, SearchRequest
from gsc.data.response.gitlab_response import ProjectResponse, FileResponse
from gsc.domain.entities.gitlab_model import Project, File


class GitLabProjectRepository(BaseRepository):
    def __init__(self, project_request: ProjectRequest) -> None:
        super().__init__()
        self._request = project_request

    def project_info(self, project_id: int) -> Observable:
        return self._request.project_info(project_id).pipe(
            ops.map(self.__project_mapping)
        )

    def project_list(self, group_name: str) -> Observable:
        return self._request.project_list(
            group_name, GitLabConstant.GROUP_API_LIMIT
        ).pipe(ops.map(self.__project_mapping))

    def __project_mapping(self, response: ProjectResponse) -> Project:
        return Project(
            id=response.id,
            name=response.name,
            archived=response.archived,
            url=response.web_url,
        )


class GitLabSearchRepository(BaseRepository):
    def __init__(self, search_request: SearchRequest) -> None:
        super().__init__()
        self._request = search_request

    def search(self, project_id: int, keyword: str) -> Observable:
        return self._request.search_in_project(
            project_id, keyword, GitLabConstant.SEARCH_API_LIMIT
        ).pipe(
            ops.distinct(lambda item: item.path),
            ops.map(self.__file_mapping),
        )

    def __file_mapping(self, response: FileResponse) -> File:
        return File(
            name=response.name,
            path=response.path,
            ref=response.ref,
            data_preview=response.data_preview,
        )
