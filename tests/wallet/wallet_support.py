from __future__ import annotations

import logging
from typing import Optional

import pytest
from monero import (
    MoneroAccount,
    MoneroDaemon,
    MoneroDaemonRpc,
    MoneroNetworkType,
    MoneroRpcConnection,
    MoneroTxQuery,
    MoneroWallet,
    MoneroWalletConfig,
    MoneroWalletFull,
    MoneroWalletKeys,
    MoneroWalletLight,
    MoneroWalletRpc,
)
from typing_extensions import override

from utils import BlockchainUtils, MoneroDaemonLws, StringUtils, TestUtils as Utils, WalletType
from .base_test_monero_wallet import BaseTestMoneroWallet

logger: logging.Logger = logging.getLogger("TestMoneroWallet")


class FullWalletSupport(BaseTestMoneroWallet):
    """What the full wallet tests do differently from the common ones."""

    @classmethod
    @override
    def get_wallet_type(cls) -> WalletType:
        return WalletType.FULL

    @pytest.fixture(scope="class")
    @classmethod
    @override
    def wallet(cls) -> MoneroWalletFull:
        """Test full wallet instance"""
        return Utils.get_wallet_full()

    @override
    def after_all(self) -> None:
        super().after_all()
        Utils.WALLET_FULL_TESTS_RUN = True

    @override
    def _create_wallet(self, config: Optional[MoneroWalletConfig], start_syncing: bool = True) -> MoneroWalletFull:
        # assign defaults
        if config is None:
            config = MoneroWalletConfig()
        random: bool = self.is_random_wallet_config(config)
        if config.path is None:
            config.path = Utils.TEST_WALLETS_DIR + "/" + StringUtils.get_random_string()
        if config.password is None:
            config.password = Utils.WALLET_PASSWORD
        if config.network_type is None:
            config.network_type = Utils.NETWORK_TYPE
        if config.server is None:
            config.server = Utils.get_daemon_rpc_connection()
        if config.restore_height is None and not random:
            config.restore_height = 0

        config.regtest = config.network_type == MoneroNetworkType.MAINNET and Utils.REGTEST

        # create wallet
        wallet: MoneroWalletFull = MoneroWalletFull.create_wallet(config)
        if not random:
            assert config.restore_height == wallet.get_restore_height()
        if start_syncing is not False and wallet.is_connected_to_daemon():
            wallet.start_syncing(Utils.SYNC_PERIOD_IN_MS)
        return wallet

    @override
    def _open_wallet(self, config: Optional[MoneroWalletConfig], start_syncing: bool = True) -> MoneroWalletFull:
        # assign defaults
        if config is None:
            config = MoneroWalletConfig()
        if config.password is None:
            config.password = Utils.WALLET_PASSWORD
        if config.network_type is None:
            config.network_type = Utils.NETWORK_TYPE
        if config.server is None:
            config.server = Utils.get_daemon_rpc_connection()

        # open wallet
        assert config.network_type is not None
        assert config.path is not None

        wallet: MoneroWalletFull = MoneroWalletFull.open_wallet(config.path, config.password, config.network_type)
        wallet.set_daemon_connection(config.server)
        if start_syncing is not False and wallet.is_connected_to_daemon():
            wallet.start_syncing(Utils.SYNC_PERIOD_IN_MS)
        return wallet

    @override
    def _close_wallet(self, wallet: MoneroWallet, save: bool = False) -> None:
        wallet.close(save)

    @override
    def _get_seed_languages(self) -> list[str]:
        return self.get_test_wallet().get_seed_languages()

    @override
    @classmethod
    def get_test_wallet(cls) -> MoneroWalletFull:
        return super().get_test_wallet() # type: ignore


