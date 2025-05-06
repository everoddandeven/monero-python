"""
Monero Python

Copyright (c) everoddandeven

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

Parts of this file are originally copyright (c) woodser

Parts of this file are originally copyright (c) 2014-2019, The Monero Project

Redistribution and use in source and binary forms, with or without modification, are
permitted provided that the following conditions are met:

All rights reserved.

1. Redistributions of source code must retain the above copyright notice, this list of
   conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice, this list
   of conditions and the following disclaimer in the documentation and/or other
   materials provided with the distribution.

3. Neither the name of the copyright holder nor the names of its contributors may be
   used to endorse or promote products derived from this software without specific
   prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY
EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL
THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT,
STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF
THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

Parts of this file are originally copyright (c) 2012-2013 The Cryptonote developers
"""
from __future__ import annotations
import typing
__all__ = ['MoneroAccount', 'MoneroAccountTag', 'MoneroAddressBookEntry', 'MoneroAddressType', 'MoneroAltChain', 'MoneroBan', 'MoneroBlock', 'MoneroBlockHeader', 'MoneroBlockTemplate', 'MoneroCheck', 'MoneroCheckReserve', 'MoneroCheckTx', 'MoneroConnectionManager', 'MoneroConnectionManagerListener', 'MoneroConnectionPollType', 'MoneroConnectionProriotyComparator', 'MoneroConnectionSpan', 'MoneroConnectionType', 'MoneroDaemon', 'MoneroDaemonDefault', 'MoneroDaemonInfo', 'MoneroDaemonListener', 'MoneroDaemonRpc', 'MoneroDaemonSyncInfo', 'MoneroDaemonUpdateCheckResult', 'MoneroDaemonUpdateDownloadResult', 'MoneroDecodedAddress', 'MoneroDestination', 'MoneroError', 'MoneroFeeEstimate', 'MoneroHardForkInfo', 'MoneroIncomingTransfer', 'MoneroIntegratedAddress', 'MoneroJsonRequest', 'MoneroJsonRequestEmptyParams', 'MoneroJsonRequestParams', 'MoneroJsonResponse', 'MoneroKeyImage', 'MoneroKeyImageImportResult', 'MoneroKeyImageSpentStatus', 'MoneroMessageSignatureResult', 'MoneroMessageSignatureType', 'MoneroMinerTxSum', 'MoneroMiningStatus', 'MoneroMultisigInfo', 'MoneroMultisigInitResult', 'MoneroMultisigSignResult', 'MoneroNetworkType', 'MoneroOutgoingTransfer', 'MoneroOutput', 'MoneroOutputDistributionEntry', 'MoneroOutputHistogramEntry', 'MoneroOutputQuery', 'MoneroOutputWallet', 'MoneroPathRequest', 'MoneroPeer', 'MoneroPruneResult', 'MoneroRequest', 'MoneroRpcConnection', 'MoneroRpcError', 'MoneroSubaddress', 'MoneroSubmitTxResult', 'MoneroSyncResult', 'MoneroTransfer', 'MoneroTransferQuery', 'MoneroTx', 'MoneroTxBacklogEntry', 'MoneroTxConfig', 'MoneroTxPoolStats', 'MoneroTxPriority', 'MoneroTxQuery', 'MoneroTxSet', 'MoneroTxWallet', 'MoneroUtils', 'MoneroVersion', 'MoneroWallet', 'MoneroWalletConfig', 'MoneroWalletFull', 'MoneroWalletKeys', 'MoneroWalletListener', 'MoneroWalletRpc', 'SerializableStruct', 'VectorInt', 'VectorMoneroBlock', 'VectorMoneroBlockHeader', 'VectorMoneroDestination', 'VectorMoneroIncomingTransfer', 'VectorMoneroOutgoingTransfer', 'VectorMoneroOutput', 'VectorMoneroOutputWallet', 'VectorMoneroSubaddress', 'VectorMoneroTransfer', 'VectorMoneroTx', 'VectorMoneroTxWallet', 'VectorString', 'VectorUint32', 'VectorUint64', 'VectorUint8']
class MoneroAccount(SerializableStruct):
    """
    Models a Monero account.
    """
    balance: int | None
    index: int | None
    primary_address: str | None
    subaddresses: list[MoneroSubaddress]
    tag: str | None
    unlocked_balance: int | None
    def __init__(self) -> None:
        ...
class MoneroAccountTag:
    """
    Models a Monero account tag.
    """
    account_indices: list[int]
    label: str | None
    tag: str | None
    @typing.overload
    def __init__(self) -> None:
        ...
    @typing.overload
    def __init__(self, tag: str, label: str) -> None:
        ...
    @typing.overload
    def __init__(self, tag: str, label: str, account_indices: list[int]) -> None:
        ...
class MoneroAddressBookEntry:
    """
    Monero address book entry model.
    """
    address: str | None
    description: str | None
    index: int | None
    payment_id: str | None
    @typing.overload
    def __init__(self) -> None:
        ...
    @typing.overload
    def __init__(self, index: int, address: str, description: str) -> None:
        ...
    @typing.overload
    def __init__(self, index: int, address: str, description: str, payment_id: str) -> None:
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
    """
    Models an alternative chain seen by the node.
    """
    block_hashes: list[str]
    difficulty: int | None
    height: int | None
    length: int | None
    main_chain_parent_block_hash: str | None
    def __init__(self) -> None:
        ...
class MoneroBan:
    """
     Monero banhammer.
    """
    host: str | None
    ip: int | None
    is_banned: bool | None
    seconds: int | None
    def __init__(self) -> None:
        ...
class MoneroBlock(MoneroBlockHeader):
    """
    Models a Monero block in the blockchain.
    """
    hex: str | None
    miner_tx: MoneroTx | None
    tx_hashes: list[str]
    txs: list[MoneroTx]
    def __init__(self) -> None:
        ...
    @typing.overload
    def copy(self, src: MoneroBlock, tgt: MoneroBlock) -> MoneroBlock:
        ...
    @typing.overload
    def copy(self, src: MoneroBlockHeader, tgt: MoneroBlockHeader) -> MoneroBlockHeader:
        ...
    @typing.overload
    def merge(self, _self: MoneroBlock, other: MoneroBlock) -> None:
        ...
    @typing.overload
    def merge(self, _self: MoneroBlockHeader, other: MoneroBlockHeader) -> None:
        ...
class MoneroBlockHeader(SerializableStruct):
    """
    Models a Monero block header which contains information about the block.
    """
    cumulative_difficulty: int | None
    depth: int | None
    difficulty: int | None
    hash: str | None
    height: int | None
    long_term_weight: int | None
    major_version: int | None
    miner_tx_hash: str | None
    minor_version: int | None
    nonce: int | None
    num_txs: int | None
    orphan_status: bool | None
    pow_hash: str | None
    prev_hash: str | None
    reward: int | None
    size: int | None
    timestamp: int | None
    weight: int | None
    def __init__(self) -> None:
        ...
    def copy(self, src: MoneroBlockHeader, tgt: MoneroBlockHeader) -> MoneroBlockHeader:
        ...
    def merge(self, _self: MoneroBlockHeader, other: MoneroBlockHeader) -> None:
        ...
class MoneroBlockTemplate:
    """
    Monero block template to mine.
    """
    block_hashing_blob: str | None
    block_template_blob: str | None
    difficulty: int | None
    expected_reward: int | None
    height: int | None
    next_seed_hash: str | None
    prev_hash: str | None
    reserved_offset: int | None
    seed_hash: str | None
    seed_height: int | None
    def __init__(self) -> None:
        ...
class MoneroCheck(SerializableStruct):
    """
    Base class for results from checking a transaction or reserve proof.
    """
    is_good: bool
    def __init__(self) -> None:
        ...
class MoneroCheckReserve(MoneroCheck):
    """
    Results from checking a reserve proof.
    """
    total_amount: int | None
    unconfirmed_spent_amount: int | None
    def __init__(self) -> None:
        ...
class MoneroCheckTx(MoneroCheck):
    """
    Results from checking a transaction key.
    """
    in_tx_pool: bool | None
    num_confirmations: int | None
    received_amount: int | None
    def __init__(self) -> None:
        ...
class MoneroConnectionManager:
    """
    Manages a collection of prioritized connections to daemon or wallet RPC endpoints.
    """
    def __init__(self) -> None:
        ...
    @typing.overload
    def add_connection(self, connection: MoneroRpcConnection) -> None:
        """
        Add a connection. The connection may have an elevated priority for this manager to use.
        
        :param connection: the connection to add
        """
        ...
    @typing.overload
    def add_connection(self, uri: str) -> None:
        """
        Add a connection URI.
        
        :param uri: uri of the connection to add
        """
        ...
    def add_listener(self, listener: MoneroConnectionManagerListener) -> None:
        """
        Add a listener to receive notifications when the connection changes.
        
        :param listener: the listener to add
        """
        ...
    def check_connection(self) -> None:
        """
        Check the current connection. If disconnected and auto switch enabled, switches to best available connection.
        """
        ...
    def check_connections(self) -> None:
        """
        Check all managed connections.
        """
        ...
    def clear(self) -> None:
        """
        Remove all connections.
        """
        ...
    def disconnect(self) -> None:
        """
        Disconnect from the current connection.
        """
        ...
    def get_auto_switch(self) -> bool:
        """
        Get if auto switch is enabled or disabled.
         
        :return: true if auto switch enabled, false otherwise
        """
        ...
    @typing.overload
    def get_best_available_connection(self, excluded_connections: set[MoneroRpcConnection]) -> MoneroRpcConnection:
        """
        Get the best available connection in order of priority then response time.

        :param excluded_connections: connections to be excluded from consideration (optional)
        :return: the best available connection in order of priority then response time, null if no connections available
        """
        ...
    @typing.overload
    def get_best_available_connection(self, excluded_connection: MoneroRpcConnection) -> MoneroRpcConnection:
        """
        Get the best available connection in order of priority then response time.

        :param excluded_connection: connection to be excluded from consideration (optional)
        :return: the best available connection in order of priority then response time, null if no connections available
        """
        ...
    @typing.overload
    def get_best_available_connection(self) -> MoneroRpcConnection:
        """
        Get the best available connection in order of priority then response time.

        :return: the best available connection in order of priority then response time, null if no connections available
        """
        ...
    def get_connection(self) -> MoneroRpcConnection:
        """
        Get the current connection.
        """
        ...
    def get_connection_by_uri(self, uri: str) -> MoneroRpcConnection:
        """
        Get a connection by URI.
        
        :param uri: URI of the connection to get
        :return: the connection with the URI or null if no connection with the URI exists
        """
        ...
    def get_connections(self) -> list[MoneroRpcConnection]:
        """
        Get all connections in order of current connection (if applicable), online status, priority, and name.
        """
        ...
    def get_listeners(self) -> list[MoneroConnectionManagerListener]:
        """
        Get all listeners.
        """
        ...
    def get_peer_connections(self) -> list[MoneroRpcConnection]:
        """
        Collect connectable peers of the managed connections.
        
        :return: connectable peers
        """
        ...
    def get_timeout(self) -> int:
        """
        Get the request timeout.
        
        :return: the request timeout before a connection is considered offline
        """
        ...
    def has_connection(self, uri: str) -> bool:
        """
        Indicates if this manager has a connection with the given URI.
         
        :param uri: URI of the connection to check
        :return: true if this manager has a connection with the given URI, false otherwise
        """
        ...
    def is_connected(self) -> bool:
        """
        Indicates if the connection manager is connected to a node.
         
        :return: true if the current connection is set, online, and not unauthenticated, null if unknown, false otherwise
        """
        ...
    def remove_connection(self, uri: str) -> None:
        """
        Remove a connection.
        
        :param uri: uri of the connection to remove
        """
        ...
    def remove_listener(self, listener: MoneroConnectionManagerListener) -> None:
        """
        Remove a listener.
        
        :param listener: the listener to remove
        """
        ...
    def remove_listeners(self) -> None:
        """
        Remove all listeners.
        """
        ...
    def reset(self) -> None:
        """
        Reset to default state.
        """
        ...
    def set_auto_switch(self, auto_switch: bool) -> None:
        """
        Automatically switch to the best available connection as connections are polled, based on priority, response time, and consistency.
         
        :param auto_switch: specifies if the connection should auto switch to a better connection
        """
        ...
    @typing.overload
    def set_connection(self, connection: MoneroRpcConnection | None) -> None:
        """
        Set the current connection.
        Replace connection if its URI was previously added. Otherwise add new connection.
        Notify if current connection changes.
        Does not check the connection.
        
        :param connection: is the connection to make current
        """
        ...
    @typing.overload
    def set_connection(self, uri: str) -> None:
        """
        Set the current connection without changing the credentials.
        Add new connection if URI not previously added.
        Notify if current connection changes.
        Does not check the connection.
        
        :param uri: identifies the connection to make current
        """
        ...
    def set_timeout(self, timeout_ms: int) -> None:
        """
        Set the maximum request time before a connection is considered offline.
         
        :param timeout_ms: is the timeout before a connection is considered offline
        """
        ...
    def start_polling(self, period_ms: int | None = None, auto_switch: bool | None = None, timeout_ms: int | None = None, poll_type: MoneroConnectionPollType | None = None, excluded_connections: list[MoneroRpcConnection] | None = None) -> None:
        """
        Start polling connections.
         
        :param period_ms: poll period in milliseconds (default 20s)
        :param auto_switch: specifies to automatically switch to the best connection (default true unless changed)
        :param timeout_ms: specifies the timeout to poll a single connection (default 5s unless changed)
        :param poll_type: one of PRIORITIZED (poll connections in order of priority until connected; default), CURRENT (poll current connection), or ALL (poll all connections)
        :param excluded_connections: connections excluded from being polled
        """
        ...
    def stop_polling(self) -> None:
        """
        Stop polling connections.
        """
        ...
class MoneroConnectionManagerListener:
    """
    Default connection manager listener which takes no action on notifications.
    """
    def __init__(self) -> None:
        ...
    def on_connection_changed(self, connection: MoneroRpcConnection) -> None:
        """
        Notified on connection change events.
         
        :param connection: the connection manager's current connection
        """
        ...
class MoneroConnectionPollType:
    """
    Members:
    
      PRIORITIZED
    
      CURRENT
    
      ALL
    
      UNDEFINED
    """
    ALL: typing.ClassVar[MoneroConnectionPollType]  # value = <MoneroConnectionPollType.ALL: 2>
    CURRENT: typing.ClassVar[MoneroConnectionPollType]  # value = <MoneroConnectionPollType.CURRENT: 1>
    PRIORITIZED: typing.ClassVar[MoneroConnectionPollType]  # value = <MoneroConnectionPollType.PRIORITIZED: 0>
    UNDEFINED: typing.ClassVar[MoneroConnectionPollType]  # value = <MoneroConnectionPollType.UNDEFINED: 3>
    __members__: typing.ClassVar[dict[str, MoneroConnectionPollType]]  # value = {'PRIORITIZED': <MoneroConnectionPollType.PRIORITIZED: 0>, 'CURRENT': <MoneroConnectionPollType.CURRENT: 1>, 'ALL': <MoneroConnectionPollType.ALL: 2>, 'UNDEFINED': <MoneroConnectionPollType.UNDEFINED: 3>}
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
class MoneroConnectionProriotyComparator:
    @staticmethod
    def compare(p1: int, p2: int) -> int:
        ...
