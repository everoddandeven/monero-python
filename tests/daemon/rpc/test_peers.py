from __future__ import annotations

import logging

import pytest
from monero import MoneroBan, MoneroDaemonRpc, MoneroPeer

from utils import DaemonUtils, TestUtils as Utils
from .base_test_monero_daemon_rpc import BaseTestMoneroDaemonRpc

logger: logging.Logger = logging.getLogger("TestMoneroDaemonRpcPeers")


@pytest.mark.integration
class TestMoneroDaemonRpcPeers(BaseTestMoneroDaemonRpc):
    """Rpc daemon peers integration tests."""

    # Can get peers with active incoming or outgoing connections
    @pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_get_peers(self, daemon: MoneroDaemonRpc) -> None:
        peers: list[MoneroPeer] = daemon.get_peers()
        assert len(peers) >= 0, "Daemon has no incoming or outgoing peers to test"
        seen: set[tuple[str, int]] = set()
        for peer in peers:
            assert peer.host is not None
            assert peer.port is not None
            peer_key: tuple[str, int] = (peer.host, peer.port)
            assert peer_key not in seen, f"Duplicate peer found: {peer_key}"
            seen.add(peer_key)
            assert peer.is_online, "Expected active peer connection to be online"
            DaemonUtils.test_peer(peer)

    # Can get all known peers which may be online or offline
    @pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_get_known_peers(self, daemon: MoneroDaemonRpc) -> None:
        peers: list[MoneroPeer] = daemon.get_known_peers()
        if Utils.REGTEST:
            assert len(peers) == 0, "Regtest daemon should not have known peers to test"
            logger.warning("Regtest daemon doesn't have known peers to test")
        else:
            assert len(peers) > 0, "Daemon has no known peers to test"

        for peer in peers:
            DaemonUtils.test_known_peer(peer, False)

    # Can get public nodes known to the daemon
    @pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_get_public_peers(self, daemon: MoneroDaemonRpc) -> None:
        peers: list[MoneroPeer] = daemon.get_public_peers()
        if Utils.REGTEST:
            assert len(peers) == 0
        for peer in peers:
            DaemonUtils.test_known_peer(peer, False)

    # Can limit the number of outgoing peers
    @pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_set_outgoing_peer_limit(self, daemon: MoneroDaemonRpc) -> None:
        daemon.set_outgoing_peer_limit(0)
        daemon.set_outgoing_peer_limit(8)
        daemon.set_outgoing_peer_limit(10)

    # Can limit the number of incoming peers
    @pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_set_incoming_peer_limit(self, daemon: MoneroDaemonRpc) -> None:
        daemon.set_incoming_peer_limit(0)
        daemon.set_incoming_peer_limit(8)
        daemon.set_incoming_peer_limit(10)

    # Can get, set, and reset a download bandwidth limit
    @pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    @pytest.mark.flaky(reruns=5, reruns_delay=10, only_rerun=[])
    def test_set_download_bandwidth(self, daemon: MoneroDaemonRpc) -> None:
        init_val: int = daemon.get_download_limit()
        assert init_val > 0
        set_val: int = init_val * 2
        daemon.set_download_limit(set_val)
        assert set_val == daemon.get_download_limit()
        reset_val: int = daemon.reset_download_limit()
        assert init_val == reset_val

        # test invalid limits
        with pytest.raises(Exception) as exc_info:
            daemon.set_download_limit(0)
        assert str(exc_info.value) == "Download limit must be an integer greater than 0"

        assert daemon.get_download_limit() == init_val

    # Can get, set, and reset an upload bandwidth limit
    @pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    @pytest.mark.flaky(reruns=5, reruns_delay=10, only_rerun=[])
    def test_set_upload_bandwidth(self, daemon: MoneroDaemonRpc) -> None:
        init_val: int = daemon.get_upload_limit()
        assert init_val > 0
        set_val: int = init_val * 2
        daemon.set_upload_limit(set_val)
        assert set_val == daemon.get_upload_limit()
        reset_val: int = daemon.reset_upload_limit()
        assert init_val == reset_val

        # test invalid limits
        with pytest.raises(Exception) as exc_info:
            daemon.set_upload_limit(0)
        assert str(exc_info.value) == "Upload limit must be an integer greater than 0"

        assert init_val == daemon.get_upload_limit()

    # Can ban a peer
    @pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_ban_peer(self, daemon: MoneroDaemonRpc) -> None:
        # set ban
        host: str = "192.168.1.51"
        ban: MoneroBan = MoneroBan()
        ban.host = host
        ban.is_banned = True
        ban.seconds = 60
        daemon.set_peer_ban(ban)

        # test ban
        bans: list[MoneroBan] = daemon.get_peer_bans()
        found: bool = False
        for peer_ban in bans:
            DaemonUtils.test_ban(peer_ban)
            if host == peer_ban.host:
                found = True

        assert found, f"Could not find peer ban {host}"

    # Can ban peers
    @pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_ban_peers(self, daemon: MoneroDaemonRpc) -> None:
        # set bans
        addr1: str = "192.168.1.52"
        addr2: str = "192.168.1.53"
        ban1: MoneroBan = MoneroBan()
        ban1.host = addr1
        ban1.is_banned = True
        ban1.seconds = 60
        ban2: MoneroBan = MoneroBan()
        ban2.host = addr2
        ban2.is_banned = True
        ban2.seconds = 60
        bans: list[MoneroBan] = []
        bans.append(ban1)
        bans.append(ban2)
        daemon.set_peer_bans(bans)

        # test bans
        bans = daemon.get_peer_bans()
        found1: bool = False
        found2: bool = False
        for a_ban in bans:
            DaemonUtils.test_ban(a_ban)
            if addr1 == a_ban.host:
                found1 = True
            if addr2 == a_ban.host:
                found2 = True

        assert found1, f"Could not find peer ban1 {addr1}"
        assert found2, f"Could not find peer ban2 {addr2}"

    # Can query the ban status of a single peer
    @pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_get_peer_ban(self, daemon: MoneroDaemonRpc) -> None:
        host: str = "192.168.1.60"
        ban: MoneroBan = MoneroBan()
        ban.host = host
        ban.is_banned = True
        ban.seconds = 60
        daemon.set_peer_ban(ban)

        banned: MoneroBan = daemon.get_peer_ban(host)
        assert banned.is_banned is True
        assert banned.seconds is not None and banned.seconds > 0

        assert daemon.get_peer_ban("192.168.1.61").is_banned is False

        with pytest.raises(Exception) as exc_info:
            daemon.get_peer_ban("")
        assert str(exc_info.value) == "Must provide an address to check the ban status of"
