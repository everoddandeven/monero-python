"""
"""
from __future__ import annotations
import typing
__all__ = ['MoneroAccount', 'MoneroAccountTag', 'MoneroAddressBookEntry', 'MoneroAddressType', 'MoneroAltChain', 'MoneroBan', 'MoneroBlock', 'MoneroBlockHeader', 'MoneroBlockTemplate', 'MoneroCheck', 'MoneroCheckReserve', 'MoneroCheckTx', 'MoneroConnectionSpan', 'MoneroConnectionType', 'MoneroDaemon', 'MoneroDaemonInfo', 'MoneroDaemonListener', 'MoneroDaemonRpc', 'MoneroDaemonSyncInfo', 'MoneroDaemonUpdateCheckResult', 'MoneroDaemonUpdateDownloadResult', 'MoneroDecodedAddress', 'MoneroDestination', 'MoneroEmptyRequest', 'MoneroError', 'MoneroFeeEstimate', 'MoneroHardForkInfo', 'MoneroIncomingTransfer', 'MoneroIntegratedAddress', 'MoneroJsonRequest', 'MoneroJsonResponse', 'MoneroKeyImage', 'MoneroKeyImageImportResult', 'MoneroKeyImageSpentStatus', 'MoneroMessageSignatureResult', 'MoneroMessageSignatureType', 'MoneroMinerTxSum', 'MoneroMiningStatus', 'MoneroMultisigInfo', 'MoneroMultisigInitResult', 'MoneroMultisigSignResult', 'MoneroNetworkType', 'MoneroOutgoingTransfer', 'MoneroOutput', 'MoneroOutputDistributionEntry', 'MoneroOutputHistogramEntry', 'MoneroOutputQuery', 'MoneroOutputWallet', 'MoneroPeer', 'MoneroPruneResult', 'MoneroRpcConnection', 'MoneroSubaddress', 'MoneroSubmitTxResult', 'MoneroSyncResult', 'MoneroTransfer', 'MoneroTransferQuery', 'MoneroTx', 'MoneroTxBacklogEntry', 'MoneroTxConfig', 'MoneroTxPoolStats', 'MoneroTxPriority', 'MoneroTxQuery', 'MoneroTxSet', 'MoneroTxWallet', 'MoneroUtils', 'MoneroVersion', 'MoneroWallet', 'MoneroWalletConfig', 'MoneroWalletFull', 'MoneroWalletKeys', 'MoneroWalletListener', 'MoneroWalletRpc', 'SerializableStruct']
class MoneroAccount(SerializableStruct):
    balance: int
    index: int
    primary_address: str
    subaddresses: list[MoneroSubaddress]
    tag: str
    unlocked_balance: int
    def __init__(self) -> None:
        ...
class MoneroAccountTag:
    account_indices: list[int]
    label: str
    tag: str
    @typing.overload
    def __init__(self, tag: str, label: str) -> None:
        ...
    @typing.overload
    def __init__(self, tag: str, label: str, account_indices: list[int]) -> None:
        ...
class MoneroAddressBookEntry:
    address: str
    description: str
    index: int
    payment_id: str
    def __init__(self) -> None:
        ...
class MoneroAddressType:
    """
    Members:
    
      PRIMARY_ADDRESS
    
      INTEGRATED_ADDRESS
    
      SUBADDRESS
    """
    INTEGRATED_ADDRESS: typing.ClassVar[MoneroAddressType]  # value = <MoneroAddressType.INTEGRATED_ADDRESS: 1>
    PRIMARY_ADDRESS: typing.ClassVar[MoneroAddressType]  # value = <MoneroAddressType.PRIMARY_ADDRESS: 0>
    SUBADDRESS: typing.ClassVar[MoneroAddressType]  # value = <MoneroAddressType.SUBADDRESS: 2>
    __members__: typing.ClassVar[dict[str, MoneroAddressType]]  # value = {'PRIMARY_ADDRESS': <MoneroAddressType.PRIMARY_ADDRESS: 0>, 'INTEGRATED_ADDRESS': <MoneroAddressType.INTEGRATED_ADDRESS: 1>, 'SUBADDRESS': <MoneroAddressType.SUBADDRESS: 2>}
    def __eq__(self, other: typing.Any) -> bool:
        ...
    def __getstate__(self) -> int:
        ...
    def __hash__(self) -> int:
        ...
    def __index__(self) -> int:
        ...
    def __init__(self, value: int) -> None:
        ...
    def __int__(self) -> int:
        ...
    def __ne__(self, other: typing.Any) -> bool:
        ...
    def __repr__(self) -> str:
        ...
    def __setstate__(self, state: int) -> None:
        ...
    def __str__(self) -> str:
        ...
    @property
    def name(self) -> str:
        ...
    @property
    def value(self) -> int:
        ...
class MoneroAltChain:
    block_hashes: list[str]
    difficulty: int
    height: int
    length: int
    main_chain_parent_block_hash: str
    def __init__(self) -> None:
        ...
class MoneroBan:
    host: str
    ip: int
    is_banned: bool
    seconds: int
    def __init__(self) -> None:
        ...
class MoneroBlock(MoneroBlockHeader):
    hex: str
    miner_tx: MoneroTx
    tx_hashes: list[str]
    txs: list[MoneroTx]
    def __init__(self) -> None:
        ...
class MoneroBlockHeader(SerializableStruct):
    cumulative_difficulty: int
    depth: int
    difficulty: int
    hash: str
    height: int
    long_term_weight: int
    major_version: int
    miner_tx_hash: str
    minor_version: int
    nonce: int
    num_txs: int
    orphan_status: bool
    pow_hash: str
    prev_hash: str
    reward: int
    size: int
    timestamp: int
    weight: int
    def __init__(self) -> None:
        ...
class MoneroBlockTemplate:
    block_hashing_blob: str
    block_template_blob: str
    difficulty: int
    expected_reward: int
    height: int
    next_seed_hash: str
    prev_hash: str
    reserved_offset: int
    seed_hash: str
    seed_height: int
    def __init__(self) -> None:
        ...
class MoneroCheck(SerializableStruct):
    is_good: bool
    def __init__(self) -> None:
        ...
class MoneroCheckReserve(MoneroCheck):
    total_amount: int
    unconfirmed_spent_amount: int
    def __init__(self) -> None:
        ...
class MoneroCheckTx(MoneroCheck):
    in_tx_pool: bool
    num_confirmations: int
    received_amount: int
    def __init__(self) -> None:
        ...
