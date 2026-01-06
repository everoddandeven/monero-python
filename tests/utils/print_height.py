import logging
from abc import ABC

from .test_utils import TestUtils

logger: logging.Logger = logging.getLogger(__name__)


class PrintHeight(ABC):

    @classmethod
    def print(cls) -> None:
        daemon = TestUtils.get_daemon_rpc()
        logging.info(f"Height: {daemon.get_height()}")