class RpcWalletSupport(BaseTestMoneroWallet):
    """What the rpc wallet tests do differently from the common ones."""

    @classmethod
    @override
    def get_wallet_type(cls) -> WalletType:
        return WalletType.RPC

    @pytest.fixture(scope="class")
    @classmethod
    @override
    def wallet(cls) -> MoneroWalletRpc:
        """Test rpc wallet instance."""
        return cls.get_test_wallet()

    @classmethod
    @override
    def get_test_wallet(cls) -> MoneroWalletRpc:
        return super().get_test_wallet() # type: ignore

    @override
    def _open_wallet(self, config: MoneroWalletConfig | None) -> MoneroWalletRpc:
        return Utils.open_wallet_rpc(config)

    @override
    def _create_wallet(self, config: MoneroWalletConfig) -> MoneroWalletRpc:
        return Utils.create_wallet_rpc(config)

    @override
    def _close_wallet(self, wallet: MoneroWallet, save: bool = False) -> None:
        wallet.close(save)
        Utils.free_wallet_rpc_resource(wallet)

    @override
    def _get_seed_languages(self) -> list[str]:
        return self.get_test_wallet().get_seed_languages()

    @override
    def before_all(self) -> None:
        super().before_all()

    @override
    def after_all(self) -> None:
        super().after_all()
        Utils.free_wallet_rpc_resources()

    @override
    def before_each(self, request: pytest.FixtureRequest) -> None:
        super().before_each(request)
        # The server has the same keys as the full wallet, and what that one sends and flushes from the pool (test_prove_unrelayed_txs) it
        # keeps as pending: 500 seconds after, at any test, it marks it failed and sets its inputs as unspent, even when another tx spent
        # them. The daemon says which outputs are spent (the ones spent in the pool too), so a test never starts with the wrong ones.
        wallet: MoneroWalletRpc = self.get_test_wallet()
        if not wallet.is_closed():
            wallet.rescan_spent()

    @override
    def after_each(self, request: pytest.FixtureRequest) -> None:
        super().after_each(request)
        Utils.free_wallet_rpc_resources()

    @override
    def get_daemon_rpc_uri(self) -> str:
        return Utils.DAEMON_RPC_URI if not Utils.IN_CONTAINER else Utils.CONTAINER_DAEMON_RPC_URI


class KeysWalletSupport(BaseTestMoneroWallet):
    """What the keys-only wallet tests do differently from the common ones."""

    _account_indices: list[int] = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

    _subaddress_indices: list[int] = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

    @pytest.fixture(scope="class")
    @classmethod
    @override
    def wallet(cls) -> MoneroWalletKeys:
        """Test keys wallet instance"""
        return Utils.get_wallet_keys()

    @pytest.fixture(scope="class")
    @classmethod
    @override
    def daemon(cls) -> MoneroDaemonRpc:
        return MoneroDaemon() # type: ignore

    @classmethod
    @override
    def get_wallet_type(cls) -> WalletType:
        return WalletType.KEYS

    @override
    def after_all(self) -> None:
        logger.info(f"Teardown test class {type(self).__name__}")

    @override
    def before_each(self, request: pytest.FixtureRequest) -> None:
        logger.info(f"Before {request.node.name}")

    @override
    def after_each(self, request: pytest.FixtureRequest) -> None:
        logger.info(self.after_message(request))

    @classmethod
    @override
    def is_random_wallet_config(cls, config: Optional[MoneroWalletConfig]) -> bool:
        assert config is not None
        return super().is_random_wallet_config(config) and config.private_spend_key is None

    @override
    def _create_wallet(self, config: Optional[MoneroWalletConfig]) -> MoneroWalletKeys:
        # assign defaults
        if config is None:
            config = MoneroWalletConfig()

        random: bool = self.is_random_wallet_config(config)
        if config.network_type is None:
            config.network_type = Utils.NETWORK_TYPE

        # create wallet
        if random:
            wallet: MoneroWalletKeys = MoneroWalletKeys.create_wallet_random(config)
        elif config.seed is not None and config.seed != "":
            wallet = MoneroWalletKeys.create_wallet_from_seed(config)
        elif config.primary_address is not None and config.private_view_key is not None:
            wallet = MoneroWalletKeys.create_wallet_from_keys(config)
        elif config.primary_address is not None and config.private_spend_key is not None:
            wallet = MoneroWalletKeys.create_wallet_from_keys(config)
        else:
            raise Exception("Invalid configuration")

        return wallet

    @override
    def _open_wallet(self, config: Optional[MoneroWalletConfig]) -> MoneroWallet:
        raise NotImplementedError("TestMoneroWalletKeys._open_wallet(): not supported")

    @override
    def _close_wallet(self, wallet: MoneroWallet, save: bool = False) -> None:
        # a keys-only wallet has nothing to persist, so `save` is ignored
        wallet.close()

    @override
    def _get_seed_languages(self) -> list[str]:
        return self.get_test_wallet().get_seed_languages()

    @classmethod
    @override
    def get_test_wallet(cls) -> MoneroWalletKeys:
        return super().get_test_wallet() # type: ignore

    def _get_test_accounts(self, wallet: MoneroWallet, include_subaddresses: bool = False) -> list[MoneroAccount]:
        account_indices: list[int] = self._account_indices
        subaddress_indices: list[int] = self._subaddress_indices
        accounts: list[MoneroAccount] = []
        for account_idx in account_indices:
            account: MoneroAccount = wallet.get_account(account_idx)

            if include_subaddresses:
                account.subaddresses = wallet.get_subaddresses(account_idx, subaddress_indices)

            accounts.append(account)

        return accounts


