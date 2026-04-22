import logging

from abc import ABC
from typing import Optional

from monero import (
    MoneroTransfer, MoneroIncomingTransfer, MoneroOutgoingTransfer,
    MoneroDestination, MoneroUtils
)

from .gen_utils import GenUtils
from .context import TxContext
from .test_utils import TestUtils

logger: logging.Logger = logging.getLogger("TransferUtils")


class TransferUtils(ABC):
    """Monero transfer test utilities."""

    @classmethod
    def test_destination(cls, dest: Optional[MoneroDestination]) -> None:
        """Test monero destination.

        :param MoneroDestination | None dest: destination to test.
        """
        assert dest is not None
        assert dest.address is not None
        MoneroUtils.validate_address(dest.address, TestUtils.NETWORK_TYPE)
        GenUtils.test_unsigned_big_integer(dest.amount, True)

    @classmethod
    def test_incoming_transfer(cls, transfer: Optional[MoneroIncomingTransfer]) -> None:
        """Test monero incoming transfer.

        :param MoneroIncomingTransfer | None transfer: transfer to test.
        """
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
        """Test monero outgoing transfer.

        :param MoneroOutgoingTransfer | None transfer: outgoing transfer to test.
        :param TxContext ctx: test context.
        """
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
        """Test monero transfer.

        :param MoneroTransfer | None transfer: transfer to test.
        :param TxContext | None: test context.
        """
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
        if transfer != transfer.tx.outgoing_transfer:
            assert len(transfer.tx.incoming_transfers) != 0
            assert transfer in transfer.tx.incoming_transfers, "Transaction does not reference given transfer"
