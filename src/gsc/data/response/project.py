class Project:
    def __init__(self, **kwargs):
        self._id = kwargs["id"]
        self._name = kwargs["name"]
        self._web_url = kwargs["web_url"]

    @property
    def id(self):
        return self._id

    @property
    def name(self):
        return self._name

    @property
    def web_url(self):
        return self._web_url
