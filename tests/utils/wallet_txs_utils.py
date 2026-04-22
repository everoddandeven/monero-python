from abc import ABC
from typing import Optional
from random import shuffle

from monero import (
    MoneroWallet, MoneroTxWallet, MoneroTxQuery,
    MoneroTxConfig
)

from .assert_utils import AssertUtils
from .context import TxContext
from .tx_wallet_utils import TxWalletUtils


class WalletTxsUtils(ABC):

    @classmethod
    def get_and_test_txs(
        cls,
        wallet: MoneroWallet,
        query: Optional[MoneroTxQuery],
        ctx: Optional[TxContext],
        is_expected: Optional[bool],
        regtest: bool
    ) -> list[MoneroTxWallet]:
        """Get and test txs from wallet.

        :param MoneroWallet wallet: wallet to get txs from.
        :param MoneroTxQuery | None query: filter wallet txs by query if defined.
        :param TxContext | None ctx: transaction context.
        :param bool | None is_expected: expects empty/non-empty txs.
        """
        copy: Optional[MoneroTxQuery] = query.copy() if query is not None else None
        txs = wallet.get_txs(query) if query is not None else wallet.get_txs()
        assert txs is not None

        if is_expected is False:
            assert len(txs) == 0

        if is_expected is True:
            assert len(txs) > 0

        TxWalletUtils.test_txs_wallet(txs, ctx)
        TxWalletUtils.test_get_txs_structure(txs, query, regtest)

        if query is not None:
            AssertUtils.assert_equals(copy, query)

        return txs

    @classmethod
    def get_random_transactions(
            cls,
            wallet: MoneroWallet,
            query: Optional[MoneroTxQuery] = None,
            min_txs: Optional[int] = None,
            max_txs: Optional[int] = None
    ) -> list[MoneroTxWallet]:
        """Get random transaction from wallet.

        :param Wallet wallet: wallet to get random txs from.
        :param MoneroTxQuery | None: filter txs by query (default `None`).
        :param int | None min_txs: minimum number of txs to get (default `None`).
        :param int | None max_txs: maximum number of txs to get (default `None`).
        """
        txs = wallet.get_txs(query if query is not None else MoneroTxQuery())

        if min_txs is not None:
            assert len(txs) >= min_txs, f"{len(txs)}/{min_txs} transactions found with the query"

        shuffle(txs)

        if max_txs is None:
            return txs

        result: list[MoneroTxWallet] = []

        for i, tx in enumerate(txs):
            result.append(tx)
            if i >= max_txs - 1:
                break

        return result

    @classmethod
    def get_unrelayed_tx(cls, wallet: MoneroWallet, account_idx: int) -> MoneroTxWallet:
        """Get unrelayed tx from wallet account.

        :param MoneroWallet wallet: wallet to get unrelayed tx from.
        :param int account_idx: wallet account index to get unrelayed tx from.
        :returns MoneroTxWallet: unrealyed wallet tx.
        """
        # TODO monero-project
        assert account_idx > 0, "Txs sent from/to same account are not properly synced from the pool"
        config = MoneroTxConfig()
        config.account_index = account_idx
        config.address = wallet.get_primary_address()
        config.amount = TxWalletUtils.MAX_FEE

        tx = wallet.create_tx(config)
        assert (tx.full_hex is None or tx.full_hex == "") is False
        assert tx.relay is False, f"Expected tx.relay to be False, got {tx.relay}"
        return tx

    @classmethod
    def test_scan_txs(cls, wallet: MoneroWallet, scan_wallet: MoneroWallet) -> None:
        """Test wallet transaction scan.

        :param MoneroWallet wallet: original wallet to test.
        :param MoneroWallet scan_wallet: scan wallet to test.
        """
        # get a few tx hashes
        tx_hashes: list[str] = []
        txs: list[MoneroTxWallet] = wallet.get_txs()
        assert len(txs) > 2, "Not enough txs to scan"
        for i in range(1, 3):
            tx_hash = txs[i].hash
            assert tx_hash is not None
            tx_hashes.append(tx_hash)

        # start wallet without scanning
        # TODO create wallet without daemon connection (offline does not reconnect, default connects to localhost,
        # offline then online causes confirmed txs to disappear)
        scan_wallet.stop_syncing()
        assert scan_wallet.is_connected_to_daemon()

        # scan txs
        scan_wallet.scan_txs(tx_hashes)

        # TODO scanning txs causes merge problems reconciling 0 fee, is_miner_tx with test txs

        # close wallet
        scan_wallet.close(False)
