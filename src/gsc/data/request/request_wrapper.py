import abc
import types
import json
from typing import Any
from enum import Enum
from urllib.parse import urljoin
from requests import request, Response
from gsc.utils import json_serialize
from gsc.constants import DEFAULT_TIMEOUT


class HttpMethod(Enum):
    GET = 1
    POST = 2
    PUT = 3
    PATCH = 4
    DELETE = 5


class Request(abc.ABC):
    def __init__(
        self, method: HttpMethod, path: str, response_model, headers: dict = None
    ):
        self.path = path if path is not None else ""
        self.method = method
        self.headers = headers
        self.response_model = response_model

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

            response = self.send(
                urljoin(obj.host, req_path),
                obj.default_header,
                req_params,
                json_serialize(req_body),
            )
            return self.__convert_to_model(self.response_model, response)

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
            response = request(
                method=self.method.name.upper(),
                url=url,
                headers=req_header,
                params=params,
                data=data,
                timeout=DEFAULT_TIMEOUT,
            )
            response.raise_for_status()
            return response
        except Exception as err:
            raise err

    def __convert_to_model(self, model_cls, response: Any):
        if model_cls is None:
            raise TypeError(f"{model_cls} is not supported.")

        if not isinstance(response, (Response, types.GeneratorType)):
            raise TypeError(f"{type(response)} type is not supported.")

        if isinstance(response, types.GeneratorType):
            return self.__convert_generator(model_cls, response)

        return self.__convert_object(model_cls, response)

    def __convert_object(self, model_cls, response: Response):
        data = json.loads(response.content)

        if isinstance(data, list):
            return [model_cls(**item) for item in data]

        return [model_cls(**data)]

    def __convert_generator(self, model_cls, response: types.GeneratorType):
        for res in response:
            data = json.loads(res.content)

            if isinstance(data, dict):
                yield model_cls(**data)
            elif isinstance(data, list):
                for item in data:
                    yield model_cls(**item)
            else:
                pass


class Api:
    def __init__(self, host: str, default_header: dict = None):
        self.host = host
        self.default_header = default_header


class GetRequest(Request):
    def __init__(self, path: str, response_model, headers: dict = None):
        super().__init__(HttpMethod.GET, path, response_model, headers)


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

            if "next" not in response.links:
                break

            _url = response.links["next"]["url"]


class PostRequest(Request):
    def __init__(self, path: str, response_model, headers: dict = None):
        super().__init__(HttpMethod.POST, path, response_model, headers)


class PutRequest(Request):
    def __init__(self, path: str, response_model, headers: dict = None):
        super().__init__(HttpMethod.PUT, path, response_model, headers)


class DeleteRequest(Request):
    def __init__(self, path: str, response_model, headers: dict = None):
        super().__init__(HttpMethod.DELETE, path, response_model, headers)
