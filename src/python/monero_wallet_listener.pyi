from .monero_output_wallet import MoneroOutputWallet


class MoneroWalletListener:
    """
    Interface to receive wallet notifications.
    """
    def on_balances_changed(self, new_balance: int, new_unclocked_balance: int) -> None:
        """
        Invoked when the wallet's balances change.

        :param new_balance: new balance
        :param new_unlocked_balance: new unlocked balance
        """
        ...
    def on_new_block(self, height: int) -> None:
        """
        Invoked when a new block is processed.

        :param block: the newly processed block
        """
        ...
    def on_output_received(self, output: MoneroOutputWallet) -> None:
        """
        Invoked when the wallet receives an output.

        :param output: the received output
        """
        ...
    def on_output_spent(self, output: MoneroOutputWallet) -> None:
        """
        Invoked when the wallet spends an output.

        :param output: the spent output
        """
        ...
    def on_sync_progress(self, height: int, start_height: int, end_height: int, percent_done: float, message: str) -> None:
        """
        Invoked when sync progress is made.

        :param height: height of the synced block
        :param start_height: starting height of the sync request
        :param end_height: ending height of the sync request
        :param percent_done: sync progress as a percentage
        :param message: human-readable description of the current progress
        """
        ...
