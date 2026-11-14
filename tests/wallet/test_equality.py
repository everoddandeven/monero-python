from __future__ import annotations

import logging

import pytest
from monero import (
    MoneroAccount,
    MoneroOutputQuery,
    MoneroOutputWallet,
    MoneroTxWallet,
    MoneroWallet,
    MoneroWalletFull,
)
from typing_extensions import override

from utils import GenUtils, TestUtils, WalletEqualityUtils, WalletUtils
from .base_test_monero_wallet import BaseTestMoneroWallet
from .wallet_support import FullWalletSupport, RpcWalletSupport, KeysWalletSupport

logger: logging.Logger = logging.getLogger("TestMoneroWalletEquality")


class BaseTestMoneroWalletEquality(BaseTestMoneroWallet):
    """Common wallet equality tests."""

    # Is equal to a ground truth wallet accoring to on-chain data
    @pytest.mark.skipif(TestUtils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_wallet_equality_ground_truth(self, wallet: MoneroWallet) -> None:
        TestUtils.WALLET_TX_TRACKER.wait_for_txs_to_clear_pool([wallet])
        wallet_gt: MoneroWalletFull = TestUtils.create_wallet_ground_truth(
            TestUtils.NETWORK_TYPE, TestUtils.SEED, None, TestUtils.FIRST_RECEIVE_HEIGHT
        )
        try:
            WalletEqualityUtils.test_wallet_equality_on_chain(wallet_gt, wallet)
        finally:
            wallet_gt.close()

    # Has correct accounting across accounts, subaddresses, txs, transfers and outputs
    @pytest.mark.skipif(TestUtils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_accounting(self, wallet: MoneroWallet) -> None:
        # pre-fetch wallet balances, accounts, subaddresses and txs
        wallet_balance: int = wallet.get_balance()
        wallet_unlocked_balance: int = wallet.get_unlocked_balance()
        # includes subaddresses
        accounts: list[MoneroAccount] = wallet.get_accounts(True)

        # test wallet balance
        GenUtils.test_unsigned_big_integer(wallet_balance)
        GenUtils.test_unsigned_big_integer(wallet_unlocked_balance)
        assert wallet_balance >= wallet_unlocked_balance

        # test that wallet balance equals sum of account balances
        accounts_balance: int = 0
        accounts_unlocked_balance: int = 0
        for account in accounts:
            # test that account balance equals sum of subaddress balances
            WalletUtils.test_account(account, TestUtils.NETWORK_TYPE)
            assert account.balance is not None
            assert account.unlocked_balance is not None
            accounts_balance += account.balance
            accounts_unlocked_balance += account.unlocked_balance

        assert wallet_balance == accounts_balance
        assert wallet_unlocked_balance == accounts_unlocked_balance

        # TODO test that wallet balance equals net of wallet's incoming and outgoing tx amounts

        # balance may not equal sum of unspent outputs if unconfirmed txs
        # TODO monero-wallet-rpc: reason not to return unspent outputs on unconfirmed txs? then this isn't necessary
        txs: list[MoneroTxWallet] = wallet.get_txs()
        has_unconfirmed_tx: bool = False
        for tx in txs:
            if tx.in_tx_pool:
                has_unconfirmed_tx = True

        # wallet balance is sum of all unspent outputs
        wallet_sum: int = 0
        output_query: MoneroOutputQuery = MoneroOutputQuery()
        output_query.is_spent = False
        for output in wallet.get_outputs(output_query):
            assert output.amount is not None
            wallet_sum += output.amount

        if wallet_balance != wallet_sum:
            # txs may have changed in between calls to retry test
            wallet_sum = 0
            for output in wallet.get_outputs(output_query):
                assert output.amount is not None
                wallet_sum += output.amount

            if wallet_balance != wallet_sum:
                assert has_unconfirmed_tx, "Wallet balance must equal sum of unspent outputs if no unconfirmed txs"

        # account balances are sum of their unspent outputs
        for account in accounts:
            account_sum: int = 0
            output_query = MoneroOutputQuery()
            output_query.account_index = account.index
            output_query.is_spent = False
            account_outputs: list[MoneroOutputWallet] = wallet.get_outputs(output_query)
            for output in account_outputs:
                assert output.amount is not None
                account_sum += output.amount

            assert account.balance is not None
            if account.balance != account_sum:
                assert has_unconfirmed_tx, "Account balance must equal sum of its unspent outputs if no unconfirmed txs"

            # subaddress balances are sum of their unspent outputs
            for subaddress in account.subaddresses:
                subaddress_sum: int = 0
                output_query = MoneroOutputQuery()
                output_query.account_index = account.index
                output_query.subaddress_index = subaddress.index
                output_query.is_spent = False
                subaddress_outputs: list[MoneroOutputWallet] = wallet.get_outputs(output_query)
                for output in subaddress_outputs:
                    assert output.amount is not None
                    subaddress_sum += output.amount

                if subaddress_sum != subaddress.balance:
                    assert has_unconfirmed_tx, "Subaddress balance must equal sum of its unspent outputs if no unconfirmed txs"


@pytest.mark.integration
class TestMoneroWalletFullEquality(FullWalletSupport, BaseTestMoneroWalletEquality):
    """Full wallet equality integration tests."""


@pytest.mark.integration
class TestMoneroWalletRpcEquality(RpcWalletSupport, BaseTestMoneroWalletEquality):
    """Rpc wallet equality integration tests."""


@pytest.mark.unit
class TestMoneroWalletKeysEquality(KeysWalletSupport, BaseTestMoneroWalletEquality):
    """Keys-only wallet equality unit tests."""

    @pytest.mark.not_supported
    @override
    def test_accounting(self, wallet: MoneroWallet) -> None:
        return super().test_accounting(wallet)

    @pytest.mark.not_supported
    @override
    def test_wallet_equality_ground_truth(self, wallet: MoneroWallet) -> None:
        return super().test_wallet_equality_ground_truth(wallet)
