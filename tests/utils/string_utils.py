from abc import ABC


class StringUtils(ABC):

    @classmethod
    def get_percentage(cls, n: int, m: int, precision: int = 2) -> str:
        r: float = (n / m)*100
        return f"{round(r, precision)}%"