class LightWalletSupport(BaseTestMoneroWallet):
    """What the light wallet tests do differently from the common ones."""

    @classmethod
    @override
    def get_wallet_type(cls) -> WalletType:
        return WalletType.LIGHT

    def _create_open_wallet(self, config: Optional[MoneroWalletConfig], create: bool = True, start_syncing: bool = True) -> MoneroWalletLight:
        """Create or open a light wallet."""
        # assign defaults
        if config is None:
            config = MoneroWalletConfig()
        if config.network_type is None:
            config.network_type = Utils.NETWORK_TYPE

        wallet: MoneroWalletLight
        rpc: MoneroRpcConnection = Utils.get_daemon_lws_connection()
        logger.info(f"create: {create}, config: {config.serialize()}")
        if create and not MoneroWalletLight.wallet_exists(config, rpc):
            # create wallet
            logger.info("creating wallet")
            wallet = MoneroWalletLight.create_wallet(config, rpc)
            logger.info(f"Created wallet {wallet.get_primary_address()}")
        else:
            # open wallet
            if config.restore_height is not None:
                # A restore height asks lws to scan the account again from there (an import request), and the account of an existing
                # wallet is, for the test of a scan, the account that all the tests share: lws forgets what it scanned of it, and it does not
                # start again until a block arrives. On regtest at a high difficulty that is minutes, and the tests that follow see a wallet
                # without txs.
                logger.info(f"opening wallet without its restore height {config.restore_height}, lws would scan it again")
                config = config.copy()
                config.restore_height = None
            logger.info("opening wallet")
            wallet = MoneroWalletLight.open_wallet(config, rpc)

        if start_syncing and wallet.is_connected_to_daemon():
            wallet.sync()
            wallet.start_syncing(Utils.SYNC_PERIOD_IN_MS)

        # TODO ensure wallet is synced with the daemon

        return wallet

    _unconfirmable_hashes: set[str] = set()
    """Hashes of the txs that stayed pending after some blocks, such as the ones that were created and never relayed: the tests do not wait for them."""

    def _wait_for_pending_txs(self, wallet: MoneroWalletLight, max_blocks: int = 5) -> None:
        """Mine until lws and the light wallet report as confirmed the txs that the wallet created.

        lws does not report the txs of the pool, so the light wallet keeps the ones that it creates as pending until lws reports them in a
        block. A test that sends and does not mine leaves them, and the next ones would see unconfirmed txs, with a received timestamp, and
        outputs that lws does not know yet. The blocks are generated at once on regtest: lws needs time to scan them, and then the wallet to sync.

        :param MoneroWalletLight wallet: light wallet to wait for.
        :param int max_blocks: number of blocks to mine at most, the txs that are still pending after them are not waited for again.
        """
        query: MoneroTxQuery = MoneroTxQuery()
        query.is_confirmed = False
        pending: set[str] = set()
        for attempt in range(max_blocks + 1):
            pending = {tx.hash for tx in wallet.get_txs(query) if tx.hash is not None} - self._unconfirmable_hashes
            if not pending:
                return
            if attempt == max_blocks:
                break
            logger.debug(f"Mining a block, the light wallet has {len(pending)} pending tx(s): {pending}")
            BlockchainUtils.wait_for_blocks(1)
            Utils.wait_for_lws_scan(wallet)
            wallet.sync()

        logger.warning(f"The light wallet has pending txs after {max_blocks} blocks, they are not waited for again: {pending}")
        self._unconfirmable_hashes.update(pending)

    @override
    def before_each(self, request: pytest.FixtureRequest) -> None:
        super().before_each(request)
        self._wait_for_pending_txs(self.get_test_wallet())

    @pytest.fixture(scope="class")
    @classmethod
    def daemon_lws(cls) -> MoneroDaemonLws:
        """Test monero-lws daemon instance."""
        return Utils.get_daemon_lws()

    @pytest.fixture(scope="class")
    @classmethod
    @override
    def wallet(cls) -> MoneroWalletLight:
        """Test light wallet instance."""
        return cls.get_test_wallet()

    @classmethod
    @override
    def get_test_wallet(cls) -> MoneroWalletLight:
        return super().get_test_wallet() # type: ignore

    @override
    def _open_wallet(self, config: Optional[MoneroWalletConfig], start_syncing: bool = True) -> MoneroWalletLight:
        return self._create_open_wallet(config, False, start_syncing)

    @override
    def _create_wallet(self, config: Optional[MoneroWalletConfig], start_syncing: bool = True) -> MoneroWalletLight:
        return self._create_open_wallet(config, True, start_syncing)

    @override
    def _close_wallet(self, wallet: MoneroWallet, save: bool = False) -> None:
        wallet.close(save)

    @override
    def _get_seed_languages(self) -> list[str]:
        return MoneroWalletLight.get_seed_languages()
