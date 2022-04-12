from gsc.core.rx_task import RxTask
from gsc.core.request_wrapper import (
    Api,
    GetRequest,
    GetRequestAutoFetchPagination,
)
from gsc.config import AppConfig, GitLabConfig
from gsc.data.response.gitlab_response import FileResponse, ProjectResponse


class GitLabApi(Api):
    def __init__(self) -> None:
        config = GitLabConfig()
        selected_env = config.get_session_env()
        super().__init__(
            selected_env.host_name,
            {
                "Content-Type": "application/json;charset=UTF-8",
                "PRIVATE-TOKEN": selected_env.private_token,
            },
            AppConfig().is_debug(),
        )


class ProjectRequest(GitLabApi):
    @RxTask
    @GetRequestAutoFetchPagination(
        path="api/v4/groups/{group_name}/projects", response_model=ProjectResponse
    )
    def project_list(self, group_name: str, limit: int):
        return {"group_name": group_name}, {
            "page": 1,
            "per_page": limit,
            "order_by": "id",
            "sort": "asc",
        }

    @RxTask
    @GetRequest(path="api/v4/projects/{proj_id}", response_model=ProjectResponse)
    def project_info(self, proj_id: int):
        return {"proj_id": proj_id}, None


class SearchRequest(GitLabApi):
    @RxTask
    @GetRequest(path="api/v4/projects/{proj_id}/search", response_model=FileResponse)
    def search_in_project(self, proj_id: int, keyword: str):
        return {"proj_id": proj_id}, {
            "scope": "blobs",
            "search": keyword,
            "per_page": 100,
        }
