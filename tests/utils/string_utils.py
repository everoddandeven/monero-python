from abc import ABC
from secrets import token_hex


class StringUtils(ABC):
    """Strin utilities"""

    @classmethod
    def get_percentage(cls, n: int, m: int, precision: int = 2) -> str:
        """Get percentage in readable format"""
        r: float = (n / m)*100
        return cls.get_percentage_float(r, precision)

    @classmethod
    def get_percentage_float(cls, n: float, precision: int = 2) -> str:
        """Get percentage in readable format"""
        return f"{round(n, precision)}%"

    @classmethod
    def get_random_string(cls, n: int = 25) -> str:
        """Generate random string"""
        return token_hex(n)
