import logging

from abc import ABC
from typing import Optional


from monero import (
    MoneroTransfer, MoneroTxWallet,
    MoneroTxConfig, MoneroUtils,
    MoneroDestination, MoneroTxSet,
    MoneroTxQuery, MoneroBlock,
    MoneroNetworkType, MoneroCheckTx,
    MoneroCheckReserve
)

from .assert_utils import AssertUtils
from .gen_utils import GenUtils
from .context import TxContext
from .block_utils import BlockUtils
from .output_utils import OutputUtils
from .transfer_utils import TransferUtils


logger: logging.Logger = logging.getLogger("TxWalletUtils")


class TxWalletUtils(ABC):

    MAX_FEE: int = 7500000*10000
    """Max tx fee."""

    @classmethod
    def test_tx_wallet(cls, tx: Optional[MoneroTxWallet], context: Optional[TxContext] = None) -> None:
        """Test monero tx wallet.

        :param MoneroTxWallet | None tx: wallet transaction to test.
        :param TxContext | None context: test context (default `None`).
        """
        # validate / sanitize inputs
        ctx = TxContext(context)
        ctx.wallet = None # TODO: re-enable
        assert tx is not None
        if ctx.is_send_response is None or ctx.config is None:
            assert ctx.is_send_response is None, "if either sendRequest or isSendResponse is defined, they must both be defined"
            assert ctx.config is None, "if either sendRequest or isSendResponse is defined, they must both be defined"

        # test common field types
        assert tx.hash is not None
        assert tx.is_confirmed is not None
        assert tx.is_miner_tx is not None
        assert tx.is_failed is not None
        assert tx.is_relayed is not None
        assert tx.in_tx_pool is not None
        assert tx.is_locked is not None
        GenUtils.test_unsigned_big_integer(tx.fee)
        if tx.payment_id is not None:
            # default payment id converted to None
            assert MoneroTxWallet.DEFAULT_PAYMENT_ID != tx.payment_id
        if tx.note is not None:
            # empty notes converted to undefined
            assert len(tx.note) > 0

        assert tx.unlock_time is not None
        assert tx.unlock_time >= 0
        assert tx.size is None # TODO monero-wallet-rpc: add tx_size to get_transfers and get_transfer_by_txid
        assert tx.received_timestamp is None # TODO monero-wallet-rpc: return received timestamp (asked to file issue if wanted)

        # test send tx
        if ctx.is_send_response is True:
            assert tx.weight is not None
            assert tx.weight > 0
            assert len(tx.inputs) > 0
            for tx_input in tx.inputs:
                assert tx_input.tx == tx
        else:
            assert tx.weight is None
            assert len(tx.inputs) == 0

        # test confirmed
        if tx.is_confirmed:
            assert tx.block is not None
            assert tx in tx.block.txs
            assert tx.block.height is not None
            assert tx.block.height > 0
            assert tx.block.timestamp is not None
            assert tx.block.timestamp > 0
            assert tx.relay is True
            assert tx.is_relayed is True
            assert tx.is_failed is False
            assert tx.in_tx_pool is False
            assert tx.is_double_spend_seen is False
            assert tx.num_confirmations is not None
            assert tx.num_confirmations > 0
        else:
            assert tx.block is None
            assert tx.num_confirmations is not None
            assert tx.num_confirmations == 0

        # test in tx pool
        if tx.in_tx_pool:
            assert tx.is_confirmed is False
            assert tx.relay is True
            assert tx.is_relayed is True
            assert tx.is_double_spend_seen is False
            assert tx.is_locked is True

            # these should be initialized unless a response from sending
            # TODO re-enable when received timestamp returned in wallet rpc
            #if ctx.is_send_response:
            #    assert tx.received_timestamp > 0
        else:
            assert tx.last_relayed_timestamp is None

        # test miner tx
        if tx.is_miner_tx:
            assert tx.fee is not None
            assert tx.fee == 0

        # test failed
        # TODO what else to test associated with failed
        if tx.is_failed:
            assert isinstance(tx.outgoing_transfer, MoneroTransfer)
            # TODO re-enable when received timestamp returned in wallet rpc
            #assert tx.received_timestamp > 0
        else:
            if tx.is_relayed:
                assert tx.is_double_spend_seen is False
            else:
                assert tx.relay is False
                assert tx.is_relayed is False
                assert tx.is_double_spend_seen is None

        assert tx.last_failed_height is None
        assert tx.last_failed_hash is None

        # received time only for tx pool or failed txs
        if tx.received_timestamp is not None:
            assert tx.in_tx_pool or tx.is_failed

        # test relayed tx
        if tx.is_relayed:
            assert tx.relay is True
        if tx.relay is False:
            assert (not tx.is_relayed) is True

        # test outgoing transfer per configuration
        if ctx.has_outgoing_transfer is False:
            assert tx.outgoing_transfer is None
        if ctx.has_destinations is True:
            assert tx.outgoing_transfer is not None
            assert len(tx.outgoing_transfer.destinations) > 0

        # test outgoing transfer
        if tx.outgoing_transfer is not None:
            assert tx.is_outgoing is True
            TransferUtils.test_transfer(tx.outgoing_transfer, ctx)
            if ctx.is_sweep_response is True:
                assert len(tx.outgoing_transfer.destinations) == 1, f"Expected 1 tx, got {len(tx.outgoing_transfer.destinations)}"
            # TODO handle special cases
        else:
            assert len(tx.incoming_transfers) > 0
            assert tx.get_outgoing_amount() == 0
            assert tx.outgoing_transfer is None
            assert tx.ring_size is None
            assert tx.full_hex is None
            assert tx.metadata is None
            assert tx.key is None

        # test incoming transfers
        if len(tx.incoming_transfers) > 0:
            assert tx.is_incoming is True
            GenUtils.test_unsigned_big_integer(tx.get_incoming_amount())
            assert tx.is_failed is False

            # test each transfer and collect transfer sum
            transfer_sum: int = 0
            for transfer in tx.incoming_transfers:
                TransferUtils.test_transfer(transfer, ctx)
                assert transfer.amount is not None
                transfer_sum += transfer.amount
                if ctx.wallet is not None:
                    addr = ctx.wallet.get_address(transfer.account_index, transfer.subaddress_index)
                    assert transfer.address == addr
                # TODO special case: transfer amount of 0

            # incoming transfers add up to incoming tx amount
            assert tx.get_incoming_amount() == transfer_sum
        else:
            assert tx.outgoing_transfer is not None
            assert tx.get_incoming_amount() == 0
            assert len(tx.incoming_transfers) == 0

        # test tx results from send or relay
        if ctx.is_send_response is True:
            # test tx set
            assert tx.tx_set is not None
            found: bool = False
            for a_tx in tx.tx_set.txs:
                if a_tx == tx:
                    found = True
                    break

            if ctx.is_copy is True:
                assert found is False
            else:
                assert found

            # test common attributes
            assert ctx.config is not None
            config: MoneroTxConfig = ctx.config
            assert tx.is_confirmed is False
            TransferUtils.test_transfer(tx.outgoing_transfer, ctx)
            assert tx.ring_size == MoneroUtils.get_ring_size()
            assert tx.unlock_time == 0
            assert tx.block is None
            assert tx.key is not None
            assert len(tx.key) > 0
            assert tx.full_hex is not None
            assert len(tx.full_hex) > 0
            assert tx.metadata is not None
            assert tx.received_timestamp is None
            assert tx.is_locked is True

            # get locked state
            if tx.unlock_time == 0:
                assert tx.is_confirmed == (not tx.is_locked)
            else:
                assert tx.is_locked is True

            # TODO implement is_locked
            #for output in tx.get_outputs_wallet():
            #    assert tx.is_locked == output.is_locked

            # test destinations of sent tx
            assert tx.outgoing_transfer is not None
            if len(tx.outgoing_transfer.destinations) == 0:
                assert config.can_split is True
                # TODO: remove this after >18.3.1 when amounts_by_dest_list official
                logger.warning("Destinations not returned from split transactions")
            else:
                subtract_fee_from_dests: bool = len(config.subtract_fee_from) > 0
                if ctx.is_sweep_response is True:
                    dests: list[MoneroDestination] = config.get_normalized_destinations()
                    assert len(dests) == 1
                    assert dests[0].amount is None
                    if not subtract_fee_from_dests:
                        assert tx.outgoing_transfer.amount == tx.outgoing_transfer.destinations[0].amount

            if config.relay is True:
                # test relayed txs
                assert tx.in_tx_pool is True
                assert tx.relay is True
                assert tx.is_relayed is True
                assert tx.last_relayed_timestamp is not None
                assert tx.last_relayed_timestamp > 0
                assert tx.is_double_spend_seen is False
            else:
                # test non-relayed txs
                assert tx.in_tx_pool is False
                assert tx.relay is False
                assert tx.is_relayed is False
                assert tx.last_relayed_timestamp is None
                assert tx.is_double_spend_seen is None

        else:
            # test tx result query
            # tx set only initialized on send responses
            assert tx.tx_set is None
            assert tx.ring_size is None
            assert tx.key is None
            assert tx.full_hex is None
            assert tx.metadata is None
            assert tx.last_relayed_timestamp is None

        # test inputs
        if tx.is_outgoing is True and ctx.is_send_response is True:
            assert len(tx.inputs) > 0

        for wallet_input in tx.get_inputs_wallet():
            OutputUtils.test_input_wallet(wallet_input)

        # test outputs
        if tx.is_incoming is True and ctx.include_outputs is True:
            if tx.is_confirmed is True:
                assert len(tx.outputs) > 0
            else:
                assert len(tx.outputs) == 0

        for output in tx.get_outputs_wallet():
            OutputUtils.test_output_wallet(output)

        # TODO test deep copy
        #if ctx.is_copy is not True:
        #    cls.test_tx_wallet_copy(tx, ctx)

    @classmethod
    def test_txs_wallet(cls, txs: list[MoneroTxWallet], context: Optional[TxContext]) -> None:
        """Test a list of transactions.

        :param list[MoneroTxWallet] txs: transactions to test.
        :param TxContext | None context: test context.
        """
        for tx in txs:
            cls.test_tx_wallet(tx, context)

    @classmethod
    def test_described_tx_set(cls, described_tx_set: MoneroTxSet, network_type: MoneroNetworkType) -> None:
        """Test described tx set.

        :param MoneroTxSet described_tx_set: described tx set to test.
        :param MoneroNetworkType network_type: tx set network type.
        """
        assert len(described_tx_set.txs) > 0
        assert described_tx_set.signed_tx_hex is None
        assert described_tx_set.unsigned_tx_hex is None

        # test each transaction
        # TODO use common tx wallet test?
        assert described_tx_set.multisig_tx_hex is None
        for parsed_tx in described_tx_set.txs:
            # TODO monero-cpp full wallet is not assigning tx set to parsed txs
            #assert parsed_tx.tx_set is not None
            #assert parsed_tx.tx_set == described_tx_set, f"{parsed_tx.tx_set.serialize()} != {described_tx_set.serialize()}"
            GenUtils.test_unsigned_big_integer(parsed_tx.input_sum, True)
            GenUtils.test_unsigned_big_integer(parsed_tx.output_sum, True)
            GenUtils.test_unsigned_big_integer(parsed_tx.fee)
            GenUtils.test_unsigned_big_integer(parsed_tx.change_amount)
            if parsed_tx.change_amount == 0:
                assert parsed_tx.change_address is None
            else:
                assert parsed_tx.change_address is not None
                MoneroUtils.validate_address(parsed_tx.change_address, network_type)
            assert parsed_tx.ring_size is not None
            assert parsed_tx.ring_size > 1
            assert parsed_tx.unlock_time is not None
            assert parsed_tx.unlock_time >= 0
            assert parsed_tx.num_dummy_outputs is not None
            assert parsed_tx.num_dummy_outputs >= 0
            assert parsed_tx.extra_hex is not None
            assert len(parsed_tx.extra_hex) > 0
            assert parsed_tx.payment_id is None or len(parsed_tx.payment_id) > 0
            assert parsed_tx.is_outgoing is True
            assert parsed_tx.outgoing_transfer is not None
            assert len(parsed_tx.outgoing_transfer.destinations) > 0
            assert parsed_tx.is_incoming is None
            for destination in parsed_tx.outgoing_transfer.destinations:
                TransferUtils.test_destination(destination)

    @classmethod
    def test_get_txs_structure(cls, txs: list[MoneroTxWallet], q: Optional[MoneroTxQuery], regtest: bool) -> None:
        """
        Tests the integrity of the full structure in the given txs from the block down
        to transfers / destinations.

        :param list[MoneroTxWallet] txs: list of txs to get structure from.
        :param MoneroTxQuery | None q: filter txs by query, if set.
        :param bool regtest: indicates if running test on regtest network.
        """
        query = q if q is not None else MoneroTxQuery()
        # collect unique blocks in order
        seen_blocks: set[MoneroBlock] = set()
        blocks: list[MoneroBlock] = []
        unconfirmed_txs: list[MoneroTxWallet] = []

        for tx in txs:
            if tx.block is None:
                unconfirmed_txs.append(tx)
            else:
                assert BlockUtils.is_tx_in_block(tx.hash, tx.block)
                if tx.block not in seen_blocks:
                    seen_blocks.add(tx.block)
                    blocks.append(tx.block)

        # tx hashes must be in order if requested
        if len(query.hashes) > 0:
            assert len(txs) == len(query.hashes)
            for i, query_hash in enumerate(query.hashes):
                assert query_hash == txs[i].hash

        # test that txs and blocks reference each other and blocks are in ascending order unless specific tx hashes queried
        index: int = 0
        prev_block_height: Optional[int] = None
        for block in blocks:
            if prev_block_height is None:
                prev_block_height = block.height
            elif len(query.hashes) == 0:
                assert block.height is not None
                msg = f"Blocks are not in order of heights: {prev_block_height} vs {block.height}"
                assert block.height > prev_block_height, msg

            for tx in block.txs:
                assert tx.block == block
                if len(query.hashes) == 0:
                    other = txs[index]
                    if not regtest:
                        assert other.hash == tx.hash, "Txs in block are not in order"
                        # verify tx order is self-consistent with blocks unless txs manually re-ordered by querying by hash
                        assert other == tx
                    else:
                        # TODO regtest wallet2 has inconsinstent txs order betwenn
                        assert other in block.txs, "Tx not found in block"

                index += 1

        assert len(txs) == index + len(unconfirmed_txs), f"txs: {len(txs)}, unconfirmed txs: {len(unconfirmed_txs)}, index: {index}"

        # test that incoming transfers are in order of ascending accounts and subaddresses
        for tx in txs:
            if len(tx.incoming_transfers) == 0:
                continue

            prev_account_idx: Optional[int] = None
            prev_subaddress_idx: Optional[int] = None
            for transfer in tx.incoming_transfers:
                if prev_account_idx is None:
                    prev_account_idx = transfer.account_index

                else:
                    assert prev_account_idx is not None
                    assert transfer.account_index is not None
                    assert prev_account_idx <= transfer.account_index
                    if prev_account_idx < transfer.account_index:
                        prev_subaddress_idx = None
                        prev_account_idx = transfer.account_index
                    if prev_subaddress_idx is None:
                        prev_subaddress_idx = transfer.subaddress_index
                    else:
                        assert transfer.subaddress_index is not None
                        assert prev_subaddress_idx < transfer.subaddress_index

        # test that outputs are in order of ascending accounts and subaddresses
        for tx in txs:
            if len(tx.outputs) == 0:
                continue

            prev_account_idx: Optional[int] = None
            prev_subaddress_idx: Optional[int] = None
            for output in tx.get_outputs_wallet():
                if prev_account_idx is None:
                    prev_account_idx = output.account_index
                else:
                    assert output.account_index is not None
                    assert prev_account_idx <= output.account_index
                    if prev_account_idx < output.account_index:
                        prev_subaddress_idx = None
                        prev_account_idx = output.account_index
                    if prev_subaddress_idx is None:
                        prev_subaddress_idx = output.subaddress_index
                    else:
                        assert prev_subaddress_idx is not None
                        assert output.subaddress_index is not None
                        # TODO: this does not test that index < other index if subaddresses are equal
                        assert prev_subaddress_idx <= output.subaddress_index

    @classmethod
    def test_common_tx_sets(cls, txs: list[MoneroTxWallet], has_signed: bool, has_unsigned: bool, has_multisig: bool) -> None:
        """Test common tx set in txs.

        :param list[MoneroTxWallet] txs: txs to test common sets.
        :param bool has_signed: expects signed tx hex to be defined in tx set.
        :param bool has_unsigned: expects unsigned tx hex to be defined in tx set.
        :param bool has_multisig: expects multisig tx hex to be defined in tx set.
        """
        assert len(txs) > 0
        # assert that all sets are same reference
        tx_set: Optional[MoneroTxSet] = None
        for i, tx in enumerate(txs):
            assert isinstance(tx, MoneroTxWallet)
            if i == 0:
                tx_set = tx.tx_set
            else:
                assert tx.tx_set == tx_set

        # test expected set
        assert tx_set is not None

        if has_signed:
            # check signed tx hex
            assert tx_set.signed_tx_hex is not None
            assert len(tx_set.signed_tx_hex) > 0

        if has_unsigned:
            # check unsigned tx hex
            assert tx_set.unsigned_tx_hex is not None
            assert len(tx_set.unsigned_tx_hex) > 0

        if has_multisig:
            # check multisign tx hex
            assert tx_set.multisig_tx_hex is not None
            assert len(tx_set.multisig_tx_hex) > 0

    @classmethod
    def test_spend_tx(cls, spend_tx: Optional[MoneroTxWallet]) -> None:
        """Test spend transaction.

        :param MoneroTxWallet | None spend_tx: Spend transaction to test.
        """
        # validate spend tx
        assert spend_tx is not None
        assert len(spend_tx.inputs) > 0
        # validate tx inputs
        for input_wallet in spend_tx.inputs:
            assert input_wallet.key_image is not None
            assert input_wallet.key_image.hex is not None
            assert len(input_wallet.key_image.hex) > 0

    @classmethod
    def test_check_tx(cls, tx: Optional[MoneroTxWallet], check: MoneroCheckTx) -> None:
        """Test tx with check result.

        :param MoneroTxWallet | None tx: transaction to test.
        :param MoneroCheckTx check: transaction check result to test.
        """
        assert tx is not None
        assert check.is_good is not None
        if check.is_good is True:
            assert check.num_confirmations is not None
            assert check.num_confirmations >= 0
            assert check.in_tx_pool is not None
            GenUtils.test_unsigned_big_integer(check.received_amount)
            if check.in_tx_pool is True:
                assert check.num_confirmations == 0
            else:
                # TODO (monero-wall-rpc) this fails (confirmations is 0) for (at least one) transaction
                # that has 1 confirmation on test_check_tx_key()
                assert check.num_confirmations > 0
        else:
            assert check.in_tx_pool is None
            assert check.num_confirmations is None
            assert check.received_amount is None

    @classmethod
    def test_check_reserve(cls, check: MoneroCheckReserve) -> None:
        """Test wallet check reserve.

        :param MoneroCheckReserve check: reserve check to test.
        """
        assert check.is_good is not None
        if check.is_good is True:
            assert check.total_amount is not None
            GenUtils.test_unsigned_big_integer(check.total_amount)
            assert check.total_amount >= 0

            assert check.unconfirmed_spent_amount is not None
            GenUtils.test_unsigned_big_integer(check.unconfirmed_spent_amount)
            assert check.unconfirmed_spent_amount >= 0
        else:
            assert check.total_amount is None
            assert check.unconfirmed_spent_amount is None

    @classmethod
    def set_block_copy(cls, copy: MoneroTxWallet, tx: MoneroTxWallet) -> None:
        """
        Replace tx block reference with copy.

        :param MoneroTxWallet copy: copy transaction reference.
        :param MoneroTxWallet tx: original transaction reference.
        """
        # skip unconfirmed tx
        if copy.is_confirmed is not True:
            return

        # copy block
        assert tx.block is not None
        block = tx.block.copy()

        # set copy tx in block copy
        block.txs = [copy]

        # set block copy reference to tx copy
        copy.block = block

    @classmethod
    def txs_mergeable(cls, tx1: MoneroTxWallet, tx2: MoneroTxWallet) -> bool:
        """Check if txs are mergeable.

        :param MoneroTxWallet tx1: first tx to check merge with.
        :param MoneroTxWallet tx2: second tx to check merge with.
        :returns bool: `True` if txs are mergeable, `False` otherwise.
        """
        try:
            # copy txs
            copy1 = tx1.copy()
            copy2 = tx2.copy()
            # set block copies
            cls.set_block_copy(copy1, tx1)
            cls.set_block_copy(copy2, tx2)
            # test merge
            copy1.merge(copy2)
            return True
        except Exception as e:
            # merge failed
            logger.warning(f"Txs are not mergeable: {e}")
            return False

    @classmethod
    def assert_list_txs_equals(cls, txs1: list[MoneroTxWallet], txs2: list[MoneroTxWallet], check_order: bool = False) -> None:
        """Checks txs lists equality.

        :param list[MoneroTxWallet] txs1: first list to check equality.
        :param list[MoneroTxWallet] txs2: second list to check equality.
        :param bool check_order: check also order (default `False`).
        """
        # assert lists have same size
        assert len(txs1) == len(txs2), "Txs lists count doesn't equal"

        if check_order:
            # check lists have same objects and order
            AssertUtils.assert_list_equals(txs1, txs2, "Txs lists doesn't equal")
            return

        # collect tx hashes
        tx_hashes1: list[str] = []
        tx_hashes2: list[str] = []

        for i, tx1 in enumerate(txs1):
            tx2: MoneroTxWallet = txs2[i]
            assert tx1.hash is not None
            assert tx2.hash is not None
            tx_hashes1.append(tx1.hash)
            tx_hashes2.append(tx2.hash)

        # assert that lists have same hashes
        for tx_hash1 in tx_hashes1:
            assert tx_hash1 in tx_hashes2
