from dependency_injector import containers, providers
from gsc.config import GitLabConfig
from gsc.data.request.gitlab_request import ProjectRequest, SearchRequest
from gsc.data.repository.gitlab_repository import (
    GitLabProjectRepository,
    GitLabSearchRepository,
)
from gsc.use_cases.gitlab_search_use_case import (
    GitLabSearchProjectUseCase,
    GitLabSearchGroupUseCase,
)


class GitLabContainer(containers.DeclarativeContainer):
    # Dependencies
    app_config = providers.Dependency()

    # Config
    config = providers.ThreadSafeSingleton(GitLabConfig)

    # Api request
    project_request = providers.Singleton(
        ProjectRequest, config=config, app_config=app_config
    )
    search_request = providers.Singleton(
        SearchRequest, config=config, app_config=app_config
    )

    # Repository
    project_repo = providers.Factory(GitLabProjectRepository, project_request)
    search_repo = providers.Factory(GitLabSearchRepository, search_request)

    # Use case
    search_proj_use_case = providers.Factory(
        GitLabSearchProjectUseCase, project_repo, search_repo
    )
    search_group_use_case = providers.Factory(
        GitLabSearchGroupUseCase, project_repo, search_repo
    )
