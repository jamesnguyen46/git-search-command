class FileName:
    def __init__(self, **kwargs):
        self._name = kwargs["basename"]
        self._path = kwargs["path"]
        self._start_lines = []
        self._start_lines.append(kwargs["startline"])
        self._project_id = kwargs["project_id"]
        self._data_preview = kwargs["data"]

    @property
    def name(self):
        return self._name

    @property
    def path(self):
        return self._path

    @property
    def project_id(self):
        return self._project_id

    @property
    def start_lines(self):
        return self._start_lines

    @start_lines.setter
    def start_lines(self, new_list):
        self._start_lines = new_list

    @property
    def data_preview(self):
        return self._data_preview
