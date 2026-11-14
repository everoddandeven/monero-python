from __future__ import annotations

import logging
from typing import Optional

import pytest
from monero import (
    MoneroAccount,
    MoneroCheckReserve,
    MoneroCheckTx,
    MoneroDaemonRpc,
    MoneroDestination,
    MoneroSubmitTxResult,
    MoneroTransferQuery,
    MoneroTx,
    MoneroTxConfig,
    MoneroTxQuery,
    MoneroTxWallet,
    MoneroWallet,
    MoneroWalletConfig,
)
from typing_extensions import override

from utils import TestUtils, TxWalletUtils, WalletErrorUtils, WalletTestUtils, WalletTxsUtils, WalletUtils
from .base_test_monero_wallet import BaseTestMoneroWallet
from .wallet_support import FullWalletSupport, RpcWalletSupport, KeysWalletSupport

logger: logging.Logger = logging.getLogger("TestMoneroWalletProofs")


class BaseTestMoneroWalletProofs(BaseTestMoneroWallet):
    """Common wallet proofs tests."""

    # Can check a transfer using the transaction's secret key and the destination
    @pytest.mark.skipif(TestUtils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_check_tx_key(self, wallet: MoneroWallet) -> None:
        # get random txs that are confirmed and have outgoing destinations
        txs: list[MoneroTxWallet] = []
        try:
            query: MoneroTxQuery = MoneroTxQuery()
            query.is_confirmed = True
            query.transfer_query = MoneroTransferQuery()
            query.transfer_query.has_destinations = True
            txs = WalletTxsUtils.get_random_transactions(wallet, query, 1, WalletUtils.MAX_TX_PROOFS)
        except AssertionError as e:
            if "found with" in str(e):
                raise Exception("No txs with outgoing destinations found; run send tests")
            raise

        # test good checks
        assert len(txs) > 0, "No transactions found with outgoing destinations"
        for tx in txs:
            assert tx.hash is not None
            key: str = wallet.get_tx_key(tx.hash)
            assert tx.outgoing_transfer is not None
            assert len(tx.outgoing_transfer.destinations) > 0
            for destination in tx.outgoing_transfer.destinations:
                assert destination.address is not None
                check: MoneroCheckTx = wallet.check_tx_key(tx.hash, key, destination.address)
                assert destination.amount is not None
                if destination.amount > 0:
                    # TODO monero-wallet-rpc: indicates amount received amount is 0 despite transaction with transfer to this address
                    # TODO monero-wallet-rpc: returns 0-4 errors, not consistent
                    assert check.received_amount is not None
                    if check.received_amount == 0:
                        msg: str = f"WARNING: key proof indicates no funds received despite transfer (txid={tx.hash}, key={key}, address={destination.address} amount={destination.amount})"
                        logger.warning(msg)
                else:
                    assert check.received_amount == 0
                TxWalletUtils.test_check_tx(tx, check)

        # test get tx key with invalid hash
        with pytest.raises(Exception) as exc_info:
            wallet.get_tx_key("invalid_tx_id")
        WalletErrorUtils.test_invalid_tx_hash_error(exc_info.value)
        # test check with invalid tx hash
        tx: MoneroTxWallet = txs[0]
        assert tx.hash is not None
        key: str = wallet.get_tx_key(tx.hash)
        assert tx.outgoing_transfer is not None
        destination: MoneroDestination = tx.outgoing_transfer.destinations[0]
        assert destination.address is not None
        with pytest.raises(Exception) as exc_info:
            wallet.check_tx_key("invalid_tx_id", key, destination.address)
        WalletErrorUtils.test_invalid_tx_hash_error(exc_info.value)
        # test check with invalid key
        with pytest.raises(Exception) as exc_info:
            wallet.check_tx_key(tx.hash, "invalid_tx_key", destination.address)
        WalletErrorUtils.test_invalid_tx_key_error(exc_info.value)
        # test check with invalid address
        with pytest.raises(Exception) as exc_info:
            wallet.check_tx_key(tx.hash, key, "invalid_tx_address")
        WalletErrorUtils.test_invalid_address_error(exc_info.value)
        # test check with different address
        different_address: Optional[str] = None
        for a_tx in wallet.get_txs():
            if a_tx.outgoing_transfer is None or len(a_tx.outgoing_transfer.destinations) == 0:
                continue
            for a_destination in a_tx.outgoing_transfer.destinations:
                assert a_destination.address is not None
                if a_destination.address != destination.address:
                    different_address = a_destination.address
                    break

        assert different_address is not None, "Could not get a different outgoing address to test; run send tests"
        check: MoneroCheckTx = wallet.check_tx_key(tx.hash, key, different_address)
        assert check.is_good is True
        assert check.received_amount is not None
        assert check.received_amount >= 0
        TxWalletUtils.test_check_tx(tx, check)

    # Can prove a transaction by getting its signature
    @pytest.mark.skipif(TestUtils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_check_tx_proof(self, wallet: MoneroWallet) -> None:
        # get random txs with outgoing destinations
        txs: list[MoneroTxWallet] = []
        try:
            query: MoneroTxQuery = MoneroTxQuery()
            query.transfer_query = MoneroTransferQuery()
            query.transfer_query.has_destinations = True
            txs = WalletTxsUtils.get_random_transactions(wallet, query, 2, WalletUtils.MAX_TX_PROOFS)
        except Exception as e:
            if "found with" in str(e):
                raise Exception("No txs with outgoing destinations found; run send tests")
            raise

        # test good checks with messages
        for tx in txs:
            assert tx.hash is not None
            assert tx.outgoing_transfer is not None
            for destination in tx.outgoing_transfer.destinations:
                assert destination.address is not None
                signature: str = wallet.get_tx_proof(tx.hash, destination.address, "This transaction definitely happened.")
                check: MoneroCheckTx = wallet.check_tx_proof(tx.hash, destination.address, "This transaction definitely happened.", signature)
                TxWalletUtils.test_check_tx(tx, check)

        # test good check without message
        tx: MoneroTx = txs[0]
        assert tx.hash is not None
        assert tx.outgoing_transfer is not None
        assert len(tx.outgoing_transfer.destinations) > 0
        destination: MoneroDestination = tx.outgoing_transfer.destinations[0]
        assert destination.address is not None
        signature: str = wallet.get_tx_proof(tx.hash, destination.address)
        check: MoneroCheckTx = wallet.check_tx_proof(tx.hash, destination.address, '', signature)
        TxWalletUtils.test_check_tx(tx, check)

        # test get proof with invalid hash
        with pytest.raises(Exception) as exc_info:
            wallet.get_tx_proof("invalid_tx_id", destination.address)
        WalletErrorUtils.test_invalid_tx_hash_error(exc_info.value)
        # test check tx proof with invalid tx hash
        with pytest.raises(Exception) as exc_info:
            wallet.check_tx_proof("invalid_tx_id", destination.address, '', signature)
        WalletErrorUtils.test_invalid_tx_hash_error(exc_info.value)
        # test check with invalid address
        with pytest.raises(Exception) as exc_info:
            wallet.check_tx_proof(tx.hash, "invalid_tx_address", '', signature)
        WalletErrorUtils.test_invalid_address_error(exc_info.value)
        # test check with wrong message
        signature = wallet.get_tx_proof(tx.hash, destination.address, "This is the right message")
        check = wallet.check_tx_proof(tx.hash, destination.address, "This is the wrong message", signature)
        assert check.is_good is False
        TxWalletUtils.test_check_tx(tx, check)

        # test check with wrong signature
        other_tx: MoneroTxWallet = txs[1]
        assert other_tx.hash is not None
        assert other_tx.outgoing_transfer is not None
        assert len(other_tx.outgoing_transfer.destinations) > 0
        address: Optional[str] = other_tx.outgoing_transfer.destinations[0].address
        assert address is not None
        wrong_signature: str = wallet.get_tx_proof(other_tx.hash, address, "This is the right message")
        try:
            check = wallet.check_tx_proof(tx.hash, destination.address, "This is the right message", wrong_signature)
            assert check.is_good is False
        except Exception as e:
            WalletErrorUtils.test_invalid_signature_error(e)

        # test check with empty signature
        try:
            check = wallet.check_tx_proof(tx.hash, destination.address, "This is the right message", "")
            assert check.is_good is False
        except Exception as e:
            assert str(e) == "Must provide signature to check tx proof"

    # Can prove a spend using a generated signature and no destination public address
    @pytest.mark.skipif(TestUtils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disablde")
    def test_check_spend_proof(self, wallet: MoneroWallet) -> None:
        # get random confirmed outgoing txs
        query: MoneroTxQuery = MoneroTxQuery()
        query.is_incoming = False
        query.in_tx_pool = False
        query.is_failed = False
        txs: list[MoneroTxWallet] = WalletTxsUtils.get_random_transactions(wallet, query, 2, WalletUtils.MAX_TX_PROOFS)
        for tx in txs:
            assert tx.is_confirmed is True
            assert len(tx.incoming_transfers) == 0
            assert tx.outgoing_transfer is not None

        # test good checks with messages
        for tx in txs:
            assert tx.hash is not None
            logger.debug(f"Getting tx hash {tx.hash} proof")
            signature: str = wallet.get_spend_proof(tx.hash, "I am a message.")
            logger.debug(f"Checking tx hash {tx.hash} proof")
            result: bool = wallet.check_spend_proof(tx.hash, "I am a message.", signature)
            assert result is True

        # test good check without message
        tx: MoneroTxWallet = txs[0]
        assert tx.hash is not None
        signature: str = wallet.get_spend_proof(tx.hash)
        result: bool = wallet.check_spend_proof(tx.hash, '', signature)
        assert result is True

        # test get proof with invalid hash
        with pytest.raises(Exception) as exc_info:
            wallet.get_spend_proof("invalid_tx_id")
        WalletErrorUtils.test_invalid_tx_hash_error(exc_info.value)
        # test check with invalid tx hash
        with pytest.raises(Exception) as exc_info:
            wallet.check_spend_proof("invalid_tx_id", '', signature)
        WalletErrorUtils.test_invalid_tx_hash_error(exc_info.value)
        # test check with invalid message
        signature = wallet.get_spend_proof(tx.hash, "This is the right message")
        result = wallet.check_spend_proof(tx.hash, "This is the wrong message", signature)
        assert result is False

        # test check with wrong signature
        other_tx: MoneroTxWallet = txs[1]
        assert other_tx.hash is not None
        signature = wallet.get_spend_proof(other_tx.hash, "This is the right message")
        result = wallet.check_spend_proof(tx.hash, "This is the right message", signature)
        assert result is False

    # Can prove reserves in the wallet
    @pytest.mark.skipif(TestUtils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disablde")
    def test_get_reserve_proof_wallet(self, wallet: MoneroWallet) -> None:
        # get proof of entire wallet
        signature: str = wallet.get_reserve_proof_wallet("Test message")

        # check proof of entire wallet
        check: MoneroCheckReserve = wallet.check_reserve_proof(wallet.get_primary_address(), "Test message", signature)
        assert check.is_good is True
        TxWalletUtils.test_check_reserve(check)
        balance: int = wallet.get_balance()
        if balance != check.total_amount:
            # TODO monero-wallet-rpc: this check fails with unconfirmed txs
            query: MoneroTxQuery = MoneroTxQuery()
            query.in_tx_pool = True
            unconfirmed_txs: list[MoneroTxWallet] = wallet.get_txs(query)
            assert len(unconfirmed_txs) > 0, "Reserve amount must equal balance unless wallet has unconfirmed txs"

        # test different wallet address
        different_address: str = WalletTestUtils.get_external_wallet_address()
        with pytest.raises(Exception) as exc_info:
            wallet.check_reserve_proof(different_address, "Test message", signature)
        WalletErrorUtils.test_no_subaddress_error(exc_info.value)
        # test subaddress
        with pytest.raises(Exception) as exc_info:
            address: Optional[str] = wallet.get_subaddress(0, 1).address
            assert address is not None
            wallet.check_reserve_proof(address, "Test message", signature)
        WalletErrorUtils.test_no_subaddress_error(exc_info.value)
        # test wrong message
        check = wallet.check_reserve_proof(wallet.get_primary_address(), "Wrong message", signature)
        # TODO: specifically test reserve checks, probably separate objects
        assert check.is_good is False
        TxWalletUtils.test_check_reserve(check)

        # test wrong signature
        with pytest.raises(Exception) as exc_info:
            wallet.check_reserve_proof(wallet.get_primary_address(), "Test message", "wrong signature")
        WalletErrorUtils.test_signature_header_error(exc_info.value)

    # Can prove reserves in an account
    @pytest.mark.skipif(TestUtils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disablde")
    def test_get_reserve_proof_account(self, wallet: MoneroWallet) -> None:
        # test proofs of accounts
        num_non_zero_tests: int = 0
        msg: str = "Test message"
        accounts: list[MoneroAccount] = wallet.get_accounts()
        signature: str = ''
        for account in accounts:
            assert account.balance is not None
            assert account.index is not None
            if account.balance > 0:
                check_amount: int = int(account.balance/2)
                signature = wallet.get_reserve_proof_account(account.index, check_amount, msg)
                check: MoneroCheckReserve = wallet.check_reserve_proof(wallet.get_primary_address(), msg, signature)
                assert check.is_good is True
                TxWalletUtils.test_check_reserve(check)
                assert check.total_amount is not None
                assert check.total_amount >= 0
                num_non_zero_tests += 1
            else:
                with pytest.raises(Exception) as exc_info:
                    wallet.get_reserve_proof_account(account.index, account.balance, msg)
                logger.debug(str(exc_info.value))

                with pytest.raises(Exception) as exc_info:
                    wallet.get_reserve_proof_account(account.index, TxWalletUtils.MAX_FEE, msg)
                logger.debug(str(exc_info.value))

        assert num_non_zero_tests > 1, "Must have more than one account with non-zero balance; run send-to-multiple tests"

        # test error when not enough balance for requested minimum reserve amount
        # TODO monero-project#6595: an over-balance reserve proof should be rejected but isn't
        account: MoneroAccount = accounts[0]
        assert account.balance is not None
        amount: int = account.balance + TxWalletUtils.MAX_FEE
        try:
            proof: str = wallet.get_reserve_proof_account(0, amount, "Test message")
            reserve: MoneroCheckReserve = wallet.check_reserve_proof(wallet.get_primary_address(), "Test message", proof)
            logger.warning(f"Got reserve proof despite insufficient balance: {reserve.serialize()}")
        except Exception as e:
            logger.debug(str(e))

        # test different wallet address
        different_address: str = WalletTestUtils.get_external_wallet_address()
        with pytest.raises(Exception) as exc_info:
            wallet.check_reserve_proof(different_address, "Test message", signature)
        logger.debug(str(exc_info.value))

        # test subaddress
        address: Optional[str] = wallet.get_subaddress(0, 1).address
        assert address is not None
        with pytest.raises(Exception) as exc_info:
            wallet.check_reserve_proof(address, "Test message", signature)
        logger.debug(str(exc_info.value))

        # test wrong message
        check: MoneroCheckReserve = wallet.check_reserve_proof(wallet.get_primary_address(), "Wrong message", signature)
        # TODO: specifically test reserve checks, probably separate objects
        assert check.is_good is False
        TxWalletUtils.test_check_reserve(check)

        # test wrong signature
        with pytest.raises(Exception) as exc_info:
            wallet.check_reserve_proof(wallet.get_primary_address(), "Test message", "wrong signature")
        logger.debug(str(exc_info.value))

    # Can prove unrelayed txs
    @pytest.mark.skipif(TestUtils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_prove_unrelayed_txs(self, daemon: MoneroDaemonRpc, wallet: MoneroWallet) -> None:
        # create unrelayed tx to verify
        address1: str = WalletTestUtils.get_external_wallet_address()
        address2: str = wallet.get_address(0, 0)
        address3: str = wallet.get_address(1, 0)
        tx_config: MoneroTxConfig = MoneroTxConfig()
        tx_config.account_index = 0
        tx_config.destinations.append(MoneroDestination(address1, TxWalletUtils.MAX_FEE))
        tx_config.destinations.append(MoneroDestination(address2, TxWalletUtils.MAX_FEE * 2))
        tx_config.destinations.append(MoneroDestination(address3, TxWalletUtils.MAX_FEE * 3))
        tx: MoneroTxWallet = wallet.create_tx(tx_config)
        assert tx.full_hex is not None
        assert tx.hash is not None
        assert tx.key is not None

        # submit tx to daemon but do not relay
        result: MoneroSubmitTxResult = daemon.submit_tx_hex(tx.full_hex, True)
        assert result.is_good

        # create random wallet to verify transfers
        verifying_wallet: MoneroWallet = self._create_wallet(MoneroWalletConfig())

        try:
            # verify transfer 1
            check: MoneroCheckTx = verifying_wallet.check_tx_key(tx.hash, tx.key, address1)
            assert check.is_good
            assert check.in_tx_pool is True
            assert check.num_confirmations == 0
            assert check.received_amount == TxWalletUtils.MAX_FEE

            # verify transfer 2
            check = verifying_wallet.check_tx_key(tx.hash, tx.key, address2)
            assert check.is_good
            assert check.in_tx_pool is True
            assert check.num_confirmations == 0
            # + change amount
            assert check.received_amount is not None
            assert check.received_amount >= TxWalletUtils.MAX_FEE * 2

            # verify transfer 3
            check = verifying_wallet.check_tx_key(tx.hash, tx.key, address3)
            assert check.is_good
            assert check.in_tx_pool is True
            assert check.num_confirmations == 0
            assert TxWalletUtils.MAX_FEE * 3 == check.received_amount
        finally:
            # cleanup, otherwise it permanently ties up the dest outputs for entire session
            daemon.flush_tx_pool(tx.hash)
            self._close_wallet(verifying_wallet)


@pytest.mark.integration
class TestMoneroWalletFullProofs(FullWalletSupport, BaseTestMoneroWalletProofs):
    """Full wallet proofs integration tests."""


@pytest.mark.integration
class TestMoneroWalletRpcProofs(RpcWalletSupport, BaseTestMoneroWalletProofs):
    """Rpc wallet proofs integration tests."""


@pytest.mark.unit
class TestMoneroWalletKeysProofs(KeysWalletSupport, BaseTestMoneroWalletProofs):
    """Keys-only wallet proofs unit tests."""

    @pytest.mark.not_supported
    @override
    def test_check_tx_key(self, wallet: MoneroWallet) -> None:
        return super().test_check_tx_key(wallet)

    @pytest.mark.not_supported
    @override
    def test_check_tx_proof(self, wallet: MoneroWallet) -> None:
        return super().test_check_tx_proof(wallet)

    @pytest.mark.not_supported
    @override
    def test_check_spend_proof(self, wallet: MoneroWallet) -> None:
        return super().test_check_spend_proof(wallet)

    @pytest.mark.not_supported
    @override
    def test_get_reserve_proof_wallet(self, wallet: MoneroWallet) -> None:
        return super().test_get_reserve_proof_wallet(wallet)

    @pytest.mark.not_supported
    @override
    def test_get_reserve_proof_account(self, wallet: MoneroWallet) -> None:
        return super().test_get_reserve_proof_account(wallet)

    @pytest.mark.not_supported
    @override
    def test_prove_unrelayed_txs(self, daemon: MoneroDaemonRpc, wallet: MoneroWallet) -> None:
        return super().test_prove_unrelayed_txs(daemon, wallet)
