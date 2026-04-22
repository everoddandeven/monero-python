
from abc import ABC
from typing import Optional

from monero import MoneroWallet, MoneroTxConfig, MoneroDaemon

from .single_tx_sender import SingleTxSender
from .from_multiple_tx_sender import FromMultipleTxSender
from .to_multiple_tx_sender import ToMultipleTxSender
from .wallet_sweeper import WalletSweeper
from .send_and_update_txs_tester import SendAndUpdateTxsTester
from .sync_with_pool_submit_tester import SyncWithPoolSubmitTester


class WalletSendUtils(ABC):

    # Convenience method for single tx send tests
    @classmethod
    def test_send_to_single(cls, wallet: MoneroWallet, can_split: bool, relay: Optional[bool] = None, payment_id: Optional[str] = None) -> None:
        """Test creating transaction and sending to single destination.

        :param MoneroWallet wallet: wallet to send funds from.
        :param bool can_split: Can split transactions.
        :param bool | None relay: Relay created transaction(s).
        :param str | None payment_id: Transaction payment id.
        """
        config = MoneroTxConfig()
        config.can_split = can_split
        config.relay = relay
        config.payment_id = payment_id
        sender = SingleTxSender(wallet, config)
        sender.send()

    # Convenience method for sending funds from multiple sources
    @classmethod
    def test_send_from_multiple(cls, wallet: MoneroWallet, can_split: bool | None) -> None:
        """Test send multiple txs from wallet.

        :param MoneroWallet wallet: test wallet to send txs from.
        :param bool can_split: can split wallet txs.
        """
        sender: FromMultipleTxSender = FromMultipleTxSender(wallet, can_split)
        sender.send()

    # Convenience method for multiple tx send tests
    @classmethod
    def test_send_to_multiple(
        cls,
        wallet: MoneroWallet,
        num_accounts: int,
        num_subaddresses_per_account: int,
        can_split: bool,
        send_amount_per_subaddress: Optional[int] = None,
        subtract_fee_from_destinations: bool = False
    ) -> None:
        sender: ToMultipleTxSender = ToMultipleTxSender(
            wallet, num_accounts, num_subaddresses_per_account,
            can_split, send_amount_per_subaddress, subtract_fee_from_destinations)
        sender.send()

    @classmethod
    def test_sweep_wallet(cls, wallet: MoneroWallet, sweep_each_subaddress: Optional[bool]) -> None:
        """Test creating sweep wallet transaction.

        :param MoneroWallet wallet: test wallet to sweep.
        :param bool | None sweep_each_subaddress: sweep each wallet subaddresses.
        """
        sweeper: WalletSweeper = WalletSweeper(wallet, sweep_each_subaddress)
        sweeper.sweep()

    @classmethod
    def test_send_and_update_txs(cls, daemon: MoneroDaemon, wallet: MoneroWallet, config: MoneroTxConfig) -> None:
        tester: SendAndUpdateTxsTester = SendAndUpdateTxsTester(daemon, wallet, config)
        tester.test()

    @classmethod
    def test_sync_with_pool_submit(cls, daemon: MoneroDaemon, wallet: MoneroWallet, config: MoneroTxConfig) -> None:
        tester: SyncWithPoolSubmitTester = SyncWithPoolSubmitTester(daemon, wallet, config)
        tester.test()
