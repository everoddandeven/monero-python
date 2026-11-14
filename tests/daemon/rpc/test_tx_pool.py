from __future__ import annotations

import logging

import pytest
from monero import (
    MoneroDaemonRpc,
    MoneroFeeEstimate,
    MoneroSubmitTxResult,
    MoneroTx,
    MoneroTxPoolStats,
    MoneroWalletRpc,
)

from utils import (
    DaemonUtils,
    GenUtils,
    SubmitThenRelayTxTester,
    TestContext,
    TestUtils as Utils,
    TxUtils,
    WalletTxsUtils,
)
from .base_test_monero_daemon_rpc import BaseTestMoneroDaemonRpc

logger: logging.Logger = logging.getLogger("TestMoneroDaemonRpcTxPool")


@pytest.mark.integration
class TestMoneroDaemonRpcTxPool(BaseTestMoneroDaemonRpc):
    """Rpc daemon tx pool integration tests."""

    # Can get fee estimate
    @pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_get_fee_estimate(self, daemon: MoneroDaemonRpc) -> None:
        fee_estimate: MoneroFeeEstimate = daemon.get_fee_estimate()
        logger.debug(f"Testing fee estimate: {fee_estimate.serialize()}")
        GenUtils.test_unsigned_big_integer(fee_estimate.fee, True)
        assert len(fee_estimate.fees) == 4, "Exptected 4 fees"
        for fee in fee_estimate.fees:
            GenUtils.test_unsigned_big_integer(fee, True)
        GenUtils.test_unsigned_big_integer(fee_estimate.quantization_mask, True)

    # Can get all transactions in the transaction pool
    @pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_get_txs_in_pool(self, daemon: MoneroDaemonRpc, wallet: MoneroWalletRpc) -> None:
        Utils.WALLET_TX_TRACKER.wait_for_txs_to_clear_pool(wallet)

        # submit tx to pool but don't relay
        tx: MoneroTx = WalletTxsUtils.get_unrelayed_tx(wallet, 1)
        assert tx.hash is not None
        assert tx.full_hex is not None
        result: MoneroSubmitTxResult = daemon.submit_tx_hex(tx.full_hex, True)
        DaemonUtils.test_submit_tx_result_good(result)
        assert result.is_relayed is False

        # fetch txs in pool
        txs: list[MoneroTx] = daemon.get_tx_pool()
        num_txs: int = len(txs)

        # fetch tx hashes in pool
        tx_hashes: list[str] = daemon.get_tx_pool_hashes()
        num_tx_hashes: int = len(tx_hashes)

        # context for testing tx
        ctx: TestContext = TestContext()
        ctx.is_pruned = False
        ctx.is_confirmed = False
        ctx.from_get_tx_pool = True

        # test txs
        assert num_txs > 0, "Test requires an unconfirmed tx in the tx pool"
        assert num_txs == num_tx_hashes, f"Txs in pool {num_txs} != Txs hashes in pool {num_tx_hashes}"
        for a_tx in txs:
            TxUtils.test_tx(a_tx, ctx)
            assert a_tx.hash in tx_hashes

        # flush the tx from the pool, gg
        daemon.flush_tx_pool(tx.hash)
        wallet.sync()

    # Can get transaction pool statistics
    @pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_get_tx_pool_statistics(self, daemon: MoneroDaemonRpc, wallet: MoneroWalletRpc) -> None:
        Utils.WALLET_TX_TRACKER.wait_for_txs_to_clear_pool([wallet])
        tx_ids: list[str] = []
        try:
            # submit txs to the pool but don't relay
            for i in range(1, 3):
                # submit tx hex
                tx: MoneroTx = WalletTxsUtils.get_unrelayed_tx(wallet, i)
                assert tx.full_hex is not None
                result: MoneroSubmitTxResult = daemon.submit_tx_hex(tx.full_hex, True)
                assert result.is_good, f"Expected True, got {result.is_good}"
                assert tx.hash is not None
                tx_ids.append(tx.hash)

                # get tx pool stats
                stats: MoneroTxPoolStats = daemon.get_tx_pool_stats()
                assert stats.num_txs is not None
                assert stats.num_txs > i - 1
                DaemonUtils.test_tx_pool_stats(stats)
        finally:
            # flush txs
            daemon.flush_tx_pool(tx_ids)

    # Can flush all transactions from the pool
    @pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_flush_txs_from_pool(self, daemon: MoneroDaemonRpc, wallet: MoneroWalletRpc) -> None:
        Utils.WALLET_TX_TRACKER.wait_for_txs_to_clear_pool(wallet)

        # preserve original transactions in the pool
        tx_pool_before: list[MoneroTx] = daemon.get_tx_pool()

        # submit txs to the pool but don't relay
        for i in range(1, 3):
            tx: MoneroTx = WalletTxsUtils.get_unrelayed_tx(wallet, i)
            assert tx.full_hex is not None
            result: MoneroSubmitTxResult = daemon.submit_tx_hex(tx.full_hex, True)
            DaemonUtils.test_submit_tx_result_good(result)

        assert len(tx_pool_before) + 2 == len(daemon.get_tx_pool())

        # flush tx pool
        daemon.flush_tx_pool()
        assert len(daemon.get_tx_pool()) == 0

        # re-submit original transactions
        for tx in tx_pool_before:
            assert tx.full_hex is not None
            assert tx.is_relayed is not None
            result: MoneroSubmitTxResult = daemon.submit_tx_hex(tx.full_hex, tx.is_relayed)

        # pool is back to original state
        assert len(tx_pool_before) == len(daemon.get_tx_pool())

        # sync wallet for next test
        wallet.sync()

    # Can flush a transaction from the pool by hash
    @pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_flush_tx_from_pool_by_hash(self, daemon: MoneroDaemonRpc, wallet: MoneroWalletRpc) -> None:
        Utils.WALLET_TX_TRACKER.wait_for_txs_to_clear_pool(wallet)

        # preserve original transactions in the pool
        tx_pool_before: list[MoneroTx] = daemon.get_tx_pool()

        # submit txs to the pool but don't relay
        txs: list[MoneroTx] = []
        for i in range(1, 3):
            tx: MoneroTx = WalletTxsUtils.get_unrelayed_tx(wallet, i)
            assert tx.full_hex is not None
            result: MoneroSubmitTxResult = daemon.submit_tx_hex(tx.full_hex, True)
            DaemonUtils.test_submit_tx_result_good(result)
            txs.append(tx)

        # remove each tx from the pool by hash and test
        num_txs: int = len(txs)
        for i, tx in enumerate(txs):
            assert tx.hash is not None
            # flush tx from pool
            daemon.flush_tx_pool(tx.hash)

            # test tx pool
            pool_txs: list[MoneroTx] = daemon.get_tx_pool()
            assert num_txs - i - 1 == len(pool_txs)

        # pool is back to original state
        assert len(tx_pool_before) == len(daemon.get_tx_pool())

        # sync wallet for next test
        wallet.sync()

    # Can flush transactions from the pool by hashes
    @pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_flush_txs_from_pool_by_hashes(self, daemon: MoneroDaemonRpc, wallet: MoneroWalletRpc) -> None:
        Utils.WALLET_TX_TRACKER.wait_for_txs_to_clear_pool(wallet)

        # preserve original transactions in the pool
        tx_pool_before: list[MoneroTx] = daemon.get_tx_pool()

        # submit txs to the pool but don't relay
        tx_hashes: list[str] = []
        for i in range(1, 3):
            tx: MoneroTx = WalletTxsUtils.get_unrelayed_tx(wallet, i)
            assert tx.hash is not None
            assert tx.full_hex is not None
            result: MoneroSubmitTxResult = daemon.submit_tx_hex(tx.full_hex, True)
            DaemonUtils.test_submit_tx_result_good(result)
            tx_hashes.append(tx.hash)

        assert len(tx_pool_before) + len(tx_hashes) == len(daemon.get_tx_pool())

        # remove all txs by hashes
        daemon.flush_tx_pool(tx_hashes)

        # pool is back to original state
        assert len(tx_pool_before) == len(daemon.get_tx_pool())
        wallet.sync()

    # Can submit a tx in hex format to the pool and relay in one call
    @pytest.mark.skipif(Utils.TEST_RELAYS is False, reason="TEST_RELAYS disabled")
    @pytest.mark.skipif(Utils.LITE_MODE, reason="LITE_MODE enabled")
    def test_submit_and_relay_tx_hex(self, daemon: MoneroDaemonRpc, wallet: MoneroWalletRpc) -> None:
        # wait one time for wallet txs in the pool to clear
        # TODO monero-project: update from pool does not prevent creating double spend tx
        Utils.WALLET_TX_TRACKER.wait_for_txs_to_clear_pool(wallet)

        # create 2 txs, the second will double spend outputs of first
        #  TODO: this test requires tx to be from/to different accounts else
        # the occlusion issue (#4500) causes the tx to not be recognized by the wallet at all
        tx1: MoneroTx = WalletTxsUtils.get_unrelayed_tx(wallet, 2)
        tx2: MoneroTx = WalletTxsUtils.get_unrelayed_tx(wallet, 2)

        # submit and relay tx1
        assert tx1.hash is not None
        assert tx1.full_hex is not None
        result: MoneroSubmitTxResult = daemon.submit_tx_hex(tx1.full_hex)
        assert result.is_relayed is True
        DaemonUtils.test_submit_tx_result_good(result)

        # tx1 is in the pool
        txs: list[MoneroTx] = daemon.get_tx_pool()
        found: bool = False
        for a_tx in txs:
            assert a_tx.hash is not None
            if a_tx.hash == tx1.hash:
                assert a_tx.is_relayed is True
                found = True
                break

        assert found, "Tx1 was not found after being submitted to the daemon's tx pool"

        # tx1 is recognized by the wallet
        wallet.sync()
        wallet.get_tx(tx1.hash)

        # submit and relay tx2 hex which double spends tx1
        assert tx2.full_hex is not None
        result = daemon.submit_tx_hex(tx2.full_hex)
        assert result.is_relayed is True
        DaemonUtils.test_submit_tx_result_double_spend(result)

        # tx2 is not in the pool
        txs = daemon.get_tx_pool()
        found = False
        for a_tx in txs:
            assert a_tx.hash is not None
            if a_tx.hash == tx2.hash:
                found = True
                break

        assert not found, "Tx2 should not be in the pool because it double spends tx1 which is in the pool"

    # Can submit a tx in hex format to the pool then relay
    @pytest.mark.skipif(Utils.TEST_RELAYS is False, reason="TEST_RELAYS disabled")
    @pytest.mark.skipif(Utils.LITE_MODE, reason="LITE_MODE enabled")
    def test_submit_then_relay_tx_hex(self, daemon: MoneroDaemonRpc, wallet: MoneroWalletRpc) -> None:
        Utils.WALLET_TX_TRACKER.wait_for_txs_to_clear_pool(wallet)
        tx: MoneroTx = WalletTxsUtils.get_unrelayed_tx(wallet, 1)
        tester: SubmitThenRelayTxTester = SubmitThenRelayTxTester(daemon, [tx])
        tester.test()

    # Can submit txs in hex format to the pool then relay
    @pytest.mark.skipif(Utils.TEST_RELAYS is False, reason="TEST_RELAYS disabled")
    @pytest.mark.skipif(Utils.LITE_MODE, reason="LITE_MODE enabled")
    def test_submit_then_relay_tx_hexes(self, daemon: MoneroDaemonRpc, wallet: MoneroWalletRpc) -> None:
        Utils.WALLET_TX_TRACKER.wait_for_txs_to_clear_pool(wallet)
        txs: list[MoneroTx] = []
        txs.append(WalletTxsUtils.get_unrelayed_tx(wallet, 1))
        # TODO: accounts cannot be re-used across send tests else isRelayed is true; wallet needs to update?
        txs.append(WalletTxsUtils.get_unrelayed_tx(wallet, 2))
        tester: SubmitThenRelayTxTester = SubmitThenRelayTxTester(daemon, txs)
        tester.test()