class MoneroConnectionSpan:
    connection_id: str
    num_blocks: int
    rate: int
    remote_address: str
    size: int
    speed: int
    start_height: int
    def __init__(self) -> None:
        ...
class MoneroConnectionType:
    """
    Members:
    
      INVALID
    
      IPV4
    
      IPV6
    
      TOR
    
      I2P
    """
    I2P: typing.ClassVar[MoneroConnectionType]  # value = <MoneroConnectionType.I2P: 4>
    INVALID: typing.ClassVar[MoneroConnectionType]  # value = <MoneroConnectionType.INVALID: 0>
    IPV4: typing.ClassVar[MoneroConnectionType]  # value = <MoneroConnectionType.IPV4: 1>
    IPV6: typing.ClassVar[MoneroConnectionType]  # value = <MoneroConnectionType.IPV6: 2>
    TOR: typing.ClassVar[MoneroConnectionType]  # value = <MoneroConnectionType.TOR: 3>
    __members__: typing.ClassVar[dict[str, MoneroConnectionType]]  # value = {'INVALID': <MoneroConnectionType.INVALID: 0>, 'IPV4': <MoneroConnectionType.IPV4: 1>, 'IPV6': <MoneroConnectionType.IPV6: 2>, 'TOR': <MoneroConnectionType.TOR: 3>, 'I2P': <MoneroConnectionType.I2P: 4>}
    def __eq__(self, other: typing.Any) -> bool:
        ...
    def __getstate__(self) -> int:
        ...
    def __hash__(self) -> int:
        ...
    def __index__(self) -> int:
        ...
    def __init__(self, value: int) -> None:
        ...
    def __int__(self) -> int:
        ...
    def __ne__(self, other: typing.Any) -> bool:
        ...
    def __repr__(self) -> str:
        ...
    def __setstate__(self, state: int) -> None:
        ...
    def __str__(self) -> str:
        ...
    @property
    def name(self) -> str:
        ...
    @property
    def value(self) -> int:
        ...
class MoneroDaemon:
    def add_listener(self, listener: MoneroDaemonListener) -> None:
        ...
    def check_for_update(self) -> MoneroDaemonUpdateCheckResult:
        ...
    @typing.overload
    def download_update(self) -> MoneroDaemonUpdateCheckResult:
        ...
    @typing.overload
    def download_update(self, download_path: str) -> MoneroDaemonUpdateCheckResult:
        ...
    @typing.overload
    def flush_tx_pool(self) -> None:
        ...
    @typing.overload
    def flush_tx_pool(self, hashes: list[str]) -> None:
        ...
    def get_alt_block_hashes(self) -> list[str]:
        ...
    def get_alt_chains(self) -> list[MoneroAltChain]:
        ...
    def get_block_by_hash(self, hash: str) -> MoneroBlock:
        ...
    def get_block_by_height(self, height: int) -> MoneroBlock:
        ...
    def get_block_hash(self, height: int) -> str:
        ...
    def get_block_hashes(self, block_hashes: list[str], start_height: int) -> list[str]:
        ...
    def get_block_header_by_hash(self, hash: str) -> MoneroBlockHeader:
        ...
    def get_block_header_by_height(self, height: int) -> MoneroBlockHeader:
        ...
    def get_block_headers_by_range(self, start_height: int, end_height: int) -> list[MoneroBlockHeader]:
        ...
    @typing.overload
    def get_block_template(self, wallet_address: str) -> MoneroBlockTemplate:
        ...
    @typing.overload
    def get_block_template(self, wallet_address: str, reserve_size: int) -> MoneroBlockTemplate:
        ...
    def get_blocks_by_hash(self, block_hashes: list[str], start_height: int, prune: bool) -> list[MoneroBlock]:
        ...
    def get_blocks_by_height(self, heights: list[int]) -> list[MoneroBlock]:
        ...
    def get_blocks_by_range(self, start_height: int, end_height: int) -> list[MoneroBlock]:
        ...
    @typing.overload
    def get_blocks_by_range_chunked(self, start_height: int, end_height: int) -> list[MoneroBlock]:
        ...
    @typing.overload
    def get_blocks_by_range_chunked(self, start_height: int, end_height: int, max_chunk_size: int) -> list[MoneroBlock]:
        ...
    def get_download_limit(self) -> int:
        ...
    def get_fee_estimate(self, grace_blocks: int = 0) -> MoneroFeeEstimate:
        ...
    def get_hard_fork_info(self) -> MoneroHardForkInfo:
        ...
    def get_height(self) -> int:
        ...
    def get_info(self) -> MoneroDaemonInfo:
        ...
    def get_key_image_spent_status(self, key_image: str) -> MoneroKeyImageSpentStatus:
        ...
    def get_key_image_spent_statuses(self, key_images: list[str]) -> list[MoneroKeyImageSpentStatus]:
        ...
    def get_known_peers(self) -> list[MoneroPeer]:
        ...
    def get_last_block_header(self) -> MoneroBlockHeader:
        ...
    def get_listeners(self) -> list[MoneroDaemonListener]:
        ...
    def get_miner_tx_sum(self, height: int, num_blocks: int) -> MoneroMinerTxSum:
        ...
    def get_mining_status(self) -> MoneroMiningStatus:
        ...
    @typing.overload
    def get_output_distribution(self, amounts: list[int]) -> list[MoneroOutputDistributionEntry]:
        ...
    @typing.overload
    def get_output_distribution(self, amounts: list[int], is_cumulative: bool, start_height: int, end_height: int) -> list[MoneroOutputDistributionEntry]:
        ...
    def get_output_histogram(self, amounts: list[int], min_count: int, max_count: int, is_unlocked: bool, recent_cutoff: int) -> list[MoneroOutputHistogramEntry]:
        ...
    def get_outputs(self, outputs: list[MoneroOutput]) -> list[MoneroOutput]:
        ...
    def get_peer_bans(self) -> list[MoneroBan]:
        ...
    def get_peers(self) -> list[MoneroPeer]:
        ...
    def get_sync_info(self) -> MoneroDaemonSyncInfo:
        ...
    def get_tx(self, tx_hash: str, prune: bool = False) -> MoneroTx:
        ...
    def get_tx_hex(self, tx_hash: str, prune: bool = False) -> str:
        ...
    def get_tx_hexes(self, tx_hashes: list[str], prune: bool = False) -> list[str]:
        ...
    def get_tx_pool(self) -> list[MoneroTx]:
        ...
    def get_tx_pool_backlog(self) -> list[MoneroTxBacklogEntry]:
        ...
    def get_tx_pool_hashes(self) -> list[str]:
        ...
    def get_txs(self, tx_hashes: list[str], prune: bool = False) -> list[MoneroTx]:
        ...
    def get_upload_limit(self) -> int:
        ...
    def get_version(self) -> MoneroVersion:
        ...
    def is_trusted(self) -> bool:
        ...
    def prune_blockchain(self, check: bool) -> MoneroPruneResult:
        ...
    def relay_tx_by_hash(self, tx_hash: str) -> None:
        ...
    def relay_txs_by_hash(self, tx_hashes: list[str]) -> None:
        ...
    def remove_listener(self, listener: MoneroDaemonListener) -> None:
        ...
    def reset_download_limit(self) -> int:
        ...
    def reset_upload_limit(self) -> int:
        ...
    def set_download_limit(self, limit: int) -> int:
        ...
    def set_incoming_peer_limit(self, limit: int) -> None:
        ...
    def set_outgoing_peer_limit(self, limit: int) -> None:
        ...
    def set_peer_ban(self, ban: MoneroBan) -> None:
        ...
    def set_peer_bans(self, bans: list[MoneroBan]) -> None:
        ...
    def set_upload_limit(self, limit: int) -> int:
        ...
    def start_mining(self, address: str, num_threads: int, is_background: bool, ignore_battery: bool) -> None:
        ...
    def stop(self) -> None:
        ...
    def stop_mining(self) -> None:
        ...
    def submit_block(self, block_blob: str) -> None:
        ...
    def submit_blocks(self, block_blobs: list[str]) -> None:
        ...
    def submit_tx_hex(self, tx_hex: str, do_not_relay: bool = False) -> MoneroSubmitTxResult:
        ...
    def wait_for_next_block_header(self) -> MoneroBlockHeader:
        ...
