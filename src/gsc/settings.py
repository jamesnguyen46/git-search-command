from pickle import TRUE
import dotenv
from os import environ as env
from os.path import join, dirname


dotenv_path = join(dirname(__file__), ".env")
env_dict = dotenv.dotenv_values(dotenv_path)


def set(key, value):
    try:
        dotenv.set_key(dotenv_path, key, value)
        return True, None
    except Exception as err:
        return False, err


def value(key):
    return env_dict.get(key)


def values(keys: list):
    return [value(key) for key in keys]
