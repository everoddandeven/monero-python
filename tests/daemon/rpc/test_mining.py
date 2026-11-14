from __future__ import annotations

import logging

import pytest
from monero import (
    MoneroAddAuxiliaryPowResult,
    MoneroAuxiliaryPow,
    MoneroBlockTemplate,
    MoneroDaemonRpc,
    MoneroMinerData,
    MoneroMiningStatus,
    MoneroWalletRpc,
)

from utils import DaemonUtils, MiningUtils, TestUtils as Utils
from .base_test_monero_daemon_rpc import BaseTestMoneroDaemonRpc

logger: logging.Logger = logging.getLogger("TestMoneroDaemonRpcMining")


@pytest.mark.integration
class TestMoneroDaemonRpcMining(BaseTestMoneroDaemonRpc):
    """Rpc daemon mining integration tests."""

    # Can start and stop mining
    @pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_mining(self, daemon: MoneroDaemonRpc, wallet: MoneroWalletRpc) -> None:
        # stop mining at beginning of test
        MiningUtils.try_stop_mining(daemon)

        # generate address to mine to
        address: str = wallet.get_primary_address()

        # start mining
        daemon.start_mining(address, 1, False, True)

        # stop mining
        daemon.stop_mining()

    # Can get mining status
    @pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_get_mining_status(self, daemon: MoneroDaemonRpc, wallet: MoneroWalletRpc) -> None:
        try:
            # stop mining at beginning of test
            MiningUtils.try_stop_mining(daemon)

            # test status without mining
            status: MoneroMiningStatus = daemon.get_mining_status()
            logger.debug(f"Testing mining status: {status.serialize()}")
            assert status.is_active is False
            assert status.address is None, f"Mining address is not None: {status.address}"
            assert 0 == status.speed
            assert 0 == status.num_threads
            assert status.is_background is None

            # test status with mining
            address: str = wallet.get_primary_address()
            thread_count: int = 1
            is_background: bool = False
            daemon.start_mining(address, thread_count, is_background, True)
            status = daemon.get_mining_status()
            logger.debug(f"Testing mining status: {status.serialize()}")
            assert status.speed is not None
            assert status.is_active is True
            assert address == status.address
            assert status.speed >= 0
            assert thread_count == status.num_threads
            assert is_background == status.is_background
        finally:
            # stop mining at end of test
            MiningUtils.try_stop_mining(daemon)

    # Can submit a mined block to the network
    @pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    @pytest.mark.flaky(reruns=5, reruns_delay=5, only_rerun=[])
    def test_submit_mined_block(self, daemon: MoneroDaemonRpc) -> None:
        # get template to mine on
        template: MoneroBlockTemplate = daemon.get_block_template(Utils.ADDRESS)
        assert template.block_template_blob is not None

        # TODO monero rpc: way to get mining nonce when found in order to submit?

        # try to submit block hashing blob without nonce
        with pytest.raises(Exception) as exc_info:
            daemon.submit_block(template.block_template_blob)
        assert str(exc_info.value) == "Block not accepted"

    # Can get the data needed to mine a block
    @pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_get_miner_data(self, daemon: MoneroDaemonRpc) -> None:
        data: MoneroMinerData = daemon.get_miner_data()
        DaemonUtils.test_miner_data(data)

    # Can calculate a block's proof-of-work hash
    @pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_calculate_pow(self, daemon: MoneroDaemonRpc) -> None:
        data: MoneroMinerData = daemon.get_miner_data()
        template: MoneroBlockTemplate = daemon.get_block_template(Utils.ADDRESS)
        assert data.major_version is not None
        assert data.height is not None
        assert data.seed_hash is not None
        assert template.block_template_blob is not None

        pow_hash: str = daemon.calculate_pow(data.major_version, data.height, template.block_template_blob, data.seed_hash)
        assert len(pow_hash) == 64

        with pytest.raises(Exception) as exc_info:
            daemon.calculate_pow(data.major_version, data.height, "", data.seed_hash)
        assert str(exc_info.value) == "Must provide a block blob to hash"

    # Can add auxiliary proof-of-work to a block template
    @pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_add_auxiliary_pow(self, daemon: MoneroDaemonRpc) -> None:
        template: MoneroBlockTemplate = daemon.get_block_template(Utils.ADDRESS)
        assert template.block_template_blob is not None

        aux_pow: MoneroAuxiliaryPow = MoneroAuxiliaryPow("11" * 32, "22" * 32)
        result: MoneroAddAuxiliaryPowResult = daemon.add_auxiliary_pow(template.block_template_blob, [aux_pow])
        assert result.block_template_blob is not None and len(result.block_template_blob) > 0
        assert result.block_hashing_blob is not None and len(result.block_hashing_blob) > 0
        assert result.merkle_root is not None and len(result.merkle_root) == 64
        assert result.merkle_tree_depth is not None and result.merkle_tree_depth >= 0
        assert len(result.aux_pow) == 1
        assert result.aux_pow[0].id is not None and len(result.aux_pow[0].id) == 64
        assert result.aux_pow[0].hash is not None and len(result.aux_pow[0].hash) == 64

        with pytest.raises(Exception) as exc_info:
            daemon.add_auxiliary_pow(template.block_template_blob, [])
        assert str(exc_info.value) == "Must provide auxiliary proof of work to add"