class MoneroDaemonInfo:
    adjusted_timestamp: int
    block_size_limit: int
    block_size_median: int
    block_weight_limit: int
    block_weight_median: int
    bootstrap_daemon_address: str
    credits: int
    cumulative_difficulty: int
    database_size: int
    difficulty: int
    free_space: int
    height: int
    height_without_bootstrap: int
    is_busy_syncing: bool
    is_offline: bool
    is_restricted: bool
    is_synchronized: bool
    network_type: MoneroNetworkType
    num_alt_blocks: int
    num_incoming_connections: int
    num_offline_peers: int
    num_online_peers: int
    num_outgoing_connections: int
    num_rpc_connections: int
    num_txs: int
    num_txs_pool: int
    start_timestamp: int
    target: int
    target_height: int
    top_block_hash: str
    update_available: bool
    version: str
    was_bootstrap_ever_used: bool
    def __init__(self) -> None:
        ...
class MoneroDaemonListener:
    last_header: MoneroBlockHeader
    def on_new_block(self, header: MoneroBlockHeader) -> None:
        ...
class MoneroDaemonRpc(MoneroDaemon):
    @typing.overload
    def __init__(self) -> None:
        ...
    @typing.overload
    def __init__(self, rpc: MoneroRpcConnection) -> None:
        ...
    @typing.overload
    def __init__(self, uri: str, username: str = '', password: str = '') -> None:
        ...
class MoneroDaemonSyncInfo:
    credits: int
    height: int
    next_needed_pruning_seed: int
    overview: str
    peers: list[MoneroPeer]
    spans: list[MoneroConnectionSpan]
    target_height: int
    top_block_hash: str
    def __init__(self) -> None:
        ...
class MoneroDaemonUpdateCheckResult:
    auto_uri: str
    hash: str
    is_update_available: bool
    user_uri: str
    version: str
    def __init__(self) -> None:
        ...
class MoneroDaemonUpdateDownloadResult(MoneroDaemonUpdateCheckResult):
    download_path: str
    def __init__(self) -> None:
        ...
class MoneroDecodedAddress:
    address: str
    address_type: MoneroAddressType
    network_type: MoneroNetworkType
    def __init__(self, address: str, address_type: MoneroAddressType, network_type: MoneroNetworkType) -> None:
        ...
class MoneroDestination:
    address: str
    amount: int
    def __init__(self) -> None:
        ...
class MoneroEmptyRequest(SerializableStruct):
    def __init__(self) -> None:
        ...
class MoneroError(Exception):
    pass
class MoneroFeeEstimate:
    fee: int
    fees: list[int]
    quantization_mask: int
    def __init__(self) -> None:
        ...
class MoneroHardForkInfo:
    credits: int
    earliest_height: int
    is_enabled: bool
    num_votes: int
    state: int
    threshold: int
    top_block_hash: str
    version: int
    voting: int
    window: int
    def __init__(self) -> None:
        ...
class MoneroIncomingTransfer(MoneroTransfer):
    address: str
    num_suggested_confirmations: int
    subaddress_index: int
    def __init__(self) -> None:
        ...
class MoneroIntegratedAddress(SerializableStruct):
    integrated_address: str
    payment_id: str
    standard_address: str
    def __init__(self) -> None:
        ...
class MoneroJsonRequest(SerializableStruct):
    id: str
    method: str
    params: SerializableStruct
    version: str
    @typing.overload
    def __init__(self, method: str) -> None:
        ...
    @typing.overload
    def __init__(self, method: str, params: SerializableStruct) -> None:
        ...
class MoneroJsonResponse:
    id: str
    jsonrpc: str
    @staticmethod
    def deserialize(response_json: str) -> MoneroJsonResponse:
        ...
    def __init__(self) -> None:
        ...
class MoneroKeyImage(SerializableStruct):
    hex: str
    signature: str
    @staticmethod
    def deserialize_key_images(key_images_json: str) -> list[MoneroKeyImage]:
        ...
    def __init__(self) -> None:
        ...
class MoneroKeyImageImportResult(SerializableStruct):
    height: int
    spent_amount: int
    unspent_amount: int
    def __init__(self) -> None:
        ...
