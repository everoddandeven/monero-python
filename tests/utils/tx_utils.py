import logging

from abc import ABC
from typing import Optional
from monero import MoneroTx

from .context import TestContext
from .assert_utils import AssertUtils
from .tx_tester import TxTester

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

        AssertUtils.assert_equals(tx, copy)
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
    def test_tx(cls, tx: MoneroTx | None, ctx: TestContext) -> None:
        """Test monero tx.

        :param MoneroTx | None tx: transaction to test.
        :param TestContext ctx: test context.
        """
        assert tx is not None, "No tx provided"
        tester: TxTester = TxTester(tx, ctx)
        tester.run()

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
        assert miner_tx.is_confirmed
        # TODO binary blocks doesn't have depth?
        # assert miner_tx.num_confirmations is not None
        # assert miner_tx.num_confirmations > 0

        # TODO: miner tx does not have hashes in binary requests so this will fail, need to derive using prunable data
        # ctx = new TestContext()
        # ctx.has_json = false
        # ctx.is_pruned = true
        # ctx.is_full = false
        # ctx.is_confirmed = true
        # ctx.is_miner = true
        # ctx.from_get_tx_pool = true
        # cls.test_tx(miner_tx, ctx)
