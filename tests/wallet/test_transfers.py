from __future__ import annotations

import logging

import pytest
from monero import (
    MoneroIncomingTransfer,
    MoneroOutgoingTransfer,
    MoneroTransfer,
    MoneroTransferQuery,
    MoneroTxQuery,
    MoneroTxWallet,
    MoneroWallet,
)
from typing_extensions import override

from utils import TestUtils, TransferUtils, WalletTransfersUtils, WalletTxsUtils
from .base_test_monero_wallet import BaseTestMoneroWallet
from .wallet_support import FullWalletSupport, RpcWalletSupport, KeysWalletSupport

logger: logging.Logger = logging.getLogger("TestMoneroWalletTransfers")


class BaseTestMoneroWalletTransfers(BaseTestMoneroWallet):
    """Common wallet transfers tests."""

    # Can get transfers in the wallet, accounts, and subaddresses
    @pytest.mark.skipif(TestUtils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_get_transfers(self, wallet: MoneroWallet) -> None:
        # get all transfers
        WalletTransfersUtils.get_and_test_transfers(wallet, None, None, True)

        # get transfers by account index
        non_default_incoming: bool = False
        for account in wallet.get_accounts(True):
            transfer_query: MoneroTransferQuery = MoneroTransferQuery()
            transfer_query.account_index = account.index
            account_transfers: list[MoneroTransfer] = WalletTransfersUtils.get_and_test_transfers(wallet, transfer_query, None, None)
            for transfer in account_transfers:
                assert transfer.account_index == account.index

            # get transfers by subaddress index
            subaddress_transfers: list[MoneroTransfer] = []
            for subaddress in account.subaddresses:
                subaddress_query: MoneroTransferQuery = MoneroTransferQuery()
                subaddress_query.account_index = subaddress.account_index
                subaddress_query.subaddress_index = subaddress.index
                transfers: list[MoneroTransfer] = WalletTransfersUtils.get_and_test_transfers(wallet, subaddress_query, None, None)

                for transfer in transfers:
                    # test account and subaddress indices
                    assert subaddress.account_index == transfer.account_index
                    if transfer.is_incoming() is True:
                        assert isinstance(transfer, MoneroIncomingTransfer)
                        assert subaddress.index == transfer.subaddress_index
                        if transfer.account_index != 0 and transfer.subaddress_index != 0:
                            non_default_incoming = True
                    else:
                        assert isinstance(transfer, MoneroOutgoingTransfer)
                        assert subaddress.index in transfer.subaddress_indices
                        if transfer.account_index != 0:
                            for subaddr_idx in transfer.subaddress_indices:
                                if subaddr_idx > 0:
                                    non_default_incoming = True
                                    break

                    # don't add duplicates
                    # TODO monero-wallet-rpc: duplicate outgoing transfers returned for different
                    # subaddress indices, way to return outgoing subaddress indices?

                    found: bool = False
                    for subaddress_transfer in subaddress_transfers:
                        assert transfer.tx is not None
                        assert subaddress_transfer.tx is not None
                        eq_hash: bool = transfer.tx.hash == subaddress_transfer.tx.hash
                        if transfer.serialize() == subaddress_transfer.serialize() and eq_hash:
                            found = True
                            break

                    if not found:
                        subaddress_transfers.append(transfer)

            assert len(account_transfers) == len(subaddress_transfers)

            # collect unique subaddress indices
            subaddress_indices: set[int] = set()
            for transfer in subaddress_transfers:
                if transfer.is_incoming():
                    assert isinstance(transfer, MoneroIncomingTransfer)
                    assert transfer.subaddress_index is not None
                    subaddress_indices.add(transfer.subaddress_index)
                else:
                    assert isinstance(transfer, MoneroOutgoingTransfer)
                    for idx in transfer.subaddress_indices:
                        subaddress_indices.add(idx)

            # get and test transfers by subaddress indices
            transfer_query = MoneroTransferQuery()
            transfer_query.account_index = account.index
            for idx in subaddress_indices:
                transfer_query.subaddress_indices.append(idx)

            transfers = WalletTransfersUtils.get_and_test_transfers(wallet, transfer_query, None, None)
            # TODO monero-wallet-rpc: these may not be equal because outgoing transfers are always from subaddress 0 (#5171)
            # and/or incoming transfers from/to same account are occluded (#4500)
            assert len(subaddress_transfers) == len(transfers)
            for transfer in transfers:
                assert transfer.account_index == account.index
                if transfer.is_incoming():
                    assert isinstance(transfer, MoneroIncomingTransfer)
                    assert transfer.subaddress_index in subaddress_indices
                else:
                    assert isinstance(transfer, MoneroOutgoingTransfer)
                    intersections: set[int] = set(subaddress_indices)
                    overlap: set[int] = intersections.intersection(transfer.subaddress_indices)
                    assert overlap is not None and len(overlap) > 0, "Subaddresses must overlap"

        # ensure transfer found with non-zero account and subaddress indices
        assert non_default_incoming, "No transfers found in non-default account and subaddress; run send-to-multiple tests"

    # Can get transfers with additional configuration
    @pytest.mark.skipif(TestUtils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_get_transfers_with_query(self, wallet: MoneroWallet) -> None:
        # get incoming transfers
        query: MoneroTransferQuery = MoneroTransferQuery()
        query.incoming = True
        transfers: list[MoneroTransfer] = WalletTransfersUtils.get_and_test_transfers(wallet, query, None, True)
        for transfer in transfers:
            assert transfer.is_incoming()

        # get outgoing transfers
        query = MoneroTransferQuery()
        query.outgoing = True
        transfers = WalletTransfersUtils.get_and_test_transfers(wallet, query, None, True)
        for transfer in transfers:
            assert transfer.is_outgoing()

        # get confirmed transfers to account 0
        query = MoneroTransferQuery()
        query.account_index = 0
        query.tx_query = MoneroTxQuery()
        query.tx_query.is_confirmed = True
        transfers = WalletTransfersUtils.get_and_test_transfers(wallet, query, None, True)
        for transfer in transfers:
            assert transfer.account_index == 0
            assert transfer.tx is not None
            assert transfer.tx.is_confirmed is True

        # get confirmed transfers to (1, 2)
        query = MoneroTransferQuery()
        query.account_index = 1
        query.subaddress_index = 2
        query.tx_query = MoneroTxQuery()
        query.tx_query.is_confirmed = True
        transfers = WalletTransfersUtils.get_and_test_transfers(wallet, query, None, True)
        for transfer in transfers:
            assert transfer.account_index == 1
            if transfer.is_incoming():
                assert isinstance(transfer, MoneroIncomingTransfer)
                assert transfer.subaddress_index == 2
            else:
                assert isinstance(transfer, MoneroOutgoingTransfer)
                assert 2 in transfer.subaddress_indices

            assert transfer.tx is not None
            assert transfer.tx.is_confirmed is True

        # get transfers in the tx pool
        query = MoneroTransferQuery()
        query.tx_query = MoneroTxQuery()
        query.tx_query.in_tx_pool = True
        transfers = WalletTransfersUtils.get_and_test_transfers(wallet, query, None, None)
        for transfer in transfers:
            assert transfer.tx is not None
            assert transfer.tx.in_tx_pool is True

        # get random transactions
        txs: list[MoneroTxWallet] = WalletTxsUtils.get_random_transactions(wallet, None, 3, 5)

        # get transfers with a tx hash
        tx_hashes: list[str] = []
        for tx in txs:
            assert tx.hash is not None
            tx_hashes.append(tx.hash)
            query = MoneroTransferQuery()
            query.tx_query = MoneroTxQuery()
            query.tx_query.hash = tx.hash
            transfers = WalletTransfersUtils.get_and_test_transfers(wallet, query, None, True)
            for transfer in transfers:
                assert transfer.tx is not None
                assert tx.hash == transfer.tx.hash

        # get transfers with tx hashes
        query = MoneroTransferQuery()
        query.tx_query = MoneroTxQuery()
        query.tx_query.hashes = tx_hashes
        transfers = WalletTransfersUtils.get_and_test_transfers(wallet, query, None, True)
        for transfer in transfers:
            assert transfer.tx is not None
            assert transfer.tx.hash is not None
            assert transfer.tx.hash in tx_hashes

        # TODO test that transfers with the same tx_hash have same tx reference
        # TODO test transfers destinations

        # get transfers with pre-built query that are confirmed and have outgoing destinations
        transfer_query: MoneroTransferQuery = MoneroTransferQuery()
        transfer_query.outgoing = True
        transfer_query.has_destinations = True
        transfer_query.tx_query = MoneroTxQuery()
        transfer_query.tx_query.is_confirmed = True
        transfers = WalletTransfersUtils.get_and_test_transfers(wallet, transfer_query, None, None)
        for transfer in transfers:
            assert transfer.is_outgoing() is True
            assert isinstance(transfer, MoneroOutgoingTransfer)
            assert len(transfer.destinations) > 0
            assert transfer.tx is not None
            assert transfer.tx.is_confirmed is True

        # get incoming transfers to account 0 which has outgoing transfers (i.e. originated from the same wallet)
        query = MoneroTransferQuery()
        query.account_index = 1
        query.incoming = True
        query.tx_query = MoneroTxQuery()
        query.tx_query.is_outgoing = True
        transfers = wallet.get_transfers(query)
        assert len(transfers) > 0
        for transfer in transfers:
            assert transfer.is_incoming() is True
            assert transfer.account_index == 1
            assert transfer.tx is not None
            assert transfer.tx.is_outgoing is True
            assert transfer.tx.outgoing_transfer is None

        # get incoming transfers to a spefici address
        subaddress: str = wallet.get_address(1, 0)
        query = MoneroTransferQuery()
        query.incoming = True
        query.address = subaddress
        transfers = wallet.get_transfers(query)
        assert len(transfers) > 0
        for transfer in transfers:
            assert isinstance(transfer, MoneroIncomingTransfer)
            assert transfer.account_index == 1
            assert transfer.subaddress_index == 0
            assert transfer.address == subaddress

    # Can get incoming and outgoing transfers using convenience methods
    @pytest.mark.skipif(TestUtils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_get_incoming_outgoing_transfers(self, wallet: MoneroWallet) -> None:
        # get incoming transfers
        in_transfers: list[MoneroIncomingTransfer] = wallet.get_incoming_transfers()
        assert len(in_transfers) > 0
        for in_transfer in in_transfers:
            assert in_transfer.is_incoming() is True
            TransferUtils.test_transfer(in_transfer, None)

        # get incoming transfers with query
        amount: int | None = in_transfers[0].amount
        account_idx: int | None = in_transfers[0].account_index
        subaddress_idx: int | None = in_transfers[0].subaddress_index
        assert account_idx is not None
        assert subaddress_idx is not None
        query: MoneroTransferQuery = MoneroTransferQuery()
        query.amount = amount
        query.account_index = account_idx
        query.subaddress_index = subaddress_idx
        query.tx_query = MoneroTxQuery()
        query.tx_query.is_confirmed = True
        in_transfers = wallet.get_incoming_transfers(query)
        assert len(in_transfers) > 0
        for in_transfer in in_transfers:
            assert in_transfer.is_incoming() is True
            assert in_transfer.amount == amount
            assert in_transfer.account_index == account_idx
            assert in_transfer.subaddress_index == subaddress_idx
            TransferUtils.test_transfer(in_transfer, None)

        # get incoming transfers with contradictory query
        query = MoneroTransferQuery()
        query.incoming = False
        with pytest.raises(Exception) as exc_info:
            wallet.get_incoming_transfers(query)
        assert str(exc_info.value) == "Transfer query contradicts getting incoming transfers"

        # get outgoing transfers
        out_transfers: list[MoneroOutgoingTransfer] = wallet.get_outgoing_transfers()
        assert len(out_transfers) > 0
        for out_transfer in out_transfers:
            assert out_transfer.is_outgoing() is True
            TransferUtils.test_transfer(out_transfer, None)

        # get outgoing transfers with query
        query = MoneroTransferQuery()
        query.account_index = account_idx
        query.subaddress_index = subaddress_idx
        out_transfers = wallet.get_outgoing_transfers(query)
        assert len(out_transfers) > 0
        for out_transfer in out_transfers:
            assert out_transfer.is_outgoing() is True
            assert out_transfer.account_index == account_idx
            assert subaddress_idx in out_transfer.subaddress_indices
            TransferUtils.test_transfer(out_transfer, None)

        # get outgoing transfers with contradictory query
        query = MoneroTransferQuery()
        query.outgoing = False
        with pytest.raises(Exception) as exc_info:
            wallet.get_outgoing_transfers(query)
        assert str(exc_info.value) == "Transfer query contradicts getting outgoing transfers"

    # Validates inputs when getting transfers
    @pytest.mark.skipif(TestUtils.TEST_NON_RELAYS is False or TestUtils.LITE_MODE, reason="TEST_NON_RELAYS disabled or LITE_MODE enabled")
    def test_validate_inputs_get_transfers(self, wallet: MoneroWallet) -> None:
        # test with invalid hash
        transfer_query: MoneroTransferQuery = MoneroTransferQuery()
        transfer_query.tx_query = MoneroTxQuery()
        transfer_query.tx_query.hash = "invalid_id"

        transfers: list[MoneroTransfer] = wallet.get_transfers(transfer_query)
        assert len(transfers) == 0

        # test invalid hash in list
        random_txs: list[MoneroTxWallet] = WalletTxsUtils.get_random_transactions(wallet, None, 3, 5)
        transfer_query.tx_query = MoneroTxQuery()
        random_hash: str | None = random_txs[0].hash
        assert random_hash is not None
        transfer_query.tx_query.hashes.append(random_hash)
        transfer_query.tx_query.hashes.append("invalid_id")

        transfers = wallet.get_transfers(transfer_query)
        assert len(transfers) > 0

        tx: MoneroTxWallet | None = transfers[0].tx
        assert tx is not None
        for transfer in transfers:
            assert transfer.tx is tx

        # test unused subaddress indices
        transfer_query = MoneroTransferQuery()
        transfer_query.account_index = 0
        transfer_query.subaddress_indices.append(1234907)
        transfers = wallet.get_transfers(transfer_query)

        # test invalid subaddress index
        transfer_query = MoneroTransferQuery()
        transfer_query.account_index = 0
        with pytest.raises(Exception):
            transfer_query.subaddress_index = -1
            wallet.get_transfers(transfer_query)


@pytest.mark.integration
class TestMoneroWalletFullTransfers(FullWalletSupport, BaseTestMoneroWalletTransfers):
    """Full wallet transfers integration tests."""


@pytest.mark.integration
class TestMoneroWalletRpcTransfers(RpcWalletSupport, BaseTestMoneroWalletTransfers):
    """Rpc wallet transfers integration tests."""


@pytest.mark.unit
class TestMoneroWalletKeysTransfers(KeysWalletSupport, BaseTestMoneroWalletTransfers):
    """Keys-only wallet transfers unit tests."""

    @pytest.mark.not_supported
    @override
    def test_get_transfers(self, wallet: MoneroWallet) -> None:
        return super().test_get_transfers(wallet)

    @pytest.mark.not_supported
    @override
    def test_validate_inputs_get_transfers(self, wallet: MoneroWallet) -> None:
        return super().test_validate_inputs_get_transfers(wallet)

    @pytest.mark.not_supported
    @override
    def test_get_transfers_with_query(self, wallet: MoneroWallet) -> None:
        return super().test_get_transfers_with_query(wallet)

    @pytest.mark.not_supported
    @override
    def test_get_incoming_outgoing_transfers(self, wallet: MoneroWallet) -> None:
        return super().test_get_incoming_outgoing_transfers(wallet)