class MoneroKeyImageSpentStatus:
    """
    Members:
    
      NOT_SPENT
    
      CONFIRMED
    
      TX_POOL
    """
    CONFIRMED: typing.ClassVar[MoneroKeyImageSpentStatus]  # value = <MoneroKeyImageSpentStatus.CONFIRMED: 1>
    NOT_SPENT: typing.ClassVar[MoneroKeyImageSpentStatus]  # value = <MoneroKeyImageSpentStatus.NOT_SPENT: 0>
    TX_POOL: typing.ClassVar[MoneroKeyImageSpentStatus]  # value = <MoneroKeyImageSpentStatus.TX_POOL: 2>
    __members__: typing.ClassVar[dict[str, MoneroKeyImageSpentStatus]]  # value = {'NOT_SPENT': <MoneroKeyImageSpentStatus.NOT_SPENT: 0>, 'CONFIRMED': <MoneroKeyImageSpentStatus.CONFIRMED: 1>, 'TX_POOL': <MoneroKeyImageSpentStatus.TX_POOL: 2>}
    def __eq__(self, other: typing.Any) -> bool:
        ...
    def __getstate__(self) -> int:
        ...
    def __hash__(self) -> int:
        ...
    def __index__(self) -> int:
        ...
    def __init__(self, value: int) -> None:
        ...
    def __int__(self) -> int:
        ...
    def __ne__(self, other: typing.Any) -> bool:
        ...
    def __repr__(self) -> str:
        ...
    def __setstate__(self, state: int) -> None:
        ...
    def __str__(self) -> str:
        ...
    @property
    def name(self) -> str:
        ...
    @property
    def value(self) -> int:
        ...
class MoneroMessageSignatureResult(SerializableStruct):
    is_good: bool
    is_old: bool
    signature_type: MoneroMessageSignatureType
    version: int
    def __init__(self) -> None:
        ...
class MoneroMessageSignatureType:
    """
    Members:
    
      SIGN_WITH_SPEND_KEY
    
      SIGN_WITH_VIEW_KEY
    """
    SIGN_WITH_SPEND_KEY: typing.ClassVar[MoneroMessageSignatureType]  # value = <MoneroMessageSignatureType.SIGN_WITH_SPEND_KEY: 0>
    SIGN_WITH_VIEW_KEY: typing.ClassVar[MoneroMessageSignatureType]  # value = <MoneroMessageSignatureType.SIGN_WITH_VIEW_KEY: 1>
    __members__: typing.ClassVar[dict[str, MoneroMessageSignatureType]]  # value = {'SIGN_WITH_SPEND_KEY': <MoneroMessageSignatureType.SIGN_WITH_SPEND_KEY: 0>, 'SIGN_WITH_VIEW_KEY': <MoneroMessageSignatureType.SIGN_WITH_VIEW_KEY: 1>}
    def __eq__(self, other: typing.Any) -> bool:
        ...
    def __getstate__(self) -> int:
        ...
    def __hash__(self) -> int:
        ...
    def __index__(self) -> int:
        ...
    def __init__(self, value: int) -> None:
        ...
    def __int__(self) -> int:
        ...
    def __ne__(self, other: typing.Any) -> bool:
        ...
    def __repr__(self) -> str:
        ...
    def __setstate__(self, state: int) -> None:
        ...
    def __str__(self) -> str:
        ...
    @property
    def name(self) -> str:
        ...
    @property
    def value(self) -> int:
        ...
class MoneroMinerTxSum:
    emission_sum: int
    fee_sum: int
    def __init__(self) -> None:
        ...
class MoneroMiningStatus:
    address: str
    is_active: bool
    is_background: bool
    num_threads: int
    speed: int
    def __init__(self) -> None:
        ...
class MoneroMultisigInfo:
    is_multisig: bool
    is_ready: bool
    num_participants: int
    threshold: int
    def __init__(self) -> None:
        ...
class MoneroMultisigInitResult:
    address: str
    multisig_hex: str
    def __init__(self) -> None:
        ...
class MoneroMultisigSignResult:
    signed_multisig_tx_hex: str
    tx_hashes: list[str]
    def __init__(self) -> None:
        ...
class MoneroNetworkType:
    """
    Members:
    
      MAINNET
    
      TESTNET
    
      STAGENET
    """
    MAINNET: typing.ClassVar[MoneroNetworkType]  # value = <MoneroNetworkType.MAINNET: 0>
    STAGENET: typing.ClassVar[MoneroNetworkType]  # value = <MoneroNetworkType.STAGENET: 2>
    TESTNET: typing.ClassVar[MoneroNetworkType]  # value = <MoneroNetworkType.TESTNET: 1>
    __members__: typing.ClassVar[dict[str, MoneroNetworkType]]  # value = {'MAINNET': <MoneroNetworkType.MAINNET: 0>, 'TESTNET': <MoneroNetworkType.TESTNET: 1>, 'STAGENET': <MoneroNetworkType.STAGENET: 2>}
    def __eq__(self, other: typing.Any) -> bool:
        ...
    def __getstate__(self) -> int:
        ...
    def __hash__(self) -> int:
        ...
    def __index__(self) -> int:
        ...
    def __init__(self, value: int) -> None:
        ...
    def __int__(self) -> int:
        ...
    def __ne__(self, other: typing.Any) -> bool:
        ...
    def __repr__(self) -> str:
        ...
    def __setstate__(self, state: int) -> None:
        ...
    def __str__(self) -> str:
        ...
    @property
    def name(self) -> str:
        ...
    @property
    def value(self) -> int:
        ...
class MoneroOutgoingTransfer(MoneroTransfer):
    addresses: list[str]
    destinations: list[MoneroDestination]
    subaddress_indices: list[int]
    def __init__(self) -> None:
        ...
class MoneroOutput(SerializableStruct):
    amount: int
    index: int
    key_image: MoneroKeyImage
    ring_output_indices: list[int]
    stealth_public_key: str
    tx: MoneroTx
    def __init__(self) -> None:
        ...
class MoneroOutputDistributionEntry:
    amount: int
    base: int
    distribution: list[int]
    start_height: int
    def __init__(self) -> None:
        ...
class MoneroOutputHistogramEntry:
    amount: int
    num_instances: int
    recent_instances: int
    unlocked_instances: int
    def __init__(self) -> None:
        ...
class MoneroOutputQuery(MoneroOutputWallet):
    max_amount: int
    min_amount: int
    subaddress_indices: list[int]
    tx_query: MoneroTxQuery
    @staticmethod
    def deserialize_from_block(output_query_json: str) -> MoneroOutputQuery:
        ...
    def __init__(self) -> None:
        ...
    def meets_criteria(self, output: MoneroOutputWallet, query_parent: bool = True) -> bool:
        ...
