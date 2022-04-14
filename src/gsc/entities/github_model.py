from gsc.entities.base_model import BaseModel


class Repository(BaseModel):
    def __init__(self, **kwargs):
        # pylint: disable=C0103
        self.id = kwargs.get("id")
        self.name = kwargs.get("name")
        self.full_name = kwargs.get("full_name")
        self.web_url = kwargs.get("html_url")


class SearchResult(BaseModel):
    def __init__(self, **kwargs):
        self.total_count = kwargs.get("total_count")
        self.items = []
        items = kwargs.get("items")
        for item in items:
            file_name = FileName(**item)
            self.items.append(file_name)


class FileName(BaseModel):
    def __init__(self, **kwargs):
        self.name = kwargs.get("name")
        self.path = kwargs.get("path")
        self.web_url = kwargs.get("html_url")
