import pytest
import logging

from monero import (
    SerializableStruct, SslOptions,
    MoneroError, MoneroRpcError
)

from utils import BaseTestClass, AssertUtils

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
    def test_serializable_struct(self) -> None:
        # SerializableStruct is abstract and cannot be instantiated directly
        with pytest.raises(TypeError):
            SerializableStruct()

    # test ssl options serialization integrity
    def test_ssl_options(self) -> None:
        # create ssl_options objects and populate properties
        ssl_options: SslOptions = SslOptions()
        ssl_options.ssl_allow_any_cert = True
        ssl_options.ssl_allowed_fingerprints = ["fingerprint1", "fingerprint2"]
        ssl_options.ssl_ca_file = "ca_file"
        ssl_options.ssl_certificate_path = "certificate_path"
        ssl_options.ssl_private_key_path = "private_key_path"
        AssertUtils.assert_serialization_integrity(ssl_options)
