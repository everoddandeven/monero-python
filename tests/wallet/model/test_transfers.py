from __future__ import annotations

import logging

import pytest
from monero import (
    IncomingTransferComparator,
    MoneroDestination,
    MoneroIncomingTransfer,
    MoneroOutgoingTransfer,
    MoneroTxWallet,
)

from utils import AssertUtils, BaseTestClass, TestUtils

logger: logging.Logger = logging.getLogger("TestMoneroWalletModelTransfers")


@pytest.mark.unit
class TestMoneroWalletModelTransfers(BaseTestClass):
    """Wallet transfer model unit tests."""

    def test_incoming_transfer_deserialize(self) -> None:
        transfer: MoneroIncomingTransfer = MoneroIncomingTransfer()
        transfer.amount = 500000
        transfer.account_index = 0
        transfer.subaddress_index = 1
        transfer.address = TestUtils.ADDRESS
        transfer.num_suggested_confirmations = 10
        AssertUtils.assert_serialization_integrity(transfer)

    def test_outgoing_transfer_deserialize(self) -> None:
        transfer: MoneroOutgoingTransfer = MoneroOutgoingTransfer()
        transfer.amount = 500000
        transfer.account_index = 0
        transfer.subaddress_indices = [0, 1]
        transfer.addresses = [TestUtils.ADDRESS]
        transfer.destinations = [MoneroDestination(TestUtils.ADDRESS, 500000)]
        AssertUtils.assert_serialization_integrity(transfer)

    def test_incoming_transfer_copy(self) -> None:
        transfer: MoneroIncomingTransfer = MoneroIncomingTransfer()
        transfer.amount = 500000
        transfer.account_index = 0
        transfer.subaddress_index = 1
        transfer.address = TestUtils.ADDRESS
        transfer.num_suggested_confirmations = 10

        copy: MoneroIncomingTransfer = transfer.copy()
        assert copy is not transfer
        assert copy.serialize() == transfer.serialize()

    def test_incoming_transfer_merge(self) -> None:
        a: MoneroIncomingTransfer = MoneroIncomingTransfer()
        a.amount = 500000
        a.account_index = 0
        a.subaddress_index = 1
        # a.tx is left unset on both sides so merge() won't recurse into tx merge

        b: MoneroIncomingTransfer = a.copy()
        b.address = TestUtils.ADDRESS  # a.address is unset -> merge fills the gap
        a.merge(b)
        assert a.address == TestUtils.ADDRESS

    def test_incoming_transfer_merge_recurses_into_tx_merge(self) -> None:
        tx_a: MoneroTxWallet = MoneroTxWallet()
        tx_a.hash = "a" * 64
        tx_a.is_confirmed = True

        tx_b: MoneroTxWallet = MoneroTxWallet()
        tx_b.hash = "a" * 64
        tx_b.is_confirmed = True
        tx_b.num_confirmations = 9  # tx_a's num_confirmations is unset -> merge fills the gap

        a: MoneroIncomingTransfer = MoneroIncomingTransfer()
        a.tx = tx_a
        a.account_index = 0
        a.amount = 100

        b: MoneroIncomingTransfer = MoneroIncomingTransfer()
        b.tx = tx_b
        b.account_index = 0
        b.amount = 100

        # transfers on different txs -> merge delegates to tx merge (which comes back to merging transfers)
        a.merge(b)
        assert tx_a.num_confirmations == 9

    def test_incoming_transfer_merge_zero_amount_conflict_keeps_original(self) -> None:
        tx: MoneroTxWallet = MoneroTxWallet()
        tx.hash = "a" * 64

        a: MoneroIncomingTransfer = MoneroIncomingTransfer()
        a.tx = tx
        a.account_index = 0
        a.amount = 500

        b: MoneroIncomingTransfer = MoneroIncomingTransfer()
        b.tx = tx
        b.account_index = 0
        b.amount = 0

        # conflicting amounts where one side is 0 are a known monero-project quirk (failed tx in
        # pool): merge() warns and leaves the amount as-is rather than reconciling it
        a.merge(b)
        assert a.amount == 500

    def test_incoming_transfer_lt_comparator(self) -> None:
        t1: MoneroIncomingTransfer = MoneroIncomingTransfer()
        t1.tx = MoneroTxWallet()
        t1.account_index = 0
        t1.subaddress_index = 0

        t2: MoneroIncomingTransfer = MoneroIncomingTransfer()
        t2.tx = MoneroTxWallet()
        t2.account_index = 0
        t2.subaddress_index = 1

        assert t1 < t2
        assert not (t2 < t1)
        assert IncomingTransferComparator.compare(t1, t2)
        assert not IncomingTransferComparator.compare(t2, t1)

        transfers: list[MoneroIncomingTransfer] = [t2, t1]
        transfers.sort()
        assert transfers[0] is t1
        assert transfers[1] is t2

    def test_outgoing_transfer_copy(self) -> None:
        transfer: MoneroOutgoingTransfer = MoneroOutgoingTransfer()
        transfer.amount = 500000
        transfer.account_index = 0
        transfer.addresses = [TestUtils.ADDRESS]
        transfer.subaddress_indices = [0]
        transfer.destinations = [MoneroDestination(TestUtils.ADDRESS, 500000)]

        copy: MoneroOutgoingTransfer = transfer.copy()
        assert copy is not transfer
        assert copy.serialize() == transfer.serialize()

    def test_outgoing_transfer_merge(self) -> None:
        a: MoneroOutgoingTransfer = MoneroOutgoingTransfer()
        a.amount = 500000
        a.account_index = 0
        # a.addresses/subaddress_indices/destinations left empty on both sides so far

        b: MoneroOutgoingTransfer = a.copy()
        b.addresses = [TestUtils.ADDRESS]
        b.subaddress_indices = [0]
        b.destinations = [MoneroDestination(TestUtils.ADDRESS, 500000)]
        a.merge(b)  # a's lists are empty -> merge adopts b's
        assert a.addresses == [TestUtils.ADDRESS]
        assert a.subaddress_indices == [0]
        assert len(a.destinations) == 1

    def test_outgoing_transfer_merge_destinations_with_unset_fields(self) -> None:
        # destinations with unset address/amount are a reachable state; merge()
        # must compare them without dereferencing the empty optionals
        a: MoneroOutgoingTransfer = MoneroOutgoingTransfer()
        a.amount = 500000
        a.account_index = 0
        a.destinations = [MoneroDestination()]
        b: MoneroOutgoingTransfer = a.copy()
        b.destinations = [MoneroDestination()]
        a.merge(b)  # equal (empty) destinations -> no error
        assert len(a.destinations) == 1

    def test_outgoing_transfer_merge_conflicting_destinations_raises(self) -> None:
        a: MoneroOutgoingTransfer = MoneroOutgoingTransfer()
        a.amount = 500000
        a.account_index = 0
        a.destinations = [MoneroDestination(TestUtils.ADDRESS, 1)]
        b: MoneroOutgoingTransfer = a.copy()
        b.destinations = [MoneroDestination(TestUtils.ADDRESS, 2)]
        with pytest.raises(RuntimeError) as exc_info:
            a.merge(b)
        assert str(exc_info.value) == "Destination vectors are different"
