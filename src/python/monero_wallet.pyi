import typing

from .monero_wallet_listener import MoneroWalletListener
from .monero_check_reserve import MoneroCheckReserve
from .monero_check_tx import MoneroCheckTx
from .monero_account import MoneroAccount
from .monero_account_tag import MoneroAccountTag
from .monero_address_book_entry import MoneroAddressBookEntry
from .monero_subaddress import MoneroSubaddress
from .monero_connection_manager import MoneroConnectionManager
from .monero_rpc_connection import MoneroRpcConnection
from .monero_tx_priority import MoneroTxPriority
from .monero_tx_config import MoneroTxConfig
from .monero_tx_wallet import MoneroTxWallet
from .monero_tx_query import MoneroTxQuery
from .monero_version import MoneroVersion
from .monero_integrated_address import MoneroIntegratedAddress
from .monero_key_image_import_result import MoneroKeyImageImportResult
from .monero_tx_set import MoneroTxSet
from .monero_multisig_init_result import MoneroMultisigInitResult
from .monero_key_image import MoneroKeyImage
from .monero_multisig_info import MoneroMultisigInfo
from .monero_network_type import MoneroNetworkType
from .monero_output_wallet import MoneroOutputWallet
from .monero_output_query import MoneroOutputQuery
from .monero_transfer import MoneroTransfer
from .monero_transfer_query import MoneroTransferQuery
from .monero_message_signature_type import MoneroMessageSignatureType
from .monero_multisig_sign_result import MoneroMultisigSignResult
from .monero_sync_result import MoneroSyncResult
from .monero_message_signature_result import MoneroMessageSignatureResult



