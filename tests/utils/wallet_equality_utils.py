from abc import ABC

from monero import (
    MoneroWallet, MoneroTxQuery, MoneroDaemon, MoneroTransferQuery, 
    MoneroOutputQuery, MoneroAccount, MoneroSubaddress, 
    MoneroTxWallet, MoneroTransfer, MoneroOutputWallet
)

from .wallet_tx_tracker import WalletTxTracker


class WalletEqualityUtils(ABC):

    @classmethod
    def test_wallet_equality_on_chain(
            cls, daemon: MoneroDaemon, sync_period_ms: int, tx_tracker: WalletTxTracker,
            w1: MoneroWallet, w2: MoneroWallet
    ) -> None:
        tx_tracker.reset() # all wallets need to wait for txs to confirm to reliably sync

        # wait for relayed txs associated with wallets to clear pool
        assert w1.is_connected_to_daemon() == w2.is_connected_to_daemon()
        if w1.is_connected_to_daemon():
            tx_tracker.wait_for_wallet_txs_to_clear_pool(daemon, sync_period_ms, [w1, w2])

        # sync the wallets until same height
        while w1.get_height() != w2.get_height():
            w1.sync()
            w2.sync()

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
        assert account1 == account2
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
    def test_tx_wallets_equal_on_chain(cls, txs1: list[MoneroTxWallet], txs2: list[MoneroTxWallet]) -> None:
        raise NotImplementedError("test_tx_wallets_equal_on_chain(): not implemented")

    @classmethod
    def transfer_cached_info(cls, src: MoneroTxWallet, tgt: MoneroTxWallet) -> None:
        raise NotImplementedError("transfer_cached_info(): not implemented")

    @classmethod
    def test_transfers_equal_on_chain(cls, transfers1: list[MoneroTransfer], transfers2: list[MoneroTransfer]) -> None:
        raise NotImplementedError("test_transfers_equal_on_chain(): not implemented")

    @classmethod
    def test_output_wallets_equal_on_chain(
            cls, outputs1: list[MoneroOutputWallet], outputs2: list[MoneroOutputWallet]
    ) -> None:
        raise NotImplementedError("test_output_wallet_equals_on_chain(): not implemented")
