from .monero_wallet import MoneroWallet
from .monero_wallet_config import MoneroWalletConfig


class MoneroWalletKeys(MoneroWallet):
    """
    Implements a Monero wallet to provide basic key management.
    """
    @staticmethod
    def create_wallet_from_keys(config: MoneroWalletConfig) -> MoneroWalletKeys:
        """
        Create a wallet from an address, view key, and spend key.
    
        :param MoneroWalletConfig config: is the wallet configuration (network type, address, view key, spend key, language).
        :return MoneroWalletKeys: a pointer to the wallet instance.
        """
        ...
    @staticmethod
    def create_wallet_from_seed(config: MoneroWalletConfig) -> MoneroWalletKeys:
        """
        Create a wallet from an existing mnemonic phrase or seed.

        :param MoneroWalletConfig config: is the wallet configuration (network type, seed, seed offset, isMultisig).
        :return MoneroWalletKeys: a pointer to the wallet instance.
        """
        ...
    @staticmethod
    def create_wallet_random(config: MoneroWalletConfig) -> MoneroWalletKeys:
        """
        Create a new wallet with a randomly generated seed.

        :param MoneroWalletConfig config: is the wallet configuration (network type and language).
        :return MoneroWalletKeys: a pointer to the wallet instance.
        """
        ...
    @staticmethod
    def get_seed_languages() -> list[str]:
        """
        Get a list of available languages for the wallet's seed.

        :return list[str]: The available languages for the wallet's seed.
        """
        ...
