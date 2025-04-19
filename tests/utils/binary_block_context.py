from .test_context import TestContext


class BinaryBlockContext(TestContext):

  def __init__(self) -> None:
    super().__init__()
    self.hasHex = False
    self.headerIsFull = False
    self.hasTxs = True
    self.txContext = TestContext()
    self.txContext.isPruned = False
    self.txContext.isConfirmed = True
    self.txContext.fromGetTxPool = False
    self.txContext.hasOutputIndices = False
    self.txContext.fromBinaryBlock = True
