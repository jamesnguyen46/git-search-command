from dataclasses import dataclass
from gsc.core.base_model import BaseModel


# pylint: disable=R0902
@dataclass
class RepositoryResponse(BaseModel):
    def __init__(self, **kwargs):
        super().__init__()
        # pylint: disable=C0103
        self.id = kwargs.get("id")
        self.name = kwargs.get("name")
        self.full_name = kwargs.get("full_name")
        self.private = kwargs.get("private")
        self.archived = kwargs.get("archived")
        self.html_url = kwargs.get("html_url")
        self.fork = kwargs.get("fork")
        self.forks_url = kwargs.get("forks_url")


@dataclass
class ResultResponse(BaseModel):
    def __init__(self, **kwargs):
        super().__init__()
        self.total_count = kwargs.get("total_count")
        self.items = []
        items = kwargs.get("items")
        if items:
            for item in items:
                self.items.append(FileResponse(**item))


@dataclass
class FileResponse(BaseModel):
    def __init__(self, **kwargs):
        super().__init__()
        self.name = kwargs.get("name")
        self.path = kwargs.get("path")
        self.html_url = kwargs.get("html_url")
        repository = kwargs.get("repository")
        if repository:
            self.repository_id = repository.get("id")
