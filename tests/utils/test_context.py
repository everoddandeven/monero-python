from __future__ import annotations
from typing import Any

class TestContext:
  hasHex: bool = True
  hasTxs: bool = False
  headerIsFull: bool = True
  txContext: TestContext
  isPruned: bool = False
  isConfirmed: bool = False
  fromGetTxPool: bool = False
  hasOutputIndices: bool = False
  fromBinaryBlock: bool = False
  