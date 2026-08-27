from __future__ import annotations

import json

from typing import Any, Optional
from monero import MoneroWallet, MoneroTxConfig

from .serializable_context import SerializableContext


class TxContext(SerializableContext):
    """Provides context or configuration for test methods to test a type."""

    wallet: Optional[MoneroWallet] = None
    """Context wallet."""
    config: Optional[MoneroTxConfig] = None
    """Transaction configuration."""
    has_outgoing_transfer: Optional[bool] = None
    """Expect outgoing transfer in tx."""
    has_incoming_transfers: Optional[bool] = None
    """Expect incoming transfers in tx."""
    has_destinations: Optional[bool] = None
    """Expect destinations in tx."""
    is_copy: Optional[bool] = None
    """Indicates if a copy is being tested which means back references won't be the same."""
    include_outputs: Optional[bool] = None
    """Expects outputs in tx."""
    is_send_response: Optional[bool] = None
    """Expect newly created tx."""
    is_sweep_response: Optional[bool] = None
    """Expect newly created tx from sweep action."""
    is_sweep_output_response: Optional[bool] = None
    """Expect newly created tx from specific output sweep."""
    # TODO monero-wallet-rpc: this only necessary because sweep_output does not return account index

    def __init__(self, ctx: Optional[TxContext] = None) -> None:
        """Initialize a new tx context.

        :param TxContext | None ctx: Transaction context to copy.
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

    def to_dict(self) -> dict[str, Any]:
        """Build the JSON object for this tx context (defined fields only).

        ``wallet`` is a live wallet handle rather than serializable data, so it
        is only reflected by the ``hasWallet`` flag and is not restored on
        :meth:`deserialize`.

        :returns dict[str, Any]: the context as a JSON-serializable dict.
        """
        root: dict[str, Any] = {}
        if self.wallet is not None:
            root["hasWallet"] = True
        if self.config is not None:
            root["config"] = json.loads(self.config.serialize())
        self._put(root, "hasOutgoingTransfer", self.has_outgoing_transfer)
        self._put(root, "hasIncomingTransfers", self.has_incoming_transfers)
        self._put(root, "hasDestinations", self.has_destinations)
        self._put(root, "isCopy", self.is_copy)
        self._put(root, "includeOutputs", self.include_outputs)
        self._put(root, "isSendResponse", self.is_send_response)
        self._put(root, "isSweepResponse", self.is_sweep_response)
        self._put(root, "isSweepOutputResponse", self.is_sweep_output_response)
        return root

    @staticmethod
    def from_dict(node: dict[str, Any], ctx: TxContext) -> None:
        """Populate ``ctx`` from a parsed JSON object.

        :param dict[str, Any] node: parsed JSON object.
        :param TxContext ctx: instance to populate.
        """
        for key, value in node.items():
            if key == "config":
                ctx.config = MoneroTxConfig.deserialize(json.dumps(value))
            elif key == "hasOutgoingTransfer":
                ctx.has_outgoing_transfer = value
            elif key == "hasIncomingTransfers":
                ctx.has_incoming_transfers = value
            elif key == "hasDestinations":
                ctx.has_destinations = value
            elif key == "isCopy":
                ctx.is_copy = value
            elif key == "includeOutputs":
                ctx.include_outputs = value
            elif key == "isSendResponse":
                ctx.is_send_response = value
            elif key == "isSweepResponse":
                ctx.is_sweep_response = value
            elif key == "isSweepOutputResponse":
                ctx.is_sweep_output_response = value
            # "hasWallet" is informational only; the live wallet handle cannot be restored
