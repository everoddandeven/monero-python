import sys
from abc import ABC


class OsUtils(ABC):

    @classmethod
    def is_windows(cls) -> bool:
        return sys.platform == 'win32'
