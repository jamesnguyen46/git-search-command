from functools import wraps
from typing import Any
from enum import Enum
import abc
import threading
import json
import types
from urllib.parse import urljoin
from requests.adapters import HTTPAdapter
from urllib3.util import Retry
from urllib3.exceptions import InsecureRequestWarning
import requests


DEFAULT_TIMEOUT = 20


class HttpMethod(Enum):
    GET = 1
    POST = 2
    PUT = 3
    PATCH = 4
    DELETE = 5


class RequestDecorator(abc.ABC):
    # pylint: disable=R0913
    def __init__(
        self,
        method: HttpMethod,
        path: str,
        response_model,
        headers: dict = None,
        timeout: int = None,
    ):
        self.path = path if path is not None else ""
        self.method = method
        self.headers = headers
        self.response_model = response_model
        self.timeout = timeout or DEFAULT_TIMEOUT
        self.__lock = None
        self.__object = None

    def __call__(self, func):
        def json_serialize(obj):
            try:
                return json.dumps(obj, ensure_ascii=False).encode("utf-8")
            except TypeError:
                return json.dumps(
                    obj, default=lambda o: o.__dict__, ensure_ascii=False
                ).encode("utf-8")

        @wraps(func)
        def wrapper(obj, *args, **kwargs):
            if not isinstance(obj, Api):
                raise TypeError("Object type is not supported.")

            self.__object = obj
            path_dict, param_dict = func(obj, *args, **kwargs)

            req_path = self.path
            if path_dict is not None:
                req_path = req_path.format_map(path_dict)

            body_required = self.method not in (HttpMethod.GET, HttpMethod.DELETE)
            req_body = param_dict if body_required else None
            req_params = param_dict if not body_required else None

            response = self.send(
                urljoin(obj.host, req_path),
                obj.default_header,
                req_params,
                json_serialize(req_body),
                obj.ssl_verify,
            )
            return self.__convert_to_model(self.response_model, response)

        return wrapper

    def send(
        self,
        url: str,
        headers: dict = None,
        params: dict = None,
        data: dict = None,
        ssl_verify=True,
    ):
        req_header = self.headers
        if req_header is not None and headers is not None:
            req_header.update(headers)
        elif headers is not None:
            req_header = headers
        else:
            pass

        try:
            retries = Retry(
                total=3,
                backoff_factor=10,
                respect_retry_after_header=True,
                status_forcelist=[429, 403],
            )

            if not ssl_verify:
                # Suppress only the single warning from urllib3 needed.
                requests.packages.urllib3.disable_warnings(
                    category=InsecureRequestWarning
                )

            session = requests.Session()
            session.mount(self.__object.host, HTTPAdapter(max_retries=retries))
            session.verify = ssl_verify
            response = session.request(
                method=self.method.name.upper(),
                url=url,
                headers=req_header,
                params=params,
                data=data,
                timeout=self.timeout,
                hooks={
                    "response": self.__debug_request if self.__object.is_debug else None
                },
            )
            response.raise_for_status()
            return response
        except Exception as err:
            raise err
        finally:
            session.close()

    def __convert_to_model(self, model_cls, response: Any):
        if model_cls is None:
            raise TypeError(f"{model_cls} is not supported.")

        if not isinstance(response, (requests.Response, types.GeneratorType)):
            raise TypeError(f"{type(response)} type is not supported.")

        if isinstance(response, types.GeneratorType):
            return self.__convert_generator(model_cls, response)

        return self.__convert_object(model_cls, response)

    def __convert_object(self, model_cls, response: requests.Response):
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

    def __debug_request(self, response: requests.Response, *_, **__):
        if not self.__lock:
            self.__lock = threading.RLock()
        thread = threading.Thread(
            target=self.__print_thread_task, args=(self.__lock, response)
        )
        thread.start()
        thread.join()

    def __print_thread_task(self, lock, response: requests.Response):
        lock.acquire()
        print(f"Request  --> {response.request.method} {response.request.url}")
        print(
            f"Response <-- [{response.elapsed}] {response.status_code} {response.reason}\n"
        )
        lock.release()


class Api:
    def __init__(
        self, host: str, default_header: dict = None, ssl_verify=True, is_debug=False
    ):
        self.host = host
        self.default_header = default_header
        self.ssl_verify = ssl_verify
        self.is_debug = is_debug


class GetRequest(RequestDecorator):
    def __init__(
        self, path: str, response_model, headers: dict = None, timeout: int = None
    ):
        super().__init__(HttpMethod.GET, path, response_model, headers, timeout)


class GetRequestPagination(GetRequest):
    # pylint: disable=too-many-arguments
    def send(
        self,
        url: str,
        headers: dict = None,
        params: dict = None,
        data: dict = None,
        ssl_verify=True,
    ):
        _url = url
        while True:
            if _url == url:
                response = super().send(url, headers, params, data, ssl_verify)
            else:
                response = super().send(_url, headers, ssl_verify=ssl_verify)

            yield response

            if "next" not in response.links:
                break

            _url = response.links["next"]["url"]


class PostRequest(RequestDecorator):
    def __init__(
        self, path: str, response_model, headers: dict = None, timeout: int = None
    ):
        super().__init__(HttpMethod.POST, path, response_model, headers, timeout)


class PutRequest(RequestDecorator):
    def __init__(
        self, path: str, response_model, headers: dict = None, timeout: int = None
    ):
        super().__init__(HttpMethod.PUT, path, response_model, headers, timeout)


class DeleteRequest(RequestDecorator):
    def __init__(
        self, path: str, response_model, headers: dict = None, timeout: int = None
    ):
        super().__init__(HttpMethod.DELETE, path, response_model, headers, timeout)


# Alias
# pylint: disable=C0103
get_request = GetRequest
get_request_pagination = GetRequestPagination
post_request = PostRequest
put_request = PutRequest
delete_request = DeleteRequest
