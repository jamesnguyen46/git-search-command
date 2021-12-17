import os
import sys
import requests
import argparse

class BaseRepository:
    def __init__(self, base_url, common_header = None):
        self.base_url = base_url
        self.common_header = common_header

    def send_Http_get(self, api_path, request_param = None):
        try:
            response = requests.get(
                url = f"{self.base_url}/{api_path}",
                params = request_param,
                headers = self.common_header
            )
            if response.status_code != 200:
                return False, f"[Error] Api \"{api_path}\" : {response.json()['message']}"

            return True, response
        except:
            return False, f"[Error] Api \"{api_path}\" : {sys.exc_info()[0]} occurred."

class GitlabApi:
    BASE_URL = os.environ['GITLAB_BASE_URL']
    PROJECT_GROUP_API = "groups/{}/projects"
    PROJECT_INFO_API = "projects/{}"
    SEARCH_API = "projects/{}/search"

class GitlabConstant:
    API_TOKEN = os.environ['GITLAB_API_TOKEN']
    PAGING = 100

class GitlabRepository(BaseRepository):
    def __init__(self):
        super().__init__(
            GitlabApi.BASE_URL,
            { 'PRIVATE-TOKEN' : GitlabConstant.API_TOKEN }
        )

    def get_project_list(self, group_name):
        status, response = self.__send_get_request_paging(
            GitlabApi.PROJECT_GROUP_API.format(group_name),
            request_param = { "order_by" : "id", "sort" : "asc" }
        )
        
        if not status: return status, response

        project_array = []
        for i in response:
            # Ignore the projects which have archived
            if i['archived'] == True: continue

            project_array.append(
                { 'id' : i['id'], 'name' : i['name'] }
            )
        return status, project_array

    def get_project_info(self, project_id):
        status, response = self.__send_get_request(GitlabApi.PROJECT_INFO_API.format(project_id))
        if status: return status, response['name']
        else: return status, response

    def search_content(self, project_id, keyword):
        status, response = self.__send_get_request_paging(
            GitlabApi.SEARCH_API.format(project_id), 
            request_param = { "scope" : "blobs", "search" : f"{keyword}" }
        )

        if not status: return status, response

        file_name_array = []
        for i in response:
            file_name_array.append(i['filename'])
        return status, file_name_array

    def __send_get_request_paging(self, api_path, request_param = None):
        param = { "per_page" : GitlabConstant.PAGING }
        if request_param is not None:
            param.update(request_param)
        
        page_index = 1
        total_response = []
        while True:
            param["page"] = page_index
            success, response = self.send_Http_get(api_path, param)
            # Break loop condition if there is any error
            if not success: return False, response

            total_response += response.json()

            if "x-total-pages" not in response.headers: break
            if page_index >= int(response.headers["x-total-pages"]): break

            page_index += 1

        return True, total_response
    
    def __send_get_request(self, api_path, request_param = None):
        success, response = self.send_Http_get(api_path, request_param)
        return success, response if not success else response.json()

class Color:
    HEADER = "\033[95m"
    WARNING = "\033[93m"
    ERROR = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"

class SearchCommand:
    def __init__(self):
        self.repository = GitlabRepository()

    def search_in_group(self, keyword, group_name):
        self.log_start()
        status, project_results = self.repository.get_project_list(group_name)
        if not status:
            self.log_header(f"Group \"{group_name}\" : ???")
            self.exit_error(project_results)

        if len(project_results) == 0:
            self.log_header(f"Group \"{group_name}\" : ...")
            self.exit_warning(f"There are no project(s) in group.")

        proj_count = 0
        for proj in project_results:
            search_status, search_result = self.repository.search_content(proj['id'], keyword)

            if not search_status: continue
            # Don't show project which there does not contain keyword.
            if len(search_result) == 0: continue
        
            proj_count += 1
            self.log_header(f"[{proj['id']}] {proj['name']} ({len(search_result)})")
            for filename in search_result:
                self.log_result(filename)

        self.divider()
        self.log_end(f"There are {proj_count} project(s) which contain \"{keyword}\" keyword.", False)

    def search_in_project(self, keyword, project_id):
        self.log_start()
        proj_status, proj_value = self.repository.get_project_info(project_id)
        if not proj_status:
            self.log_header(f"Project ({project_id}) : ???")
            self.exit_error(proj_value)

        self.log_header(f"[{project_id}] {proj_value}")
        search_status, search_result = self.repository.search_content(project_id, keyword)
        if not search_status: 
            self.exit_error(search_result)

        if len(search_result) == 0:
            self.exit_warning(f"There are no file(s) which contain \"{keyword}\" keyword.")

        for filename in search_result:
            self.log_result(filename)

        self.log_end(f"There are {len(search_result)} file(s) which contain \"{keyword}\" keyword.")

    def log_start(self): print("Searching...")

    def log_end(self, msg, show_end_divider = True):
        print("\n" + Color.WARNING + Color.BOLD + msg + Color.ENDC)
        self.divider() if show_end_divider else print("")
        sys.exit(0)

    def log_header(self, msg): self.divider(); print(Color.HEADER + Color.BOLD + msg + Color.ENDC + "\n")

    def log_result(self, msg): print(msg)

    def exit_warning(self, msg): print(Color.WARNING + msg + Color.ENDC); self.divider(); sys.exit(0)

    def exit_error(self, msg): print(Color.ERROR + msg + Color.ENDC); self.divider(); sys.exit(1)

    def divider(self): print("-----------------------------")

# ********** MAIN **********
parser = argparse.ArgumentParser()
parser.add_argument("keyword", help = "something that you want to find.")
group = parser.add_mutually_exclusive_group(required = True)
group.add_argument("-p", "--project_id", type = int, help = "the project id.")
group.add_argument("-g", "--group", help = "the group name.")
args = parser.parse_args()

command = SearchCommand()
if args.group: command.search_in_group(args.keyword, args.group)
elif args.project_id: command.search_in_project(args.keyword, args.project_id)
else: args.print_usage()
# ************************** 