class MoneroOutputWallet(MoneroOutput):
    account_index: int
    is_frozen: bool
    is_spent: bool
    subaddress_index: int
    def __init__(self) -> None:
        ...
class MoneroPeer:
    address: str
    avg_download: int
    avg_upload: int
    connection_type: MoneroConnectionType
    current_download: int
    current_upload: int
    hash: str
    height: int
    host: str
    id: str
    is_incoming: bool
    is_local_host: bool
    is_local_ip: bool
    is_online: bool
    last_seen_timestamp: int
    live_time: int
    num_receives: int
    num_sends: int
    num_support_flags: int
    port: int
    pruning_seed: int
    receive_idle_time: int
    rpc_credits_per_hash: int
    rpc_port: int
    send_idle_time: int
    state: str
    def __init__(self) -> None:
        ...
class MoneroPruneResult:
    is_pruned: bool
    pruning_seed: int
    def __init__(self) -> None:
        ...
class MoneroRpcConnection:
    password: str
    priority: int
    proxy: str
    timeout: int
    uri: str
    username: str
    zmq_uri: str
    @typing.overload
    def __init__(self, uri: str = '', username: str = '', password: str = '', zmq_uri: str = '', priority: int = 0, timeout: int = 0) -> None:
        ...
    @typing.overload
    def __init__(self, rpc: MoneroRpcConnection) -> None:
        ...
    def check_connection(self) -> bool:
        ...
    def get_attribute(self, key: str) -> str:
        ...
    def is_authenticated(self) -> bool:
        ...
    def is_connected(self) -> bool:
        ...
    def is_i2p(self) -> bool:
        ...
    def is_onion(self) -> bool:
        ...
    def is_online(self) -> bool:
        ...
    def send_json_request(self, request: MoneroJsonRequest) -> MoneroJsonResponse:
        ...
    def set_attribute(self, key: str, value: str) -> None:
        ...
    def set_credentials(self, username: str, password: str) -> None:
        ...
class MoneroSubaddress(SerializableStruct):
    account_index: int
    address: str
    balance: int
    index: int
    is_used: bool
    label: str
    num_blocks_to_unlock: int
    num_unspent_outputs: int
    unlocked_balance: int
    def __init__(self) -> None:
        ...
class MoneroSubmitTxResult:
    credits: int
    has_invalid_input: bool
    has_invalid_output: bool
    has_too_few_outputs: bool
    is_double_spend: bool
    is_fee_too_low: bool
    is_good: bool
    is_mixin_too_low: bool
    is_nonzero_unlock_time: bool
    is_overspend: bool
    is_relayed: bool
    is_too_big: bool
    is_tx_extra_too_big: bool
    reason: str
    sanity_check_failed: bool
    top_block_hash: str
    def __init__(self) -> None:
        ...
class MoneroSyncResult(SerializableStruct):
    num_blocks_fetched: int
    received_money: bool
    def __init__(self) -> None:
        ...
class MoneroTransfer:
    account_index: int
    amount: int
    tx: MoneroTxWallet
    def __init__(self) -> None:
        ...
    def is_incoming(self) -> bool:
        ...
    def is_outgoing(self) -> bool:
        ...
class MoneroTransferQuery(MoneroTransfer):
    address: str
    addresses: list[str]
    destinations: list[MoneroDestination]
    has_destinations: bool
    incoming: bool
    subaddress_index: int
    subaddress_indices: list[int]
    tx_query: MoneroTxQuery
    @staticmethod
    def deserialize_from_block(transfer_query_json: str) -> MoneroTransferQuery:
        ...
    def __init__(self) -> None:
        ...
    def meets_criteria(self, transfer: MoneroTransferQuery, query_parent: bool = True) -> bool:
        ...
class MoneroTx(SerializableStruct):
    block: MoneroBlock
    common_tx_sets: str
    extra: list[int]
    fee: int
    full_hex: str
    hash: str
    in_tx_pool: bool
    inputs: list[MoneroOutput]
    is_confirmed: bool
    is_double_spend_seen: bool
    is_failed: bool
    is_kept_by_block: bool
    is_miner_tx: bool
    is_relayed: bool
    key: str
    last_failed_hash: str
    last_failed_height: int
    last_relayed_timestamp: int
    max_used_block_hash: str
    max_used_block_height: int
    metadata: str
    num_confirmations: int
    output_indices: list[int]
    outputs: list[MoneroOutput]
    payment_id: str
    prunable_hash: str
    prunable_hex: str
    pruned_hex: str
    rct_sig_prunable: str
    rct_signatures: str
    received_timestamp: int
    relay: bool
    ring_size: int
    signatures: list[str]
    size: int
    unlock_time: int
    version: int
    weight: int
    def __init__(self) -> None:
        ...
class MoneroTxBacklogEntry:
    def __init__(self) -> None:
        ...
class MoneroTxConfig(SerializableStruct):
    account_index: int
    address: str
    amount: int
    below_amount: int
    can_split: bool
    destinations: list[MoneroDestination]
    fee: int
    key_image: str
    note: str
    payment_id: str
    priority: MoneroTxPriority
    recipient_name: str
    relay: bool
    ring_size: int
    subaddress_indices: list[int]
    subtract_fee_from: list[int]
    sweep_each_subaddress: bool
    @staticmethod
    def deserialize(config_json: str) -> MoneroTxConfig:
        ...
    @typing.overload
    def __init__(self) -> None:
        ...
    @typing.overload
    def __init__(self, config: MoneroTxConfig) -> None:
        ...
    def copy(self) -> MoneroTxConfig:
        ...
    def get_normalized_destinations(self) -> list[MoneroDestination]:
        ...
class MoneroTxPoolStats:
    bytes_max: int
    bytes_med: int
    bytes_min: int
    bytes_total: int
    fee_total: int
    histo98pc: int
    num10m: int
    num_double_spends: int
    num_failing: int
    num_not_relayed: int
    num_txs: int
    oldest_timestamp: int
    def __init__(self) -> None:
        ...