class MoneroConnectionSpan:
    """
    Monero daemon connection span.
    """
    connection_id: str | None
    num_blocks: int | None
    rate: int | None
    remote_address: str | None
    size: int | None
    speed: int | None
    start_height: int | None
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
    """
    Monero daemon interface.
    """
    def __init__(self) -> None:
        ...
    def add_listener(self, listener: MoneroDaemonListener) -> None:
        """
        Register a listener to receive daemon notifications.
        
        :param: listener the listener to register
        """
        ...
    def check_for_update(self) -> MoneroDaemonUpdateCheckResult:
        """
        Check for update.
        
        :return: the result of the update check
        """
        ...
    @typing.overload
    def download_update(self) -> MoneroDaemonUpdateDownloadResult:
        """
        Download an update.
        
        :param path: is the path to download the update (optional)
        :return: the result of the update download
        """
        ...
    @typing.overload
    def download_update(self, download_path: str) -> MoneroDaemonUpdateDownloadResult:
        """
        Download an update.
        
        :return: the result of the update download
        """
        ...
    @typing.overload
    def flush_tx_pool(self) -> None:
        """
        Flush transactions from the tx pool.        
        """
        ...
    @typing.overload
    def flush_tx_pool(self, hashes: list[str]) -> None:
        """
        Flush transactions from the tx pool.
        
        :param hashes: are hashes of transactions to flush
        """
        ...
    def get_alt_block_hashes(self) -> list[str]:
        """
        Get known block hashes which are not on the main chain.
        
        :return: known block hashes which are not on the main chain
        """
        ...
    def get_alt_chains(self) -> list[MoneroAltChain]:
        """
        Get alternative chains seen by the node.
        
        :return: alternative chains seen by the node
        """
        ...
    def get_block_by_hash(self, hash: str) -> MoneroBlock:
        """
        Get a block by hash.
        
        :param block_hash: is the hash of the block to get
        :return: the block with the given hash
        """
        ...
    def get_block_by_height(self, height: int) -> MoneroBlock:
        """
        Get a block by height.
        
        :param height: is the height of the block to get
        :return: the block at the given height
        """
        ...
    def get_block_hash(self, height: int) -> str:
        """
        Get a block's hash by its height.
        
        :param height: is the height of the block hash to get
        :return: the block's hash at the given height
        """
        ...
    def get_block_hashes(self, block_hashes: list[str], start_height: int) -> list[str]:
        """
        Get block hashes as a binary request to the daemon.
        
        :param block_hashes: specify block hashes to fetch; first 10 blocks hash goes
                sequential, next goes in pow(2,n) offset, like 2, 4, 8, 16, 32, 64
                and so on, and the last one is always genesis block
        :param start_height: is the starting height of block hashes to return
        :return: the requested block hashes
        """
        ...
    def get_block_header_by_hash(self, hash: str) -> MoneroBlockHeader:
        """
        Get a block header by its hash.
        
        :param hash: is the hash of the block to get the header of
        :return: the block's header
        """
        ...
    def get_block_header_by_height(self, height: int) -> MoneroBlockHeader:
        """
        Get a block header by its height.
        
        :param height: is the height of the block to get the header of
        :return: the block's header
        """
        ...
    def get_block_headers_by_range(self, start_height: int, end_height: int) -> list[MoneroBlockHeader]:
        """
        Get block headers for the given range.
        
        :param start_height: is the start height lower bound inclusive (optional)
        :param end_height: is the end height upper bound inclusive (optional)
        :return: block headers in the given range
        """
        ...
    @typing.overload
    def get_block_template(self, wallet_address: str) -> MoneroBlockTemplate:
        """
        Get a block template for mining a new block.
        
        :param wallet_address: is the address of the wallet to receive miner transactions if block is successfully mined
        :param reserve_size: is the reserve size (optional)
        :return: a block template for mining a new block
        """
        ...
    @typing.overload
    def get_block_template(self, wallet_address: str, reserve_size: int) -> MoneroBlockTemplate:
        """
        Get a block template for mining a new block.
        
        :param wallet_address: is the address of the wallet to receive miner transactions if block is successfully mined
        :param reserve_size: is the reserve size (optional)
        :return: a block template for mining a new block
        """
        ...
    def get_blocks_by_hash(self, block_hashes: list[str], start_height: int, prune: bool) -> list[MoneroBlock]:
        """
        Get a block by hash.
        
        :param block_hash: is the hash of the block to get
        :return: the block with the given hash
        """
        ...
    def get_blocks_by_height(self, heights: list[int]) -> list[MoneroBlock]:
        """
        Get blocks at the given heights.
        
        :param heights: are the heights of the blocks to get
        :return: blocks at the given heights
        """
        ...
    def get_blocks_by_range(self, start_height: int, end_height: int) -> list[MoneroBlock]:
        """
        Get blocks in the given height range.
        
        :param start_height: is the start height lower bound inclusive (optional)
        :param end_height: is the end height upper bound inclusive (optional)
        :return: blocks in the given height range
        """
        ...
    @typing.overload
    def get_blocks_by_range_chunked(self, start_height: int, end_height: int) -> list[MoneroBlock]:
        """
        Get blocks in the given height range as chunked requests so that each request is
        not too big.
        
        :param start_height: is the start height lower bound inclusive (optional)
        :param end_height: is the end height upper bound inclusive (optional)
        :param max_chunk_size: is the maximum chunk size in any one request (default 3,000,000 bytes)
        :return: blocks in the given height range
        """
        ...
    @typing.overload
    def get_blocks_by_range_chunked(self, start_height: int, end_height: int, max_chunk_size: int) -> list[MoneroBlock]:
        """
        Get blocks in the given height range as chunked requests so that each request is
        not too big.
        
        :param start_height: is the start height lower bound inclusive (optional)
        :param end_height: is the end height upper bound inclusive (optional)
        :param max_chunk_size: is the maximum chunk size in any one request (default 3,000,000 bytes)
        :return: blocks in the given height range
        """
        ...
    def get_download_limit(self) -> int:
        """
        Get the download bandwidth limit.
        
        :return: is the download bandwidth limit
        """
        ...
    def get_fee_estimate(self, grace_blocks: int = 0) -> MoneroFeeEstimate:
        """
        Get mining fee estimates per kB.
        
        :param grace_blocks: TODO
        :return: mining fee estimates per kB
        """
        ...
    def get_hard_fork_info(self) -> MoneroHardForkInfo:
        """
        Look up information regarding hard fork voting and readiness.
        
        :return: hard fork information
        """
        ...
    def get_height(self) -> int:
        """
        Get the number of blocks in the longest chain known to the node.
        
        :return: the number of blocks
        """
        ...
    def get_info(self) -> MoneroDaemonInfo:
        """
        Get general information about the state of the node and the network.
        
        :return: general information about the node and network
        """
        ...
    def get_key_image_spent_status(self, key_image: str) -> MoneroKeyImageSpentStatus:
        """
        Get the spent status of the given key image.
        
        :param key_image: is key image hex to get the status of
        :return: the status of the key image
        """
        ...
    def get_key_image_spent_statuses(self, key_images: list[str]) -> list[MoneroKeyImageSpentStatus]:
        """
        Get the spent status of each given key image.
        
        :param key_images: are hex key images to get the statuses of
        :return: the spent status for each key image
        """
        ...
    def get_known_peers(self) -> list[MoneroPeer]:
        """
        Get all known peers including their last known online status.
        
        :return: the daemon's known peers
        """
        ...
    def get_last_block_header(self) -> MoneroBlockHeader:
        """
        Get the last block's header.
        
        :return: the last block's header
        """
        ...
    def get_listeners(self) -> list[MoneroDaemonListener]:
        """
        Get the listeners registered with the daemon.
        
        :return: the registered listeners
        """
        ...
    def get_miner_tx_sum(self, height: int, num_blocks: int) -> MoneroMinerTxSum:
        """
        Gets the total emissions and fees from the genesis block to the current height.
        
        :param height: is the height to start computing the miner sum
        :param num_blocks: are the number of blocks to include in the sum
        :return: the sum emission and fees since the geneis block
        """
        ...
    def get_mining_status(self) -> MoneroMiningStatus:
        """
        Get the daemon's mining status.
        
        :return: the daemon's mining status
        """
        ...
    @typing.overload
    def get_output_distribution(self, amounts: list[int]) -> list[MoneroOutputDistributionEntry]:
        """
        Creates an output distribution.
        
        :param amounts: are amounts of outputs to make the distribution with
        :return: output distribution entries meeting the parameters
        """
        ...
    @typing.overload
    def get_output_distribution(self, amounts: list[int], is_cumulative: bool, start_height: int, end_height: int) -> list[MoneroOutputDistributionEntry]:
        """
        Creates an output distribution.
        
        :param amounts: are amounts of outputs to make the distribution with
        :param is_cumulative: specifies if the results should be cumulative (defaults to TODO)
        :param start_height: is the start height lower bound inclusive (optional)
        :param end_height: is the end height upper bound inclusive (optional)
        :return: output distribution entries meeting the parameters
        """
        ...
    def get_output_histogram(self, amounts: list[int], min_count: int, max_count: int, is_unlocked: bool, recent_cutoff: int) -> list[MoneroOutputHistogramEntry]:
        """
        Get a histogram of output amounts. For all amounts (possibly filtered by
        parameters), gives the number of outputs on the chain for that amount.
        RingCT outputs counts as 0 amount.
        
        :param amounts: are amounts of outputs to make the histogram with
        :param min_count: TODO
        :param max_count: TODO
        :param is_unlocked: makes a histogram with outputs with the specified lock state
        :param recent_cutoff: TODO
        :return: output histogram entries meeting the parameters
        """
        ...
    def get_outputs(self, outputs: list[MoneroOutput]) -> list[MoneroOutput]:
        """
        Get outputs identified by a list of output amounts and indices as a binary
        request.
        
        :param outputs: identify each output by amount and index
        :return: the identified outputs
        """
        ...
    def get_peer_bans(self) -> list[MoneroBan]:
        """
        Get peer bans.
        
        :return: entries about banned peers
        """
        ...
    def get_peers(self) -> list[MoneroPeer]:
        """
        Get peers with active incoming or outgoing connections to the node.
        
        :return: the daemon's peers
        """
        ...
    def get_sync_info(self) -> MoneroDaemonSyncInfo:
        """
        Get synchronization information.
        
        :return: contains sync information
        """
        ...
    def get_tx(self, tx_hash: str, prune: bool = False) -> MoneroTx | None:
        """
        Get a transaction by hash.
        
        :param tx_hash: is the hash of the transaction to get
        :param prune: specifies if the returned tx should be pruned (defaults to false)
        :return: the transaction with the given hash or null if not found
        """
        ...
    def get_tx_hex(self, tx_hash: str, prune: bool = False) -> str | None:
        """
        Get a transaction hex by hash.
        
        :param tx_hash: is the hash of the transaction to get hex from
        :param prune: specifies if the returned tx hex should be pruned (defaults to false)
        :return: the tx hex with the given hash
        """
        ...
    def get_tx_hexes(self, tx_hashes: list[str], prune: bool = False) -> list[str]:
        """
        Get transaction hexes by hashes.
        
        :param tx_hashes: are hashes of transactions to get hexes from
        :return: are the tx hexes
        """
        ...
    def get_tx_pool(self) -> list[MoneroTx]:
        """
        Get valid transactions seen by the node but not yet mined into a block, as well
        as spent key image information for the tx pool.
        
        :return: transactions in the transaction pool
        """
        ...
    def get_tx_pool_backlog(self) -> list[MoneroTxBacklogEntry]:
        """
        Get all transaction pool backlog.
        
        :return: transaction pool backlog entries
        """
        ...
    def get_tx_pool_hashes(self) -> list[str]:
        """
        Get hashes of transactions in the transaction pool.
         
        :return: hashes of transactions in the transaction pool
        """
        ...
    def get_tx_pool_stats(self) -> MoneroTxPoolStats:
        """
        Get transaction pool statistics.
         
        :return: statistics about the transaction pool
        """
        ...
    def get_txs(self, tx_hashes: list[str], prune: bool = False) -> list[MoneroTx]:
        """
        Get transactions by hashes.
        
        :param tx_hashes: are hashes of transactions to get
        :return: found transactions with the given hashes
        """
        ...
    def get_upload_limit(self) -> int:
        """
        Get the upload bandwidth limit.
         
        :return: is the upload bandwidth limit
        """
        ...
    def get_version(self) -> MoneroVersion:
        """
        Gets the version of the daemon.
        
        :return: the version of the daemon
        """
        ...
    def is_trusted(self) -> bool:
        """
        Indicates if the daemon is trusted or untrusted.
        
        :return: true if the daemon is trusted, false otherwise
        """
        ...
    def prune_blockchain(self, check: bool) -> MoneroPruneResult:
        """
        Prune the blockchain.
        
        :param check specifies: to check the pruning (default false)
        :return: the prune result
        """
        ...
    def relay_tx_by_hash(self, tx_hash: str) -> None:
        """
        Relays a transaction by hash.
        
        :param tx_hash: identifies the transaction to relay
        """
        ...
    def relay_txs_by_hash(self, tx_hashes: list[str]) -> None:
        """
        Relays transactions by hash.
        
        :param tx_hashes: identify the transactions to relay
        """
        ...
    def remove_listener(self, listener: MoneroDaemonListener) -> None:
        """
        Unregister a listener to receive daemon notifications.
        
        :param listener: a previously registered listener to be unregistered
        """
        ...
    def reset_download_limit(self) -> int:
        """
        Reset the download bandwidth limit.
        
        :return: the download bandwidth limit after resetting
        """
        ...
    def reset_upload_limit(self) -> int:
        """
        Reset the upload bandwidth limit.
        
        :return: the upload bandwidth limit after resetting
        """
        ...
    def set_download_limit(self, limit: int) -> int:
        """
        Set the download bandwidth limit.
        
        :param limit: is the download limit to set (-1 to reset to default)
        :return: int is the new download limit after setting
        """
        ...
    def set_incoming_peer_limit(self, limit: int) -> None:
        """
        Limit number of incoming peers.
        
        :param limit: is the maximum number of incoming peers
        """
        ...
    def set_outgoing_peer_limit(self, limit: int) -> None:
        """
        Limit number of outgoing peers.
        
        :param limit: is the maximum number of outgoing peers
        """
        ...
    def set_peer_ban(self, ban: MoneroBan) -> None:
        """
        Ban a peer node.
        
        :param ban: contains information about a node to ban
        """
        ...
    def set_peer_bans(self, bans: list[MoneroBan]) -> None:
        """
        Ban peers nodes.
        
        :param bans: are bans to apply against peer nodes
        """
        ...
    def set_upload_limit(self, limit: int) -> int:
        """
        Set the upload bandwidth limit.
        
        :param limit: is the upload limit to set (-1 to reset to default)
        :return: int is the new upload limit after setting
        """
        ...
    def start_mining(self, address: str, num_threads: int, is_background: bool, ignore_battery: bool) -> None:
        """
        Start mining.
        
        :param address: is the address given miner rewards if the daemon mines a block
        :param num_threads: is the number of mining threads to run
        :param is_background: specifies if the miner should run in the background or not
        :param ignore_battery: specifies if the battery state (e.g. on laptop) should be ignored or not
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
        
        :param block_blob: is the mined block to submit
        """
        ...
    def submit_blocks(self, block_blobs: list[str]) -> None:
        """
        Submit mined blocks to the network.
         
        :param block_blobs: are the mined blocks to submit
        """
        ...
    def submit_tx_hex(self, tx_hex: str, do_not_relay: bool = False) -> MoneroSubmitTxResult:
        """
        Submits a transaction to the daemon's pool.
        
        :param tx_hex: is the raw transaction hex to submit
        :return: the submission results
        """
        ...
    def wait_for_next_block_header(self) -> MoneroBlockHeader:
        """
        Get the header of the next block added to the chain.

        :return: the header of the next block added to the chain
        """
        ...
class MoneroDaemonDefault(MoneroDaemon):
    """
    Base Monero daemon with default implementations.
    """
    def __init__(self) -> None:
        ...
class MoneroDaemonInfo:
    """
    Monero daemon info.
    """
    adjusted_timestamp: int | None
    block_size_limit: int | None
    block_size_median: int | None
    block_weight_limit: int | None
    block_weight_median: int | None
    bootstrap_daemon_address: str | None
    credits: int | None
    cumulative_difficulty: int | None
    database_size: int | None
    difficulty: int | None
    free_space: int | None
    height: int | None
    height_without_bootstrap: int | None
    is_busy_syncing: bool | None
    is_offline: bool | None
    is_restricted: bool | None
    is_synchronized: bool | None
    network_type: MoneroNetworkType | None
    num_alt_blocks: int | None
    num_incoming_connections: int | None
    num_offline_peers: int | None
    num_online_peers: int | None
    num_outgoing_connections: int | None
    num_rpc_connections: int | None
    num_txs: int | None
    num_txs_pool: int | None
    start_timestamp: int | None
    target: int | None
    target_height: int | None
    top_block_hash: str | None
    update_available: bool | None
    version: str | None
    was_bootstrap_ever_used: bool | None
    def __init__(self) -> None:
        ...
class MoneroDaemonListener:
    """
    Receives notifications as a daemon is updated.
    """
    last_header: MoneroBlockHeader
    def __init__(self) -> None:
        ...
    def on_block_header(self, header: MoneroBlockHeader) -> None:
        """
        Called when a new block is added to the chain.
        
        :param header: is the header of the block added to the chain
        """
        ...
