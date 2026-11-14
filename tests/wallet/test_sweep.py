from __future__ import annotations

import logging

import pytest
from monero import (
    MoneroAccount,
    MoneroOutputQuery,
    MoneroOutputWallet,
    MoneroSubaddress,
    MoneroTxConfig,
    MoneroTxQuery,
    MoneroTxWallet,
    MoneroWallet,
)
from typing_extensions import override

from utils import IntegrationTestUtils, OutputUtils, TestUtils, TxContext, TxWalletUtils, WalletSendUtils
from .base_test_monero_wallet import BaseTestMoneroWallet
from .wallet_support import FullWalletSupport, RpcWalletSupport, KeysWalletSupport

logger: logging.Logger = logging.getLogger("TestMoneroWalletSweep")


class BaseTestMoneroWalletSweep(BaseTestMoneroWallet):
    """Common wallet sweep tests."""

    # Can sweep individual outputs identified by their key images
    @pytest.mark.skipif(TestUtils.TEST_RELAYS is False, reason="TEST_RELAYS disabled")
    def test_sweep_outputs(self, wallet: MoneroWallet) -> None:
        TestUtils.WALLET_TX_TRACKER.wait_for_txs_to_clear_pool(wallet)

        # test config
        num_outputs: int = 3

        # get outputs to sweep (not spent, unlocked, and amount >= fee)
        query: MoneroOutputQuery = MoneroOutputQuery()
        query.is_spent = False
        tx_query: MoneroTxQuery = MoneroTxQuery()
        tx_query.is_locked = False
        query.set_tx_query(tx_query, True)
        spendable_unlocked_outputs: list[MoneroOutputWallet] = wallet.get_outputs(query)
        outputs_to_sweep: list[MoneroOutputWallet] = []
        for spendable_output in spendable_unlocked_outputs:
            if len(outputs_to_sweep) >= num_outputs:
                break
            assert spendable_output.amount is not None
            if spendable_output.amount > TxWalletUtils.MAX_FEE:
                outputs_to_sweep.append(spendable_output)

        assert len(outputs_to_sweep) >= num_outputs, "Wallet does not have enough sweepable outputs; run send tests"

        # sweep each output by key image
        for output in outputs_to_sweep:
            OutputUtils.test_output_wallet(output)
            assert output.is_spent is False
            assert output.tx is not None
            assert isinstance(output.tx, MoneroTxWallet)
            assert output.tx.is_locked is False
            assert output.amount is not None

            if output.amount <= TxWalletUtils.MAX_FEE:
                continue

            # sweep output to address
            assert output.account_index is not None
            assert output.subaddress_index is not None
            assert output.key_image is not None
            assert output.key_image.hex is not None
            address: str = wallet.get_address(output.account_index, output.subaddress_index)
            config: MoneroTxConfig = MoneroTxConfig()
            config.address = address
            config.key_image = output.key_image.hex
            config.relay = True
            tx: MoneroTxWallet = wallet.sweep_output(config)

            # test result tx
            ctx: TxContext = TxContext()
            ctx.wallet = wallet
            ctx.config = config
            ctx.config.can_split = False
            ctx.is_send_response = True
            ctx.is_sweep_response = True
            ctx.is_sweep_output_response = True
            TxWalletUtils.test_tx_wallet(tx, ctx)

        # get outputs after sweeping
        after_outputs: list[MoneroOutputWallet] = wallet.get_outputs()

        # swept outputs are now spent
        for after_output in after_outputs:
            assert after_output.key_image is not None

            for output in outputs_to_sweep:
                assert output.key_image is not None
                if output.key_image.hex == after_output.key_image.hex:
                    assert after_output.is_spent is True, "Output should be spent"

    # Can sweep individual outputs identified by their key images
    @pytest.mark.skipif(TestUtils.TEST_RELAYS is False, reason="TEST_RELAYS disabled")
    def test_sweep_dust_no_relay(self, wallet: MoneroWallet) -> None:
        TestUtils.WALLET_TX_TRACKER.wait_for_txs_to_clear_pool(wallet)

        # sweep dust which returns empty list if no dust to sweep (dust does not exist after rct)
        txs: list[MoneroTxWallet] = wallet.sweep_dust(False)
        if len(txs) == 0:
            return

        # test txs
        ctx: TxContext = TxContext()
        ctx.is_send_response = True
        ctx.config = MoneroTxConfig()
        ctx.config.relay = False
        ctx.is_sweep_response = True
        for tx in txs:
            TxWalletUtils.test_tx_wallet(tx, ctx)

        # relay txs
        metadatas: list[str] = []
        for tx in txs:
            assert tx.metadata is not None
            metadatas.append(tx.metadata)

        tx_hashes: list[str] = wallet.relay_txs(metadatas)
        assert len(tx_hashes) == len(txs)
        for tx_hash in tx_hashes:
            assert len(tx_hash) == 64

        # fetch and test txs
        tx_query: MoneroTxQuery = MoneroTxQuery()
        tx_query.hashes = tx_hashes
        txs = wallet.get_txs(tx_query)
        ctx.config.relay = True
        for tx in txs:
            TxWalletUtils.test_tx_wallet(tx, ctx)

    # Can sweep dust
    @pytest.mark.skipif(TestUtils.TEST_RELAYS is False, reason="TEST_RELAYS disabled")
    def test_sweep_dust(self, wallet: MoneroWallet) -> None:
        TestUtils.WALLET_TX_TRACKER.wait_for_txs_to_clear_pool(wallet)

        # sweep dust which returns empty list if no dust to sweep (dust does not exist after rct)
        txs: list[MoneroTxWallet] = wallet.sweep_dust(True)

        # test any txs
        ctx: TxContext = TxContext()
        ctx.wallet = wallet
        ctx.config = None
        ctx.is_send_response = True
        ctx.is_sweep_response = True
        for tx in txs:
            TxWalletUtils.test_tx_wallet(tx, ctx)

    # Can sweep subaddresses
    @pytest.mark.skipif(TestUtils.TEST_RESETS is False, reason="TEST_RESETS disabled")
    def test_sweep_subaddresses(self, wallet: MoneroWallet) -> None:
        TestUtils.WALLET_TX_TRACKER.wait_for_txs_to_clear_pool(wallet)
        NUM_SUBADDRESSES_TO_SWEEP: int = 2

        # collect subaddresses with balance and unlocked balance
        subaddresses: list[MoneroSubaddress] = []
        subaddresses_balance: list[MoneroSubaddress] = []
        subaddresses_unlocked: list[MoneroSubaddress] = []
        for account in wallet.get_accounts(True):
            if account.index == 0:
                # skip default account
                continue
            for subaddress in account.subaddresses:
                subaddresses.append(subaddress)
                assert subaddress.balance is not None
                if subaddress.balance > TxWalletUtils.MAX_FEE:
                    subaddresses_balance.append(subaddress)
                assert subaddress.unlocked_balance is not None
                if subaddress.unlocked_balance > TxWalletUtils.MAX_FEE:
                    subaddresses_unlocked.append(subaddress)

        # test requires at least one more subaddresses than the number being swept to verify it does not change
        msg: str = f"Test requires balance in at least {NUM_SUBADDRESSES_TO_SWEEP + 1} subaddresses from non-default acccount; run send-to-multiple tests"
        assert len(subaddresses_balance) >= NUM_SUBADDRESSES_TO_SWEEP + 1, msg
        assert len(subaddresses_unlocked) >= NUM_SUBADDRESSES_TO_SWEEP + 1, "Wallet is waiting on unlocked funds"

        # sweep from first unlocked subaddresses
        for i in range(NUM_SUBADDRESSES_TO_SWEEP):
            # sweep unlocked account
            unlocked_subaddress: MoneroSubaddress = subaddresses_unlocked[i]
            config: MoneroTxConfig = MoneroTxConfig()
            config.address = wallet.get_primary_address()
            assert unlocked_subaddress.account_index is not None
            assert unlocked_subaddress.index is not None
            config.account_index = unlocked_subaddress.account_index
            config.subaddress_indices.append(unlocked_subaddress.index)
            config.relay = True
            txs: list[MoneroTxWallet] = wallet.sweep_unlocked(config)

            # test transactions
            assert len(txs) > 0
            for tx in txs:
                assert tx.tx_set is not None
                assert tx in tx.tx_set.txs
                ctx: TxContext = TxContext()
                ctx.wallet = wallet
                ctx.config = config
                ctx.is_send_response = True
                ctx.is_sweep_response = True
                TxWalletUtils.test_tx_wallet(tx, ctx)

            # assert unlocked balance is less than max fee
            subaddress: MoneroSubaddress = wallet.get_subaddress(unlocked_subaddress.account_index, unlocked_subaddress.index)
            assert subaddress.unlocked_balance is not None
            assert subaddress.unlocked_balance < TxWalletUtils.MAX_FEE

        # test subaddresses after sweeping
        subaddresses_after: list[MoneroSubaddress] = []
        for account in wallet.get_accounts(True):
            if account.index == 0:
                # skip default account
                continue
            for subaddress in account.subaddresses:
                subaddresses_after.append(subaddress)

        assert len(subaddresses) == len(subaddresses_after)
        for i, subaddress_before in enumerate(subaddresses):
            subaddress_after: MoneroSubaddress = subaddresses_after[i]
            assert subaddress_after.unlocked_balance is not None

            # determine if subaddress was swept
            swept: bool = False
            for j in range(NUM_SUBADDRESSES_TO_SWEEP):
                subaddress_unlocked: MoneroSubaddress = subaddresses_unlocked[j]
                account_eq: bool = subaddress_unlocked.account_index == subaddress_before.account_index
                subaddr_eq: bool = subaddress_unlocked.index == subaddress_before.index
                if account_eq and subaddr_eq:
                    swept = True
                    break

            # assert unlocked balance is less than max fee if swept, unchanged otherwise
            if swept:
                assert subaddress_after.unlocked_balance < TxWalletUtils.MAX_FEE
            else:
                assert subaddress_before.unlocked_balance == subaddress_after.unlocked_balance

    # Can sweep accounts
    @pytest.mark.skipif(TestUtils.TEST_RESETS is False, reason="TEST_RESETS disabled")
    def test_sweep_accounts(self, wallet: MoneroWallet) -> None:
        TestUtils.WALLET_TX_TRACKER.wait_for_txs_to_clear_pool(wallet)
        NUM_ACCOUNTS_TO_SWEEP: int = 1

        # collect accounts with sufficient balance and unlocked balance to cover the fee
        accounts: list[MoneroAccount] = wallet.get_accounts(True)
        accounts_balance: list[MoneroAccount] = []
        accounts_unlocked: list[MoneroAccount] = []
        for account in accounts:
            if account.index == 0:
                # skip default account
                continue
            assert account.balance is not None
            assert account.unlocked_balance is not None
            if account.balance > TxWalletUtils.MAX_FEE:
                accounts_balance.append(account)
            if account.unlocked_balance > TxWalletUtils.MAX_FEE:
                accounts_unlocked.append(account)

        # test requires at least one more accounts than the number being swept to verify it does not change

        msg: str =  f"Test requires balance greater than the fee in at least {NUM_ACCOUNTS_TO_SWEEP + 1} non-default accounts; run send-to-multiple tests"
        assert len(accounts_balance) >= NUM_ACCOUNTS_TO_SWEEP + 1, msg
        assert len(accounts_unlocked) >= NUM_ACCOUNTS_TO_SWEEP + 1, "Wallet is waiting on unlocked funds"

        # sweep from first unlocked accounts
        for i in range(NUM_ACCOUNTS_TO_SWEEP):
            # sweep unlocked account
            unlocked_account: MoneroAccount = accounts_unlocked[i]
            assert unlocked_account.index is not None
            config: MoneroTxConfig = MoneroTxConfig()
            config.address = wallet.get_primary_address()
            config.account_index = unlocked_account.index
            config.relay = True
            txs: list[MoneroTxWallet] = wallet.sweep_unlocked(config)

            # test transactions
            assert len(txs) > 0
            for tx in txs:
                ctx: TxContext = TxContext()
                ctx.wallet = wallet
                ctx.config = config
                ctx.is_send_response = True
                ctx.is_sweep_response = True
                TxWalletUtils.test_tx_wallet(tx, ctx)
                assert tx.tx_set is not None
                assert tx in tx.tx_set.txs

            # assert unlocked account balance less than max fee
            account: MoneroAccount = wallet.get_account(unlocked_account.index)

        # test accounts after sweeping
        accounts_after: list[MoneroAccount] = wallet.get_accounts(True)
        assert len(accounts) == len(accounts_after)
        for i, account_before in enumerate(accounts):
            account_after: MoneroAccount = accounts_after[i]
            assert account_after.unlocked_balance is not None

            # determine if account was swept
            swept: bool = False
            for j in range(NUM_ACCOUNTS_TO_SWEEP):
                account_unlocked: MoneroAccount = accounts_unlocked[j]
                if account_unlocked.index == account_before.index:
                    swept = True
                    break

            # assert unlocked balance is less than max fee if swept, unchanged otherwise
            if swept:
                assert account_after.unlocked_balance < TxWalletUtils.MAX_FEE
            else:
                assert account_after.unlocked_balance == account_after.unlocked_balance

    # Can sweep the whole wallet by accounts
    @pytest.mark.skipif(TestUtils.TEST_RESETS is False, reason="TEST_RESETS disabled")
    def test_sweep_wallet_by_accounts(self, wallet: MoneroWallet) -> None:
        IntegrationTestUtils.fund_wallet_and_wait_for_unlocked(wallet)
        WalletSendUtils.test_sweep_wallet(wallet, None)

    # Can sweep the whole wallet by subaddresses
    @pytest.mark.skipif(TestUtils.TEST_RESETS is False, reason="TEST_RESETS disabled")
    @pytest.mark.xfail(reason="TODO wallet2 error: No unlocked balance in the specified subaddress(es)")
    def test_sweep_wallet_by_subaddresses(self, wallet: MoneroWallet) -> None:
        IntegrationTestUtils.fund_wallet_and_wait_for_unlocked(wallet)
        WalletSendUtils.test_sweep_wallet(wallet, True)


