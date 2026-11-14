from __future__ import annotations

import logging

import pytest
from monero import MoneroRpcConnection, MoneroRpcPaymentInfo, MoneroVersion

from utils import AssertUtils, BaseTestClass

logger: logging.Logger = logging.getLogger("TestMoneroDaemonModelRpc")


@pytest.mark.unit
class TestMoneroDaemonModelRpc(BaseTestClass):
    """Daemon rpc model unit tests."""

    def test_version_deserialize(self) -> None:
        version: MoneroVersion = MoneroVersion()
        version.number = 65552
        version.is_release = True
        AssertUtils.assert_serialization_integrity(version)

    def test_rpc_payment_info_deserialize(self) -> None:
        info: MoneroRpcPaymentInfo = MoneroRpcPaymentInfo()
        info.credits = 42
        info.top_block_hash = "a" * 64
        AssertUtils.assert_serialization_integrity(info)

    def test_rpc_connection_deserialize(self) -> None:
        connection: MoneroRpcConnection = MoneroRpcConnection("http://127.0.0.1:18081", "user", "pass", "127.0.0.1:9050", "tcp://127.0.0.1:18083", 2, 5000)
        json_str: str = connection.serialize()
        logger.debug(f"Serialized rpc connection: {json_str}")
        restored: MoneroRpcConnection = MoneroRpcConnection.deserialize(json_str)
        assert restored.uri == connection.uri
        assert restored.username == connection.username
        assert restored.password == connection.password
        assert restored.proxy_uri == connection.proxy_uri
        assert restored.zmq_uri == connection.zmq_uri

    def test_rpc_connection_priority_and_timeout_deserialize(self) -> None:
        # to_rapidjson_val() emits "priority" and "timeoutMs" but
        # from_property_tree() never read either back
        connection: MoneroRpcConnection = MoneroRpcConnection("http://127.0.0.1:18081", priority=2, timeout_ms=5000)
        json_str: str = connection.serialize()
        logger.debug(f"Serialized rpc connection: {json_str}")
        assert '"priority"' in json_str and '"timeoutMs"' in json_str
        restored: MoneroRpcConnection = MoneroRpcConnection.deserialize(json_str)
        logger.debug(f"Deserialized rpc connection re-serialized: {restored.serialize()}")
        assert restored.priority == connection.priority
        assert restored.timeout_ms == connection.timeout_ms
