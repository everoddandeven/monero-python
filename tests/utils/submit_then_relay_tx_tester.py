
from time import sleep

from monero import (
    MoneroDaemonRpc, MoneroTx,
    MoneroSubmitTxResult
)

from .daemon_utils import DaemonUtils


class SubmitThenRelayTxTester:
    """Test submitting then relaying txs."""

    daemon: MoneroDaemonRpc
    """Daemon rpc test instance."""
    txs: list[MoneroTx]
    """Transactions to test."""

    def __init__(self, daemon: MoneroDaemonRpc, txs: list[MoneroTx]) -> None:
        """
        Initialize a submit-then-relay-tx tester

        :param MoneroDaemonRpc daemon: daemon rpc instance.
        :param list[MoneroTx] txs: txs to test.
        """
        self.daemon = daemon
        self.txs = txs

    def is_tx_in_pool(self, tx_hash: str) -> bool:
        """
        Check if tx is in pool.

        :param str tx_hash: the transaction's hash to check.
        :returns bool: `True` if transaction was found in the pool.
        """
        pool_txs: list[MoneroTx] = self.daemon.get_tx_pool()
        for a_tx in pool_txs:
            assert a_tx.hash is not None
            if a_tx.hash == tx_hash:
                assert a_tx.is_relayed is False
                return True

        return False

    def ensure_txs_relayed(self) -> None:
        """
        Ensure test transactions are relayed.
        """
        # ensure txs are relayed
        pool_txs: list[MoneroTx] = self.daemon.get_tx_pool()
        for tx in self.txs:
            found: bool = False
            for a_tx in pool_txs:
                assert a_tx.hash is not None
                if a_tx.hash == tx.hash:
                    assert a_tx.is_relayed is True
                    found = True
                    break

            assert found, "Tx was not found after being submitted to the daemon's tx pool"

    def get_and_test_tx_hashes(self) -> list[str]:
        """
        Submit and get tx hashes without relaying.

        :returns list[str]: list of non-relayed tx hashes.
        """
        tx_hashes: list[str] = []
        for tx in self.txs:
            assert tx.hash is not None
            assert tx.full_hex is not None
            tx_hashes.append(tx.hash)
            result: MoneroSubmitTxResult = self.daemon.submit_tx_hex(tx.full_hex, True)
            DaemonUtils.test_submit_tx_result_good(result)
            assert result.is_relayed is False

            # ensure tx is in pool
            assert self.is_tx_in_pool(tx.hash), "Tx was not found after being submitted to the daemon's tx pool"

            # fetch tx by hash and ensure not relayed
            fetched_tx: MoneroTx | None = self.daemon.get_tx(tx.hash)
            assert fetched_tx is not None
            assert fetched_tx.is_relayed is False

        return tx_hashes

    def test(self) -> None:
        """Start test"""
        # submit txs hex but don't relay
        tx_hashes: list[str] = self.get_and_test_tx_hashes()

        # relay the txs
        try:
            if len(tx_hashes) == 1:
                self.daemon.relay_tx_by_hash(tx_hashes[0])
            else:
                self.daemon.relay_txs_by_hash(tx_hashes)

        except Exception:
            # flush txs when relay fails to prevent double spends in other tests
            self.daemon.flush_tx_pool(tx_hashes)
            raise

        # wait for txs to be relayed
        # TODO (monero-project): all txs should be relayed: https://github.com/monero-project/monero/issues/8523

        sleep(1)
        self.ensure_txs_relayed()
