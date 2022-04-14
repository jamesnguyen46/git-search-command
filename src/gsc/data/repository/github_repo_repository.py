from gsc.constants import GitHubConstant
from gsc.data.repository.base_repository import BaseRepository
from gsc.entities.github_model import Repository
from gsc.data.request.github_request import RepositoryApi


class GitHubRepoRepository(BaseRepository):
    def __init__(self) -> None:
        super().__init__()
        self.api = RepositoryApi()

    def repository_list(self):
        return self.object_mapping(
            Repository, self.api.repository_list(GitHubConstant.DEFAULT_PAGING_ITEM_NUMBER)
        )
