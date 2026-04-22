from .serializable_struct import SerializableStruct


class MoneroRpcPaymentInfo(SerializableStruct):
    """Models a Monero RPC payment information."""

    credits: int | None
    """If payment for RPC is enabled, the number of credits available to the requesting client. Otherwise, 0."""

    top_block_hash: str | None
    """If payment for RPC is enabled, the hash of the highest block in the chain. Otherwise, `None`."""
