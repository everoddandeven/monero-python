import typing

from .monero_connection_manager import MoneroConnectionManager
from .monero_network_type import MoneroNetworkType
from .monero_rpc_connection import MoneroRpcConnection


class MoneroWalletConfig:
    """
    Configures a wallet to create.
    """
    account_lookahead: int | None
    connection_manager: MoneroConnectionManager | None
    is_multisig: bool | None
    language: str | None
    network_type: MoneroNetworkType | None
    password: str | None
    path: str | None
    primary_address: str | None
    private_spend_key: str | None
    private_view_key: str | None
    restore_height: int | None
    save_current: bool | None
    seed: str | None
    seed_offset: str | None
    server: MoneroRpcConnection | None
    subaddress_lookahead: int | None
    @staticmethod
    def deserialize(config_json: str) -> MoneroWalletConfig:
        ...
    @typing.overload
    def __init__(self) -> None:
        ...
    @typing.overload
    def __init__(self, config: MoneroWalletConfig) -> None:
        ...
    def copy(self) -> MoneroWalletConfig:
        ...
