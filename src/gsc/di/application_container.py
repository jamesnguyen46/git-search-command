from dependency_injector import containers, providers
from gsc.config import AppConfig
from gsc.di.gitlab_container import GitLabContainer


class ApplicationContainer(containers.DeclarativeContainer):
    # Config
    config = providers.ThreadSafeSingleton(AppConfig)

    # Gitlab module
    gitlab_module = providers.Container(GitLabContainer, app_config=config)
