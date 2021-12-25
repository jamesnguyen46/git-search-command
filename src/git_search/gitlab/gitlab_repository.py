from os import environ as env
from git_search.base.base_repository import BaseRepository
from git_search.constant.const import PAGING
from git_search.api.gitlab_api import PROJECT_GROUP_API, PROJECT_INFO_API, SEARCH_API


class GitlabRepository(BaseRepository):
    def __init__(self):
        super().__init__(
            env["GITLAB_BASE_URL"], {"PRIVATE-TOKEN": env["GITLAB_API_TOKEN"]}
        )

    def get_project_list(self, group_name):
        status, response = self.__send_get_request_paging(
            PROJECT_GROUP_API.format(group_name),
            request_param={"order_by": "id", "sort": "asc"},
        )

        if not status:
            return status, response

        project_array = []
        for i in response:
            # Ignore the projects which have archived
            if i["archived"] is True:
                continue

            project_array.append({"id": i["id"], "name": i["name"]})
        return status, project_array

    def get_project_info(self, project_id):
        status, response = self.__send_get_request(PROJECT_INFO_API.format(project_id))
        if not status:
            return status, response
        return status, response["name"]

    def search_content(self, project_id, keyword):
        status, response = self.__send_get_request_paging(
            SEARCH_API.format(project_id),
            request_param={"scope": "blobs", "search": f"{keyword}"},
        )

        if not status:
            return status, response

        file_name_array = []
        for i in response:
            file_name_array.append(i["filename"])
        return status, file_name_array

    def __send_get_request_paging(self, api_path, request_param=None):
        param = {"per_page": PAGING}
        if request_param is not None:
            param.update(request_param)

        page_index = 1
        total_response = []
        while True:
            param["page"] = page_index
            success, response = self.send_http_get(api_path, param)
            # Break loop condition if there is any error
            if not success:
                return False, response

            total_response += response.json()

            if "x-total-pages" not in response.headers:
                break
            if page_index >= int(response.headers["x-total-pages"]):
                break

            page_index += 1

        return True, total_response

    def __send_get_request(self, api_path, request_param=None):
        success, response = self.send_http_get(api_path, request_param)
        return success, response if not success else response.json()
