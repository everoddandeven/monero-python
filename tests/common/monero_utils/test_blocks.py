from __future__ import annotations

import logging

import pytest
from monero import MoneroBlock, MoneroIncomingTransfer, MoneroOutputWallet, MoneroTxWallet, MoneroUtils

from utils import BaseTestClass

logger: logging.Logger = logging.getLogger("TestMoneroUtilsBlocks")


@pytest.mark.unit
class TestMoneroUtilsBlocks(BaseTestClass):
    """Monero utilities blocks unit tests."""

    def test_get_blocks_from_txs_dedup_and_order(self) -> None:
        block1: MoneroBlock = MoneroBlock()
        block1.height = 100
        block2: MoneroBlock = MoneroBlock()
        block2.height = 200

        tx1: MoneroTxWallet = MoneroTxWallet()
        tx1.hash = "a" * 64
        tx1.block = block1

        tx2: MoneroTxWallet = MoneroTxWallet()
        tx2.hash = "b" * 64
        tx2.block = block2

        tx3: MoneroTxWallet = MoneroTxWallet()  # shares block1 with tx1
        tx3.hash = "c" * 64
        tx3.block = block1

        blocks: list[MoneroBlock] = MoneroUtils.get_blocks_from_txs([tx1, tx2, tx3])
        assert len(blocks) == 2  # block1 deduplicated despite appearing twice
        assert blocks[0] is block1  # blocks are returned in first-seen order
        assert blocks[1] is block2

    def test_get_blocks_from_txs_unconfirmed_placeholder(self) -> None:
        tx1: MoneroTxWallet = MoneroTxWallet()
        tx1.hash = "a" * 64
        tx2: MoneroTxWallet = MoneroTxWallet()
        tx2.hash = "b" * 64
        assert tx1.block is None and tx2.block is None

        blocks: list[MoneroBlock] = MoneroUtils.get_blocks_from_txs([tx1, tx2])

        # unconfirmed (blockless) txs are grouped under one shared placeholder block
        assert len(blocks) == 1
        placeholder: MoneroBlock = blocks[0]
        assert placeholder.height is None
        assert len(placeholder.txs) == 2

        # side effect: get_blocks_from_txs() mutates its inputs, attaching each
        # unconfirmed tx to the placeholder block it creates
        assert tx1.block is placeholder
        assert tx2.block is placeholder

    def test_get_blocks_from_txs_mixed_confirmed_and_unconfirmed(self) -> None:
        block: MoneroBlock = MoneroBlock()
        block.height = 100
        confirmed: MoneroTxWallet = MoneroTxWallet()
        confirmed.hash = "a" * 64
        confirmed.block = block

        unconfirmed1: MoneroTxWallet = MoneroTxWallet()
        unconfirmed1.hash = "b" * 64
        unconfirmed2: MoneroTxWallet = MoneroTxWallet()
        unconfirmed2.hash = "c" * 64

        blocks: list[MoneroBlock] = MoneroUtils.get_blocks_from_txs([confirmed, unconfirmed1, unconfirmed2])
        assert len(blocks) == 2  # the real block, plus one shared unconfirmed placeholder
        assert blocks[0] is block
        assert blocks[1].height is None
        assert unconfirmed1.block is unconfirmed2.block is blocks[1]

    def test_get_blocks_from_txs_empty(self) -> None:
        assert MoneroUtils.get_blocks_from_txs([]) == []

    def test_get_blocks_from_transfers_dedup_and_order(self) -> None:
        block1: MoneroBlock = MoneroBlock()
        block1.height = 100
        block2: MoneroBlock = MoneroBlock()
        block2.height = 200

        t1: MoneroIncomingTransfer = MoneroIncomingTransfer()
        t1.tx = MoneroTxWallet()
        t1.tx.hash = "a" * 64
        t1.tx.block = block1

        t2: MoneroIncomingTransfer = MoneroIncomingTransfer()
        t2.tx = MoneroTxWallet()
        t2.tx.hash = "b" * 64
        t2.tx.block = block2

        t3: MoneroIncomingTransfer = MoneroIncomingTransfer()  # tx shares block1 with t1
        t3.tx = MoneroTxWallet()
        t3.tx.hash = "c" * 64
        t3.tx.block = block1

        blocks: list[MoneroBlock] = MoneroUtils.get_blocks_from_transfers([t1, t2, t3])
        assert len(blocks) == 2
        assert blocks[0] is block1
        assert blocks[1] is block2

    def test_get_blocks_from_transfers_unconfirmed_placeholder(self) -> None:
        t1: MoneroIncomingTransfer = MoneroIncomingTransfer()
        t1.tx = MoneroTxWallet()
        t1.tx.hash = "a" * 64
        t2: MoneroIncomingTransfer = MoneroIncomingTransfer()
        t2.tx = MoneroTxWallet()
        t2.tx.hash = "b" * 64
        assert t1.tx.block is None and t2.tx.block is None

        blocks: list[MoneroBlock] = MoneroUtils.get_blocks_from_transfers([t1, t2])
        assert len(blocks) == 1
        placeholder: MoneroBlock = blocks[0]
        assert placeholder.height is None

        # side effect: mutates transfer.tx.block, same as get_blocks_from_txs()
        assert t1.tx.block is placeholder
        assert t2.tx.block is placeholder

    def test_get_blocks_from_transfers_mixed_confirmed_and_unconfirmed(self) -> None:
        block: MoneroBlock = MoneroBlock()
        block.height = 100
        confirmed: MoneroIncomingTransfer = MoneroIncomingTransfer()
        confirmed.tx = MoneroTxWallet()
        confirmed.tx.hash = "a" * 64
        confirmed.tx.block = block

        unconfirmed1: MoneroIncomingTransfer = MoneroIncomingTransfer()
        unconfirmed1.tx = MoneroTxWallet()
        unconfirmed1.tx.hash = "b" * 64
        unconfirmed2: MoneroIncomingTransfer = MoneroIncomingTransfer()
        unconfirmed2.tx = MoneroTxWallet()
        unconfirmed2.tx.hash = "c" * 64

        blocks: list[MoneroBlock] = MoneroUtils.get_blocks_from_transfers([confirmed, unconfirmed1, unconfirmed2])
        assert len(blocks) == 2  # the real block, plus one shared unconfirmed placeholder
        assert blocks[0] is block
        assert blocks[1].height is None
        assert unconfirmed1.tx.block is unconfirmed2.tx.block is blocks[1]

    def test_get_blocks_from_transfers_missing_tx_raises(self) -> None:
        # a transfer with no tx set is a legitimate, reachable state (it's just
        # never assigned); get_blocks_from_transfers() must raise a catchable
        # exception, not dereference transfer.tx and segfault
        transfer: MoneroIncomingTransfer = MoneroIncomingTransfer()
        transfer.amount = 500000
        with pytest.raises(RuntimeError) as exc_info:
            MoneroUtils.get_blocks_from_transfers([transfer])
        assert str(exc_info.value) == "Transfer has no tx"

    def test_get_blocks_from_transfers_missing_tx_raises_after_partial_mutation(self) -> None:
        # get_blocks_from_transfers() is not transactional: a transfer earlier
        # in the list is already mutated (attached to a placeholder block)
        # before a later, invalid transfer aborts the whole call
        good: MoneroIncomingTransfer = MoneroIncomingTransfer()
        good.tx = MoneroTxWallet()
        good.tx.hash = "a" * 64
        assert good.tx.block is None

        bad: MoneroIncomingTransfer = MoneroIncomingTransfer()  # no tx
        with pytest.raises(RuntimeError):
            MoneroUtils.get_blocks_from_transfers([good, bad])

        assert good.tx.block is not None
        assert good.tx.block.height is None

    def test_get_blocks_from_transfers_empty(self) -> None:
        assert MoneroUtils.get_blocks_from_transfers([]) == []

    def test_get_blocks_from_outputs_dedup_and_order(self) -> None:
        block1: MoneroBlock = MoneroBlock()
        block1.height = 100
        block2: MoneroBlock = MoneroBlock()
        block2.height = 200

        tx1: MoneroTxWallet = MoneroTxWallet()
        tx1.hash = "a" * 64
        tx1.block = block1
        tx2: MoneroTxWallet = MoneroTxWallet()
        tx2.hash = "b" * 64
        tx2.block = block2

        o1: MoneroOutputWallet = MoneroOutputWallet()
        o1.tx = tx1
        o2: MoneroOutputWallet = MoneroOutputWallet()
        o2.tx = tx2
        o3: MoneroOutputWallet = MoneroOutputWallet()  # tx shares block1 with o1
        o3.tx = tx1

        blocks: list[MoneroBlock] = MoneroUtils.get_blocks_from_outputs([o1, o2, o3])
        assert len(blocks) == 2
        assert blocks[0] is block1
        assert blocks[1] is block2

    def test_get_blocks_from_outputs_unconfirmed_raises(self) -> None:
        # unlike get_blocks_from_txs()/get_blocks_from_transfers(), an
        # unconfirmed (blockless) output's tx does not get a placeholder
        # block -- it raises instead
        output: MoneroOutputWallet = MoneroOutputWallet()
        output.tx = MoneroTxWallet()
        output.tx.hash = "a" * 64
        assert output.tx.block is None

        with pytest.raises(RuntimeError, match="Need to handle unconfirmed output"):
            MoneroUtils.get_blocks_from_outputs([output])

    def test_get_blocks_from_outputs_unconfirmed_raises_after_earlier_match(self) -> None:
        # unlike get_blocks_from_transfers(), get_blocks_from_outputs() never mutates its inputs
        block: MoneroBlock = MoneroBlock()
        block.height = 100
        confirmed_tx: MoneroTxWallet = MoneroTxWallet()
        confirmed_tx.hash = "a" * 64
        confirmed_tx.block = block
        good: MoneroOutputWallet = MoneroOutputWallet()
        good.tx = confirmed_tx

        bad: MoneroOutputWallet = MoneroOutputWallet()
        bad.tx = MoneroTxWallet()
        bad.tx.hash = "b" * 64  # unconfirmed

        with pytest.raises(RuntimeError, match="Need to handle unconfirmed output"):
            MoneroUtils.get_blocks_from_outputs([good, bad])

    def test_get_blocks_from_outputs_missing_tx_raises(self) -> None:
        # same as get_blocks_from_transfers(): output.tx is a legitimate but
        # unchecked null; must raise rather than dereference and segfault
        output: MoneroOutputWallet = MoneroOutputWallet()
        output.amount = 1000000
        with pytest.raises(RuntimeError) as exc_info:
            MoneroUtils.get_blocks_from_outputs([output])
        assert str(exc_info.value) == "Output has no tx"

    def test_get_blocks_from_outputs_empty(self) -> None:
        assert MoneroUtils.get_blocks_from_outputs([]) == []
