from __future__ import annotations

import logging
import subprocess
import sys

import pytest
from monero import (
    MoneroIncomingTransfer,
    MoneroKeyImage,
    MoneroOutgoingTransfer,
    MoneroOutputQuery,
    MoneroOutputWallet,
    MoneroTransfer,
    MoneroTransferQuery,
    MoneroTxSet,
    MoneroTxWallet,
)

from utils import AssertUtils, BaseTestClass, TestUtils

logger: logging.Logger = logging.getLogger("TestMoneroWalletModelTxs")


@pytest.mark.unit
class TestMoneroWalletModelTxs(BaseTestClass):
    """Wallet tx model unit tests."""

    def test_tx_wallet_deserialize(self) -> None:
        tx_wallet: MoneroTxWallet = MoneroTxWallet()
        tx_wallet.hash = "a" * 64
        tx_wallet.is_miner_tx = False
        tx_wallet.fee = 7500000
        tx_wallet.relay = True
        tx_wallet.is_relayed = True
        tx_wallet.is_confirmed = True
        tx_wallet.in_tx_pool = False
        tx_wallet.num_confirmations = 10
        tx_wallet.unlock_time = 0
        tx_wallet.is_incoming = True
        tx_wallet.is_outgoing = False
        tx_wallet.note = "thanks"
        tx_wallet.is_locked = False
        tx_wallet.input_sum = 2000000
        tx_wallet.output_sum = 1900000
        # tx_set, incoming_transfers, outgoing_transfer, change_address,
        # change_amount, num_dummy_outputs and extra_hex all raise "not
        # implemented" (see below), same as their monero_tx base counterparts
        # (version, inputs, outputs, ...) tested in test_monero_daemon_model.py
        AssertUtils.assert_serialization_integrity(tx_wallet)

    @pytest.mark.parametrize("json_fragment", [
        '{"txSet":{}}',
        '{"incomingTransfers":[]}',
        '{"outgoingTransfer":{}}',
        '{"changeAddress":"' + TestUtils.ADDRESS + '"}',
        '{"changeAmount":1}',
        '{"numDummyOutputs":1}',
        '{"extraHex":"deadbeef"}',
    ])
    def test_tx_wallet_unimplemented_fields(self, json_fragment: str) -> None:
        with pytest.raises(Exception, match="not implemented"):
            MoneroTxWallet.deserialize(json_fragment)

    def test_tx_set_deserialize(self) -> None:
        tx_set: MoneroTxSet = MoneroTxSet()
        tx_set.unsigned_tx_hex = "deadbeef"
        tx_set.multisig_tx_hex = "beefdead"
        AssertUtils.assert_serialization_integrity(tx_set)

    def test_tx_set_signed_tx_hex_deserialize(self) -> None:
        tx_set: MoneroTxSet = MoneroTxSet()
        tx_set.signed_tx_hex = "deadbeef"
        AssertUtils.assert_serialization_integrity(tx_set)

    def test_tx_set_txs_deserialize(self) -> None:
        json_str: str = '{"txs": [{"hash": "' + "a" * 64 + '"}, {"hash": "' + "b" * 64 + '"}]}'
        tx_set: MoneroTxSet = MoneroTxSet.deserialize(json_str)
        assert len(tx_set.txs) == 2
        assert all(isinstance(tx, MoneroTxWallet) for tx in tx_set.txs)
        assert tx_set.txs[0].hash == "a" * 64
        assert tx_set.txs[1].hash == "b" * 64

    def test_tx_wallet_merge_incoming_transfers_with_unset_indices_are_kept_distinct(self) -> None:
        """
        merge_incoming_transfer() dedups incoming transfers by (account_index, subaddress_index)
        when reconciling two txs' transfer lists. Previously it dereferenced both indices
        unconditionally (boost::optional UB when unset), reachable via TxWallet.merge() with
        user-constructed MoneroIncomingTransfer objects that never had an index assigned. Since
        identity can't be verified without both indices, unset-index transfers must be kept as
        distinct entries rather than crashing or being silently coalesced. Run in an isolated
        subprocess: locally this UB just gives a wrong (deduped) result, but the same
        optional::get() assertion has been observed to abort the whole process in CI's build
        (NDEBUG/ODR ambiguity between monero-cpp and monero-python's own compiled units), which a
        plain in-process assertion can't survive.
        """
        script: str = (
            "import monero, sys\n"
            "tx_a = monero.MoneroTxWallet()\n"
            "tx_a.hash = 'a' * 64\n"
            "tx_a.is_confirmed = True\n"
            "transfer_a = monero.MoneroIncomingTransfer()\n"  # account_index/subaddress_index intentionally unset
            "transfer_a.tx = tx_a\n"
            "tx_a.incoming_transfers = [transfer_a]\n"
            "tx_b = monero.MoneroTxWallet()\n"
            "tx_b.hash = 'a' * 64\n"
            "tx_b.is_confirmed = True\n"
            "transfer_b = monero.MoneroIncomingTransfer()\n"  # account_index/subaddress_index intentionally unset
            "transfer_b.tx = tx_b\n"
            "tx_b.incoming_transfers = [transfer_b]\n"
            "tx_a.merge(tx_b)\n"
            "n = len(tx_a.incoming_transfers) if tx_a.incoming_transfers else 0\n"
            "sys.exit(0 if n == 2 else f'incoming_transfers not kept distinct: len={n}')\n"
        )
        result: subprocess.CompletedProcess[str] = subprocess.run([sys.executable, "-c", script], capture_output=True, text=True, timeout=30)
        logger.debug(f"subprocess exit code: {result.returncode}, stderr: {result.stderr.strip()}")
        assert result.returncode == 0, (
            f"TxWallet.merge() did not keep unset-index incoming transfers distinct "
            f"(exit code {result.returncode}): {result.stderr.strip()[-300:]}"
        )

    def test_tx_wallet_copy(self) -> None:
        tx: MoneroTxWallet = MoneroTxWallet()
        tx.hash = "a" * 64
        tx.is_confirmed = True
        tx.note = "hello"

        copy: MoneroTxWallet = tx.copy()
        assert copy is not tx
        assert copy.serialize() == tx.serialize()

    def test_tx_wallet_copy_re_copies_inputs_as_output_wallet(self) -> None:
        tx: MoneroTxWallet = MoneroTxWallet()
        tx.hash = "a" * 64

        key_image: MoneroKeyImage = MoneroKeyImage()
        key_image.hex = "1" * 64
        tx_input: MoneroOutputWallet = MoneroOutputWallet()
        tx_input.tx = tx
        tx_input.key_image = key_image
        tx_input.amount = 1234
        tx_input.account_index = 2
        tx_input.subaddress_index = 3
        tx_input.is_spent = True
        tx_input.is_frozen = False
        tx.inputs = [tx_input]

        copy: MoneroTxWallet = tx.copy()
        assert isinstance(copy.inputs[0], MoneroOutputWallet)
        assert copy.inputs[0] is not tx_input
        assert copy.inputs[0].amount == 1234
        assert copy.inputs[0].account_index == 2
        assert copy.inputs[0].subaddress_index == 3
        assert copy.inputs[0].is_spent is True
        assert copy.inputs[0].is_frozen is False
        assert copy.inputs[0].key_image.hex == "1" * 64 # type: ignore
        assert copy.inputs[0].tx is copy

    def test_tx_wallet_merge(self) -> None:
        a: MoneroTxWallet = MoneroTxWallet()
        a.hash = "a" * 64
        a.is_confirmed = True  # required: base monero_tx::merge() dereferences is_confirmed directly

        b: MoneroTxWallet = a.copy()
        b.note = "hello"  # a.note is unset -> merge fills the gap
        a.merge(b)
        assert a.note == "hello"

    def test_tx_wallet_merge_is_locked_can_become_false(self) -> None:
        a: MoneroTxWallet = MoneroTxWallet()
        a.hash = "a" * 64
        a.is_confirmed = True
        a.is_locked = False  # self: already unlocked
        b: MoneroTxWallet = a.copy()
        b.is_locked = True   # other: still locked
        a.merge(b)
        assert a.is_locked is False

    def test_tx_wallet_inputs_deserialize_as_output_wallet(self) -> None:
        tx: MoneroTxWallet = MoneroTxWallet()
        tx.hash = "a" * 64
        tx_input: MoneroOutputWallet = MoneroOutputWallet()
        tx_input.amount = 500000
        tx_input.index = 7
        tx_input.account_index = 1
        tx_input.subaddress_index = 2
        tx_input.is_spent = True
        tx_input.is_frozen = False
        tx_input.key_image = MoneroKeyImage()
        tx_input.key_image.hex = "k" * 64
        tx.inputs = [tx_input]

        json_str: str = tx.serialize()
        assert "accountIndex" in json_str
        assert "isSpent" in json_str

        # monero_tx::from_property_tree parses inputs as MoneroOutput; the wallet
        # deserializer re-parses them as MoneroOutputWallet in place
        restored: MoneroTxWallet = MoneroTxWallet.deserialize(json_str)
        assert len(restored.inputs) == 1
        assert isinstance(restored.inputs[0], MoneroOutputWallet)
        assert restored.inputs[0].account_index == 1
        assert restored.inputs[0].subaddress_index == 2
        assert restored.inputs[0].is_spent is True
        assert restored.inputs[0].is_frozen is False
        assert restored.inputs[0].key_image is not None
        assert restored.inputs[0].key_image.hex == "k" * 64
        assert restored.inputs[0].tx is restored

    def test_tx_wallet_outputs_deserialize_as_output_wallet(self) -> None:
        tx: MoneroTxWallet = MoneroTxWallet()
        tx.hash = "a" * 64
        output: MoneroOutputWallet = MoneroOutputWallet()
        output.amount = 500000
        output.index = 3
        output.account_index = 2
        output.subaddress_index = 1
        output.is_spent = True
        output.is_frozen = False
        tx.outputs = [output]

        json_str: str = tx.serialize()
        assert "accountIndex" in json_str
        assert "isSpent" in json_str

        restored: MoneroTxWallet = MoneroTxWallet.deserialize(json_str)
        assert len(restored.outputs) == 1
        assert isinstance(restored.outputs[0], MoneroOutputWallet)
        assert restored.outputs[0].account_index == 2
        assert restored.outputs[0].subaddress_index == 1
        assert restored.outputs[0].is_spent is True
        assert restored.outputs[0].is_frozen is False

    def test_tx_wallet_get_outputs_wallet_after_deserialize(self) -> None:
        tx: MoneroTxWallet = MoneroTxWallet()
        tx.hash = "a" * 64
        output: MoneroOutputWallet = MoneroOutputWallet()
        output.amount = 500000
        output.index = 3
        tx.outputs = [output]

        restored: MoneroTxWallet = MoneroTxWallet.deserialize(tx.serialize())
        # once deserialize works: raises "nullptr given to monero_output_query::meets_criteria()"
        outputs_wallet: list[MoneroOutputWallet] = restored.get_outputs_wallet()
        assert len(outputs_wallet) == 1
        assert outputs_wallet[0].amount == 500000

    def test_tx_wallet_filter_inputs_wallet(self) -> None:
        def make_input(account_index: int, amount: int) -> MoneroOutputWallet:
            tx_input: MoneroOutputWallet = MoneroOutputWallet()
            tx_input.account_index = account_index
            tx_input.amount = amount
            return tx_input

        tx: MoneroTxWallet = MoneroTxWallet()
        tx.hash = "a" * 64
        tx.inputs = [make_input(0, 100), make_input(1, 200), make_input(0, 300)]

        query: MoneroOutputQuery = MoneroOutputQuery()
        query.account_index = 0

        # filter returns the matches and drops the rest from tx.inputs in place
        matched: list[MoneroOutputWallet] = tx.filter_inputs_wallet(query)
        assert [i.amount for i in matched] == [100, 300]
        assert all(isinstance(i, MoneroOutputWallet) for i in matched)
        assert [i.amount for i in tx.inputs] == [100, 300]

        # an unconstrained query keeps everything
        assert len(tx.filter_inputs_wallet(MoneroOutputQuery())) == 2

    def test_tx_wallet_get_inputs_wallet(self) -> None:
        def make_input(account_index: int, amount: int) -> MoneroOutputWallet:
            tx_input: MoneroOutputWallet = MoneroOutputWallet()
            tx_input.account_index = account_index
            tx_input.amount = amount
            return tx_input

        tx: MoneroTxWallet = MoneroTxWallet()
        tx.hash = "a" * 64
        tx.inputs = [make_input(0, 100), make_input(1, 200), make_input(0, 300)]

        query: MoneroOutputQuery = MoneroOutputQuery()
        query.account_index = 0

        # get_inputs_wallet() does not mutate tx.inputs
        matched: list[MoneroOutputWallet] = tx.get_inputs_wallet(query)
        assert [i.amount for i in matched] == [100, 300]
        assert len(tx.inputs) == 3

        # unconstrained default query (no args) returns all inputs
        assert len(tx.get_inputs_wallet()) == 3

    def test_tx_wallet_filter_outputs_wallet(self) -> None:
        def make_output(account_index: int, amount: int) -> MoneroOutputWallet:
            output: MoneroOutputWallet = MoneroOutputWallet()
            output.account_index = account_index
            output.amount = amount
            return output

        tx: MoneroTxWallet = MoneroTxWallet()
        tx.hash = "a" * 64
        tx.outputs = [make_output(0, 100), make_output(1, 200), make_output(0, 300)]

        query: MoneroOutputQuery = MoneroOutputQuery()
        query.account_index = 0

        # filter returns the matches and drops the rest from tx.outputs in place
        matched: list[MoneroOutputWallet] = tx.filter_outputs_wallet(query)
        assert [o.amount for o in matched] == [100, 300]
        assert all(isinstance(o, MoneroOutputWallet) for o in matched)
        assert [o.amount for o in tx.outputs] == [100, 300]

        # an unconstrained query keeps everything
        assert len(tx.filter_outputs_wallet(MoneroOutputQuery())) == 2

    def test_tx_wallet_filter_transfers(self) -> None:
        tx: MoneroTxWallet = MoneroTxWallet()
        tx.hash = "a" * 64

        outgoing: MoneroOutgoingTransfer = MoneroOutgoingTransfer()
        outgoing.amount = 1000

        incoming_1: MoneroIncomingTransfer = MoneroIncomingTransfer()
        incoming_1.account_index = 0
        incoming_1.amount = 100

        incoming_2: MoneroIncomingTransfer = MoneroIncomingTransfer()
        incoming_2.account_index = 1
        incoming_2.amount = 200

        tx.outgoing_transfer = outgoing
        tx.incoming_transfers = [incoming_1, incoming_2]

        query: MoneroTransferQuery = MoneroTransferQuery()
        query.incoming = True
        query.account_index = 0

        # filter returns the matches and drops the rest (outgoing_transfer cleared, incoming_2 removed)
        matched: list[MoneroTransfer] = tx.filter_transfers(query)
        assert [t.amount for t in matched] == [100]
        assert tx.outgoing_transfer is None
        assert [t.amount for t in tx.incoming_transfers] == [100]

    def test_tx_wallet_get_transfers(self) -> None:
        tx: MoneroTxWallet = MoneroTxWallet()
        tx.hash = "a" * 64
        tx.outgoing_transfer = MoneroOutgoingTransfer()
        tx.outgoing_transfer.amount = 1000
        tx.incoming_transfers = [MoneroIncomingTransfer(), MoneroIncomingTransfer()]
        tx.incoming_transfers[0].amount = 100
        tx.incoming_transfers[1].amount = 200

        # no-arg overload delegates to an empty query -> outgoing then incoming, in order
        all_transfers: list[MoneroTransfer] = tx.get_transfers()
        assert [t.amount for t in all_transfers] == [1000, 100, 200]
        assert isinstance(all_transfers[0], MoneroOutgoingTransfer)
        assert all(isinstance(t, MoneroIncomingTransfer) for t in all_transfers[1:])

        # get_transfers() does not mutate the tx
        assert tx.outgoing_transfer is not None
        assert len(tx.incoming_transfers) == 2

    def test_tx_wallet_get_transfers_with_query(self) -> None:
        tx: MoneroTxWallet = MoneroTxWallet()
        tx.hash = "a" * 64
        tx.outgoing_transfer = MoneroOutgoingTransfer()
        tx.outgoing_transfer.amount = 1000
        tx.incoming_transfers = [MoneroIncomingTransfer(), MoneroIncomingTransfer()]
        tx.incoming_transfers[0].amount = 100
        tx.incoming_transfers[1].amount = 200

        incoming_query: MoneroTransferQuery = MoneroTransferQuery()
        incoming_query.incoming = True
        assert [t.amount for t in tx.get_transfers(incoming_query)] == [100, 200]

        outgoing_query: MoneroTransferQuery = MoneroTransferQuery()
        outgoing_query.outgoing = True
        assert [t.amount for t in tx.get_transfers(outgoing_query)] == [1000]

        no_match_query: MoneroTransferQuery = MoneroTransferQuery()
        no_match_query.amount = 999999
        assert tx.get_transfers(no_match_query) == []

    def test_tx_wallet_copy_preserves_output_wallet_type(self) -> None:
        tx: MoneroTxWallet = MoneroTxWallet()
        tx.hash = "a" * 64
        output: MoneroOutputWallet = MoneroOutputWallet()
        output.amount = 500000
        output.account_index = 2
        output.is_spent = True
        tx.outputs = [output]

        copy: MoneroTxWallet = tx.copy()
        assert len(copy.outputs) == 1
        assert isinstance(copy.outputs[0], MoneroOutputWallet)
        assert copy.outputs[0].account_index == 2
        assert copy.outputs[0].is_spent is True
