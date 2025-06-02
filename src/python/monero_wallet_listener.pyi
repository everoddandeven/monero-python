from .monero_output_wallet import MoneroOutputWallet


class MoneroWalletListener:
    """
    Interface to receive wallet notifications.
    """
    def __init__(self) -> None:
        """Initialize a wallet listener."""
        ...

    def on_balances_changed(self, new_balance: int, new_unclocked_balance: int) -> None:
        """
        Invoked when the wallet's balances change.

        :param int new_balance: new balance
        :param int new_unlocked_balance: new unlocked balance
        """
        ...
    def on_new_block(self, height: int) -> None:
        """
        Invoked when a new block is processed.

        :param int height: the newly processed block
        """
        ...
    def on_output_received(self, output: MoneroOutputWallet) -> None:
        """
        Invoked when the wallet receives an output.

        :param MoneroOutputWallet output: the received output
        """
        ...
    def on_output_spent(self, output: MoneroOutputWallet) -> None:
        """
        Invoked when the wallet spends an output.

        :param MoneroOutputWallet output: the spent output
        """
        ...
    def on_sync_progress(self, height: int, start_height: int, end_height: int, percent_done: float, message: str) -> None:
        """
        Invoked when sync progress is made.

        :param int height: height of the synced block
        :param int start_height: starting height of the sync request
        :param int end_height: ending height of the sync request
        :param float percent_done: sync progress as a percentage
        :param str message: human-readable description of the current progress
        """
        ...
