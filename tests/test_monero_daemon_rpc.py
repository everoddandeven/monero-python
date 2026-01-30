import pytest
import time
import json
import logging

from monero import (
    MoneroDaemonRpc, MoneroVersion, MoneroBlockHeader, MoneroBlockTemplate,
    MoneroBlock, MoneroWallet, MoneroMiningStatus, MoneroPruneResult,
    MoneroDaemonUpdateCheckResult, MoneroDaemonUpdateDownloadResult,
    MoneroDaemonListener, MoneroPeer, MoneroDaemonInfo, MoneroDaemonSyncInfo,
    MoneroHardForkInfo, MoneroAltChain, MoneroTx, MoneroSubmitTxResult,
    MoneroTxPoolStats, MoneroBan, MoneroTxConfig, MoneroDestination
)
from utils import (
    TestUtils as Utils, TestContext,
    BinaryBlockContext, MiningUtils,
    OsUtils, AssertUtils, TxUtils,
    BlockUtils, GenUtils, DaemonUtils
)

logger: logging.Logger = logging.getLogger("TestMoneroDaemonRpc")


@pytest.mark.skipif(OsUtils.is_windows(), reason="TODO setup test environment for windows")
class TestMoneroDaemonRpc:
    _daemon: MoneroDaemonRpc = Utils.get_daemon_rpc()
    _wallet: MoneroWallet = Utils.get_wallet_rpc() # type: ignore
    BINARY_BLOCK_CTX: BinaryBlockContext = BinaryBlockContext()

    #region Fixtures

    @pytest.fixture(scope="class", autouse=True)
    def before_all(self):
        if not OsUtils.is_windows():
            MiningUtils.wait_until_blockchain_ready()

    @pytest.fixture(autouse=True)
    def setup_and_teardown(self, request: pytest.FixtureRequest):
        logger.info(f"Before {request.node.name}") # type: ignore
        yield
        logger.info(f"After {request.node.name}") # type: ignore

    #endregion

    #region Tests

    # Can get the daemon's version
    @pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_get_version(self):
        version: MoneroVersion = self._daemon.get_version()
        assert version.number is not None
        AssertUtils.assert_true(version.number > 0)
        AssertUtils.assert_not_none(version.is_release)

    # Can indicate if it's trusted
    @pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_is_trusted(self):
        self._daemon.is_trusted()

    # Can get the blockchain height
    @pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_get_height(self):
        height = self._daemon.get_height()
        AssertUtils.assert_true(height > 0, "Height must be greater than 0")

    # Can get a block hash by height
    @pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_get_block_id_by_height(self):
        last_header: MoneroBlockHeader = self._daemon.get_last_block_header()
        assert last_header.height is not None
        hash_str: str = self._daemon.get_block_hash(last_header.height)
        AssertUtils.assert_not_none(hash_str)
        AssertUtils.assert_equals(64, len(hash_str))

    # Can get a block template
    @pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_get_block_template(self):
        template: MoneroBlockTemplate = self._daemon.get_block_template(Utils.ADDRESS, 2)
        DaemonUtils.test_block_template(template)

    # Can get the last block's header
    @pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_get_last_block_header(self):
        last_header: MoneroBlockHeader = self._daemon.get_last_block_header()
        BlockUtils.test_block_header(last_header, True)

    # Can get a block header by hash
    @pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_get_block_header_by_hash(self):
        # retrieve by hash of last block
        last_header: MoneroBlockHeader = self._daemon.get_last_block_header()
        assert last_header.height is not None
        hash_str: str = self._daemon.get_block_hash(last_header.height)
        header: MoneroBlockHeader = self._daemon.get_block_header_by_hash(hash_str)
        BlockUtils.test_block_header(header, True)
        AssertUtils.assert_equals(last_header, header)

        # retrieve by hash of previous to last block
        hash_str = self._daemon.get_block_hash(last_header.height - 1)
        header = self._daemon.get_block_header_by_hash(hash_str)
        BlockUtils.test_block_header(header, True)
        AssertUtils.assert_equals(last_header.height - 1, header.height)

    # Can get a block header by height
    @pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_get_block_header_by_height(self):
        # retrieve by height of last block
        last_header: MoneroBlockHeader = self._daemon.get_last_block_header()
        assert last_header.height is not None
        header: MoneroBlockHeader = self._daemon.get_block_header_by_height(last_header.height)
        BlockUtils.test_block_header(header, True)
        AssertUtils.assert_equals(last_header, header)

        # retrieve by height of previous to last block
        header = self._daemon.get_block_header_by_height(last_header.height - 1)
        BlockUtils.test_block_header(header, True)
        AssertUtils.assert_equals(last_header.height - 1, header.height)

    # Can get block headers by range
    # TODO: test start with no end, vice versa, inclusivity
    @pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_get_block_headers_by_range(self):
        # determine start and end height based on number of blocks and how many blocks ago
        num_blocks = 100
        num_blocks_ago = 100
        current_height = self._daemon.get_height()
        start_height = current_height - num_blocks_ago
        end_height = current_height - (num_blocks_ago - num_blocks) - 1

        # fetch headers
        headers: list[MoneroBlockHeader] = self._daemon.get_block_headers_by_range(start_height, end_height)

        # test headers
        AssertUtils.assert_equals(num_blocks, len(headers))
        i: int = 0
        while i < num_blocks:
            header: MoneroBlockHeader = headers[i]
            AssertUtils.assert_equals(start_height + i, header.height)
            BlockUtils.test_block_header(header, True)
            i += 1

    # Can get a block by hash
    @pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_get_block_by_hash(self):
        # test config
        ctx = TestContext()
        ctx.has_hex = True
        ctx.has_txs = False
        ctx.header_is_full = True

        # retrieve by hash of last block
        last_header: MoneroBlockHeader = self._daemon.get_last_block_header()
        assert last_header.height is not None
        hash_str: str = self._daemon.get_block_hash(last_header.height)
        block: MoneroBlock = self._daemon.get_block_by_hash(hash_str)
        assert block.height is not None
        BlockUtils.test_block(block, ctx)
        AssertUtils.assert_equals(self._daemon.get_block_by_height(block.height), block)
        assert len(block.txs) == 0, f"No block tx expected, found: {len(block.txs)}"

        # retrieve by hash of previous to last block
        hash_str = self._daemon.get_block_hash(last_header.height - 1)
        block = self._daemon.get_block_by_hash(hash_str)
        BlockUtils.test_block(block, ctx)
        AssertUtils.assert_equals(self._daemon.get_block_by_height(last_header.height - 1), block)
        assert len(block.txs) == 0, f"No block tx expected, found: {len(block.txs)}"

    # Can get blocks by hash which includes transactions (binary)
    #@pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    @pytest.mark.skip(reason="Not implemented")
    def test_get_blocks_by_hash_binary(self) -> None:
        raise NotImplementedError("Not implemented")

    # Can get a block by height
    @pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_get_block_by_height(self):
        # config for testing blocks
        ctx = TestContext()
        ctx.has_hex = True
        ctx.header_is_full = True
        ctx.has_txs = False

        # retrieve by height of last block
        last_header: MoneroBlockHeader = self._daemon.get_last_block_header()
        assert last_header.height is not None
        block: MoneroBlock = self._daemon.get_block_by_height(last_header.height)
        assert block.height is not None
        BlockUtils.test_block(block, ctx)
        AssertUtils.assert_equals(self._daemon.get_block_by_height(block.height), block)

        # retrieve by height of previous to last block
        block = self._daemon.get_block_by_height(last_header.height - 1)
        BlockUtils.test_block(block, ctx)
        AssertUtils.assert_equals(last_header.height - 1, block.height)

    # Can get blocks by height which includes transactions (binary)
    #@pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    @pytest.mark.skip(reason="TODO fund wallet")
    def test_get_blocks_by_height_binary(self):
        # set number of blocks to test
        num_blocks = 100

        # select random heights # TODO: this is horribly inefficient way of computing last 100 blocks if not shuffling
        current_height: int = self._daemon.get_height()
        all_heights: list[int] = []
        i: int = 0
        while i < current_height:
            all_heights.append(i)
            i += 1

        heights: list[int] = []
        i = len(all_heights) - num_blocks

        while i < len(all_heights):
            heights.append(all_heights[i])
            i += 1

        # fetch blocks
        blocks: list[MoneroBlock] = self._daemon.get_blocks_by_height(heights)

        # test blocks
        tx_found: bool = False
        AssertUtils.assert_equals(num_blocks, len(blocks))
        i = 0
        while i < len(heights):
            block: MoneroBlock = blocks[i]
            if len(block.txs) > 0:
                tx_found = True

            BlockUtils.test_block(block, self.BINARY_BLOCK_CTX)
            AssertUtils.assert_equals(block.height, heights[i])
            i += 1

        AssertUtils.assert_true(tx_found, "No transactions found to test")

    # Can get blocks by range in a single request
    @pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_get_blocks_by_range(self):
        # get height range
        num_blocks = 100
        num_blocks_ago = 102
        AssertUtils.assert_true(num_blocks > 0)
        AssertUtils.assert_true(num_blocks_ago >= num_blocks)
        height = self._daemon.get_height()
        AssertUtils.assert_true(height - num_blocks_ago + num_blocks - 1 < height)
        start_height = height - num_blocks_ago
        end_height = height - num_blocks_ago + num_blocks - 1

        # test known start and end heights
        BlockUtils.test_get_blocks_range(self._daemon, start_height, end_height, height, False, self.BINARY_BLOCK_CTX)

        # test unspecified start
        BlockUtils.test_get_blocks_range(self._daemon, None, num_blocks - 1, height, False, self.BINARY_BLOCK_CTX)

        # test unspecified end
        BlockUtils.test_get_blocks_range(self._daemon, height - num_blocks - 1, None, height, False, self.BINARY_BLOCK_CTX)

    # Can get blocks by range using chunked requests
    @pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_get_blocks_by_range_chunked(self):
        # get long height range
        num_blocks = min(self._daemon.get_height() - 2, 1440) # test up to ~2 days of blocks
        AssertUtils.assert_true(num_blocks > 0)
        height = self._daemon.get_height()
        AssertUtils.assert_true(height - num_blocks - 1 < height)
        start_height = height - num_blocks
        end_height = height - 1

        # test known start and end heights
        BlockUtils.test_get_blocks_range(self._daemon, start_height, end_height, height, True, self.BINARY_BLOCK_CTX)

        # test unspecified start
        BlockUtils.test_get_blocks_range(self._daemon, None, num_blocks - 1, height, True, self.BINARY_BLOCK_CTX)

        # test unspecified end
        BlockUtils.test_get_blocks_range(self._daemon, end_height - num_blocks - 1, None, height, True, self.BINARY_BLOCK_CTX)

    # Can get block hashes (binary)
    #@pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    @pytest.mark.skip(reason="Binary request not implemented")
    def test_get_block_ids_binary(self) -> None:
        # get_hashes.bin
        raise NotImplementedError("Binary request not implemented")

    # Can get a transaction by hash and without pruning
    @pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_get_tx_by_hash(self) -> None:
        # fetch tx hashses to test
        tx_hashes = TxUtils.get_confirmed_tx_hashes(self._daemon)

        # context for creating txs
        ctx = TestContext()
        ctx.is_pruned = False
        ctx.is_confirmed = True
        ctx.from_get_tx_pool = False

        # fetch each tx by hash without pruning
        for tx_hash in tx_hashes:
            tx = self._daemon.get_tx(tx_hash)
            TxUtils.test_tx(tx, ctx)

        # fetch each tx by hash with pruning
        for tx_hash in tx_hashes:
            tx = self._daemon.get_tx(tx_hash, True)
            ctx.is_pruned = True
            TxUtils.test_tx(tx, ctx)

        # fetch invalid hash
        try:
            self._daemon.get_tx("invalid tx hash")
            raise Exception("fail")
        except Exception as e:
            AssertUtils.assert_equals("Invalid transaction hash", str(e))

    # Can get transactions by hashes with and without pruning
    #@pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    @pytest.mark.skip(reason="TODO fund wallet")
    def test_get_txs_by_hashes(self) -> None:
        # fetch tx hashses to test
        tx_hashes = TxUtils.get_confirmed_tx_hashes(self._daemon)
        assert len(tx_hashes) > 0, "No tx hashes found"

        # context for creating txs
        ctx = TestContext()
        ctx.is_pruned = False
        ctx.is_confirmed = True
        ctx.from_get_tx_pool = False

        # fetch each tx by hash without pruning
        txs = self._daemon.get_txs(tx_hashes)
        assert len(txs) == len(tx_hashes), f"Expected len(txs) == len(tx_hashes), got {len(txs)} == {len(tx_hashes)}"
        for tx in txs:
            TxUtils.test_tx(tx, ctx)

        # fetch each tx by hash with pruning
        txs = self._daemon.get_txs(tx_hashes, True)
        ctx.is_pruned = True
        assert len(txs) == len(tx_hashes), f"Expected len(txs) == len(tx_hashes), got {len(txs)} == {len(tx_hashes)}"
        for tx in txs:
            TxUtils.test_tx(tx, ctx)

        # fetch missing hash
        dest = MoneroDestination()
        dest.address = self._wallet.get_primary_address()
        dest.amount = TxUtils.MAX_FEE
        config = MoneroTxConfig()
        config.account_index = 0
        config.destinations.append(dest)
        tx = self._wallet.create_tx(config)
        assert tx.hash is not None
        assert self._daemon.get_tx(tx.hash) is None
        tx_hashes.append(tx.hash)
        num_txs = len(txs)
        txs = self._daemon.get_txs(tx_hashes)
        assert num_txs == len(txs)

        # fetch invalid hash
        try:
            self._daemon.get_txs(["invalid tx hash"])
            raise Exception("fail")
        except Exception as e:
            AssertUtils.assert_equals("Invalid transaction hash", str(e))

    # Can get transaction pool statistics
    #@pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    @pytest.mark.skip("TODO implement monero_wallet_rpc.get_txs()")
    def test_get_tx_pool_statistics(self):
        daemon = self._daemon
        wallet = self._wallet
        Utils.WALLET_TX_TRACKER.wait_for_wallet_txs_to_clear_pool(daemon, Utils.SYNC_PERIOD_IN_MS, [wallet])
        tx_ids: list[str] = []
        try:
            # submit txs to the pool but don't relay
            i = 1
            while 1 < 3:
                # submit tx hex
                tx: MoneroTx = TxUtils.get_unrelayed_tx(wallet, i)
                assert tx.full_hex is not None
                result: MoneroSubmitTxResult = self._daemon.submit_tx_hex(tx.full_hex, True)
                AssertUtils.assert_true(result.is_good, json.dumps(result))
                assert tx.hash is not None
                tx_ids.append(tx.hash)

                # get tx pool stats
                stats: MoneroTxPoolStats = self._daemon.get_tx_pool_stats()
                assert stats.num_txs is not None
                AssertUtils.assert_true(stats.num_txs > i - 1)
                DaemonUtils.test_tx_pool_stats(stats)
                i += 1

        except Exception as e:
            # flush txs
            self._daemon.flush_tx_pool(tx_ids)
            raise e

    # Can get the miner tx sum
    @pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_get_miner_tx_sum(self) -> None:
        tx_sum = self._daemon.get_miner_tx_sum(0, min(5000, self._daemon.get_height()))
        DaemonUtils.test_miner_tx_sum(tx_sum)

    # Can get fee estimate
    @pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_get_fee_estimate(self) -> None:
        fee_estimate = self._daemon.get_fee_estimate()
        GenUtils.test_unsigned_big_integer(fee_estimate.fee, True)
        assert len(fee_estimate.fees) == 4, "Exptected 4 fees"
        for fee in fee_estimate.fees:
            GenUtils.test_unsigned_big_integer(fee, True)
        GenUtils.test_unsigned_big_integer(fee_estimate.quantization_mask, True)

    # Can get general information
    @pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_get_general_information(self):
        info: MoneroDaemonInfo = self._daemon.get_info()
        DaemonUtils.test_info(info)

    # Can get sync information
    @pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_get_sync_information(self):
        sync_info: MoneroDaemonSyncInfo = self._daemon.get_sync_info()
        DaemonUtils.test_sync_info(sync_info)

    # Can get hard fork information
    @pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_get_hard_fork_information(self):
        hard_fork_info: MoneroHardForkInfo = self._daemon.get_hard_fork_info()
        DaemonUtils.test_hard_fork_info(hard_fork_info)

    # Can get alternative chains
    @pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_get_alternative_chains(self):
        alt_chains: list[MoneroAltChain] = self._daemon.get_alt_chains()
        for altChain in alt_chains:
            DaemonUtils.test_alt_chain(altChain)

    # Can get alternative block hashes
    @pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_get_alternative_block_ids(self):
        alt_block_ids: list[str] = self._daemon.get_alt_block_hashes()
        for altBlockId in alt_block_ids:
            AssertUtils.assert_not_none(altBlockId)
            AssertUtils.assert_equals(64, len(altBlockId)) # TODO: common validation

    # Can get, set, and reset a download bandwidth limit
    @pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_set_download_bandwidth(self):
        init_val: int = self._daemon.get_download_limit()
        AssertUtils.assert_true(init_val > 0)
        set_val: int = init_val * 2
        self._daemon.set_download_limit(set_val)
        AssertUtils.assert_equals(set_val, self._daemon.get_download_limit())
        reset_val: int = self._daemon.reset_download_limit()
        AssertUtils.assert_equals(init_val, reset_val)

        # test invalid limits
        try:
            self._daemon.set_download_limit(0)
            raise Exception("Should have thrown error on invalid input")
        except Exception as e:
            AssertUtils.assert_equals("Download limit must be an integer greater than 0", str(e))

        AssertUtils.assert_equals(self._daemon.get_download_limit(), init_val)

    # Can get, set, and reset an upload bandwidth limit
    @pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_set_upload_bandwidth(self):
        init_val: int = self._daemon.get_upload_limit()
        AssertUtils.assert_true(init_val > 0)
        set_val: int = init_val * 2
        self._daemon.set_upload_limit(set_val)
        AssertUtils.assert_equals(set_val, self._daemon.get_upload_limit())
        reset_val: int = self._daemon.reset_upload_limit()
        AssertUtils.assert_equals(init_val, reset_val)

        # test invalid limits
        try:
            self._daemon.set_upload_limit(0)
            raise Exception("Should have thrown error on invalid input")
        except Exception as e:
            AssertUtils.assert_equals("Upload limit must be an integer greater than 0", str(e))

        AssertUtils.assert_equals(init_val, self._daemon.get_upload_limit())

    # Can get peers with active incoming or outgoing connections
    @pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_get_peers(self):
        peers: list[MoneroPeer] = self._daemon.get_peers()
        AssertUtils.assert_false(len(peers) == 0, "Daemon has no incoming or outgoing peers to test")
        for peer in peers:
            DaemonUtils.test_peer(peer)

    # Can get all known peers which may be online or offline
    @pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_get_known_peers(self):
        peers: list[MoneroPeer] = self._daemon.get_known_peers()
        if Utils.REGTEST:
            AssertUtils.assert_true(len(peers) == 0, "Regtest daemon should not have known peers to test")
        else:
            AssertUtils.assert_false(len(peers) == 0, "Daemon has no known peers to test")

        for peer in peers:
            DaemonUtils.test_known_peer(peer, False)

    # Can limit the number of outgoing peers
    @pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_set_outgoing_peer_limit(self):
        self._daemon.set_outgoing_peer_limit(0)
        self._daemon.set_outgoing_peer_limit(8)
        self._daemon.set_outgoing_peer_limit(10)

    # Can limit the number of incoming peers
    @pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_set_incoming_peer_limit(self):
        self._daemon.set_incoming_peer_limit(0)
        self._daemon.set_incoming_peer_limit(8)
        self._daemon.set_incoming_peer_limit(10)

    # Can notify listeners when a new block is added to the chain
    @pytest.mark.skipif(Utils.LITE_MODE is True or Utils.TEST_NOTIFICATIONS is False, reason="TEST_NOTIFICATIONS disabled")
    def test_block_listener(self):
        try:
            # start mining if possible to help push the network along
            address: str = self._wallet.get_primary_address()
            try:
                self._daemon.start_mining(address, 8, False, True)
            except Exception as e:
                logger.warning(f"[!]: {str(e)}")

            # register a listener
            listener: MoneroDaemonListener = MoneroDaemonListener()
            self._daemon.add_listener(listener)

            # wait for next block notification
            header: MoneroBlockHeader = self._daemon.wait_for_next_block_header()
            self._daemon.remove_listener(listener) # unregister listener so daemon does not keep polling
            BlockUtils.test_block_header(header, True)

            # test that listener was called with equivalent header
            AssertUtils.assert_equals(header, listener.last_header)
        except Exception as e:
            raise e
        finally:
            # stop mining
            try :
                self._daemon.stop_mining()
            except Exception as e:
                logger.warning(f"[!]: {str(e)}")

    # Can ban a peer
    @pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_ban_peer(self):
        # set ban
        host = "192.168.1.51"
        ban = MoneroBan()
        ban.host = host
        ban.is_banned = True
        ban.seconds = 60
        self._daemon.set_peer_ban(ban)

        # test ban
        bans = self._daemon.get_peer_bans()
        found: bool = False
        for peer_ban in bans:
            DaemonUtils.test_ban(peer_ban)
            if host == peer_ban.host:
                found = True

        assert found, f"Could not find peer ban {host}"

    # Can ban peers
    @pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_ban_peers(self):
        # set bans
        addr1 = "192.168.1.52"
        addr2 = "192.168.1.53"
        ban1 = MoneroBan()
        ban1.host = addr1
        ban1.is_banned = True
        ban1.seconds = 60
        ban2 = MoneroBan()
        ban2.host = addr2
        ban2.is_banned = True
        ban2.seconds = 60
        bans: list[MoneroBan] = []
        bans.append(ban1)
        bans.append(ban2)
        self._daemon.set_peer_bans(bans)

        # test bans
        bans = self._daemon.get_peer_bans()
        found1: bool = False
        found2: bool = False
        for aBan in bans:
            DaemonUtils.test_ban(aBan)
            if addr1 == aBan.host:
                found1 = True
            if addr2 == aBan.host:
                found2 = True

        assert found1, f"Could not find peer ban1 {addr1}"
        assert found2, f"Could not find peer ban2 {addr2}"

    # Can start and stop mining
    @pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_mining(self):
        # stop mining at beginning of test
        try:
            self._daemon.stop_mining()
        except Exception as e:
            logger.warning(f"[!]: {str(e)}")

        # generate address to mine to
        address: str = self._wallet.get_primary_address()

        # start mining
        self._daemon.start_mining(address, 2, False, True)

        # stop mining
        self._daemon.stop_mining()

    # Can get mining status
    @pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_get_mining_status(self):
        try:
            # stop mining at beginning of test
            try:
                self._daemon.stop_mining()
            except Exception as e:
                logger.warning(f"[!]: {str(e)}")

            # test status without mining
            status: MoneroMiningStatus = self._daemon.get_mining_status()
            AssertUtils.assert_equals(False, status.is_active)
            AssertUtils.assert_is_none(status.address, f"Mining address is not None: {status.address}")
            AssertUtils.assert_equals(0, status.speed)
            AssertUtils.assert_equals(0, status.num_threads)
            AssertUtils.assert_is_none(status.is_background)

            # test status with mining
            address: str = self._wallet.get_primary_address()
            thread_count: int = 3
            is_background: bool = False
            self._daemon.start_mining(address, thread_count, is_background, True)
            status = self._daemon.get_mining_status()
            assert status.speed is not None
            AssertUtils.assert_equals(True, status.is_active)
            AssertUtils.assert_equals(address, status.address)
            AssertUtils.assert_true(status.speed >= 0)
            AssertUtils.assert_equals(thread_count, status.num_threads)
            AssertUtils.assert_equals(is_background, status.is_background)
        except Exception as e:
            raise e
        finally:
            # stop mining at end of test
            try:
                self._daemon.stop_mining()
            except Exception as e:
                logger.warning(f"[!]: {str(e)}")

    # Can submit a mined block to the network
    @pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    @pytest.mark.flaky(reruns=5, reruns_delay=5)
    def test_submit_mined_block(self):
        # get template to mine on
        template: MoneroBlockTemplate = self._daemon.get_block_template(Utils.ADDRESS)
        assert template.block_template_blob is not None

        # TODO monero rpc: way to get mining nonce when found in order to submit?

        # try to submit block hashing blob without nonce
        try:
            self._daemon.submit_block(template.block_template_blob)
            raise Exception("Should have thrown error")
        except Exception as e:
            # AssertUtils.assert_equals(-7, (int) e.getCode())
            AssertUtils.assert_equals("Block not accepted", str(e))

    # Can prune the blockchain
    @pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_prune_blockchain(self):
        result: MoneroPruneResult = self._daemon.prune_blockchain(True)

        if result.is_pruned:
            assert result.pruning_seed is not None
            AssertUtils.assert_true(result.pruning_seed > 0)
        else:
            AssertUtils.assert_equals(0, result.pruning_seed)

    # Can check for an update
    @pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    @pytest.mark.flaky(reruns=5, reruns_delay=5)
    def test_check_for_update(self):
        result: MoneroDaemonUpdateCheckResult = self._daemon.check_for_update()
        DaemonUtils.test_update_check_result(result)

    # Can download an update
    @pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    @pytest.mark.flaky(reruns=5, reruns_delay=5)
    def test_download_update(self):
        # download to default path
        result: MoneroDaemonUpdateDownloadResult = self._daemon.download_update()
        DaemonUtils.test_update_download_result(result, None)

        # download to defined path
        path: str = "test_download_" + str(time.time()) + ".tar.bz2"
        result = self._daemon.download_update(path)
        DaemonUtils.test_update_download_result(result, path)

        # test invalid path
        if result.is_update_available:
            try:
                self._daemon.download_update("./ohhai/there")
                raise Exception("Should have thrown error")
            except Exception as e:
                AssertUtils.assert_not_equals(str(e), "Should have thrown error")
                # AssertUtils.assert_equals(500, (int) e.getCode()) # TODO monerod: this causes a 500 in daemon rpc

    # Can be stopped
    #@pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    @pytest.mark.skip(reason="test is disabled to not interfere with other tests")
    def test_stop(self):
        # stop the daemon
        self._daemon.stop()

        # give the daemon time to shut down
        # TimeUnit.MILLISECONDS.sleep(Utils.SYNC_PERIOD_IN_MS)

        # try to interact with the daemon
        try:
            self._daemon.get_height()
            raise Exception("Should have thrown error")
        except Exception as e:
            AssertUtils.assert_not_equals("Should have thrown error", str(e))

    #endregion
