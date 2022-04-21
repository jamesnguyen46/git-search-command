from rx import Observable, operators as ops
from gsc.constants import GitHubConstant
from gsc.data.repository.base_repository import BaseRepository
from gsc.data.request.github_request import RepositoryRequest, SearchRequest
from gsc.data.response.github_response import RepositoryResponse, FileResponse
from gsc.entities.github_model import Repository, File
from gsc.core.rx_task import rx_pool_scheduler


class GitHubRepoRepository(BaseRepository):
    def __init__(self, repo_request: RepositoryRequest) -> None:
        super().__init__()
        self._request = repo_request

    def get_repository_info(self, repo_name: str) -> Observable:
        return self._request.get_repository_info(repo_name).pipe(
            ops.map(self.__object_mapping)
        )

    def get_repository_list(self) -> Observable:
        return self._request.get_repository_list(
            GitHubConstant.REPOSITORY_LIST_API_LIMIT
        ).pipe(ops.map(self.__object_mapping))

    def __object_mapping(self, response: RepositoryResponse) -> Repository:
        return Repository(
            id=response.id,
            name=response.name,
            full_name=response.full_name,
            private=response.private,
            archived=response.archived,
            html_url=response.html_url,
            fork=response.fork,
            forks_url=response.forks_url,
        )


class GitHubSearchRepository(BaseRepository):
    def __init__(self, search_request: SearchRequest) -> None:
        super().__init__()
        self._request = search_request

    def search(self, repo_full_name: int, keyword: str) -> Observable:
        return self._request.search_in_repo(
            repo_full_name, keyword, GitHubConstant.SEARCH_API_LIMIT
        ).pipe(
            ops.subscribe_on(rx_pool_scheduler),
            ops.map(lambda value: value.items),
            ops.flat_map(lambda item: item),
            ops.map(self.__file_mapping),
        )

    def __file_mapping(self, response: FileResponse) -> File:
        return File(
            name=response.name,
            path=response.path,
            html_url=response.html_url,
            repository_id=response.repository_id,
        )
