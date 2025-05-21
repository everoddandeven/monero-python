import typing

from .monero_connection_manager import MoneroConnectionManager
from .monero_network_type import MoneroNetworkType
from .monero_rpc_connection import MoneroRpcConnection


class MoneroWalletConfig:
    """
    Configures a wallet to create.
    """
    account_lookahead: int | None
    """Account index look ahead."""
    connection_manager: MoneroConnectionManager | None
    """The wallet connection manager."""
    is_multisig: bool | None
    """Indicates if the wallet is a multisignature wallet."""
    language: str | None
    """The wallet language."""
    network_type: MoneroNetworkType | None
    """The wallet network type."""
    password: str | None
    """The wallet password."""
    path: str | None
    """The wallet path on file system."""
    primary_address: str | None
    """The wallet standard address."""
    private_spend_key: str | None
    """The wallet private spend key."""
    private_view_key: str | None
    """The wallet private view key."""
    restore_height: int | None
    """The wallet restore height."""
    save_current: bool | None
    """Save the wallet."""
    seed: str | None
    """The wallet mnemonic."""
    seed_offset: str | None
    """The wallet custom seed offset."""
    server: MoneroRpcConnection | None
    """The wallet RPC connection."""
    subaddress_lookahead: int | None
    """Subaddress index look ahead."""
    @staticmethod
    def deserialize(config_json: str) -> MoneroWalletConfig:
        """
        Deserialize a Monero wallet config from a JSON string.

        :param str config_json: JSON string.
        :return MoneroWalletConfig: The deserialized wallet config.
        """
        ...
    @typing.overload
    def __init__(self) -> None:
        """
        Initialize an empty Monero wallet config.
        """
        ...
    @typing.overload
    def __init__(self, config: MoneroWalletConfig) -> None:
        """
        Initialize a Monero wallet config.

        :param MoneroWalletConfig config: Config to copy.
        """
        ...
    def copy(self) -> MoneroWalletConfig:
        """
        Copy this wallet config.

        :return MoneroWalletConfig: Copy of the wallet config.
        """
        ...
