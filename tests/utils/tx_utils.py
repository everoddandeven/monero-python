import logging

from abc import ABC
from typing import Optional
from monero import MoneroTx

from .gen_utils import GenUtils
from .context import TestContext
from .assert_utils import AssertUtils
from .output_utils import OutputUtils

logger: logging.Logger = logging.getLogger("TxUtils")


class TxUtils(ABC):
    """Tx utils for tests."""

    __test__ = False

    @classmethod
    def test_tx_copy(cls, tx: Optional[MoneroTx], context: Optional[TestContext]) -> None:
        """Test monero tx copy.

        :param MoneroTx | None tx: transaction to test copy.
        :param TestContext | None context: test context.
        """
        # copy tx and assert deep equality
        assert tx is not None
        copy = tx.copy()
        assert isinstance(copy, MoneroTx)
        assert copy.block is None
        if tx.block is not None:
            block_copy = tx.block.copy()
            block_copy.txs = [copy]

        AssertUtils.assert_equals(str(tx), str(copy))
        assert copy != tx

        # test different input references
        if len(copy.inputs) == 0:
            assert len(tx.inputs) == 0
        else:
            assert copy.inputs != tx.inputs
            for i, output in enumerate(copy.outputs):
                assert tx.outputs[i].amount == output.amount

        # test copied tx
        ctx = TestContext(context)
        ctx.do_not_test_copy = True # to prevent infinite recursion
        if tx.block is not None:
            block_copy = tx.block.copy()
            block_copy.txs = [copy]
            copy.block = block_copy

        cls.test_tx(copy, ctx)

        # test merging with copy
        merged = copy
        merged.merge(copy.copy())
        assert str(tx) == str(merged)

    @classmethod
    def test_tx(cls, tx: Optional[MoneroTx], ctx: Optional[TestContext]) -> None:
        """Test monero tx.

        :param MoneroTx | None tx: transaction to test.
        :param TestContext | None ctx: test context.
        """
        # check inputs
        assert tx is not None
        assert ctx is not None
        assert ctx.is_pruned is not None
        assert ctx.is_confirmed is not None
        assert ctx.from_get_tx_pool is not None

        # standard across all txs
        assert tx.hash is not None
        assert len(tx.hash) == 64
        if tx.is_relayed is None:
            assert tx.in_tx_pool is True
        else:
            assert tx.is_relayed is not None
        assert tx.is_confirmed is not None
        assert tx.in_tx_pool is not None
        assert tx.is_miner_tx is not None
        assert tx.is_double_spend_seen is not None
        assert tx.version is not None
        assert tx.version >= 0
        assert tx.unlock_time is not None
        assert tx.unlock_time >= 0
        assert tx.extra is not None
        assert len(tx.extra) > 0
        GenUtils.test_unsigned_big_integer(tx.fee, True)

        # test presence of output indices
        # TODO change this over to outputs only
        if tx.is_miner_tx is True:
            # TODO how to get output indices for miner transactions?
            assert len(tx.output_indices) == 0
        if tx.in_tx_pool or ctx.from_get_tx_pool or ctx.has_output_indices is False:
            assert len(tx.output_indices) == 0
        else:
            assert len(tx.output_indices) > 0

        # test confirmed ctx
        if ctx.is_confirmed is True:
            assert tx.is_confirmed is True
        elif ctx.is_confirmed is False:
            assert tx.is_confirmed is False

        # test confirmed
        if tx.is_confirmed is True:
            block = tx.block
            assert block is not None
            assert tx in block.txs
            assert block.height is not None
            assert block.height > 0
            assert block.timestamp is not None
            assert block.timestamp > 0
            assert tx.relay is True
            assert tx.is_relayed is True
            assert tx.is_failed is False
            assert tx.in_tx_pool is False
            assert tx.is_double_spend_seen is False
            if ctx.from_binary_block is True:
                assert tx.num_confirmations is None
            else:
                assert tx.num_confirmations is not None
                assert tx.num_confirmations > 0
        else:
            assert tx.block is None, f"Expected block tx to be null: {tx.block.serialize()}"
            assert tx.num_confirmations == 0

        # test in tx pool
        if tx.in_tx_pool:
            assert tx.is_confirmed is False
            assert tx.is_double_spend_seen is False
            assert tx.last_failed_height is None
            assert tx.last_failed_hash is None
            assert tx.received_timestamp is not None
            assert tx.received_timestamp > 0
            if ctx.from_get_tx_pool:
                assert tx.size is not None
                assert tx.size > 0
                assert tx.weight is not None
                assert tx.weight > 0
                assert tx.is_kept_by_block is not None
                assert tx.max_used_block_height is not None
                assert tx.max_used_block_height >= 0
                assert tx.max_used_block_hash is not None

            assert tx.last_failed_height is None
            assert tx.last_failed_hash is None
        else:
            assert tx.last_relayed_timestamp is None

        # test miner tx
        if tx.is_miner_tx:
            assert tx.fee == 0
            assert len(tx.inputs) == 0
            assert len(tx.signatures) == 0

        # test failed
        # TODO what else to test associated with failed
        if tx.is_failed:
            assert tx.received_timestamp is not None
            assert tx.received_timestamp > 0
        else:
            if tx.is_relayed is None:
                assert tx.relay is None
            elif tx.is_relayed:
                assert tx.is_double_spend_seen is False
            else:
                assert tx.is_relayed is False
                if ctx.from_get_tx_pool:
                    assert tx.relay is False
                    assert tx.is_double_spend_seen is not None

        assert tx.last_failed_height is None
        assert tx.last_failed_hash is None

        # received time only for tx pool or failed txs
        if tx.received_timestamp is not None:
            assert tx.in_tx_pool or tx.is_failed

        # test inputs and outputs
        if not tx.is_miner_tx:
            assert len(tx.inputs) > 0

        for tx_input in tx.inputs:
            assert tx == tx_input.tx
            OutputUtils.test_input(tx_input, ctx)

        assert len(tx.outputs) > 0
        for output in tx.outputs:
            assert tx == output.tx
            OutputUtils.test_output(output, ctx)

        # test pruned vs not pruned
        # tx might be pruned regardless of configuration
        is_pruned: bool = tx.pruned_hex is not None
        if ctx.is_pruned:
            assert is_pruned
        if ctx.from_get_tx_pool or ctx.from_binary_block:
            assert tx.prunable_hash is None
        else:
            assert tx.prunable_hash is not None

        if is_pruned:
            assert tx.rct_sig_prunable is None
            assert tx.size is None
            assert tx.last_relayed_timestamp is None
            assert tx.received_timestamp is None
            # TODO getting full hex in regtest regardless configuration
            # assert tx.full_hex is None, f"Expected None got: {tx.full_hex}"
            assert tx.pruned_hex is not None
        else:
            assert tx.version is not None
            assert tx.version >= 0
            assert tx.unlock_time is not None
            assert tx.unlock_time >= 0
            assert tx.extra is not None
            assert len(tx.extra) > 0

            if ctx.from_binary_block is True:
                # TODO: get_blocks_by_height() has inconsistent client-side pruning
                assert tx.full_hex is None
                assert tx.rct_sig_prunable is None
            else:
                assert tx.full_hex is not None
                assert len(tx.full_hex) > 0
                # TODO define and test this
                #assert tx.rct_sig_prunable is not None

            assert tx.is_double_spend_seen is False
            if tx.is_confirmed:
                assert tx.last_relayed_timestamp is None
                assert tx.received_timestamp is None
            else:
                if tx.is_relayed:
                    assert tx.last_relayed_timestamp is not None
                    assert tx.last_relayed_timestamp > 0
                else:
                    assert tx.last_relayed_timestamp is None

                assert tx.received_timestamp is not None
                assert tx.received_timestamp > 0

        # TODO test failed tx

        # TODO implement extra copy
        # test deep copy
        #if ctx.do_not_test_copy is not True:
        #    cls.test_tx_copy(tx, ctx)

    @classmethod
    def test_miner_tx(cls, miner_tx: Optional[MoneroTx]) -> None:
        """Test monero miner tx.

        :param MoneroTx | None miner_tx: miner transaction to test.
        """
        assert miner_tx is not None
        assert miner_tx.is_miner_tx is not None
        assert miner_tx.version is not None
        assert miner_tx.version >= 0
        assert miner_tx.extra is not None
        assert len(miner_tx.extra) > 0
        assert miner_tx.unlock_time is not None
        assert miner_tx.unlock_time >= 0

        # TODO: miner tx does not have hashes in binary requests so this will fail, need to derive using prunable data
        # ctx = new TestContext()
        # ctx.has_json = false
        # ctx.is_pruned = true
        # ctx.is_full = false
        # ctx.is_confirmed = true
        # ctx.is_miner = true
        # ctx.from_get_tx_pool = true
        # cls.test_tx(miner_tx, ctx)
