from itertools import groupby
from gsc.request.rx_task import rx_task
from gsc.data.repository.base_repository import BaseRepository
from gsc.data.response.search_result import SearchResult
from gsc.data.api.gitlab_api import SearchApi


class GitLabSearchRepository(BaseRepository):
    def __init__(self) -> None:
        super().__init__()
        self.api = SearchApi()

    @rx_task
    def search(self, project_id: int, keyword: str):
        return self.do_search(project_id, keyword)

    def do_search(self, project_id: int, keyword: str):
        response = self.object_mapping(
            SearchResult, self.api.search_in_project(project_id, keyword)
        )

        if isinstance(response, list):
            last_file_path = ""
            accumulate_start_line = []
            for item in response:
                if last_file_path == item.path:
                    item.start_lines = accumulate_start_line + item.start_lines
                    accumulate_start_line = item.start_lines
                    continue

                last_file_path = item.path
                accumulate_start_line = item.start_lines

        return [list(group).pop() for _, group in groupby(response, lambda x: x.path)]


# TEMP : remove it later
if __name__ == "__main__":

    def print_result(item):
        str_line = ", ".join(map(str, item.start_lines))
        print(f"{item.path} (line {str_line})")

    repo = GitLabSearchRepository()
    repo.search(2110, "addImplement").subscribe(
        on_next=print_result,
        on_completed=lambda: print("search_in_project completed"),
        on_error=lambda e: print(f"[Error] : {e}"),
    )

    # res = repo.do_search(2110, "addImplement")
    # for item in res:
    #     str_line = ", ".join(map(str, item.start_lines))
    #     print(f"{item.path} (line {str_line})")
