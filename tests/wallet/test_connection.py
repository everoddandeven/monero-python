from __future__ import annotations

import logging

import pytest
from monero import MoneroRpcConnection, MoneroWallet, MoneroWalletConfig, MoneroWalletRpc
from typing_extensions import override

from utils import AssertUtils, TestUtils, TestUtils as Utils, WalletErrorUtils
from .base_test_monero_wallet import BaseTestMoneroWallet
from .wallet_support import FullWalletSupport, RpcWalletSupport, KeysWalletSupport

logger: logging.Logger = logging.getLogger("TestMoneroWalletConnection")


class BaseTestMoneroWalletConnection(BaseTestMoneroWallet):
    """Common wallet connection tests."""

    # Can get the daemon's max peer height
    @pytest.mark.skipif(TestUtils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_get_daemon_max_peer_height(self, wallet: MoneroWallet) -> None:
        height: int = wallet.get_daemon_max_peer_height()
        assert height > 0

    # Can get the daemon's height
    @pytest.mark.skipif(TestUtils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_get_daemon_height(self, wallet: MoneroWallet) -> None:
        assert wallet.is_connected_to_daemon(), "Wallet is not connected to daemon"
        daemon_height: int = wallet.get_daemon_height()
        assert daemon_height > 0

    # Can set the daemon connection
    @pytest.mark.skipif(TestUtils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_set_daemon_connection(self) -> None:
        # create random wallet with default daemon connection
        config: MoneroWalletConfig = MoneroWalletConfig()
        wallet: MoneroWallet = self._create_wallet(config)
        daemon_rpc_uri: str = self.get_daemon_rpc_uri()
        connection: MoneroRpcConnection = MoneroRpcConnection(
            daemon_rpc_uri, TestUtils.DAEMON_RPC_USERNAME, TestUtils.DAEMON_RPC_PASSWORD
        )
        AssertUtils.assert_equals(connection, wallet.get_daemon_connection())
        assert wallet.is_connected_to_daemon() # uses default localhost connection

        # set empty server uri
        wallet.set_daemon_connection("")
        assert wallet.get_daemon_connection() is None
        assert wallet.is_connected_to_daemon() is False

        # set offline server uri
        wallet.set_daemon_connection(TestUtils.OFFLINE_SERVER_URI)
        connection = MoneroRpcConnection(TestUtils.OFFLINE_SERVER_URI, "", "")
        AssertUtils.assert_equals(connection, wallet.get_daemon_connection())
        assert wallet.is_connected_to_daemon() is False

        # set daemon with wrong credentials
        wallet.set_daemon_connection(daemon_rpc_uri, "wronguser", "wrongpass")
        connection = MoneroRpcConnection(daemon_rpc_uri, "wronguser", "wrongpass")
        AssertUtils.assert_equals(connection, wallet.get_daemon_connection())
        if "" == TestUtils.DAEMON_RPC_USERNAME:
            # TODO: monerod without authentication works with bad credentials?
            assert wallet.is_connected_to_daemon()
        else:
            assert wallet.is_connected_to_daemon() is False

        # set daemon with authentication
        wallet.set_daemon_connection(
            daemon_rpc_uri, TestUtils.DAEMON_RPC_USERNAME, TestUtils.DAEMON_RPC_PASSWORD
        )
        connection = MoneroRpcConnection(
            daemon_rpc_uri, TestUtils.DAEMON_RPC_USERNAME, TestUtils.DAEMON_RPC_PASSWORD
        )
        AssertUtils.assert_equals(connection, wallet.get_daemon_connection())
        assert wallet.is_connected_to_daemon()

        # nullify daemon connection
        wallet.set_daemon_connection(None)
        assert wallet.get_daemon_connection() is None
        wallet.set_daemon_connection(daemon_rpc_uri)
        connection = MoneroRpcConnection(daemon_rpc_uri)
        AssertUtils.assert_equals(connection, wallet.get_daemon_connection())
        wallet.set_daemon_connection(None)
        assert wallet.get_daemon_connection() is None

        # set daemon uri to non-daemon
        if not TestUtils.IN_CONTAINER: # TODO sometimes this fails in container...
            wallet.set_daemon_connection("www.getmonero.org")
            connection = MoneroRpcConnection("www.getmonero.org")
            AssertUtils.assert_equals(connection, wallet.get_daemon_connection())
            assert wallet.is_connected_to_daemon() is False

        # set daemon to invalid uri
        wallet.set_daemon_connection("abc123")
        assert wallet.is_connected_to_daemon() is False

        # attempt to sync
        try:
            with pytest.raises(Exception, match="Wallet is not connected to daemon"):
                wallet.sync()
        finally:
            self._close_wallet(wallet)


@pytest.mark.integration
class TestMoneroWalletFullConnection(FullWalletSupport, BaseTestMoneroWalletConnection):
    """Full wallet connection integration tests."""


@pytest.mark.integration
class TestMoneroWalletRpcConnection(RpcWalletSupport, BaseTestMoneroWalletConnection):
    """Rpc wallet connection integration tests."""

    @pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_offline_wallet(self) -> None:
        offline_wallet: MoneroWalletRpc = MoneroWalletRpc(Utils.OFFLINE_SERVER_URI, Utils.WALLET_RPC_USERNAME, Utils.WALLET_PASSWORD)
        with pytest.raises(Exception) as exc_info:
            offline_wallet.is_view_only()
        WalletErrorUtils.test_wallet_is_not_connected_error(exc_info.value)

    @pytest.mark.not_supported
    @override
    def test_get_daemon_max_peer_height(self, wallet: MoneroWallet) -> None:
        return super().test_get_daemon_max_peer_height(wallet)

    @pytest.mark.not_supported
    @override
    def test_get_daemon_height(self, wallet: MoneroWallet) -> None:
        return super().test_get_daemon_height(wallet)


@pytest.mark.unit
class TestMoneroWalletKeysConnection(KeysWalletSupport, BaseTestMoneroWalletConnection):
    """Keys-only wallet connection unit tests."""

    @pytest.mark.not_supported
    @override
    def test_get_daemon_height(self, wallet: MoneroWallet) -> None:
        return super().test_get_daemon_height(wallet)

    @pytest.mark.not_supported
    @override
    def test_get_daemon_max_peer_height(self, wallet: MoneroWallet) -> None:
        return super().test_get_daemon_max_peer_height(wallet)

    @pytest.mark.not_supported
    @override
    def test_set_daemon_connection(self) -> None:
        return super().test_set_daemon_connection()