@pytest.mark.integration
class TestMoneroWalletFullSweep(FullWalletSupport, BaseTestMoneroWalletSweep):
    """Full wallet sweep integration tests."""


@pytest.mark.integration
class TestMoneroWalletRpcSweep(RpcWalletSupport, BaseTestMoneroWalletSweep):
    """Rpc wallet sweep integration tests."""


@pytest.mark.unit
class TestMoneroWalletKeysSweep(KeysWalletSupport, BaseTestMoneroWalletSweep):
    """Keys-only wallet sweep unit tests."""

    @pytest.mark.not_supported
    @override
    def test_sweep_outputs(self, wallet: MoneroWallet) -> None:
        return super().test_sweep_outputs(wallet)

    @pytest.mark.not_supported
    @override
    def test_sweep_dust_no_relay(self, wallet: MoneroWallet) -> None:
        return super().test_sweep_dust_no_relay(wallet)

    @pytest.mark.not_supported
    @override
    def test_sweep_dust(self, wallet: MoneroWallet) -> None:
        return super().test_sweep_dust(wallet)

    @pytest.mark.not_supported
    @override
    def test_sweep_subaddresses(self, wallet: MoneroWallet) -> None:
        return super().test_sweep_subaddresses(wallet)

    @pytest.mark.not_supported
    @override
    def test_sweep_accounts(self, wallet: MoneroWallet) -> None:
        return super().test_sweep_accounts(wallet)

    @pytest.mark.not_supported
    @override
    def test_sweep_wallet_by_accounts(self, wallet: MoneroWallet) -> None:
        return super().test_sweep_wallet_by_accounts(wallet)

    @pytest.mark.not_supported
    @override
    def test_sweep_wallet_by_subaddresses(self, wallet: MoneroWallet) -> None:
        return super().test_sweep_wallet_by_subaddresses(wallet)
