from itertools import groupby
from gsc.request.rx_task import rx_task
from gsc.data.repository.base_repository import BaseRepository
from gsc.entities.gitlab_model import FileName
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
            FileName, self.api.search_in_project(project_id, keyword)
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