class MoneroDaemonRpc(MoneroDaemonDefault):
    """
    Implements a Monero daemon using monerod.
    """
    @typing.overload
    def __init__(self) -> None:
        ...
    @typing.overload
    def __init__(self, rpc: MoneroRpcConnection) -> None:
        ...
    @typing.overload
    def __init__(self, uri: str, username: str = '', password: str = '') -> None:
        ...
    def get_rpc_connection(self) -> MoneroRpcConnection:
        """
        Get the daemon's RPC connection.
        
        :return: the daemon's rpc connection
        """
        ...
    def is_connected(self) -> bool:
        """
        Indicates if the client is connected to the daemon via RPC.
        
        :return: true if the client is connected to the daemon, false otherwise
        """
        ...
class MoneroDaemonSyncInfo:
    """
    Models daemon synchronization information.
    """
    credits: int | None
    height: int | None
    next_needed_pruning_seed: int | None
    overview: str | None
    peers: list[MoneroPeer]
    spans: list[MoneroConnectionSpan]
    target_height: int | None
    top_block_hash: str | None
    def __init__(self) -> None:
        ...
class MoneroDaemonUpdateCheckResult:
    """
    Models the result of checking for a daemon update.
    """
    auto_uri: str | None
    hash: str | None
    is_update_available: bool | None
    user_uri: str | None
    version: str | None
    def __init__(self) -> None:
        ...
class MoneroDaemonUpdateDownloadResult(MoneroDaemonUpdateCheckResult):
    """
    Models the result of downloading an update.
    """
    download_path: str | None
    def __init__(self) -> None:
        ...
class MoneroDecodedAddress:
    """
    Maintains metadata for a decoded address.
    """
    address: str
    address_type: MoneroAddressType
    network_type: MoneroNetworkType
    def __init__(self, address: str, address_type: MoneroAddressType, network_type: MoneroNetworkType) -> None:
        ...
class MoneroDestination:
    """
    Models an outgoing transfer destination.
    """
    address: str | None
    amount: int | None
    @typing.overload
    def __init__(self) -> None:
        ...
    @typing.overload
    def __init__(self, address: str) -> None:
        ...
    @typing.overload
    def __init__(self, address: str, amount: int) -> None:
        ...
    def copy(self, src: MoneroDestination, tgt: MoneroDestination) -> MoneroDestination:
        ...
class MoneroError(Exception):
    """
    Monero exception.
    """
    pass
class MoneroFeeEstimate:
    """
    Models a Monero fee estimate.
    """
    fee: int | None
    fees: list[int]
    quantization_mask: int | None
    def __init__(self) -> None:
        ...
class MoneroHardForkInfo:
    """
    Monero hard fork info.
    """
    credits: int | None
    earliest_height: int | None
    is_enabled: bool | None
    num_votes: int | None
    state: int | None
    threshold: int | None
    top_block_hash: str | None
    version: int | None
    voting: int | None
    window: int | None
    def __init__(self) -> None:
        ...
class MoneroIncomingTransfer(MoneroTransfer):
    """
    Models an incoming transfer of funds to the wallet.
    """
    address: str | None
    num_suggested_confirmations: int | None
    subaddress_index: int | None
    def __init__(self) -> None:
        ...
    @typing.overload
    def copy(self, src: MoneroIncomingTransfer, tgt: MoneroIncomingTransfer) -> MoneroIncomingTransfer:
        ...
    @typing.overload
    def copy(self, src: MoneroTransfer, tgt: MoneroTransfer) -> MoneroIncomingTransfer:
        ...
    @typing.overload
    def merge(self, _self: MoneroIncomingTransfer, other: MoneroIncomingTransfer) -> None:
        ...
    @typing.overload
    def merge(self, _self: MoneroTransfer, other: MoneroTransfer) -> None:
        ...
class MoneroIntegratedAddress(SerializableStruct):
    """
    Monero integrated address model.
    """
    integrated_address: str
    payment_id: str
    standard_address: str
    def __init__(self) -> None:
        ...
class MoneroJsonRequest(MoneroRequest):
    """
    Models a Monero JSON-RPC request.
    """
    id: str | None
    params: MoneroJsonRequestParams | None
    version: str | None
    @typing.overload
    def __init__(self) -> None:
        ...
    @typing.overload
    def __init__(self, request: MoneroJsonRequest) -> None:
        ...
    @typing.overload
    def __init__(self, method: str) -> None:
        ...
    @typing.overload
    def __init__(self, method: str, params: MoneroJsonRequestParams) -> None:
        ...
class MoneroJsonRequestEmptyParams(MoneroJsonRequestParams):
    """
    Empty Monero JSON-RPC request parameters.
    """
    def __init__(self) -> None:
        ...
class MoneroJsonRequestParams(SerializableStruct):
    """
    Models a Monero JSON-RPC request parameters.
    """
    def __init__(self) -> None:
        ...
class MoneroJsonResponse:
    """
    Models a Monero JSON-RPC response.
    """
    id: str | None
    jsonrpc: str | None
    @staticmethod
    def deserialize(response_json: str) -> MoneroJsonResponse:
        ...
    @typing.overload
    def __init__(self) -> None:
        ...
    @typing.overload
    def __init__(self, response: MoneroJsonResponse) -> None:
        ...
    def get_result(self) -> typing.Any | None:
        ...
class MoneroKeyImage(SerializableStruct):
    """
    Models a Monero key image.
    """
    hex: str | None
    signature: str | None
    @staticmethod
    def deserialize_key_images(key_images_json: str) -> list[MoneroKeyImage]:
        ...
    def __init__(self) -> None:
        ...
    def copy(self, src: MoneroKeyImage, tgt: MoneroKeyImage) -> MoneroKeyImage:
        ...
    def merge(self, _self: MoneroKeyImage, other: MoneroKeyImage) -> None:
        ...
class MoneroKeyImageImportResult(SerializableStruct):
    """
    Models results from importing key images.
    """
    height: int | None
    spent_amount: int | None
    unspent_amount: int | None
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
    """
    Models results from message verification.
    """
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
    """
    Model for the summation of miner emissions and fees.
    """
    emission_sum: int | None
    fee_sum: int | None
    def __init__(self) -> None:
        ...
class MoneroMiningStatus:
    """
    Monero daemon mining status.
    """
    address: str | None
    is_active: bool | None
    is_background: bool | None
    num_threads: int | None
    speed: int | None
    def __init__(self) -> None:
        ...
class MoneroMultisigInfo:
    """
    Models information about a multisig wallet.
    """
    is_multisig: bool
    is_ready: bool
    num_participants: int
    threshold: int
    def __init__(self) -> None:
        ...
class MoneroMultisigInitResult:
    """
    Models the result of initializing a multisig wallet which results in the
    multisig wallet's address xor another multisig hex to share with
    participants to create the wallet.
    """
    address: str | None
    multisig_hex: str | None
    def __init__(self) -> None:
        ...
class MoneroMultisigSignResult:
    """
    Models the result of signing multisig tx hex.
    """
    signed_multisig_tx_hex: str | None
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
    """
    Models an outgoing transfer of funds from the wallet.
    """
    addresses: list[str]
    destinations: list[MoneroDestination]
    subaddress_indices: list[int]
    def __init__(self) -> None:
        ...
    @typing.overload
    def copy(self, src: MoneroOutgoingTransfer, tgt: MoneroIncomingTransfer) -> MoneroOutgoingTransfer:
        ...
    @typing.overload
    def copy(self, src: MoneroTransfer, tgt: MoneroTransfer) -> MoneroOutgoingTransfer:
        ...
    @typing.overload
    def merge(self, _self: MoneroOutgoingTransfer, other: MoneroOutgoingTransfer) -> None:
        ...
    @typing.overload
    def merge(self, _self: MoneroTransfer, other: MoneroTransfer) -> None:
        ...
class MoneroOutput(SerializableStruct):
    """
    Models a Monero transaction output.
    """
    amount: int | None
    index: int | None
    key_image: MoneroKeyImage | None
    ring_output_indices: list[int]
    stealth_public_key: str | None
    tx: MoneroTx
    def __init__(self) -> None:
        ...
    def copy(self, src: MoneroOutput, tgt: MoneroOutput) -> MoneroOutput:
        ...
    def merge(self, _self: MoneroOutput, other: MoneroOutput) -> None:
        ...
class MoneroOutputDistributionEntry:
    """
    Models a Monero output distribution entry.
    """
    amount: int | None
    base: int | None
    distribution: list[int]
    start_height: int | None
    def __init__(self) -> None:
        ...
class MoneroOutputHistogramEntry:
    """
    Models a Monero output histogram entry.
    """
    amount: int | None
    num_instances: int | None
    recent_instances: int | None
    unlocked_instances: int | None
    def __init__(self) -> None:
        ...
class MoneroOutputQuery(MoneroOutputWallet):
    """
    Configures a query to retrieve wallet outputs (i.e. outputs that the wallet has or had the
    ability to spend).
   
    All outputs are returned except those that do not meet the criteria defined in this query.
    """
    max_amount: int | None
    min_amount: int | None
    subaddress_indices: list[int]
    tx_query: MoneroTxQuery | None
    @staticmethod
    def deserialize_from_block(output_query_json: str) -> MoneroOutputQuery:
        ...
    def __init__(self) -> None:
        ...
    @typing.overload
    def copy(self, src: MoneroOutputQuery, tgt: MoneroOutputQuery) -> MoneroOutputQuery:
        ...
    @typing.overload
    def copy(self, src: MoneroOutputWallet, tgt: MoneroOutputWallet) -> MoneroOutputQuery:
        ...
    @typing.overload
    def copy(self, src: MoneroOutput, tgt: MoneroOutput) -> MoneroOutputQuery: # type: ignore
        ...
    def meets_criteria(self, output: MoneroOutputWallet, query_parent: bool = True) -> bool:
        ...
class MoneroOutputWallet(MoneroOutput):
    """
    Models a Monero output with wallet extensions.
    """
    account_index: int | None
    is_frozen: bool | None
    is_spent: bool | None
    subaddress_index: int | None
    def __init__(self) -> None:
        ...
    @typing.overload
    def copy(self, src: MoneroOutputWallet, tgt: MoneroOutputWallet) -> MoneroOutputWallet:
        ...
    @typing.overload
    def copy(self, src: MoneroOutput, tgt: MoneroOutput) -> MoneroOutputWallet:
        ...
    @typing.overload
    def merge(self, _self: MoneroOutputWallet, other: MoneroOutputWallet) -> None:
        ...
    @typing.overload
    def merge(self, _self: MoneroOutput, other: MoneroOutput) -> None:
        ...
class MoneroPathRequest(MoneroRequest):
    """
    Models a Monero RPC request.
    """
    def __init__(self) -> None:
        ...
class MoneroPeer:
    """
    Models a peer to the daemon.
    """
    address: str | None
    avg_download: int | None
    avg_upload: int | None
    connection_type: MoneroConnectionType | None
    current_download: int | None
    current_upload: int | None
    hash: str | None
    height: int | None
    host: str | None
    id: str | None
    is_incoming: bool | None
    is_local_host: bool | None
    is_local_ip: bool | None
    is_online: bool | None
    last_seen_timestamp: int | None
    live_time: int | None
    num_receives: int | None
    num_sends: int | None
    num_support_flags: int | None
    port: int | None
    pruning_seed: int | None
    receive_idle_time: int | None
    rpc_credits_per_hash: int | None
    rpc_port: int | None
    send_idle_time: int | None
    state: str | None
    def __init__(self) -> None:
        ...
class MoneroPruneResult:
    """
    Result of pruning the blockchain.
    """
    is_pruned: bool | None
    pruning_seed: int | None
    def __init__(self) -> None:
        ...
class MoneroRequest(SerializableStruct):
    """
    Models a Monero HTTP request.
    """
    method: str | None
    def __init__(self) -> None:
        ...
class MoneroRpcConnection:
    """
    Models a connection to a daemon.
    """
    password: str | None
    priority: int
    proxy: str | None
    response_time: int | None
    timeout: int
    uri: str | None
    username: str | None
    zmq_uri: str | None
    @staticmethod
    def compare(c1: MoneroRpcConnection, c2: MoneroRpcConnection, current_connection: MoneroRpcConnection) -> int:
        ...
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
    def send_json_request(self, method: str, parameters: object | None = None) -> object:
        ...
    def send_path_request(self, method: str, parameters: object | None = None) -> object:
        ...
    def send_binary_request(self, method: str, parameters: object | None = None) -> object:
        ...
    def set_attribute(self, key: str, value: str) -> None:
        ...
    def set_credentials(self, username: str, password: str) -> None:
        ...
class MoneroRpcError(RuntimeError):
    """
    Exception when interacting with the Monero daemon or wallet RPC API.
    """
    def __init__(self, code: int, aMessage: str):
        ...
    def get_code(self) -> int:
        """
        JSON-RPC error code.
        """
        ...
    def get_message(self) -> str:
        """
        JSON-RPC error message.
        """
        ...
class MoneroSubaddress(SerializableStruct):
    """
    Models a Monero subaddress.
    """
    account_index: int | None
    address: str | None
    balance: int | None
    index: int | None
    is_used: bool | None
    label: str | None
    num_blocks_to_unlock: int | None
    num_unspent_outputs: int | None
    unlocked_balance: int | None
    def __init__(self) -> None:
        ...
class MoneroSubmitTxResult:
    """
    Models the result from submitting a tx to a daemon.
    """
    credits: int | None
    has_invalid_input: bool | None
    has_invalid_output: bool | None
    has_too_few_outputs: bool | None
    is_double_spend: bool | None
    is_fee_too_low: bool | None
    is_good: bool | None
    is_mixin_too_low: bool | None
    is_nonzero_unlock_time: bool | None
    is_overspend: bool | None
    is_relayed: bool | None
    is_too_big: bool | None
    is_tx_extra_too_big: bool | None
    reason: str | None
    sanity_check_failed: bool | None
    top_block_hash: str | None
    def __init__(self) -> None:
        ...
class MoneroSyncResult(SerializableStruct):
    """
    Models a result of syncing a wallet.
    """
    num_blocks_fetched: int
    received_money: bool
    @typing.overload
    def __init__(self) -> None:
        ...
    @typing.overload
    def __init__(self, num_blocks_fetched: int, received_money: bool) -> None:
        ...
class MoneroTransfer:
    """
    Models a base transfer of funds to or from the wallet.
    """
    account_index: int | None
    amount: int | None
    tx: MoneroTxWallet
    def __init__(self) -> None:
        ...
    def copy(self, src: MoneroTransfer, tgt: MoneroTransfer) -> MoneroTransfer:
        ...
    def is_incoming(self) -> bool | None:
        ...
    def is_outgoing(self) -> bool | None:
        ...
    def merge(self, _self: MoneroTransfer, other: MoneroTransfer) -> None:
        ...
class MoneroTransferQuery(MoneroTransfer):
    """
    Configures a query to retrieve transfers.
    
    All transfers are returned except those that do not meet the criteria defined in this query.
    """
    address: int | None
    addresses: list[str]
    destinations: list[MoneroDestination]
    has_destinations: bool | None
    incoming: bool | None
    subaddress_indices: list[int]
    tx_query: MoneroTxQuery | None
    @staticmethod
    def deserialize_from_block(transfer_query_json: str) -> MoneroTransferQuery:
        ...
    def __init__(self) -> None:
        ...
    @typing.overload
    def copy(self, src: MoneroTransferQuery, tgt: MoneroTransferQuery) -> MoneroTransferQuery:
        ...
    @typing.overload
    def copy(self, src: MoneroTransfer, tgt: MoneroTransfer) -> MoneroTransferQuery:
        ...
    def meets_criteria(self, transfer: MoneroTransferQuery, query_parent: bool = True) -> bool:
        ...
