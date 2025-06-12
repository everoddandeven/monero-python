import typing

from .monero_daemon_listener import MoneroDaemonListener
from .monero_daemon_update_check_result import MoneroDaemonUpdateCheckResult
from .monero_daemon_update_download_result import MoneroDaemonUpdateDownloadResult
from .monero_alt_chain import MoneroAltChain
from .monero_block import MoneroBlock
from .monero_block_header import MoneroBlockHeader
from .monero_block_template import MoneroBlockTemplate
from .monero_fee_estimate import MoneroFeeEstimate
from .monero_hard_fork_info import MoneroHardForkInfo
from .monero_daemon_info import MoneroDaemonInfo
from .monero_key_image_spent_status import MoneroKeyImageSpentStatus
from .monero_peer import MoneroPeer
from .monero_miner_tx_sum import MoneroMinerTxSum
from .monero_mining_status import MoneroMiningStatus
from .monero_output_distribution_entry import MoneroOutputDistributionEntry
from .monero_output_histogram_entry import MoneroOutputHistogramEntry
from .monero_output import MoneroOutput
from .monero_tx import MoneroTx
from .monero_ban import MoneroBan
from .monero_daemon_sync_info import MoneroDaemonSyncInfo
from .monero_tx_backlog_entry import MoneroTxBacklogEntry
from .monero_tx_pool_stats import MoneroTxPoolStats
from .monero_version import MoneroVersion
from .monero_prune_result import MoneroPruneResult
from .monero_submit_tx_result import MoneroSubmitTxResult


