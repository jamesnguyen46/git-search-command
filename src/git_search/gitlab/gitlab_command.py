import sys
from git_search.gitlab.gitlab_repository import GitlabRepository


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
            self.log_header(f'Group "{group_name}" : ???')
            self.exit_error(project_results)

        if len(project_results) == 0:
            self.log_header(f'Group "{group_name}" : ...')
            self.exit_warning("There are no project(s) in group.")

        proj_count = 0
        for proj in project_results:
            search_status, search_result = self.repository.search_content(
                proj["id"], keyword
            )

            if not search_status:
                continue
            # Don't show project which there does not contain keyword.
            if len(search_result) == 0:
                continue

            proj_count += 1
            self.log_header(f"[{proj['id']}] {proj['name']} ({len(search_result)})")
            for filename in search_result:
                self.log_result(filename)

        self.divider()
        self.log_end(
            f'There are {proj_count} project(s) which contain "{keyword}" keyword.',
            False,
        )

    def search_in_project(self, keyword, project_id):
        self.log_start()
        proj_status, proj_value = self.repository.get_project_info(project_id)
        if not proj_status:
            self.log_header(f"Project ({project_id}) : ???")
            self.exit_error(proj_value)

        self.log_header(f"[{project_id}] {proj_value}")
        search_status, search_result = self.repository.search_content(
            project_id, keyword
        )
        if not search_status:
            self.exit_error(search_result)

        if len(search_result) == 0:
            self.exit_warning(
                f'There are no file(s) which contain "{keyword}" keyword.'
            )

        for filename in search_result:
            self.log_result(filename)

        self.log_end(
            f'There are {len(search_result)} file(s) which contain "{keyword}" keyword.'
        )

    def log_start(self):
        print("Searching...")

    def log_end(self, msg, show_end_divider=True):
        print("\n" + Color.WARNING + Color.BOLD + msg + Color.ENDC)
        if show_end_divider:
            self.divider()
        else:
            print("")
        sys.exit(0)

    def log_header(self, msg):
        self.divider()
        print(Color.HEADER + Color.BOLD + msg + Color.ENDC + "\n")

    def log_result(self, msg):
        print(msg)

    def exit_warning(self, msg):
        print(Color.WARNING + msg + Color.ENDC)
        self.divider()
        sys.exit(0)

    def exit_error(self, msg):
        print(Color.ERROR + msg + Color.ENDC)
        self.divider()
        sys.exit(1)

    def divider(self):
        print("-----------------------------")
