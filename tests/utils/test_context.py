from __future__ import annotations
from typing import Optional


class TestContext:
    has_hex: bool = True
    has_txs: bool = False
    header_is_full: bool = True
    tx_context: Optional[TestContext] = None
    is_pruned: bool = False
    is_confirmed: bool = False
    from_get_tx_pool: bool = False
    has_output_indices: bool = False
    from_binary_block: bool = False
