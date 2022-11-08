from dataclasses import dataclass
from gsc.core.base_model import BaseModel

# pylint: disable=R0902
@dataclass(unsafe_hash=True)
class Repository(BaseModel):
    # pylint: disable=C0103
    id: int
    name: str
    full_name: str
    private: bool
    archived: bool
    html_url: str
    fork: bool
    forks_url: str


@dataclass
class File(BaseModel):
    name: str
    path: str
    html_url: str
    repository_id: int
