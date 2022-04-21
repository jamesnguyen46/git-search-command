from dataclasses import dataclass
from gsc.entities.base_model import BaseModel


@dataclass(unsafe_hash=True)
class Project(BaseModel):
    # pylint: disable=C0103
    id: int
    name: str
    archived: bool
    url: str


@dataclass
class File(BaseModel):
    name: str
    path: str
    ref: str
    data_preview: bool
    project_url: str = ""

    @property
    def url(self):
        return f"{self.project_url}/-/blob/{self.ref}/{self.path}"
