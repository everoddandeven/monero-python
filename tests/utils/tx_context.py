from __future__ import annotations

from typing import Optional
from monero import MoneroWallet, MoneroTxConfig


class TxContext:

    wallet: Optional[MoneroWallet]
    config: Optional[MoneroTxConfig]
    has_outgoing_transfer: Optional[bool]
    has_incoming_transfers: Optional[bool]
    has_destinations: Optional[bool]
    is_copy: Optional[bool] # indicates if a copy is being tested which means back references won't be the same
    include_outputs: Optional[bool]
    is_send_response: Optional[bool]
    is_sweep_response: Optional[bool]
    # TODO monero-wallet-rpc: this only necessary because sweep_output does not return account index
    is_sweep_output_response: Optional[bool]

    def __init__(self, ctx: Optional[TxContext] = None) -> None:
        self.wallet = ctx.wallet if ctx is not None else None
        self.config = ctx.config if ctx is not None else None
        self.has_outgoing_transfer = ctx.has_outgoing_transfer if ctx is not None else None
        self.has_incoming_transfers = ctx.has_incoming_transfers if ctx is not None else None
        self.has_destinations = ctx.has_destinations if ctx is not None else None
        self.is_copy = ctx.is_copy if ctx is not None else None
        self.include_outputs = ctx.include_outputs if ctx is not None else None
        self.is_send_response = ctx.is_send_response if ctx is not None else None
        self.is_sweep_response = ctx.is_sweep_response if ctx is not None else None
        self.is_sweep_output_response = ctx.is_sweep_output_response if ctx is not None else None
