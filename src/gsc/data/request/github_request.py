from gsc.config import AppConfig, GitHubConfig
from gsc.core.request_decorator import (
    Api,
    get_request,
    get_request_pagination,
)
from gsc.constants import GitHubConstant, APP_NAME
from gsc.core.rx_task import rx_task
from gsc.core.rate_limit import rate_limit
from gsc.data.response.github_response import RepositoryResponse, ResultResponse


class GitHubApi(Api):
    def __init__(self, config: GitHubConfig, app_config: AppConfig) -> None:
        selected_env = config.get_session_env()
        super().__init__(
            selected_env.host_name,
            {
                "User-Agent": f"{APP_NAME}",
                "Accept": "application/vnd.github.v3+json",
                "Authorization": f"token {selected_env.private_token}",
            },
            app_config.is_debug(),
        )


class RepositoryRequest(GitHubApi):
    @rx_task
    @get_request_pagination(path="user/repos", response_model=RepositoryResponse)
    def get_repository_list(self, limit: int):
        return None, {"page": 1, "per_page": limit}

    @rx_task
    @get_request(path="repos/{repo_name}", response_model=RepositoryResponse)
    def get_repository_info(self, repo_name: str):
        return {"repo_name": repo_name}, None


class SearchRequest(GitHubApi):
    @rx_task
    @rate_limit(
        calls=GitHubConstant.SEARCH_RATE_LIMIT_CALLS,
        period=GitHubConstant.SEARCH_RATE_LIMIT_PERIOD,
    )
    @get_request(
        path="search/code",
        headers={"Accept": "application/vnd.github.v3.text-match+json"},
        response_model=ResultResponse,
    )
    def search_in_repo(self, repo_full_name: int, keyword: str, limit: int):
        query = f"{keyword}+repo:{repo_full_name}"
        return None, {
            "q": query,
            "per_page": limit,
        }
