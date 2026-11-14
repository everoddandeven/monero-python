from __future__ import annotations

import logging

import pytest
from monero import (
    MoneroDestination,
    MoneroIncomingTransfer,
    MoneroOutgoingTransfer,
    MoneroTransfer,
    MoneroTransferQuery,
    MoneroTxQuery,
    MoneroTxWallet,
)

from utils import AssertUtils, BaseTestClass, TestUtils

logger: logging.Logger = logging.getLogger("TestMoneroWalletModelTransferQuery")


@pytest.mark.unit
class TestMoneroWalletModelTransferQuery(BaseTestClass):
    """Wallet transfer query model unit tests."""

    # Test transfer query expected behaviour
    def test_transfer_query(self) -> None:
        transfer_query: MoneroTransferQuery = MoneroTransferQuery()
        tx_query: MoneroTxQuery = MoneroTxQuery()

        # assign tx query to transfer query
        transfer_query.tx_query = tx_query

        assert tx_query.transfer_query is not None
        assert tx_query.transfer_query == transfer_query

        # reassign transfer query to tx query
        transfer_query.tx_query.transfer_query = transfer_query
        assert transfer_query.tx_query is not None
        assert transfer_query == transfer_query.tx_query.transfer_query

        # remove tx query from transfer query
        transfer_query.tx_query = None

        assert tx_query.transfer_query is None

        transfer_query: MoneroTransferQuery = MoneroTransferQuery()
        transfer_query.tx_query = MoneroTxQuery()

        # check incoming/outgoing
        assert transfer_query.incoming is None
        assert transfer_query.outgoing is None
        assert transfer_query.is_incoming() is None
        assert transfer_query.is_outgoing() is None

        # set incoming
        transfer_query.incoming = True
        assert transfer_query.is_incoming() is True
        assert transfer_query.outgoing is False
        assert transfer_query.is_outgoing() is False
        transfer_query.incoming = None

        # set outgoing
        transfer_query.outgoing = True
        assert transfer_query.is_outgoing() is True
        assert transfer_query.incoming is False
        assert transfer_query.is_incoming() is False

    def test_transfer_query_meets_criteria_matches_unconstrained_transfer(self) -> None:
        transfer: MoneroIncomingTransfer = MoneroIncomingTransfer()
        transfer.amount = 100
        assert MoneroTransferQuery().meets_criteria(transfer, False) is True

    @pytest.mark.parametrize("field,value,other_value", [
        ("amount", 100, 999),
        ("account_index", 2, 5),
    ])
    def test_transfer_query_meets_criteria_common_field_filters(self, field: str, value: object, other_value: object) -> None:
        transfer: MoneroIncomingTransfer = MoneroIncomingTransfer()
        transfer.amount = 1
        setattr(transfer, field, value)

        query: MoneroTransferQuery = MoneroTransferQuery()
        setattr(query, field, value)
        assert query.meets_criteria(transfer, False) is True

        setattr(query, field, other_value)
        assert query.meets_criteria(transfer, False) is False

    def test_transfer_query_meets_criteria_incoming_outgoing_flags(self) -> None:
        incoming: MoneroIncomingTransfer = MoneroIncomingTransfer()
        incoming.amount = 1
        outgoing: MoneroOutgoingTransfer = MoneroOutgoingTransfer()
        outgoing.amount = 1

        incoming_query: MoneroTransferQuery = MoneroTransferQuery()
        incoming_query.incoming = True
        assert incoming_query.meets_criteria(incoming, False) is True
        assert incoming_query.meets_criteria(outgoing, False) is False

        outgoing_query: MoneroTransferQuery = MoneroTransferQuery()
        outgoing_query.outgoing = True
        assert outgoing_query.meets_criteria(outgoing, False) is True
        assert outgoing_query.meets_criteria(incoming, False) is False

    def test_transfer_query_meets_criteria_incoming_has_destinations_always_false(self) -> None:
        # has_destinations is an outgoing-only concept; setting it on the query
        # rejects an incoming transfer regardless of True/False
        incoming: MoneroIncomingTransfer = MoneroIncomingTransfer()
        incoming.amount = 1

        query_true: MoneroTransferQuery = MoneroTransferQuery()
        query_true.has_destinations = True
        assert query_true.meets_criteria(incoming, False) is False

        query_false: MoneroTransferQuery = MoneroTransferQuery()
        query_false.has_destinations = False
        assert query_false.meets_criteria(incoming, False) is False

    def test_transfer_query_meets_criteria_incoming_address_fields(self) -> None:
        incoming: MoneroIncomingTransfer = MoneroIncomingTransfer()
        incoming.amount = 1
        incoming.address = TestUtils.ADDRESS
        incoming.subaddress_index = 3

        address_query: MoneroTransferQuery = MoneroTransferQuery()
        address_query.address = TestUtils.ADDRESS
        assert address_query.meets_criteria(incoming, False) is True
        address_query.address = TestUtils.MINING_ADDRESS
        assert address_query.meets_criteria(incoming, False) is False

        addresses_query: MoneroTransferQuery = MoneroTransferQuery()
        addresses_query.addresses = [TestUtils.ADDRESS, TestUtils.MINING_ADDRESS]
        assert addresses_query.meets_criteria(incoming, False) is True
        addresses_query.addresses = [TestUtils.MINING_ADDRESS]
        assert addresses_query.meets_criteria(incoming, False) is False

        subaddress_index_query: MoneroTransferQuery = MoneroTransferQuery()
        subaddress_index_query.subaddress_index = 3
        assert subaddress_index_query.meets_criteria(incoming, False) is True
        subaddress_index_query.subaddress_index = 9
        assert subaddress_index_query.meets_criteria(incoming, False) is False

        subaddress_indices_query: MoneroTransferQuery = MoneroTransferQuery()
        subaddress_indices_query.subaddress_indices = [3, 4]
        assert subaddress_indices_query.meets_criteria(incoming, False) is True
        subaddress_indices_query.subaddress_indices = [9]
        assert subaddress_indices_query.meets_criteria(incoming, False) is False

    def test_transfer_query_meets_criteria_outgoing_address_fields(self) -> None:
        outgoing: MoneroOutgoingTransfer = MoneroOutgoingTransfer()
        outgoing.amount = 1
        outgoing.addresses = [TestUtils.ADDRESS, TestUtils.MINING_ADDRESS]

        # a single address must be a member of the transfer's address list
        address_query: MoneroTransferQuery = MoneroTransferQuery()
        address_query.address = TestUtils.ADDRESS
        assert address_query.meets_criteria(outgoing, False) is True
        address_query.address = "9" + "z" * 94
        assert address_query.meets_criteria(outgoing, False) is False
        assert address_query.meets_criteria(MoneroOutgoingTransfer(), False) is False  # no addresses at all

        # a list of addresses only needs to intersect
        addresses_query: MoneroTransferQuery = MoneroTransferQuery()
        addresses_query.addresses = [TestUtils.MINING_ADDRESS, "9" + "z" * 94]
        assert addresses_query.meets_criteria(outgoing, False) is True
        addresses_query.addresses = ["9" + "z" * 94]
        assert addresses_query.meets_criteria(outgoing, False) is False

    def test_transfer_query_meets_criteria_outgoing_subaddress_fields(self) -> None:
        outgoing: MoneroOutgoingTransfer = MoneroOutgoingTransfer()
        outgoing.amount = 1
        outgoing.subaddress_indices = [3, 4]

        subaddress_index_query: MoneroTransferQuery = MoneroTransferQuery()
        subaddress_index_query.subaddress_index = 3
        assert subaddress_index_query.meets_criteria(outgoing, False) is True
        subaddress_index_query.subaddress_index = 9
        assert subaddress_index_query.meets_criteria(outgoing, False) is False
        assert subaddress_index_query.meets_criteria(MoneroOutgoingTransfer(), False) is False  # no indices at all

        subaddress_indices_query: MoneroTransferQuery = MoneroTransferQuery()
        subaddress_indices_query.subaddress_indices = [4, 100]
        assert subaddress_indices_query.meets_criteria(outgoing, False) is True
        subaddress_indices_query.subaddress_indices = [100, 200]
        assert subaddress_indices_query.meets_criteria(outgoing, False) is False

    def test_transfer_query_meets_criteria_outgoing_has_destinations(self) -> None:
        with_destinations: MoneroOutgoingTransfer = MoneroOutgoingTransfer()
        with_destinations.amount = 1
        with_destinations.destinations = [MoneroDestination(TestUtils.ADDRESS, 1)]
        without_destinations: MoneroOutgoingTransfer = MoneroOutgoingTransfer()
        without_destinations.amount = 1

        query_true: MoneroTransferQuery = MoneroTransferQuery()
        query_true.has_destinations = True
        assert query_true.meets_criteria(with_destinations, False) is True
        assert query_true.meets_criteria(without_destinations, False) is False

        query_false: MoneroTransferQuery = MoneroTransferQuery()
        query_false.has_destinations = False
        assert query_false.meets_criteria(without_destinations, False) is True
        assert query_false.meets_criteria(with_destinations, False) is False

    def test_transfer_query_meets_criteria_invalid_transfer_type_raises(self) -> None:
        transfer: MoneroTransfer = MoneroTransfer()
        transfer.amount = 1
        with pytest.raises(RuntimeError) as exc_info:
            MoneroTransferQuery().meets_criteria(transfer, False)
        assert str(exc_info.value) == "Transfer must be monero_incoming_transfer or monero_outgoing_transfer"

    def test_transfer_query_meets_criteria_query_parent_links_tx_query(self) -> None:
        tx: MoneroTxWallet = MoneroTxWallet()
        tx.hash = "a" * 64
        transfer: MoneroIncomingTransfer = MoneroIncomingTransfer()
        transfer.amount = 100
        transfer.tx = tx

        query: MoneroTransferQuery = MoneroTransferQuery()
        query.amount = 100
        query.tx_query = MoneroTxQuery()
        query.tx_query.hash = "b" * 64  # does not match the transfer's tx

        # query_parent defaults to True: the mismatching tx_query rejects the transfer
        assert query.meets_criteria(transfer) is False
        assert query.meets_criteria(transfer, False) is True  # bypassed when not querying the parent

        query.tx_query.hash = "a" * 64
        assert query.meets_criteria(transfer) is True

    def test_transfer_query_meets_criteria_none_transfer_raises(self) -> None:
        with pytest.raises(RuntimeError) as exc_info:
            MoneroTransferQuery().meets_criteria(None, False) # type: ignore
        assert str(exc_info.value) == "nullptr given to monero_transfer_query::meets_criteria()"

    def test_transfer_query_deserialize(self) -> None:
        query: MoneroTransferQuery = MoneroTransferQuery()
        query.amount = 500000
        query.account_index = 0
        query.incoming = True
        query.address = TestUtils.ADDRESS
        query.subaddress_index = 1
        query.subaddress_indices = [0, 1, 2]
        query.has_destinations = False
        # addresses, destinations and tx_query all raise "not implemented" (see below)
        AssertUtils.assert_serialization_integrity(query)

    @pytest.mark.parametrize("json_fragment", [
        '{"addresses":["' + TestUtils.ADDRESS + '"]}',
        '{"destinations":[{"address":"' + TestUtils.ADDRESS + '","amount":1}]}',
        '{"txQuery":{}}',
    ])
    def test_transfer_query_unimplemented_fields(self, json_fragment: str) -> None:
        with pytest.raises(Exception, match="not implemented"):
            MoneroTransferQuery.deserialize(json_fragment)

    def test_transfer_query_deserialize_from_block(self) -> None:
        tx_query: MoneroTxQuery = MoneroTxQuery()
        tx_query.hash = "a" * 64
        transfer_query: MoneroTransferQuery = MoneroTransferQuery()
        transfer_query.amount = 500000
        transfer_query.account_index = 0
        tx_query.transfer_query = transfer_query

        # deserialize_from_block expects a block node wrapping the tx query under "txs"
        block_json: str = '{"txs":[' + tx_query.serialize() + ']}'
        restored: MoneroTransferQuery = MoneroTransferQuery.deserialize_from_block(block_json)
        assert restored.amount == 500000
        assert restored.account_index == 0
        assert restored.tx_query is not None
        assert restored.tx_query.hash == "a" * 64

    def test_transfer_query_deserialize_from_block_no_nested_query(self) -> None:
        # a tx with no nested transferQuery gets an empty one, linked to the tx query
        tx_query: MoneroTxQuery = MoneroTxQuery()
        tx_query.hash = "a" * 64
        block_json: str = '{"txs":[' + tx_query.serialize() + ']}'
        restored: MoneroTransferQuery = MoneroTransferQuery.deserialize_from_block(block_json)
        assert restored.amount is None
        assert restored.tx_query is not None
        assert restored.tx_query.hash == "a" * 64

    def test_transfer_query_deserialize_from_block_no_txs(self) -> None:
        restored: MoneroTransferQuery = MoneroTransferQuery.deserialize_from_block('{"txs": []}')
        assert restored.amount is None
        assert restored.tx_query is None

    def test_transfer_query_copy(self) -> None:
        query: MoneroTransferQuery = MoneroTransferQuery()
        query.amount = 500000
        query.incoming = True
        query.address = TestUtils.ADDRESS

        copy: MoneroTransferQuery = query.copy()
        assert copy is not query
        assert copy.serialize() == query.serialize()

    def test_transfer_query_copy_deep_copies_destinations(self) -> None:
        query: MoneroTransferQuery = MoneroTransferQuery()
        destination: MoneroDestination = MoneroDestination(TestUtils.ADDRESS, 100)
        query.destinations = [destination]

        copy: MoneroTransferQuery = query.copy()
        assert len(copy.destinations) == 1
        assert copy.destinations[0] is not destination
        assert copy.destinations[0].address == TestUtils.ADDRESS
        assert copy.destinations[0].amount == 100
