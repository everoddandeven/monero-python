from .monero_rpc_payment_info import MoneroRpcPaymentInfo
from .monero_auxiliary_pow import MoneroAuxiliaryPow


class MoneroAddAuxiliaryPowResult(MoneroRpcPaymentInfo):
    """Models the result of adding auxiliary proof-of-work to a block template for merge mining."""

    block_template_blob: str | None
    """The updated block template blob."""
    block_hashing_blob: str | None
    """The updated block hashing blob."""
    merkle_root: str | None
    """The Merkle root committing to the auxiliary blocks."""
    merkle_tree_depth: int | None
    """The depth of the auxiliary Merkle tree."""
    aux_pow: list[MoneroAuxiliaryPow]
    """The (possibly reordered) auxiliary proof-of-work entries."""

    @staticmethod
    def deserialize(json: str) -> MoneroAddAuxiliaryPowResult:
        """
        Deserialize a MoneroAddAuxiliaryPowResult from a JSON string.

        :param str json: MoneroAddAuxiliaryPowResult in JSON format.
        :returns MoneroAddAuxiliaryPowResult: deserialized instance.
        """
        ...

    def __init__(self) -> None:
        """Initialize a Monero add auxiliary proof-of-work result."""
        ...
