from dependency_injector import containers, providers
from gsc.config import AppConfig
from gsc.di.gitlab_container import GitLabContainer


class ApplicationContainer(containers.DeclarativeContainer):
    # Config
    config = providers.Singleton(AppConfig)

    # Gitlab
    gitlab = providers.Container(GitLabContainer, app_config=config)
