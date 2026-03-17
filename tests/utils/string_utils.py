from abc import ABC
from secrets import token_hex


class StringUtils(ABC):
    """General string utilities"""

    @classmethod
    def get_percentage(cls, n: int, m: int, precision: int = 2) -> str:
        """
        Get percentage in readable format

        :param int n: steps completed.
        :param int m: total steps.
        :param int precision: percentage precision.
        :returns str: percentage in readable format.
        """
        # calculate percentage from steps
        r: float = (n / m)*100
        return cls.get_percentage_float(r, precision)

    @classmethod
    def get_percentage_float(cls, n: float, precision: int = 2) -> str:
        """
        Get percentage in readable format.

        :param float n: percentage value.
        :param int precision: percentage precision.
        :returns str: percentage in readable format.
        """
        # set precision
        return f"{round(n, precision)}%"

    @classmethod
    def get_random_string(cls, n: int = 25) -> str:
        """
        Generate random string.

        :param int n: length of the random string to generate (default `25`).
        :returns str: random string.
        """
        # generate random string
        return token_hex(n)

    @classmethod
    def is_none_or_empty(cls, str_value: str | None) -> bool:
        """
        Checks if string is `None` or empty.

        :param str | None str_value: string value to check.
        :returns bool: `True` if `str_value` is `None` or empty, `False` otherwise.
        """
        return str_value is None or len(str_value) == 0
