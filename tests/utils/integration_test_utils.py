import logging

from abc import ABC

from monero import MoneroWallet, MoneroTxWallet, MoneroTxQuery

from .wallet_utils import WalletUtils
from .blockchain_utils import BlockchainUtils
from .wallet_type import WalletType
from .test_utils import TestUtils

logger: logging.Logger = logging.getLogger("IntegrationTestUtils")


class IntegrationTestUtils(ABC):
    """Integration test utilities"""

    __test__ = False

    @classmethod
    def setup(cls, wallet_type: WalletType) -> None:
        """
        Setup integration test environment: mines the blockchain until
        `TestUtils.MIN_BLOCK_HEIGHT` and fund test wallet by integration test wallet type

        :param MoneroWallet wallet_type: wallet type to use in integration tests
        """
        if wallet_type == WalletType.KEYS or wallet_type == WalletType.UNDEFINED:
            return
        BlockchainUtils.setup_blockchain(TestUtils.NETWORK_TYPE)
        # get test wallet
        wallet: MoneroWallet
        type_str: str = "FULL"
        if wallet_type == WalletType.FULL:
            wallet = TestUtils.get_wallet_full()
        elif wallet_type == WalletType.RPC:
            wallet = TestUtils.get_wallet_rpc()
            type_str = "RPC"
        else:
            logger.warning("Only RPC and FULL wallet are supported for integration tests")
            return

        wallet_txs: list[MoneroTxWallet] = wallet.get_txs()
        num_wallet_txs: int = len(wallet_txs)
        # fund wallet with mined coins and wait for unlocked balance
        txs = cls.fund_wallet_and_wait_for_unlocked(wallet)

        # setup regtest first receive height
        if TestUtils.REGTEST:
            tx: MoneroTxWallet = txs[0] if num_wallet_txs == 0 else wallet_txs[0]
            tx_height: int | None = tx.get_height()
            assert tx_height is not None
            TestUtils.FIRST_RECEIVE_HEIGHT = tx_height
            logger.debug(f"Set FIRST_RECEIVE_HEIGHT = {tx_height}")

        if num_wallet_txs == 0:
            logger.info(f"Funded test wallet {type_str}")

    @classmethod
    def fund_wallet_and_wait_for_unlocked(cls, wallet: MoneroWallet) -> list[MoneroTxWallet]:
        """
        Fund wallet used for integration tests and wait for unlocked balance.

        :param MoneroWallet wallet: wallet to use for an integration test
        :returns list[MoneroTxWallet]: list of transactions used to fund test wallet
        """
        # fund wallet
        txs: list[MoneroTxWallet] = WalletUtils.fund_wallet(wallet)
        if len(txs) > 0:
            # mine blocks to confirm txs
            BlockchainUtils.wait_for_blocks(11)
            query: MoneroTxQuery = MoneroTxQuery()
            for tx in txs:
                assert tx.hash is not None
                query.hashes.append(tx.hash)

            num_txs: int = len(txs)
            txs = wallet.get_txs(query)

            assert len(txs) == num_txs

        return txs
