import logging

from monero import (
    MoneroWallet, MoneroWalletKeys, MoneroTxWallet,
    MoneroWalletConfig, MoneroNetworkType,
    MoneroUtils
)

from .wallet_test_utils import WalletTestUtils

logger: logging.Logger = logging.getLogger("TxSpammer")


class TxSpammer:
    """Utility used to spam txs on blockchain."""

    _network_type: MoneroNetworkType = MoneroNetworkType.MAINNET
    """Network type."""

    def __init__(self, network_type: MoneroNetworkType) -> None:
        """Initialize a new transaction spammer.

        :param MoneroNetworkType network_type: Network type.
        """
        self._network_type = network_type

    def create_spam_wallets(self, n: int = 10) -> list[MoneroWallet]:
        """Create random wallet used as spam destinations.

        :param MoneroNetworkType network_type: Network type.
        :param int n: number of wallets to create.
        :returns list[MoneroWalletKeys]: random wallets created.
        """
        assert n >= 0, "n must be >= 0"
        wallets: list[MoneroWallet] = []
        # setup basic wallet config
        config = MoneroWalletConfig()
        config.network_type = self._network_type
        # create n random wallets
        for i in range(n):
            wallet: MoneroWalletKeys = MoneroWalletKeys.create_wallet_random(config)
            wallets.append(wallet)
            logger.debug(f"Created random wallet ({i + 1}): {wallet.get_primary_address()}")

        return wallets

    def spam(self) -> list[MoneroTxWallet]:
        """Spam txs on blockchain.

        :returns list[MoneroTxWallet]: txs spammed on blockchain.
        """
        # get random wallets to use
        wallets: list[MoneroWallet] = self.create_spam_wallets()
        logger.info("Spamming txs on blockchain...")
        txs: list[MoneroTxWallet] = WalletTestUtils.fund_wallets(wallets, 1, 1, 0)

        for i, tx in enumerate(txs):
            # log tx
            assert tx.hash is not None
            assert tx.outgoing_transfer is not None
            assert len(tx.outgoing_transfer.destinations) == 1
            address: str | None = tx.outgoing_transfer.destinations[0].address
            amount: int | None = tx.outgoing_transfer.destinations[0].amount
            assert address is not None
            assert amount is not None
            logger.info(f"[{i + 1}] Spammed {MoneroUtils.atomic_units_to_xmr(amount)} XMR with tx {tx.hash} to address {address}")

        assert len(txs) > 0, "No transactions spammed on blockchain!"

        return txs
