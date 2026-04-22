import pytest
import logging

from monero import (
    MoneroError, MoneroRpcError, SerializableStruct
)

from utils import BaseTestClass

logger: logging.Logger = logging.getLogger("TestMoneroCommon")


@pytest.mark.unit
class TestMoneroCommon(BaseTestClass):
    """Monero common unit tests."""

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
    @pytest.mark.xfail(raises=TypeError, reason="Serializable struct is an abstract class")
    def test_serializable_struct(self) -> None:
        ser_struct: SerializableStruct = SerializableStruct()
        ser_struct.serialize()
