import pytest
import time
import json

from typing import Optional
from monero import (
  MoneroDaemonRpc, MoneroVersion, MoneroBlockHeader, MoneroBlockTemplate, 
  MoneroBlock, MoneroWalletRpc, MoneroMiningStatus, MoneroPruneResult,
  MoneroDaemonUpdateCheckResult, MoneroDaemonUpdateDownloadResult,
  MoneroDaemonListener, MoneroPeer, MoneroDaemonInfo, MoneroDaemonSyncInfo,
  MoneroHardForkInfo, MoneroAltChain, MoneroTx, MoneroSubmitTxResult,
  MoneroTxPoolStats
)
from utils import MoneroTestUtils as Utils, TestContext, BinaryBlockContext


class TestMoneroDaemonRpc:
  _daemon: MoneroDaemonRpc = Utils.get_daemon_rpc()
  _wallet: MoneroWalletRpc = Utils.get_wallet_rpc()
  BINARY_BLOCK_CTX: BinaryBlockContext = BinaryBlockContext()
  LITE_MODE: bool = False
  TEST_NOTIFICATIONS: bool = True

  # Can get the daemon's version
  def test_get_version(self):
    Utils.assert_true(Utils.TEST_NON_RELAYS)
    version: MoneroVersion = self._daemon.get_version()
    assert version.number is not None
    Utils.assert_true(version.number > 0)
    Utils.assert_not_none(version.is_release)

  # Can indicate if it's trusted
  def test_is_trusted(self):
    Utils.assert_true(Utils.TEST_NON_RELAYS)
    self._daemon.is_trusted()

  # Can get the blockchain height
  def test_get_geight(self):
    Utils.assert_true(Utils.TEST_NON_RELAYS)
    height = self._daemon.get_height()
    Utils.assert_true(height > 0, "Height must be greater than 0")

  # Can get a block hash by height
  def test_get_block_id_by_height(self):
    Utils.assert_true(Utils.TEST_NON_RELAYS)
    lastHeader: MoneroBlockHeader = self._daemon.get_last_block_header()
    assert lastHeader.height is not None
    hash: str = self._daemon.get_block_hash(lastHeader.height)
    Utils.assert_not_none(hash)
    Utils.assert_equals(64, len(hash))

  # Can get a block template
  def test_get_block_template(self):
    Utils.assert_true(Utils.TEST_NON_RELAYS)
    template: MoneroBlockTemplate = self._daemon.get_block_template(Utils.ADDRESS, 2)
    Utils.test_block_template(template)

  # Can get the last block's header
  def test_get_last_block_header(self):
    Utils.assert_true(Utils.TEST_NON_RELAYS)
    lastHeader: MoneroBlockHeader = self._daemon.get_last_block_header()
    Utils.test_block_header(lastHeader, True)

  # Can get a block header by hash
  def test_get_block_header_by_hash(self):
    Utils.assert_true(Utils.TEST_NON_RELAYS)
    
    # retrieve by hash of last block
    lastHeader: MoneroBlockHeader = self._daemon.get_last_block_header()
    assert lastHeader.height is not None
    hash: str = self._daemon.get_block_hash(lastHeader.height)
    header: MoneroBlockHeader = self._daemon.get_block_header_by_hash(hash)
    Utils.test_block_header(header, True)
    Utils.assert_equals(lastHeader, header)
    
    # retrieve by hash of previous to last block
    hash = self._daemon.get_block_hash(lastHeader.height - 1)
    header = self._daemon.get_block_header_by_hash(hash)
    Utils.test_block_header(header, True)
    Utils.assert_equals(lastHeader.height - 1, header.height)

  # Can get a block header by height
  def test_get_block_header_by_height(self):
    Utils.assert_true(Utils.TEST_NON_RELAYS)
    
    # retrieve by height of last block
    lastHeader: MoneroBlockHeader = self._daemon.get_last_block_header()
    assert lastHeader.height is not None
    header: MoneroBlockHeader = self._daemon.get_block_header_by_height(lastHeader.height)
    Utils.test_block_header(header, True)
    Utils.assert_equals(lastHeader, header)
    
    # retrieve by height of previous to last block
    header = self._daemon.get_block_header_by_height(lastHeader.height - 1)
    Utils.test_block_header(header, True)
    Utils.assert_equals(lastHeader.height - 1, header.height)

  # Can get block headers by range
  # TODO: test start with no end, vice versa, inclusivity
  def test_get_block_headers_by_range(self):
    Utils.assert_true(Utils.TEST_NON_RELAYS)
    
    # determine start and end height based on number of blocks and how many blocks ago
    numBlocks = 100
    numBlocksAgo = 100
    currentHeight = self._daemon.get_height()
    startHeight = currentHeight - numBlocksAgo
    endHeight = currentHeight - (numBlocksAgo - numBlocks) - 1
    
    # fetch headers
    headers: list[MoneroBlockHeader] = self._daemon.get_block_headers_by_range(startHeight, endHeight)
    
    # test headers
    Utils.assert_equals(numBlocks, len(headers))
    i: int = 0
    while i < numBlocks:
      header: MoneroBlockHeader = headers[i]
      Utils.assert_equals(startHeight + i, header.height)
      Utils.test_block_header(header, True)
      i += 1

  # Can get a block by hash
  def test_get_block_by_hash(self):
    Utils.assert_true(Utils.TEST_NON_RELAYS)
    
    # test config
    ctx = TestContext()
    ctx.hasHex = True
    ctx.hasTxs = False
    ctx.headerIsFull = True
    
    # retrieve by hash of last block
    lastHeader: MoneroBlockHeader = self._daemon.get_last_block_header()
    assert lastHeader.height is not None
    hash: str = self._daemon.get_block_hash(lastHeader.height)
    block: MoneroBlock = self._daemon.get_block_by_hash(hash)
    assert block.height is not None
    Utils.test_block(block, ctx)
    Utils.assert_equals(self._daemon.get_block_by_height(block.height), block)
    Utils.assert_equals(None, block.txs)
    
    # retrieve by hash of previous to last block
    hash = self._daemon.get_block_hash(lastHeader.height - 1)
    block = self._daemon.get_block_by_hash(hash)
    Utils.test_block(block, ctx)
    Utils.assert_equals(self._daemon.get_block_by_height(lastHeader.height - 1), block)
    Utils.assert_equals(None, block.txs)

  # Can get blocks by hash which includes transactions (binary)
  def test_get_blocks_by_hash_binary(self):
    Utils.assert_true(Utils.TEST_NON_RELAYS)
    raise NotImplementedError("Not implemented")

  # Can get a block by height
  def test_get_block_by_height(self):
    Utils.assert_true(Utils.TEST_NON_RELAYS)  
    # config for testing blocks
    ctx = TestContext()
    ctx.hasHex = True
    ctx.headerIsFull = True
    ctx.hasTxs = False
    
    # retrieve by height of last block
    lastHeader: MoneroBlockHeader = self._daemon.get_last_block_header()
    assert lastHeader.height is not None
    block: MoneroBlock = self._daemon.get_block_by_height(lastHeader.height)
    assert block.height is not None
    Utils.test_block(block, ctx)
    Utils.assert_equals(self._daemon.get_block_by_height(block.height), block)
    
    # retrieve by height of previous to last block
    block = self._daemon.get_block_by_height(lastHeader.height - 1)
    Utils.test_block(block, ctx)
    Utils.assert_equals(lastHeader.height - 1, block.height)

  # Can get blocks by height which includes transactions (binary)
  def test_get_blocks_by_height_binary(self):
    Utils.assert_true(Utils.TEST_NON_RELAYS)
    
    # set number of blocks to test
    numBlocks = 100
    
    # select random heights  # TODO: this is horribly inefficient way of computing last 100 blocks if not shuffling
    currentHeight: int = self._daemon.get_height()
    allHeights: list[int] = []
    i: int = 0
    while i < currentHeight:
      allHeights.append(i)
      i += 1

    heights: list[int] = []
    i = len(allHeights) - numBlocks
    
    while i < len(allHeights):
      heights.append(allHeights[i])
      i += 1
    
    # fetch blocks
    blocks: list[MoneroBlock] = self._daemon.get_blocks_by_height(heights)

    # test blocks
    txFound: bool = False
    Utils.assert_equals(numBlocks, len(blocks))
    i = 0
    while i < len(heights):
      block: MoneroBlock = blocks[i]
      if len(block.txs) > 0:
        txFound = True

      Utils.test_block(block, self.BINARY_BLOCK_CTX)
      Utils.assert_equals(block.height, heights[i])
      i += 1

    Utils.assert_true(txFound, "No transactions found to test")

  # Can get transaction pool statistics
  def test_get_tx_pool_statistics(self):
    Utils.assert_true(Utils.TEST_NON_RELAYS)
    daemon = self._daemon
    wallet = self._wallet
    Utils.WALLET_TX_TRACKER.wait_for_wallet_txs_to_clear_pool(daemon, Utils.SYNC_PERIOD_IN_MS, [wallet])
    err: Optional[Exception] = None
    txIds: list[str] = []
    try:
      # submit txs to the pool but don't relay
      i = 1
      while 1 < 3:
        # submit tx hex
        tx: MoneroTx =  Utils.get_unrelayed_tx(wallet, i)
        assert tx.full_hex is not None
        result: MoneroSubmitTxResult = self._daemon.submit_tx_hex(tx.full_hex, True)
        Utils.assert_true(result.is_good, json.dumps(result))
        assert tx.hash is not None
        txIds.append(tx.hash)
        
        # get tx pool stats
        stats: MoneroTxPoolStats = self._daemon.get_tx_pool_stats()
        assert stats.num_txs is not None
        Utils.assert_true(stats.num_txs > i - 1)
        Utils.test_tx_pool_stats(stats)
        i += 1
      
    except Exception as e:
      err = e

    # flush txs
    self._daemon.flush_tx_pool(txIds)
    if err is not None:
      raise Exception(err)

  # Can get general information
  def test_get_general_information(self):
    Utils.assert_true(Utils.TEST_NON_RELAYS)
    info: MoneroDaemonInfo = self._daemon.get_info()
    Utils.test_info(info)

  # Can get sync information
  def test_get_sync_information(self):
    Utils.assert_true(Utils.TEST_NON_RELAYS)
    syncInfo: MoneroDaemonSyncInfo = self._daemon.get_sync_info()
    Utils.test_sync_info(syncInfo)

  # Can get hard fork information
  def test_get_hard_fork_information(self):
    Utils.assert_true(Utils.TEST_NON_RELAYS)
    hardForkInfo: MoneroHardForkInfo = self._daemon.get_hard_fork_info()
    Utils.test_hard_fork_info(hardForkInfo)

  # Can get alternative chains
  def test_get_alternative_chains(self):
    Utils.assert_true(Utils.TEST_NON_RELAYS)
    altChains: list[MoneroAltChain] = self._daemon.get_alt_chains()
    for altChain in altChains:
      Utils.test_alt_chain(altChain)

  # Can get alternative block hashes
  def test_get_alternative_block_ids(self):
    Utils.assert_true(Utils.TEST_NON_RELAYS)
    altBlockIds: list[str] = self._daemon.get_alt_block_hashes()
    for altBlockId in altBlockIds:
      Utils.assert_not_none(altBlockId)
      Utils.assert_equals(64, len(altBlockId))  # TODO: common validation

  # Can get, set, and reset a download bandwidth limit
  def test_set_download_bandwidth(self):
    Utils.assert_true(Utils.TEST_NON_RELAYS)
    initVal: int = self._daemon.get_download_limit()
    Utils.assert_true(initVal > 0)
    setVal: int = initVal * 2
    self._daemon.set_download_limit(setVal)
    Utils.assert_equals(setVal, self._daemon.get_download_limit())
    resetVal: int = self._daemon.reset_download_limit()
    Utils.assert_equals(initVal, resetVal)
    
    # test invalid limits
    try:
      self._daemon.set_download_limit(0)
      raise Exception("Should have thrown error on invalid input")
    except Exception as e:
      Utils.assert_equals("Download limit must be an integer greater than 0", str(e))

    Utils.assert_equals(self._daemon.get_download_limit(), initVal)

  # Can get, set, and reset an upload bandwidth limit
  def test_set_upload_bandwidth(self):
    Utils.assert_true(Utils.TEST_NON_RELAYS)
    initVal: int = self._daemon.get_upload_limit()
    Utils.assert_true(initVal > 0)
    setVal: int = initVal * 2
    self._daemon.set_upload_limit(setVal)
    Utils.assert_equals(setVal, self._daemon.get_upload_limit())
    resetVal: int = self._daemon.reset_upload_limit()
    Utils.assert_equals(initVal, resetVal)
    
    # test invalid limits
    try:
      self._daemon.set_upload_limit(0)
      raise Exception("Should have thrown error on invalid input")
    except Exception as e:
      Utils.assert_equals("Upload limit must be an integer greater than 0", str(e))

    Utils.assert_equals(initVal, self._daemon.get_upload_limit())

  # Can get peers with active incoming or outgoing connections
  def test_get_peers(self):
    Utils.assert_true(Utils.TEST_NON_RELAYS)
    peers: list[MoneroPeer] = self._daemon.get_peers()
    Utils.assert_false(len(peers) == 0, "Daemon has no incoming or outgoing peers to test")
    for peer in peers:
      Utils.test_peer(peer)

  # Can get all known peers which may be online or offline
  def test_get_known_peers(self):
    Utils.assert_true(Utils.TEST_NON_RELAYS)
    peers: list[MoneroPeer] = self._daemon.get_known_peers()
    Utils.assert_false(len(peers) == 0, "Daemon has no known peers to test")
    for peer in peers:
      Utils.test_known_peer(peer, False)

  # Can limit the number of outgoing peers
  def test_set_outgoing_peer_limit(self):
    Utils.assert_true(Utils.TEST_NON_RELAYS)
    self._daemon.set_outgoing_peer_limit(0)
    self._daemon.set_outgoing_peer_limit(8)
    self._daemon.set_outgoing_peer_limit(10)

  # Can limit the number of incoming peers
  def test_set_incoming_peer_limit(self):
    Utils.assert_true(Utils.TEST_NON_RELAYS)
    self._daemon.set_incoming_peer_limit(0)
    self._daemon.set_incoming_peer_limit(8)
    self._daemon.set_incoming_peer_limit(10)

  # Can notify listeners when a new block is added to the chain
  def test_block_listener(self):
    Utils.assert_true(not self.LITE_MODE and self.TEST_NOTIFICATIONS)
    
    try:
      # start mining if possible to help push the network along
      address: str = self._wallet.get_primary_address()
      try: 
        self._daemon.start_mining(address, 8, False, True)
      except:
        pass
      
      # register a listener
      listener: MoneroDaemonListener = MoneroDaemonListener()
      self._daemon.add_listener(listener)
      
      # wait for next block notification
      header: MoneroBlockHeader = self._daemon.wait_for_next_block_header()
      self._daemon.remove_listener(listener) # unregister listener so daemon does not keep polling
      Utils.test_block_header(header, True)
      
      # test that listener was called with equivalent header
      Utils.assert_equals(header, listener.last_header)
    except Exception as e:
      raise e
    finally:
      # stop mining
      try :
        self._daemon.stop_mining()
      except:
        pass

  # Can start and stop mining
  def test_mining(self):
    Utils.assert_true(Utils.TEST_NON_RELAYS)
    
    # stop mining at beginning of test
    try:
      self._daemon.stop_mining()
    except:
      pass
    
    # generate address to mine to
    address: str = self._wallet.get_primary_address()
    
    # start mining
    self._daemon.start_mining(address, 2, False, True)
    
    # stop mining
    self._daemon.stop_mining()

  # Can get mining status
  def test_get_mining_status(self):
    Utils.assert_true(Utils.TEST_NON_RELAYS)
    
    try:
      # stop mining at beginning of test
      try:
        self._daemon.stop_mining()
      except:
        pass
      
      # test status without mining
      status: MoneroMiningStatus = self._daemon.get_mining_status()
      Utils.assert_equals(False, status.is_active)
      Utils.assert_is_none(status.address)
      Utils.assert_equals(0, status.speed)
      Utils.assert_equals(0, status.num_threads)
      Utils.assert_is_none(status.is_background)
      
      # test status with mining
      address: str = self._wallet.get_primary_address()
      threadCount: int = 3
      isBackground: bool = False
      self._daemon.start_mining(address, threadCount, isBackground, True)
      status = self._daemon.get_mining_status()
      assert status.speed is not None
      Utils.assert_equals(True, status.is_active)
      Utils.assert_equals(address, status.address)
      Utils.assert_true(status.speed >= 0)
      Utils.assert_equals(threadCount, status.num_threads)
      Utils.assert_equals(isBackground, status.is_background)
    except Exception as e:
      raise e
    finally:

      # stop mining at end of test
      try:
        self._daemon.stop_mining()
      except:
        pass

  # Can submit a mined block to the network
  def test_submit_mined_block(self):
    Utils.assert_true(Utils.TEST_NON_RELAYS)
    
    # get template to mine on
    template: MoneroBlockTemplate = self._daemon.get_block_template(Utils.ADDRESS)
    assert template.block_template_blob is not None
    
    # TODO monero rpc: way to get mining nonce when found in order to submit?
    
    # try to submit block hashing blob without nonce
    try:
      self._daemon.submit_block(template.block_template_blob)
      raise Exception("Should have thrown error")
    except Exception as e:
      # Utils.assert_equals(-7, (int) e.getCode())
      Utils.assert_equals("Block not accepted", str(e))

  # Can prune the blockchain
  def test_prune_blockchain(self):
    Utils.assert_true(Utils.TEST_NON_RELAYS)

    result: MoneroPruneResult = self._daemon.prune_blockchain(True)

    if (result.is_pruned):
      assert result.pruning_seed is not None
      Utils.assert_true(result.pruning_seed > 0)
    else:
      Utils.assert_equals(0,  result.pruning_seed)

  # Can check for an update
  def test_check_for_update(self):
    Utils.assert_true(Utils.TEST_NON_RELAYS)

    result: MoneroDaemonUpdateCheckResult = self._daemon.check_for_update()
    Utils.test_update_check_result(result)

  # Can download an update
  @pytest.mark.skip(reason="")
  def test_download_update(self):
    Utils.assert_true(Utils.TEST_NON_RELAYS)
    
    # download to default path
    result: MoneroDaemonUpdateDownloadResult = self._daemon.download_update()
    Utils.test_update_download_result(result, None)
    
    # download to defined path
    path: str = "test_download_" + str(time.time()) + ".tar.bz2"
    result = self._daemon.download_update(path)
    Utils.test_update_download_result(result, path)
    
    # test invalid path
    if (result.is_update_available):
      try:
        result = self._daemon.download_update("./ohhai/there")
        raise Exception("Should have thrown error")
      except Exception as e:
        Utils.assert_not_equals(str(e), "Should have thrown error")
        # Utils.assert_equals(500, (int) e.getCode())  # TODO monerod: this causes a 500 in daemon rpc

  # Can be stopped
  @pytest.mark.skip(reason="test is disabled to not interfere with other tests")
  def test_stop(self):
    Utils.assert_true(Utils.TEST_NON_RELAYS)
    
    # stop the daemon
    self._daemon.stop()
    
    # give the daemon time to shut down
    # TimeUnit.MILLISECONDS.sleep(Utils.SYNC_PERIOD_IN_MS)
    
    # try to interact with the daemon
    try:
      self._daemon.get_height()
      raise Exception("Should have thrown error")
    except Exception as e:
      Utils.assert_not_equals("Should have thrown error", str(e))
