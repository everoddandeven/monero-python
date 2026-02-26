import logging

from typing import Optional
from monero import MoneroWalletKeys, MoneroTxWallet, MoneroNetworkType

from .wallet_utils import WalletUtils
from .mining_utils import MiningUtils

logger: logging.Logger = logging.getLogger("TxSpammer")


class TxSpammer:
    """Utility used to spam txs on blockchain"""

    _wallets: Optional[list[MoneroWalletKeys]] = None
    _network_type: MoneroNetworkType = MoneroNetworkType.MAINNET

    def __init__(self, network_type: MoneroNetworkType) -> None:
        self._network_type = network_type

    def get_wallets(self) -> list[MoneroWalletKeys]:
        if self._wallets is None:
            self._wallets = WalletUtils.create_random_wallets(self._network_type)
        return self._wallets.copy()

    def spam(self) -> list[MoneroTxWallet]:
        """Spam txs on blockchain"""
        # create random wallets to use
        wallets = self.get_wallets()
        txs: list[MoneroTxWallet] = []
        logger.info("Spamming txs on blockchain...")
        for i, wallet in enumerate(wallets):
            # fund random wallet
            spam_txs = MiningUtils.fund_wallet(wallet, 1, 1, 0)
            wallet_addr = wallet.get_primary_address()
            assert spam_txs is not None and len(spam_txs) > 0, f"Could not spam tx for random wallet ({i}): {wallet_addr}"
            for tx in txs:
                logger.debug(f"Spammed tx {tx.hash} for random wallet ({i}): {wallet_addr}")
                # save tx
                txs.append(tx)
        logger.info(f"Spammed {len(txs)} txs on blockchain")
        return txs
