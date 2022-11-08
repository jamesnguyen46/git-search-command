import abc
from dataclasses import dataclass
import jsonpickle


@dataclass
class BaseModel(abc.ABC):
    def __str__(self) -> str:
        return jsonpickle.encode(self.__dict__)

    def to_json_string(self) -> str:
        return jsonpickle.encode(self.__dict__)

    @classmethod
    def from_json(cls, json_str: str):
        attr_dict = jsonpickle.decode(json_str)
        return cls(**attr_dict)
