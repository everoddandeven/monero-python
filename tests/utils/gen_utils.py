from typing import Union, Any, Optional
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
    def test_unsigned_big_integer(cls, num: Any, non_zero: Optional[bool] = None):
        assert num is not None, "Number is None"
        assert isinstance(num, int), f"Value is not number: {num}"
        assert num >= 0, "Value cannot be negative"
        if non_zero is True:
            assert num > 0, "Number is zero"
        elif non_zero is False:
            assert num == 0, f"Number is not zero: {num}"

    @classmethod
    def current_timestamp(cls) -> int:
        return round(time() * 1000)

    @classmethod
    def current_timestamp_str(cls) -> str:
        return f"{cls.current_timestamp()}"

    @classmethod
    def has_key(cls, key: Optional[str], dictionary: dict[str, Any]) -> bool:
        assert key is not None, "Key is None"
        for k in dictionary:
            if k == key:
                return True
        return False
