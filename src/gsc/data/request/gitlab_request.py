from gsc.config import AppConfig, GitLabConfig
from gsc.core.request_decorator import (
    Api,
    get_request,
    get_request_pagination,
)
from gsc.constants import GitLabConstant, APP_NAME
from gsc.core.rx_task import rx_task
from gsc.core.rate_limit import rate_limit
from gsc.data.response.gitlab_response import FileResponse, ProjectResponse


class GitLabApi(Api):
    def __init__(self, config: GitLabConfig, app_config: AppConfig) -> None:
        selected_env = config.get_session_env()
        super().__init__(
            selected_env.host_name,
            {
                "User-Agent": f"{APP_NAME}",
                "Content-Type": "application/json;charset=UTF-8",
                "PRIVATE-TOKEN": selected_env.private_token,
            },
            selected_env.verify_ssl_cert,
            app_config.is_debug(),
        )


class ProjectRequest(GitLabApi):
    @rx_task
    @get_request_pagination(
        path="api/v4/groups/{group_name}/projects", response_model=ProjectResponse
    )
    def project_list(self, group_name: str, limit: int):
        return {"group_name": group_name}, {
            "page": 1,
            "per_page": limit,
            "order_by": "id",
            "sort": "asc",
            "include_subgroups": "true",
        }

    @rx_task
    @get_request_pagination(path="api/v4/projects", response_model=ProjectResponse)
    def own_project_list(self, limit: int):
        return None, {"simple": "true", "owned": "true", "per_page": limit}

    @rx_task
    @get_request(path="api/v4/projects/{proj_id}", response_model=ProjectResponse)
    def project_info(self, proj_id: int):
        return {"proj_id": proj_id}, None


class SearchRequest(GitLabApi):
    @rx_task
    @rate_limit(
        calls=GitLabConstant.SEARCH_RATE_LIMIT_CALLS,
        period=GitLabConstant.SEARCH_RATE_LIMIT_PERIOD,
    )
    @get_request(path="api/v4/projects/{proj_id}/search", response_model=FileResponse)
    def search_in_project(self, proj_id: int, keyword: str, limit: int):
        return {"proj_id": proj_id}, {
            "scope": "blobs",
            "search": keyword,
            "per_page": limit,
        }
