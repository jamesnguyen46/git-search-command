import types
import json
from typing import Any
from gsc.request.request_wrapper import Response


class BaseRepository:
    def object_mapping(self, model_cls, response: Any):
        if model_cls is None:
            raise TypeError(f"{model_cls} is not supported.")

        if not isinstance(response, (Response, types.GeneratorType)):
            raise TypeError(f"{type(response)} type is not supported.")

        if isinstance(response, types.GeneratorType):
            return self.__handle_response_generator(model_cls, response)

        return self.__handle_response_object(model_cls, response)

    def __handle_response_object(self, model_cls, response: Response):
        data = json.loads(response.binary)

        if isinstance(data, list):
            return [model_cls(**item) for item in data]

        return [model_cls(**data)]

    def __handle_response_generator(self, model_cls, response: types.GeneratorType):
        for res in response:
            data = json.loads(res.binary)

            if isinstance(data, dict):
                yield model_cls(**data)
            elif isinstance(data, list):
                for item in data:
                    yield model_cls(**item)
            else:
                pass
