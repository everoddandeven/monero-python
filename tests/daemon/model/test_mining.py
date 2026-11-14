from __future__ import annotations

import logging

import pytest
from monero import (
    MoneroAddAuxiliaryPowResult,
    MoneroAuxiliaryPow,
    MoneroGenerateBlocksResult,
    MoneroMinerData,
    MoneroMinerTxSum,
    MoneroMiningStatus,
    MoneroTx,
)

from utils import AssertUtils, BaseTestClass

logger: logging.Logger = logging.getLogger("TestMoneroDaemonModelMining")


@pytest.mark.unit
class TestMoneroDaemonModelMining(BaseTestClass):
    """Daemon mining model unit tests."""

    def test_mining_status_deserialize(self) -> None:
        status: MoneroMiningStatus = MoneroMiningStatus()
        status.is_active = True
        status.is_background = False
        status.address = "9" + "a" * 94
        status.speed = 500
        status.num_threads = 4
        AssertUtils.assert_serialization_integrity(status)

    def test_mining_status_inactive_clears_background_and_address_deserialize(self) -> None:
        # when isActive is false from_property_tree drops isBackground and address
        # even if present in the json
        json_str: str = (
            '{"isActive": false, "isBackground": true, '
            '"address": "' + "9" + "a" * 94 + '", "speed": 500, "numThreads": 4}'
        )
        status: MoneroMiningStatus = MoneroMiningStatus.deserialize(json_str)
        assert status.is_active is False
        assert status.is_background is None
        assert status.address is None
        assert status.speed == 500
        assert status.num_threads == 4

    def test_miner_tx_sum_deserialize(self) -> None:
        summ: MoneroMinerTxSum = MoneroMinerTxSum()
        summ.emission_sum_low = 1000
        summ.emission_sum_high = 0
        summ.fee_sum_low = 10
        summ.fee_sum_high = 0
        AssertUtils.assert_serialization_integrity(summ)

    def test_generate_blocks_result_deserialize(self) -> None:
        result: MoneroGenerateBlocksResult = MoneroGenerateBlocksResult()
        result.block_hashes = ["a" * 64, "b" * 64]
        result.height = 12345
        AssertUtils.assert_serialization_integrity(result)

    def test_miner_data_deserialize(self) -> None:
        data: MoneroMinerData = MoneroMinerData()
        data.credits = 0
        data.top_block_hash = "a" * 64
        data.major_version = 16
        data.height = 3000000
        data.prev_hash = "b" * 64
        data.seed_hash = "c" * 64
        data.difficulty = "0x1f4"  # daemon reports difficulty as a hex string
        data.median_weight = 300000
        data.already_generated_coins = 5646232813355588
        tx: MoneroTx = MoneroTx()
        tx.hash = "d" * 64
        tx.fee = 10000
        data.tx_pool_backlog = [tx]
        AssertUtils.assert_serialization_integrity(data)

    def test_auxiliary_pow_deserialize(self) -> None:
        aux_pow: MoneroAuxiliaryPow = MoneroAuxiliaryPow("a" * 64, "b" * 64)
        assert aux_pow.id == "a" * 64
        assert aux_pow.hash == "b" * 64
        AssertUtils.assert_serialization_integrity(aux_pow)

    def test_add_auxiliary_pow_result_deserialize(self) -> None:
        result: MoneroAddAuxiliaryPowResult = MoneroAddAuxiliaryPowResult()
        result.credits = 0
        result.top_block_hash = "a" * 64
        result.block_template_blob = "abcd"
        result.block_hashing_blob = "ef01"
        result.merkle_root = "b" * 64
        result.merkle_tree_depth = 2
        result.aux_pow = [MoneroAuxiliaryPow("c" * 64, "d" * 64)]
        AssertUtils.assert_serialization_integrity(result)
