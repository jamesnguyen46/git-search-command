from dependency_injector import containers, providers
from gsc.config import AppConfig
from gsc.di.github_container import GitHubContainer
from gsc.di.gitlab_container import GitLabContainer


class ApplicationContainer(containers.DeclarativeContainer):
    # Config
    config = providers.ThreadSafeSingleton(AppConfig)

    # GitLab module
    gitlab_module = providers.Container(GitLabContainer, app_config=config)

    # GitHub module
    github_module = providers.Container(GitHubContainer, app_config=config)
