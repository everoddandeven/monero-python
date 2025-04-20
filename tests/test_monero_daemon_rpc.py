import pytest
import time

from monero import (
  MoneroDaemonRpc, MoneroVersion, MoneroBlockHeader, MoneroBlockTemplate, 
  MoneroBlock, MoneroWalletRpc, MoneroMiningStatus, MoneroPruneResult,
  MoneroDaemonUpdateCheckResult, MoneroDaemonUpdateDownloadResult
)
from utils import MoneroTestUtils as Utils, TestContext, BinaryBlockContext

daemon: MoneroDaemonRpc = Utils.get_daemon_rpc()
wallet: MoneroWalletRpc = Utils.get_wallet_rpc()
BINARY_BLOCK_CTX: BinaryBlockContext = BinaryBlockContext()

# Can get the daemon's version
def test_get_version():
  Utils.assert_true(Utils.TEST_NON_RELAYS)
  version: MoneroVersion = daemon.get_version()
  Utils.assert_not_none(version.number)
  Utils.assert_true(version.number > 0)
  Utils.assert_not_none(version.is_release)

# Can indicate if it's trusted
def test_is_trusted():
  Utils.assert_true(Utils.TEST_NON_RELAYS)
  daemon.is_trusted()

# Can get the blockchain height
def test_get_geight():
  Utils.assert_true(Utils.TEST_NON_RELAYS)
  height = daemon.get_height()
  Utils.assert_true(height > 0, "Height must be greater than 0")

# Can get a block hash by height
def test_get_block_id_by_height():
  Utils.assert_true(Utils.TEST_NON_RELAYS)
  lastHeader: MoneroBlockHeader = daemon.get_last_block_header()
  hash: str = daemon.get_block_hash(lastHeader.height)
  Utils.assert_not_none(hash)
  Utils.assert_equals(64, len(hash))

# Can get a block template
def test_get_block_template():
  Utils.assert_true(Utils.TEST_NON_RELAYS)
  template: MoneroBlockTemplate = daemon.get_block_template(Utils.ADDRESS, 2)
  Utils.test_block_template(template)

# Can get the last block's header
def test_get_last_block_header():
  Utils.assert_true(Utils.TEST_NON_RELAYS)
  lastHeader: MoneroBlockHeader = daemon.get_last_block_header()
  Utils.test_block_header(lastHeader, True)

# Can get a block header by hash
def test_get_block_header_by_hash():
  Utils.assert_true(Utils.TEST_NON_RELAYS)
  
  # retrieve by hash of last block
  lastHeader: MoneroBlockHeader = daemon.get_last_block_header()
  hash: str = daemon.get_block_hash(lastHeader.height)
  header: MoneroBlockHeader = daemon.get_block_header_by_hash(hash)
  Utils.test_block_header(header, True)
  Utils.assert_equals(lastHeader, header)
  
  # retrieve by hash of previous to last block
  hash = daemon.get_block_hash(lastHeader.height - 1)
  header = daemon.get_block_header_by_hash(hash)
  Utils.test_block_header(header, True)
  Utils.assert_equals(lastHeader.height - 1, header.height)

# Can get a block header by height
def test_get_block_header_by_height():
  Utils.assert_true(Utils.TEST_NON_RELAYS)
  
  # retrieve by height of last block
  lastHeader: MoneroBlockHeader = daemon.get_last_block_header()
  header: MoneroBlockHeader = daemon.get_block_header_by_height(lastHeader.height)
  Utils.test_block_header(header, True)
  Utils.assert_equals(lastHeader, header)
  
  # retrieve by height of previous to last block
  header = daemon.get_block_header_by_height(lastHeader.height - 1)
  Utils.test_block_header(header, True)
  Utils.assert_equals(lastHeader.height - 1, header.height)

# Can get block headers by range
# TODO: test start with no end, vice versa, inclusivity
def test_get_block_headers_by_range():
  Utils.assert_true(Utils.TEST_NON_RELAYS)
  
  # determine start and end height based on number of blocks and how many blocks ago
  numBlocks = 100
  numBlocksAgo = 100
  currentHeight = daemon.get_height()
  startHeight = currentHeight - numBlocksAgo
  endHeight = currentHeight - (numBlocksAgo - numBlocks) - 1
  
  # fetch headers
  headers: list[MoneroBlockHeader] = daemon.get_block_headers_by_range(startHeight, endHeight)
  
  # test headers
  Utils.assert_equals(numBlocks, len(headers))
  i: int = 0
  while i < numBlocks:
    header: MoneroBlockHeader = headers[i]
    Utils.assert_equals(startHeight + i, header.height)
    Utils.test_block_header(header, True)
    i += 1

# Can get a block by hash
def test_get_block_by_hash():
  Utils.assert_true(Utils.TEST_NON_RELAYS)
  
  # test config
  ctx = TestContext()
  ctx.hasHex = True
  ctx.hasTxs = False
  ctx.headerIsFull = True
  
  # retrieve by hash of last block
  lastHeader: MoneroBlockHeader = daemon.get_last_block_header()
  hash: str = daemon.get_block_hash(lastHeader.height)
  block: MoneroBlock = daemon.get_block_by_hash(hash)
  Utils.test_block(block, ctx)
  Utils.assert_equals(daemon.get_block_by_height(block.height), block)
  Utils.assert_equals(None, block.txs)
  
  # retrieve by hash of previous to last block
  hash = daemon.get_block_hash(lastHeader.height - 1)
  block = daemon.get_block_by_hash(hash)
  Utils.test_block(block, ctx)
  Utils.assert_equals(daemon.get_block_by_height(lastHeader.height - 1), block)
  Utils.assert_equals(None, block.txs)

