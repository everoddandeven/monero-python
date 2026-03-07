from monero import (
    MoneroWallet, MoneroTxWallet, MoneroTransfer,
    MoneroOutputWallet, MoneroWalletRpc, MoneroTxQuery,
    MoneroKeyImage, MoneroTxConfig, MoneroTxSet
)
from .test_utils import TestUtils
from .tx_utils import TxUtils


class ViewOnlyAndOfflineWalletTester:
    """Test view-only and offline wallet compatibility"""

    _wallet: MoneroWallet
    """Wallet test instance"""
    _view_only_wallet: MoneroWallet
    """View-only wallet test instance"""
    _offline_wallet: MoneroWallet
    """Offline full wallet test instance"""

    def __init__(self, wallet: MoneroWallet, view_only_wallet: MoneroWallet, offline_wallet: MoneroWallet) -> None:
        """
        Initialize a new view only and offline wallet tester

        :param MoneroWallet wallet: wallet test instance
        :param MoneroWallet view_only_wallet: view-only wallet test instance
        :param MoneroWallet offline_wallet: offline full wallet test instance
        """
        self._wallet = wallet
        self._view_only_wallet = view_only_wallet
        self._offline_wallet = offline_wallet

    #region Private Methods

    def _setup(self) -> None:
        # wait for txs to confirm and for sufficient unlocked balance
        TestUtils.WALLET_TX_TRACKER.wait_for_txs_to_clear_pool([self._wallet, self._view_only_wallet])
        TestUtils.WALLET_TX_TRACKER.wait_for_unlocked_balance(self._wallet, 0, None, TxUtils.MAX_FEE * 4)

        # test getting txs, transfers, and outputs from view-only wallet
        txs: list[MoneroTxWallet] = self._view_only_wallet.get_txs()
        assert len(txs) > 0

        transfers: list[MoneroTransfer] = self._view_only_wallet.get_transfers()
        assert len(transfers) > 0

        outputs: list[MoneroOutputWallet] = self._view_only_wallet.get_outputs()
        assert len(outputs) > 0

    def _test_view_only_wallet(self) -> str:
        """
        Test view-only wallet and returns primary address

        :returns str: view-only wallet primary address
        """
        # collect info from main test wallet
        primary_address: str = self._wallet.get_primary_address()
        private_view_key: str = self._wallet.get_private_view_key()

        # test and sync view-only
        assert primary_address == self._view_only_wallet.get_primary_address()
        assert private_view_key == self._view_only_wallet.get_private_view_key()
        assert self._view_only_wallet.is_view_only()
        err_msg: str = "Should have failed"

        try:
            self._view_only_wallet.get_seed()
            raise Exception(err_msg)
        except Exception as e:
            assert err_msg != str(e), str(e)

        try:
            self._view_only_wallet.get_seed_language()
            raise Exception(err_msg)
        except Exception as e:
            assert err_msg != str(e), str(e)

        try:
            self._view_only_wallet.get_private_spend_key()
            raise Exception(err_msg)
        except Exception as e:
            assert err_msg != str(e), str(e)

        # TODO: this fails with monero-wallet-rpc and monerod with authentication
        assert self._view_only_wallet.is_connected_to_daemon()
        self._view_only_wallet.sync()
        assert len(self._view_only_wallet.get_txs()) > 0

        return primary_address

    def _test_offline_wallet(self) -> None:
        # test offline wallet
        assert self._offline_wallet.is_connected_to_daemon() is False
        assert self._offline_wallet.is_view_only() is False

        if not isinstance(self._offline_wallet, MoneroWalletRpc):
            # TODO monero-project: cannot get seed from offline wallet rpc
            assert TestUtils.SEED == self._offline_wallet.get_seed()

        query: MoneroTxQuery = MoneroTxQuery()
        query.in_tx_pool = False
        txs = self._offline_wallet.get_txs(query)
        assert len(txs) == 0

    #endregion

    def test(self) -> None:
        """Run test"""
        # cleanup wallet state
        self._setup()

        # test view-only wallet and get primary address
        primary_address: str = self._test_view_only_wallet()

        # export outputs from view-only wallet
        outputs_hex: str = self._view_only_wallet.export_outputs()

        self._test_offline_wallet()

        # import outputs to offline wallet
        num_outputs_imported: int = self._offline_wallet.import_outputs(outputs_hex)
        assert num_outputs_imported > 0, "No outputs imported"

        # export key images from offline wallet
        key_images: list[MoneroKeyImage] = self._offline_wallet.export_key_images()

        # import key images to view-only wallet
        assert self._view_only_wallet.is_connected_to_daemon()
        self._view_only_wallet.import_key_images(key_images)
        assert self._wallet.get_balance() == self._view_only_wallet.get_balance()

        # create unsigned tx using view-only wallet
        tx_config: MoneroTxConfig = MoneroTxConfig()
        tx_config.account_index = 0
        tx_config.address = primary_address
        tx_config.amount = TxUtils.MAX_FEE * 3
        unsigned_tx: MoneroTxWallet = self._view_only_wallet.create_tx(tx_config)
        assert unsigned_tx.tx_set is not None
        assert unsigned_tx.tx_set.unsigned_tx_hex is not None

        # sign tx using offline wallet
        signed_tx_set: MoneroTxSet = self._offline_wallet.sign_txs(unsigned_tx.tx_set.unsigned_tx_hex)
        assert signed_tx_set.signed_tx_hex is not None
        assert len(signed_tx_set.signed_tx_hex) > 0
        assert len(signed_tx_set.txs) == 1
        tx_from_set = signed_tx_set.txs[0]
        assert tx_from_set.hash is not None
        assert len(tx_from_set.hash) > 0

        # parse or "describe" unsigned tx set
        described_tx_set: MoneroTxSet = self._offline_wallet.describe_unsigned_tx_set(unsigned_tx.tx_set.unsigned_tx_hex)
        TxUtils.test_described_tx_set(described_tx_set)

        # submit signed tx using view-only wallet
        if TestUtils.TEST_RELAYS:
            tx_hashes: list[str] = self._view_only_wallet.submit_txs(signed_tx_set.signed_tx_hex)
            assert len(tx_hashes) == 1
            assert len(tx_hashes[0]) == 64
            # wait for confirmation for other tests
            TestUtils.WALLET_TX_TRACKER.wait_for_txs_to_clear_pool(self._view_only_wallet)
