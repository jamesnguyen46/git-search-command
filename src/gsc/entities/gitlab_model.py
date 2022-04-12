from gsc.entities.base_model import BaseModel


class Project(BaseModel):
    def __init__(self):
        # pylint: disable=C0103
        self.id = None
        self.name = None
        self.archived = False
        self.url = None


class File(BaseModel):
    def __init__(self):
        self.name = None
        self.path = None
        self.ref = None
        self.project_url = None
        self.data_preview = None

    @property
    def url(self):
        return f"{self.project_url}/-/blob/{self.ref}/{self.path}"