class MoneroTx(SerializableStruct):
    """
    Models a Monero transaction on the blockchain.
    """
    block: MoneroBlock | None
    common_tx_sets: str | None
    extra: list[int]
    fee: int | None
    full_hex: str | None
    hash: str | None
    in_tx_pool: bool | None
    inputs: list[MoneroOutput]
    is_confirmed: bool | None
    is_double_spend_seen: bool | None
    is_failed: bool | None
    is_kept_by_block: bool | None
    is_miner_tx: bool | None
    is_relayed: bool | None
    key: str | None
    last_failed_hash: str | None
    last_failed_height: int | None
    last_relayed_timestamp: int | None
    max_used_block_hash: str | None
    max_used_block_height: int | None
    metadata: str | None
    num_confirmations: int | None
    output_indices: list[int]
    outputs: list[MoneroOutput]
    payment_id: str | None
    prunable_hash: str | None
    prunable_hex: str | None
    pruned_hex: str | None
    rct_sig_prunable: str | None
    rct_signatures: str | None
    received_timestamp: int | None
    relay: bool | None
    ring_size: int | None
    signatures: list[str]
    size: int | None
    unlock_time: int | None
    version: int | None
    weight: int | None
    def __init__(self) -> None:
        ...
    def copy(self, src: MoneroTx, tgt: MoneroTx) -> MoneroTx:
        ...
    def get_height(self) -> int | None:
        ...
    def merge(self, _self: MoneroTx, other: MoneroTx) -> None:
        ...
class MoneroTxBacklogEntry:
    def __init__(self) -> None:
        ...
class MoneroTxConfig(SerializableStruct):
    """
    Configures a transaction to send, sweep, or create a payment URI.
    """
    account_index: int | None
    address: str | None
    amount: int | None
    below_amount: int | None
    can_split: bool | None
    destinations: list[MoneroDestination]
    fee: int | None
    key_image: str | None
    note: str | None
    payment_id: str | None
    priority: MoneroTxPriority | None
    recipient_name: str | None
    relay: bool | None
    ring_size: int | None
    subaddress_indices: list[int]
    subtract_fee_from: list[int]
    sweep_each_subaddress: bool | None
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
    """
    Models transaction pool statistics.
    """
    bytes_max: int | None
    bytes_med: int | None
    bytes_min: int | None
    bytes_total: int | None
    fee_total: int | None
    histo98pc: int | None
    num10m: int | None
    num_double_spends: int | None
    num_failing: int | None
    num_not_relayed: int | None
    num_txs: int | None
    oldest_timestamp: int | None
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
    """
    Configures a query to retrieve transactions.
   
    All transactions are returned except those that do not meet the criteria defined in this query.
    """
    has_payment_id: bool | None
    hashes: list[str]
    height: int | None
    include_outputs: int | None
    input_query: MoneroOutputQuery | None
    is_incoming: bool | None
    is_outgoing: bool | None
    max_height: int | None
    min_height: int | None
    output_query: MoneroOutputQuery | None
    payment_ids: list[str]
    transfer_query: MoneroTransferQuery | None
    @staticmethod
    def deserialize_from_block(tx_query_json: str) -> MoneroTxQuery:
        ...
    def __init__(self) -> None:
        ...
    @typing.overload
    def copy(self, src: MoneroTxQuery, tgt: MoneroTxQuery) -> MoneroTxQuery:
        ...
    @typing.overload
    def copy(self, src: MoneroTxWallet, tgt: MoneroTxWallet) -> MoneroTxQuery:
        ...
    @typing.overload
    def copy(self, src: MoneroTx, tgt: MoneroTx) -> MoneroTxQuery: # type: ignore
        ...
    def meets_criteria(self, tx: MoneroTxWallet, query_children: bool = False) -> bool:
        ...
class MoneroTxSet(SerializableStruct):
    """
    Groups transactions who share common hex data which is needed in order to
    sign and submit the transactions.

    For example, multisig transactions created from create_txs() share a common
    hex string which is needed in order to sign and submit the multisig
    transactions.
    """
    multisig_tx_hex: str | None
    signed_tx_hex: str | None
    txs: list[MoneroTxWallet]
    unsigned_tx_hex: str | None
    @staticmethod
    def deserialize(tx_set_json: str) -> MoneroTxSet:
        ...
    def __init__(self) -> None:
        ...
class MoneroTxWallet(MoneroTx):
    """
    Models a Monero transaction in the context of a wallet.
    """
    change_address: str | None
    change_amount: int | None
    extra_hex: str | None
    incoming_transfers: list[MoneroIncomingTransfer]
    input_sum: int | None
    is_incoming: bool | None
    is_locked: bool | None
    is_outgoing: bool | None
    note: str | None
    num_dummy_outputs: int | None
    outgoing_transfer: MoneroOutgoingTransfer | None
    output_sum: int | None
    tx_set: MoneroTxSet | None
    def __init__(self) -> None:
        ...
    @typing.overload
    def copy(self, src: MoneroTxWallet, tgt: MoneroTxWallet) -> MoneroTxWallet:
        ...
    @typing.overload
    def copy(self, src: MoneroTx, tgt: MoneroTx) -> MoneroTxWallet:
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
    @typing.overload
    def merge(self, _self: MoneroTxWallet, tgt: MoneroTxWallet) -> None:
        ...
    @typing.overload
    def merge(self, _self: MoneroTx, tgt: MoneroTx) -> None: # type: ignore
        ...
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
    def binary_to_dict(bin: bytes) -> dict:
        ...
    @staticmethod
    def binary_to_json(bin: bytes) -> str:
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
    def dict_to_binary(dictionary: dict) -> bytes:
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
class MoneroVersion(SerializableStruct):
    """
    Models a Monero version.
    """
    is_release: bool | None
    number: int | None
    def __init__(self) -> None:
        ...
