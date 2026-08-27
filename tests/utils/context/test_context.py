from __future__ import annotations

from typing import Any, Optional

from .serializable_context import SerializableContext


class TestContext(SerializableContext):
    """Provides context or configuration for test methods to test a type."""

    __test__ = False

    has_json: Optional[bool] = None
    """Expect presence of json field."""
    is_pruned: Optional[bool] = None
    """Expect pruning."""
    is_full: Optional[bool] = None
    """Expect complete model."""
    is_confirmed: Optional[bool] = None
    """Expect confirmations."""
    is_miner_tx: Optional[bool] = None
    """Expect miner tx."""
    from_get_tx_pool: Optional[bool] = None
    """Expect from tx pool."""
    from_binary_block: Optional[bool] = None
    """Expect from binary block."""
    has_output_indices: Optional[bool] = None
    """Expect output indices."""
    do_not_test_copy: Optional[bool] = None
    """Diable copy tests."""
    has_txs: Optional[bool] = None
    """Expect txs."""
    has_hex: Optional[bool] = None
    """Expect hex field."""
    header_is_full: Optional[bool] = None
    """Expect full header."""
    tx_context: Optional[TestContext] = None
    """Tx context."""

    def __init__(self, ctx: Optional[TestContext] = None) -> None:
        """Initialize a new test context.

        :param TestContext | None ctx: test context to copy.
        """
        if ctx is not None:
            # copy reference
            self.has_json = ctx.has_json
            self.is_pruned = ctx.is_pruned
            self.is_full = ctx.is_full
            self.is_confirmed = ctx.is_confirmed
            self.is_miner_tx = ctx.is_miner_tx
            self.from_get_tx_pool = ctx.from_get_tx_pool
            self.from_binary_block = ctx.from_binary_block
            self.has_output_indices = ctx.has_output_indices
            self.do_not_test_copy = ctx.do_not_test_copy
            self.has_txs = ctx.has_txs
            self.header_is_full = ctx.header_is_full
            self.tx_context = ctx.tx_context

    def to_dict(self) -> dict[str, Any]:
        """Build the JSON object for this test context (defined fields only).

        :returns dict[str, Any]: the context as a JSON-serializable dict.
        """
        root: dict[str, Any] = {}
        self._put(root, "hasJson", self.has_json)
        self._put(root, "isPruned", self.is_pruned)
        self._put(root, "isFull", self.is_full)
        self._put(root, "isConfirmed", self.is_confirmed)
        self._put(root, "isMinerTx", self.is_miner_tx)
        self._put(root, "fromGetTxPool", self.from_get_tx_pool)
        self._put(root, "fromBinaryBlock", self.from_binary_block)
        self._put(root, "hasOutputIndices", self.has_output_indices)
        self._put(root, "doNotTestCopy", self.do_not_test_copy)
        self._put(root, "hasTxs", self.has_txs)
        self._put(root, "hasHex", self.has_hex)
        self._put(root, "headerIsFull", self.header_is_full)
        if self.tx_context is not None:
            root["txContext"] = self.tx_context.to_dict()
        return root

    @staticmethod
    def from_dict(node: dict[str, Any], ctx: TestContext) -> None:
        """Populate ``ctx`` from a parsed JSON object.

        :param dict[str, Any] node: parsed JSON object.
        :param TestContext ctx: instance to populate.
        """
        for key, value in node.items():
            if key == "hasJson":
                ctx.has_json = value
            elif key == "isPruned":
                ctx.is_pruned = value
            elif key == "isFull":
                ctx.is_full = value
            elif key == "isConfirmed":
                ctx.is_confirmed = value
            elif key == "isMinerTx":
                ctx.is_miner_tx = value
            elif key == "fromGetTxPool":
                ctx.from_get_tx_pool = value
            elif key == "fromBinaryBlock":
                ctx.from_binary_block = value
            elif key == "hasOutputIndices":
                ctx.has_output_indices = value
            elif key == "doNotTestCopy":
                ctx.do_not_test_copy = value
            elif key == "hasTxs":
                ctx.has_txs = value
            elif key == "hasHex":
                ctx.has_hex = value
            elif key == "headerIsFull":
                ctx.header_is_full = value
            elif key == "txContext":
                ctx.tx_context = TestContext()
                TestContext.from_dict(value, ctx.tx_context)
