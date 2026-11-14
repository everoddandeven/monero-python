from __future__ import annotations

import logging

import pytest
from monero import (
    MoneroBlock,
    MoneroKeyImage,
    MoneroOutput,
    MoneroSubmitTxResult,
    MoneroTx,
    MoneroTxPoolStats,
    TxHeightComparator,
)

from utils import AssertUtils, BaseTestClass

logger: logging.Logger = logging.getLogger("TestMoneroDaemonModelTxs")


@pytest.mark.unit
class TestMoneroDaemonModelTxs(BaseTestClass):
    """Daemon txs model unit tests."""

    def test_tx_deserialize(self) -> None:
        tx: MoneroTx = MoneroTx()
        tx.hash = "a" * 64
        tx.is_miner_tx = False
        tx.payment_id = "b" * 16
        tx.fee = 7500000
        tx.relay = True
        tx.is_relayed = True
        tx.is_confirmed = True
        tx.in_tx_pool = False
        tx.is_locked = False
        tx.num_confirmations = 10
        tx.unlock_time = 0
        tx.last_relayed_timestamp = 1700000000
        tx.received_timestamp = 1700000000
        tx.is_double_spend_seen = False
        tx.key = "c" * 64
        tx.full_hex = "deadbeef"
        tx.pruned_hex = "deadbeef"
        tx.prunable_hex = "deadbeef"
        tx.prunable_hash = "d" * 64
        tx.size = 1500
        tx.weight = 1500
        tx.metadata = "meta"
        tx.is_kept_by_block = False
        tx.is_failed = False
        tx.last_failed_hash = "e" * 64
        tx.max_used_block_hash = "f" * 64
        # mixin, rctSignatures, rctSigPrunable and signatures are still left
        # unimplemented in from_property_tree() (see below)
        AssertUtils.assert_serialization_integrity(tx)

    @pytest.mark.parametrize("json_fragment", [
        '{"mixin":5}',
        '{"rctSignatures":"x"}',
        '{"rctSigPrunable":"x"}',
        '{"signatures":["x"]}',
    ])
    def test_tx_unimplemented_fields(self, json_fragment: str) -> None:
        with pytest.raises(Exception, match="not implemented"):
            MoneroTx.deserialize(json_fragment)

    def test_tx_version_common_tx_sets_last_failed_and_max_used_block_height_deserialize(self) -> None:
        tx: MoneroTx = MoneroTx()
        tx.version = 2
        tx.common_tx_sets = "sets"
        tx.last_failed_height = 100
        tx.max_used_block_height = 200
        AssertUtils.assert_serialization_integrity(tx)

    def test_tx_ring_size_deserialize(self) -> None:
        tx: MoneroTx = MoneroTx()
        tx.ring_size = 16
        AssertUtils.assert_serialization_integrity(tx)

    def test_tx_extra_deserialize(self) -> None:
        tx: MoneroTx = MoneroTx()
        tx.extra = [1, 2, 3, 255]
        AssertUtils.assert_serialization_integrity(tx)

    def test_tx_inputs_outputs_and_output_indices_deserialize(self) -> None:
        tx: MoneroTx = MoneroTx()
        tx.output_indices = [100, 101]
        vin: MoneroOutput = MoneroOutput()
        vin.amount = 1
        vin.key_image = MoneroKeyImage()
        vin.key_image.hex = "a" * 64
        tx.inputs = [vin]
        vout: MoneroOutput = MoneroOutput()
        vout.amount = 2
        vout.index = 0
        tx.outputs = [vout]
        AssertUtils.assert_serialization_integrity(tx)

    def test_submit_tx_result_deserialize(self) -> None:
        result: MoneroSubmitTxResult = MoneroSubmitTxResult()
        result.credits = 1
        result.top_block_hash = "a" * 64
        result.is_relayed = True
        result.is_double_spend = False
        result.is_fee_too_low = False
        result.has_invalid_input = False
        result.has_invalid_output = False
        result.has_too_few_outputs = False
        result.is_mixin_too_low = False
        result.is_overspend = False
        result.reason = "ok"
        result.is_too_big = False
        result.sanity_check_failed = False
        result.is_tx_extra_too_big = False
        result.is_nonzero_unlock_time = False
        # is_good is serialized but never read back by from_property_tree()
        AssertUtils.assert_serialization_integrity(result)

    def test_submit_tx_result_is_good_deserialize(self) -> None:
        result: MoneroSubmitTxResult = MoneroSubmitTxResult()
        result.is_good = True
        json_str: str = result.serialize()
        logger.debug(f"Serialized submit tx result: {json_str}")
        assert "isGood" in json_str
        restored: MoneroSubmitTxResult = MoneroSubmitTxResult.deserialize(json_str)
        logger.debug(f"Deserialized submit tx result re-serialized: {restored.serialize()}")
        assert restored.is_good == result.is_good

    def test_tx_pool_stats_deserialize(self) -> None:
        stats: MoneroTxPoolStats = MoneroTxPoolStats()
        stats.num_txs = 5
        stats.num_not_relayed = 1
        stats.num_failing = 0
        stats.num_double_spends = 0
        stats.num10m = 2
        stats.fee_total = 1000
        stats.bytes_max = 2000
        stats.bytes_med = 1500
        stats.bytes_min = 1000
        stats.bytes_total = 5000
        stats.histo98pc = 1800
        stats.oldest_timestamp = 1700000000
        # histo is serialized as an object but from_property_tree() has a TODO
        # and never reads it back into the map
        AssertUtils.assert_serialization_integrity(stats)

    def test_tx_pool_stats_histo_deserialize(self) -> None:
        stats: MoneroTxPoolStats = MoneroTxPoolStats()
        stats.histo = {100: 1, 200: 2}
        json_str: str = stats.serialize()
        logger.debug(f"Serialized tx pool stats: {json_str}")
        assert "histo" in json_str
        restored: MoneroTxPoolStats = MoneroTxPoolStats.deserialize(json_str)
        logger.debug(f"Deserialized tx pool stats re-serialized: {restored.serialize()}")
        assert dict(restored.histo) == dict(stats.histo)

    def test_tx_copy(self) -> None:
        tx: MoneroTx = MoneroTx()
        tx.hash = "a" * 64
        tx.is_confirmed = True
        tx.fee = 7500000

        copy: MoneroTx = tx.copy()
        assert copy is not tx
        assert copy.serialize() == tx.serialize()

    def test_tx_copy_deep_copies_inputs(self) -> None:
        tx: MoneroTx = MoneroTx()
        tx.hash = "a" * 64

        key_image: MoneroKeyImage = MoneroKeyImage()
        key_image.hex = "1" * 64
        tx_input: MoneroOutput = MoneroOutput()
        tx_input.tx = tx
        tx_input.key_image = key_image
        tx_input.amount = 1234
        tx.inputs = [tx_input]

        copy: MoneroTx = tx.copy()
        assert len(copy.inputs) == 1
        assert copy.inputs[0] is not tx_input
        assert copy.inputs[0].key_image.hex == "1" * 64 # type: ignore
        assert copy.inputs[0].amount == 1234
        assert copy.inputs[0].tx is copy

    def test_tx_merge(self) -> None:
        a: MoneroTx = MoneroTx()
        a.hash = "a" * 64
        a.is_confirmed = True  # required: merge() dereferences is_confirmed directly
        a.fee = 7500000

        b: MoneroTx = a.copy()
        b.num_confirmations = 5  # a.num_confirmations is unset -> merge fills the gap
        a.merge(b)
        assert a.num_confirmations == 5

    def test_tx_merge_adopts_other_block(self) -> None:
        block: MoneroBlock = MoneroBlock()
        block.height = 200

        other: MoneroTx = MoneroTx()
        other.hash = "a" * 64
        other.is_confirmed = True
        other.block = block
        block.txs = [other]

        tx: MoneroTx = MoneroTx()
        tx.hash = "a" * 64
        tx.is_confirmed = True
        # tx.block is unset -> merge adopts other's block and repoints the block at tx
        tx.merge(other)
        assert tx.block is block
        assert block.txs[0] is tx

    def test_tx_merge_is_confirmed_can_become_true(self) -> None:
        a: MoneroTx = MoneroTx()
        a.hash = "a" * 64
        a.is_confirmed = False
        b: MoneroTx = a.copy()
        b.is_confirmed = True
        a.merge(b)
        assert a.is_confirmed is True

    def test_tx_merge_is_double_spend_seen_can_become_true(self) -> None:
        a: MoneroTx = MoneroTx()
        a.hash = "a" * 64
        a.is_confirmed = True
        a.is_double_spend_seen = False
        b: MoneroTx = a.copy()
        b.is_double_spend_seen = True
        a.merge(b)
        assert a.is_double_spend_seen is True

    def test_tx_merge_in_tx_pool_can_become_true(self) -> None:
        a: MoneroTx = MoneroTx()
        a.hash = "a" * 64
        a.is_confirmed = False
        a.in_tx_pool = False
        b: MoneroTx = a.copy()
        b.in_tx_pool = True
        a.merge(b)
        assert a.in_tx_pool is True

    def test_tx_merge_is_locked_can_become_false(self) -> None:
        a: MoneroTx = MoneroTx()
        a.hash = "a" * 64
        a.is_confirmed = True
        a.is_locked = False  # self: already unlocked
        b: MoneroTx = a.copy()
        b.is_locked = True   # other: still locked
        a.merge(b)
        assert a.is_locked is False

    def test_tx_merge_extra_and_output_indices(self) -> None:
        a: MoneroTx = MoneroTx()
        a.hash = "a" * 64
        a.is_confirmed = True  # required: merge() dereferences is_confirmed directly
        b: MoneroTx = a.copy()
        b.extra = [1, 2, 3, 255]
        b.output_indices = [100, 101]
        a.merge(b)  # a.extra/output_indices are unset -> merge should adopt b's
        assert a.extra == [1, 2, 3, 255]
        assert a.output_indices == [100, 101]

    def test_tx_merge_inputs(self) -> None:
        def make_input(tx: MoneroTx, key_image_hex: str) -> MoneroOutput:
            key_image: MoneroKeyImage = MoneroKeyImage()
            key_image.hex = key_image_hex
            tx_input: MoneroOutput = MoneroOutput()
            tx_input.tx = tx
            tx_input.key_image = key_image
            return tx_input

        a: MoneroTx = MoneroTx()
        a.hash = "a" * 64
        a.is_confirmed = True  # required: merge() dereferences is_confirmed directly
        a.inputs = [make_input(a, "1" * 64)]

        b: MoneroTx = MoneroTx()
        b.hash = "a" * 64
        b.is_confirmed = True
        shared_input: MoneroOutput = make_input(b, "1" * 64)  # same key image -> merged into a's input
        shared_input.amount = 5000
        b.inputs = [shared_input, make_input(b, "2" * 64)]    # new key image -> appended

        a.merge(b)
        assert len(a.inputs) == 2
        assert a.inputs[0].key_image.hex == "1" * 64 # type: ignore
        assert a.inputs[0].amount == 5000  # filled from b's matching input
        assert a.inputs[1].key_image.hex == "2" * 64 # type: ignore
        assert a.inputs[1].tx is a  # appended input is repointed at a

    def test_tx_lt_height_comparator(self) -> None:
        tx_a: MoneroTx = MoneroTx()
        tx_a.block = MoneroBlock()
        tx_a.block.height = 100

        tx_b: MoneroTx = MoneroTx()
        tx_b.block = MoneroBlock()
        tx_b.block.height = 200

        assert tx_a < tx_b
        assert not (tx_b < tx_a)
        assert TxHeightComparator.compare(tx_a, tx_b)
        assert not TxHeightComparator.compare(tx_b, tx_a)

        txs: list[MoneroTx] = [tx_b, tx_a]
        txs.sort()
        assert txs[0] is tx_a
        assert txs[1] is tx_b

        # unconfirmed (no block) transactions sort after confirmed ones
        tx_unconfirmed: MoneroTx = MoneroTx()
        assert tx_a < tx_unconfirmed
        assert not (tx_unconfirmed < tx_a)
