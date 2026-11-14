from __future__ import annotations

import logging

import pytest
from monero import MoneroBan, MoneroConnectionSpan, MoneroConnectionType, MoneroPeer

from utils import AssertUtils, BaseTestClass

logger: logging.Logger = logging.getLogger("TestMoneroDaemonModelPeers")


@pytest.mark.unit
class TestMoneroDaemonModelPeers(BaseTestClass):
    """Daemon peers model unit tests."""

    def test_ban_deserialize(self) -> None:
        ban: MoneroBan = MoneroBan()
        ban.host = "127.0.0.1"
        ban.ip = 2130706433
        ban.is_banned = True
        ban.seconds = 3600
        AssertUtils.assert_serialization_integrity(ban)

    def test_connection_span_deserialize(self) -> None:
        span: MoneroConnectionSpan = MoneroConnectionSpan()
        span.connection_id = "deadbeef"
        span.remote_address = "127.0.0.1:18080"
        span.num_blocks = 10
        span.rate = 100
        span.speed = 200
        span.size = 1024
        span.start_height = 1000
        AssertUtils.assert_serialization_integrity(span)

    def test_peer_deserialize(self) -> None:
        peer: MoneroPeer = MoneroPeer()
        peer.id = "1122334455667788"
        peer.address = "127.0.0.1:18080"
        peer.host = "127.0.0.1"
        peer.port = 18080
        peer.last_seen_timestamp = 1700000000
        peer.pruning_seed = 0
        peer.rpc_port = 18081
        peer.rpc_credits_per_hash = 0
        peer.hash = "a" * 64
        peer.avg_download = 10
        peer.avg_upload = 20
        peer.current_download = 30
        peer.current_upload = 40
        peer.height = 12345
        peer.is_incoming = True
        peer.live_time = 3600
        peer.is_local_ip = False
        peer.is_local_host = False
        peer.num_receives = 5
        peer.num_sends = 6
        peer.receive_idle_time = 7
        peer.send_idle_time = 8
        peer.state = "normal"
        peer.num_support_flags = 1
        # is_online and connection_type are serialized (isOnline/addressType) but
        # monero_peer::from_property_tree() never reads them back, so they are
        # deliberately excluded from this round trip (see test below).
        AssertUtils.assert_serialization_integrity(peer)

    def test_peer_is_online_deserialize(self) -> None:
        peer: MoneroPeer = MoneroPeer()
        peer.is_online = True
        json_str: str = peer.serialize()
        logger.debug(f"Serialized peer: {json_str}")
        assert "isOnline" in json_str
        restored: MoneroPeer = MoneroPeer.deserialize(json_str)
        logger.debug(f"Deserialized peer re-serialized: {restored.serialize()}")
        assert restored.is_online == peer.is_online

    def test_peer_connection_serialization_integrity(self) -> None:
        peer: MoneroPeer = MoneroPeer()
        peer.connection_type = MoneroConnectionType.IPV6
        json_str: str = peer.serialize()
        logger.debug(f"Serialized peer: {json_str}")
        assert "addressType" in json_str
        restored: MoneroPeer = MoneroPeer.deserialize(json_str)
        logger.debug(f"Deserialized peer re-serialized: {restored.serialize()}")
        assert restored.connection_type == peer.connection_type

    def test_peer_connection_type_deserialize(self) -> None:
        # connection_type is likewise never serialized by to_rapidjson_val(), so it
        # can only be exercised by handing from_property_tree a raw "addressType" field
        for value, expected in [
            (0, MoneroConnectionType.INVALID),
            (1, MoneroConnectionType.IPV4),
            (2, MoneroConnectionType.IPV6),
            (3, MoneroConnectionType.TOR),
            (4, MoneroConnectionType.I2P),
        ]:
            peer: MoneroPeer = MoneroPeer.deserialize(f'{{"addressType":{value}}}')
            assert peer.connection_type == expected

    def test_peer_connection_type_invalid(self) -> None:
        # TODO throws RuntimeError rather than MoneroError
        with pytest.raises(RuntimeError, match="Invalid RPC peer type"):
            MoneroPeer.deserialize('{"addressType":5}')
