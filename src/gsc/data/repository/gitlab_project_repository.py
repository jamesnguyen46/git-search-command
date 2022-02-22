from gsc.constant.const import PAGING_ITEM_NUMBER
from gsc.data.repository.base_repository import BaseRepository
from gsc.data.response.project import Project
from gsc.data.api.gitlab_api import ProjectApi
from gsc.request.rx_task import rx_task


class GitLabProjectRepository(BaseRepository):
    def __init__(self) -> None:
        super().__init__()
        self.api = ProjectApi()

    @rx_task
    def project_info(self, project_id: int):
        return self.object_mapping(Project, self.api.project_info(project_id))

    @rx_task
    def project_list(self, group_name: str):
        return self.object_mapping(
            Project, self.api.project_list(group_name, PAGING_ITEM_NUMBER)
        )


# TEMP : remove it later
if __name__ == "__main__":
    repo = GitLabProjectRepository()

    def print_console():
        pass

    repo.project_list("android").subscribe(
        on_next=lambda p: print(f"[{p.id}] {p.name} : {p.web_url}"),
        on_completed=lambda: print("project_list completed"),
        on_error=lambda e: print(f"[Error] : {e}"),
    )

    repo.project_info(2110).subscribe(
        on_next=lambda p: print(f"[{p.id}] {p.name} : {p.web_url}"),
        on_completed=lambda: print("project_info completed"),
        on_error=lambda e: print(f"[Error] : {e}"),
    )
