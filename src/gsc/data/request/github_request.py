from gsc.core.rx_task import rx_task
from gsc.core.request_decorator import Api, get_request
from gsc.config import AppConfig, GitHubConfig


class GitHubApi(Api):
    def __init__(self) -> None:
        config = GitHubConfig()
        selected_env = config.get_session_env()
        super().__init__(
            selected_env.host_name,
            {
                "Accept": "application/vnd.github.v3+json",
                "Authorization": f"token {selected_env.private_token}",
            },
            AppConfig().is_debug(),
        )


class RepositoryApi(GitHubApi):
    @rx_task
    @get_request(path="user/repos")
    def repository_list(self, limit: int):
        return None, {
            "page": 1,
            "per_page": limit,
        }


class SearchApi(GitHubApi):
    @rx_task
    @get_request(path="search/code")
    def search_in_repository(self, repo_name: str, keyword: str):
        query = f"{keyword}+repo:{repo_name}"
        return None, {
            "q": query,
            "per_page": 100,
            "page": 1,
        }
