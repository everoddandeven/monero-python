from abc import ABC

from .monero_test_utils import MoneroTestUtils


class PrintHeight(ABC):

    @classmethod
    def print(cls) -> None:
        daemon = MoneroTestUtils.get_daemon_rpc()
        print(f"Height: {daemon.get_height()}")
