import abc
from os.path import join, dirname
import dotenv
from gsc.entities.base_model import BaseModel


class Env(BaseModel):
    def __init__(self, **kwargs) -> None:
        self.name = kwargs.get("name")
        self.host_name = kwargs.get("host_name")
        self.private_token = kwargs.get("private_token")


class BaseConfig(abc.ABC):
    def __init__(self, file_name: str) -> None:
        self._config_path = join(dirname(__file__), f"{file_name.lower()}.env")
        self.__reload_keys()

    def set_key(self, key: str, value: str):
        try:
            dotenv.set_key(self._config_path, key, value)
            self.__reload_keys()
            return True, None
        except Exception as err:
            return False, err

    def get_key(self, key: str) -> str:
        return self._config_dict.get(key)

    def remove_key(self, key: str):
        dotenv.unset_key(self._config_path, key)
        self.__reload_keys()

    def get_all(self) -> dict:
        return self._config_dict

    def has_key(self, key: str):
        return key in self._config_dict

    def __reload_keys(self):
        self._config_dict = dotenv.dotenv_values(self._config_path)


class AppConfig(BaseConfig):
    DEBUG_FLAG = "DEBUG"

    def __init__(self, _: str = None) -> None:
        super().__init__(type(self).__name__)

    def set_debug(self, debug):
        super().set_key(self.DEBUG_FLAG, str(debug))

    def is_debug(self):
        return super().get_key(self.DEBUG_FLAG) == "True"


class EnvConfig(BaseConfig):
    DEFAULT_ENV = "DEFAULT_ENV"
    SESSION_ENV = "SESSION_ENV"

    def __init__(self, _=None) -> None:
        super().__init__(type(self).__name__)
        self._exclude_keys = [self.DEFAULT_ENV, self.SESSION_ENV]
        self._all_envs = None
        self.__reload_envs()

    def set_env(self, env: Env):
        # Automatically set new env as default if there is no any env before
        if len(self._all_envs) == 0:
            super().set_key(self.DEFAULT_ENV, env.name)

        super().set_key(env.name, env.to_json_string())
        self.__reload_envs()
        return True, None

    def get_env(self, name: str) -> Env:
        str_value = super().get_key(name)
        if not str_value:
            return None

        return Env.from_json(str_value)

    def get_all_envs(self) -> list:
        return self._all_envs

    def remove_env(self, name: str):
        if not self.is_env_existed(name):
            return

        super().remove_key(name)
        self.__reload_envs()

        # Re-select the default env. If there is any env existed, select the top env.
        list_env_empty = len(self._all_envs) == 0
        if self.get_default_env() is None and not list_env_empty:
            self.set_default_env(self._all_envs[0].name)
        else:
            self.remove_default_env()

    def is_env_existed(self, name: str) -> bool:
        return self.has_key(name)

    def get_default_env(self) -> Env:
        default_env_key = super().get_key(self.DEFAULT_ENV)
        return self.get_env(default_env_key)

    def set_default_env(self, name: str):
        if not self.is_env_existed(name):
            return False, ValueError("Value is not existed.")

        return super().set_key(self.DEFAULT_ENV, name)

    def remove_default_env(self):
        return super().remove_key(self.DEFAULT_ENV)

    def is_default_env(self, name: str):
        return name == super().get_key(self.DEFAULT_ENV)

    def get_session_env(self) -> Env:
        session_env_key = super().get_key(self.SESSION_ENV)
        return self.get_env(session_env_key)

    def set_session_env(self, name: str):
        if not self.is_env_existed(name):
            return False, ValueError("Value is not existed.")

        return super().set_key(self.SESSION_ENV, name)

    def __reload_envs(self):
        self._all_envs = [
            Env.from_json(value)
            for key, value in super().get_all().items()
            if (key not in self._exclude_keys) and value
        ]


class GitLabConfig(EnvConfig):
    pass


class GitHubConfig(EnvConfig):
    pass
