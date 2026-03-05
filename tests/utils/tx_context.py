from __future__ import annotations

from typing import Optional
from monero import MoneroWallet, MoneroTxConfig


class TxContext:
    """Provides context or configuration for test methods to test a type."""

    wallet: Optional[MoneroWallet] = None
    """Context wallet"""
    config: Optional[MoneroTxConfig] = None
    """Transaction configuration"""
    has_outgoing_transfer: Optional[bool] = None
    """Expect outgoing transfer in tx"""
    has_incoming_transfers: Optional[bool] = None
    """Expect incoming transfers in tx"""
    has_destinations: Optional[bool] = None
    """Expect destinations in tx"""
    is_copy: Optional[bool] = None
    """Indicates if a copy is being tested which means back references won't be the same"""
    include_outputs: Optional[bool] = None
    """Expects outputs in tx"""
    is_send_response: Optional[bool] = None
    """Expect newly created tx"""
    is_sweep_response: Optional[bool] = None
    """Expect newly created tx from sweep action"""
    is_sweep_output_response: Optional[bool] = None
    """Expect newly created tx from specific output sweep"""
    # TODO monero-wallet-rpc: this only necessary because sweep_output does not return account index

    def __init__(self, ctx: Optional[TxContext] = None) -> None:
        """
        Initialize a new tx context.

        :param TxContext | None ctx: Transaction context to copy
        """
        if ctx is not None:
            # copy reference
            self.wallet = ctx.wallet
            self.config = ctx.config
            self.has_outgoing_transfer = ctx.has_outgoing_transfer
            self.has_incoming_transfers = ctx.has_incoming_transfers
            self.has_destinations = ctx.has_destinations
            self.is_copy = ctx.is_copy
            self.include_outputs = ctx.include_outputs
            self.is_send_response = ctx.is_send_response
            self.is_sweep_response = ctx.is_sweep_response
            self.is_sweep_output_response = ctx.is_sweep_output_response
