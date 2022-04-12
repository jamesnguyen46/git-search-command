from gsc.entities.base_model import BaseModel


class ProjectResponse(BaseModel):
    def __init__(self, **kwargs):
        # pylint: disable=C0103
        self.id = kwargs.get("id")
        self.name = kwargs.get("name")
        self.archived = kwargs.get("archived")
        self.web_url = kwargs.get("web_url")


class FileResponse(BaseModel):
    def __init__(self, **kwargs):
        self.name = kwargs.get("basename")
        self.path = kwargs.get("path")
        self.ref = kwargs.get("ref")
        self.start_line = kwargs.get("startline")
        self.project_id = kwargs.get("project_id")
        self.data_preview = kwargs.get("data")