class MoneroTxPriority:
    """
    Members:
    
      DEFAULT
    
      UNIMPORTANT
    
      NORMAL
    
      ELEVATED
    """
    DEFAULT: typing.ClassVar[MoneroTxPriority]  # value = <MoneroTxPriority.DEFAULT: 0>
    ELEVATED: typing.ClassVar[MoneroTxPriority]  # value = <MoneroTxPriority.ELEVATED: 3>
    NORMAL: typing.ClassVar[MoneroTxPriority]  # value = <MoneroTxPriority.NORMAL: 2>
    UNIMPORTANT: typing.ClassVar[MoneroTxPriority]  # value = <MoneroTxPriority.UNIMPORTANT: 1>
    __members__: typing.ClassVar[dict[str, MoneroTxPriority]]  # value = {'DEFAULT': <MoneroTxPriority.DEFAULT: 0>, 'UNIMPORTANT': <MoneroTxPriority.UNIMPORTANT: 1>, 'NORMAL': <MoneroTxPriority.NORMAL: 2>, 'ELEVATED': <MoneroTxPriority.ELEVATED: 3>}
    def __eq__(self, other: typing.Any) -> bool:
        ...
    def __getstate__(self) -> int:
        ...
    def __hash__(self) -> int:
        ...
    def __index__(self) -> int:
        ...
    def __init__(self, value: int) -> None:
        ...
    def __int__(self) -> int:
        ...
    def __ne__(self, other: typing.Any) -> bool:
        ...
    def __repr__(self) -> str:
        ...
    def __setstate__(self, state: int) -> None:
        ...
    def __str__(self) -> str:
        ...
    @property
    def name(self) -> str:
        ...
    @property
    def value(self) -> int:
        ...
class MoneroTxQuery(MoneroTxWallet):
    has_payment_id: bool
    hashes: list[str]
    height: int
    include_outputs: int
    input_query: MoneroOutputQuery
    is_incoming: bool
    is_outgoing: bool
    max_height: int
    min_height: int
    output_query: MoneroOutputQuery
    payment_ids: list[str]
    transfer_query: MoneroTransferQuery
    @staticmethod
    def deserialize_from_block(tx_query_json: str) -> MoneroTxQuery:
        ...
    def __init__(self) -> None:
        ...
    def meets_criteria(self, tx: MoneroTxWallet, query_children: bool = False) -> bool:
        ...
class MoneroTxSet(SerializableStruct):
    multisig_tx_hex: str
    signed_tx_hex: str
    txs: list[MoneroTxWallet]
    unsigned_tx_hex: str
    @staticmethod
    def deserialize(tx_set_json: str) -> MoneroTxSet:
        ...
    def __init__(self) -> None:
        ...
class MoneroTxWallet(MoneroTx):
    change_address: str
    change_amount: int
    extra_hex: str
    incoming_transfers: list[MoneroIncomingTransfer]
    input_sum: int
    is_incoming: bool
    is_locked: bool
    is_outgoing: bool
    note: str
    num_dummy_outputs: int
    outgoing_transfer: MoneroOutgoingTransfer
    output_sum: int
    tx_set: MoneroTxSet
    def __init__(self) -> None:
        ...
    def filter_outputs_wallet(self, query: MoneroOutputQuery) -> list[MoneroOutputWallet]:
        ...
    def filter_transfers(self, query: MoneroTransferQuery) -> list[MoneroTransfer]:
        ...
    @typing.overload
    def get_outputs_wallet(self) -> list[MoneroOutputWallet]:
        ...
    @typing.overload
    def get_outputs_wallet(self, query: MoneroOutputQuery) -> list[MoneroOutputWallet]:
        ...
    @typing.overload
    def get_transfers(self) -> list[MoneroTransfer]:
        ...
    @typing.overload
    def get_transfers(self, query: MoneroTransferQuery) -> list[MoneroTransfer]:
        ...
class MoneroUtils:
    @staticmethod
    def configure_logging(path: str, console: bool) -> None:
        ...
    @staticmethod
    def get_blocks_from_outputs(outputs: list[MoneroOutputWallet]) -> list[MoneroBlock]:
        ...
    @staticmethod
    def get_blocks_from_transfers(transfers: list[MoneroTransfer]) -> list[MoneroBlock]:
        ...
    @staticmethod
    def get_blocks_from_txs(txs: list[MoneroTxWallet]) -> list[MoneroBlock]:
        ...
    @staticmethod
    def get_integrated_address(network_type: MoneroNetworkType, standard_address: str, payment_id: str = '') -> MoneroIntegratedAddress:
        ...
    @staticmethod
    def get_payment_uri(config: MoneroTxConfig) -> str:
        ...
    @staticmethod
    def get_ring_size() -> int:
        ...
    @staticmethod
    def get_version() -> str:
        ...
    @staticmethod
    def is_valid_address(address: str, network_type: MoneroNetworkType) -> bool:
        ...
    @staticmethod
    def is_valid_language(language: str) -> bool:
        ...
    @staticmethod
    def is_valid_mnemonic(mnemonic: str) -> bool:
        ...
    @staticmethod
    def is_valid_payment_id(payment_id: str) -> bool:
        ...
    @staticmethod
    def is_valid_private_spend_key(private_spend_key: str) -> bool:
        ...
    @staticmethod
    def is_valid_private_view_key(private_view_key: str) -> bool:
        ...
    @staticmethod
    def is_valid_public_spend_key(public_spend_key: str) -> bool:
        ...
    @staticmethod
    def is_valid_public_view_key(public_view_key: str) -> bool:
        ...
    @staticmethod
    def set_log_level(loglevel: int) -> None:
        ...
    @staticmethod
    def validate_address(address: str, network_type: MoneroNetworkType) -> None:
        ...
    @staticmethod
    def validate_mnemonic(mnemonic: str) -> None:
        ...
    @staticmethod
    def validate_payment_id(payment_id: str) -> None:
        ...
    @staticmethod
    def validate_private_spend_key(private_spend_key: str) -> None:
        ...
    @staticmethod
    def validate_private_view_key(private_view_key: str) -> None:
        ...
    @staticmethod
    def validate_public_spend_key(public_spend_key: str) -> None:
        ...
    @staticmethod
    def validate_public_view_key(public_view_key: str) -> None:
        ...
class MoneroVersion(SerializableStruct):
    is_release: bool
    number: int
    def __init__(self) -> None:
        ...
