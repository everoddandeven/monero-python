from .test_context import TestContext


class BinaryBlockContext(TestContext):
    """Binary block test context"""

    def __init__(self) -> None:
        """
        Initialize a new binary block test context
        """
        super().__init__()
        # set binary block test context constants
        self.has_hex = False
        self.header_is_full = False
        self.has_txs = True
        self.tx_context = TestContext()
        self.tx_context.is_pruned = False
        self.tx_context.is_confirmed = True
        self.tx_context.from_get_tx_pool = False
        self.tx_context.has_output_indices = False
        self.tx_context.from_binary_block = True
