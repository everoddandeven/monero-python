import logging

from typing import Optional

from monero import (
    MoneroTxWallet, MoneroTransfer, MoneroTxConfig,
    MoneroUtils, MoneroDestination
)

from .gen_utils import GenUtils
from .output_utils import OutputUtils
from .transfer_utils import TransferUtils
from .context import TxContext

logger: logging.Logger = logging.getLogger("TxWalletTester")


class TxWalletTester:

    tx: MoneroTxWallet
    ctx: TxContext

    def __init__(self, tx: MoneroTxWallet, context: Optional[TxContext]) -> None:
        self.tx = tx
        # validate / sanitize inputs
        self.ctx = TxContext(context)
        self.ctx.wallet = None # TODO: re-enable
        assert tx is not None
        if self.ctx.is_send_response is None or self.ctx.config is None:
            assert self.ctx.is_send_response is None, "if either send_request or is_send_response is defined, they must both be defined"
            assert self.ctx.config is None, "if either send_request or is_send_response is defined, they must both be defined"

    def _test_common(self) -> None:
        # test common field types
        assert self.tx.hash is not None
        assert self.tx.is_confirmed is not None
        assert self.tx.is_miner_tx is not None
        assert self.tx.is_failed is not None
        assert self.tx.is_relayed is not None
        assert self.tx.in_tx_pool is not None
        assert self.tx.is_locked is not None
        GenUtils.test_unsigned_big_integer(self.tx.fee)
        if self.tx.payment_id is not None:
            # default payment id converted to None
            assert MoneroTxWallet.DEFAULT_PAYMENT_ID != self.tx.payment_id
        if self.tx.note is not None:
            # empty notes converted to undefined
            assert len(self.tx.note) > 0

        assert self.tx.unlock_time is not None
        assert self.tx.unlock_time >= 0
        assert self.tx.size is None # TODO monero-wallet-rpc: add tx_size to get_transfers and get_transfer_by_txid
        assert self.tx.received_timestamp is None # TODO monero-wallet-rpc: return received timestamp (asked to file issue if wanted)

    def _test_send(self) -> None:
        # test send tx
        if self.ctx.is_send_response is True:
            assert self.tx.weight is not None
            assert self.tx.weight > 0
            assert len(self.tx.inputs) > 0
            for tx_input in self.tx.inputs:
                assert tx_input.tx == self.tx
        else:
            assert self.tx.weight is None
            assert len(self.tx.inputs) == 0

    def _test_pool_status(self) -> None:
        # test confirmed
        if self.tx.is_confirmed:
            assert self.tx.block is not None
            assert self.tx in self.tx.block.txs
            assert self.tx.block.height is not None
            assert self.tx.block.height > 0
            assert self.tx.block.timestamp is not None
            assert self.tx.block.timestamp > 0
            assert self.tx.relay is True
            assert self.tx.is_relayed is True
            assert self.tx.is_failed is False
            assert self.tx.in_tx_pool is False
            assert self.tx.is_double_spend_seen is False
            assert self.tx.num_confirmations is not None
            assert self.tx.num_confirmations > 0
        else:
            assert self.tx.block is None
            assert self.tx.num_confirmations is not None
            assert self.tx.num_confirmations == 0

        # test in tx pool
        if self.tx.in_tx_pool:
            assert self.tx.is_confirmed is False
            assert self.tx.relay is True
            assert self.tx.is_relayed is True
            assert self.tx.is_double_spend_seen is False
            assert self.tx.is_locked is True

            # these should be initialized unless a response from sending
            # TODO re-enable when received timestamp returned in wallet rpc
            #if cself.self.tx.is_send_response:
            #    assert self.tx.received_timestamp > 0
        else:
            assert self.tx.last_relayed_timestamp is None

    def _test_status(self) -> None:
        # test miner tx
        if self.tx.is_miner_tx:
            assert self.tx.fee is not None
            assert self.tx.fee == 0

        # test failed
        # TODO what else to test associated with failed
        if self.tx.is_failed:
            assert isinstance(self.tx.outgoing_transfer, MoneroTransfer)
            # TODO re-enable when received timestamp returned in wallet rpc
            #assert self.tx.received_timestamp > 0
        else:
            if self.tx.is_relayed:
                assert self.tx.is_double_spend_seen is False
            else:
                assert self.tx.relay is False
                assert self.tx.is_relayed is False
                assert self.tx.is_double_spend_seen is None

        assert self.tx.last_failed_height is None
        assert self.tx.last_failed_hash is None

        # received time only for tx pool or failed txs
        if self.tx.received_timestamp is not None:
            assert self.tx.in_tx_pool or self.tx.is_failed

        # test relayed tx
        if self.tx.is_relayed:
            assert self.tx.relay is True
        if self.tx.relay is False:
            assert (not self.tx.is_relayed) is True

    def _test_outgoing_transfer(self) -> None:
        # test outgoing transfer per configuration
        if self.ctx.has_outgoing_transfer is False:
            assert self.tx.outgoing_transfer is None
        if self.ctx.has_destinations is True:
            assert self.tx.outgoing_transfer is not None
            assert len(self.tx.outgoing_transfer.destinations) > 0

        # test outgoing transfer
        if self.tx.outgoing_transfer is not None:
            assert self.tx.is_outgoing is True
            TransferUtils.test_transfer(self.tx.outgoing_transfer, self.ctx)
            if self.ctx.is_sweep_response is True:
                assert len(self.tx.outgoing_transfer.destinations) == 1, f"Expected 1 tx, got {len(self.tx.outgoing_transfer.destinations)}"
            # TODO handle special cases
        else:
            assert len(self.tx.incoming_transfers) > 0
            assert self.tx.get_outgoing_amount() == 0
            assert self.tx.outgoing_transfer is None
            assert self.tx.ring_size is None
            assert self.tx.full_hex is None
            assert self.tx.metadata is None
            assert self.tx.key is None

    def _test_incoming_transfers(self) -> None:
        # test incoming transfers
        if len(self.tx.incoming_transfers) > 0:
            assert self.tx.is_incoming is True
            GenUtils.test_unsigned_big_integer(self.tx.get_incoming_amount())
            assert self.tx.is_failed is False

            # test each transfer and collect transfer sum
            transfer_sum: int = 0
            for transfer in self.tx.incoming_transfers:
                assert transfer.account_index is not None
                assert transfer.subaddress_index is not None
                TransferUtils.test_transfer(transfer, self.ctx)
                assert transfer.amount is not None
                transfer_sum += transfer.amount
                if self.ctx.wallet is not None:
                    addr = self.ctx.wallet.get_address(transfer.account_index, transfer.subaddress_index)
                    assert transfer.address == addr
                # TODO special case: transfer amount of 0

            # incoming transfers add up to incoming tx amount
            assert self.tx.get_incoming_amount() == transfer_sum
        else:
            assert self.tx.outgoing_transfer is not None
            assert self.tx.get_incoming_amount() == 0
            assert len(self.tx.incoming_transfers) == 0

    def _test_relay(self, config: MoneroTxConfig) -> None:
        if config.relay is True:
            # test relayed txs
            assert self.tx.in_tx_pool is True
            assert self.tx.relay is True
            assert self.tx.is_relayed is True
            assert self.tx.last_relayed_timestamp is not None
            assert self.tx.last_relayed_timestamp > 0
            assert self.tx.is_double_spend_seen is False
        else:
            # test non-relayed txs
            assert self.tx.in_tx_pool is False
            assert self.tx.relay is False
            assert self.tx.is_relayed is False
            assert self.tx.last_relayed_timestamp is None
            assert self.tx.is_double_spend_seen is None

    def _test_send_response(self) -> None:
        # test tx set
        assert self.tx.tx_set is not None
        found: bool = False
        for a_tx in self.tx.tx_set.txs:
            if a_tx == self.tx:
                found = True
                break

        if self.ctx.is_copy is True:
            assert found is False
        else:
            assert found

        # test common attributes
        assert self.ctx.config is not None
        config: MoneroTxConfig = self.ctx.config
        assert self.tx.is_confirmed is False
        TransferUtils.test_transfer(self.tx.outgoing_transfer, self.ctx)
        assert self.tx.ring_size == MoneroUtils.get_ring_size()
        assert self.tx.unlock_time == 0
        assert self.tx.block is None
        assert self.tx.key is not None
        assert len(self.tx.key) > 0
        assert self.tx.full_hex is not None
        assert len(self.tx.full_hex) > 0
        assert self.tx.metadata is not None
        assert self.tx.received_timestamp is None
        assert self.tx.is_locked is True

        # get locked state
        if self.tx.unlock_time == 0:
            assert self.tx.is_confirmed == (not self.tx.is_locked)
        else:
            assert self.tx.is_locked is True

        # TODO implement is_locked
        #for output in self.tx.get_outputs_wallet():
        #    assert self.tx.is_locked == output.is_locked

        # test destinations of sent tx
        assert self.tx.outgoing_transfer is not None
        if len(self.tx.outgoing_transfer.destinations) == 0:
            assert config.can_split is True
            # TODO: remove this after >18.3.1 when amounts_by_dest_list official
            logger.warning("Destinations not returned from split transactions")
        else:
            subtract_fee_from_dests: bool = len(config.subtract_fee_from) > 0
            if self.ctx.is_sweep_response is True:
                dests: list[MoneroDestination] = config.get_normalized_destinations()
                assert len(dests) == 1
                assert dests[0].amount is None
                if not subtract_fee_from_dests:
                    assert self.tx.outgoing_transfer.amount == self.tx.outgoing_transfer.destinations[0].amount

        self._test_relay(config)

    def _test_inputs_and_outputs(self) -> None:
        # test inputs
        if self.tx.is_outgoing is True and self.ctx.is_send_response is True:
            assert len(self.tx.inputs) > 0

        for self.wallet_input in self.tx.get_inputs_wallet():
            OutputUtils.test_input_wallet(self.wallet_input)

        # test outputs
        if self.tx.is_incoming is True and self.ctx.include_outputs is True:
            if self.tx.is_confirmed is True:
                assert len(self.tx.outputs) > 0
            else:
                assert len(self.tx.outputs) == 0

        for output in self.tx.get_outputs_wallet():
            OutputUtils.test_output_wallet(output)

    def run(self) -> None:
        """Run test."""
        self._test_common()
        self._test_send()
        self._test_pool_status()
        self._test_status()
        self._test_outgoing_transfer()
        self._test_incoming_transfers()

        if self.ctx.is_send_response:
            self._test_send_response()
        else:
            # test tx result query
            # tx set only initialized on send responses
            assert self.tx.tx_set is None
            assert self.tx.ring_size is None
            assert self.tx.key is None
            assert self.tx.full_hex is None
            assert self.tx.metadata is None
            assert self.tx.last_relayed_timestamp is None

        self._test_inputs_and_outputs()
