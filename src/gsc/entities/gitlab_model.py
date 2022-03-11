from gsc.entities.base import BaseModel


class Project:
    def __init__(self, **kwargs):
        # pylint: disable=C0103
        self.id = kwargs.get("id")
        self.name = kwargs.get("name")
        self.web_url = kwargs.get("web_url")


class FileName(BaseModel):
    def __init__(self, **kwargs):
        self.name = kwargs.get("basename")
        self.path = kwargs.get("path")
        self.start_lines = []
        self.start_lines.append(kwargs.get("startline"))
        self.project_id = kwargs.get("project_id")
        self.data_preview = kwargs.get("data")