class MoneroDaemon:
    """
    Monero daemon interface.
    """
    def __init__(self) -> None:
        """Initialize a Monero daemon."""
        ...
    def add_listener(self, listener: MoneroDaemonListener) -> None:
        """
        Register a listener to receive daemon notifications.
        
        :param MoneroDaemonListener: listener the listener to register
        """
        ...
    def check_for_update(self) -> MoneroDaemonUpdateCheckResult:
        """
        Check for update.
        
        :return MoneroDaemonUpdateCheckResult: the result of the update check
        """
        ...
    @typing.overload
    def download_update(self) -> MoneroDaemonUpdateDownloadResult:
        """
        Download an update.
        
        :param path: is the path to download the update (optional)
        :return MoneroDaemonUpdateDownloadResult: the result of the update download
        """
        ...
    @typing.overload
    def download_update(self, download_path: str) -> MoneroDaemonUpdateDownloadResult:
        """
        Download an update.
        
        :return MoneroDaemonUpdateDownloadResult: the result of the update download
        """
        ...
    @typing.overload
    def flush_tx_pool(self) -> None:
        """
        Flush transactions from the tx pool.        
        """
        ...
    @typing.overload
    def flush_tx_pool(self, hash: str) -> None:
        """
        Flush transaction from the tx pool.
        """
        ...
    @typing.overload
    def flush_tx_pool(self, hashes: list[str]) -> None:
        """
        Flush transactions from the tx pool.
        
        :param list[str] hashes: are hashes of transactions to flush
        """
        ...
    def get_alt_block_hashes(self) -> list[str]:
        """
        Get known block hashes which are not on the main chain.
        
        :return list[str]: known block hashes which are not on the main chain
        """
        ...
    def get_alt_chains(self) -> list[MoneroAltChain]:
        """
        Get alternative chains seen by the node.
        
        :return list[MoneroAltChain]: alternative chains seen by the node
        """
        ...
    def get_block_by_hash(self, hash: str) -> MoneroBlock:
        """
        Get a block by hash.
        
        :param str hash: is the hash of the block to get
        :return MoneroBlock: the block with the given hash
        """
        ...
    def get_block_by_height(self, height: int) -> MoneroBlock:
        """
        Get a block by height.
        
        :param int height: is the height of the block to get
        :return MoneroBlock: the block at the given height
        """
        ...
    def get_block_hash(self, height: int) -> str:
        """
        Get a block's hash by its height.
        
        :param int height: is the height of the block hash to get
        :return str: the block's hash at the given height
        """
        ...
    def get_block_hashes(self, block_hashes: list[str], start_height: int) -> list[str]:
        """
        Get block hashes as a binary request to the daemon.
        
        :param list[str] block_hashes: specify block hashes to fetch; first 10 blocks 
                hash goes sequential, next goes in pow(2,n) offset, 
                like 2, 4, 8, 16, 32, 64 and so on, and the last one is always genesis block
        :param int start_height: is the starting height of block hashes to return
        :return list[str]: the requested block hashes
        """
        ...
    def get_block_header_by_hash(self, hash: str) -> MoneroBlockHeader:
        """
        Get a block header by its hash.
        
        :param str hash: is the hash of the block to get the header of
        :return MoneroBlockHeader: the block's header
        """
        ...
    def get_block_header_by_height(self, height: int) -> MoneroBlockHeader:
        """
        Get a block header by its height.
        
        :param int height: is the height of the block to get the header of
        :return MoneroBlockHeader: the block's header
        """
        ...
    def get_block_headers_by_range(self, start_height: int, end_height: int) -> list[MoneroBlockHeader]:
        """
        Get block headers for the given range.
        
        :param int start_height: is the start height lower bound inclusive (optional)
        :param int end_height: is the end height upper bound inclusive (optional)
        :return list[MoneroBlockHeader]: block headers in the given range
        """
        ...
    @typing.overload
    def get_block_template(self, wallet_address: str) -> MoneroBlockTemplate:
        """
        Get a block template for mining a new block.
        
        :param str wallet_address: is the address of the wallet to receive miner transactions if block is successfully mined
        :return MoneroBlockTemplate: a block template for mining a new block
        """
        ...
    @typing.overload
    def get_block_template(self, wallet_address: str, reserve_size: int) -> MoneroBlockTemplate:
        """
        Get a block template for mining a new block.
        
        :param str wallet_address: is the address of the wallet to receive miner transactions if block is successfully mined
        :param int reserve_size: is the reserve size (optional)
        :return MoneroBlockTemplate: a block template for mining a new block
        """
        ...
    def get_blocks_by_hash(self, block_hashes: list[str], start_height: int, prune: bool) -> list[MoneroBlock]:
        """
        Get a block by hash.
        
        :param list[str] block_hash: is the hash of the block to get
        :return list[MoneroBlock]: the block with the given hash
        """
        ...
    def get_blocks_by_height(self, heights: list[int]) -> list[MoneroBlock]:
        """
        Get blocks at the given heights.
        
        :param list[int] heights: are the heights of the blocks to get
        :return list[MoneroBlock]: blocks at the given heights
        """
        ...
    def get_blocks_by_range(self, start_height: int, end_height: int) -> list[MoneroBlock]:
        """
        Get blocks in the given height range.
        
        :param int start_height: is the start height lower bound inclusive (optional)
        :param int end_height: is the end height upper bound inclusive (optional)
        :return list[MoneroBlock]: blocks in the given height range
        """
        ...
    @typing.overload
    def get_blocks_by_range_chunked(self, start_height: int, end_height: int) -> list[MoneroBlock]:
        """
        Get blocks in the given height range as chunked requests so that each request is
        not too big.
        
        :param int start_height: is the start height lower bound inclusive (optional)
        :param int end_height: is the end height upper bound inclusive (optional)
        :return list[MoneroBlock]: blocks in the given height range
        """
        ...
    @typing.overload
    def get_blocks_by_range_chunked(self, start_height: int, end_height: int, max_chunk_size: int) -> list[MoneroBlock]:
        """
        Get blocks in the given height range as chunked requests so that each request is
        not too big.
        
        :param int start_height: is the start height lower bound inclusive (optional)
        :param int end_height: is the end height upper bound inclusive (optional)
        :param int max_chunk_size: is the maximum chunk size in any one request (default 3,000,000 bytes)
        :return list[MoneroBlock]: blocks in the given height range
        """
        ...
    def get_download_limit(self) -> int:
        """
        Get the download bandwidth limit.
        
        :return int: is the download bandwidth limit
        """
        ...
    def get_fee_estimate(self, grace_blocks: int = 0) -> MoneroFeeEstimate:
        """
        Get mining fee estimates per kB.
        
        :param int grace_blocks: TODO
        :return MoneroFeeEstimate: mining fee estimates per kB
        """
        ...
    def get_hard_fork_info(self) -> MoneroHardForkInfo:
        """
        Look up information regarding hard fork voting and readiness.
        
        :return MoneroHardForkInfo: hard fork information
        """
        ...
    def get_height(self) -> int:
        """
        Get the number of blocks in the longest chain known to the node.
        
        :return int: the number of blocks
        """
        ...
    def get_info(self) -> MoneroDaemonInfo:
        """
        Get general information about the state of the node and the network.
        
        :return MoneroDaemonInfo: general information about the node and network
        """
        ...
    def get_key_image_spent_status(self, key_image: str) -> MoneroKeyImageSpentStatus:
        """
        Get the spent status of the given key image.
        
        :param str key_image: is key image hex to get the status of
        :return MoneroKeyImageSpentStatus: the status of the key image
        """
        ...
    def get_key_image_spent_statuses(self, key_images: list[str]) -> list[MoneroKeyImageSpentStatus]:
        """
        Get the spent status of each given key image.
        
        :param list[str] key_images: are hex key images to get the statuses of
        :return list[MoneroKeyImageSpentStatus]: the spent status for each key image
        """
        ...
    def get_known_peers(self) -> list[MoneroPeer]:
        """
        Get all known peers including their last known online status.
        
        :return list[MoneroPeer]: the daemon's known peers
        """
        ...
    def get_last_block_header(self) -> MoneroBlockHeader:
        """
        Get the last block's header.
        
        :return MoneroBlockHeader: the last block's header
        """
        ...
    def get_listeners(self) -> list[MoneroDaemonListener]:
        """
        Get the listeners registered with the daemon.
        
        :return list[MoneroDaemonListener]: the registered listeners
        """
        ...
    def get_miner_tx_sum(self, height: int, num_blocks: int) -> MoneroMinerTxSum:
        """
        Gets the total emissions and fees from the genesis block to the current height.
        
        :param int height: is the height to start computing the miner sum
        :param int num_blocks: are the number of blocks to include in the sum
        :return MoneroMinerTxSum: the sum emission and fees since the geneis block
        """
        ...
    def get_mining_status(self) -> MoneroMiningStatus:
        """
        Get the daemon's mining status.
        
        :return MoneroMiningStatus: the daemon's mining status
        """
        ...
    @typing.overload
    def get_output_distribution(self, amounts: list[int]) -> list[MoneroOutputDistributionEntry]:
        """
        Creates an output distribution.
        
        :param list[int] amounts: are amounts of outputs to make the distribution with
        :return list[MoneroOutputDistributionEntry]: output distribution entries meeting the parameters
        """
        ...
    @typing.overload
    def get_output_distribution(self, amounts: list[int], is_cumulative: bool, start_height: int, end_height: int) -> list[MoneroOutputDistributionEntry]:
        """
        Creates an output distribution.
        
        :param list[int] amounts: are amounts of outputs to make the distribution with
        :param bool is_cumulative: specifies if the results should be cumulative (defaults to TODO)
        :param int start_height: is the start height lower bound inclusive (optional)
        :param int end_height: is the end height upper bound inclusive (optional)
        :return list[MoneroOutputDistributionEntry]: output distribution entries meeting the parameters
        """
        ...
    def get_output_histogram(self, amounts: list[int], min_count: int, max_count: int, is_unlocked: bool, recent_cutoff: int) -> list[MoneroOutputHistogramEntry]:
        """
        Get a histogram of output amounts. For all amounts (possibly filtered by
        parameters), gives the number of outputs on the chain for that amount.
        RingCT outputs counts as 0 amount.
        
        :param int amounts: are amounts of outputs to make the histogram with
        :param int min_count: TODO
        :param int max_count: TODO
        :param bool is_unlocked: makes a histogram with outputs with the specified lock state
        :param int recent_cutoff: TODO
        :return list[MoneroOutputHistogramEntry]: output histogram entries meeting the parameters
        """
        ...
    def get_outputs(self, outputs: list[MoneroOutput]) -> list[MoneroOutput]:
        """
        Get outputs identified by a list of output amounts and indices as a binary
        request.
        
        :param list[MoneroOutput] outputs: identify each output by amount and index
        :return list[MoneroOutput]: the identified outputs
        """
        ...
    def get_peer_bans(self) -> list[MoneroBan]:
        """
        Get peer bans.
        
        :return list[MoneroBan]: entries about banned peers
        """
        ...
    def get_peers(self) -> list[MoneroPeer]:
        """
        Get peers with active incoming or outgoing connections to the node.
        
        :return list[MoneroPeer]: the daemon's peers
        """
        ...
    def get_sync_info(self) -> MoneroDaemonSyncInfo:
        """
        Get synchronization information.
        
        :return MoneroDaemonSyncInfo: contains sync information
        """
        ...
    def get_tx(self, tx_hash: str, prune: bool = False) -> MoneroTx | None:
        """
        Get a transaction by hash.
        
        :param str tx_hash: is the hash of the transaction to get
        :param bool prune: specifies if the returned tx should be pruned (defaults to false)
        :return Optional[MoneroTx]: the transaction with the given hash or null if not found
        """
        ...
    def get_tx_hex(self, tx_hash: str, prune: bool = False) -> str | None:
        """
        Get a transaction hex by hash.
        
        :param str tx_hash: is the hash of the transaction to get hex from
        :param bool prune: specifies if the returned tx hex should be pruned (defaults to false)
        :return Optional[str]: the tx hex with the given hash
        """
        ...
    def get_tx_hexes(self, tx_hashes: list[str], prune: bool = False) -> list[str]:
        """
        Get transaction hexes by hashes.
        
        :param list[str] tx_hashes: are hashes of transactions to get hexes from
        :param bool prune: Prune transaction hashes.
        :return list[str]: are the tx hexes
        """
        ...
    def get_tx_pool(self) -> list[MoneroTx]:
        """
        Get valid transactions seen by the node but not yet mined into a block, as well
        as spent key image information for the tx pool.
        
        :return list[MoneroTx]: transactions in the transaction pool
        """
        ...
    def get_tx_pool_backlog(self) -> list[MoneroTxBacklogEntry]:
        """
        Get all transaction pool backlog.
        
        :return list[MoneroTxBacklogEntry]: transaction pool backlog entries
        """
        ...
    def get_tx_pool_hashes(self) -> list[str]:
        """
        Get hashes of transactions in the transaction pool.
         
        :return list[str]: hashes of transactions in the transaction pool
        """
        ...
    def get_tx_pool_stats(self) -> MoneroTxPoolStats:
        """
        Get transaction pool statistics.
         
        :return MoneroTxPoolStats: statistics about the transaction pool
        """
        ...
    def get_txs(self, tx_hashes: list[str], prune: bool = False) -> list[MoneroTx]:
        """
        Get transactions by hashes.
        
        :param list[str] tx_hashes: are hashes of transactions to get
        :param bool prune: Prune transactions.
        :return list[MoneroTx]: found transactions with the given hashes
        """
        ...
    def get_upload_limit(self) -> int:
        """
        Get the upload bandwidth limit.
         
        :return int: is the upload bandwidth limit
        """
        ...
    def get_version(self) -> MoneroVersion:
        """
        Gets the version of the daemon.
        
        :return MoneroVersion: the version of the daemon
        """
        ...
    def is_trusted(self) -> bool:
        """
        Indicates if the daemon is trusted or untrusted.
        
        :return bool: true if the daemon is trusted, false otherwise
        """
        ...
    def prune_blockchain(self, check: bool) -> MoneroPruneResult:
        """
        Prune the blockchain.
        
        :param bool check: specifies to check the pruning (default false)
        :return MoneroPruneResult: the prune result
        """
        ...
    def relay_tx_by_hash(self, tx_hash: str) -> None:
        """
        Relays a transaction by hash.
        
        :param str tx_hash: identifies the transaction to relay
        """
        ...
    def relay_txs_by_hash(self, tx_hashes: list[str]) -> None:
        """
        Relays transactions by hash.
        
        :param list[str] tx_hashes: identify the transactions to relay
        """
        ...
    def remove_listener(self, listener: MoneroDaemonListener) -> None:
        """
        Unregister a listener to receive daemon notifications.
        
        :param MoneroDaemonListener listener: a previously registered listener to be unregistered
        """
        ...
    def reset_download_limit(self) -> int:
        """
        Reset the download bandwidth limit.
        
        :return int: the download bandwidth limit after resetting
        """
        ...
    def reset_upload_limit(self) -> int:
        """
        Reset the upload bandwidth limit.
        
        :return int: the upload bandwidth limit after resetting
        """
        ...
    def set_download_limit(self, limit: int) -> int:
        """
        Set the download bandwidth limit.
        
        :param int limit: is the download limit to set (-1 to reset to default)
        :return int: is the new download limit after setting
        """
        ...
    def set_incoming_peer_limit(self, limit: int) -> None:
        """
        Limit number of incoming peers.
        
        :param int limit: is the maximum number of incoming peers
        """
        ...
    def set_outgoing_peer_limit(self, limit: int) -> None:
        """
        Limit number of outgoing peers.
        
        :param int limit: is the maximum number of outgoing peers
        """
        ...
    def set_peer_ban(self, ban: MoneroBan) -> None:
        """
        Ban a peer node.
        
        :param MoneroBan ban: contains information about a node to ban
        """
        ...
    def set_peer_bans(self, bans: list[MoneroBan]) -> None:
        """
        Ban peers nodes.
        
        :param list[MoneroBan] bans: are bans to apply against peer nodes
        """
        ...
    def set_upload_limit(self, limit: int) -> int:
        """
        Set the upload bandwidth limit.
        
        :param int limit: is the upload limit to set (-1 to reset to default)
        :return int: is the new upload limit after setting
        """
        ...
    def start_mining(self, address: str, num_threads: int, is_background: bool, ignore_battery: bool) -> None:
        """
        Start mining.
        
        :param str address: is the address given miner rewards if the daemon mines a block
        :param int num_threads: is the number of mining threads to run
        :param bool is_background: specifies if the miner should run in the background or not
        :param bool ignore_battery: specifies if the battery state (e.g. on laptop) should be ignored or not
        """
        ...
    def stop(self) -> None:
        """
        Safely disconnect and shut down the daemon.
        """
        ...
    def stop_mining(self) -> None:
        """
        Stop mining.
        """
        ...
    def submit_block(self, block_blob: str) -> None:
        """
        Submit a mined block to the network.
        
        :param str block_blob: is the mined block to submit
        """
        ...
    def submit_blocks(self, block_blobs: list[str]) -> None:
        """
        Submit mined blocks to the network.
         
        :param list[str] block_blobs: are the mined blocks to submit
        """
        ...
    def submit_tx_hex(self, tx_hex: str, do_not_relay: bool = False) -> MoneroSubmitTxResult:
        """
        Submits a transaction to the daemon's pool.
        
        :param str tx_hex: is the raw transaction hex to submit
        :return MoneroSubmitTxResult: the submission results
        """
        ...
    def wait_for_next_block_header(self) -> MoneroBlockHeader:
        """
        Get the header of the next block added to the chain.

        :return MoneroBlockHeader: the header of the next block added to the chain
        """
        ...
