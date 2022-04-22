from dependency_injector import containers, providers
from gsc.config import GitHubConfig
from gsc.data.request.github_request import RepositoryRequest, SearchRequest
from gsc.data.repository.github_repository import (
    GitHubRepoRepository,
    GitHubSearchRepository,
)
from gsc.use_cases.github_search_use_case import (
    GitHubSearchRepoUseCase,
    GitHubSearchMultiRepoUseCase,
)


class GitHubContainer(containers.DeclarativeContainer):
    # Dependencies
    app_config = providers.Dependency()

    # Config
    config = providers.ThreadSafeSingleton(GitHubConfig)

    # Api request
    repo_request = providers.Singleton(
        RepositoryRequest, config=config, app_config=app_config
    )
    search_request = providers.Singleton(
        SearchRequest, config=config, app_config=app_config
    )

    # Repository
    get_repo = providers.Factory(GitHubRepoRepository, repo_request)
    search_repo = providers.Factory(GitHubSearchRepository, search_request)

    # Use case
    search_repo_use_case = providers.Factory(
        GitHubSearchRepoUseCase, get_repo, search_repo
    )
    search_multi_repo_use_case = providers.Factory(
        GitHubSearchMultiRepoUseCase, get_repo, search_repo
    )
