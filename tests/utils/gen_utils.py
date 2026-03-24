from typing import Union, Any, Optional
from abc import ABC
from time import sleep, time
from os import makedirs
from os.path import exists as path_exists


class GenUtils(ABC):
    """General test utilities."""

    @classmethod
    def create_dir_if_not_exists(cls, dir_path: str) -> None:
        """
        Creates a directory if doesn't exists.

        :param str dir_path: path of the directory to create.
        """
        if path_exists(dir_path):
            return

        makedirs(dir_path)

    @classmethod
    def wait_for(cls, milliseconds: int) -> None:
        """
        Waits for specified time.

        :param int milliseconds: milliseconds to wait for.
        """
        sleep(milliseconds / 1000)

    @classmethod
    def is_empty(cls, value: Union[str, list[Any], None]) -> bool:
        return value == ""

    @classmethod
    def test_unsigned_big_integer(cls, num: Any, non_zero: Optional[bool] = None) -> None:
        """
        Test number is a unsigned big integer.

        :param Any num: number to test.
        :param bool | None non_zero: assert number is non zero.
        """
        assert num is not None, "Number is None"
        assert isinstance(num, int), f"Value is not number: {num}"
        assert num >= 0, "Value cannot be negative"
        if non_zero is True:
            assert num > 0, "Number is zero"
        elif non_zero is False:
            assert num == 0, f"Number is not zero: {num}"

    @classmethod
    def current_timestamp(cls) -> int:
        """
        Gets current timestamp in milliseconds.

        :returns int: current timestamp in milliseconds.
        """
        return round(time() * 1000)

    @classmethod
    def current_timestamp_str(cls) -> str:
        """
        Gets current timestamp in milliseconds.

        :returns str: current timestamp in milliseconds.
        """
        return f"{cls.current_timestamp()}"

    @classmethod
    def has_key(cls, key: Optional[str], dictionary: dict[str, Any]) -> bool:
        assert key is not None, "Key is None"
        for k in dictionary:
            if k == key:
                return True
        return False

    @classmethod
    def count_num_instances(cls, instances: list[int]) -> dict[int, int]:
        height_counts: dict[int, int] = {}
        for inst in instances:
            count: Optional[int] = height_counts.get(inst, None)
            height_counts[inst] = 1 if count is None else count + 1
        return height_counts

    @classmethod
    def get_modes(cls, counts: dict[int, int]) -> set[int]:
        modes: set[int] = set()
        max_count: Optional[int] = None
        for cnt in counts.values():
            if max_count is None or cnt > max_count:
                max_count = cnt

        for entry in counts.items():
            if entry[1] == max_count:
                modes.add(entry[0])

        return modes
