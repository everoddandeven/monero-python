from abc import ABC
from secrets import token_hex


class StringUtils(ABC):

    @classmethod
    def get_percentage(cls, n: int, m: int, precision: int = 2) -> str:
        r: float = (n / m)*100
        return cls.get_percentage_float(r, precision)

    @classmethod
    def get_percentage_float(cls, n: float, precision: int = 2) -> str:
        return f"{round(n, precision)}%"

    @classmethod
    def get_random_string(cls, n: int = 25) -> str:
        return token_hex(n)
