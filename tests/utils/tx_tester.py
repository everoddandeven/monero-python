
from monero import MoneroTx

from .context import TestContext
from .gen_utils import GenUtils
from .output_utils import OutputUtils


class TxTester:
    """Test a `MoneroTx`."""

    tx: MoneroTx
    """Transaction to test."""

    ctx: TestContext
    """Transaction test context."""

    def __init__(self, tx: MoneroTx, ctx: TestContext) -> None:
        """Initialize a new transaction tester.

        :param MoneroTx tx: transaction to test.
        :param TestContext ctx: test context.
        """
        # check inputs
        assert ctx.is_pruned is not None
        assert ctx.is_confirmed is not None
        assert ctx.from_get_tx_pool is not None
        self.tx = tx
        self.ctx = ctx

    def _test_standard(self) -> None:
        """Test standard tx data model accross all txs."""

        # standard across all txs
        assert self.tx.hash is not None
        assert len(self.tx.hash) == 64
        if self.tx.is_relayed is None:
            assert self.tx.in_tx_pool is True
        else:
            assert self.tx.is_relayed is not None
        assert self.tx.is_confirmed is not None
        assert self.tx.in_tx_pool is not None
        assert self.tx.is_miner_tx is not None
        assert self.tx.is_double_spend_seen is not None
        assert self.tx.version is not None
        assert self.tx.version >= 0
        assert self.tx.unlock_time is not None
        assert self.tx.unlock_time >= 0
        assert self.tx.extra is not None
        assert len(self.tx.extra) > 0
        GenUtils.test_unsigned_big_integer(self.tx.fee, True)

        # test presence of output indices
        # TODO change this over to outputs only
        if self.tx.is_miner_tx is True:
            # TODO how to get output indices for miner transactions?
            assert len(self.tx.output_indices) == 0
            assert self.tx.fee == 0
            assert len(self.tx.inputs) == 0
            assert len(self.tx.signatures) == 0
        if self.tx.in_tx_pool or self.ctx.from_get_tx_pool or self.ctx.has_output_indices is False:
            assert len(self.tx.output_indices) == 0
        else:
            assert len(self.tx.output_indices) > 0

    def _test_confirmed(self) -> None:
        """Test transaction confirmation."""
        # test confirmed ctx
        if self.ctx.is_confirmed is True:
            assert self.tx.is_confirmed is True
        elif self.ctx.is_confirmed is False:
            assert self.tx.is_confirmed is False

        # test confirmed
        if self.tx.is_confirmed is True:
            block = self.tx.block
            assert block is not None
            assert self.tx in block.txs
            assert block.height is not None
            assert block.height > 0
            assert block.timestamp is not None
            assert block.timestamp > 0
            assert self.tx.relay is True
            assert self.tx.is_relayed is True
            assert self.tx.is_failed is False
            assert self.tx.in_tx_pool is False
            assert self.tx.is_double_spend_seen is False
            if self.ctx.from_binary_block is True:
                assert self.tx.num_confirmations is None
            else:
                assert self.tx.num_confirmations is not None
                assert self.tx.num_confirmations > 0
        else:
            assert self.tx.block is None, f"Expected block tx to be null: {self.tx.block.serialize()}"
            assert self.tx.num_confirmations == 0

    def _test_in_tx_pool(self) -> None:
        """Test transaction pool details."""
        # test in tx pool
        if self.tx.in_tx_pool:
            assert self.tx.is_confirmed is False
            assert self.tx.is_double_spend_seen is False
            assert self.tx.last_failed_height is None
            assert self.tx.last_failed_hash is None
            assert self.tx.received_timestamp is not None
            assert self.tx.received_timestamp > 0
            if self.ctx.from_get_tx_pool:
                assert self.tx.size is not None
                assert self.tx.size > 0
                assert self.tx.weight is not None
                assert self.tx.weight > 0
                assert self.tx.is_kept_by_block is not None
                assert self.tx.max_used_block_height is not None
                assert self.tx.max_used_block_height >= 0
                assert self.tx.max_used_block_hash is not None

            assert self.tx.last_failed_height is None
            assert self.tx.last_failed_hash is None
        else:
            assert self.tx.last_relayed_timestamp is None

    def _test_failed(self) -> None:
        # test failed
        # TODO what else to test associated with failed
        if self.tx.is_failed:
            assert self.tx.received_timestamp is not None
            assert self.tx.received_timestamp > 0
        else:
            if self.tx.is_relayed is None:
                assert self.tx.relay is None
            elif self.tx.is_relayed:
                assert self.tx.is_double_spend_seen is False
            else:
                assert self.tx.is_relayed is False
                if self.ctx.from_get_tx_pool:
                    assert self.tx.relay is False
                    assert self.tx.is_double_spend_seen is not None

        assert self.tx.last_failed_height is None
        assert self.tx.last_failed_hash is None

        # received time only for tx pool or failed txs
        if self.tx.received_timestamp is not None:
            assert self.tx.in_tx_pool or self.tx.is_failed

    def _test_inputs_and_outputs(self) -> None:
        """Test transaction's inputs and outputs."""

        # test inputs and outputs
        if not self.tx.is_miner_tx:
            assert len(self.tx.inputs) > 0

        for tx_input in self.tx.inputs:
            assert self.tx == tx_input.tx
            OutputUtils.test_input(tx_input, self.ctx)

        assert len(self.tx.outputs) > 0
        for output in self.tx.outputs:
            assert self.tx == output.tx
            OutputUtils.test_output(output, self.ctx)

    def _test_full_tx(self) -> None:
        """Test non-pruned transaction"""
        assert self.tx.version is not None
        assert self.tx.version >= 0
        assert self.tx.unlock_time is not None
        assert self.tx.unlock_time >= 0
        assert self.tx.extra is not None
        assert len(self.tx.extra) > 0

        if self.ctx.from_binary_block is True:
            # TODO: get_blocks_by_height() has inconsistent client-side pruning
            assert self.tx.full_hex is None
            assert self.tx.rct_sig_prunable is None
        else:
            assert self.tx.full_hex is not None
            assert len(self.tx.full_hex) > 0
            # TODO define and test this
            #assert self.tx.rct_sig_prunable is not None

        assert self.tx.is_double_spend_seen is False
        if self.tx.is_confirmed:
            assert self.tx.last_relayed_timestamp is None
            assert self.tx.received_timestamp is None
        else:
            if self.tx.is_relayed:
                assert self.tx.last_relayed_timestamp is not None
                assert self.tx.last_relayed_timestamp > 0
            else:
                assert self.tx.last_relayed_timestamp is None

            assert self.tx.received_timestamp is not None
            assert self.tx.received_timestamp > 0

    def _test_pruning(self) -> None:
        """Test transaction pruning."""
        # test pruned vs not pruned
        # tx might be pruned regardless of configuration
        is_pruned: bool = self.tx.pruned_hex is not None
        if self.ctx.is_pruned:
            assert is_pruned
        if self.ctx.from_get_tx_pool or self.ctx.from_binary_block:
            assert self.tx.prunable_hash is None
        else:
            assert self.tx.prunable_hash is not None

        if is_pruned:
            assert self.tx.rct_sig_prunable is None
            assert self.tx.size is None
            assert self.tx.last_relayed_timestamp is None
            assert self.tx.received_timestamp is None
            # TODO getting full hex in regtest regardless configuration
            # assert self.tx.full_hex is None, f"Expected None got: {tx.full_hex}"
            assert self.tx.pruned_hex is not None
        else:
            self._test_full_tx()

    def run(self) -> None:
        """Run MoneroTx test."""
        ...

        self._test_standard()
        self._test_confirmed()
        self._test_in_tx_pool()
        self._test_failed()
        self._test_inputs_and_outputs()
        self._test_pruning()

        # TODO test failed tx

        # TODO implement extra copy
        # test deep copy
        #if ctx.do_not_test_copy is not True:
        #    cls.test_tx_copy(tx, ctx)
