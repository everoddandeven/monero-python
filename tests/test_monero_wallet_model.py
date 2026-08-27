import pytest
import logging
import subprocess
import sys

from monero import (
    MoneroTxQuery, MoneroTransferQuery, MoneroOutputQuery,
    MoneroWalletConfig, MoneroDestination, MoneroUtils,
    MoneroTxConfig, MoneroSubaddress, MoneroAccount, MoneroTxWallet,
    MoneroOutputWallet, MoneroKeyImage, MoneroIntegratedAddress,
    MoneroKeyImageImportResult, MoneroMessageSignatureResult,
    MoneroMessageSignatureType, MoneroCheckTx, MoneroCheckReserve,
    MoneroMultisigInfo, MoneroMultisigInitResult, MoneroMultisigSignResult,
    MoneroAddressBookEntry, MoneroAccountTag, MoneroIncomingTransfer,
    MoneroOutgoingTransfer, IncomingTransferComparator, OutputComparator, MoneroTx,
    MoneroTxSet
)
from utils import BaseTestClass, TestUtils, AssertUtils

logger: logging.Logger = logging.getLogger("TestMoneroWalletModel")


@pytest.mark.unit
class TestMoneroWalletModel(BaseTestClass):
    """Test monero wallet data model."""

    #region Tests

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

    def test_destination(self) -> None:
        amount: int = MoneroUtils.xmr_to_atomic_units(1)
        dest: MoneroDestination = MoneroDestination(TestUtils.ADDRESS, amount)
        logger.debug(f"Testing destination: {dest.serialize()}")
        copy: MoneroDestination = dest.copy()
        AssertUtils.assert_equals(dest, copy)

    def test_wallet_config(self) -> None:
        config: MoneroWalletConfig = TestUtils.get_wallet_full_config(TestUtils.get_daemon_rpc_connection())
        logger.debug(f"Testing wallet config: {config.serialize()}")
        copy: MoneroWalletConfig = config.copy()
        AssertUtils.assert_equals(config, copy)
        config_str: str = config.serialize()
        deserialized_config: MoneroWalletConfig = MoneroWalletConfig.deserialize(config_str)
        logger.debug(f"Deserialized config: {deserialized_config.serialize()}")
        AssertUtils.assert_equals(config, deserialized_config)

    def test_tx_config(self) -> None:
        config: MoneroTxConfig = MoneroTxConfig()
        config.set_address(TestUtils.ADDRESS)
        config.amount = MoneroUtils.xmr_to_atomic_units(0.5)
        config.account_index = 0
        config.subaddress_indices = [i for i in range(10)]
        config.below_amount = MoneroUtils.xmr_to_atomic_units(0.1)
        config.can_split = True
        config.fee = MoneroUtils.xmr_to_atomic_units(0.00075)
        config.sweep_each_subaddress = False

        copy: MoneroTxConfig = config.copy()
        AssertUtils.assert_equals(config, copy)

        config_str: str = config.serialize()
        logger.debug(f"Serialized tx config: {config_str}")

        deserialized_config: MoneroTxConfig = MoneroTxConfig.deserialize(config_str)
        AssertUtils.assert_equals(config, deserialized_config)

    #endregion

    #region Serialize/deserialize integrity

    def test_subaddress_deserialize(self) -> None:
        subaddress: MoneroSubaddress = MoneroSubaddress()
        subaddress.account_index = 0
        subaddress.index = 1
        subaddress.address = TestUtils.ADDRESS
        subaddress.label = "primary"
        subaddress.balance = 1000000
        subaddress.unlocked_balance = 900000
        subaddress.is_used = True
        subaddress.num_unspent_outputs = 3
        subaddress.num_blocks_to_unlock = 0
        AssertUtils.assert_serialization_integrity(subaddress)

    def test_account_deserialize(self) -> None:
        account: MoneroAccount = MoneroAccount()
        account.index = 0
        account.balance = 1000000
        account.unlocked_balance = 900000
        account.primary_address = TestUtils.ADDRESS
        account.tag = "savings"
        # subaddresses is serialized as a sub-array but from_property_tree() never
        # reads it back (see test below)
        AssertUtils.assert_serialization_integrity(account)

    @pytest.mark.xfail(reason="monero_account::from_property_tree() never reads back \"subaddresses\" even though to_rapidjson_val() emits it", strict=True)
    def test_account_subaddresses_deserialize(self) -> None:
        account: MoneroAccount = MoneroAccount()
        account.subaddresses = [MoneroSubaddress()]
        json_str: str = account.serialize()
        logger.debug(f"Serialized account: {json_str}")
        assert "subaddresses" in json_str
        restored: MoneroAccount = MoneroAccount.deserialize(json_str)
        logger.debug(f"Deserialized account re-serialized: {restored.serialize()}")
        assert len(restored.subaddresses) == len(account.subaddresses)

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

    def test_output_wallet_deserialize(self) -> None:
        output_wallet: MoneroOutputWallet = MoneroOutputWallet()
        output_wallet.amount = 1000000
        output_wallet.index = 2
        key_image: MoneroKeyImage = MoneroKeyImage()
        key_image.hex = "a" * 64
        key_image.signature = "b" * 128
        output_wallet.key_image = key_image
        output_wallet.account_index = 0
        output_wallet.subaddress_index = 1
        output_wallet.is_spent = False
        output_wallet.is_frozen = False
        AssertUtils.assert_serialization_integrity(output_wallet)

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

    @pytest.mark.xfail(reason="monero_tx_query has monero_tx_wallet's fields of the same name, so from_property_tree() double-populates them", strict=True)
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

    @pytest.mark.xfail(reason="monero_tx_query::to_rapidjson_val() never serialized input_query/output_query", strict=True)
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

    def test_integrated_address_deserialize(self) -> None:
        address: MoneroIntegratedAddress = MoneroIntegratedAddress()
        address.standard_address = TestUtils.ADDRESS
        address.payment_id = "d" * 16
        address.integrated_address = TestUtils.ADDRESS
        AssertUtils.assert_serialization_integrity(address)

    def test_key_image_import_result_deserialize(self) -> None:
        result: MoneroKeyImageImportResult = MoneroKeyImageImportResult()
        result.height = 3000000
        result.spent_amount = 500000
        result.unspent_amount = 1500000
        AssertUtils.assert_serialization_integrity(result)

    def test_message_signature_result_deserialize(self) -> None:
        result: MoneroMessageSignatureResult = MoneroMessageSignatureResult()
        result.is_good = True
        result.is_old = False
        result.version = 2
        result.signature_type = MoneroMessageSignatureType.SIGN_WITH_SPEND_KEY
        AssertUtils.assert_serialization_integrity(result)

    def test_check_tx_deserialize(self) -> None:
        check: MoneroCheckTx = MoneroCheckTx()
        check.is_good = True
        check.in_tx_pool = False
        check.num_confirmations = 10
        check.received_amount = 500000
        AssertUtils.assert_serialization_integrity(check)

    def test_check_reserve_deserialize(self) -> None:
        check: MoneroCheckReserve = MoneroCheckReserve()
        check.is_good = True
        check.total_amount = 1000000
        check.unconfirmed_spent_amount = 0
        AssertUtils.assert_serialization_integrity(check)

    def test_multisig_info_deserialize(self) -> None:
        info: MoneroMultisigInfo = MoneroMultisigInfo()
        info.is_multisig = True
        info.is_ready = True
        info.threshold = 2
        info.num_participants = 3
        AssertUtils.assert_serialization_integrity(info)

    def test_multisig_init_result_deserialize(self) -> None:
        result: MoneroMultisigInitResult = MoneroMultisigInitResult()
        result.address = TestUtils.ADDRESS
        result.multisig_hex = "deadbeef"
        AssertUtils.assert_serialization_integrity(result)

    def test_multisig_sign_result_deserialize(self) -> None:
        result: MoneroMultisigSignResult = MoneroMultisigSignResult()
        result.signed_multisig_tx_hex = "deadbeef"
        result.tx_hashes = ["a" * 64, "b" * 64]
        AssertUtils.assert_serialization_integrity(result)

    def test_address_book_entry_deserialize(self) -> None:
        entry: MoneroAddressBookEntry = MoneroAddressBookEntry()
        entry.index = 0
        entry.address = TestUtils.ADDRESS
        entry.description = "friend"
        entry.payment_id = "e" * 16
        AssertUtils.assert_serialization_integrity(entry)

    def test_account_tag_deserialize(self) -> None:
        tag: MoneroAccountTag = MoneroAccountTag()
        tag.tag = "savings"
        tag.label = "Savings accounts"
        tag.account_indices = [0, 1, 2]
        AssertUtils.assert_serialization_integrity(tag)

    def test_tx_set_deserialize(self) -> None:
        tx_set: MoneroTxSet = MoneroTxSet()
        tx_set.unsigned_tx_hex = "deadbeef"
        tx_set.multisig_tx_hex = "beefdead"
        AssertUtils.assert_serialization_integrity(tx_set)

    @pytest.mark.xfail(reason="monero_tx_set::deserialize() bug", strict=True)
    def test_tx_set_signed_tx_hex_deserialize(self) -> None:
        tx_set: MoneroTxSet = MoneroTxSet()
        tx_set.signed_tx_hex = "deadbeef"
        AssertUtils.assert_serialization_integrity(tx_set)

    #endregion

    #region Copy / merge / comparators

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

    @pytest.mark.xfail(reason="merge_incoming_transfer() dereferences account/subaddress index unconditionally (boost::optional UB when unset); locally this just dedups wrongly, but the same NDEBUG/ODR-ambiguity root cause aborts the process in CI", strict=True)
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

    @pytest.mark.xfail(reason="monero_outgoing_transfer::merge() dereferences destination address/amount unconditionally", strict=True)
    def test_outgoing_transfer_merge_destinations_with_unset_fields(self) -> None:
        script: str = (
            "import monero, sys\n"
            # dirty the heap first: a clean freshly-started interpreter doesn't reliably
            # reproduce the crash, but a heap with realistic allocation churn (much closer to
            # a real test run or application) does, consistently
            "garbage = []\n"
            "for i in range(500):\n"
            "    tx = monero.MoneroTxWallet()\n"
            "    tx.hash = 'b' * 64 + str(i)\n"
            "    tx.note = 'x' * (i % 200)\n"
            "    garbage.append(tx)\n"
            "del garbage\n"
            "a = monero.MoneroOutgoingTransfer()\n"
            "a.amount = 500000\n"
            "a.account_index = 0\n"
            "a.destinations = [monero.MoneroDestination()]\n"
            "b = a.copy()\n"
            "b.destinations = [monero.MoneroDestination()]\n"
            "try:\n"
            "    a.merge(b)\n"
            "    sys.exit('merge() did not raise')\n"
            "except RuntimeError as e:\n"
            "    sys.exit(0 if str(e) == 'Destination vectors are different' else f'wrong message: {e}')\n"
        )
        result: subprocess.CompletedProcess[str] = subprocess.run([sys.executable, "-c", script], capture_output=True, text=True, timeout=30)
        logger.debug(f"subprocess exit code: {result.returncode}, stderr: {result.stderr.strip()}")
        assert result.returncode == 0, (
            f"outgoing_transfer.merge() did not cleanly raise 'Destination vectors are different' "
            f"(exit code {result.returncode}): {result.stderr.strip()[-300:]}"
        )

    def test_output_wallet_copy(self) -> None:
        output: MoneroOutputWallet = MoneroOutputWallet()
        output.amount = 1000000
        output.index = 2
        output.account_index = 0
        output.subaddress_index = 1
        output.is_spent = False
        output.is_frozen = False

        copy: MoneroOutputWallet = output.copy()
        assert copy is not output
        assert copy.serialize() == output.serialize()

    def test_output_wallet_merge(self) -> None:
        a: MoneroOutputWallet = MoneroOutputWallet()
        a.amount = 1000000
        a.index = 2
        a.account_index = 0
        a.subaddress_index = 1
        # a.tx is left unset on both sides so merge() won't recurse into tx merge

        b: MoneroOutputWallet = a.copy()
        b.is_spent = True  # a.is_spent is unset -> merge fills the gap
        a.merge(b)
        assert a.is_spent is True

    def test_output_wallet_lt_comparator(self) -> None:
        o1: MoneroOutputWallet = MoneroOutputWallet()
        o1.tx = MoneroTx()
        o1.account_index = 0
        o1.subaddress_index = 0
        o1.index = 0
        o1.key_image = MoneroKeyImage()
        o1.key_image.hex = "a" * 64

        o2: MoneroOutputWallet = MoneroOutputWallet()
        o2.tx = MoneroTx()
        o2.account_index = 0
        o2.subaddress_index = 0
        o2.index = 1
        o2.key_image = MoneroKeyImage()
        o2.key_image.hex = "b" * 64

        assert o1 < o2
        assert not (o2 < o1)
        assert OutputComparator.compare(o1, o2)
        assert not OutputComparator.compare(o2, o1)

        outputs: list[MoneroOutputWallet] = [o2, o1]
        outputs.sort()
        assert outputs[0] is o1
        assert outputs[1] is o2

    def test_tx_wallet_copy(self) -> None:
        tx: MoneroTxWallet = MoneroTxWallet()
        tx.hash = "a" * 64
        tx.is_confirmed = True
        tx.note = "hello"

        copy: MoneroTxWallet = tx.copy()
        assert copy is not tx
        assert copy.serialize() == tx.serialize()

    def test_tx_wallet_merge(self) -> None:
        a: MoneroTxWallet = MoneroTxWallet()
        a.hash = "a" * 64
        a.is_confirmed = True  # required: base monero_tx::merge() dereferences is_confirmed directly

        b: MoneroTxWallet = a.copy()
        b.note = "hello"  # a.note is unset -> merge fills the gap
        a.merge(b)
        assert a.note == "hello"

    @pytest.mark.xfail(reason="gen_utils::reconcile()'s bug", strict=True)
    def test_tx_wallet_merge_is_locked_can_become_false(self) -> None:
        a: MoneroTxWallet = MoneroTxWallet()
        a.hash = "a" * 64
        a.is_confirmed = True
        a.is_locked = False  # self: already unlocked
        b: MoneroTxWallet = a.copy()
        b.is_locked = True   # other: still locked
        a.merge(b)
        assert a.is_locked is False

    @pytest.mark.xfail(reason="TODO monero-cpp bug", strict=True)
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

    @pytest.mark.xfail(reason="TODO monero-cpp bug", strict=True)
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

    @pytest.mark.xfail(reason="TODO monero-cpp fix monero_tx::copy()", strict=True)
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

    def test_transfer_query_copy(self) -> None:
        query: MoneroTransferQuery = MoneroTransferQuery()
        query.amount = 500000
        query.incoming = True
        query.address = TestUtils.ADDRESS

        copy: MoneroTransferQuery = query.copy()
        assert copy is not query
        assert copy.serialize() == query.serialize()

    def test_output_query_copy(self) -> None:
        query: MoneroOutputQuery = MoneroOutputQuery()
        query.amount = 1000000
        query.min_amount = 100000
        query.max_amount = 2000000

        copy: MoneroOutputQuery = query.copy()
        assert copy is not query
        assert copy.serialize() == query.serialize()

    def test_tx_query_copy(self) -> None:
        query: MoneroTxQuery = MoneroTxQuery()
        query.hash = "a" * 64
        query.height = 3000000
        query.is_confirmed = True

        copy: MoneroTxQuery = query.copy()
        assert copy is not query
        assert copy.serialize() == query.serialize()

    #endregion
