from gsc.core.rx_task import rx_task
from gsc.data.repository.base_repository import BaseRepository
from gsc.entities.github_model import SearchResult
from gsc.data.request.github_request import SearchApi


class GitHubSearchRepository(BaseRepository):
    def __init__(self) -> None:
        super().__init__()
        self.api = SearchApi()

    @rx_task
    def search(self, repo_name: str, keyword: str):
        return self.do_search(repo_name, keyword)

    def do_search(self, repo_name: str, keyword: str):
        response = self.object_mapping(
            SearchResult, self.api.search_in_repository(repo_name, keyword)
        )
        return response[0].items if isinstance(response, list) else response.items
