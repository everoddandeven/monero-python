from typing import Optional

from monero import MoneroBlock, MoneroTxWallet, MoneroTxQuery, MoneroTx

from .block_utils import BlockUtils


class TxsStructureTester:
    """Tests the integrity of the full structure in the given txs from the block down to transfers / destinations."""

    txs: list[MoneroTxWallet]
    """Txs to test structure."""

    query: MoneroTxQuery
    """Filter txs by query."""

    regtest: bool
    """Indicates if running test on regtest network."""

    seen_blocks: set[MoneroBlock]
    """Unique set of seen blocks in txs."""

    blocks: list[MoneroBlock]
    """All blocks seen by txs."""

    unconfirmed_txs: list[MoneroTxWallet]
    """Unconfirmed transactions to test."""

    @property
    def num_txs(self) -> int:
        """Number of transactions to test."""
        return len(self.txs)

    @property
    def num_unconfirmed_txs(self) -> int:
        """Number of unconfirmed txs to test."""
        return len(self.unconfirmed_txs)

    @property
    def num_tx_hashes(self) -> int:
        """Number of tx hashes set in tx query."""
        return len(self.query.hashes)

    def __init__(self, txs: list[MoneroTxWallet], query: Optional[MoneroTxQuery], regtest: bool) -> None:
        """Initialize a new txs structure tester.

        :param list[MoneroTxWallet] txs: list of txs to get structure from.
        :param MoneroTxQuery | None query: filter txs by query, if set.
        :param bool regtest: indicates if running test on regtest network.
        """
        self.txs = txs
        self.query = query if query is not None else MoneroTxQuery()
        self.seen_blocks = set()
        self.blocks = []
        self.unconfirmed_txs = []
        self.regtest = regtest

        # initialize
        for tx in txs:
            if tx.block is None:
                self.unconfirmed_txs.append(tx)
            else:
                assert BlockUtils.is_tx_in_block(tx.hash, tx.block)
                if tx.block not in self.seen_blocks:
                    self.seen_blocks.add(tx.block)
                    self.blocks.append(tx.block)

    def _test_block_txs_order(self, tx: MoneroTx, block: MoneroBlock, index: int) -> None:
        assert tx.block == block
        if self.num_tx_hashes == 0:
            other = self.txs[index]
            if not self.regtest:
                assert other.hash == tx.hash, "Txs in block are not in order"
                # verify tx order is self-consistent with blocks unless txs manually re-ordered by querying by hash
                assert other == tx
            else:
                # TODO regtest wallet2 has inconsinstent txs order betwenn
                assert other in block.txs, "Tx not found in block"

    def _test_txs_order(self) -> None:
        """Test that txs and blocks reference each other and blocks are in
        ascending order unless specific tx hashes queried.
        """
        # tx hashes must be in order if requested
        if self.num_tx_hashes > 0:
            assert self.num_txs == self.num_tx_hashes
            for i, query_hash in enumerate(self.query.hashes):
                assert query_hash == self.txs[i].hash

        # test that txs and blocks reference each other and blocks are in ascending order unless specific tx hashes queried
        index: int = 0
        prev_block_height: Optional[int] = None
        for block in self.blocks:
            if prev_block_height is None:
                prev_block_height = block.height
            elif self.num_tx_hashes == 0:
                assert block.height is not None
                msg = f"Blocks are not in order of heights: {prev_block_height} vs {block.height}"
                assert block.height > prev_block_height, msg

            for tx in block.txs:
                self._test_block_txs_order(tx, block, index)
                index += 1

        assert self.num_txs == index + self.num_unconfirmed_txs, f"txs: {self.num_txs}, unconfirmed txs: {self.num_unconfirmed_txs}, index: {index}"

    def _test_incoming_transfers_order(self) -> None:
        """Test that incoming transfers are in order
        of ascending accounts and subaddresses.
        """
        # test that incoming transfers are in order of ascending accounts and subaddresses
        for tx in self.txs:
            if len(tx.incoming_transfers) == 0:
                continue

            prev_account_idx: Optional[int] = None
            prev_subaddress_idx: Optional[int] = None
            for transfer in tx.incoming_transfers:
                if prev_account_idx is None:
                    prev_account_idx = transfer.account_index

                else:
                    assert prev_account_idx is not None
                    assert transfer.account_index is not None
                    assert prev_account_idx <= transfer.account_index
                    if prev_account_idx < transfer.account_index:
                        prev_subaddress_idx = None
                        prev_account_idx = transfer.account_index
                    if prev_subaddress_idx is None:
                        prev_subaddress_idx = transfer.subaddress_index
                    else:
                        assert transfer.subaddress_index is not None
                        assert prev_subaddress_idx < transfer.subaddress_index

    def _test_outputs_order(self) -> None:
        """test that outputs are in order of ascending accounts and subaddresses."""
        # test that outputs are in order of ascending accounts and subaddresses
        for tx in self.txs:
            if len(tx.outputs) == 0:
                continue

            prev_account_idx: Optional[int] = None
            prev_subaddress_idx: Optional[int] = None
            for output in tx.get_outputs_wallet():
                if prev_account_idx is None:
                    prev_account_idx = output.account_index
                else:
                    assert output.account_index is not None
                    assert prev_account_idx <= output.account_index
                    if prev_account_idx < output.account_index:
                        prev_subaddress_idx = None
                        prev_account_idx = output.account_index
                    if prev_subaddress_idx is None:
                        prev_subaddress_idx = output.subaddress_index
                    else:
                        assert prev_subaddress_idx is not None
                        assert output.subaddress_index is not None
                        # TODO: this does not test that index < other index if subaddresses are equal
                        assert prev_subaddress_idx <= output.subaddress_index

    def run(self) -> None:
        """Run test."""
        self._test_txs_order()
        self._test_incoming_transfers_order()
        self._test_outputs_order()
