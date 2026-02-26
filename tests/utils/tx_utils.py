import logging

from abc import ABC
from typing import Optional
from random import shuffle
from monero import (
    MoneroWallet, MoneroTxQuery, MoneroTxWallet,
    MoneroBlock, MoneroTransfer, MoneroIncomingTransfer,
    MoneroOutgoingTransfer, MoneroDestination,
    MoneroUtils, MoneroOutputWallet, MoneroTx,
    MoneroOutput, MoneroKeyImage, MoneroDaemon,
    MoneroTxConfig, MoneroTxSet
)

from .tx_context import TxContext
from .gen_utils import GenUtils
from .test_context import TestContext
from .assert_utils import AssertUtils
from .test_utils import TestUtils

logger: logging.Logger = logging.getLogger("TxUtils")


class TxUtils(ABC):
    """Tx utils for tests"""

    __test__ = False

    MAX_FEE = 7500000*10000
    """Max tx fee"""

    @classmethod
    def test_key_image(cls, image: Optional[MoneroKeyImage], context: Optional[TestContext] = None) -> None:
        """Test monero key image"""
        assert image is not None
        assert image.hex is not None
        assert len(image.hex) > 0
        if image.signature is not None:
            assert len(image.signature) > 0

    @classmethod
    def test_output(cls, output: Optional[MoneroOutput], context: Optional[TestContext] = None) -> None:
        """Test monero output"""
        assert output is not None
        GenUtils.test_unsigned_big_integer(output.amount)
        if context is None:
            return
        assert output.tx is not None
        ctx = TestContext(context)
        if output.tx.in_tx_pool or ctx.has_output_indices is False:
            assert output.index is None
        else:
            assert output.index is not None
            assert output.index >= 0
            assert output.stealth_public_key is not None
            assert len(output.stealth_public_key) > 0

    @classmethod
    def test_input(cls, xmr_input: Optional[MoneroOutput], ctx: Optional[TestContext]) -> None:
        """Test monero input"""
        assert xmr_input is not None
        cls.test_output(xmr_input)
        cls.test_key_image(xmr_input.key_image, ctx)
        assert len(xmr_input.ring_output_indices) > 0

    @classmethod
    def test_input_wallet(cls, xmr_input: Optional[MoneroOutputWallet]) -> None:
        """Test monero input wallet"""
        assert xmr_input is not None
        assert xmr_input.key_image is not None
        assert xmr_input.key_image.hex is not None
        assert len(xmr_input.key_image.hex) > 0
        assert xmr_input.amount is None

    @classmethod
    def test_output_wallet(cls, output: Optional[MoneroOutputWallet]) -> None:
        """Test monero output wallet"""
        assert output is not None
        assert output.account_index is not None
        assert output.account_index >= 0
        assert output.subaddress_index is not None
        assert output.subaddress_index >= 0
        assert output.index is not None
        assert output.index >= 0
        assert output.is_spent is not None
        # TODO implement is_locked
        #assert output.is_locked is not None
        assert output.is_frozen is not None
        assert output.key_image is not None
        assert output.key_image.hex is not None
        assert len(output.key_image.hex) > 0
        GenUtils.test_unsigned_big_integer(output.amount, True)

        # output has circular reference to its transaction which has some initialized fields
        tx = output.tx
        assert tx is not None
        assert output in tx.outputs
        assert tx.hash is not None
        # TODO implement is_locked
        #assert tx.is_locked is not None
        # TODO monero-wallet-rpc: possible to get unconfirmed outputs?
        assert tx.is_confirmed is True
        assert tx.is_relayed is True
        assert tx.is_failed is False
        tx_height = tx.get_height()
        assert tx_height is not None
        assert tx_height > 0

        # test copying
        copy = output.copy()
        assert copy != output
        AssertUtils.assert_equals(copy, output)
        # TODO: should output copy do deep copy of tx so models are graph instead of tree?  Would need to work out circular references
        assert copy.tx is None

    @classmethod
    def test_destination(cls, dest: Optional[MoneroDestination]) -> None:
        """Test monero destination"""
        assert dest is not None
        assert dest.address is not None
        MoneroUtils.validate_address(dest.address, TestUtils.NETWORK_TYPE)
        GenUtils.test_unsigned_big_integer(dest.amount, True)

    @classmethod
    def test_incoming_transfer(cls, transfer: Optional[MoneroIncomingTransfer]) -> None:
        """Test monero incoming transfer"""
        assert transfer is not None
        assert transfer.is_incoming() is True
        assert transfer.is_outgoing() is False
        assert transfer.address is not None
        assert transfer.subaddress_index is not None
        assert transfer.subaddress_index >= 0
        assert transfer.num_suggested_confirmations is not None
        assert transfer.num_suggested_confirmations > 0

    @classmethod
    def test_outgoing_transfer(cls, transfer: Optional[MoneroOutgoingTransfer], ctx: TxContext) -> None:
        """Test monero outgoing transfer"""
        assert transfer is not None
        assert transfer.is_incoming() is False
        assert transfer.is_outgoing() is True
        if ctx.is_send_response is not True:
            assert len(transfer.subaddress_indices) > 0

        for subaddress_idx in transfer.subaddress_indices:
            assert subaddress_idx >= 0

        if len(transfer.addresses) > 0:
            assert len(transfer.subaddress_indices) == len(transfer.addresses)
            for address in transfer.addresses:
                assert address is not None

        # test destinations sum to outgoing amount
        if len(transfer.destinations) > 0:
            transfer_sum: int = 0
            for destination in transfer.destinations:
                cls.test_destination(destination)
                assert destination.amount is not None
                transfer_sum += destination.amount

            assert transfer_sum == transfer.amount, f"Destinations sum doesn't equal transfer amount: {transfer_sum} != {transfer.amount}"

    @classmethod
    def test_transfer(cls, transfer: Optional[MoneroTransfer], context: Optional[TxContext]) -> None:
        """Test monero transfer"""
        ctx = context if context is not None else TxContext()
        assert transfer is not None
        GenUtils.test_unsigned_big_integer(transfer.amount)
        if ctx.is_sweep_output_response is not True:
            assert transfer.account_index is not None
            assert transfer.account_index >= 0
        if transfer.is_incoming():
            assert isinstance(transfer, MoneroIncomingTransfer)
            cls.test_incoming_transfer(transfer)
        else:
            assert isinstance(transfer, MoneroOutgoingTransfer)
            cls.test_outgoing_transfer(transfer, ctx)

        # transfer and tx reference each other
        assert transfer.tx is not None
        if not AssertUtils.equals(transfer, transfer.tx.outgoing_transfer):
            assert len(transfer.tx.incoming_transfers) != 0
            assert transfer in transfer.tx.incoming_transfers, "Transaction does not reference given transfer"

    @classmethod
    def test_tx_wallet(cls, tx: Optional[MoneroTxWallet], context: Optional[TxContext]) -> None:
        """Test monero tx wallet"""
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
            cls.test_transfer(tx.outgoing_transfer, ctx)
            if ctx.is_sweep_response is True:
                assert len(tx.outgoing_transfer.destinations) == 1
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
                cls.test_transfer(transfer, ctx)
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
            config = ctx.config
            assert tx.is_confirmed is False
            cls.test_transfer(tx.outgoing_transfer, ctx)
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
                subtract_fee_from_dests = len(config.subtract_fee_from) > 0
                if ctx.is_sweep_response is True:
                    assert len(config.destinations) == 1
                    assert config.destinations[0].amount is None
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
            cls.test_input_wallet(wallet_input)

        # test outputs
        if tx.is_incoming is True and ctx.include_outputs is True:
            if tx.is_confirmed is True:
                assert len(tx.outputs) > 0
            else:
                assert len(tx.outputs) == 0

        for output in tx.get_outputs_wallet():
            cls.test_output_wallet(output)

        # TODO test deep copy
        #if ctx.is_copy is not True:
        #    cls.test_tx_wallet_copy(tx, ctx)

    @classmethod
    def test_txs_wallet(cls, txs: list[MoneroTxWallet], context: Optional[TxContext]) -> None:
        for tx in txs:
            cls.test_tx_wallet(tx, context)

    @classmethod
    def test_tx_copy(cls, tx: Optional[MoneroTx], context: Optional[TestContext]) -> None:
        """Test monero tx copy"""
        # copy tx and assert deep equality
        assert tx is not None
        copy = tx.copy()
        assert isinstance(copy, MoneroTx)
        assert copy.block is None
        if tx.block is not None:
            block_copy = tx.block.copy()
            block_copy.txs = [copy]

        AssertUtils.assert_equals(str(tx), str(copy))
        assert copy != tx

        # test different input references
        if len(copy.inputs) == 0:
            assert len(tx.inputs) == 0
        else:
            assert copy.inputs != tx.inputs
            for i, output in enumerate(copy.outputs):
                assert tx.outputs[i].amount == output.amount

        # test copied tx
        ctx = TestContext(context)
        ctx.do_not_test_copy = True # to prevent infinite recursion
        if tx.block is not None:
            block_copy = tx.block.copy()
            block_copy.txs = [copy]
            copy.block = block_copy

        cls.test_tx(copy, ctx)

        # test merging with copy
        merged = copy
        merged.merge(copy.copy())
        assert str(tx) == str(merged)

    @classmethod
    def test_tx(cls, tx: Optional[MoneroTx], ctx: Optional[TestContext]) -> None:
        """Test monero tx"""
        # check inputs
        assert tx is not None
        assert ctx is not None
        assert ctx.is_pruned is not None
        assert ctx.is_confirmed is not None
        assert ctx.from_get_tx_pool is not None

        # standard across all txs
        assert tx.hash is not None
        assert len(tx.hash) == 64
        if tx.is_relayed is None:
            assert tx.in_tx_pool is True
        else:
            assert tx.is_relayed is not None
        assert tx.is_confirmed is not None
        assert tx.in_tx_pool is not None
        assert tx.is_miner_tx is not None
        assert tx.is_double_spend_seen is not None
        assert tx.version is not None
        assert tx.version >= 0
        assert tx.unlock_time is not None
        assert tx.unlock_time >= 0
        assert tx.extra is not None
        assert len(tx.extra) > 0
        # TODO regtest daemon not returning tx fee...
        # GenUtils.test_unsigned_big_integer(tx.fee, True)

        # test presence of output indices
        # TODO change this over to outputs only
        if tx.is_miner_tx is True:
            # TODO how to get output indices for miner transactions?
            assert len(tx.output_indices) == 0
        if tx.in_tx_pool or ctx.from_get_tx_pool or ctx.has_output_indices is False:
            assert len(tx.output_indices) == 0
        else:
            assert len(tx.output_indices) > 0

        # test confirmed ctx
        if ctx.is_confirmed is True:
            assert tx.is_confirmed is True
        elif ctx.is_confirmed is False:
            assert tx.is_confirmed is False

        # test confirmed
        if tx.is_confirmed is True:
            block = tx.block
            assert block is not None
            assert tx in block.txs
            assert block.height is not None
            assert block.height > 0
            assert block.timestamp is not None
            assert block.timestamp > 0
            assert tx.relay is True
            assert tx.is_relayed is True
            assert tx.is_failed is False
            assert tx.in_tx_pool is False
            assert tx.is_double_spend_seen is False
            if ctx.from_binary_block is True:
                assert tx.num_confirmations is None
            else:
                assert tx.num_confirmations is not None
                assert tx.num_confirmations > 0
        else:
            assert tx.block is None
            assert tx.num_confirmations == 0

        # test in tx pool
        if tx.in_tx_pool:
            assert tx.is_confirmed is False
            assert tx.is_double_spend_seen is False
            assert tx.last_failed_height is None
            assert tx.last_failed_hash is None
            assert tx.received_timestamp is not None
            assert tx.received_timestamp > 0
            if ctx.from_get_tx_pool:
                assert tx.size is not None
                assert tx.size > 0
                assert tx.weight is not None
                assert tx.weight > 0
                assert tx.is_kept_by_block is not None
                assert tx.max_used_block_height is not None
                assert tx.max_used_block_height >= 0
                assert tx.max_used_block_hash is not None

            assert tx.last_failed_height is None
            assert tx.last_failed_hash is None
        else:
            assert tx.last_relayed_timestamp is None

        # test miner tx
        if tx.is_miner_tx:
            assert tx.fee == 0
            assert len(tx.inputs) == 0
            assert len(tx.signatures) == 0

        # test failed
        # TODO what else to test associated with failed
        if tx.is_failed:
            assert tx.received_timestamp is not None
            assert tx.received_timestamp > 0
        else:
            if tx.is_relayed is None:
                assert tx.relay is None
            elif tx.is_relayed:
                assert tx.is_double_spend_seen is False
            else:
                assert tx.is_relayed is False
                if ctx.from_get_tx_pool:
                    assert tx.relay is False
                    assert tx.is_double_spend_seen is not None

        assert tx.last_failed_height is None
        assert tx.last_failed_hash is None

        # received time only for tx pool or failed txs
        if tx.received_timestamp is not None:
            assert tx.in_tx_pool or tx.is_failed

        # test inputs and outputs
        if not tx.is_miner_tx:
            assert len(tx.inputs) > 0

        for tx_input in tx.inputs:
            assert tx == tx_input.tx
            cls.test_input(tx_input, ctx)

        assert len(tx.outputs) > 0
        for output in tx.outputs:
            assert tx == output.tx
            cls.test_output(output, ctx)

        # test pruned vs not pruned
        # tx might be pruned regardless of configuration
        is_pruned: bool = tx.pruned_hex is not None
        if ctx.is_pruned:
            assert is_pruned
        if ctx.from_get_tx_pool or ctx.from_binary_block:
            assert tx.prunable_hash is None
        else:
            assert tx.prunable_hash is not None

        if is_pruned:
            assert tx.rct_sig_prunable is None
            assert tx.size is None
            assert tx.last_relayed_timestamp is None
            assert tx.received_timestamp is None
            # TODO getting full hex in regtest regardless configuration
            # assert tx.full_hex is None, f"Expected None got: {tx.full_hex}"
            assert tx.pruned_hex is not None
        else:
            assert tx.version is not None
            assert tx.version >= 0
            assert tx.unlock_time is not None
            assert tx.unlock_time >= 0
            assert tx.extra is not None
            assert len(tx.extra) > 0

            if ctx.from_binary_block is True:
                # TODO: get_blocks_by_height() has inconsistent client-side pruning
                assert tx.full_hex is None
                assert tx.rct_sig_prunable is None
            else:
                assert tx.full_hex is not None
                assert len(tx.full_hex) > 0
                # TODO define and test this
                #assert tx.rct_sig_prunable is not None

            assert tx.is_double_spend_seen is False
            if tx.is_confirmed:
                assert tx.last_relayed_timestamp is None
                assert tx.received_timestamp is None
            else:
                if tx.is_relayed:
                    assert tx.last_relayed_timestamp is not None
                    assert tx.last_relayed_timestamp > 0
                else:
                    assert tx.last_relayed_timestamp is None

                assert tx.received_timestamp is not None
                assert tx.received_timestamp > 0

        # TODO test failed tx

        # TODO implement extra copy
        # test deep copy
        #if ctx.do_not_test_copy is not True:
        #    cls.test_tx_copy(tx, ctx)

    @classmethod
    def test_miner_tx(cls, miner_tx: Optional[MoneroTx]) -> None:
        """Test monero miner tx"""
        assert miner_tx is not None
        AssertUtils.assert_not_none(miner_tx.is_miner_tx)
        assert miner_tx.version is not None
        AssertUtils.assert_true(miner_tx.version >= 0)
        AssertUtils.assert_not_none(miner_tx.extra)
        AssertUtils.assert_true(len(miner_tx.extra) > 0)
        assert miner_tx.unlock_time is not None
        AssertUtils.assert_true(miner_tx.unlock_time >= 0)

        # TODO: miner tx does not have hashes in binary requests so this will fail, need to derive using prunable data
        # ctx = new TestContext()
        # ctx.has_json = false
        # ctx.is_pruned = true
        # ctx.is_full = false
        # ctx.is_confirmed = true
        # ctx.is_miner = true
        # ctx.from_get_tx_pool = true
        # cls.test_tx(miner_tx, ctx)

    @classmethod
    def get_and_test_txs(cls, wallet: MoneroWallet, query: Optional[MoneroTxQuery], ctx: Optional[TxContext], is_expected: bool, regtest: bool) -> list[MoneroTxWallet]:
        """Get and test txs from wallet"""
        copy: Optional[MoneroTxQuery] = query.copy() if query is not None else None
        txs = wallet.get_txs(query) if query is not None else wallet.get_txs()
        assert txs is not None

        if is_expected is False:
            assert len(txs) == 0

        if is_expected is True:
            assert len(txs) > 0

        cls.test_txs_wallet(txs, ctx)
        cls.test_get_txs_structure(txs, query, regtest)

        if query is not None:
            AssertUtils.assert_equals(copy, query)

        return txs

    @classmethod
    def is_tx_in_block(cls, tx: MoneroTxWallet, block: MoneroBlock) -> bool:
        """Check if transaction is included in block"""
        for block_tx in block.txs:
            if block_tx.hash == tx.hash:
                return True

        return False

    @classmethod
    def is_block_in_blocks(cls, block: MoneroBlock, blocks: set[MoneroBlock] | list[MoneroBlock]) -> bool:
        """Check if block is contained in set or list"""
        for b in blocks:
            if b == block:
                return True

        return False

    @classmethod
    def log_txs(cls, txs1: list[MoneroTx] | list[MoneroTxWallet], txs2: list[MoneroTxWallet]) -> None:
        num_txs1 = len(txs1)
        num_txs2 = len(txs2)
        assert num_txs1 == num_txs2, f"Txs size don't equal: {num_txs1} != {num_txs2}"
        for i, tx1 in enumerate(txs1):
            tx2 = txs2[i]
            idxs: list[str] = []
            for transfer in tx2.incoming_transfers:
                idxs.append(f"{transfer.account_index}:{transfer.subaddress_index}")

            logger.debug(f"BLOCK TX: {tx1.hash}, WALLET TX: {tx2.hash}, {idxs}")

    @classmethod
    def test_get_txs_structure(cls, txs: list[MoneroTxWallet], q: Optional[MoneroTxQuery], regtest: bool) -> None:
        """
        Tests the integrity of the full structure in the given txs from the block down
        to transfers / destinations.
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
                assert cls.is_tx_in_block(tx, tx.block)
                if not cls.is_block_in_blocks(tx.block, seen_blocks):
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
                        cls.log_txs(block.txs, txs[index:(index + len(block.txs))])
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
                    if prev_subaddress_idx:
                        prev_subaddress_idx = output.subaddress_index
                    else:
                        assert prev_subaddress_idx is not None
                        assert output.subaddress_index is not None
                        # TODO: this does not test that index < other index if subaddresses are equal
                        assert prev_subaddress_idx <= output.subaddress_index

    @classmethod
    def get_random_transactions(
            cls,
            wallet: MoneroWallet,
            query: Optional[MoneroTxQuery] = None,
            min_txs: Optional[int] = None,
            max_txs: Optional[int] = None
    ) -> list[MoneroTxWallet]:
        """Get random transaction from wallet"""
        txs = wallet.get_txs(query if query is not None else MoneroTxQuery())

        if min_txs is not None:
            assert len(txs) >= min_txs, f"{len(txs)}/{min_txs} transactions found with the query"

        shuffle(txs)

        if max_txs is None:
            return txs

        result: list[MoneroTxWallet] = []
        i = 0

        for tx in txs:
            result.append(tx)
            if i >= max_txs - 1:
                break
            i += 1

        return result

    @classmethod
    def get_confirmed_tx_hashes(cls, daemon: MoneroDaemon) -> list[str]:
        """Get confirmed tx hashes from daemon from last 5 blocks"""
        hashes: list[str] = []
        height: int = daemon.get_height()
        while len(hashes) < 5 and height > 0:
            height -= 1
            block = daemon.get_block_by_height(height)
            for tx_hash in block.tx_hashes:
                hashes.append(tx_hash)
        return hashes

    @classmethod
    def get_unrelayed_tx(cls, wallet: MoneroWallet, account_idx: int):
        """Get unrelayed tx from wallet account"""
        # TODO monero-project
        assert account_idx > 0, "Txs sent from/to same account are not properly synced from the pool"
        config = MoneroTxConfig()
        config.account_index = account_idx
        config.address = wallet.get_primary_address()
        config.amount = cls.MAX_FEE

        tx = wallet.create_tx(config)
        assert (tx.full_hex is None or tx.full_hex == "") is False
        assert tx.relay is False, f"Expected tx.relay to be False, got {tx.relay}"
        return tx

    @classmethod
    def test_common_tx_sets(cls, txs: list[MoneroTxWallet], has_signed: bool, has_unsigned: bool, has_multisig: bool) -> None:
        """
        Test common tx set in txs 
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
    def set_block_copy(cls, copy: MoneroTxWallet, tx: MoneroTxWallet) -> None:
        if copy.is_confirmed is not True:
            return

        assert tx.block is not None
        block = tx.block.copy()
        block.txs = [copy]
        copy.block = block

    @classmethod
    def txs_mergeable(cls, tx1: MoneroTxWallet, tx2: MoneroTxWallet) -> bool:
        try:
            copy1 = tx1.copy()
            copy2 = tx2.copy()
            cls.set_block_copy(copy1, tx1)
            cls.set_block_copy(copy2, tx2)
            copy1.merge(copy2)
            return True
        except Exception as e:
            logger.warning(f"Txs are not mergeable: {e}")
            return False