class MoneroWallet:
    """
    Base wallet with default implementations.
    """
    
    DEFAULT_LANGUAGE: str
    """Default Monero wallet seed language."""

    def __init__(self) -> None:
        """Initialize a Monero wallet."""
        ...
    def add_address_book_entry(self, address: str, description: str) -> int:
        """
        Add an address book entry.

        :param str address: is the entry address
        :param str description: is the entry description (optional)
        :return int: the index of the added entry
        """
        ...
    def add_listener(self, listener: MoneroWalletListener) -> None:
        """
        Register a listener receive wallet notifications.

        :param MoneroWalletListener listener: is the listener to receive wallet notifications
        """
        ...
    def change_password(self, old_password: str, new_password: str) -> None:
        """
        Change the wallet password.

        :param str old_password: is the wallet's old password
        :param str new_password: is the wallet's new password
        """
        ...
    def check_reserve_proof(self, address: str, message: str, signature: str) -> MoneroCheckReserve:
        """
        Proves a wallet has a disposable reserve using a signature.

        :param str address: is the public wallet address
        :param str message: is a message included with the signature to further authenticate the proof (optional)
        :param str signature: is the reserve proof signature to check
        :return MoneroCheckReserve: the result of checking the signature proof
        """
        ...
    def check_spend_proof(self, tx_hash: str, message: str, signature: str) -> bool:
        """
        Prove a spend using a signature. Unlike proving a transaction, it does not require the destination public address.

        :param str tx_hash: specifies the transaction to prove
        :param str message: is a message included with the signature to further authenticate the proof (optional)
        :param str signature: is the transaction signature to confirm
        :return bool: true if the signature is good, false otherwise
        """
        ...
    def check_tx_key(self, tx_hash: str, tx_key: str, address: str) -> MoneroCheckTx:
        """
        Check a transaction in the blockchain with its secret key.

        :param str tx_hash: specifies the transaction to check
        :param str tx_key: is the transaction's secret key
        :param str address: is the destination public address of the transaction
        :return MoneroCheckTx: the result of the check
        """
        ...
    def check_tx_proof(self, tx_hash: str, address: str, message: str, signature: str) -> MoneroCheckTx:
        """
        Prove a transaction by checking its signature.

        :param str tx_hash: specifies the transaction to prove
        :param str address: is the destination public address of the transaction
        :param str message: is a message included with the signature to further authenticate the proof (optional)
        :param str signature: is the transaction signature to confirm
        :return MoneroCheckTx: the result of the check
        """
        ...
    def close(self, save: bool = False) -> None:
        """
        Optionally save then close the wallet.

        :param bool save: specifies if the wallet should be saved before being closed (default false)
        """
        ...
    def create_account(self, label: str = '') -> MoneroAccount:
        """
        Create a new account with a label for the first subaddress.

        :param str label: specifies the label for the account's first subaddress (optional)

        :return MoneroAccount: the created account
        """
        ...
    def create_subaddress(self, account_idx: int, label: str = '') -> MoneroSubaddress:
        """
        Create a subaddress within an account.

        :param int account_idx: specifies the index of the account to create the subaddress within
        :param str label: specifies the the label for the subaddress (defaults to empty std::string)
        :return MoneroSubaddress: the created subaddress
        """
        ...
    def create_tx(self, config: MoneroTxConfig) -> MoneroTxWallet:
        """
        Create a transaction to transfer funds from this wallet.

        :param MoneroTxConfig config: configures the transaction to create
        :return MoneroTxWallet: the created transaction (free memory using monero_utils::free)
        """
        ...
    def create_txs(self, config: MoneroTxConfig) -> list[MoneroTxWallet]:
        """
        Create one or more transactions to transfer funds from this wallet.

        :param MoneroTxConfig config: configures the transactions to create
        :return list[MoneroTxWallet]: the created transactions (free memory using monero_utils::free)
        """
        ...
    def decode_integrated_address(self, integrated_address: str) -> MoneroIntegratedAddress:
        """
        Decode an integrated address to get its standard address and payment id.

        :param str integrated_address: is an integrated address to decode
        
        :return MoneroIntegratedAddress: the decoded integrated address including standard address and payment id
        """
        ...
    def delete_address_book_entry(self, index: int) -> None:
        """
        Delete an address book entry.

        :param int index: is the index of the entry to delete
        """
        ...
    def describe_tx_set(self, tx_set: MoneroTxSet) -> MoneroTxSet:
        """
        Describes a tx set containing unsigned or multisig tx hex to a new tx set containing structured transactions.

        :param MoneroTxSet tx_set: is a tx set containing unsigned or multisig tx hex
        :return MoneroTxSet: the tx set containing structured transactions
        """
        ...
    def edit_address_book_entry(self, index: int, set_address: bool, address: str, set_description: bool, description: str) -> None:
        """
        Edit an address book entry.

        :param int index: is the index of the address book entry to edit
        :param bool set_address: specifies if the address should be updated
        :param str address: is the updated address
        :param bool set_description: specifies if the description should be updated
        :param str description: is the updated description
        """
        ...
    def exchange_multisig_keys(self, multisig_hexes: list[str], password: str) -> MoneroMultisigInitResult:
        """
        Exchange multisig hex with participants in a M/N multisig wallet.

        This process must be repeated with participants exactly N-M times.

        :param list[str] multisig_hexes: are multisig hex from each participant
        :param str password: is the wallet's password // TODO monero-project: redundant? wallet is created with password
        :return MoneroMultisigInitResult: the result which has the multisig's address xor this wallet's multisig hex to share with participants iff not done
        """
        
        ...
    def export_key_images(self, all: bool = False) -> list[MoneroKeyImage]:
        """
        Export signed key images.

        :param bool all: export all key images if true, else export key images since the last export
        :return list[MoneroKeyImage]: the wallet's signed key images
        """
        ...
    def export_multisig_hex(self) -> str:
        """
        Export this wallet's multisig info as hex for other participants.

        :return str: this wallet's multisig info as hex for other participants
        """
        ...
    def export_outputs(self, all: bool = False) -> str:
        """
        Export outputs in hex format.

        :param bool all: export all outputs if true, else export outputs since the last export
        :return str: outputs in hex format, empty string if no outputs
        """
        ...
    def freeze_output(self, key_image: str) -> None:
        """
        Freeze an output.

        :param str key_image: key image of the output to freeze
        """
        ...
    @typing.overload
    def get_account(self, account_idx: int) -> MoneroAccount:
        """
        Get an account without subaddress information.

        :param int account_idx: specifies the account to get
        :return MoneroAccount: the retrieved account
        """
        ...
    @typing.overload
    def get_account(self, account_idx: int, include_subaddresses: bool) -> MoneroAccount:
        """
        Get an account.

        :param int account_idx: specifies the account to get
        :param bool include_subaddresses: specifies if subaddresses should be included
        :return MoneroAccount: the retrieved account
        """
        ...
    def get_account_tags(self) -> list[MoneroAccountTag]:
        """
        Return all account tags.
        
        :return list[MoneroAccountTag]: the wallet's account tags
        """
        ...
    @typing.overload
    def get_accounts(self) -> list[MoneroAccount]:
        """
        Get all accounts.

        :return list[MoneroAccount]: all accounts within the wallet
        """
        ...
    @typing.overload
    def get_accounts(self, include_subaddresses: bool) -> list[MoneroAccount]:
        """
        Get all accounts.

        :param bool include_subaddresses: specifies if subaddresses should be included

        :return list[MoneroAccount]: all accounts within the wallet
        """
        ...
    @typing.overload
    def get_accounts(self, tag: str) -> list[MoneroAccount]:
        """
        Get all accounts.

        :param str tag: is the tag for filtering accounts, all accounts if null

        :return list[MoneroAccount]: all accounts for the wallet with the given tag
        """
        ...
    @typing.overload
    def get_accounts(self, include_subaddresses: bool, tag: str) -> list[MoneroAccount]:
        """
        Get all accounts.

        :param bool include_subaddresses: specifies if subaddresses should be included
        :param str tag: is the tag for filtering accounts, all accounts if null
        :return list[MoneroAccount]: all accounts for the wallet with the given tag
        """
        ...
    def get_address(self, account_idx: int, subaddress_idx: int) -> str:
        """
        Get the address of a specific subaddress.

        :param int account_idx: specifies the account index of the address's subaddress
        :param int subaddress_idx: specifies the subaddress index within the account
        :return str: the receive address of the specified subaddress
        """
        ...
    def get_address_book_entries(self, indices: list[int]) -> list[MoneroAddressBookEntry]:
        """
        Get all address book entries.

        :param list[int] indices: are indices of the entries to get
        :return list[MoneroAddressBookEntry]: the address book entries
        """
        ...
    def get_address_index(self, address: str) -> MoneroSubaddress:
        """
        Get the account and subaddress index of the given address.

        :param str address: is the address to get the account and subaddress index from
        :return MoneroSubaddress: the account and subaddress indices
        :raise MoneroError: exception if address is not a wallet address
        """
        ...
    def get_attribute(self, key: str) -> str:
        """
        Get an attribute.

        :param str key: is the attribute to get the value of
        :param str value: is set to the key's value if set
        :return bool: true if the key's value has been set, false otherwise
        """
        ...
    @typing.overload
    def get_balance(self) -> int:
        """
        Get the wallet's balance.
        
        :return int: the wallet's balance
        """
        ...
    @typing.overload
    def get_balance(self, account_idx: int) -> int:
        """
        Get an account's balance.

        :param int account_idx: is the index of the account to get the balance of
        :return int: the account's balance
        """
        ...
    @typing.overload
    def get_balance(self, account_idx: int, subaddress_idx: int) -> int:
        """
        Get a subaddress's balance.

        :param int account_idx: is the index of the subaddress's account to get the balance of
        :param int subaddress_idx: is the index of the subaddress to get the balance of
        :return int: the subaddress's balance
        """
        ...
    def get_connection_manager(self) -> MoneroConnectionManager | None:
        """
        Get the wallet's daemon connection manager.
        
        :return Optional[MoneroConnectionManager]: the wallet's daemon connection manager
        """
        ...
    def get_daemon_connection(self) -> MoneroRpcConnection | None:
        """
        Get the wallet's daemon connection.

        :return Optional[MoneroRpcConnection]: the wallet's daemon connection
        """
        ...
    def get_daemon_height(self) -> int:
        """
        Get the height that the wallet's daemon is synced to.

        :return int: the height that the wallet's daemon is synced to
        """
        ...
    def get_daemon_max_peer_height(self) -> int:
        """
        Get the maximum height of the peers the wallet's daemon is connected to.

        :return int: the maximum height of the peers the wallet's daemon is connected to
        """
        ...
    def get_default_fee_priority(self) -> MoneroTxPriority:
        """
        Get the current default fee priority (unimportant, normal, elevated, etc).

        :return MoneroTxPriority: the current fee priority
        """
        ...
    def get_height(self) -> int:
        """
        Get the height of the last block processed by the wallet (its index + 1).

        :return int: the height of the last block processed by the wallet
        """
        ...
    def get_height_by_date(self, year: int, month: int, day: int) -> int:
        """
        Get the blockchain's height by date as a conservative estimate for scanning.
         
        :param int year: year of the height to get
        :param int month: month of the height to get as a number between 1 and 12
        :param int day: day of the height to get as a number between 1 and 31

        :return int: the blockchain's approximate height at the given date
        """
        ...
    def get_integrated_address(self, standard_address: str = '', payment_id: str = '') -> MoneroIntegratedAddress:
        """
        Get an integrated address from a standard address and a payment id.

        :param str standard_address: is the integrated addresse's standard address (defaults to wallet's primary address)
        :param str payment_id: is the integrated addresse's payment id (defaults to randomly generating new payment id)
        
        :return MoneroIntegratedAddress: the integrated address
        """
        ...
    def get_listeners(self) -> list[MoneroWalletListener]:
        """
        Get the listeners registered with the wallet.

        :return list[MoneroWalletListener]: List of listener registered with the wallet
        """
        ...
    def get_multisig_info(self) -> MoneroMultisigInfo:
        """
        Get multisig info about this wallet.

        :return MoneroMultisigInfo: multisig info about this wallet
        """
        ...
    def get_network_type(self) -> MoneroNetworkType:
        """
        Get the wallet's network type (mainnet, testnet, or stagenet).

        :return MoneroNetworkType: the wallet's network type
        """
        ...
    def get_outputs(self, query: MoneroOutputQuery) -> list[MoneroOutputWallet]:
        """
        Get outputs created from previous transactions that belong to the wallet
        (i.e. that the wallet can spend one time).  Outputs are part of
        transactions which are stored in blocks on the blockchain.

        Results can be configured by passing a monero_output_query.  Outputs must
        meet every criteria defined in the query in order to be returned.  All
        filtering is optional and no filtering is applied when not defined.

        :param MoneroOutputQuery query: specifies query options (optional)
        :return list[MoneroOutputWallet]: wallet outputs per the query (free memory using monero_utils::free)
        """
        ...
    def get_path(self) -> str:
        """
        Get the path of this wallet's file on disk.

        :return str: the path of this wallet's file on disk
        """
        ...
    def get_payment_uri(self, config: MoneroTxConfig) -> str:
        """
        Creates a payment URI from a tx configuration.

        :param MoneroTxConfig config: specifies configuration for a potential tx
        :return str: is the payment uri
        """
        ...
    def get_primary_address(self) -> str:
        """
        Get the wallet's primary address.

        :return str: the wallet's primary address
        """
        ...
    def get_private_spend_key(self) -> str:
        """
        Get the wallet's private spend key.

        :return str: the wallet's private spend key
        """
        ...
    def get_private_view_key(self) -> str:
        """
        Get the wallet's private view key.

        :return str: the wallet's private view key
        """
        ...
    def get_public_spend_key(self) -> str:
        """
        Get the wallet's public spend key.

        :return str: the wallet's public spend key
        """
        ...
    def get_public_view_key(self) -> str:
        """
        Get the wallet's public view key.

        :return str: the wallet's public view key
        """
        ...
    def get_reserve_proof_account(self, account_idx: int, amount: int, message: str) -> str:
        """
        Generate a signature to prove an available amount in an account.

        :param int account_idx: specifies the account to prove ownership of the amount
        :param int amount: is the minimum amount to prove as available in the account
        :param str message: is a message to include with the signature to further authenticate the proof (optional)
        :return str: the reserve proof signature
        """
        ...
    def get_reserve_proof_wallet(self, message: str) -> str:
        """
        Generate a signature to prove the entire balance of the wallet.

        :param str message: is a message included with the signature to further authenticate the proof (optional)
        :return str: the reserve proof signature
        """
        ...
    def get_restore_height(self) -> int:
        """
        Get the height of the first block that the wallet scans.
        
        :return int: the height of the first block that the wallet scans
        """
        ...
    def get_seed(self) -> str:
        """
        Get the wallet's mnemonic phrase or seed.

        :return str: the wallet's mnemonic phrase or seed.
        """
        ...
    def get_seed_language(self) -> str:
        """
        Get the language of the wallet's mnemonic phrase or seed.

        :return str: the language of the wallet's mnemonic phrase or seed.
        """
        ...
    def get_spend_proof(self, tx_hash: str, message: str) -> str:
        """
        Generate a signature to prove a spend. Unlike proving a transaction, it does not require the destination public address.

        :param str tx_hash: specifies the transaction to prove
        :param str message: is a message to include with the signature to further authenticate the proof (optional)
        :return str: the transaction signature
        """
        ...
    def get_subaddress(self, account_idx: int, subaddress_idx: int) -> MoneroSubaddress:
        """
        Get a subaddress.

        :param int account_idx: specifies the index of the subaddress's account
        :param int subaddress_idx: specifies index of the subaddress within the account
        :return MoneroSubaddress: the retrieved subaddress
        """
        ...
    @typing.overload
    def get_subaddresses(self, account_idx: int) -> list[MoneroSubaddress]:
        """
        Get all subaddresses in an account.

        :param int account_idx: specifies the account to get subaddresses within
        :return list[MoneroSubaddress]: the retrieved subaddresses
        """
        ...
    @typing.overload
    def get_subaddresses(self, account_idx: int, subaddress_indices: list[int]) -> list[MoneroSubaddress]:
        """
        Get subaddresses in an account.

        :param int account_idx: specifies the account to get subaddresses within
        :param list[int] subaddress_indices: are specific subaddresses to get (optional)
        :return list[MoneroSubaddress]: the retrieved subaddresses
        """
        ...
    def get_transfers(self, query: MoneroTransferQuery) -> list[MoneroTransfer]:
        """
        Get incoming and outgoing transfers to and from this wallet.  An outgoing
        transfer represents a total amount sent from one or more subaddresses
        within an account to individual destination addresses, each with their
        own amount.  An incoming transfer represents a total amount received into
        a subaddress within an account.  Transfers belong to transactions which
        are stored on the blockchain.

        Query results can be filtered by passing in a monero_transfer_query.
        Transfers must meet every criteria defined in the query in order to be
        returned.  All filtering is optional and no filtering is applied when not
        defined.

        :param MoneroTransferQuery query: filters query results (optional)
        :return list[MoneroTransfer]: wallet transfers per the query (free memory using MoneroUtils.free())
        """
        ...
    def get_tx_key(self, tx_hash: str) -> str:
        """
        Get a transaction's secret key from its hash.

        :param str tx_hash: is the transaction's hash
        :return str: is the transaction's secret key
        """
        ...
    def get_tx_note(self, tx_hash: str) -> str:
        """
        Get a transaction note.

        :param str tx_hash: specifies the transaction to get the note of
        :return str: the tx note
        """
        ...
    def get_tx_notes(self, tx_hashes: list[str]) -> list[str]:
        """
        Get notes for multiple transactions.

        :param list[str] tx_hashes: identify the transactions to get notes for
        :returns list[str]: notes for the transactions
        """
        ...
    def get_tx_proof(self, tx_hash: str, address: str, message: str) -> str:
        """
        Get a transaction signature to prove it.

        :param str tx_hash: specifies the transaction to prove
        :param str address: is the destination public address of the transaction
        :param str message: is a message to include with the signature to further authenticate the proof (optional)
        :return str: the transaction signature
        """
        ...
    @typing.overload
    def get_txs(self) -> list[MoneroTxWallet]:
        """
        Get all wallet transactions.  Wallet transactions contain one or more
        transfers that are either incoming or outgoing to the wallet.

        :return list[MoneroTxWallet]: all wallet transactions (free memory using MoneroUtils.free())
        """
        ...
    @typing.overload
    def get_txs(self, query: MoneroTxQuery) -> list[MoneroTxWallet]:
        """
        Get wallet transactions.  Wallet transactions contain one or more
        transfers that are either incoming or outgoing to the wallet.

        Query results can be filtered by passing in a transaction query.
        Transactions must meet every criteria defined in the query in order to
        be returned.  All filtering is optional and no filtering is applied when
        not defined.

        :param MoneroTxQuery query: filters query results (optional)
        :return list[MoneroTxWallet]: wallet transactions per the query (free memory using monero_utils::free)
        """
        ...
    @typing.overload
    def get_unlocked_balance(self) -> int:
        """
        Get the wallet's unlocked balance.

        :return int: the wallet's unlocked balance
        """
        ...
    @typing.overload
    def get_unlocked_balance(self, account_idx: int) -> int:
        """
        Get an account's unlocked balance.

        :param int account_idx: is the index of the account to get the unlocked balance of
        :return int: the account's unlocked balance
        """
        ...
    @typing.overload
    def get_unlocked_balance(self, account_idx: int, subaddress_idx: int) -> int:
        """
        Get a subaddress's unlocked balance.

        :param int account_idx: is the index of the subaddress's account to get the unlocked balance of
        :param int subaddress_idx: is the index of the subaddress to get the unlocked balance of
        
        :return int: the subaddress's balance
        """
        ...
    def get_version(self) -> MoneroVersion:
        """
        Get the wallet's version.

        :return MoneroVersion: the wallet's version
        """
        ...
    def import_key_images(self, key_images: list[MoneroKeyImage]) -> MoneroKeyImageImportResult:
        """
        Import signed key images and verify their spent status.

        :param list[MoneroKeyImage] key_images: are key images to import and verify (requires hex and signature)
        :return MoneroKeyImageImportResult: results of the import
        """
        ...
    def import_multisig_hex(self, multisig_hexes: list[str]) -> int:
        """
        Import multisig info as hex from other participants.

        Note: If the daemon is not trusted, this method will not automatically
        update the spent status after importing peer multisig hex.

        :param multisig_hexes: are multisig hex from each participant
        :return int: the number of outputs signed with the given multisig hex
        """
        ...
    def import_outputs(self, outputs_hex: str) -> int:
        """
        Import outputs in hex format.

        :param outputs_hex: are outputs in hex format
        :return int: the number of outputs imported
        """
        ...
    def is_closed(self) -> bool:
        """
        Indicates if the wallet is closed.
        
        :return bool: true if the wallet is closed, false otherwise
        """
        ...
    def is_connected_to_daemon(self) -> bool:
        """
        Indicates if the wallet is connected a daemon.
        
        :return bool: true if the wallet is connected to daemon, false otherwise
        """
        ...
    def is_daemon_trusted(self) -> bool:
        """
        Indicates if the daemon is trusted or untrusted.

        :return bool: true if the daemon is trusted, false otherwise
        """
        ...
    def is_multisig(self) -> bool:
        """
        Indicates if this wallet is a multisig wallet.

        :return bool: true if this is a multisig wallet, false otherwise
        """
        ...
    def is_multisig_import_needed(self) -> bool:
        """
        Indicates if importing multisig data is needed for returning a correct balance.

        :return bool: true if importing multisig data is needed for returning a correct balance, false otherwise
        """
        ...
    def is_output_frozen(self, key_image: str) -> bool:
        """
        Check if an output is frozen.

        :param str key_image: key image of the output to check if frozen
        :return bool: true if the output is frozen, false otherwise
        """
        ...
    def is_synced(self) -> bool:
        """
        Indicates if the wallet is synced with the daemon.

        :return bool: true if the wallet is synced with the daemon, false otherwise
        """
        ...
    def is_view_only(self) -> bool:
        """
        Indicates if the wallet is view-only, meaning it does have the private
        spend key and can therefore only observe incoming outputs.
        
        :return bool: true if the wallet is view-only, false otherwise
        """
        ...
    def make_multisig(self, multisig_hexes: list[str], threshold: int, password: str) -> str:
        """
        Make this wallet multisig by importing multisig hex from participants.

        :param list[str] multisig_hexes: are multisig hex from each participant
        :param int threshold: is the number of signatures needed to sign transfers
        :param str password: is the wallet password
        :return str: this wallet's multisig hex to share with participants
        """
        ...
    def move_to(self, path: str, password: str) -> None:
        """
        Move the wallet from its current path to the given path.

        :param str path: is the new wallet's path
        :param str password: is the new wallet's password
        """
        ...
    def parse_payment_uri(self, uri: str) -> MoneroTxConfig:
        """
        Parses a payment URI to a tx configuration.

        :param uri: is the payment uri to parse
        :return MoneroTxConfig: the tx configuration parsed from the uri
        """
        ...
    def prepare_multisig(self) -> str:
        """
        Get multisig info as hex to share with participants to begin creating a
        multisig wallet.

        :return str: this wallet's multisig hex to share with participants
        """
        ...
    @typing.overload
    def relay_tx(self, tx_metadata: str) -> str:
        """
        Relay a transaction previously created without relaying.

        :param str tx_metadata: is transaction metadata previously created without relaying
        :return str: is the hash of the relayed tx
        """
        ...
    @typing.overload
    def relay_tx(self, tx: MoneroTxWallet) -> str:
        """
        Relay a previously created transaction.

        :param MoneroTxWallet tx: is the transaction to relay
        :return str: the hash of the relayed tx
        """
        ...
    @typing.overload
    def relay_txs(self, txs: list[MoneroTxWallet]) -> list[str]:
        """
        Relay previously created transactions.

        :param list[MoneroTxWallet] txs: are the transactions to relay
        :return list[str]: the hashes of the relayed txs
        """
        ...
    @typing.overload
    def relay_txs(self, tx_metadatas: list[str]) -> list[str]:
        """
        Relay transactions previously created without relaying.

        :param list[str] tx_metadatas: are transaction metadata previously created without relaying
        :return list[str]: the hashes of the relayed txs
        """
        ...
    def remove_listener(self, listener: MoneroWalletListener) -> None:
        """
        Unregister a listener to receive wallet notifications.

        :param MoneroWalletListener listener: is the listener to unregister
        """
        ...
    def rescan_blockchain(self) -> None:
        """
        Rescan the blockchain from scratch, losing any information which cannot be recovered from
        the blockchain itself.

        WARNING: This method discards local wallet data like destination addresses, tx secret keys,
        tx notes, etc.
        """
        ...
    def rescan_spent(self) -> None:
        """
        Rescan the blockchain for spent outputs.

        Note: this can only be called with a trusted daemon.

        Example use case: peer multisig hex is import when connected to an untrusted daemon,
        so the wallet will not rescan spent outputs.  Then the wallet connects to a trusted
        daemon.  This method should be manually invoked to rescan outputs.
        """
        ...
    def save(self) -> None:
        """
        Save the wallet at its current path.
        """
        ...
    def scan_txs(self, tx_hashes: list[str]) -> None:
        """
        Scan transactions by their hash/id.

        :param list[str] tx_hashes: tx hashes to scan.
        """
        ...
    def set_account_tag_label(self, tag: str, label: str) -> None:
        """
        Sets a human-readable description for a tag.

        :param str tag: is the tag to set a description for.
        :param str label: is the label to set for the tag.
        """
        ...
    def set_account_label(self, account_idx: int, label: str) -> None:
        """
        Set a human-readable description for an account.

        :param int account_idx: account index.
        :param str label: is the label to set.
        """
        ...
    def set_attribute(self, key: str, val: str) -> None:
        """
        Set an arbitrary attribute.

        :param str key: is the attribute key.
        :param str val: is the attribute value.
        """
        ...
    def set_connection_manager(self, connection_manager: MoneroConnectionManager | None) -> None:
        """
        Set the wallet's daemon connection manager.
        
        :param MoneroConnectionManager connection_manager: manages connections to monerod
        """
        ...
    @typing.overload
    def set_daemon_connection(self, connection: MoneroRpcConnection | None) -> None:
        """
        Set the wallet's daemon connection.

        :param MoneroRpcConnection connection: is the connection to set.
        """
        ...
    @typing.overload
    def set_daemon_connection(self, uri: str = '', username: str = '', password: str = '') -> None:
        """
        Set the wallet's daemon connection.

        :param str uri: is the connection to set.
        :param str username: is the username to authenticate with the daemon (optional).
        :param str password: is the password to authenticate with the daemon (optional).
        """
        ...
    def set_daemon_proxy(self, uri: str = '') -> None:
        """
        Set the Tor proxy to the daemon.
        
        :param str uri: is the proxy uri to set.
        """
        ...
    def set_restore_height(self, restore_height: int) -> None:
        """
        Set the height of the first block that the wallet scans.

        :param int restore_height: is the height of the first block that the wallet scans.
        """
        ...
    def set_subaddress_label(self, account_idx: int, subaddress_idx: int, label: str = '') -> None:
        """
        Set a subaddress label.
        
        :param int account_idx: index of the account to set the label for.
        :param int subaddress_idx: index of the subaddress to set the label for.
        :param str label: the label to set.
        """
        ...
    def set_tx_note(self, tx_hash: str, note: str) -> None:
        """
        Set a note for a specific transaction.

        :param str tx_hash: specifies the transaction.
        :param str note: specifies the note.
        """
        ...
    def set_tx_notes(self, tx_hashes: list[str], notes: list[str]) -> None:
        """
        Set notes for multiple transactions.

        :param list[str] tx_hashes: specify the transactions to set notes for.
        :param list[str] notes: are the notes to set for the transactions.
        """
        ...
    def sign_message(self, msg: str, signature_type: MoneroMessageSignatureType, account_idx: int = 0, subaddress_idx: int = 0) -> str:
        """
        Sign a message.

        :param str msg: the message to sign.
        :param MoneroMessageSignatureType signature_type: sign with spend key or spend key.
        :param int account_idx: the account index of the message signature (default `0`).
        :param int subaddress_idx: the subaddress index of the message signature (default `0`).
        :return str: the message signature
        """
        ...
    def sign_multisig_tx_hex(self, multisig_tx_hex: str) -> MoneroMultisigSignResult:
        """
        Sign previously created multisig transactions as represented by hex.

        :param str multisig_tx_hex: is the hex shared among the multisig transactions when they were created.
        :return MoneroMultisigSignResult: the result of signing the multisig transactions.
        """
        ...
    def sign_txs(self, unsigned_tx_hex: str) -> MoneroTxSet:
        """
        Sign unsigned transactions from a view-only wallet.

        :param str unsigned_tx_hex: is unsigned transaction hex from when the transactions were created.
        :return MoneroTxSet: the signed transaction set.
        """
        ...
    def start_syncing(self, sync_period_in_ms: int = 10000) -> None:
        """
        Start background synchronizing with a maximum period between syncs.

        :param int sync_period_in_ms: maximum period between syncs in milliseconds.
        """
        ...
    def start_mining(self, num_threads: int | None = None, background_mining: bool | None = None, ignore_battery: bool | None = None) -> None:
        """
        Start mining.

        :param Optional[int] num_threads: is the number of threads created for mining (optional).
        :param Optional[bool] background_mining: specifies if mining should occur in the background (optional).
        :param Optional[ignore_battery]: specifies if the battery should be ignored for mining (optional).
        """
        ...
    def stop_mining(self) -> None:
        """
        Stop mining.
        """
        ...
    def stop_syncing(self) -> None:
        """
        Stop the asynchronous thread to continuously synchronize the wallet with the daemon.
        """
        ...
    def submit_multisig_tx_hex(self, signed_multisig_tx_hex: str) -> list[str]:
        """
        Submit signed multisig transactions as represented by a hex std::string.

        :param str signed_multisig_tx_hex: is the signed multisig hex returned from signMultisigTxs()
        :return list[str]: the resulting transaction hashes
        """
        ...
    def submit_txs(self, signed_tx_hex: str) -> list[str]:
        """
        Submit signed transactions from a view-only wallet.

        :param str signed_tx_hex: is signed transaction hex from sign_txs()
        :return list[str]: the resulting transaction hashes
        """
        ...
    def sweep_dust(self, relay: bool = False) -> list[MoneroTxWallet]:
        """
        Sweep all unmixable dust outputs back to the wallet to make them easier to spend and mix.

        :param bool relay: specifies if the resulting transaction should be relayed (default false)
        :return list[MoneroTxWallet]: the created transactions (free memory using monero_utils::free)
        """
        ...
    def sweep_output(self, config: MoneroTxConfig) -> MoneroTxWallet:
        """
        Sweep an output with a given key image.

        :param MoneroTxConfig config: configures the sweep transaction
        :return MoneroTxWallet: the created transaction (free memory using monero_utils::free)
        """
        ...
    def sweep_unlocked(self, config: MoneroTxConfig) -> list[MoneroTxWallet]:
        """
        Sweep unlocked funds according to the given config.

        :param MoneroTxConfig config: is the sweep configuration
        :return list[MoneroTxWallet]: the created transactions (free memory using monero_utils::free)
        """
        ...
    @typing.overload
    def sync(self) -> MoneroSyncResult:
        """
        Synchronize the wallet with the daemon as a one-time synchronous process.

        :return: the sync result
        """
        ...
    @typing.overload
    def sync(self, listener: MoneroWalletListener) -> MoneroSyncResult:
        """
        Synchronize the wallet with the daemon as a one-time synchronous process.

        :param MoneroWalletListener listener: listener to receive notifications during synchronization
        
        :return MoneroSyncResult: the sync result
        """
        ...
    @typing.overload
    def sync(self, start_height: int) -> MoneroSyncResult:
        """
        Synchronize the wallet with the daemon as a one-time synchronous process.

        :param int start_height: is the start height to sync from (ignored if less than last processed block)
        
        :return MoneroSyncResult: the sync result
        """
        ...
    @typing.overload
    def sync(self, start_height: int, listener: MoneroWalletListener) -> MoneroSyncResult:
        """
        Synchronizes the wallet with the blockchain.

        :param int start_height: start height to sync from (ignored if less than last processed block)
        :param MoneroWalletListener listener: listener to receive notifications during synchronization

        :return MoneroSyncResult: the sync result
        """
        ...
    def tag_accounts(self, tag: str, account_indices: list[int]) -> None:
        """
        Tag accounts.
        
        :param str tag: is the tag to apply to the specified accounts.
        :param list[int] account_indice: are the indices of the accounts to tag.
        """
        ...
    def thaw_output(self, key_image: str) -> None:
        """
        Thaw a frozen output.

        :param key_image: key image of the output to thaw
        """
        ...
    def untag_accounts(self, account_indices: list[int]) -> None:
        """
        Untag acconts.
        
        :param list[int] account_indices: are the indices of the accounts to untag.
        """
        ...
    def verify_message(self, msg: str, address: str, signature: str) -> MoneroMessageSignatureResult:
        """
        Verify a message signature.

        :param str msg: the signed message.
        :param str address: signing address.
        :param str signature: signature.
        :return MoneroMessageSignatureResult: the message signature result.
        """
        ...
    def wait_for_next_block(self) -> int:
        """
        Wait for the next block to be added to the chain.

        :return int: the height of the next block when it is added to the chain.
        """
        ...
