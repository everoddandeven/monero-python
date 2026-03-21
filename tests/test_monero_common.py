import pytest
import logging

from monero import (
    MoneroError, MoneroRpcError, SerializableStruct
)

logger: logging.Logger = logging.getLogger("TestMoneroCommon")


@pytest.mark.unit
class TestMoneroCommon:
    """Monero common unit tests"""

    @pytest.fixture(autouse=True)
    def setup_and_teardown(self, request: pytest.FixtureRequest):
        logger.info(f"Before {request.node.name}") # type: ignore
        yield
        logger.info(f"After {request.node.name}") # type: ignore

    # test monero error inheritance
    def test_monero_error(self) -> None:
        monero_err: MoneroError = MoneroError("Test monero error")
        monero_rpc_err: MoneroRpcError = MoneroRpcError("Test monero rpc error")

        # test monero error
        assert isinstance(monero_err, Exception)
        assert str(monero_err) == "Test monero error"

        # test monero rpc error
        assert isinstance(monero_rpc_err, Exception)
        assert isinstance(monero_rpc_err, MoneroError)
        assert str(monero_rpc_err) == "Test monero rpc error"
        assert monero_rpc_err.code == -1

    # test serializable struct
    @pytest.mark.not_implemented
    def test_serializable_struct(self) -> None:
        ser_struct: SerializableStruct = SerializableStruct()
        ser_struct.serialize()
