import logging

from abc import ABC
from typing import Optional

from monero import (
    MoneroWallet, MoneroTxQuery, MoneroTransferQuery,
    MoneroOutputQuery, MoneroAccount, MoneroSubaddress,
    MoneroTxWallet, MoneroTransfer, MoneroOutputWallet,
    MoneroTx, MoneroOutgoingTransfer, MoneroIncomingTransfer
)

from .gen_utils import GenUtils
from .assert_utils import AssertUtils
from .tx_utils import TxUtils
from .test_utils import TestUtils as Utils

logger: logging.Logger = logging.getLogger("WalletEqualityUtils")


class WalletEqualityUtils(ABC):
    """Utilities to deep compare wallets."""

    @classmethod
    def test_wallet_equality_on_chain(cls, w1: MoneroWallet, w2: MoneroWallet) -> None:
        """
        Compares two wallets for equality using only on-chain data.

        :param MoneroWallet w1: A wallet to compare
        :param MoneroWallet w2: A wallet to compare
        """
        logger.debug("test_wallet_equality_on_chain()")
        # wait for relayed txs associated with wallets to clear pool
        assert w1.is_connected_to_daemon() == w2.is_connected_to_daemon()
        if w1.is_connected_to_daemon():
            # sync the wallets until same height
            while w1.get_height() != w2.get_height():
                w1.sync()
                w2.sync()
            # wait for txs to clear the pool
            Utils.WALLET_TX_TRACKER.wait_for_txs_to_clear_pool([w1, w2])

        # test that wallets are equal using only on-chain data
        assert w1.get_height() == w2.get_height()
        assert w1.get_seed() == w2.get_seed()
        assert w1.get_primary_address() == w2.get_primary_address()
        assert w1.get_private_view_key() == w2.get_private_view_key()
        assert w1.get_private_spend_key() == w2.get_private_spend_key()

        tx_query = MoneroTxQuery()
        tx_query.is_confirmed = True
        cls.test_tx_wallets_equal_on_chain(w1.get_txs(tx_query), w2.get_txs(tx_query))
        tx_query.include_outputs = True
        cls.test_tx_wallets_equal_on_chain(w1.get_txs(tx_query), w2.get_txs(tx_query)) # fetch and compare outputs
        cls.test_accounts_equal_on_chain(w1.get_accounts(True), w2.get_accounts(True))
        assert w1.get_balance() == w2.get_balance()
        assert w1.get_unlocked_balance() == w2.get_unlocked_balance()
        transfer_query = MoneroTransferQuery()
        transfer_query.tx_query = MoneroTxQuery()
        # TODO set transfer query is setter
        transfer_query.tx_query.transfer_query = transfer_query
        transfer_query.tx_query.is_confirmed = True
        cls.test_transfers_equal_on_chain(w1.get_transfers(transfer_query), w2.get_transfers(transfer_query))
        output_query = MoneroOutputQuery()
        output_query.tx_query = MoneroTxQuery()
        output_query.tx_query.is_confirmed = True
        cls.test_output_wallets_equal_on_chain(w1.get_outputs(output_query), w2.get_outputs(output_query))

    @classmethod
    def test_accounts_equal_on_chain(cls, accounts1: list[MoneroAccount], accounts2: list[MoneroAccount]) -> None:
        accounts1_size = len(accounts1)
        accounts2_size = len(accounts2)
        size = accounts1_size if accounts1_size > accounts2_size else accounts2_size
        i = 0

        while i < size:
            if i < accounts1_size and i < accounts2_size:
                cls.test_account_equal_on_chain(accounts1[i], accounts2[i])
            elif i >= accounts1_size:
                j = i

                while j < accounts2_size:
                    assert 0 == accounts2[j].balance
                    assert len(accounts2[j].subaddresses) >= 1
                    for subaddress in accounts2[j].subaddresses:
                        assert subaddress.is_used is False
                    j += 1

                return
            else:
                j = i
                while j < accounts1_size:
                    assert 0 == accounts1[j].balance
                    assert len(accounts1[j].subaddresses) >= 1
                    for subaddress in accounts1[j].subaddresses:
                        assert subaddress.is_used is False
                    j += 1

                return

            i += 1

    @classmethod
    def test_account_equal_on_chain(cls, account1: MoneroAccount, account2: MoneroAccount) -> None:
        # nullify off-chain data for comparison
        subaddresses1 = account1.subaddresses
        subaddresses2 = account2.subaddresses
        account1.subaddresses.clear()
        account2.subaddresses.clear()
        account1.tag = None
        account2.tag = None

        # test account equality
        AssertUtils.assert_equals(account1, account2, "Accounts are not equal")
        cls.test_subaddresses_equal_on_chain(subaddresses1, subaddresses2)

    @classmethod
    def test_subaddresses_equal_on_chain(
            cls, subaddresses1: list[MoneroSubaddress], subaddresses2: list[MoneroSubaddress]
    ) -> None:
        subaddresses1_len = len(subaddresses1)
        subaddresses2_len = len(subaddresses2)
        size = subaddresses1_len if subaddresses1_len > subaddresses2_len else subaddresses2_len
        i = 0

        while i < size:
            if i < subaddresses1_len and i < subaddresses2_len:
                cls.test_subaddress_equal_on_chain(subaddresses1[i], subaddresses2[i])
            elif i >= subaddresses1_len:
                j = i
                while j < subaddresses2_len:
                    assert 0 == subaddresses2[j].balance
                    assert False is subaddresses2[j].is_used
                    j += 1

                return
            else:
                j = i
                while j < subaddresses1_len:
                    assert 0 == subaddresses1[i].balance
                    assert False is subaddresses1[j].is_used

                return

            i += 1

    @classmethod
    def test_subaddress_equal_on_chain(cls, subaddress1: MoneroSubaddress, subaddress2: MoneroSubaddress) -> None:
        subaddress1.label = None # nullify off-chain data for comparison
        subaddress2.label = None
        assert subaddress1 == subaddress2

    @classmethod
    def remove_txs(cls, txs: list[MoneroTxWallet], to_remove: set[MoneroTxWallet]) -> None:
        for tx_to_remove in to_remove:
            txs.remove(tx_to_remove)

    @classmethod
    def test_tx_wallets_equal_on_chain(cls, txs_1: list[MoneroTxWallet], txs_2: list[MoneroTxWallet]) -> None:
        # remove pool or failed txs for comparison
        txs1: list[MoneroTxWallet] = txs_1.copy()
        to_remove: set[MoneroTxWallet] = set()
        for tx in txs1:
            if tx.in_tx_pool or tx.is_failed:
                to_remove.add(tx)

        cls.remove_txs(txs1, to_remove)

        txs2: list[MoneroTxWallet] = txs_2.copy()
        to_remove.clear()
        for tx in txs2:
            if tx.in_tx_pool or tx.is_failed:
                to_remove.add(tx)

        cls.remove_txs(txs2, to_remove)

        # nullify off-chain data for comparison
        all_txs: list[MoneroTxWallet] = txs1.copy()
        all_txs.extend(txs2)
        for tx in all_txs:
            tx.note = None
            if tx.outgoing_transfer is not None:
                tx.outgoing_transfer.addresses = []

        # compare txs
        assert len(txs1) == len(txs2)
        for tx1 in txs1:
            found = False
            for tx2 in txs2:
                assert tx1.hash is not None
                assert tx2.hash is not None
                if tx1.hash != tx2.hash:
                    continue
                # transfer cached info if known for comparison
                if tx1.outgoing_transfer is not None and len(tx1.outgoing_transfer.destinations) > 0:
                    if tx2.outgoing_transfer is None or len(tx2.outgoing_transfer.destinations) == 0:
                        cls.transfer_cached_info(tx1, tx2)
                elif tx2.outgoing_transfer is not None and len(tx2.outgoing_transfer.destinations) > 0:
                    cls.transfer_cached_info(tx2, tx1)

                # test tx equality
                assert TxUtils.txs_mergeable(tx1, tx2), "Txs are not mergeable"
                AssertUtils.assert_equals(tx1, tx2)
                found = True

                # test block equality except txs to ignore order
                assert tx1.block is not None
                assert tx2.block is not None
                block_txs1: list[MoneroTx] = tx1.block.txs
                block_txs2: list[MoneroTx] = tx2.block.txs
                tx1.block.txs = []
                tx2.block.txs = []
                AssertUtils.assert_equals(block_txs1, block_txs2)
                tx1.block.txs = block_txs1
                tx2.block.txs = block_txs2

            # each tx must have one and only one match
            assert found, "Tx not found"

    @classmethod
    def transfer_cached_info(cls, src: MoneroTxWallet, tgt: MoneroTxWallet) -> None:
        # fill in missing incoming transfers when sending from/to the same account
        if len(src.incoming_transfers) > 0:
            for in_transfer in src.incoming_transfers:
                assert src.outgoing_transfer is not None
                if in_transfer.account_index == src.outgoing_transfer.account_index:
                    tgt.incoming_transfers.append(in_transfer)

            tgt.incoming_transfers.sort() # type: ignore

        # transfer info to outgoing transfer
        if tgt.outgoing_transfer is None:
            tgt.outgoing_transfer = src.outgoing_transfer
        else:
            assert src.outgoing_transfer is not None
            tgt.outgoing_transfer.destinations = src.outgoing_transfer.destinations.copy()
            tgt.outgoing_transfer.amount = src.outgoing_transfer.amount

        # transfer payment id if outgoing
        # TODO monero-wallet-rpc does not provide payment id for outgoing transfer when cache missing
        # https://github.com/monero-project/monero/issues/8378
        if tgt.outgoing_transfer is not None:
            tgt.payment_id = src.payment_id

    @classmethod
    def test_transfers_equal_on_chain(cls, transfers1: list[MoneroTransfer], transfers2: list[MoneroTransfer]) -> None:
        assert len(transfers1) == len(transfers2)
        logger.debug("test_transfers_equal_on_chain()")

        # test and collect transfers per transaction
        txs_transfers_1: dict[str, list[MoneroTransfer]] = {}
        txs_transfers_2: dict[str, list[MoneroTransfer]] = {}
        last_height: Optional[int] = None
        last_tx1: Optional[MoneroTxWallet] = None
        last_tx2: Optional[MoneroTxWallet] = None

        i = 0
        while i < len(transfers1):
            transfer1 = transfers1[i]
            transfer2 = transfers2[i]

            # transfers must have same height even if they don't belong to same tx
            # (because tx ordering within blocks is not currently provided by wallet2)
            assert transfer1.tx.get_height() == transfer2.tx.get_height()

            # transfers must be in ascending order by height
            if last_height is None:
                last_height = transfer1.tx.get_height()
            else:
                transfer_height = transfer1.tx.get_height()
                assert transfer_height is not None
                assert last_height <= transfer_height

            assert transfer1.tx.hash is not None
            assert transfer2.tx.hash is not None

            # transfers must be consecutive per transaction
            if last_tx1 != transfer1.tx:
                assert not GenUtils.has_key(transfer1.tx.hash, txs_transfers_1)
                # cannot be seen before
                last_tx1 = transfer1.tx

            if last_tx2 != transfer2.tx:
                assert not GenUtils.has_key(transfer2.tx.hash, txs_transfers_2)
                # cannot be seen before
                last_tx2 = transfer2.tx

            # collect tx1 transfer
            tx_transfers1 = txs_transfers_1.get(transfer1.tx.hash)
            if tx_transfers1 is None:
                tx_transfers1 = []
                txs_transfers_1[transfer1.tx.hash] = tx_transfers1

            tx_transfers1.append(transfer1)

            # collect tx2 transfer
            tx_transfers2 = txs_transfers_2.get(transfer2.tx.hash)
            if tx_transfers2 is None:
                tx_transfers2 = []
                txs_transfers_2[transfer2.tx.hash] = tx_transfers2

            tx_transfers2.append(transfer2)

            i += 1

        # compare collected transfers per tx for equality
        for tx_hash in txs_transfers_1:
            tx_transfers1 = txs_transfers_1[tx_hash]
            tx_transfers2 = txs_transfers_2[tx_hash]
            assert len(tx_transfers1) == len(tx_transfers2)

            # normalize and compare transfers
            i = 0
            while i < len(tx_transfers1):
                transfer1 = tx_transfers1[i]
                transfer2 = tx_transfers2[i]

                # normalize outgoing transfers
                if isinstance(transfer1, MoneroOutgoingTransfer):
                    assert isinstance(transfer2, MoneroOutgoingTransfer)

                    # transfer destination info if known for comparison
                    if len(transfer1.destinations) > 0:
                        if len(transfer2.destinations) == 0:
                            cls.transfer_cached_info(transfer1.tx, transfer2.tx)
                    elif len(transfer2.destinations) > 0:
                        cls.transfer_cached_info(transfer2.tx, transfer1.tx)

                    # nullify other local wallet data
                    transfer1.addresses = []
                    transfer2.addresses = []
                else:
                    # normalize incoming transfers
                    assert isinstance(transfer1, MoneroIncomingTransfer)
                    assert isinstance(transfer2, MoneroIncomingTransfer)
                    transfer1.address = None
                    transfer2.address = None

                # compare transfer equality
                AssertUtils.assert_equals(transfer1, transfer2)

                i += 1

    @classmethod
    def test_output_wallets_equal_on_chain(cls, outputs1: list[MoneroOutputWallet], outputs2: list[MoneroOutputWallet]) -> None:
        assert len(outputs1) == len(outputs2)
        # test and collect outputs per transaction
        txs_outputs1: dict[str, list[MoneroOutputWallet]] = {}
        txs_outputs2: dict[str, list[MoneroOutputWallet]] = {}
        last_height: Optional[int] = None
        last_tx1: Optional[MoneroTxWallet] = None
        last_tx2: Optional[MoneroTxWallet] = None

        i: int = 0
        while i < len(outputs1):
            output1 = outputs1[i]
            output2 = outputs2[i]

            # outputs must have same height even if they don't belong to same tx
            # (because tx ordering within blocks is not currently provided by wallet2)
            assert output1.tx.get_height() == output2.tx.get_height()

            # outputs must be in ascending order by height
            if last_height is None:
                last_height = output1.tx.get_height()
            else:
                output_height = output1.tx.get_height()
                assert output_height is not None
                assert last_height <= output_height

            assert output1.tx.hash is not None
            assert output2.tx.hash is not None

            # outputs must be consecutive per transaction
            if last_tx1 != output1.tx:
                # cannot be seen before
                assert not GenUtils.has_key(output1.tx.hash, txs_outputs1)
                assert isinstance(output1.tx, MoneroTxWallet)
                last_tx1 = output1.tx

            if last_tx2 != output2.tx:
                # cannot be seen before
                assert not GenUtils.has_key(output2.tx.hash, txs_outputs2)
                assert isinstance(output2.tx, MoneroTxWallet)
                last_tx2 = output2.tx

            # collect tx1 output
            tx_outputs1 = txs_outputs1.get(output1.tx.hash)
            if tx_outputs1 is None:
                tx_outputs1 = []
                txs_outputs1[output1.tx.hash] = tx_outputs1

            tx_outputs1.append(output1)

            # collect tx2 output
            tx_outputs2 = txs_outputs2.get(output2.tx.hash)
            if tx_outputs2 is None:
                tx_outputs2 = []
                txs_outputs2[output2.tx.hash] = tx_outputs2

            tx_outputs2.append(output2)
            i += 1

        # compare collected outputs per tx for equality
        for tx_hash in txs_outputs2:
            tx_outputs1 = txs_outputs1[tx_hash]
            tx_outputs2 = txs_outputs2[tx_hash]
            assert len(tx_outputs1) == len(tx_outputs2)

            # normalize and compare outputs
            i = 0
            while i < len(tx_outputs1):
                output1 = tx_outputs1[i]
                output2 = tx_outputs2[i]
                assert output1.tx.hash == output2.tx.hash
                AssertUtils.assert_equals(output1, output2)
                i += 1
