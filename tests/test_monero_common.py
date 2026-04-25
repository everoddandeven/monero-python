import pytest
import logging

from json import loads

from monero import (
    SerializableStruct, SslOptions,
    MoneroError, MoneroRpcError
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
        SerializableStruct()

    def test_ssl_options(self) -> None:
        ssl_options: SslOptions = SslOptions()
        ssl_options.ssl_allow_any_cert = True
        ssl_options.ssl_allowed_fingerprints = ["fingerprint1", "fingerprint2"]
        ssl_options.ssl_ca_file = "ca_file"
        ssl_options.ssl_certificate_path = "certificate_path"
        ssl_options.ssl_private_key_path = "private_key_path"
        logger.info(f"Testing ssl options: {ssl_options.serialize()}")
        obj: dict[str, str] = loads(ssl_options.serialize())
        assert obj['sslAllowAnyCert'] == ssl_options.ssl_allow_any_cert
        assert obj['sslCaFile'] == ssl_options.ssl_ca_file
        assert obj['sslCertificatePath'] == ssl_options.ssl_certificate_path
        assert obj['sslPrivateKeyPath'] == ssl_options.ssl_private_key_path

        allowed_fingerprints: list[str] = obj['sslAllowedFingerprints'] # type: ignore

        for i, allowed_fingerprint in enumerate(allowed_fingerprints):
            assert allowed_fingerprint == ssl_options.ssl_allowed_fingerprints[i]