# Can get blocks by hash which includes transactions (binary)
def test_get_blocks_by_hash_binary():
  Utils.assert_true(Utils.TEST_NON_RELAYS)
  raise NotImplementedError("Not implemented")

# Can get a block by height
def test_get_block_by_height():
  Utils.assert_true(Utils.TEST_NON_RELAYS)  
  # config for testing blocks
  ctx = TestContext()
  ctx.hasHex = True
  ctx.headerIsFull = True
  ctx.hasTxs = False
  
  # retrieve by height of last block
  lastHeader: MoneroBlockHeader = daemon.get_last_block_header()
  block: MoneroBlock = daemon.get_block_by_height(lastHeader.height)
  Utils.test_block(block, ctx)
  Utils.assert_equals(daemon.get_block_by_height(block.height), block)
  
  # retrieve by height of previous to last block
  block = daemon.get_block_by_height(lastHeader.height - 1)
  Utils.test_block(block, ctx)
  Utils.assert_equals(lastHeader.height - 1, block.height)

# Can get blocks by height which includes transactions (binary)
def test_get_blocks_by_height_binary():
  Utils.assert_true(Utils.TEST_NON_RELAYS)
  
  # set number of blocks to test
  numBlocks = 100
  
  # select random heights  # TODO: this is horribly inefficient way of computing last 100 blocks if not shuffling
  currentHeight: int = daemon.get_height()
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
  blocks: list[MoneroBlock] = daemon.get_blocks_by_height(heights)

  # test blocks
  txFound: bool = False
  Utils.assert_equals(numBlocks, len(blocks))
  i = 0
  while i < len(heights):
    block: MoneroBlock = blocks[i]
    if len(block.txs) > 0:
      txFound = True

    Utils.test_block(block, BINARY_BLOCK_CTX)
    Utils.assert_equals(block.height, heights[i])
    i += 1

  Utils.assert_true(txFound, "No transactions found to test")

# Can start and stop mining
def test_mining():
  Utils.assert_true(Utils.TEST_NON_RELAYS)
  
  # stop mining at beginning of test
  try:
    daemon.stop_mining()
  except:
    pass
  
  # generate address to mine to
  address: str = wallet.get_primary_address()
  
  # start mining
  daemon.start_mining(address, 2, False, True)
  
  # stop mining
  daemon.stop_mining()


# Can get mining status
def test_get_mining_status():
  Utils.assert_true(Utils.TEST_NON_RELAYS)
  
  try:
    # stop mining at beginning of test
    try:
      daemon.stop_mining()
    except:
      pass
    
    # test status without mining
    status: MoneroMiningStatus = daemon.get_mining_status()
    Utils.assert_equals(False, status.is_active)
    Utils.assert_is_none(status.address)
    Utils.assert_equals(0, status.speed)
    Utils.assert_equals(0, status.num_threads)
    Utils.assert_is_none(status.is_background)
    
    # test status with mining
    address: str = wallet.get_primary_address()
    threadCount: int = 3
    isBackground: bool = False
    daemon.start_mining(address, threadCount, isBackground, True)
    status = daemon.get_mining_status()
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
      daemon.stop_mining()
    except:
      pass

# Can submit a mined block to the network
def test_submit_mined_block():
  Utils.assert_true(Utils.TEST_NON_RELAYS)
  
  # get template to mine on
  template: MoneroBlockTemplate = daemon.get_block_template(Utils.ADDRESS)
  
  # TODO monero rpc: way to get mining nonce when found in order to submit?
  
  # try to submit block hashing blob without nonce
  try:
    daemon.submit_block(template.block_template_blob)
    raise Exception("Should have thrown error")
  except Exception as e:
    # Utils.assert_equals(-7, (int) e.getCode())
    Utils.assert_equals("Block not accepted", str(e))

# Can prune the blockchain
def test_prune_blockchain():
  Utils.assert_true(Utils.TEST_NON_RELAYS)

  result: MoneroPruneResult = daemon.prune_blockchain(True)

  if (result.is_pruned):
    Utils.assert_true(result.pruning_seed > 0)
  else:
    Utils.assert_equals(0,  result.pruning_seed)

# Can check for an update
def test_check_for_update():
  Utils.assert_true(Utils.TEST_NON_RELAYS)

  result: MoneroDaemonUpdateCheckResult = daemon.check_for_update()
  Utils.test_update_check_result(result)

# Can download an update
@pytest.mark.skip(reason="")
def test_download_update():
  Utils.assert_true(Utils.TEST_NON_RELAYS)
  
  # download to default path
  result: MoneroDaemonUpdateDownloadResult = daemon.download_update()
  Utils.test_update_download_result(result, None)
  
  # download to defined path
  path: str = "test_download_" + str(time.time()) + ".tar.bz2"
  result = daemon.download_update(path)
  Utils.test_update_download_result(result, path)
  
  # test invalid path
  if (result.is_update_available):
    try:
      result = daemon.download_update("./ohhai/there")
      raise Exception("Should have thrown error")
    except Exception as e:
      Utils.assert_not_equals(str(e), "Should have thrown error")
      # Utils.assert_equals(500, (int) e.getCode())  # TODO monerod: this causes a 500 in daemon rpc

# Can be stopped
@pytest.mark.skip(reason="test is disabled to not interfere with other tests")
def test_stop():
  Utils.assert_true(Utils.TEST_NON_RELAYS)
  
  # stop the daemon
  daemon.stop()
  
  # give the daemon time to shut down
  # TimeUnit.MILLISECONDS.sleep(Utils.SYNC_PERIOD_IN_MS)
  
  # try to interact with the daemon
  try:
    daemon.get_height()
    raise Exception("Should have thrown error")
  except Exception as e:
    Utils.assert_not_equals("Should have thrown error", str(e))
