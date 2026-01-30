from __future__ import annotations
from typing import Optional


class TestContext:
    """Provides context or configuration for test methods to test a type."""

    __test__ = False

    has_json: Optional[bool] = None
    """Expect presence of json field"""
    is_pruned: Optional[bool] = None
    """Expect pruning"""
    is_full: Optional[bool] = None
    """Expect complete model"""
    is_confirmed: Optional[bool] = None
    """Expect confirmations"""
    is_miner_tx: Optional[bool] = None
    """Expect miner tx"""
    from_get_tx_pool: Optional[bool] = None
    """Expect from tx pool"""
    from_binary_block: Optional[bool] = None
    """Expect from binary block"""
    has_output_indices: Optional[bool] = None
    """Expect output indices"""
    do_not_test_copy: Optional[bool] = None
    """Diable copy tests"""
    has_txs: Optional[bool] = None
    """Expect txs"""
    has_hex: Optional[bool] = None
    """Expect hex field"""
    header_is_full: Optional[bool] = None
    """Expect full header"""
    tx_context: Optional[TestContext] = None
    """Tx context"""

    def __init__(self, ctx: Optional[TestContext] = None) -> None:
        if ctx is not None:
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
