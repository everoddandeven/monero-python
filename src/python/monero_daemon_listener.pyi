from .monero_block_header import MoneroBlockHeader


class MoneroDaemonListener:
    """
    Receives notifications as a daemon is updated.
    """
    last_header: MoneroBlockHeader | None
    """Last block header added to the chain."""
    def __init__(self) -> None:
        ...
    def on_block_header(self, header: MoneroBlockHeader) -> None:
        """
        Called when a new block is added to the chain.
        
        :param MoneroBlockHeader header: is the header of the block added to the chain
        """
        ...
