from __future__ import annotations

import logging

import pytest
from monero import MoneroKeyImage, MoneroOutputQuery, MoneroOutputWallet, MoneroTxQuery, MoneroTxWallet

from utils import AssertUtils, BaseTestClass

logger: logging.Logger = logging.getLogger("TestMoneroWalletModelOutputQuery")


@pytest.mark.unit
class TestMoneroWalletModelOutputQuery(BaseTestClass):
    """Wallet output query model unit tests."""

    # Test output query expected behaviour
    def test_output_query(self) -> None:
        output_query: MoneroOutputQuery = MoneroOutputQuery()
        tx_query: MoneroTxQuery = MoneroTxQuery()

        # test tx query property assign
        try:
            output_query.tx_query = tx_query # type: ignore
        except AttributeError as e:
            err_msg: str = str(e)
            assert "object has no setter" in err_msg, err_msg

        # assign tx query to output query
        output_query.set_tx_query(tx_query, True)

        assert output_query.tx_query is not None
        assert output_query.tx_query == tx_query
        assert tx_query.input_query is None
        assert tx_query.output_query is not None
        assert tx_query.output_query == output_query

        # reassign output query to tx query
        output_query.tx_query.output_query = output_query
        assert output_query.tx_query is not None
        assert output_query == output_query.tx_query.output_query

        # remove tx query from output query
        output_query.set_tx_query(None, True)

        assert output_query.tx_query is None
        assert tx_query.output_query is None

    # Test input query expected behaviour
    def test_input_query(self) -> None:
        input_query: MoneroOutputQuery = MoneroOutputQuery()
        tx_query: MoneroTxQuery = MoneroTxQuery()

        # assign tx query to input query
        input_query.set_tx_query(tx_query, False)

        assert input_query.tx_query is not None
        assert input_query.tx_query == tx_query
        assert tx_query.output_query is None
        assert tx_query.input_query is not None
        assert tx_query.input_query == input_query

        # reassign input query to tx query
        input_query.tx_query.input_query = input_query
        assert input_query.tx_query is not None
        assert input_query == input_query.tx_query.input_query

        # remove tx query from input query
        input_query.set_tx_query(None, False)

        assert input_query.tx_query is None
        assert tx_query.input_query is None

    def test_output_query_meets_criteria_matches_unconstrained_output(self) -> None:
        output: MoneroOutputWallet = MoneroOutputWallet()
        output.amount = 1
        assert MoneroOutputQuery().meets_criteria(output, False) is True

    @pytest.mark.parametrize("field,value,other_value", [
        ("account_index", 2, 9),
        ("subaddress_index", 5, 1),
        ("amount", 100, 1),
        ("is_spent", True, False),
        ("is_frozen", False, True),
    ])
    def test_output_query_meets_criteria_field_filters(self, field: str, value: object, other_value: object) -> None:
        output: MoneroOutputWallet = MoneroOutputWallet()
        output.amount = 1
        setattr(output, field, value)

        query: MoneroOutputQuery = MoneroOutputQuery()
        setattr(query, field, value)
        assert query.meets_criteria(output, False) is True

        setattr(query, field, other_value)
        assert query.meets_criteria(output, False) is False

    @pytest.mark.parametrize("field,value", [
        ("account_index", 2),
        ("subaddress_index", 5),
        ("amount", 100),
        ("is_spent", True),
        ("is_frozen", False),
    ])
    def test_output_query_meets_criteria_field_filters_require_output_value(self, field: str, value: object) -> None:
        # a query constraint never matches an output that leaves the field unset
        output: MoneroOutputWallet = MoneroOutputWallet()
        query: MoneroOutputQuery = MoneroOutputQuery()
        setattr(query, field, value)
        assert query.meets_criteria(output, False) is False

    def test_output_query_meets_criteria_key_image(self) -> None:
        output: MoneroOutputWallet = MoneroOutputWallet()
        output.amount = 1
        output.key_image = MoneroKeyImage()
        output.key_image.hex = "a" * 64
        output.key_image.signature = "b" * 128

        hex_query: MoneroOutputQuery = MoneroOutputQuery()
        hex_query.key_image = MoneroKeyImage()
        hex_query.key_image.hex = "a" * 64
        assert hex_query.meets_criteria(output, False) is True
        hex_query.key_image.hex = "c" * 64
        assert hex_query.meets_criteria(output, False) is False

        signature_query: MoneroOutputQuery = MoneroOutputQuery()
        signature_query.key_image = MoneroKeyImage()
        signature_query.key_image.signature = "b" * 128
        assert signature_query.meets_criteria(output, False) is True
        signature_query.key_image.signature = "d" * 128
        assert signature_query.meets_criteria(output, False) is False

        # never matches an output with no key image at all
        no_key_image_query: MoneroOutputQuery = MoneroOutputQuery()
        no_key_image_query.key_image = MoneroKeyImage()
        no_key_image_query.key_image.hex = "a" * 64
        assert no_key_image_query.meets_criteria(MoneroOutputWallet(), False) is False

    def test_output_query_meets_criteria_subaddress_indices(self) -> None:
        output: MoneroOutputWallet = MoneroOutputWallet()
        output.amount = 1
        output.subaddress_index = 7

        query: MoneroOutputQuery = MoneroOutputQuery()
        query.subaddress_indices = [7, 8]
        assert query.meets_criteria(output, False) is True

        query.subaddress_indices = [1, 2]
        assert query.meets_criteria(output, False) is False

    def test_output_query_meets_criteria_min_max_amount(self) -> None:
        output: MoneroOutputWallet = MoneroOutputWallet()
        output.amount = 50

        min_query: MoneroOutputQuery = MoneroOutputQuery()
        min_query.min_amount = 10
        assert min_query.meets_criteria(output, False) is True
        min_query.min_amount = 100
        assert min_query.meets_criteria(output, False) is False

        max_query: MoneroOutputQuery = MoneroOutputQuery()
        max_query.max_amount = 100
        assert max_query.meets_criteria(output, False) is True
        max_query.max_amount = 10
        assert max_query.meets_criteria(output, False) is False

    def test_output_query_meets_criteria_query_parent_links_tx_query(self) -> None:
        tx: MoneroTxWallet = MoneroTxWallet()
        tx.hash = "a" * 64
        output: MoneroOutputWallet = MoneroOutputWallet()
        output.amount = 1
        output.tx = tx

        query: MoneroOutputQuery = MoneroOutputQuery()
        query.amount = 1
        tx_query: MoneroTxQuery = MoneroTxQuery()
        tx_query.hash = "b" * 64
        query.set_tx_query(tx_query, True)

        # query_parent defaults to True: the mismatching tx_query rejects the output
        assert query.meets_criteria(output) is False
        assert query.meets_criteria(output, False) is True  # bypassed when not querying the parent

        tx_query.hash = "a" * 64
        assert query.meets_criteria(output) is True

    def test_output_query_meets_criteria_none_output_raises(self) -> None:
        with pytest.raises(RuntimeError) as exc_info:
            MoneroOutputQuery().meets_criteria(None, False) # type: ignore
        assert str(exc_info.value) == "nullptr given to monero_output_query::meets_criteria()"

    def test_output_query_deserialize(self) -> None:
        query: MoneroOutputQuery = MoneroOutputQuery()
        query.amount = 1000000
        query.index = 2
        query.account_index = 0
        query.subaddress_index = 1
        query.is_spent = False
        query.is_frozen = False
        query.subaddress_indices = [0, 1]
        query.min_amount = 100000
        query.max_amount = 2000000
        AssertUtils.assert_serialization_integrity(query)

    def test_output_query_deserialize_from_block(self) -> None:
        tx_query: MoneroTxQuery = MoneroTxQuery()
        tx_query.hash = "a" * 64
        tx_query.input_query = MoneroOutputQuery()
        tx_query.input_query.amount = 5
        tx_query.input_query.index = 1
        tx_query.output_query = MoneroOutputQuery()
        tx_query.output_query.amount = 7
        tx_query.output_query.index = 2

        # deserialize_from_block expects a block node wrapping the tx query under "txs"
        block_json: str = '{"txs":[' + tx_query.serialize() + ']}'
        restored: MoneroOutputQuery = MoneroOutputQuery.deserialize_from_block(block_json)
        assert restored.amount == 7
        assert restored.index == 2
        assert restored.tx_query is not None
        assert restored.tx_query.hash == "a" * 64
        # the input query is built alongside the output query and linked back too
        assert restored.tx_query.input_query is not None
        assert restored.tx_query.input_query.amount == 5

    def test_output_query_deserialize_from_block_no_txs(self) -> None:
        restored: MoneroOutputQuery = MoneroOutputQuery.deserialize_from_block('{"txs": []}')
        assert restored.amount is None
        assert restored.tx_query is None

    def test_output_query_copy(self) -> None:
        query: MoneroOutputQuery = MoneroOutputQuery()
        query.amount = 1000000
        query.min_amount = 100000
        query.max_amount = 2000000

        copy: MoneroOutputQuery = query.copy()
        assert copy is not query
        assert copy.serialize() == query.serialize()
