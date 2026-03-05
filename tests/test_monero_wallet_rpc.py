import pytest
import logging

from monero import (
    MoneroWallet, MoneroWalletConfig, MoneroWalletRpc,
    MoneroAccount, MoneroError, MoneroDaemonRpc,
    MoneroTxWallet, MoneroUtils
)

from typing_extensions import override
from utils import TestUtils as Utils, StringUtils, WalletUtils, WalletType
from test_monero_wallet_common import BaseTestMoneroWallet

logger: logging.Logger = logging.getLogger("TestMoneroWalletRpc")


@pytest.mark.integration
class TestMoneroWalletRpc(BaseTestMoneroWallet):
    """Rpc wallet integration tests"""

    @property
    @override
    def wallet_type(self) -> WalletType:
        return WalletType.RPC

    #region Overrides

    @pytest.fixture(scope="class")
    @override
    def wallet(self) -> MoneroWalletRpc:
        """Test rpc wallet instance"""
        return Utils.get_wallet_rpc()

    @override
    def get_test_wallet(self) -> MoneroWalletRpc:
        return super().get_test_wallet() # type: ignore

    @override
    def _open_wallet(self, config: MoneroWalletConfig | None) -> MoneroWalletRpc:
        try:
            return Utils.open_wallet_rpc(config)
        except Exception:
            Utils.free_wallet_rpc_resources()
            raise

    @override
    def _create_wallet(self, config: MoneroWalletConfig) -> MoneroWalletRpc:
        try:
            return Utils.create_wallet_rpc(config)
        except Exception:
            Utils.free_wallet_rpc_resources()
            raise

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
        # if full tests ran, wait for full wallet's pool txs to confirm
        if Utils.WALLET_FULL_TESTS_RUN:
            Utils.clear_wallet_full_txs_pool()

    @override
    def after_all(self) -> None:
        super().after_all()
        Utils.free_wallet_rpc_resources()

    @override
    def after_each(self, request: pytest.FixtureRequest) -> None:
        super().after_each(request)
        Utils.free_wallet_rpc_resources()

    @override
    def get_daemon_rpc_uri(self) -> str:
        return Utils.DAEMON_RPC_URI if not Utils.IN_CONTAINER else Utils.CONTAINER_DAEMON_RPC_URI

    #endregion

    #region Tests

    @pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    @override
    def test_get_subaddress_address_out_of_range(self, wallet: MoneroWallet) -> None:
        accounts: list[MoneroAccount] = wallet.get_accounts(True)
        account_idx: int = len(accounts) - 1
        subaddress_idx: int = len(accounts[account_idx].subaddresses)
        address = wallet.get_address(account_idx, subaddress_idx)
        assert address is None or len(address) == 0

    # Can create a wallet with a randomly generated seed
    @pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    @pytest.mark.skip(reason="TODO setup another docker monero-wallet-rpc resource")
    def test_create_wallet_random_rpc(self) -> None:
        # create random wallet with defaults
        path: str = StringUtils.get_random_string()
        config: MoneroWalletConfig = MoneroWalletConfig()
        config.path = path
        wallet: MoneroWalletRpc = self._create_wallet(config)
        seed: str = wallet.get_seed()
        MoneroUtils.validate_mnemonic(seed)
        assert Utils.SEED != seed
        MoneroUtils.validate_address(wallet.get_primary_address(), Utils.NETWORK_TYPE)
        # very quick because restore height is chain height
        wallet.sync()
        self._close_wallet(wallet)

        # create random wallet non defaults
        path = StringUtils.get_random_string()
        config = MoneroWalletConfig()
        config.path = path
        config.language = "Spanish"
        wallet = self._create_wallet(config)
        MoneroUtils.validate_mnemonic(wallet.get_seed())
        assert seed != wallet.get_seed()
        MoneroUtils.validate_address(wallet.get_primary_address(), Utils.NETWORK_TYPE)

        # attempt to create wallet which already exists
        try:
            config = MoneroWalletConfig()
            config.path = path
            config.language = "Spanish"
            self._create_wallet(config)
        except MoneroError as e:
            err_msg: str = str(e)
            assert err_msg == f"Wallet already exists: {path}", err_msg
            assert seed == wallet.get_seed()

        self._close_wallet(wallet)

    # Can create a RPC wallet from a seed
    @pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_create_wallet_from_seed_rpc(self, daemon: MoneroDaemonRpc) -> None:
        # create wallet with seed and defaults
        path: str = StringUtils.get_random_string()
        config: MoneroWalletConfig = MoneroWalletConfig()
        config.path = path
        config.seed = Utils.SEED
        config.restore_height = Utils.FIRST_RECEIVE_HEIGHT
        wallet: MoneroWalletRpc = self._create_wallet(config)

        # validate wallet
        assert Utils.SEED == wallet.get_seed()
        assert Utils.ADDRESS == wallet.get_primary_address()
        wallet.sync()
        assert daemon.get_height() == wallet.get_height()
        txs: list[MoneroTxWallet] = wallet.get_txs()
        # expect used wallet
        assert len(txs) > 0, "Wallet is not used"
        assert Utils.FIRST_RECEIVE_HEIGHT == txs[0].get_height()
        # TODO: monero-wallet-rpc: if wallet is not closed, primary address will not change
        self._close_wallet(wallet)

        # create wallet with non-defaults
        path = StringUtils.get_random_string()
        config = MoneroWalletConfig()
        config.path = path
        config.seed = Utils.SEED
        config.restore_height = Utils.FIRST_RECEIVE_HEIGHT
        config.language = "German"
        config.seed_offset = "my offset!"
        config.save_current = False
        wallet = self._create_wallet(config)

        # validate wallet
        MoneroUtils.validate_mnemonic(wallet.get_seed())
        assert wallet.get_seed() != Utils.SEED
        assert wallet.get_primary_address() != Utils.ADDRESS
        wallet.sync()
        assert daemon.get_height() == wallet.get_height()
        txs = wallet.get_txs()
        # expect non used wallet
        assert len(txs) == 0, "Wallet is used"
        self._close_wallet(wallet)

    # Can open wallets
    @pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    @pytest.mark.skip(reason="TODO setup another docker monero-wallet-rpc resource")
    def test_open_wallet(self)-> None:
        # create names of tests wallets
        # TODO setup more wallet-rpc instances
        num_test_wallets: int = 1
        names: list[str] = [ ]
        for i in range(num_test_wallets):
            logger.debug(f"Creating test wallet {i + 1}")
            names.append(StringUtils.get_random_string())

        # create test wallets
        seeds: list[str] = []
        for name in names:
            config: MoneroWalletConfig = MoneroWalletConfig()
            config.path = name
            wallet: MoneroWalletRpc = self._create_wallet(config)
            seeds.append(wallet.get_seed())
            self._close_wallet(wallet, True)

        # open test wallets
        wallets: list[MoneroWalletRpc] = []
        for i in range(num_test_wallets):
            config: MoneroWalletConfig = MoneroWalletConfig()
            config.path = names[i]
            config.password = Utils.WALLET_PASSWORD
            wallet: MoneroWalletRpc = self._open_wallet(config)
            assert seeds[i] == wallet.get_seed()
            wallets.append(wallet)

        # attempt to re-open already opened wallet
        try:
            config: MoneroWalletConfig = MoneroWalletConfig()
            self._open_wallet(config)
            raise Exception("Cannot open wallet wich is already open")
        except MoneroError as e:
            # -1 indicates wallet does not exist (or is open by another app)
            logger.critical(str(e))

        # attempt to open non-existent
        try:
            config: MoneroWalletConfig = MoneroWalletConfig()
            config.path = "btc_integrity"
            config.password = Utils.WALLET_PASSWORD
            raise Exception("Cannot open non-existent wallet")
        except MoneroError as e:
            logger.critical(e)

        # close wallets:
        for wallet in wallets:
            self._close_wallet(wallet)

    # Can indicate if multisig import is needed for correct balance information
    @pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_is_multisig_needed(self, wallet: MoneroWallet) -> None:
        # TODO test with multisig wallet
        multisig_import_needed: bool = wallet.is_multisig_import_needed()
        if Utils.REGTEST and multisig_import_needed:
            # TODO why regtest returns True?
            return

        assert multisig_import_needed is False, "Expected non-multisig wallet"

    # Can save the wallet
    @pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_save(self, wallet: MoneroWallet) -> None:
        wallet.save()

    # Can close a wallet
    @pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_close(self, daemon: MoneroDaemonRpc) -> None:
        # create a test wallet
        path: str = StringUtils.get_random_string()
        config: MoneroWalletConfig = MoneroWalletConfig()
        config.path = path
        wallet: MoneroWalletRpc = self._create_wallet(config)
        wallet.sync()

        # close the wallet
        wallet.close()
        Utils.free_wallet_rpc_resource(wallet)

        # attempt to interact with the wallet
        try:
            wallet.get_height()
        except Exception as e:
            WalletUtils.test_no_wallet_file_error(e)

        try:
            wallet.get_seed()
        except Exception as e:
            WalletUtils.test_no_wallet_file_error(e)

        try:
            wallet.sync()
        except Exception as e:
            WalletUtils.test_no_wallet_file_error(e)

        # re-open the wallet
        wallet.open_wallet(path, Utils.WALLET_PASSWORD)
        wallet.sync()
        assert daemon.get_height() == wallet.get_height()

        # close the wallet
        self._close_wallet(wallet, True)

    # Can stop the RPC server
    @pytest.mark.skip(reason="Disabled so server not actually stopped")
    def test_stop(self, wallet: MoneroWalletRpc) -> None:
        wallet.stop()

    #endregion

    #region Not Supported Tests

    @pytest.mark.not_supported
    @override
    def test_get_daemon_max_peer_height(self, wallet: MoneroWallet) -> None:
        return super().test_get_daemon_max_peer_height(wallet)

    @pytest.mark.not_supported
    @override
    def test_get_daemon_height(self, wallet: MoneroWallet) -> None:
        return super().test_get_daemon_height(wallet)

    @pytest.mark.not_supported
    @override
    def test_get_seed_language(self, wallet: MoneroWallet) -> None:
        return super().test_get_seed_language(wallet)

    @pytest.mark.not_supported
    @override
    def test_get_height_by_date(self, wallet: MoneroWallet) -> None:
        return super().test_get_height_by_date(wallet)

    @pytest.mark.xfail(reason="TODO monero-project")
    @override
    def test_get_public_view_key(self, wallet: MoneroWallet) -> None:
        return super().test_get_public_view_key(wallet)

    @pytest.mark.xfail(reason="TODO monero-project")
    @override
    def test_get_public_spend_key(self, wallet: MoneroWallet) -> None:
        return super().test_get_public_spend_key(wallet)

    #endregion

    #region Disabled Tests

    @pytest.mark.skip(reason="TODO (monero-project): https://github.com/monero-project/monero/issues/5812")
    @override
    def test_import_key_images(self, wallet: MoneroWallet) -> None:
        return super().test_import_key_images(wallet)

    @pytest.mark.skip(reason="TODO")
    @override
    def test_get_new_key_images_from_last_import(self, wallet: MoneroWallet) -> None:
        return super().test_get_new_key_images_from_last_import(wallet)

    @pytest.mark.skip(reason="TODO")
    @override
    def test_subaddress_lookahead(self, wallet: MoneroWallet) -> None:
        return super().test_subaddress_lookahead(wallet)

    @pytest.mark.skip(reason="TODO wallet-rpc can't find txs with payment ids")
    @override
    def test_get_txs_with_payment_ids(self, wallet: MoneroWallet) -> None:
        return super().test_get_txs_with_payment_ids(wallet)

    @pytest.mark.skip(reason="TODO Destination vectors are different")
    @override
    def test_subtract_fee_from(self, wallet: MoneroWallet) -> None:
        return super().test_subtract_fee_from(wallet)

    #endregion