class MoneroWallet:
    """
    Base wallet with default implementations.
    """
    def __init__(self) -> None:
        ...
    def add_address_book_entry(self, address: str, description: str) -> int:
        """
        Add an address book entry.

        :param address: is the entry address
        :param description: is the entry description (optional)
        :return: the index of the added entry
        """
        ...
    def add_listener(self, listener: MoneroWalletListener) -> None:
        """
        Register a listener receive wallet notifications.

        :param listener: is the listener to receive wallet notifications
        """
        ...
    def change_password(self, old_password: str, new_password: str) -> None:
        """
        Change the wallet password.

        :param old_password: is the wallet's old password
        :param new_password: is the wallet's new password
        """
        ...
    def check_reserve_proof(self, address: str, message: str, signature: str) -> MoneroCheckReserve:
        """
        Proves a wallet has a disposable reserve using a signature.

        :param address: is the public wallet address
        :param message: is a message included with the signature to further authenticate the proof (optional)
        :param signature: is the reserve proof signature to check
        :return: the result of checking the signature proof
        """
        ...
    def check_spend_proof(self, tx_hash: str, message: str, signature: str) -> bool:
        """
        Prove a spend using a signature. Unlike proving a transaction, it does not require the destination public address.

        :param tx_hash: specifies the transaction to prove
        :param message: is a message included with the signature to further authenticate the proof (optional)
        :param signature: is the transaction signature to confirm
        :return: true if the signature is good, false otherwise
        """
        ...
    def check_tx_key(self, tx_hash: str, tx_key: str, address: str) -> MoneroCheckTx:
        """
        Check a transaction in the blockchain with its secret key.

        :param tx_hash: specifies the transaction to check
        :param tx_key: is the transaction's secret key
        :param address: is the destination public address of the transaction
        :return: the result of the check
        """
        ...
    def check_tx_proof(self, tx_hash: str, address: str, message: str, signature: str) -> MoneroCheckTx:
        """
        Prove a transaction by checking its signature.

        :param tx_hash: specifies the transaction to prove
        :param address: is the destination public address of the transaction
        :param message: is a message included with the signature to further authenticate the proof (optional)
        :param signature: is the transaction signature to confirm
        :return: the result of the check
        """
        ...
    def close(self, save: bool = False) -> None:
        """
        Optionally save then close the wallet.

        :param save: specifies if the wallet should be saved before being closed (default false)
        """
        ...
    def create_account(self, label: str = '') -> MoneroAccount:
        """
        Create a new account with a label for the first subaddress.

        :param label: specifies the label for the account's first subaddress (optional)

        :return: the created account
        """
        ...
    def create_subaddress(self, account_idx: int, label: str = '') -> MoneroSubaddress:
        """
        Create a subaddress within an account.

        :param account_idx: specifies the index of the account to create the subaddress within
        :param label: specifies the the label for the subaddress (defaults to empty std::string)
        :return: the created subaddress
        """
        ...
    def create_tx(self, config: MoneroTxConfig) -> MoneroTxWallet:
        """
        Create a transaction to transfer funds from this wallet.

        :param config: configures the transaction to create
        :return: the created transaction (free memory using monero_utils::free)
        """
        ...
    def create_txs(self, config: MoneroTxConfig) -> list[MoneroTxWallet]:
        """
        Create one or more transactions to transfer funds from this wallet.

        :param config: configures the transactions to create
        :return: the created transactions (free memory using monero_utils::free)
        """
        ...
    def decode_integrated_address(self, integrated_address: str) -> MoneroIntegratedAddress:
        """
        Decode an integrated address to get its standard address and payment id.

        :param integrated_address: is an integrated address to decode
        
        :return: the decoded integrated address including standard address and payment id
        """
        ...
    def delete_address_book_entry(self, index: int) -> None:
        """
        Delete an address book entry.

        :param index: is the index of the entry to delete
        """
        ...
    def describe_tx_set(self, tx_set: MoneroTxSet) -> MoneroTxSet:
        """
        Describes a tx set containing unsigned or multisig tx hex to a new tx set containing structured transactions.

        :param tx_set: is a tx set containing unsigned or multisig tx hex
        :return: the tx set containing structured transactions
        """
        ...
    def edit_address_book_entry(self, index: int, set_address: bool, address: str, set_description: bool, description: str) -> None:
        """
        Edit an address book entry.

        :param index: is the index of the address book entry to edit
        :param set_address: specifies if the address should be updated
        :param address: is the updated address
        :param set_description: specifies if the description should be updated
        :param description: is the updated description
        """
        ...
    def exchange_multisig_keys(self, mutisig_hexes: list[str], password: str) -> MoneroMultisigInitResult:
        """
        Exchange multisig hex with participants in a M/N multisig wallet.

        This process must be repeated with participants exactly N-M times.

        :param multisig_hexes: are multisig hex from each participant
        :param password: is the wallet's password // TODO monero-project: redundant? wallet is created with password
        :return: the result which has the multisig's address xor this wallet's multisig hex to share with participants iff not done
        """
        
        ...
    def export_key_images(self, all: bool = False) -> list[MoneroKeyImage]:
        """
        Export signed key images.

        :param all: export all key images if true, else export key images since the last export
        :return: the wallet's signed key images
        """
        ...
    def export_multisig_hex(self) -> str:
        """
        Export this wallet's multisig info as hex for other participants.

        :return: this wallet's multisig info as hex for other participants
        """
        ...
    def export_outputs(self, all: bool = False) -> str:
        """
        Export outputs in hex format.

        :param all: export all outputs if true, else export outputs since the last export
        :return: outputs in hex format, empty string if no outputs
        """
        ...
    def freeze_output(self, key_image: str) -> None:
        """
        Freeze an output.

        :param key_image: key image of the output to freeze
        """
        ...
    @typing.overload
    def get_account(self, account_idx: int) -> MoneroAccount:
        """
        Get an account without subaddress information.

        :param account_idx: specifies the account to get
        :return: the retrieved account
        """
        ...
    @typing.overload
    def get_account(self, account_idx: int, include_subaddresses: bool) -> MoneroAccount:
        """
        Get an account.

        :param account_idx: specifies the account to get
        :param include_subaddresses: specifies if subaddresses should be included
        :return: the retrieved account
        """
        ...
    def get_account_tags(self) -> list[MoneroAccountTag]:
        """
        Return all account tags.
        
        :return: the wallet's account tags
        """
        ...
    @typing.overload
    def get_accounts(self) -> list[MoneroAccount]:
        """
        Get all accounts.

        :return: all accounts within the wallet
        """
        ...
    @typing.overload
    def get_accounts(self, include_subaddresses: bool) -> list[MoneroAccount]:
        """
        Get all accounts.

        :param include_subaddresses: specifies if subaddresses should be included

        :return: all accounts within the wallet
        """
        ...
    @typing.overload
    def get_accounts(self, tag: str) -> list[MoneroAccount]:
        """
        Get all accounts.

        :param tag: is the tag for filtering accounts, all accounts if null

        :return: all accounts for the wallet with the given tag
        """
        ...
    @typing.overload
    def get_accounts(self, include_subaddresses: bool, tag: str) -> list[MoneroAccount]:
        """
        Get all accounts.

        :param include_subaddresses: specifies if subaddresses should be included
        :param tag: is the tag for filtering accounts, all accounts if null
        :return: all accounts for the wallet with the given tag
        """
        ...
    def get_address(self, account_idx: int, subaddress_idx: int) -> str:
        """
        Get the address of a specific subaddress.

        :param account_idx: specifies the account index of the address's subaddress
        :param subaddress_idx: specifies the subaddress index within the account
        :return: the receive address of the specified subaddress
        """
        ...
    def get_address_book_entries(self, indices: list[int]) -> list[MoneroAddressBookEntry]:
        """
        Get all address book entries.

        :param: indices are indices of the entries to get
        :return: the address book entries
        """
        ...
    def get_address_index(self, address: str) -> MoneroSubaddress:
        """
        Get the account and subaddress index of the given address.

        :param address: is the address to get the account and subaddress index from
        :return: the account and subaddress indices
        :raise MoneroError: exception if address is not a wallet address
        """
        ...
    def get_attribute(self, key: str, val: str) -> bool:
        """
        Get an attribute.

        :param key: is the attribute to get the value of
        :param value: is set to the key's value if set
        :return: true if the key's value has been set, false otherwise
        """
        ...
    @typing.overload
    def get_balance(self) -> int:
        """
        Get the wallet's balance.
        
        :return: the wallet's balance
        """
        ...
    @typing.overload
    def get_balance(self, account_idx: int) -> int:
        """
        Get an account's balance.

        :param account_idx: is the index of the account to get the balance of
        :return: the account's balance
        """
        ...
    @typing.overload
    def get_balance(self, account_idx: int, subaddress_idx: int) -> int:
        """
        Get a subaddress's balance.

        :param account_idx: is the index of the subaddress's account to get the balance of
        :param subaddress_idx: is the index of the subaddress to get the balance of
        :return: the subaddress's balance
        """
        ...
    def get_connection_manager(self) -> MoneroConnectionManager | None:
        """
        Get the wallet's daemon connection manager.
        
        :return: the wallet's daemon connection manager
        """
        ...
    def get_daemon_connection(self) -> MoneroRpcConnection | None:
        """
        Get the wallet's daemon connection.

        :return: the wallet's daemon connection
        """
        ...
    def get_daemon_height(self) -> int:
        """
        Get the height that the wallet's daemon is synced to.

        :return: the height that the wallet's daemon is synced to
        """
        ...
    def get_daemon_max_peer_height(self) -> int:
        """
        Get the maximum height of the peers the wallet's daemon is connected to.

        :return: the maximum height of the peers the wallet's daemon is connected to
        """
        ...
    def get_default_fee_priority(self) -> MoneroTxPriority:
        """
        Get the current default fee priority (unimportant, normal, elevated, etc).

        :return: the current fee priority
        """
        ...
    def get_height(self) -> int:
        """
        Get the height of the last block processed by the wallet (its index + 1).

        :return: the height of the last block processed by the wallet
        """
        ...
    def get_height_by_date(self, year: int, month: int, day: int) -> int:
        """
        Get the blockchain's height by date as a conservative estimate for scanning.
         
        :param year: year of the height to get
        :param month: month of the height to get as a number between 1 and 12
        :param day: day of the height to get as a number between 1 and 31

        :return: the blockchain's approximate height at the given date
        """
        ...
    def get_integrated_address(self, standard_address: str = '', payment_id: str = '') -> MoneroIntegratedAddress:
        """
        Get an integrated address from a standard address and a payment id.

        :param standard_address: is the integrated addresse's standard address (defaults to wallet's primary address)
        :param payment_id: is the integrated addresse's payment id (defaults to randomly generating new payment id)
        
        :return: the integrated address
        """
        ...
    def get_listeners(self) -> list[MoneroWalletListener]:
        """
        Get the listeners registered with the wallet.

        :return: List of listener registered with the wallet
        """
        ...
    def get_multisig_info(self) -> MoneroMultisigInfo:
        """
        Get multisig info about this wallet.

        :return: multisig info about this wallet
        """
        ...
    def get_network_type(self) -> MoneroNetworkType:
        """
        Get the wallet's network type (mainnet, testnet, or stagenet).

        :return: the wallet's network type
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

        :param query: specifies query options (optional)
        :return: wallet outputs per the query (free memory using monero_utils::free)
        """
        ...
    def get_path(self) -> str:
        """
        Get the path of this wallet's file on disk.

        :return: the path of this wallet's file on disk
        """
        ...
    def get_payment_uri(self, config: MoneroTxConfig) -> str:
        """
        Creates a payment URI from a tx configuration.

        :param config: specifies configuration for a potential tx
        :return: is the payment uri
        """
        ...
    def get_primary_address(self) -> str:
        """
        Get the wallet's primary address.

        :return: the wallet's primary address
        """
        ...
    def get_private_spend_key(self) -> str:
        """
        Get the wallet's private spend key.

        :return: the wallet's private spend key
        """
        ...
    def get_private_view_key(self) -> str:
        """
        Get the wallet's private view key.

        :return: the wallet's private view key
        """
        ...
    def get_public_spend_key(self) -> str:
        """
        Get the wallet's public spend key.

        :return: the wallet's public spend key
        """
        ...
    def get_public_view_key(self) -> str:
        """
        Get the wallet's public view key.

        :return: the wallet's public view key
        """
        ...
    def get_reserve_proof_account(self, account_idx: int, amount: int, message: str) -> str:
        """
        Generate a signature to prove an available amount in an account.

        :param account_idx: specifies the account to prove ownership of the amount
        :param amount: is the minimum amount to prove as available in the account
        :param message: is a message to include with the signature to further authenticate the proof (optional)
        :return: the reserve proof signature
        """
        ...
    def get_reserve_proof_wallet(self, message: str) -> str:
        """
        Generate a signature to prove the entire balance of the wallet.

        :param message: is a message included with the signature to further authenticate the proof (optional)
        :return: the reserve proof signature
        """
        ...
    def get_restore_height(self) -> int:
        """
        Get the height of the first block that the wallet scans.
        
        :return: the height of the first block that the wallet scans
        """
        ...
    def get_seed(self) -> str:
        """
        Get the wallet's mnemonic phrase or seed.

        :return: the wallet's mnemonic phrase or seed.
        """
        ...
    def get_seed_language(self) -> str:
        """
        Get the language of the wallet's mnemonic phrase or seed.

        :return: the language of the wallet's mnemonic phrase or seed.
        """
        ...
    def get_spend_proof(self, tx_hash: str, message: str) -> str:
        """
        Generate a signature to prove a spend. Unlike proving a transaction, it does not require the destination public address.

        :param tx_hash: specifies the transaction to prove
        :param message: is a message to include with the signature to further authenticate the proof (optional)
        :return: the transaction signature
        """
        ...
    def get_subaddress(self, account_idx: int, subaddress_idx: int) -> MoneroSubaddress:
        """
        Get a subaddress.

        :param account_idx: specifies the index of the subaddress's account
        :param subaddress_idx: specifies index of the subaddress within the account
        :return: the retrieved subaddress
        """
        ...
    @typing.overload
    def get_subaddresses(self, account_idx: int) -> list[MoneroSubaddress]:
        """
        Get all subaddresses in an account.

        :param account_idx: specifies the account to get subaddresses within
        :return: the retrieved subaddresses
        """
        ...
    @typing.overload
    def get_subaddresses(self, account_idx: int, subaddress_indices: list[int]) -> list[MoneroSubaddress]:
        """
        Get subaddresses in an account.

        :param account_idx: specifies the account to get subaddresses within
        :param subaddress_indices: are specific subaddresses to get (optional)
        :return: the retrieved subaddresses
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

        :param query: filters query results (optional)
        :return: wallet transfers per the query (free memory using MoneroUtils.free())
        """
        ...
    def get_tx_key(self, tx_hash: str) -> str:
        """
        Get a transaction's secret key from its hash.

        :param tx_hash: is the transaction's hash
        :return: is the transaction's secret key
        """
        ...
    def get_tx_note(self, tx_hash: str) -> str:
        """
        Get a transaction note.

        :param tx_hash: specifies the transaction to get the note of
        :return: the tx note
        """
        ...
    def get_tx_notes(self, tx_hashes: list[str]) -> list[str]:
        """
        Get notes for multiple transactions.

        :param tx_hashes identify the transactions to get notes for
        :returns: notes for the transactions
        """
        ...
    def get_tx_proof(self, tx_hash: str, address: str, message: str) -> str:
        """
        Get a transaction signature to prove it.

        :param tx_hash: specifies the transaction to prove
        :param address: is the destination public address of the transaction
        :param message: is a message to include with the signature to further authenticate the proof (optional)
        :return: the transaction signature
        """
        ...
    @typing.overload
    def get_txs(self) -> list[MoneroTxWallet]:
        """
        Get all wallet transactions.  Wallet transactions contain one or more
        transfers that are either incoming or outgoing to the wallet.

        :return: all wallet transactions (free memory using MoneroUtils.free())
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

        :param query: filters query results (optional)
        :return: wallet transactions per the query (free memory using monero_utils::free)
        """
        ...
    @typing.overload
    def get_unlocked_balance(self) -> int:
        """
        Get the wallet's unlocked balance.

        :return: the wallet's unlocked balance
        """
        ...
    @typing.overload
    def get_unlocked_balance(self, account_idx: int) -> int:
        """
        Get an account's unlocked balance.

        :param account_idx: is the index of the account to get the unlocked balance of
        :return: the account's unlocked balance
        """
        ...
    @typing.overload
    def get_unlocked_balance(self, account_idx: int, subaddress_idx: int) -> int:
        """
        Get a subaddress's unlocked balance.

        :param account_idx: is the index of the subaddress's account to get the unlocked balance of
        :param subaddress_idx: is the index of the subaddress to get the unlocked balance of
        
        :return: the subaddress's balance
        """
        ...
    def get_version(self) -> MoneroVersion:
        """
        Get the wallet's version.

        :return: the wallet's version
        """
        ...
    def import_key_images(self, key_images: list[MoneroKeyImage]) -> MoneroKeyImageImportResult:
        """
        Import signed key images and verify their spent status.

        :param key_images: are key images to import and verify (requires hex and signature)
        :return: results of the import
        """
        ...
    def import_multisig_hex(self, multisig_hexes: list[str]) -> int:
        """
        Import multisig info as hex from other participants.

        Note: If the daemon is not trusted, this method will not automatically
        update the spent status after importing peer multisig hex.

        :param multisig_hexes: are multisig hex from each participant
        :return: the number of outputs signed with the given multisig hex
        """
        ...
    def import_outputs(self, outputs_hex: str) -> int:
        """
        Import outputs in hex format.

        :param outputs_hex: are outputs in hex format
        :return: the number of outputs imported
        """
        ...
    def is_closed(self) -> bool:
        """
        Indicates if the wallet is closed.
        
        :return: true if the wallet is closed, false otherwise
        """
        ...
    def is_connected_to_daemon(self) -> bool:
        """
        Indicates if the wallet is connected a daemon.
        
        :return: true if the wallet is connected to daemon, false otherwise
        """
        ...
    def is_daemon_trusted(self) -> bool:
        """
        Indicates if the daemon is trusted or untrusted.

        :return: true if the daemon is trusted, false otherwise
        """
        ...
    def is_multisig(self) -> bool:
        """
        Indicates if this wallet is a multisig wallet.

        :return: true if this is a multisig wallet, false otherwise
        """
        ...
    def is_multisig_import_needed(self) -> bool:
        """
        Indicates if importing multisig data is needed for returning a correct balance.

        :return: true if importing multisig data is needed for returning a correct balance, false otherwise
        """
        ...
    def is_output_frozen(self, key_image: str) -> bool:
        """
        Check if an output is frozen.

        :param key_image: key image of the output to check if frozen
        :return: true if the output is frozen, false otherwise
        """
        ...
    def is_synced(self) -> bool:
        """
        Indicates if the wallet is synced with the daemon.

        :return: true if the wallet is synced with the daemon, false otherwise
        """
        ...
    def is_view_only(self) -> bool:
        """
        Indicates if the wallet is view-only, meaning it does have the private
        spend key and can therefore only observe incoming outputs.
        
        :return: true if the wallet is view-only, false otherwise
        """
        ...
    def make_multisig(self, mutisig_hexes: list[str], threshold: int, password: str) -> str:
        """
        Make this wallet multisig by importing multisig hex from participants.

        :param multisig_hexes: are multisig hex from each participant
        :param threshold: is the number of signatures needed to sign transfers
        :param password: is the wallet password
        :return: this wallet's multisig hex to share with participants
        """
        ...
    def move_to(self, path: str, password: str) -> None:
        """
        Move the wallet from its current path to the given path.

        :param path: is the new wallet's path
        :param password: is the new wallet's password
        """
        ...
    def parse_payment_uri(self, uri: str) -> MoneroTxConfig:
        """
        Parses a payment URI to a tx configuration.

        :param uri: is the payment uri to parse
        :return: the tx configuration parsed from the uri
        """
        ...
    def prepare_multisig(self) -> str:
        """
        Get multisig info as hex to share with participants to begin creating a
        multisig wallet.

        :return: this wallet's multisig hex to share with participants
        """
        ...
    @typing.overload
    def relay_tx(self, tx_metadata: str) -> str:
        """
        Relay a transaction previously created without relaying.

        :param tx_metadata: is transaction metadata previously created without relaying
        :return: is the hash of the relayed tx
        """
        ...
    @typing.overload
    def relay_tx(self, tx: MoneroTxWallet) -> str:
        """
        Relay a previously created transaction.

        :param tx: is the transaction to relay
        :return: the hash of the relayed tx
        """
        ...
    @typing.overload
    def relay_txs(self, txs: list[MoneroTxWallet]) -> list[str]:
        """
        Relay previously created transactions.

        :param txs: are the transactions to relay
        :return: the hashes of the relayed txs
        """
        ...
    @typing.overload
    def relay_txs(self, tx_metadatas: list[str]) -> list[str]:
        """
        Relay transactions previously created without relaying.

        :param tx_metadatas: are transaction metadata previously created without relaying
        :return: the hashes of the relayed txs
        """
        ...
    def remove_listener(self, listener: MoneroWalletListener) -> None:
        """
        Unregister a listener to receive wallet notifications.

        :param listener: is the listener to unregister
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

        :param tx_hashes: tx hashes to scan
        """
        ...
    def set_account_tag_label(self, tag: str, label: str) -> None:
        """
        Sets a human-readable description for a tag.

        :param tag: is the tag to set a description for
        :param label: is the label to set for the tag
        """
        ...
    def set_attribute(self, key: str, val: str) -> None:
        """
        Set an arbitrary attribute.

        :param key: is the attribute key
        :param val: is the attribute value
        """
        ...
    def set_connection_manager(self, connection_manager: MoneroConnectionManager | None) -> None:
        """
        Set the wallet's daemon connection manager.
        
        :param connection_manager: manages connections to monerod
        """
        ...
    @typing.overload
    def set_daemon_connection(self, connection: MoneroRpcConnection) -> None:
        """
        Set the wallet's daemon connection.

        :param connection: is the connection to set
        """
        ...
    @typing.overload
    def set_daemon_connection(self, uri: str = '', username: str = '', password: str = '') -> None:
        """
        Set the wallet's daemon connection.

        :param uri: is the connection to set
        :param username: is the username to authenticate with the daemon (optional)
        :param password: is the password to authenticate with the daemon (optional)
        """
        ...
    def set_daemon_proxy(self, uri: str = '') -> None:
        """
        Set the Tor proxy to the daemon.
        
        :param uri: is the proxy uri to set
        """
        ...
    def set_restore_height(self, restore_height: int) -> None:
        """
        Set the height of the first block that the wallet scans.

        :param restore_height: is the height of the first block that the wallet scans
        """
        ...
    def set_subaddress_label(self, account_idx: int, subaddress_idx: int, label: str = '') -> None:
        """
        Set a subaddress label.
        
        :param account_idx: index of the account to set the label for
        :param subaddress_idx: index of the subaddress to set the label for
        :param label: the label to set
        """
        ...
    def set_tx_note(self, tx_hash: str, note: str) -> None:
        """
        Set a note for a specific transaction.

        :param tx_hash: specifies the transaction
        :param note: specifies the note
        """
        ...
    def set_tx_notes(self, tx_hashes: list[str], notes: list[str]) -> None:
        """
        Set notes for multiple transactions.

        :param tx_hashes: specify the transactions to set notes for
        :param notes: are the notes to set for the transactions
        """
        ...
    def sign_message(self, msg: str, signature_type: MoneroMessageSignatureType, account_idx: int = 0, subaddress_idx: int = 0) -> str:
        """
        Sign a message.

        :param msg: the message to sign
        :param signature_type: sign with spend key or spend key
        :param account_idx: the account index of the message signature (default 0)
        :param subaddress_idx: the subaddress index of the message signature (default 0)
        :return: the message signature
        """
        ...
    def sign_multisig_tx_hex(self, multisig_tx_hex: str) -> MoneroMultisigSignResult:
        """
        Sign previously created multisig transactions as represented by hex.

        :param multisig_tx_hex: is the hex shared among the multisig transactions when they were created
        :return: the result of signing the multisig transactions
        """
        ...
    def sign_txs(self, unsigned_tx_hex: str) -> MoneroTxSet:
        """
        Sign unsigned transactions from a view-only wallet.

        :param unsigned_tx_hex: is unsigned transaction hex from when the transactions were created
        :return: the signed transaction set
        """
        ...
    def start_syncing(self, sync_period_in_ms: int = 10000) -> None:
        """
        Start background synchronizing with a maximum period between syncs.

        :param sync_period_in_ms: maximum period between syncs in milliseconds
        """
        ...
    def start_mining(self, num_threads: int | None = None, background_mining: bool | None = None, ignore_battery: bool | None = None) -> None:
        """
        Start mining.

        :param num_threads: is the number of threads created for mining (optional)
        :param background_mining: specifies if mining should occur in the background (optional)
        :param ignore_battery: specifies if the battery should be ignored for mining (optional)
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

        :param signed_multisig_tx_hex: is the signed multisig hex returned from signMultisigTxs()
        :return: the resulting transaction hashes
        """
        ...
    def submit_txs(self, signed_tx_hex: str) -> list[str]:
        """
        Submit signed transactions from a view-only wallet.

        :param signed_tx_hex: is signed transaction hex from sign_txs()
        :return: the resulting transaction hashes
        """
        ...
    def sweep_dust(self, relay: bool = False) -> list[MoneroTxWallet]:
        """
        Sweep all unmixable dust outputs back to the wallet to make them easier to spend and mix.

        :param relay: specifies if the resulting transaction should be relayed (default false)
        :return: the created transactions (free memory using monero_utils::free)
        """
        ...
    def sweep_output(self, config: MoneroTxConfig) -> MoneroTxWallet:
        """
        Sweep an output with a given key image.

        :param config: configures the sweep transaction
        :return: the created transaction (free memory using monero_utils::free)
        """
        ...
    def sweep_unlocked(self, config: MoneroTxConfig) -> list[MoneroTxWallet]:
        """
        Sweep unlocked funds according to the given config.

        :param config: is the sweep configuration
        :return: the created transactions (free memory using monero_utils::free)
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

        :param listener: listener to receive notifications during synchronization
        
        :return: the sync result
        """
        ...
    @typing.overload
    def sync(self, start_height: int) -> MoneroSyncResult:
        """
        Synchronize the wallet with the daemon as a one-time synchronous process.

        :param start_height: is the start height to sync from (ignored if less than last processed block)
        
        :return: the sync result
        """
        ...
    @typing.overload
    def sync(self, start_height: int, listener: MoneroWalletListener) -> MoneroSyncResult:
        """
        Synchronizes the wallet with the blockchain.

        :param start_height: start height to sync from (ignored if less than last processed block)
        :param listener: listener to receive notifications during synchronization

        :return: the sync result
        """
        ...
    def tag_accounts(self, tag: str, account_indices: list[int]) -> None:
        """
        Tag accounts.
        
        :param tag: is the tag to apply to the specified accounts
        :param account_indice: are the indices of the accounts to tag
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
        
        :param account_indices: are the indices of the accounts to untag
        """
        ...
    def verify_message(self, msg: str, address: str, signature: str) -> MoneroMessageSignatureResult:
        """
        Verify a message signature.

        :param msg: the signed message
        :param address: signing address
        :param signature: signature
        :return: the message signature result
        """
        ...
    def wait_for_next_block(self) -> int:
        """
        Wait for the next block to be added to the chain.

        :return: the height of the next block when it is added to the chain
        """
        ...
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
class MoneroWalletFull(MoneroWallet):
    """
    Monero wallet implementation which uses monero-project's wallet2.
    """
    @staticmethod
    def create_wallet(config: MoneroWalletConfig) -> MoneroWalletFull:
        """
        Create a new wallet with the given configuration.

        :param config; is the wallet configuration
        :return: a pointer to the wallet instance
        """
        ...
    @staticmethod
    def get_seed_languages() -> list[str]:
        """
        Get a list of available languages for the wallet's seed.

        :return: the available languages for the wallet's seed
        """
        ...
    @staticmethod
    def open_wallet(path: str, password: str, nettype: MoneroNetworkType) -> MoneroWalletFull:
        """
        Open an existing wallet from disk.

        :param path: is the path to the wallet file to open
        :param password: is the password of the wallet file to open
        :param network_type: is the wallet's network type
        :return: a pointer to the wallet instance
        """
        ...
    @staticmethod
    @typing.overload
    def open_wallet_data(password: str, nettype: MoneroNetworkType, keys_data: str, cache_data: str) -> MoneroWalletFull:
        """
        Open an in-memory wallet from existing data buffers.

        :param password: is the password of the wallet file to open
        :param network_type: is the wallet's network type
        :param keys_data: contains the contents of the ".keys" file
        :param cache_data: contains the contents of the wallet cache file (no extension)
        :return: a pointer to the wallet instance
        """
        ...
    @staticmethod
    @typing.overload
    def open_wallet_data(password: str, nettype: MoneroNetworkType, keys_data: str, cache_data: str, daemon_connection: MoneroRpcConnection) -> MoneroWalletFull:
        """
        Open an in-memory wallet from existing data buffers.

        :param password: is the password of the wallet file to open
        :param network_type: is the wallet's network type
        :param keys_data: contains the contents of the ".keys" file
        :param cache_data: contains the contents of the wallet cache file (no extension)
        :param daemon_connection: is connection information to a daemon (default = an unconnected wallet)
        :return: a pointer to the wallet instance
        """
        ...
    @staticmethod
    def wallet_exists(path: str) -> bool:
        """
        Indicates if a wallet exists at the given path.

        :param path: is the path to check for a wallet
        :return: true if a wallet exists at the given path, false otherwise
        """
        ...
    def get_cache_file_buffer(self) -> str:
        ...
    def get_keys_file_buffer(self, password: str, view_only: bool) -> str:
        ...
