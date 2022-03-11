from enum import Enum
from http import HTTPStatus
from urllib.parse import urlparse, urljoin
import requests
from gsc.utils import json_serialize


class HttpMethod(Enum):
    GET = 1
    POST = 2
    PUT = 3
    PATCH = 4
    DELETE = 5


class Response:
    def __init__(self) -> None:
        self.url = None
        self.status_code = None
        self.json = None
        self.binary = None
        self.exception = None
        self.pagination_links = None

    @property
    def status_ok(self) -> bool:
        if self.status_code == HTTPStatus.OK:
            return True
        return False

    @property
    def endpoint(self):
        return urlparse(self.url).hostname

    @property
    def api_path(self):
        return urlparse(self.url).path


class Request:
    def __init__(self, method: HttpMethod, path: str, headers: dict = None):
        self.path = path if path is not None else ""
        self.method = method
        self.headers = headers

    def __call__(self, func):
        def wrapper(obj, *args, **kwargs):
            if not isinstance(obj, Api):
                raise TypeError("Object type is not supported.")

            path_dict, param_dict = func(obj, *args, **kwargs)

            if path_dict is not None:
                req_path = self.path.format_map(path_dict)

            body_required = self.method not in (HttpMethod.GET, HttpMethod.DELETE)
            req_body = param_dict if body_required else None
            req_params = param_dict if not body_required else None

            return self.send(
                urljoin(obj.host, req_path),
                obj.default_header,
                req_params,
                json_serialize(req_body),
            )

        return wrapper

    def send(
        self, url: str, headers: dict = None, params: dict = None, data: dict = None
    ):
        req_header = self.headers
        if req_header is not None and headers is not None:
            req_header = req_header.update(headers)
        elif headers is not None:
            req_header = headers
        else:
            pass

        try:
            response = requests.request(
                method=self.method.name.upper(),
                url=url,
                headers=req_header,
                params=params,
                data=data,
            )
            response.raise_for_status()
            return self.__handle_success_response(response)
        except Exception as err:
            return self.__handle_error(url, err)

    def __handle_success_response(self, resp: requests.Response) -> Response:
        response = Response()
        response.url = resp.url
        response.status_code = resp.status_code
        response.pagination_links = resp.links

        try:
            response.json = resp.json()
            response.binary = resp.content
        except Exception as err:
            response.exception = err
        return response

    def __handle_error(self, url: str, exc: Exception) -> Response:
        response = Response()
        response.url = url
        response.exception = exc
        return response


class Api:
    def __init__(self, host: str, default_header: dict = None):
        self.host = host
        self.default_header = default_header


class GetRequest(Request):
    def __init__(self, path: str = "", headers: object = None):
        super().__init__(HttpMethod.GET, path, headers)


class GetRequestAutoFetchPagination(GetRequest):
    def send(
        self, url: str, headers: dict = None, params: dict = None, data: dict = None
    ):
        _url = url
        while True:
            if _url == url:
                response = super().send(url, headers, params, data)
            else:
                response = super().send(_url, headers)

            yield response

            if "next" not in response.pagination_links:
                break

            _url = response.pagination_links["next"]["url"]


class PostRequest(Request):
    def __init__(self, path: str = "", headers: object = None):
        super().__init__(HttpMethod.POST, path, headers)


class PutRequest(Request):
    def __init__(self, path: str = "", headers: object = None):
        super().__init__(HttpMethod.PUT, path, headers)


class DeleteRequest(Request):
    def __init__(self, path: str = "", headers: object = None):
        super().__init__(HttpMethod.DELETE, path, headers)
