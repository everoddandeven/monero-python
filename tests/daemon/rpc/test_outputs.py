from __future__ import annotations

import logging

import pytest
from monero import (
    MoneroDaemonRpc,
    MoneroKeyImageSpentStatus,
    MoneroOutput,
    MoneroOutputDistributionEntry,
    MoneroOutputHistogramEntry,
    MoneroTx,
    MoneroWalletRpc,
)

from utils import DaemonUtils, OutputUtils, TestUtils as Utils, WalletTxsUtils
from .base_test_monero_daemon_rpc import BaseTestMoneroDaemonRpc

logger: logging.Logger = logging.getLogger("TestMoneroDaemonRpcOutputs")


@pytest.mark.integration
class TestMoneroDaemonRpcOutputs(BaseTestMoneroDaemonRpc):
    """Rpc daemon outputs integration tests."""

    @pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_get_spent_status_of_key_images(self, daemon: MoneroDaemonRpc, wallet: MoneroWalletRpc) -> None:
        Utils.WALLET_TX_TRACKER.wait_for_txs_to_clear_pool(wallet)

        # submit txs to the pool to collect key images then flush them
        txs: list[MoneroTx] = []

        for i in range(1, 3):
            tx: MoneroTx = WalletTxsUtils.get_unrelayed_tx(wallet, i)
            assert tx.full_hex is not None
            daemon.submit_tx_hex(tx.full_hex, True)
            txs.append(tx)

        key_images: list[str] = []
        tx_hashes: list[str] = []
        for tx in txs:
            assert tx.hash is not None
            tx_hashes.append(tx.hash)

        for tx in daemon.get_txs(tx_hashes):
            for tx_input in tx.inputs:
                assert tx_input.key_image is not None
                assert tx_input.key_image.hex is not None
                key_images.append(tx_input.key_image.hex)

        daemon.flush_tx_pool(tx_hashes)

        # key images are not spent
        DaemonUtils.test_spent_statuses(daemon, key_images, MoneroKeyImageSpentStatus.NOT_SPENT)

        # submit txs to the pool but don't relay
        for tx in txs:
            assert tx.full_hex is not None
            daemon.submit_tx_hex(tx.full_hex, True)

        # key images are in the tx pool
        DaemonUtils.test_spent_statuses(daemon, key_images, MoneroKeyImageSpentStatus.TX_POOL)

        # collect key images of confirmed txs
        key_images = []
        txs = DaemonUtils.get_confirmed_txs(daemon, 10)
        for tx in txs:
            for tx_input in tx.inputs:
                assert tx_input.key_image is not None
                assert tx_input.key_image.hex is not None
                key_images.append(tx_input.key_image.hex)

        # key images are all spent
        DaemonUtils.test_spent_statuses(daemon, key_images, MoneroKeyImageSpentStatus.CONFIRMED)

        # flush this test's txs from pool
        daemon.flush_tx_pool(tx_hashes)

    # Can get an output histogram (binary)
    @pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_get_output_histogram_binary(self, daemon: MoneroDaemonRpc) -> None:
        entries: list[MoneroOutputHistogramEntry] = daemon.get_output_histogram([], None, None, None, None)
        assert len(entries) > 0
        for entry in entries:
            OutputUtils.test_output_histogram_entry(entry)

    # Can get an output distribution
    @pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_get_output_distribution(self, daemon: MoneroDaemonRpc) -> None:
        amounts: list[int] = [0]
        entries: list[MoneroOutputDistributionEntry] = daemon.get_output_distribution(amounts)
        for entry in entries:
            OutputUtils.test_output_distribution_entry(entry)

    # Can get the global output indices of a transaction
    @pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_get_output_indices(self, daemon: MoneroDaemonRpc) -> None:
        tx_hashes: list[str] = DaemonUtils.get_confirmed_tx_hashes(daemon)
        assert len(tx_hashes) > 0, "No confirmed txs found"

        for tx_hash in tx_hashes:
            indices: list[int] = daemon.get_output_indices(tx_hash)
            assert len(indices) > 0
            for index in indices:
                assert index >= 0

        with pytest.raises(Exception) as exc_info:
            daemon.get_output_indices("")
        assert str(exc_info.value) == "Must provide a transaction hash"

    # Can get outputs given a list of output amounts and indices (binary)
    @pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_get_outputs(self, daemon: MoneroDaemonRpc) -> None:
        tx_hashes: list[str] = DaemonUtils.get_confirmed_tx_hashes(daemon)
        assert len(tx_hashes) > 0, "No confirmed txs found"

        # identify each output by amount 0 (RingCT) and its global index
        requested: list[MoneroOutput] = []
        for tx_hash in tx_hashes:
            for index in daemon.get_output_indices(tx_hash):
                output: MoneroOutput = MoneroOutput()
                output.amount = 0
                output.index = index
                requested.append(output)

        num_requested: int = len(requested)
        assert num_requested > 0

        fetched: list[MoneroOutput] = daemon.get_outputs(requested)
        num_fetched: int = len(fetched)
        assert num_fetched == num_requested

        for i, output in enumerate(fetched):
            logger.debug(f"Testing fetched output: {output.serialize()}")
            assert output.index == requested[i].index
            assert output.stealth_public_key is not None and len(output.stealth_public_key) == 64
            assert output.mask is not None and len(output.mask) == 64
            assert output.tx is not None
            assert output.tx.block is not None and output.tx.block.height is not None

        with pytest.raises(Exception) as exc_info:
            daemon.get_outputs([])
        assert str(exc_info.value) == "Must provide outputs to fetch"