class MoneroWalletKeys(MoneroWallet):
    """
    Implements a Monero wallet to provide basic key management.
    """
    @staticmethod
    def create_wallet_from_keys(config: MoneroWalletConfig) -> MoneroWalletKeys:
        """
        Create a wallet from an address, view key, and spend key.
    
        :param config: is the wallet configuration (network type, address, view key, spend key, language)
        """
        ...
    @staticmethod
    def create_wallet_from_seed(config: MoneroWalletConfig) -> MoneroWalletKeys:
        """
        Create a wallet from an existing mnemonic phrase or seed.

        :param config: is the wallet configuration (network type, seed, seed offset, isMultisig)
        """
        ...
    @staticmethod
    def create_wallet_random(config: MoneroWalletConfig) -> MoneroWalletKeys:
        """
        Create a new wallet with a randomly generated seed.

        :param config: is the wallet configuration (network type and language)
        """
        ...
    @staticmethod
    def get_seed_languages() -> list[str]:
        """
        Get a list of available languages for the wallet's seed.

        :return: the available languages for the wallet's seed
        """
        ...
class MoneroWalletListener:
    """
    Interface to receive wallet notifications.
    """
    def on_balances_changed(self, new_balance: int, new_unclocked_balance: int) -> None:
        """
        Invoked when the wallet's balances change.

        :param new_balance: new balance
        :param new_unlocked_balance: new unlocked balance
        """
        ...
    def on_new_block(self, height: int) -> None:
        """
        Invoked when a new block is processed.

        :param block: the newly processed block
        """
        ...
    def on_output_received(self, output: MoneroOutputWallet) -> None:
        """
        Invoked when the wallet receives an output.

        :param output: the received output
        """
        ...
    def on_output_spent(self, output: MoneroOutputWallet) -> None:
        """
        Invoked when the wallet spends an output.

        :param output: the spent output
        """
        ...
    def on_sync_progress(self, height: int, start_height: int, end_height: int, percent_done: float, message: str) -> None:
        """
        Invoked when sync progress is made.

        :param height: height of the synced block
        :param start_height: starting height of the sync request
        :param end_height: ending height of the sync request
        :param percent_done: sync progress as a percentage
        :param message: human-readable description of the current progress
        """
        ...
class MoneroWalletRpc(MoneroWallet):
    """
    Implements a Monero wallet using monero-wallet-rpc.
    """
    @typing.overload
    def __init__(self, rpc_connection: MoneroRpcConnection) -> None:
        ...
    @typing.overload
    def __init__(self, uri: str = '', username: str = '', password: str = '') -> None:
        ...
    def create_wallet(self, config: MoneroWalletConfig) -> MoneroWalletRpc:
        """
        Create and open a wallet on the monero-wallet-rpc server.

        :param config: configures the wallet to create
        :return: this wallet client
        """
        ...
    @typing.overload
    def get_accounts(self, include_subaddresses: bool, tag: str, skip_balances: bool) -> list[MoneroAccount]: # type: ignore
        """
        Get all accounts.

        :param include_subaddresses: specifies if subaddresses should be included
        :param skip_balances: skip balance check

        :return: all accounts within the wallet
        """
        ...
    def get_rpc_connection(self) -> MoneroRpcConnection | None:
        """
        Get the wallet's RPC connection.
        
        :return: the wallet's rpc connection
        """
        ...
    @typing.overload
    def open_wallet(self, config: MoneroWalletConfig) -> MoneroWalletRpc:
        """
        Open an existing wallet on the monero-wallet-rpc server.
        
        :param config: configures the wallet to open
        :return: this wallet client
        """
        ...
    @typing.overload
    def open_wallet(self, name: str, password: str) -> MoneroWalletRpc:
        """
        Open an existing wallet on the monero-wallet-rpc server.
         
        :param name: is the name of the wallet file to open
        :param password: is the wallet's password
        :return: this wallet client
        """
        ...
    def stop(self) -> None:
        """
        Save and close the current wallet and stop the RPC server.
        """
        ...
class SerializableStruct:
    """
    Base struct which can be serialized.
    """
    def __init__(self) -> None:
        ...
    def serialize(self) -> str:
        """
        Serializes the struct to a json string.

        :return: the struct serialized to a json string
        """
        ...
class VectorInt:
    # __hash__: typing.ClassVar[None] = None
    def __bool__(self) -> bool:
        """
        Check whether the list is nonempty
        """
    def __contains__(self, x: int) -> bool:
        """
        Return true the container contains ``x``
        """
    @typing.overload
    def __delitem__(self, arg0: int) -> None:
        """
        Delete the list elements at index ``i``
        """
    @typing.overload
    def __delitem__(self, arg0: slice) -> None:
        """
        Delete list elements using a slice object
        """
     def __eq__(self, arg0: VectorInt) -> bool: # type: ignore
        ...
    @typing.overload
    def __getitem__(self, s: slice) -> VectorInt:
        """
        Retrieve list elements using a slice object
        """
    @typing.overload
    def __getitem__(self, arg0: int) -> int:
        ...
    @typing.overload
    def __init__(self) -> None:
        ...
    @typing.overload
    def __init__(self, arg0: VectorInt) -> None:
        """
        Copy constructor
        """
    @typing.overload
    def __init__(self, arg0: typing.Iterable) -> None:
        ...
    def __iter__(self) -> typing.Iterator[int]:
        ...
    def __len__(self) -> int:
        ...
    def __ne__(self, arg0: VectorInt) -> bool: # type: ignore
        ...
    def __repr__(self) -> str:
        """
        Return the canonical string representation of this list.
        """
    @typing.overload
    def __setitem__(self, arg0: int, arg1: int) -> None:
        ...
    @typing.overload
    def __setitem__(self, arg0: slice, arg1: VectorInt) -> None:
        """
        Assign list elements using a slice object
        """
    def append(self, x: int) -> None:
        """
        Add an item to the end of the list
        """
    def clear(self) -> None:
        """
        Clear the contents
        """
    def count(self, x: int) -> int:
        """
        Return the number of times ``x`` appears in the list
        """
    @typing.overload
    def extend(self, L: VectorInt) -> None:
        """
        Extend the list by appending all the items in the given list
        """
    @typing.overload
    def extend(self, L: typing.Iterable) -> None:
        """
        Extend the list by appending all the items in the given list
        """
    def insert(self, i: int, x: int) -> None:
        """
        Insert an item at a given position.
        """
    @typing.overload
    def pop(self) -> int:
        """
        Remove and return the last item
        """
    @typing.overload
    def pop(self, i: int) -> int:
        """
        Remove and return the item at index ``i``
        """
    def remove(self, x: int) -> None:
        """
        Remove the first item from the list whose value is x. It is an error if there is no such item.
        """
class VectorMoneroBlock:
    #__hash__: typing.ClassVar[None] = None
    def __bool__(self) -> bool:
        """
        Check whether the list is nonempty
        """
    def __contains__(self, x: MoneroBlock) -> bool:
        """
        Return true the container contains ``x``
        """
    @typing.overload
    def __delitem__(self, arg0: int) -> None:
        """
        Delete the list elements at index ``i``
        """
    @typing.overload
    def __delitem__(self, arg0: slice) -> None:
        """
        Delete list elements using a slice object
        """
    def __eq__(self, arg0: VectorMoneroBlock) -> bool: # type: ignore
        ...
    @typing.overload
    def __getitem__(self, s: slice) -> VectorMoneroBlock:
        """
        Retrieve list elements using a slice object
        """
    @typing.overload
    def __getitem__(self, arg0: int) -> MoneroBlock:
        ...
    @typing.overload
    def __init__(self) -> None:
        ...
    @typing.overload
    def __init__(self, arg0: VectorMoneroBlock) -> None:
        """
        Copy constructor
        """
    @typing.overload
    def __init__(self, arg0: typing.Iterable) -> None:
        ...
    def __iter__(self) -> typing.Iterator[MoneroBlock]:
        ...
    def __len__(self) -> int:
        ...
    def __ne__(self, arg0: VectorMoneroBlock) -> bool: # type: ignore
        ...
    def __repr__(self) -> str:
        """
        Return the canonical string representation of this list.
        """
    @typing.overload
    def __setitem__(self, arg0: int, arg1: MoneroBlock) -> None:
        ...
    @typing.overload
    def __setitem__(self, arg0: slice, arg1: VectorMoneroBlock) -> None:
        """
        Assign list elements using a slice object
        """
    def append(self, x: MoneroBlock) -> None:
        """
        Add an item to the end of the list
        """
    def clear(self) -> None:
        """
        Clear the contents
        """
    def count(self, x: MoneroBlock) -> int:
        """
        Return the number of times ``x`` appears in the list
        """
    @typing.overload
    def extend(self, L: VectorMoneroBlock) -> None:
        """
        Extend the list by appending all the items in the given list
        """
    @typing.overload
    def extend(self, L: typing.Iterable) -> None:
        """
        Extend the list by appending all the items in the given list
        """
    def insert(self, i: int, x: MoneroBlock) -> None:
        """
        Insert an item at a given position.
        """
    @typing.overload
    def pop(self) -> MoneroBlock:
        """
        Remove and return the last item
        """
    @typing.overload
    def pop(self, i: int) -> MoneroBlock:
        """
        Remove and return the item at index ``i``
        """
    def remove(self, x: MoneroBlock) -> None:
        """
        Remove the first item from the list whose value is x. It is an error if there is no such item.
        """
class VectorMoneroBlockHeader:
    # __hash__: typing.ClassVar[None] = None
    def __bool__(self) -> bool:
        """
        Check whether the list is nonempty
        """
    def __contains__(self, x: MoneroBlockHeader) -> bool:
        """
        Return true the container contains ``x``
        """
    @typing.overload
    def __delitem__(self, arg0: int) -> None:
        """
        Delete the list elements at index ``i``
        """
    @typing.overload
    def __delitem__(self, arg0: slice) -> None:
        """
        Delete list elements using a slice object
        """
    def __eq__(self, arg0: VectorMoneroBlockHeader) -> bool: # type: ignore
        ...
    @typing.overload
    def __getitem__(self, s: slice) -> VectorMoneroBlockHeader:
        """
        Retrieve list elements using a slice object
        """
    @typing.overload
    def __getitem__(self, arg0: int) -> MoneroBlockHeader:
        ...
    @typing.overload
    def __init__(self) -> None:
        ...
    @typing.overload
    def __init__(self, arg0: VectorMoneroBlockHeader) -> None:
        """
        Copy constructor
        """
    @typing.overload
    def __init__(self, arg0: typing.Iterable) -> None:
        ...
    def __iter__(self) -> typing.Iterator[MoneroBlockHeader]:
        ...
    def __len__(self) -> int:
        ...
    def __ne__(self, arg0: VectorMoneroBlockHeader) -> bool: # type: ignore
        ...
    def __repr__(self) -> str:
        """
        Return the canonical string representation of this list.
        """
    @typing.overload
    def __setitem__(self, arg0: int, arg1: MoneroBlockHeader) -> None:
        ...
    @typing.overload
    def __setitem__(self, arg0: slice, arg1: VectorMoneroBlockHeader) -> None:
        """
        Assign list elements using a slice object
        """
    def append(self, x: MoneroBlockHeader) -> None:
        """
        Add an item to the end of the list
        """
    def clear(self) -> None:
        """
        Clear the contents
        """
    def count(self, x: MoneroBlockHeader) -> int:
        """
        Return the number of times ``x`` appears in the list
        """
    @typing.overload
    def extend(self, L: VectorMoneroBlockHeader) -> None:
        """
        Extend the list by appending all the items in the given list
        """
    @typing.overload
    def extend(self, L: typing.Iterable) -> None:
        """
        Extend the list by appending all the items in the given list
        """
    def insert(self, i: int, x: MoneroBlockHeader) -> None:
        """
        Insert an item at a given position.
        """
    @typing.overload
    def pop(self) -> MoneroBlockHeader:
        """
        Remove and return the last item
        """
    @typing.overload
    def pop(self, i: int) -> MoneroBlockHeader:
        """
        Remove and return the item at index ``i``
        """
    def remove(self, x: MoneroBlockHeader) -> None:
        """
        Remove the first item from the list whose value is x. It is an error if there is no such item.
        """
class VectorMoneroDestination:
    # __hash__: typing.ClassVar[None] = None
    def __bool__(self) -> bool:
        """
        Check whether the list is nonempty
        """
    def __contains__(self, x: MoneroDestination) -> bool:
        """
        Return true the container contains ``x``
        """
    @typing.overload
    def __delitem__(self, arg0: int) -> None:
        """
        Delete the list elements at index ``i``
        """
    @typing.overload
    def __delitem__(self, arg0: slice) -> None:
        """
        Delete list elements using a slice object
        """
    def __eq__(self, arg0: VectorMoneroDestination) -> bool: # type: ignore
        ...
    @typing.overload
    def __getitem__(self, s: slice) -> VectorMoneroDestination:
        """
        Retrieve list elements using a slice object
        """
    @typing.overload
    def __getitem__(self, arg0: int) -> MoneroDestination:
        ...
    @typing.overload
    def __init__(self) -> None:
        ...
    @typing.overload
    def __init__(self, arg0: VectorMoneroDestination) -> None:
        """
        Copy constructor
        """
    @typing.overload
    def __init__(self, arg0: typing.Iterable) -> None:
        ...
    def __iter__(self) -> typing.Iterator[MoneroDestination]:
        ...
    def __len__(self) -> int:
        ...
    def __ne__(self, arg0: VectorMoneroDestination) -> bool: # type: ignore
        ...
    def __repr__(self) -> str:
        """
        Return the canonical string representation of this list.
        """
    @typing.overload
    def __setitem__(self, arg0: int, arg1: MoneroDestination) -> None:
        ...
    @typing.overload
    def __setitem__(self, arg0: slice, arg1: VectorMoneroDestination) -> None:
        """
        Assign list elements using a slice object
        """
    def append(self, x: MoneroDestination) -> None:
        """
        Add an item to the end of the list
        """
    def clear(self) -> None:
        """
        Clear the contents
        """
    def count(self, x: MoneroDestination) -> int:
        """
        Return the number of times ``x`` appears in the list
        """
    @typing.overload
    def extend(self, L: VectorMoneroDestination) -> None:
        """
        Extend the list by appending all the items in the given list
        """
    @typing.overload
    def extend(self, L: typing.Iterable) -> None:
        """
        Extend the list by appending all the items in the given list
        """
    def insert(self, i: int, x: MoneroDestination) -> None:
        """
        Insert an item at a given position.
        """
    @typing.overload
    def pop(self) -> MoneroDestination:
        """
        Remove and return the last item
        """
    @typing.overload
    def pop(self, i: int) -> MoneroDestination:
        """
        Remove and return the item at index ``i``
        """
    def remove(self, x: MoneroDestination) -> None:
        """
        Remove the first item from the list whose value is x. It is an error if there is no such item.
        """
