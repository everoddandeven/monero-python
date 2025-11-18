import pytest
import time
import json

from monero import (
    MoneroDaemonRpc, MoneroVersion, MoneroBlockHeader, MoneroBlockTemplate,
    MoneroBlock, MoneroWalletRpc, MoneroMiningStatus, MoneroPruneResult,
    MoneroDaemonUpdateCheckResult, MoneroDaemonUpdateDownloadResult,
    MoneroDaemonListener, MoneroPeer, MoneroDaemonInfo, MoneroDaemonSyncInfo,
    MoneroHardForkInfo, MoneroAltChain, MoneroTx, MoneroSubmitTxResult,
    MoneroTxPoolStats
)
from utils import MoneroTestUtils as Utils, TestContext, BinaryBlockContext


@pytest.mark.monero_daemon_rpc
class TestMoneroDaemonRpc:
    _daemon: MoneroDaemonRpc = Utils.get_daemon_rpc()
    _wallet: MoneroWalletRpc = Utils.get_wallet_rpc()
    BINARY_BLOCK_CTX: BinaryBlockContext = BinaryBlockContext()

    # Can get the daemon's version
    @pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, "TEST_NON_RELAYS disabled")
    def test_get_version(self):
        version: MoneroVersion = self._daemon.get_version()
        assert version.number is not None
        Utils.assert_true(version.number > 0)
        Utils.assert_not_none(version.is_release)

    # Can indicate if it's trusted
    @pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, "TEST_NON_RELAYS disabled")
    def test_is_trusted(self):
        self._daemon.is_trusted()

    # Can get the blockchain height
    @pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, "TEST_NON_RELAYS disabled")
    def test_get_height(self):
        height = self._daemon.get_height()
        Utils.assert_true(height > 0, "Height must be greater than 0")

    # Can get a block hash by height
    @pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, "TEST_NON_RELAYS disabled")
    def test_get_block_id_by_height(self):
        last_header: MoneroBlockHeader = self._daemon.get_last_block_header()
        assert last_header.height is not None
        hash_str: str = self._daemon.get_block_hash(last_header.height)
        Utils.assert_not_none(hash_str)
        Utils.assert_equals(64, len(hash_str))

    # Can get a block template
    @pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, "TEST_NON_RELAYS disabled")
    def test_get_block_template(self):
        template: MoneroBlockTemplate = self._daemon.get_block_template(Utils.ADDRESS, 2)
        Utils.test_block_template(template)

    # Can get the last block's header
    @pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, "TEST_NON_RELAYS disabled")
    def test_get_last_block_header(self):
        last_header: MoneroBlockHeader = self._daemon.get_last_block_header()
        Utils.test_block_header(last_header, True)

    # Can get a block header by hash
    @pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, "TEST_NON_RELAYS disabled")
    def test_get_block_header_by_hash(self):
        # retrieve by hash of last block
        last_header: MoneroBlockHeader = self._daemon.get_last_block_header()
        assert last_header.height is not None
        hash_str: str = self._daemon.get_block_hash(last_header.height)
        header: MoneroBlockHeader = self._daemon.get_block_header_by_hash(hash_str)
        Utils.test_block_header(header, True)
        Utils.assert_equals(last_header, header)

        # retrieve by hash of previous to last block
        hash_str = self._daemon.get_block_hash(last_header.height - 1)
        header = self._daemon.get_block_header_by_hash(hash_str)
        Utils.test_block_header(header, True)
        Utils.assert_equals(last_header.height - 1, header.height)

    # Can get a block header by height
    @pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, "TEST_NON_RELAYS disabled")
    def test_get_block_header_by_height(self):
        # retrieve by height of last block
        last_header: MoneroBlockHeader = self._daemon.get_last_block_header()
        assert last_header.height is not None
        header: MoneroBlockHeader = self._daemon.get_block_header_by_height(last_header.height)
        Utils.test_block_header(header, True)
        Utils.assert_equals(last_header, header)

        # retrieve by height of previous to last block
        header = self._daemon.get_block_header_by_height(last_header.height - 1)
        Utils.test_block_header(header, True)
        Utils.assert_equals(last_header.height - 1, header.height)

    # Can get block headers by range
    # TODO: test start with no end, vice versa, inclusivity
    @pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, "TEST_NON_RELAYS disabled")
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
        Utils.assert_equals(num_blocks, len(headers))
        i: int = 0
        while i < num_blocks:
            header: MoneroBlockHeader = headers[i]
            Utils.assert_equals(start_height + i, header.height)
            Utils.test_block_header(header, True)
            i += 1

    # Can get a block by hash
    @pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, "TEST_NON_RELAYS disabled")
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
        Utils.test_block(block, ctx)
        Utils.assert_equals(self._daemon.get_block_by_height(block.height), block)
        Utils.assert_equals(None, block.txs)

        # retrieve by hash of previous to last block
        hash_str = self._daemon.get_block_hash(last_header.height - 1)
        block = self._daemon.get_block_by_hash(hash_str)
        Utils.test_block(block, ctx)
        Utils.assert_equals(self._daemon.get_block_by_height(last_header.height - 1), block)
        Utils.assert_equals(None, block.txs)

    # Can get blocks by hash which includes transactions (binary)
    @pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, "TEST_NON_RELAYS disabled")
    def test_get_blocks_by_hash_binary(self) -> None:
        raise NotImplementedError("Not implemented")

    # Can get a block by height
    @pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, "TEST_NON_RELAYS disabled")
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
        Utils.test_block(block, ctx)
        Utils.assert_equals(self._daemon.get_block_by_height(block.height), block)

        # retrieve by height of previous to last block
        block = self._daemon.get_block_by_height(last_header.height - 1)
        Utils.test_block(block, ctx)
        Utils.assert_equals(last_header.height - 1, block.height)

    # Can get blocks by height which includes transactions (binary)
    @pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, "TEST_NON_RELAYS disabled")
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
        Utils.assert_equals(num_blocks, len(blocks))
        i = 0
        while i < len(heights):
            block: MoneroBlock = blocks[i]
            if len(block.txs) > 0:
                tx_found = True

            Utils.test_block(block, self.BINARY_BLOCK_CTX)
            Utils.assert_equals(block.height, heights[i])
            i += 1

        Utils.assert_true(tx_found, "No transactions found to test")

    # Can get transaction pool statistics
    @pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, "TEST_NON_RELAYS disabled")
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
                tx: MoneroTx = Utils.get_unrelayed_tx(wallet, i)
                assert tx.full_hex is not None
                result: MoneroSubmitTxResult = self._daemon.submit_tx_hex(tx.full_hex, True)
                Utils.assert_true(result.is_good, json.dumps(result))
                assert tx.hash is not None
                tx_ids.append(tx.hash)

                # get tx pool stats
                stats: MoneroTxPoolStats = self._daemon.get_tx_pool_stats()
                assert stats.num_txs is not None
                Utils.assert_true(stats.num_txs > i - 1)
                Utils.test_tx_pool_stats(stats)
                i += 1

        except Exception as e:
            # flush txs
            self._daemon.flush_tx_pool(tx_ids)
            raise e

    # Can get general information
    @pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, "TEST_NON_RELAYS disabled")
    def test_get_general_information(self):
        info: MoneroDaemonInfo = self._daemon.get_info()
        Utils.test_info(info)

    # Can get sync information
    @pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, "TEST_NON_RELAYS disabled")
    def test_get_sync_information(self):
        sync_info: MoneroDaemonSyncInfo = self._daemon.get_sync_info()
        Utils.test_sync_info(sync_info)

    # Can get hard fork information
    @pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, "TEST_NON_RELAYS disabled")
    def test_get_hard_fork_information(self):
        hard_fork_info: MoneroHardForkInfo = self._daemon.get_hard_fork_info()
        Utils.test_hard_fork_info(hard_fork_info)

    # Can get alternative chains
    @pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, "TEST_NON_RELAYS disabled")
    def test_get_alternative_chains(self):
        alt_chains: list[MoneroAltChain] = self._daemon.get_alt_chains()
        for altChain in alt_chains:
            Utils.test_alt_chain(altChain)

    # Can get alternative block hashes
    @pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, "TEST_NON_RELAYS disabled")
    def test_get_alternative_block_ids(self):
        alt_block_ids: list[str] = self._daemon.get_alt_block_hashes()
        for altBlockId in alt_block_ids:
            Utils.assert_not_none(altBlockId)
            Utils.assert_equals(64, len(altBlockId)) # TODO: common validation

    # Can get, set, and reset a download bandwidth limit
    @pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, "TEST_NON_RELAYS disabled")
    def test_set_download_bandwidth(self):
        init_val: int = self._daemon.get_download_limit()
        Utils.assert_true(init_val > 0)
        set_val: int = init_val * 2
        self._daemon.set_download_limit(set_val)
        Utils.assert_equals(set_val, self._daemon.get_download_limit())
        reset_val: int = self._daemon.reset_download_limit()
        Utils.assert_equals(init_val, reset_val)

        # test invalid limits
        try:
            self._daemon.set_download_limit(0)
            raise Exception("Should have thrown error on invalid input")
        except Exception as e:
            Utils.assert_equals("Download limit must be an integer greater than 0", str(e))

        Utils.assert_equals(self._daemon.get_download_limit(), init_val)

    # Can get, set, and reset an upload bandwidth limit
    @pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, "TEST_NON_RELAYS disabled")
    def test_set_upload_bandwidth(self):
        init_val: int = self._daemon.get_upload_limit()
        Utils.assert_true(init_val > 0)
        set_val: int = init_val * 2
        self._daemon.set_upload_limit(set_val)
        Utils.assert_equals(set_val, self._daemon.get_upload_limit())
        reset_val: int = self._daemon.reset_upload_limit()
        Utils.assert_equals(init_val, reset_val)

        # test invalid limits
        try:
            self._daemon.set_upload_limit(0)
            raise Exception("Should have thrown error on invalid input")
        except Exception as e:
            Utils.assert_equals("Upload limit must be an integer greater than 0", str(e))

        Utils.assert_equals(init_val, self._daemon.get_upload_limit())

    # Can get peers with active incoming or outgoing connections
    @pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, "TEST_NON_RELAYS disabled")
    def test_get_peers(self):
        peers: list[MoneroPeer] = self._daemon.get_peers()
        Utils.assert_false(len(peers) == 0, "Daemon has no incoming or outgoing peers to test")
        for peer in peers:
            Utils.test_peer(peer)

    # Can get all known peers which may be online or offline
    @pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, "TEST_NON_RELAYS disabled")
    def test_get_known_peers(self):
        peers: list[MoneroPeer] = self._daemon.get_known_peers()
        Utils.assert_false(len(peers) == 0, "Daemon has no known peers to test")
        for peer in peers:
            Utils.test_known_peer(peer, False)

    # Can limit the number of outgoing peers
    @pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, "TEST_NON_RELAYS disabled")
    def test_set_outgoing_peer_limit(self):
        self._daemon.set_outgoing_peer_limit(0)
        self._daemon.set_outgoing_peer_limit(8)
        self._daemon.set_outgoing_peer_limit(10)

    # Can limit the number of incoming peers
    @pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, "TEST_NON_RELAYS disabled")
    def test_set_incoming_peer_limit(self):
        self._daemon.set_incoming_peer_limit(0)
        self._daemon.set_incoming_peer_limit(8)
        self._daemon.set_incoming_peer_limit(10)

    # Can notify listeners when a new block is added to the chain
    @pytest.mark.skipif(Utils.LITE_MODE is True or Utils.TEST_NOTIFICATIONS is False)
    def test_block_listener(self):
        try:
            # start mining if possible to help push the network along
            address: str = self._wallet.get_primary_address()
            try:
                self._daemon.start_mining(address, 8, False, True)
            except Exception as e:
                print(f"[!]: {str(e)}")

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
            except Exception as e:
                print(f"[!]: {str(e)}")

    # Can start and stop mining
    @pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, "TEST_NON_RELAYS disabled")
    def test_mining(self):
        # stop mining at beginning of test
        try:
            self._daemon.stop_mining()
        except Exception as e:
            print(f"[!]: {str(e)}")

        # generate address to mine to
        address: str = self._wallet.get_primary_address()

        # start mining
        self._daemon.start_mining(address, 2, False, True)

        # stop mining
        self._daemon.stop_mining()

    # Can get mining status
    @pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, "TEST_NON_RELAYS disabled")
    def test_get_mining_status(self):
        try:
            # stop mining at beginning of test
            try:
                self._daemon.stop_mining()
            except Exception as e:
                print(f"[!]: {str(e)}")

            # test status without mining
            status: MoneroMiningStatus = self._daemon.get_mining_status()
            Utils.assert_equals(False, status.is_active)
            Utils.assert_is_none(status.address)
            Utils.assert_equals(0, status.speed)
            Utils.assert_equals(0, status.num_threads)
            Utils.assert_is_none(status.is_background)

            # test status with mining
            address: str = self._wallet.get_primary_address()
            thread_count: int = 3
            is_background: bool = False
            self._daemon.start_mining(address, thread_count, is_background, True)
            status = self._daemon.get_mining_status()
            assert status.speed is not None
            Utils.assert_equals(True, status.is_active)
            Utils.assert_equals(address, status.address)
            Utils.assert_true(status.speed >= 0)
            Utils.assert_equals(thread_count, status.num_threads)
            Utils.assert_equals(is_background, status.is_background)
        except Exception as e:
            raise e
        finally:
            # stop mining at end of test
            try:
                self._daemon.stop_mining()
            except Exception as e:
                print(f"[!]: {str(e)}")

    # Can submit a mined block to the network
    @pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, "TEST_NON_RELAYS disabled")
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
            # Utils.assert_equals(-7, (int) e.getCode())
            Utils.assert_equals("Block not accepted", str(e))

    # Can prune the blockchain
    @pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, "TEST_NON_RELAYS disabled")
    def test_prune_blockchain(self):
        result: MoneroPruneResult = self._daemon.prune_blockchain(True)

        if result.is_pruned:
            assert result.pruning_seed is not None
            Utils.assert_true(result.pruning_seed > 0)
        else:
            Utils.assert_equals(0, result.pruning_seed)

    # Can check for an update
    @pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, "TEST_NON_RELAYS disabled")
    def test_check_for_update(self):
        result: MoneroDaemonUpdateCheckResult = self._daemon.check_for_update()
        Utils.test_update_check_result(result)

    # Can download an update
    @pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, "TEST_NON_RELAYS disabled")
    def test_download_update(self):
        # download to default path
        result: MoneroDaemonUpdateDownloadResult = self._daemon.download_update()
        Utils.test_update_download_result(result, None)

        # download to defined path
        path: str = "test_download_" + str(time.time()) + ".tar.bz2"
        result = self._daemon.download_update(path)
        Utils.test_update_download_result(result, path)

        # test invalid path
        if result.is_update_available:
            try:
                self._daemon.download_update("./ohhai/there")
                raise Exception("Should have thrown error")
            except Exception as e:
                Utils.assert_not_equals(str(e), "Should have thrown error")
                # Utils.assert_equals(500, (int) e.getCode()) # TODO monerod: this causes a 500 in daemon rpc

    # Can be stopped
    @pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, "TEST_NON_RELAYS disabled")
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
            Utils.assert_not_equals("Should have thrown error", str(e))