class MoneroWallet:
    def __init__(self) -> None:
        ...
    def add_address_book_entry(self, address: str, description: str) -> int:
        ...
    def add_listener(self, listener: MoneroWalletListener) -> None:
        ...
    def change_password(self, old_password: str, new_password: str) -> None:
        ...
    def check_reserve_proof(self, address: str, message: str, signature: str) -> MoneroCheckReserve:
        ...
    def check_spend_proof(self, tx_hash: str, message: str, signature: str) -> bool:
        ...
    def check_tx_key(self, tx_hash: str, tx_key: str, address: str) -> MoneroCheckTx:
        ...
    def check_tx_proof(self, tx_hash: str, address: str, message: str, signature: str) -> MoneroCheckTx:
        ...
    def close(self, save: bool = False) -> None:
        ...
    def create_account(self, label: str = '') -> MoneroAccount:
        ...
    def create_subaddress(self, account_idx: int, label: str = '') -> MoneroSubaddress:
        ...
    def create_tx(self, config: MoneroTxConfig) -> MoneroTxWallet:
        ...
    def create_txs(self, config: MoneroTxConfig) -> list[MoneroTxWallet]:
        ...
    def decode_integrated_address(self, integrated_address: str) -> MoneroIntegratedAddress:
        ...
    def delete_address_book_entry(self, index: int) -> None:
        ...
    def describe_tx_set(self, tx_set: MoneroTxSet) -> MoneroTxSet:
        ...
    def edit_address_book_entry(self, index: int, set_address: bool, address: str, set_description: bool, description: str) -> None:
        ...
    def exchange_multisig_keys(self, mutisig_hexes: list[str], password: str) -> MoneroMultisigInitResult:
        ...
    def export_key_images(self, all: bool = False) -> list[MoneroKeyImage]:
        ...
    def export_multisig_hex(self) -> str:
        ...
    def export_outputs(self, all: bool = False) -> str:
        ...
    def freeze_output(self, key_image: str) -> None:
        ...
    @typing.overload
    def get_account(self, account_idx: int) -> MoneroAccount:
        ...
    @typing.overload
    def get_account(self, account_idx: int, include_subaddresses: bool) -> MoneroAccount:
        ...
    @typing.overload
    def get_accounts(self) -> list[MoneroAccount]:
        ...
    @typing.overload
    def get_accounts(self, include_subaddresses: bool) -> list[MoneroAccount]:
        ...
    @typing.overload
    def get_accounts(self, tag: str) -> list[MoneroAccount]:
        ...
    @typing.overload
    def get_accounts(self, include_subaddresses: bool, tag: str) -> list[MoneroAccount]:
        ...
    def get_address(self, account_idx: int, subaddress_idx: int) -> str:
        ...
    def get_address_book_entries(self, indices: list[int]) -> list[MoneroAddressBookEntry]:
        ...
    def get_address_index(self, address: str) -> MoneroSubaddress:
        ...
    def get_attribute(self, key: str, val: str) -> bool:
        ...
    @typing.overload
    def get_balance(self) -> int:
        ...
    @typing.overload
    def get_balance(self, account_idx: int) -> int:
        ...
    @typing.overload
    def get_balance(self, account_idx: int, subaddress_idx: int) -> int:
        ...
    def get_daemon_connection(self) -> MoneroRpcConnection:
        ...
    def get_daemon_height(self) -> int:
        ...
    def get_daemon_max_peer_height(self) -> int:
        ...
    def get_default_fee_priority(self) -> MoneroTxPriority:
        ...
    def get_height(self) -> int:
        ...
    def get_height_by_date(self, year: int, month: int, day: int) -> int:
        ...
    def get_integrated_address(self, standard_address: str = '', payment_id: str = '') -> MoneroIntegratedAddress:
        ...
    def get_listeners(self) -> list[MoneroWalletListener]:
        ...
    def get_multisig_info(self) -> MoneroMultisigInfo:
        ...
    def get_network_type(self) -> MoneroNetworkType:
        ...
    def get_outputs(self, query: MoneroOutputQuery) -> list[MoneroOutputWallet]:
        ...
    def get_path(self) -> str:
        ...
    def get_payment_uri(self, config: MoneroTxConfig) -> str:
        ...
    def get_primary_address(self) -> str:
        ...
    def get_private_spend_key(self) -> str:
        ...
    def get_private_view_key(self) -> str:
        ...
    def get_public_spend_key(self) -> str:
        ...
    def get_public_view_key(self) -> str:
        ...
    def get_reserve_proof_account(self, account_idx: int, amount: int, message: str) -> str:
        ...
    def get_reserve_proof_wallet(self, message: str) -> str:
        ...
    def get_restore_height(self) -> int:
        ...
    def get_seed(self) -> str:
        ...
    def get_seed_language(self) -> str:
        ...
    def get_spend_proof(self, tx_hash: str, message: str) -> str:
        ...
    @typing.overload
    def get_subaddresses(self, account_idx: int) -> list[MoneroSubaddress]:
        ...
    @typing.overload
    def get_subaddresses(self, account_idx: int, subaddress_indices: list[int]) -> list[MoneroSubaddress]:
        ...
    def get_transfers(self, query: MoneroTransferQuery) -> list[MoneroTransfer]:
        ...
    def get_tx_key(self, tx_hash: str) -> str:
        ...
    def get_tx_note(self, tx_hash: str) -> str:
        ...
    def get_tx_notes(self, tx_hashes: list[str]) -> list[str]:
        ...
    def get_tx_proof(self, tx_hash: str, address: str, message: str) -> str:
        ...
    @typing.overload
    def get_txs(self) -> list[MoneroTxWallet]:
        ...
    @typing.overload
    def get_txs(self, query: MoneroTxQuery) -> list[MoneroTxWallet]:
        ...
    @typing.overload
    def get_unlocked_balance(self) -> int:
        ...
    @typing.overload
    def get_unlocked_balance(self, account_idx: int) -> int:
        ...
    @typing.overload
    def get_unlocked_balance(self, account_idx: int, subaddress_idx: int) -> int:
        ...
    def get_version(self) -> MoneroVersion:
        ...
    def import_key_images(self, key_images: list[MoneroKeyImage]) -> MoneroKeyImageImportResult:
        ...
    def import_multisig_hex(self, multisig_hexes: list[str]) -> int:
        ...
    def import_outputs(self, outputs_hex: str) -> int:
        ...
    def is_connected_to_daemon(self) -> bool:
        ...
    def is_daemon_trusted(self) -> bool:
        ...
    def is_multisig(self) -> bool:
        ...
    def is_multisig_import_needed(self) -> bool:
        ...
    def is_output_frozen(self, key_image: str) -> bool:
        ...
    def is_synced(self) -> bool:
        ...
    def is_view_only(self) -> bool:
        ...
    def make_multisig(self, mutisig_hexes: list[str], threshold: int, password: str) -> str:
        ...
    def move_to(self, path: str, password: str) -> None:
        ...
    def parse_payment_uri(self, uri: str) -> MoneroTxConfig:
        ...
    def prepare_multisig(self) -> str:
        ...
    @typing.overload
    def relay_tx(self, tx_metadata: str) -> str:
        ...
    @typing.overload
    def relay_tx(self, tx: MoneroTxWallet) -> str:
        ...
    @typing.overload
    def relay_txs(self, txs: list[MoneroTxWallet]) -> list[str]:
        ...
    @typing.overload
    def relay_txs(self, tx_metadatas: list[str]) -> list[str]:
        ...
    def remove_listener(self, listener: MoneroWalletListener) -> None:
        ...
    def rescan_blockchain(self) -> None:
        ...
    def rescan_spent(self) -> None:
        ...
    def save(self) -> None:
        ...
    def scan_txs(self, tx_hashes: list[str]) -> None:
        ...
    def set_attribute(self, key: str, val: str) -> None:
        ...
    @typing.overload
    def set_daemon_connection(self, connection: MoneroRpcConnection) -> None:
        ...
    @typing.overload
    def set_daemon_connection(self, uri: str = '', username: str = '', password: str = '') -> None:
        ...
    def set_daemon_proxy(self, uri: str = '') -> None:
        ...
    def set_restore_height(self, restore_height: int) -> None:
        ...
    def set_subaddress_label(self, account_idx: int, subaddress_idx: int, label: str = '') -> None:
        ...
    def set_tx_note(self, tx_hash: str, note: str) -> None:
        ...
    def set_tx_notes(self, tx_hashes: list[str], notes: list[str]) -> None:
        ...
    def sign_message(self, msg: str, signature_type: MoneroMessageSignatureType, account_idx: int = 0, subaddress_idx: int = 0) -> str:
        ...
    def sign_multisig_tx_hex(self, multisig_tx_hex: str) -> MoneroMultisigSignResult:
        ...
    def sign_txs(self, unsigned_tx_hex: str) -> MoneroTxSet:
        ...
    def start_syncing(self, sync_period_in_ms: int = 10000) -> None:
        ...
    def stop_mining(self) -> None:
        ...
    def stop_syncing(self) -> None:
        ...
    def submit_multisig_tx_hex(self, signed_multisig_tx_hex: str) -> list[str]:
        ...
    def submit_txs(self, signed_tx_hex: str) -> list[str]:
        ...
    def sweep_dust(self, relay: bool = False) -> list[MoneroTxWallet]:
        ...
    def sweep_output(self, config: MoneroTxConfig) -> MoneroTxWallet:
        ...
    def sweep_unlocked(self, config: MoneroTxConfig) -> list[MoneroTxWallet]:
        ...
    @typing.overload
    def sync(self) -> MoneroSyncResult:
        ...
    @typing.overload
    def sync(self, listener: MoneroWalletListener) -> MoneroSyncResult:
        ...
    @typing.overload
    def sync(self, start_height: int) -> MoneroSyncResult:
        ...
    @typing.overload
    def sync(self, start_height: int, listener: MoneroWalletListener) -> MoneroSyncResult:
        ...
    def thaw_output(self, key_image: str) -> None:
        ...
    def verify_message(self, msg: str, address: str, signature: str) -> MoneroMessageSignatureResult:
        ...
    def wait_for_next_block(self) -> int:
        ...
