import logging

from time import sleep
from monero import (
    MoneroWallet, MoneroTxConfig, MoneroTxWallet,
    MoneroDaemon, MoneroBlockHeader, MoneroTxQuery
)

from .test_utils import TestUtils
from .tx_utils import TxUtils
from .mining_utils import MiningUtils
from .tx_context import TxContext

logger: logging.Logger = logging.getLogger("SendAndUpdateTxsTester")


class SendAndUpdateTxsTester:
    """
    Tests sending a tx with an unlock time then tracking and updating it as
    blocks are added to the chain.

    TODO: test wallet accounting throughout this; dedicated method? probably.

    Allows sending to and from the same account which is an edge case where
    incoming txs are occluded by their outgoing counterpart (issue #4500)
    and also where it is impossible to discern which incoming output is
    the tx amount and which is the change amount without wallet metadata.
    """

    daemon: MoneroDaemon
    """Daemon test instance."""
    wallet: MoneroWallet
    """The test wallet to send from."""
    config: MoneroTxConfig
    """The send configuration to send and test."""
    num_confirmations: int
    """Number of blockchain confirmations."""

    def __init__(self, daemon: MoneroDaemon, wallet: MoneroWallet, config: MoneroTxConfig) -> None:
        """
        Initialize a new send and update txs tester.

        :param MoneroDaemon daemon: daemon test instance.
        :param MoneroWallet wallet: wallet test instance.
        :param MoneroWalletConfig config: txs send configuration to test.
        """
        self.daemon = daemon
        self.wallet = wallet
        self.config = config
        self.num_confirmations = 0

    def setup(self) -> None:
        """Setup test wallet."""
        # wait for txs to confirm and for sufficient unlocked balance
        TestUtils.WALLET_TX_TRACKER.wait_for_txs_to_clear_pool(self.wallet)
        assert len(self.config.subaddress_indices) == 0
        assert self.config.account_index is not None
        fee: int = TxUtils.MAX_FEE * 2
        TestUtils.WALLET_TX_TRACKER.wait_for_unlocked_balance(self.wallet, self.config.account_index, None, fee)

    def test_unlock_tx(self, tx: MoneroTxWallet, is_send_response: bool) -> None:
        """
        Test tx unlock.

        :param MoneroTxWallet tx: transaction to test.
        :param bool is_send_response: indicates if tx originated from send response.
        """
        ctx: TxContext = TxContext()
        ctx.wallet = self.wallet
        ctx.config = self.config
        ctx.is_send_response = is_send_response
        try:
            TxUtils.test_tx_wallet(tx, ctx)
        except Exception as e:
            logger.warning(e)
            raise

    def test_out_in_pair(self, tx_out: MoneroTxWallet, tx_in: MoneroTxWallet) -> None:
        """
        Test transaction out / in pair.

        :param MoneroTxWallet tx_out: outgoing transaction.
        :param MoneroTxWallet tx_in: incoming transaction.
        """
        assert tx_out.is_confirmed == tx_in.is_confirmed
        assert tx_in.get_incoming_amount() == tx_out.get_outgoing_amount()

    def test_out_in_pairs(self, txs: list[MoneroTxWallet], is_send_response: bool) -> None:
        """
        Test transactions out / in pairs.

        :param list[MoneroTxWallet] txs: transactions to test out / in pairs.
        :param bool is_send_response: indicates if tx originated from send response.
        """
        # for each out tx
        for tx in txs:
            self.test_unlock_tx(tx, is_send_response)
            if tx.outgoing_transfer is not None:
                continue

            tx_out: MoneroTxWallet = tx

            # find incoming counterpart
            tx_in: MoneroTxWallet | None = None
            for tx2 in txs:
                if tx.is_incoming and tx.hash == tx2.hash:
                    tx_in = tx2
                    break

            # test out / in pair
            # TODO monero-wallet-rpc: incoming txs occluded by their outgoing counterpart #4500
            if tx_in is None:
                logger.warning(f"outgoing tx {tx.hash} missing incoming counterpart (issue #4500)")
            else:
                self.test_out_in_pair(tx_out, tx_in)

    def wait_for_confirmations(self, sent_txs: list[MoneroTxWallet], num_confirmations_total: int) -> None:
        """
        Wait for txs to confirm.

        :param list[MoneroTxWallet] sent_txs: list of sent transactions.
        :param int num_confirmations_total: number of confirmed txs required.
        """
        # track resulting outgoing and incoming txs as blocks are added to the chain
        updated_txs: list[MoneroTxWallet] | None = None
        logger.info(f"{self.num_confirmations} < {num_confirmations_total} needed confirmations")
        header: MoneroBlockHeader = self.daemon.wait_for_next_block_header()
        logger.info(f"*** Block {header.height} added to chain ***")

        # give wallet time to catch up, otherwise incoming tx may not appear
        # TODO: this lets new block slip, okay?
        sleep(TestUtils.SYNC_PERIOD_IN_MS / 1000)

        # get incoming/outgoing txs with sent hashes
        tx_hashes: list[str] = []
        for sent_tx in sent_txs:
            assert sent_tx.hash is not None
            tx_hashes.append(sent_tx.hash)

        query: MoneroTxQuery = MoneroTxQuery()
        query.hashes = tx_hashes
        fetched_txs: list[MoneroTxWallet] = TxUtils.get_and_test_txs(self.wallet, query, None, True, TestUtils.REGTEST)
        assert len(fetched_txs) > 0

        # test fetched txs
        self.test_out_in_pairs(fetched_txs, False)

        # merge fetched txs into updated txs and original sent txs
        for fetched_tx in fetched_txs:
            # merge with updated txs
            if updated_txs is None:
                updated_txs = fetched_txs
            else:
                for updated_tx in updated_txs:
                    if fetched_tx.hash != updated_tx.hash or fetched_tx.is_outgoing != updated_tx.is_outgoing:
                        continue
                    updated_tx.merge(fetched_tx.copy())
                    if updated_tx.block is None and fetched_tx.block is not None:
                        # copy block for testing
                        updated_tx.block = fetched_tx.block.copy()
                        updated_tx.block.txs = [updated_tx]

            # merge with original sent txs
            for sent_tx in sent_txs:
                if fetched_tx.hash != sent_tx.hash or fetched_tx.is_outgoing != sent_tx.is_outgoing:
                    continue
                # TODO: it's mergeable but tests don't account for extra info
                # from send (e.g. hex) so not tested; could specify in test config
                sent_tx.merge(fetched_tx.copy())

        # test updated txs
        assert updated_txs is not None
        self.test_out_in_pairs(updated_txs, False)

        # update confirmations in order to exit loop
        fetched_tx = fetched_txs[0]
        assert fetched_tx.num_confirmations is not None
        self.num_confirmations = fetched_tx.num_confirmations

    def test(self) -> None:
        """Run send and update txs test."""
        self.setup()
        # this test starts and stops mining, so it's wrapped in order to stop mining if anything fails
        try:
            # send transactions
            sent_txs: list[MoneroTxWallet] = self.wallet.create_txs(self.config)

            # build test context
            ctx: TxContext = TxContext()
            ctx.wallet = self.wallet
            ctx.config = self.config
            ctx.is_send_response = True

            # test sent transactions
            for tx in sent_txs:
                TxUtils.test_tx_wallet(tx, ctx)
                assert tx.is_confirmed is False
                assert tx.in_tx_pool is True

            # attemp to start mining to push the network along
            MiningUtils.try_start_mining()

            # number of confirmations to test
            num_confirmations_total: int = 2
            # loop to update txs through confirmations

            while self.num_confirmations < num_confirmations_total:
                self.wait_for_confirmations(sent_txs, num_confirmations_total)

        finally:
            # stop mining at end of test
            MiningUtils.try_stop_mining()
