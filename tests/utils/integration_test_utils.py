import logging

from abc import ABC
from time import sleep
from monero import MoneroWallet, MoneroWalletLight, MoneroTxWallet, MoneroTxQuery, MoneroSyncResult

from .wallet_test_utils import WalletTestUtils
from .mining_utils import MiningUtils
from .blockchain_utils import BlockchainUtils
from .wallet_type import WalletType
from .test_utils import TestUtils

logger: logging.Logger = logging.getLogger("IntegrationTestUtils")


class IntegrationTestUtils(ABC):
    """Integration test utilities."""

    __test__ = False

    _LAST_SETUP: WalletType | None = None
    """Wallet type that the integration environment was set up for last, in this session."""

    @classmethod
    def setup_blockchain(cls) -> None:
        """Setup blockchain for integration tests."""
        BlockchainUtils.setup_blockchain(TestUtils.NETWORK_TYPE)

    @classmethod
    def setup(cls, wallet_type: WalletType) -> None:
        """Setup integration test environment: mines the blockchain until
         `TestUtils.MIN_BLOCK_HEIGHT` and fund test wallet by integration test wallet type.

        :param MoneroWallet wallet_type: wallet type to use in integration tests.
        """
        if wallet_type == WalletType.KEYS or wallet_type == WalletType.UNDEFINED:
            return
        # once for each run of classes of the same type, as when all the tests of a wallet type were in a class: the classes of the
        # topics that came from it would do the same work again. It is not once for the whole session: the wallets of the types have
        # the same seed, so the tests of a type spend the funds of the next one, which is funded again when its classes start
        if wallet_type == cls._LAST_SETUP:
            return
        cls.setup_blockchain()
        # get test wallet
        wallet: MoneroWallet
        type_str: str = "FULL"
        if wallet_type == WalletType.FULL:
            wallet = TestUtils.get_wallet_full()
        elif wallet_type == WalletType.RPC:
            wallet = TestUtils.get_wallet_rpc()
            type_str = "RPC"
        elif wallet_type == WalletType.LIGHT:
            wallet = TestUtils.get_wallet_light()
            type_str = "LIGHT"
        else:
            raise ValueError("Only RPC, FULL, and LIGHT wallets are supported for integration tests")

        # sync before checking for pre-existing txs: MoneroWalletLight has no local persistent
        # storage, so its cache (and get_txs()) is empty until synced, even for an already-funded address
        wallet.sync()
        wallet_txs: list[MoneroTxWallet] = wallet.get_txs()
        num_wallet_txs: int = len(wallet_txs)
        # fund wallet with mined coins and wait for unlocked balance
        txs: list[MoneroTxWallet] = cls.fund_wallet_and_wait_for_unlocked(wallet)

        # setup first receive height: the one of the oldest tx of the wallet, read after the funding. The types of wallet share the seed, so
        # the ones that run after the first find the txs of the previous types. A light wallet has not got them all before the blocks of
        # the funding: lws scans again from the restore height of the account when a block arrives, and until it ends the wallet has
        # only the txs of the last blocks. A wallet that is restored from a later height, as the ground truth of the equality tests is,
        # does not have the older txs.
        if isinstance(wallet, MoneroWalletLight):
            TestUtils.wait_for_lws_scan(wallet)
            wallet.sync()
        heights: list[int] = [h for h in (wallet_tx.get_height() for wallet_tx in wallet.get_txs()) if h is not None]
        tx_height: int | None = min(heights) if len(heights) > 0 else txs[0].get_height()
        assert tx_height is not None, "Could not get test wallet first receive height"
        TestUtils.FIRST_RECEIVE_HEIGHT = tx_height
        logger.debug(f"FIRST_RECEIVE_HEIGHT = {tx_height}")

        if num_wallet_txs == 0 and TestUtils.REGTEST:
            # needed for correct m_num_suggested_confirmations estimate in light wallet
            MiningUtils.generate_blocks(wallet.get_primary_address(), 1)
            wallet.sync()
            logger.info(f"Funded test wallet {type_str}")

        cls._LAST_SETUP = wallet_type

    @classmethod
    def fund_wallet_and_wait_for_unlocked(cls, wallet: MoneroWallet) -> list[MoneroTxWallet]:
        """Fund wallet used for integration tests and wait for unlocked balance.

        :param MoneroWallet wallet: wallet to use for an integration test.
        :returns list[MoneroTxWallet]: list of transactions used to fund test wallet.
        """
        # fund wallet
        txs: list[MoneroTxWallet] = WalletTestUtils.fund_wallet(wallet)
        if len(txs) > 0:
            # mine an output to wallet primary address
            MiningUtils.generate_blocks(wallet.get_primary_address(), 1)
            # mine blocks to confirm txs
            block_height: int = BlockchainUtils.wait_for_blocks(11)

            # sync wallet
            while wallet.get_height() < block_height:
                sync_result: MoneroSyncResult = wallet.sync()
                assert sync_result.num_blocks_fetched is not None
                if sync_result.num_blocks_fetched > 0:
                    logger.debug(f"Sync result from funded wallet: {sync_result.serialize()}")

                sleep(TestUtils.SYNC_PERIOD_IN_MS / 1000)

            # check for txs
            query: MoneroTxQuery = MoneroTxQuery()
            for tx in txs:
                assert tx.hash is not None
                query.hashes.append(tx.hash)

            num_txs: int = len(txs)
            txs = wallet.get_txs(query)

            assert len(txs) == num_txs, f"Expected {num_txs} txs, but got {len(txs)}"

            # assert txs are unlocked
            for tx in txs:
                assert tx.is_locked is False, f"Expected tx to be unlocked: {tx.serialize()}"

        return txs
