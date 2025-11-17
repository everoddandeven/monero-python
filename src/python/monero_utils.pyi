from typing import Any
from .monero_output_wallet import MoneroOutputWallet
from .monero_block import MoneroBlock
from .monero_transfer import MoneroTransfer
from .monero_tx_wallet import MoneroTxWallet
from .monero_tx_config import MoneroTxConfig
from .monero_network_type import MoneroNetworkType
from .monero_integrated_address import MoneroIntegratedAddress


class MoneroUtils:
    """
    Collection of Monero utilities.
    """
    @staticmethod
    def atomic_units_to_xmr(amount_atomic_units: int) -> float:
        """
        Convert atomic units to XMR. 

        :param int amount_atomic_units: amount in atomic units to convert to XMR
        :return float: amount in XMR
        """
        ...
    @staticmethod
    def binary_to_dict(bin: bytes) -> dict[Any, Any]:
        """
        Deserialize a dictionary from binary format.

        :param bytes bin: Dictionary in binary format.
        :return dict: Deserialized dictionary.
        """
        ...
    @staticmethod
    def binary_to_json(bin: bytes) -> str:
        """
        Deserialize a JSON string from binary format.

        :param bytes bin: JSON string in binary format.
        :return str: The deserialized JSON string.
        """
        ...
    @staticmethod
    def configure_logging(path: str, console: bool) -> None:
        """
        Initialize logging.
        
        :param str path: the path to write logs to
        :param bool console: specifies whether or not to write to the console
        """
        ...
    @staticmethod
    def dict_to_binary(dictionary: dict[Any, Any]) -> bytes:
        """
        Converts a dictionary into binary format.

        :param dict dictionary: The dictionary to convert in binary format.
        :return bytes: Binary format.
        """
        ...
    @staticmethod
    def get_blocks_from_outputs(outputs: list[MoneroOutputWallet]) -> list[MoneroBlock]:
        """
        Get distinct blocks from outputs.

        :param list[MoneroOutputWallet] outputs: Outputs to get blocks from.
        :return list[MoneroBlock]: Distinct blocks obtained from outputs.
        """
        ...
    @staticmethod
    def get_blocks_from_transfers(transfers: list[MoneroTransfer]) -> list[MoneroBlock]:
        """
        Get distinct blocks from transfers.

        :param list[MoneroTransfer] transfers: Transfers to get blocks from.
        :return list[MoneroBlock]: Distinct blocks obtained from transfers.
        """
        ...
    @staticmethod
    def get_blocks_from_txs(txs: list[MoneroTxWallet]) -> list[MoneroBlock]:
        """
        Get distinct blocks from transactions.

        :param list[MoneroOutputWallet] outputs: Transactions to get blocks from.
        :return list[MoneroBlock]: Distinct blocks obtained from transactions.
        """
        ...
    @staticmethod
    def get_integrated_address(network_type: MoneroNetworkType, standard_address: str, payment_id: str = '') -> MoneroIntegratedAddress:
        """
        Get an integrated address.
        
        :param MoneroNetworkType network_type: is the network type of the integrated address
        :param str standard_address: is the address to derive the integrated address from
        :param str payment_id: optionally specifies the integrated address's payment id (defaults to random payment id)
        :return MoneroIntegratedAddress: the integrated address
        """
        ...
    @staticmethod
    def get_payment_uri(config: MoneroTxConfig) -> str:
        """
        Creates a payment URI from a tx configuration.
                
        :param config: specifies configuration for a payment URI
        :return: the payment URI
        """
        ...
    @staticmethod
    def get_ring_size() -> int:
        """
        Network-enforced ring size.
        """
        ...
    @staticmethod
    def get_version() -> str:
        """
        Get the version of the monero-python library.
        
        :return version: the version of this monero-python library
        """
        ...
    @staticmethod
    def is_valid_address(address: str, network_type: MoneroNetworkType) -> bool:
        """
        Determine if the given address is valid.
        
        :param str address: is the address to validate
        :param MoneroNetworkType network_type: is the address's network type
        :return bool: true if the address is valid, false otherwise
        """
        ...
    @staticmethod
    def is_valid_language(language: str) -> bool:
        """
        Indicates if the given language is valid.

        :param str language: is the language to validate
        :return: true if the language is valid, false otherwise
        """
        ...
    @staticmethod
    def is_valid_mnemonic(mnemonic: str) -> bool:
        """
        Indicates if a mnemonic is valid.
        
        :param str private_spend_key: is the mnemonic to validate
        :return: true if the mnemonic is valid, false otherwise
        """
        ...
    @staticmethod
    def is_valid_payment_id(payment_id: str) -> bool:
        """
        Indicates if a payment id is valid.
        
        :param str payment_id: is the payment id to validate
        :return: true if the payment id is valid, false otherwise
        """
        ...
    @staticmethod
    def is_valid_private_spend_key(private_spend_key: str) -> bool:
        """
        Indicates if a private spend key is valid.
        
        :param str private_spend_key: is the private spend key to validate
        :return: true if the private spend key is valid, false otherwise
        """
        ...
    @staticmethod
    def is_valid_private_view_key(private_view_key: str) -> bool:
        """
        Indicates if a private view key is valid.
        
        :param str private_view_key: is the private view key to validate
        :return: true if the private view key is valid, false otherwise
        """
        ...
    @staticmethod
    def is_valid_public_spend_key(public_spend_key: str) -> bool:
        """
        Indicates if a public spend key is valid.
        
        :param str public_spend_key: is the public spend key to validate
        :return bool: true if the public spend key is valid, false otherwise
        """
        ...
    @staticmethod
    def is_valid_public_view_key(public_view_key: str) -> bool:
        """
        Indicates if a public view key is valid.
        
        :param public_view_key: is the public view key to validate
        :return: true if the public view key is valid, false otherwise
        """
        ...
    @staticmethod
    def json_to_binary(json: str) -> bytes:
        """
        Convert a JSON string into binary format.

        :return bytes: Binary format.
        """
        ...
    @staticmethod
    def set_log_level(loglevel: int) -> None:
        """
        Set the library's log level with 0 being least verbose.

        :param level: the library's log level
        """
        ...
    @staticmethod
    def validate_address(address: str, network_type: MoneroNetworkType) -> None:
        """
        Validates the given address.
        
        :param address: is the address to validate
        :param network_type: is the address's network type
        """
        ...
    @staticmethod
    def validate_mnemonic(mnemonic: str) -> None:
        """
        Validates the given mnemonic phrase.
        
        :param str mnemonic: is the mnemonic to validate
        :raise MoneroError: if the given mnemonic is invalid
        """
        ...
    @staticmethod
    def validate_payment_id(payment_id: str) -> None:
        """
        Validate a payment id.
        
        :param str payment_id: is the payment id to validate
        :raise MoneroError: if the given payment id is invalid
        """
        ...
    @staticmethod
    def validate_private_spend_key(private_spend_key: str) -> None:
        """
        Validate a private spend key.
        
        :param str private_spend_key: is the private spend key to validate
        :raise MoneroError: if the given private spend key is invalid
        """
        ...
    @staticmethod
    def validate_private_view_key(private_view_key: str) -> None:
        """
        Validate a private view key.
        
        :param str private_view_key: is the private view key to validate
        :raise MoneroError: if the given private view key is invalid
        """
        ...
    @staticmethod
    def validate_public_spend_key(public_spend_key: str) -> None:
        """
        Validate a public spend key.
        
        :param str public_spend_key: is the public spend key to validate
        :raise MoneroError: if the given public spend key is invalid
        """
        ...
    @staticmethod
    def validate_public_view_key(public_view_key: str) -> None:
        """
        Validate a public view key.
        
        :param public_view_key: is the public view key to validate
        :raise MoneroError: if the given public view key is invalid
        """
        ...
    @staticmethod
    def xmr_to_atomic_units(amount_xmr: float) -> int:
        """
        Convert XMR to atomic units.
         
        :param float amount_xmr: amount in XMR to convert to atomic units
        :return int: amount in atomic units
        """
        ...