class MoneroWalletConfig(SerializableStruct):
    account_lookahead: int
    is_multisig: bool
    language: str
    network_type: MoneroNetworkType
    password: str
    path: str
    primary_address: str
    private_spend_key: str
    private_view_key: str
    restore_height: int
    save_current: bool
    seed: str
    seed_offset: str
    server: MoneroRpcConnection
    subaddress_lookahead: int
    @staticmethod
    def deserialize(config_json: str) -> MoneroWalletConfig:
        ...
    def __init__(self) -> None:
        ...
    def copy(self) -> MoneroWalletConfig:
        ...
class MoneroWalletFull(MoneroWallet):
    @staticmethod
    def create_wallet(config: MoneroWalletConfig) -> MoneroWalletFull:
        ...
    @staticmethod
    def get_seed_languages() -> list[str]:
        ...
    @staticmethod
    def open_wallet(path: str, password: str, nettype: MoneroNetworkType) -> MoneroWalletFull:
        ...
    @staticmethod
    @typing.overload
    def open_wallet_data(password: str, nettype: MoneroNetworkType, keys_data: str, cache_data: str) -> MoneroWalletFull:
        ...
    @staticmethod
    @typing.overload
    def open_wallet_data(password: str, nettype: MoneroNetworkType, keys_data: str, cache_data: str, daemon_connection: MoneroRpcConnection) -> MoneroWalletFull:
        ...
    @staticmethod
    def wallet_exists(path: str) -> bool:
        ...
    def get_cache_file_buffer(self) -> str:
        ...
    def get_keys_file_buffer(self, password: str, view_only: bool) -> str:
        ...
class MoneroWalletKeys(MoneroWallet):
    @staticmethod
    def create_wallet_from_keys(config: MoneroWalletConfig) -> MoneroWalletKeys:
        ...
    @staticmethod
    def create_wallet_from_seed(config: MoneroWalletConfig) -> MoneroWalletKeys:
        ...
    @staticmethod
    def create_wallet_random(config: MoneroWalletConfig) -> MoneroWalletKeys:
        ...
    @staticmethod
    def get_seed_languages() -> list[str]:
        ...
class MoneroWalletListener:
    def on_balances_changed(self, new_balance: int, new_unclocked_balance: int) -> None:
        ...
    def on_new_block(self, height: int) -> None:
        ...
    def on_output_received(self, output: MoneroOutputWallet) -> None:
        ...
    def on_output_spent(self, output: MoneroOutputWallet) -> None:
        ...
    def on_sync_progress(self, height: int, start_height: int, end_height: int, percent_done: float, message: str) -> None:
        ...
class MoneroWalletRpc(MoneroWallet):
    def __init__(self, rpc_connection: MoneroRpcConnection) -> None:
        ...
class SerializableStruct:
    def __init__(self) -> None:
        ...
    def serialize(self) -> str:
        ...
