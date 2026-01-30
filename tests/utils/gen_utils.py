from typing import Union, Any
from abc import ABC
from time import sleep, time
from os import makedirs
from os.path import exists as path_exists



class GenUtils(ABC):

    @classmethod
    def create_dir_if_not_exists(cls, dir_path: str) -> None:
        if path_exists(dir_path):
            return

        makedirs(dir_path)

    @classmethod
    def wait_for(cls, milliseconds: int):
        sleep(milliseconds / 1000)

    @classmethod
    def is_empty(cls, value: Union[str, list[Any], None]) -> bool:
        return value == ""

    @classmethod
    def test_unsigned_big_integer(cls, value: Any, bool_val: bool = False):
        if not isinstance(value, int):
            raise Exception(f"Value is not number: {value}")

        if value < 0:
            raise Exception("Value cannot be negative")

    @classmethod
    def current_timestamp(cls) -> int:
        return round(time() * 1000)

    @classmethod
    def current_timestamp_str(cls) -> str:
        return f"{cls.current_timestamp()}"