class VectorMoneroIncomingTransfer:
    # __hash__: typing.ClassVar[None] = None
    def __bool__(self) -> bool:
        """
        Check whether the list is nonempty
        """
    def __contains__(self, x: MoneroIncomingTransfer) -> bool:
        """
        Return true the container contains ``x``
        """
    @typing.overload
    def __delitem__(self, arg0: int) -> None:
        """
        Delete the list elements at index ``i``
        """
    @typing.overload
    def __delitem__(self, arg0: slice) -> None:
        """
        Delete list elements using a slice object
        """
    def __eq__(self, arg0: VectorMoneroIncomingTransfer) -> bool: # type: ignore
        ...
    @typing.overload
    def __getitem__(self, s: slice) -> VectorMoneroIncomingTransfer:
        """
        Retrieve list elements using a slice object
        """
    @typing.overload
    def __getitem__(self, arg0: int) -> MoneroIncomingTransfer:
        ...
    @typing.overload
    def __init__(self) -> None:
        ...
    @typing.overload
    def __init__(self, arg0: VectorMoneroIncomingTransfer) -> None:
        """
        Copy constructor
        """
    @typing.overload
    def __init__(self, arg0: typing.Iterable) -> None:
        ...
    def __iter__(self) -> typing.Iterator[MoneroIncomingTransfer]:
        ...
    def __len__(self) -> int:
        ...
    def __ne__(self, arg0: VectorMoneroIncomingTransfer) -> bool: # type: ignore
        ...
    def __repr__(self) -> str:
        """
        Return the canonical string representation of this list.
        """
    @typing.overload
    def __setitem__(self, arg0: int, arg1: MoneroIncomingTransfer) -> None:
        ...
    @typing.overload
    def __setitem__(self, arg0: slice, arg1: VectorMoneroIncomingTransfer) -> None:
        """
        Assign list elements using a slice object
        """
    def append(self, x: MoneroIncomingTransfer) -> None:
        """
        Add an item to the end of the list
        """
    def clear(self) -> None:
        """
        Clear the contents
        """
    def count(self, x: MoneroIncomingTransfer) -> int:
        """
        Return the number of times ``x`` appears in the list
        """
    @typing.overload
    def extend(self, L: VectorMoneroIncomingTransfer) -> None:
        """
        Extend the list by appending all the items in the given list
        """
    @typing.overload
    def extend(self, L: typing.Iterable) -> None:
        """
        Extend the list by appending all the items in the given list
        """
    def insert(self, i: int, x: MoneroIncomingTransfer) -> None:
        """
        Insert an item at a given position.
        """
    @typing.overload
    def pop(self) -> MoneroIncomingTransfer:
        """
        Remove and return the last item
        """
    @typing.overload
    def pop(self, i: int) -> MoneroIncomingTransfer:
        """
        Remove and return the item at index ``i``
        """
    def remove(self, x: MoneroIncomingTransfer) -> None:
        """
        Remove the first item from the list whose value is x. It is an error if there is no such item.
        """
class VectorMoneroOutgoingTransfer:
    #__hash__: typing.ClassVar[None] = None
    def __bool__(self) -> bool:
        """
        Check whether the list is nonempty
        """
    def __contains__(self, x: MoneroOutgoingTransfer) -> bool:
        """
        Return true the container contains ``x``
        """
    @typing.overload
    def __delitem__(self, arg0: int) -> None:
        """
        Delete the list elements at index ``i``
        """
    @typing.overload
    def __delitem__(self, arg0: slice) -> None:
        """
        Delete list elements using a slice object
        """
    def __eq__(self, arg0: VectorMoneroOutgoingTransfer) -> bool: # type: ignore
        ...
    @typing.overload
    def __getitem__(self, s: slice) -> VectorMoneroOutgoingTransfer:
        """
        Retrieve list elements using a slice object
        """
    @typing.overload
    def __getitem__(self, arg0: int) -> MoneroOutgoingTransfer:
        ...
    @typing.overload
    def __init__(self) -> None:
        ...
    @typing.overload
    def __init__(self, arg0: VectorMoneroOutgoingTransfer) -> None:
        """
        Copy constructor
        """
    @typing.overload
    def __init__(self, arg0: typing.Iterable) -> None:
        ...
    def __iter__(self) -> typing.Iterator[MoneroOutgoingTransfer]:
        ...
    def __len__(self) -> int:
        ...
    def __ne__(self, arg0: VectorMoneroOutgoingTransfer) -> bool: # type: ignore
        ...
    def __repr__(self) -> str:
        """
        Return the canonical string representation of this list.
        """
    @typing.overload
    def __setitem__(self, arg0: int, arg1: MoneroOutgoingTransfer) -> None:
        ...
    @typing.overload
    def __setitem__(self, arg0: slice, arg1: VectorMoneroOutgoingTransfer) -> None:
        """
        Assign list elements using a slice object
        """
    def append(self, x: MoneroOutgoingTransfer) -> None:
        """
        Add an item to the end of the list
        """
    def clear(self) -> None:
        """
        Clear the contents
        """
    def count(self, x: MoneroOutgoingTransfer) -> int:
        """
        Return the number of times ``x`` appears in the list
        """
    @typing.overload
    def extend(self, L: VectorMoneroOutgoingTransfer) -> None:
        """
        Extend the list by appending all the items in the given list
        """
    @typing.overload
    def extend(self, L: typing.Iterable) -> None:
        """
        Extend the list by appending all the items in the given list
        """
    def insert(self, i: int, x: MoneroOutgoingTransfer) -> None:
        """
        Insert an item at a given position.
        """
    @typing.overload
    def pop(self) -> MoneroOutgoingTransfer:
        """
        Remove and return the last item
        """
    @typing.overload
    def pop(self, i: int) -> MoneroOutgoingTransfer:
        """
        Remove and return the item at index ``i``
        """
    def remove(self, x: MoneroOutgoingTransfer) -> None:
        """
        Remove the first item from the list whose value is x. It is an error if there is no such item.
        """
class VectorMoneroOutput:
    # __hash__: typing.ClassVar[None] = None
    def __bool__(self) -> bool:
        """
        Check whether the list is nonempty
        """
    def __contains__(self, x: MoneroOutput) -> bool:
        """
        Return true the container contains ``x``
        """
    @typing.overload
    def __delitem__(self, arg0: int) -> None:
        """
        Delete the list elements at index ``i``
        """
    @typing.overload
    def __delitem__(self, arg0: slice) -> None:
        """
        Delete list elements using a slice object
        """
    def __eq__(self, arg0: VectorMoneroOutput) -> bool: # type: ignore
        ...
    @typing.overload
    def __getitem__(self, s: slice) -> VectorMoneroOutput:
        """
        Retrieve list elements using a slice object
        """
    @typing.overload
    def __getitem__(self, arg0: int) -> MoneroOutput:
        ...
    @typing.overload
    def __init__(self) -> None:
        ...
    @typing.overload
    def __init__(self, arg0: VectorMoneroOutput) -> None:
        """
        Copy constructor
        """
    @typing.overload
    def __init__(self, arg0: typing.Iterable) -> None:
        ...
    def __iter__(self) -> typing.Iterator[MoneroOutput]:
        ...
    def __len__(self) -> int:
        ...
    def __ne__(self, arg0: VectorMoneroOutput) -> bool: # type: ignore
        ...
    def __repr__(self) -> str:
        """
        Return the canonical string representation of this list.
        """
    @typing.overload
    def __setitem__(self, arg0: int, arg1: MoneroOutput) -> None:
        ...
    @typing.overload
    def __setitem__(self, arg0: slice, arg1: VectorMoneroOutput) -> None:
        """
        Assign list elements using a slice object
        """
    def append(self, x: MoneroOutput) -> None:
        """
        Add an item to the end of the list
        """
    def clear(self) -> None:
        """
        Clear the contents
        """
    def count(self, x: MoneroOutput) -> int:
        """
        Return the number of times ``x`` appears in the list
        """
    @typing.overload
    def extend(self, L: VectorMoneroOutput) -> None:
        """
        Extend the list by appending all the items in the given list
        """
    @typing.overload
    def extend(self, L: typing.Iterable) -> None:
        """
        Extend the list by appending all the items in the given list
        """
    def insert(self, i: int, x: MoneroOutput) -> None:
        """
        Insert an item at a given position.
        """
    @typing.overload
    def pop(self) -> MoneroOutput:
        """
        Remove and return the last item
        """
    @typing.overload
    def pop(self, i: int) -> MoneroOutput:
        """
        Remove and return the item at index ``i``
        """
    def remove(self, x: MoneroOutput) -> None:
        """
        Remove the first item from the list whose value is x. It is an error if there is no such item.
        """
class VectorMoneroOutputWallet:
    #__hash__: typing.ClassVar[None] = None
    def __bool__(self) -> bool:
        """
        Check whether the list is nonempty
        """
    def __contains__(self, x: MoneroOutputWallet) -> bool:
        """
        Return true the container contains ``x``
        """
    @typing.overload
    def __delitem__(self, arg0: int) -> None:
        """
        Delete the list elements at index ``i``
        """
    @typing.overload
    def __delitem__(self, arg0: slice) -> None:
        """
        Delete list elements using a slice object
        """
    def __eq__(self, arg0: VectorMoneroOutputWallet) -> bool: # type: ignore
        ...
    @typing.overload
    def __getitem__(self, s: slice) -> VectorMoneroOutputWallet:
        """
        Retrieve list elements using a slice object
        """
    @typing.overload
    def __getitem__(self, arg0: int) -> MoneroOutputWallet:
        ...
    @typing.overload
    def __init__(self) -> None:
        ...
    @typing.overload
    def __init__(self, arg0: VectorMoneroOutputWallet) -> None:
        """
        Copy constructor
        """
    @typing.overload
    def __init__(self, arg0: typing.Iterable) -> None:
        ...
    def __iter__(self) -> typing.Iterator[MoneroOutputWallet]:
        ...
    def __len__(self) -> int:
        ...
    def __ne__(self, arg0: VectorMoneroOutputWallet) -> bool: # type: ignore
        ...
    def __repr__(self) -> str:
        """
        Return the canonical string representation of this list.
        """
    @typing.overload
    def __setitem__(self, arg0: int, arg1: MoneroOutputWallet) -> None:
        ...
    @typing.overload
    def __setitem__(self, arg0: slice, arg1: VectorMoneroOutputWallet) -> None:
        """
        Assign list elements using a slice object
        """
    def append(self, x: MoneroOutputWallet) -> None:
        """
        Add an item to the end of the list
        """
    def clear(self) -> None:
        """
        Clear the contents
        """
    def count(self, x: MoneroOutputWallet) -> int:
        """
        Return the number of times ``x`` appears in the list
        """
    @typing.overload
    def extend(self, L: VectorMoneroOutputWallet) -> None:
        """
        Extend the list by appending all the items in the given list
        """
    @typing.overload
    def extend(self, L: typing.Iterable) -> None:
        """
        Extend the list by appending all the items in the given list
        """
    def insert(self, i: int, x: MoneroOutputWallet) -> None:
        """
        Insert an item at a given position.
        """
    @typing.overload
    def pop(self) -> MoneroOutputWallet:
        """
        Remove and return the last item
        """
    @typing.overload
    def pop(self, i: int) -> MoneroOutputWallet:
        """
        Remove and return the item at index ``i``
        """
    def remove(self, x: MoneroOutputWallet) -> None:
        """
        Remove the first item from the list whose value is x. It is an error if there is no such item.
        """
class VectorMoneroSubaddress:
    def __bool__(self) -> bool:
        """
        Check whether the list is nonempty
        """
    @typing.overload
    def __delitem__(self, arg0: int) -> None:
        """
        Delete the list elements at index ``i``
        """
    @typing.overload
    def __delitem__(self, arg0: slice) -> None:
        """
        Delete list elements using a slice object
        """
    @typing.overload
    def __getitem__(self, s: slice) -> VectorMoneroSubaddress:
        """
        Retrieve list elements using a slice object
        """
    @typing.overload
    def __getitem__(self, arg0: int) -> MoneroSubaddress:
        ...
    @typing.overload
    def __init__(self) -> None:
        ...
    @typing.overload
    def __init__(self, arg0: VectorMoneroSubaddress) -> None:
        """
        Copy constructor
        """
    @typing.overload
    def __init__(self, arg0: typing.Iterable) -> None:
        ...
    def __iter__(self) -> typing.Iterator[MoneroSubaddress]:
        ...
    def __len__(self) -> int:
        ...
    @typing.overload
    def __setitem__(self, arg0: int, arg1: MoneroSubaddress) -> None:
        ...
    @typing.overload
    def __setitem__(self, arg0: slice, arg1: VectorMoneroSubaddress) -> None:
        """
        Assign list elements using a slice object
        """
    def append(self, x: MoneroSubaddress) -> None:
        """
        Add an item to the end of the list
        """
    def clear(self) -> None:
        """
        Clear the contents
        """
    @typing.overload
    def extend(self, L: VectorMoneroSubaddress) -> None:
        """
        Extend the list by appending all the items in the given list
        """
    @typing.overload
    def extend(self, L: typing.Iterable) -> None:
        """
        Extend the list by appending all the items in the given list
        """
    def insert(self, i: int, x: MoneroSubaddress) -> None:
        """
        Insert an item at a given position.
        """
    @typing.overload
    def pop(self) -> MoneroSubaddress:
        """
        Remove and return the last item
        """
    @typing.overload
    def pop(self, i: int) -> MoneroSubaddress:
        """
        Remove and return the item at index ``i``
        """
class VectorMoneroTransfer:
    #__hash__: typing.ClassVar[None] = None
    def __bool__(self) -> bool:
        """
        Check whether the list is nonempty
        """
    def __contains__(self, x: MoneroTransfer) -> bool:
        """
        Return true the container contains ``x``
        """
    @typing.overload
    def __delitem__(self, arg0: int) -> None:
        """
        Delete the list elements at index ``i``
        """
    @typing.overload
    def __delitem__(self, arg0: slice) -> None:
        """
        Delete list elements using a slice object
        """
    def __eq__(self, arg0: VectorMoneroTransfer) -> bool: # type: ignore
        ...
    @typing.overload
    def __getitem__(self, s: slice) -> VectorMoneroTransfer:
        """
        Retrieve list elements using a slice object
        """
    @typing.overload
    def __getitem__(self, arg0: int) -> MoneroTransfer:
        ...
    @typing.overload
    def __init__(self) -> None:
        ...
    @typing.overload
    def __init__(self, arg0: VectorMoneroTransfer) -> None:
        """
        Copy constructor
        """
    @typing.overload
    def __init__(self, arg0: typing.Iterable) -> None:
        ...
    def __iter__(self) -> typing.Iterator[MoneroTransfer]:
        ...
    def __len__(self) -> int:
        ...
    def __ne__(self, arg0: VectorMoneroTransfer) -> bool: # type: ignore
        ...
    def __repr__(self) -> str:
        """
        Return the canonical string representation of this list.
        """
    @typing.overload
    def __setitem__(self, arg0: int, arg1: MoneroTransfer) -> None:
        ...
    @typing.overload
    def __setitem__(self, arg0: slice, arg1: VectorMoneroTransfer) -> None:
        """
        Assign list elements using a slice object
        """
    def append(self, x: MoneroTransfer) -> None:
        """
        Add an item to the end of the list
        """
    def clear(self) -> None:
        """
        Clear the contents
        """
    def count(self, x: MoneroTransfer) -> int:
        """
        Return the number of times ``x`` appears in the list
        """
    @typing.overload
    def extend(self, L: VectorMoneroTransfer) -> None:
        """
        Extend the list by appending all the items in the given list
        """
    @typing.overload
    def extend(self, L: typing.Iterable) -> None:
        """
        Extend the list by appending all the items in the given list
        """
    def insert(self, i: int, x: MoneroTransfer) -> None:
        """
        Insert an item at a given position.
        """
    @typing.overload
    def pop(self) -> MoneroTransfer:
        """
        Remove and return the last item
        """
    @typing.overload
    def pop(self, i: int) -> MoneroTransfer:
        """
        Remove and return the item at index ``i``
        """
    def remove(self, x: MoneroTransfer) -> None:
        """
        Remove the first item from the list whose value is x. It is an error if there is no such item.
        """
