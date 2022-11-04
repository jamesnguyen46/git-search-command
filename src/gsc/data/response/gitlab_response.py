from dataclasses import dataclass
from gsc.entities.base_model import BaseModel


@dataclass
class ProjectResponse(BaseModel):
    def __init__(self, **kwargs):
        super().__init__()
        # pylint: disable=C0103
        self.id = kwargs.get("id")
        self.name = kwargs.get("name_with_namespace")
        self.archived = kwargs.get("archived")
        self.web_url = kwargs.get("web_url")


@dataclass
class FileResponse(BaseModel):
    def __init__(self, **kwargs):
        super().__init__()
        self.name = kwargs.get("basename")
        self.path = kwargs.get("path")
        self.ref = kwargs.get("ref")
        self.start_line = kwargs.get("startline")
        self.project_id = kwargs.get("project_id")
        self.data_preview = kwargs.get("data")
