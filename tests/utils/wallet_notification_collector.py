import logging

from typing import override

from monero import (
    MoneroWalletListener, MoneroOutputWallet,
    MoneroOutputQuery
)

logger: logging.Logger = logging.getLogger("WalletNotificationCollector")


class WalletNotificationCollector(MoneroWalletListener):
    """Collects blocks, outputs and balances changes from wallet"""

    listening: bool
    """Indicates if listener is expected to be active"""
    block_notifications: list[int]
    """Collection of blocks"""
    balance_notifications: list[tuple[int, int]]
    """Collection of balance notifications"""
    outputs_received: list[MoneroOutputWallet]
    """Collection of outputs received by the wallet"""
    outputs_spent: list[MoneroOutputWallet]
    """Collection of outputs spend by the wallet"""

    def __init__(self) -> None:
        """
        Initialize a new wallet notification collector.
        """
        super().__init__()
        self.listening = True
        self.block_notifications = []
        self.balance_notifications = []
        self.outputs_received = []
        self.outputs_spent = []

    @override
    def on_new_block(self, height: int) -> None:
        assert self.listening
        num_block_notifications: int = len(self.block_notifications)

        if num_block_notifications > 0:
            # check block notifications order
            expected_height: int = self.block_notifications[num_block_notifications - 1] + 1
            assert height == expected_height, f"Expected height {expected_height}, got {height}"

        # collect height
        self.block_notifications.append(height)
        logger.debug(f"Collected height: {height}")

    @override
    def on_balances_changed(self, new_balance: int, new_unclocked_balance: int) -> None:
        assert self.listening
        num_balance_notifications: int = len(self.balance_notifications)

        if num_balance_notifications > 0:
            last_notification: tuple[int, int] = self.balance_notifications[num_balance_notifications - 1]
            # test that balances change
            assert new_balance != last_notification[0] or new_balance != last_notification[1]

        # collect balance notification
        self.balance_notifications.append((new_balance, new_unclocked_balance))
        logger.debug(f"Collected balance: {new_balance}, unlocked balance: {new_unclocked_balance}")

    @override
    def on_output_received(self, output: MoneroOutputWallet) -> None:
        assert self.listening
        # collect received output
        self.outputs_received.append(output)
        logger.debug(f"Received output: {output.serialize()}")

    @override
    def on_output_spent(self, output: MoneroOutputWallet) -> None:
        assert self.listening
        # collect spent output
        self.outputs_spent.append(output)
        logger.debug(f"Spent output: {output.serialize()}")

    def get_outputs_received(self, query: MoneroOutputQuery) -> list[MoneroOutputWallet]:
        """
        Get outputs received by query.

        :param MoneroOutputQuery query: filter outputs received
        :returns list[MoneroOutputWallet]: outputs received by the wallet filtered by query
        """
        result: list[MoneroOutputWallet] = []
        # filter received outputs
        for output in self.outputs_received:
            if query.meets_criteria(output):
                result.append(output)
        return result

    def get_outputs_spent(self, query: MoneroOutputQuery) -> list[MoneroOutputWallet]:
        """
        Get outputs spent by query.

        :param MoneroOutputQuery query: filter outputs spent
        :returns list[MoneroOutputWallet]: outputs spent by the wallet filtered by query
        """
        result: list[MoneroOutputWallet] = []
        # filter spent outputs
        for output in self.outputs_spent:
            if query.meets_criteria(output):
                result.append(output)
        return result
