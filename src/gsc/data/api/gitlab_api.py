from os import environ as env
from gsc.request.request_wrapper import Api, GetRequest, GetRequestAutoFetchPagination


class GitLabApi(Api):
    def __init__(self) -> None:
        super().__init__(
            env["GITLAB_BASE_URL"],
            {
                "Content-Type": "application/json;charset=UTF-8",
                "PRIVATE-TOKEN": env["GITLAB_API_TOKEN"],
            },
        )


class ProjectApi(GitLabApi):
    @GetRequestAutoFetchPagination(path="api/v4/groups/{group_name}/projects")
    def project_list(self, group_name: str, limit: int):
        return {"group_name": group_name}, {
            "page": 1,
            "per_page": limit,
            "order_by": "id",
            "sort": "asc",
        }

    @GetRequest(path="api/v4/projects/{proj_id}")
    def project_info(self, proj_id: int):
        return {"proj_id": proj_id}, None


class SearchApi(GitLabApi):
    @GetRequest(path="api/v4/projects/{proj_id}/search")
    def search_in_project(self, proj_id: int, keyword: str):
        return {"proj_id": proj_id}, {"scope": "blobs", "search": keyword}
