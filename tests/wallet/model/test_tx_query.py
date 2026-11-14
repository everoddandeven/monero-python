from __future__ import annotations

import logging

import pytest
from monero import (
    MoneroBlock,
    MoneroIncomingTransfer,
    MoneroOutgoingTransfer,
    MoneroOutputQuery,
    MoneroOutputWallet,
    MoneroTransferQuery,
    MoneroTxQuery,
    MoneroTxWallet,
)

from utils import AssertUtils, BaseTestClass

logger: logging.Logger = logging.getLogger("TestMoneroWalletModelTxQuery")


@pytest.mark.unit
class TestMoneroWalletModelTxQuery(BaseTestClass):
    """Wallet tx query model unit tests."""

    # Test tx query expected behaviour
    def test_tx_query(self) -> None:
        tx_query: MoneroTxQuery = MoneroTxQuery()
        transfer_query: MoneroTransferQuery = MoneroTransferQuery()
        output_query: MoneroOutputQuery = MoneroOutputQuery()
        input_query: MoneroOutputQuery = MoneroOutputQuery()

        # assign transfer query to tx query
        tx_query.transfer_query = transfer_query

        assert tx_query.transfer_query == transfer_query
        assert transfer_query.tx_query is not None
        assert transfer_query.tx_query == tx_query

        # remove transfer query from tx query
        tx_query.transfer_query = None

        assert tx_query.transfer_query != transfer_query
        assert transfer_query.tx_query is None

        # assign output query to tx query
        tx_query.output_query = output_query

        assert tx_query.output_query == output_query
        assert output_query.tx_query is not None
        assert output_query.tx_query == tx_query

        # remove output query from tx query
        tx_query.output_query = None

        assert tx_query.output_query != output_query
        assert output_query.tx_query is None

        # assign input query to tx query
        tx_query.input_query = input_query

        assert tx_query.input_query == input_query
        assert input_query.tx_query is not None
        assert input_query.tx_query == tx_query

        # remove output query from tx query
        tx_query.input_query = None

        assert tx_query.input_query != input_query
        assert input_query.tx_query is None

    def test_tx_query_meets_criteria_matches_unconstrained_tx(self) -> None:
        tx: MoneroTxWallet = MoneroTxWallet()
        tx.hash = "a" * 64
        assert MoneroTxQuery().meets_criteria(tx) is True

    @pytest.mark.parametrize("field,value,other_value", [
        ("hash", "a" * 64, "b" * 64),
        ("payment_id", "c" * 16, "d" * 16),
        ("is_confirmed", True, False),
        ("in_tx_pool", True, False),
        ("relay", True, False),
        ("is_failed", True, False),
        ("is_miner_tx", True, False),
        ("is_locked", True, False),
        ("is_incoming", True, False),
        ("is_outgoing", True, False),
    ])
    def test_tx_query_meets_criteria_field_filters(self, field: str, value: object, other_value: object) -> None:
        tx: MoneroTxWallet = MoneroTxWallet()
        tx.hash = "a" * 64
        setattr(tx, field, value)

        query: MoneroTxQuery = MoneroTxQuery()
        setattr(query, field, value)
        assert query.meets_criteria(tx) is True

        setattr(query, field, other_value)
        assert query.meets_criteria(tx) is False

    def test_tx_query_meets_criteria_has_payment_id(self) -> None:
        with_payment_id: MoneroTxWallet = MoneroTxWallet()
        with_payment_id.hash = "a" * 64
        with_payment_id.payment_id = "b" * 16
        without_payment_id: MoneroTxWallet = MoneroTxWallet()
        without_payment_id.hash = "c" * 64

        query_true: MoneroTxQuery = MoneroTxQuery()
        query_true.has_payment_id = True
        assert query_true.meets_criteria(with_payment_id) is True
        assert query_true.meets_criteria(without_payment_id) is False

        query_false: MoneroTxQuery = MoneroTxQuery()
        query_false.has_payment_id = False
        assert query_false.meets_criteria(without_payment_id) is True
        assert query_false.meets_criteria(with_payment_id) is False

    def test_tx_query_meets_criteria_hashes(self) -> None:
        tx: MoneroTxWallet = MoneroTxWallet()
        tx.hash = "a" * 64

        query: MoneroTxQuery = MoneroTxQuery()
        query.hashes = ["a" * 64, "b" * 64]
        assert query.meets_criteria(tx) is True

        query.hashes = ["c" * 64]
        assert query.meets_criteria(tx) is False

    def test_tx_query_meets_criteria_payment_ids(self) -> None:
        with_payment_id: MoneroTxWallet = MoneroTxWallet()
        with_payment_id.hash = "a" * 64
        with_payment_id.payment_id = "b" * 16
        without_payment_id: MoneroTxWallet = MoneroTxWallet()
        without_payment_id.hash = "c" * 64

        query: MoneroTxQuery = MoneroTxQuery()
        query.payment_ids = ["b" * 16, "d" * 16]
        assert query.meets_criteria(with_payment_id) is True
        assert query.meets_criteria(without_payment_id) is False  # tx has no payment id at all

        query.payment_ids = ["d" * 16]
        assert query.meets_criteria(with_payment_id) is False  # tx's payment id isn't in the list

    def test_tx_query_meets_criteria_height_filters(self) -> None:
        def confirmed_tx(height: int) -> MoneroTxWallet:
            tx: MoneroTxWallet = MoneroTxWallet()
            tx.hash = "a" * 64
            block: MoneroBlock = MoneroBlock()
            block.height = height
            tx.block = block
            return tx

        tx: MoneroTxWallet = confirmed_tx(100)

        height_query: MoneroTxQuery = MoneroTxQuery()
        height_query.height = 100
        assert height_query.meets_criteria(tx) is True
        height_query.height = 200
        assert height_query.meets_criteria(tx) is False

        min_query: MoneroTxQuery = MoneroTxQuery()
        min_query.min_height = 50
        assert min_query.meets_criteria(tx) is True
        min_query.min_height = 150
        assert min_query.meets_criteria(tx) is False

        max_query: MoneroTxQuery = MoneroTxQuery()
        max_query.max_height = 150
        assert max_query.meets_criteria(tx) is True
        max_query.max_height = 50
        assert max_query.meets_criteria(tx) is False

        # an unconfirmed tx (no height) never satisfies a height-bound query
        unconfirmed: MoneroTxWallet = MoneroTxWallet()
        unconfirmed.hash = "b" * 64
        assert min_query.meets_criteria(unconfirmed) is False

    def test_tx_query_meets_criteria_query_children_default_and_false(self) -> None:
        tx: MoneroTxWallet = MoneroTxWallet()
        tx.hash = "a" * 64  # no inputs -> fails an enforced input_query

        query: MoneroTxQuery = MoneroTxQuery()
        query.input_query = MoneroOutputQuery()

        # query_children defaults to True, matching monero-cpp's default
        assert query.meets_criteria(tx) is False
        assert query.meets_criteria(tx, True) is False
        assert query.meets_criteria(tx, False) is True

    def test_tx_query_meets_criteria_transfer_query(self) -> None:
        def tx_with_outgoing(amount: int) -> MoneroTxWallet:
            tx: MoneroTxWallet = MoneroTxWallet()
            tx.hash = "a" * 64
            tx.outgoing_transfer = MoneroOutgoingTransfer()
            tx.outgoing_transfer.amount = amount
            tx.outgoing_transfer.tx = tx
            return tx

        def tx_with_incoming(amount: int) -> MoneroTxWallet:
            tx: MoneroTxWallet = MoneroTxWallet()
            tx.hash = "a" * 64
            transfer: MoneroIncomingTransfer = MoneroIncomingTransfer()
            transfer.amount = amount
            transfer.tx = tx
            tx.incoming_transfers = [transfer]
            return tx

        query: MoneroTxQuery = MoneroTxQuery()
        query.transfer_query = MoneroTransferQuery()
        query.transfer_query.amount = 500

        assert query.meets_criteria(tx_with_outgoing(500), True) is True  # matches via outgoing
        assert query.meets_criteria(tx_with_incoming(500), True) is True  # matches via incoming
        assert query.meets_criteria(tx_with_outgoing(1), True) is False  # no transfer matches

        # outgoing fails the query but an incoming transfer still matches as a fallback
        tx: MoneroTxWallet = tx_with_outgoing(1)
        incoming: MoneroIncomingTransfer = MoneroIncomingTransfer()
        incoming.amount = 500
        incoming.tx = tx
        tx.incoming_transfers = [incoming]
        assert query.meets_criteria(tx, True) is True

    def test_tx_query_meets_criteria_input_query(self) -> None:
        tx_no_inputs: MoneroTxWallet = MoneroTxWallet()
        tx_no_inputs.hash = "a" * 64

        tx_with_input: MoneroTxWallet = MoneroTxWallet()
        tx_with_input.hash = "b" * 64
        tx_input: MoneroOutputWallet = MoneroOutputWallet()
        tx_input.amount = 100
        tx_with_input.inputs = [tx_input]

        query: MoneroTxQuery = MoneroTxQuery()
        query.input_query = MoneroOutputQuery()
        assert query.meets_criteria(tx_no_inputs, True) is False  # no inputs at all

        query.input_query.amount = 999
        assert query.meets_criteria(tx_with_input, True) is False  # no input matches

        query.input_query.amount = 100
        assert query.meets_criteria(tx_with_input, True) is True  # one input matches

    def test_tx_query_meets_criteria_output_query(self) -> None:
        tx_no_outputs: MoneroTxWallet = MoneroTxWallet()
        tx_no_outputs.hash = "a" * 64

        tx_with_output: MoneroTxWallet = MoneroTxWallet()
        tx_with_output.hash = "b" * 64
        output: MoneroOutputWallet = MoneroOutputWallet()
        output.amount = 100
        tx_with_output.outputs = [output]

        query: MoneroTxQuery = MoneroTxQuery()
        query.output_query = MoneroOutputQuery()
        assert query.meets_criteria(tx_no_outputs, True) is False  # no outputs at all

        query.output_query.amount = 999
        assert query.meets_criteria(tx_with_output, True) is False  # no output matches

        query.output_query.amount = 100
        assert query.meets_criteria(tx_with_output, True) is True  # one output matches

    def test_tx_query_meets_criteria_none_tx_raises(self) -> None:
        with pytest.raises(RuntimeError) as exc_info:
            MoneroTxQuery().meets_criteria(None) # type: ignore
        assert str(exc_info.value) == "nullptr given to monero_tx_query::meets_criteria()"

    def test_tx_query_deserialize(self) -> None:
        tx_query: MoneroTxQuery = MoneroTxQuery()
        tx_query.hash = "a" * 64
        tx_query.is_confirmed = True
        tx_query.hashes = ["a" * 64, "b" * 64]
        tx_query.has_payment_id = False
        tx_query.payment_ids = ["c" * 16]
        tx_query.height = 3000000
        tx_query.min_height = 2999990
        tx_query.max_height = 3000010
        tx_query.include_outputs = False
        # is_outgoing/is_incoming are deliberately not set here: monero_tx_query
        # redeclares them as its own fields shadowing monero_tx_wallet's, and
        # deserializing populates both copies at once (see test below)
        AssertUtils.assert_serialization_integrity(tx_query)

    def test_tx_query_is_incoming_deserialize_not_duplicated(self) -> None:
        tx_query: MoneroTxQuery = MoneroTxQuery()
        tx_query.is_incoming = True
        tx_query.is_outgoing = False
        json_str: str = tx_query.serialize()
        logger.debug(f"Serialized tx query: {json_str}")
        assert json_str.count("isIncoming") == 1
        assert json_str.count("isOutgoing") == 1

        restored: MoneroTxQuery = MoneroTxQuery.deserialize(json_str)
        assert restored.is_incoming == tx_query.is_incoming
        assert restored.is_outgoing == tx_query.is_outgoing

        restored_json: str = restored.serialize()
        incoming_count: int = restored_json.count("isIncoming")
        outgoing_count: int = restored_json.count("isOutgoing")
        logger.debug(f"Deserialized tx query re-serialized: {restored_json}")
        logger.debug(f"'isIncoming' occurs {incoming_count} time(s), 'isOutgoing' occurs {outgoing_count} time(s) (expected 1 each -- >1 means duplicated, i.e. malformed)")
        assert incoming_count == 1
        assert outgoing_count == 1

    def test_tx_query_nested_transfer_query_deserialize(self) -> None:
        # transfer_query is a nested sub-object that to_rapidjson_val() and
        # from_property_tree() both handle recursively
        tx_query: MoneroTxQuery = MoneroTxQuery()
        tx_query.height = 3000000
        transfer_query: MoneroTransferQuery = MoneroTransferQuery()
        transfer_query.incoming = True
        transfer_query.amount = 500000
        transfer_query.account_index = 0
        tx_query.transfer_query = transfer_query

        json_str: str = tx_query.serialize()
        logger.debug(f"Serialized nested tx query: {json_str}")
        assert "transferQuery" in json_str

        restored: MoneroTxQuery = MoneroTxQuery.deserialize(json_str)
        assert restored.height == tx_query.height
        assert restored.transfer_query is not None
        assert restored.transfer_query.incoming == transfer_query.incoming
        assert restored.transfer_query.amount == transfer_query.amount
        assert restored.transfer_query.account_index == transfer_query.account_index

    def test_tx_query_input_and_output_query_deserialize(self) -> None:
        # TODO input_query/output_query are read by from_property_tree() but never written by to_rapidjson_val()
        tx_query: MoneroTxQuery = MoneroTxQuery.deserialize(
            '{"inputQuery":{"amount":5,"index":1},"outputQuery":{"amount":7,"index":2}}'
        )
        assert tx_query.input_query is not None
        assert tx_query.input_query.amount == 5
        assert tx_query.input_query.index == 1
        assert tx_query.output_query is not None
        assert tx_query.output_query.amount == 7
        assert tx_query.output_query.index == 2

    def test_tx_query_input_and_output_query_serialize_round_trip(self) -> None:
        tx_query: MoneroTxQuery = MoneroTxQuery()
        tx_query.input_query = MoneroOutputQuery()
        tx_query.input_query.amount = 5
        tx_query.input_query.index = 1
        tx_query.output_query = MoneroOutputQuery()
        tx_query.output_query.amount = 7
        tx_query.output_query.index = 2

        json_str: str = tx_query.serialize()
        logger.debug(f"Serialized tx query with input/output query: {json_str}")
        assert "inputQuery" in json_str
        assert "outputQuery" in json_str

        restored: MoneroTxQuery = MoneroTxQuery.deserialize(json_str)
        assert restored.input_query is not None
        assert restored.input_query.amount == 5
        assert restored.input_query.index == 1
        assert restored.output_query is not None
        assert restored.output_query.amount == 7
        assert restored.output_query.index == 2

    def test_tx_query_deserialize_from_block(self) -> None:
        tx_query: MoneroTxQuery = MoneroTxQuery()
        tx_query.hash = "a" * 64
        tx_query.is_confirmed = True
        tx_query.hashes = ["a" * 64, "b" * 64]
        tx_query.min_height = 100
        tx_query.max_height = 200

        # deserialize_from_block expects a block node wrapping the query under "txs"
        block_json: str = '{"txs":[' + tx_query.serialize() + ']}'
        restored: MoneroTxQuery = MoneroTxQuery.deserialize_from_block(block_json)
        assert restored.hash == "a" * 64
        assert restored.is_confirmed is True
        assert list(restored.hashes) == ["a" * 64, "b" * 64]
        assert restored.min_height == 100
        assert restored.max_height == 200

        # the query is linked back to its parent block
        assert restored.block is not None
        assert restored.block.txs[0] is restored

    def test_tx_query_deserialize_from_block_no_txs(self) -> None:
        restored: MoneroTxQuery = MoneroTxQuery.deserialize_from_block('{"txs": []}')
        assert restored.hash is None
        assert restored.block is None

    def test_tx_query_copy(self) -> None:
        query: MoneroTxQuery = MoneroTxQuery()
        query.hash = "a" * 64
        query.height = 3000000
        query.is_confirmed = True

        copy: MoneroTxQuery = query.copy()
        assert copy is not query
        assert copy.serialize() == query.serialize()

    def test_tx_query_decontextualize(self) -> None:
        query: MoneroTxQuery = MoneroTxQuery()
        query.hash = "a" * 64
        query.is_incoming = True
        query.is_outgoing = False
        query.transfer_query = MoneroTransferQuery()
        query.input_query = MoneroOutputQuery()
        query.output_query = MoneroOutputQuery()

        # mutates and returns the same query, for convenience
        decontextualized: MoneroTxQuery = MoneroTxQuery.decontextualize(query)
        assert decontextualized is query
        assert query.is_incoming is None
        assert query.is_outgoing is None
        assert query.transfer_query is None
        assert query.input_query is None
        assert query.output_query is None

        # criteria that don't require looking up other transfers/outputs are untouched
        assert query.hash == "a" * 64