class VectorMoneroTx:
    # __hash__: typing.ClassVar[None] = None
    def __bool__(self) -> bool:
        """
        Check whether the list is nonempty
        """
    def __contains__(self, x: MoneroTx) -> bool:
        """
        Return true the container contains ``x``
        """
    @typing.overload
    def __delitem__(self, arg0: int) -> None:
        """
        Delete the list elements at index ``i``
        """
    @typing.overload
    def __delitem__(self, arg0: slice) -> None:
        """
        Delete list elements using a slice object
        """
    def __eq__(self, arg0: VectorMoneroTx) -> bool: # type: ignore
        ...
    @typing.overload
    def __getitem__(self, s: slice) -> VectorMoneroTx:
        """
        Retrieve list elements using a slice object
        """
    @typing.overload
    def __getitem__(self, arg0: int) -> MoneroTx:
        ...
    @typing.overload
    def __init__(self) -> None:
        ...
    @typing.overload
    def __init__(self, arg0: VectorMoneroTx) -> None:
        """
        Copy constructor
        """
    @typing.overload
    def __init__(self, arg0: typing.Iterable) -> None:
        ...
    def __iter__(self) -> typing.Iterator[MoneroTx]:
        ...
    def __len__(self) -> int:
        ...
    def __ne__(self, arg0: VectorMoneroTx) -> bool: # type: ignore
        ...
    def __repr__(self) -> str:
        """
        Return the canonical string representation of this list.
        """
    @typing.overload
    def __setitem__(self, arg0: int, arg1: MoneroTx) -> None:
        ...
    @typing.overload
    def __setitem__(self, arg0: slice, arg1: VectorMoneroTx) -> None:
        """
        Assign list elements using a slice object
        """
    def append(self, x: MoneroTx) -> None:
        """
        Add an item to the end of the list
        """
    def clear(self) -> None:
        """
        Clear the contents
        """
    def count(self, x: MoneroTx) -> int:
        """
        Return the number of times ``x`` appears in the list
        """
    @typing.overload
    def extend(self, L: VectorMoneroTx) -> None:
        """
        Extend the list by appending all the items in the given list
        """
    @typing.overload
    def extend(self, L: typing.Iterable) -> None:
        """
        Extend the list by appending all the items in the given list
        """
    def insert(self, i: int, x: MoneroTx) -> None:
        """
        Insert an item at a given position.
        """
    @typing.overload
    def pop(self) -> MoneroTx:
        """
        Remove and return the last item
        """
    @typing.overload
    def pop(self, i: int) -> MoneroTx:
        """
        Remove and return the item at index ``i``
        """
    def remove(self, x: MoneroTx) -> None:
        """
        Remove the first item from the list whose value is x. It is an error if there is no such item.
        """
class VectorMoneroTxWallet:
    #__hash__: typing.ClassVar[None] = None
    def __bool__(self) -> bool:
        """
        Check whether the list is nonempty
        """
    def __contains__(self, x: MoneroTxWallet) -> bool:
        """
        Return true the container contains ``x``
        """
    @typing.overload
    def __delitem__(self, arg0: int) -> None:
        """
        Delete the list elements at index ``i``
        """
    @typing.overload
    def __delitem__(self, arg0: slice) -> None:
        """
        Delete list elements using a slice object
        """
    def __eq__(self, arg0: VectorMoneroTxWallet) -> bool: # type: ignore
        ...
    @typing.overload
    def __getitem__(self, s: slice) -> VectorMoneroTxWallet:
        """
        Retrieve list elements using a slice object
        """
    @typing.overload
    def __getitem__(self, arg0: int) -> MoneroTxWallet:
        ...
    @typing.overload
    def __init__(self) -> None:
        ...
    @typing.overload
    def __init__(self, arg0: VectorMoneroTxWallet) -> None:
        """
        Copy constructor
        """
    @typing.overload
    def __init__(self, arg0: typing.Iterable) -> None:
        ...
    def __iter__(self) -> typing.Iterator[MoneroTxWallet]:
        ...
    def __len__(self) -> int:
        ...
    def __ne__(self, arg0: VectorMoneroTxWallet) -> bool: # type: ignore
        ...
    def __repr__(self) -> str:
        """
        Return the canonical string representation of this list.
        """
    @typing.overload
    def __setitem__(self, arg0: int, arg1: MoneroTxWallet) -> None:
        ...
    @typing.overload
    def __setitem__(self, arg0: slice, arg1: VectorMoneroTxWallet) -> None:
        """
        Assign list elements using a slice object
        """
    def append(self, x: MoneroTxWallet) -> None:
        """
        Add an item to the end of the list
        """
    def clear(self) -> None:
        """
        Clear the contents
        """
    def count(self, x: MoneroTxWallet) -> int:
        """
        Return the number of times ``x`` appears in the list
        """
    @typing.overload
    def extend(self, L: VectorMoneroTxWallet) -> None:
        """
        Extend the list by appending all the items in the given list
        """
    @typing.overload
    def extend(self, L: typing.Iterable) -> None:
        """
        Extend the list by appending all the items in the given list
        """
    def insert(self, i: int, x: MoneroTxWallet) -> None:
        """
        Insert an item at a given position.
        """
    @typing.overload
    def pop(self) -> MoneroTxWallet:
        """
        Remove and return the last item
        """
    @typing.overload
    def pop(self, i: int) -> MoneroTxWallet:
        """
        Remove and return the item at index ``i``
        """
    def remove(self, x: MoneroTxWallet) -> None:
        """
        Remove the first item from the list whose value is x. It is an error if there is no such item.
        """
class VectorString:
    #__hash__: typing.ClassVar[None] = None
    def __bool__(self) -> bool:
        """
        Check whether the list is nonempty
        """
    def __contains__(self, x: str) -> bool:
        """
        Return true the container contains ``x``
        """
    @typing.overload
    def __delitem__(self, arg0: int) -> None:
        """
        Delete the list elements at index ``i``
        """
    @typing.overload
    def __delitem__(self, arg0: slice) -> None:
        """
        Delete list elements using a slice object
        """
    def __eq__(self, arg0: VectorString) -> bool: # type: ignore
        ...
    @typing.overload
    def __getitem__(self, s: slice) -> VectorString:
        """
        Retrieve list elements using a slice object
        """
    @typing.overload
    def __getitem__(self, arg0: int) -> str:
        ...
    @typing.overload
    def __init__(self) -> None:
        ...
    @typing.overload
    def __init__(self, arg0: VectorString) -> None:
        """
        Copy constructor
        """
    @typing.overload
    def __init__(self, arg0: typing.Iterable) -> None:
        ...
    def __iter__(self) -> typing.Iterator[str]:
        ...
    def __len__(self) -> int:
        ...
    def __ne__(self, arg0: VectorString) -> bool: # type: ignore
        ...
    def __repr__(self) -> str:
        """
        Return the canonical string representation of this list.
        """
    @typing.overload
    def __setitem__(self, arg0: int, arg1: str) -> None:
        ...
    @typing.overload
    def __setitem__(self, arg0: slice, arg1: VectorString) -> None:
        """
        Assign list elements using a slice object
        """
    def append(self, x: str) -> None:
        """
        Add an item to the end of the list
        """
    def clear(self) -> None:
        """
        Clear the contents
        """
    def count(self, x: str) -> int:
        """
        Return the number of times ``x`` appears in the list
        """
    @typing.overload
    def extend(self, L: VectorString) -> None:
        """
        Extend the list by appending all the items in the given list
        """
    @typing.overload
    def extend(self, L: typing.Iterable) -> None:
        """
        Extend the list by appending all the items in the given list
        """
    def insert(self, i: int, x: str) -> None:
        """
        Insert an item at a given position.
        """
    @typing.overload
    def pop(self) -> str:
        """
        Remove and return the last item
        """
    @typing.overload
    def pop(self, i: int) -> str:
        """
        Remove and return the item at index ``i``
        """
    def remove(self, x: str) -> None:
        """
        Remove the first item from the list whose value is x. It is an error if there is no such item.
        """
class VectorUint32:
    # __hash__: typing.ClassVar[None] = None
    def __bool__(self) -> bool:
        """
        Check whether the list is nonempty
        """
    def __contains__(self, x: int) -> bool:
        """
        Return true the container contains ``x``
        """
    @typing.overload
    def __delitem__(self, arg0: int) -> None:
        """
        Delete the list elements at index ``i``
        """
    @typing.overload
    def __delitem__(self, arg0: slice) -> None:
        """
        Delete list elements using a slice object
        """
    def __eq__(self, arg0: VectorUint32) -> bool: # type: ignore
        ...
    @typing.overload
    def __getitem__(self, s: slice) -> VectorUint32:
        """
        Retrieve list elements using a slice object
        """
    @typing.overload
    def __getitem__(self, arg0: int) -> int:
        ...
    @typing.overload
    def __init__(self) -> None:
        ...
    @typing.overload
    def __init__(self, arg0: VectorUint32) -> None:
        """
        Copy constructor
        """
    @typing.overload
    def __init__(self, arg0: typing.Iterable) -> None:
        ...
    def __iter__(self) -> typing.Iterator[int]:
        ...
    def __len__(self) -> int:
        ...
    def __ne__(self, arg0: VectorUint32) -> bool: # type: ignore
        ...
    def __repr__(self) -> str:
        """
        Return the canonical string representation of this list.
        """
    @typing.overload
    def __setitem__(self, arg0: int, arg1: int) -> None:
        ...
    @typing.overload
    def __setitem__(self, arg0: slice, arg1: VectorUint32) -> None:
        """
        Assign list elements using a slice object
        """
    def append(self, x: int) -> None:
        """
        Add an item to the end of the list
        """
    def clear(self) -> None:
        """
        Clear the contents
        """
    def count(self, x: int) -> int:
        """
        Return the number of times ``x`` appears in the list
        """
    @typing.overload
    def extend(self, L: VectorUint32) -> None:
        """
        Extend the list by appending all the items in the given list
        """
    @typing.overload
    def extend(self, L: typing.Iterable) -> None:
        """
        Extend the list by appending all the items in the given list
        """
    def insert(self, i: int, x: int) -> None:
        """
        Insert an item at a given position.
        """
    @typing.overload
    def pop(self) -> int:
        """
        Remove and return the last item
        """
    @typing.overload
    def pop(self, i: int) -> int:
        """
        Remove and return the item at index ``i``
        """
    def remove(self, x: int) -> None:
        """
        Remove the first item from the list whose value is x. It is an error if there is no such item.
        """
class VectorUint64:
    # __hash__: typing.ClassVar[None] = None
    def __bool__(self) -> bool:
        """
        Check whether the list is nonempty
        """
    def __contains__(self, x: int) -> bool:
        """
        Return true the container contains ``x``
        """
    @typing.overload
    def __delitem__(self, arg0: int) -> None:
        """
        Delete the list elements at index ``i``
        """
    @typing.overload
    def __delitem__(self, arg0: slice) -> None:
        """
        Delete list elements using a slice object
        """
    def __eq__(self, arg0: VectorUint64) -> bool: # type: ignore
        ...
    @typing.overload
    def __getitem__(self, s: slice) -> VectorUint64:
        """
        Retrieve list elements using a slice object
        """
    @typing.overload
    def __getitem__(self, arg0: int) -> int:
        ...
    @typing.overload
    def __init__(self) -> None:
        ...
    @typing.overload
    def __init__(self, arg0: VectorUint64) -> None:
        """
        Copy constructor
        """
    @typing.overload
    def __init__(self, arg0: typing.Iterable) -> None:
        ...
    def __iter__(self) -> typing.Iterator[int]:
        ...
    def __len__(self) -> int:
        ...
    def __ne__(self, arg0: VectorUint64) -> bool: # type: ignore
        ...
    def __repr__(self) -> str:
        """
        Return the canonical string representation of this list.
        """
    @typing.overload
    def __setitem__(self, arg0: int, arg1: int) -> None:
        ...
    @typing.overload
    def __setitem__(self, arg0: slice, arg1: VectorUint64) -> None:
        """
        Assign list elements using a slice object
        """
    def append(self, x: int) -> None:
        """
        Add an item to the end of the list
        """
    def clear(self) -> None:
        """
        Clear the contents
        """
    def count(self, x: int) -> int:
        """
        Return the number of times ``x`` appears in the list
        """
    @typing.overload
    def extend(self, L: VectorUint64) -> None:
        """
        Extend the list by appending all the items in the given list
        """
    @typing.overload
    def extend(self, L: typing.Iterable) -> None:
        """
        Extend the list by appending all the items in the given list
        """
    def insert(self, i: int, x: int) -> None:
        """
        Insert an item at a given position.
        """
    @typing.overload
    def pop(self) -> int:
        """
        Remove and return the last item
        """
    @typing.overload
    def pop(self, i: int) -> int:
        """
        Remove and return the item at index ``i``
        """
    def remove(self, x: int) -> None:
        """
        Remove the first item from the list whose value is x. It is an error if there is no such item.
        """
class VectorUint8:
    #__hash__: typing.ClassVar[None] = None
    def __bool__(self) -> bool:
        """
        Check whether the list is nonempty
        """
    def __contains__(self, x: int) -> bool:
        """
        Return true the container contains ``x``
        """
    @typing.overload
    def __delitem__(self, arg0: int) -> None:
        """
        Delete the list elements at index ``i``
        """
    @typing.overload
    def __delitem__(self, arg0: slice) -> None:
        """
        Delete list elements using a slice object
        """
    def __eq__(self, arg0: VectorUint8) -> bool: # type: ignore
        ...
    @typing.overload
    def __getitem__(self, s: slice) -> VectorUint8:
        """
        Retrieve list elements using a slice object
        """
    @typing.overload
    def __getitem__(self, arg0: int) -> int:
        ...
    @typing.overload
    def __init__(self) -> None:
        ...
    @typing.overload
    def __init__(self, arg0: VectorUint8) -> None:
        """
        Copy constructor
        """
    @typing.overload
    def __init__(self, arg0: typing.Iterable) -> None:
        ...
    def __iter__(self) -> typing.Iterator[int]:
        ...
    def __len__(self) -> int:
        ...
    def __ne__(self, arg0: VectorUint8) -> bool: # type: ignore
        ...
    def __repr__(self) -> str:
        """
        Return the canonical string representation of this list.
        """
    @typing.overload
    def __setitem__(self, arg0: int, arg1: int) -> None:
        ...
    @typing.overload
    def __setitem__(self, arg0: slice, arg1: VectorUint8) -> None:
        """
        Assign list elements using a slice object
        """
    def append(self, x: int) -> None:
        """
        Add an item to the end of the list
        """
    def clear(self) -> None:
        """
        Clear the contents
        """
    def count(self, x: int) -> int:
        """
        Return the number of times ``x`` appears in the list
        """
    @typing.overload
    def extend(self, L: VectorUint8) -> None:
        """
        Extend the list by appending all the items in the given list
        """
    @typing.overload
    def extend(self, L: typing.Iterable) -> None:
        """
        Extend the list by appending all the items in the given list
        """
    def insert(self, i: int, x: int) -> None:
        """
        Insert an item at a given position.
        """
    @typing.overload
    def pop(self) -> int:
        """
        Remove and return the last item
        """
    @typing.overload
    def pop(self, i: int) -> int:
        """
        Remove and return the item at index ``i``
        """
    def remove(self, x: int) -> None:
        """
        Remove the first item from the list whose value is x. It is an error if there is no such item.
        """
