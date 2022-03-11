from gsc.constants import PAGING_ITEM_NUMBER
from gsc.data.repository.base_repository import BaseRepository
from gsc.entities.gitlab_model import Project
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
