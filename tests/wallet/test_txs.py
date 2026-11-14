from __future__ import annotations

import logging
from random import shuffle
from typing import Optional

import pytest
from monero import (
    MoneroBlock,
    MoneroOutputQuery,
    MoneroTransferQuery,
    MoneroTxQuery,
    MoneroTxWallet,
    MoneroUtils,
    MoneroWallet,
)
from typing_extensions import override

from utils import (
    AssertUtils,
    GenUtils,
    StringUtils,
    TestUtils,
    TransferUtils,
    TxContext,
    TxWalletUtils,
    WalletTxsUtils,
)
from .base_test_monero_wallet import BaseTestMoneroWallet
from .wallet_support import FullWalletSupport, RpcWalletSupport, KeysWalletSupport

logger: logging.Logger = logging.getLogger("TestMoneroWalletTxs")


class BaseTestMoneroWalletTxs(BaseTestMoneroWallet):
    """Common wallet txs tests."""

    # Can get transactions in the wallet
    @pytest.mark.skipif(TestUtils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_get_txs_wallet(self, wallet: MoneroWallet) -> None:
        #non_default_incoming: bool = False
        txs: list[MoneroTxWallet] = WalletTxsUtils.get_and_test_txs(wallet, None, None, True, TestUtils.REGTEST)
        assert len(txs) > 0, "Wallet has no txs to test"
        # TODO make consistent with test funded wallet
        # assert TestUtils.FIRST_RECEIVE_HEIGHT == txs[0].get_height(), "First tx's restore height must match the restore height in TestUtils"

        # build test context
        ctx: TxContext = TxContext()
        ctx.wallet = wallet

        # test each transaction
        block_per_height: dict[int, MoneroBlock] = {}
        for i, tx in enumerate(txs):
            TxWalletUtils.test_tx_wallet(tx, ctx)

            # test merging equivalent txs
            it: MoneroTxWallet = txs[i] # is the same as tx
            copy1: MoneroTxWallet = it.copy()
            copy2: MoneroTxWallet = it.copy()

            if copy1.is_confirmed:
                assert it.block is not None
                copy1.block = it.block.copy()
                copy1.block.txs = [copy1]

            if copy2.is_confirmed:
                assert it.block is not None
                copy2.block = it.block.copy()
                copy2.block.txs = [copy2]

            copy1.merge(copy2)
            TxWalletUtils.test_tx_wallet(copy1, ctx)

            # find non-default incoming
            for transfer in it.incoming_transfers:
                assert transfer.account_index is not None
                assert transfer.subaddress_index is not None
                #if transfer.account_index != 0 and transfer.subaddress_index != 0:
                #    non_default_incoming = True

            # ensure unique block reference per height
            if it.is_confirmed:
                h: int | None = it.get_height()
                assert h is not None
                block: MoneroBlock | None = block_per_height.get(h)
                if block is None:
                    assert it.block is not None
                    block_per_height[i] = it.block
                else:
                    AssertUtils.assert_equals(block, it.block)
                    assert block == it.block, "Block references for same height must be same"

    # Can get transactions by hash
    @pytest.mark.skipif(TestUtils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_get_txs_by_hash(self, wallet: MoneroWallet) -> None:
        # max number of txs to test
        max_num_txs: int = 10

        # fetch all txs for testing
        txs: list[MoneroTxWallet] = wallet.get_txs()
        num_txs: int = len(txs)
        assert num_txs > 1, f"Test requires at least 2 txs to fetch by hash, got {num_txs}"

        # randomly pick a few for fetching by hash
        shuffle(txs)
        txs = txs[0:min(max_num_txs, num_txs)]

        # test fetching by hash
        tx_hash: str | None = txs[0].hash
        assert tx_hash is not None
        fetched_tx: MoneroTxWallet | None = wallet.get_tx(tx_hash)
        assert fetched_tx is not None
        assert tx_hash == fetched_tx.hash
        TxWalletUtils.test_tx_wallet(fetched_tx)

        # test fetching by hashes
        tx_id1: str | None = txs[0].hash
        tx_id2: str | None = txs[1].hash
        assert tx_id1 is not None
        assert tx_id2 is not None
        fetched_txs: list[MoneroTxWallet] = wallet.get_txs([tx_id1, tx_id2])
        num_fetched_txs: int = len(fetched_txs)
        assert num_fetched_txs == 2, f"Expected 2 txs, got {num_fetched_txs}"

        # test fetching by hashes as collection
        tx_hashes: list[str] = []
        for tx in txs:
            assert tx.hash is not None
            tx_hashes.append(tx.hash)

        fetched_txs = wallet.get_txs(tx_hashes)
        assert len(txs) == len(fetched_txs)
        for i, tx in enumerate(txs):
            fetched_tx = fetched_txs[i]
            assert tx.hash == fetched_tx.hash
            TxWalletUtils.test_tx_wallet(fetched_tx)

        # test fetching with missing tx hashes
        missing_hash: str = "d01ede9cde813b2a693069b640c4b99c5adbdb49fbbd8da2c16c8087d0c3e320"
        tx_hashes.append(missing_hash)
        fetched_txs = wallet.get_txs(tx_hashes)
        assert len(txs) == len(fetched_txs)
        for i, tx in enumerate(txs):
            fetched_tx = fetched_txs[i]
            assert tx.hash == fetched_tx.hash
            TxWalletUtils.test_tx_wallet(fetched_tx)

    # Can get transactions with additional configuration
    @pytest.mark.skipif(TestUtils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_get_txs_with_query(self, wallet: MoneroWallet) -> None:
        # get random transactions for testing
        random_txs: list[MoneroTxWallet] = WalletTxsUtils.get_random_transactions(wallet, None, 3, 5)
        for random_tx in random_txs:
            TxWalletUtils.test_tx_wallet(random_tx, None)

        # get transactions by hash
        tx_hashes: list[str] = []
        for random_tx in random_txs:
            assert random_tx.hash is not None
            tx_hashes.append(random_tx.hash)
            query: MoneroTxQuery = MoneroTxQuery()
            query.hash = random_tx.hash
            txs: list[MoneroTxWallet] = WalletTxsUtils.get_and_test_txs(wallet, query, None, True, TestUtils.REGTEST)
            assert len(txs) == 1
            # txs change with chain so check mergeability
            merged: MoneroTxWallet = txs[0]
            merged.merge(random_tx.copy())
            TxWalletUtils.test_tx_wallet(merged)

        # get transactions by hashes
        query = MoneroTxQuery()
        query.hashes = tx_hashes
        txs = WalletTxsUtils.get_and_test_txs(wallet, query, None, None, TestUtils.REGTEST)
        assert len(txs) == len(random_txs)
        for tx in txs:
            assert tx.hash in tx_hashes

        # get transactions with an outgoing transfer
        ctx: TxContext = TxContext()
        ctx.has_outgoing_transfer = True
        query = MoneroTxQuery()
        query.is_outgoing = True
        txs = WalletTxsUtils.get_and_test_txs(wallet, query, ctx, True, TestUtils.REGTEST)
        for tx in txs:
            assert tx.is_outgoing is True
            assert tx.outgoing_transfer is not None
            TransferUtils.test_transfer(tx.outgoing_transfer, None)

        # get transactions without an outgoing transfer
        ctx.has_outgoing_transfer = False
        query = MoneroTxQuery()
        query.is_outgoing = False
        txs = WalletTxsUtils.get_and_test_txs(wallet, query, ctx, True, TestUtils.REGTEST)
        for tx in txs:
            assert tx.outgoing_transfer is None

        # get transactions with incoming transfers
        ctx = TxContext()
        ctx.has_incoming_transfers = True
        query = MoneroTxQuery()
        query.is_incoming = True
        txs = WalletTxsUtils.get_and_test_txs(wallet, query, ctx, True, TestUtils.REGTEST)
        for tx in txs:
            assert tx.is_incoming is True
            assert len(tx.incoming_transfers) > 0
            for transfer in tx.incoming_transfers:
                TransferUtils.test_transfer(transfer, None)

        # get transactions without incoming transfers
        ctx.has_incoming_transfers = False
        query = MoneroTxQuery()
        query.is_incoming = False
        txs = WalletTxsUtils.get_and_test_txs(wallet, query, ctx, True, TestUtils.REGTEST)
        for tx in txs:
            assert tx.is_incoming is False
            assert len(tx.incoming_transfers) == 0

        # get transactions associated with an account
        account_idx: int = 1
        query = MoneroTxQuery()
        query.transfer_query = MoneroTransferQuery()
        query.transfer_query.account_index = account_idx
        txs = wallet.get_txs(query)

        for tx in txs:
            found: bool = False
            if tx.is_outgoing and tx.outgoing_transfer.account_index == account_idx: # type: ignore
                    found = True
            elif len(tx.incoming_transfers) > 0:
                for transfer in tx.incoming_transfers:
                    if transfer.account_index == account_idx:
                        found = True
                        break

            assert found, f"Transaction is not associated with account {account_idx}: \n{tx.serialize()}"

        # get txs with manually built query that are confirmed and have an outgoing transfer from account 0
        ctx = TxContext()
        ctx.has_outgoing_transfer = True
        tx_query: MoneroTxQuery = MoneroTxQuery()
        tx_query.is_confirmed = True
        tx_query.transfer_query = MoneroTransferQuery()
        tx_query.transfer_query.account_index = 0
        tx_query.transfer_query.outgoing = True
        txs = WalletTxsUtils.get_and_test_txs(wallet, tx_query, ctx, True, TestUtils.REGTEST)
        for tx in txs:
            if tx.is_confirmed is not True:
                logger.warning(f"{tx.serialize()}")
            assert tx.is_confirmed is True
            assert tx.is_outgoing is True
            assert tx.outgoing_transfer is not None
            assert tx.outgoing_transfer.account_index == 0

        # get txs with outgoing transfers that have destinations to account 1
        tx_query = MoneroTxQuery()
        tx_query.is_confirmed = True
        tx_query.transfer_query = MoneroTransferQuery()
        tx_query.transfer_query.account_index = 0
        tx_query.transfer_query.has_destinations = True

        txs = WalletTxsUtils.get_and_test_txs(wallet, tx_query, None, None, TestUtils.REGTEST)
        for tx in txs:
            assert tx.is_outgoing is True
            assert tx.outgoing_transfer is not None
            assert len(tx.outgoing_transfer.destinations) > 0

        # include outputs with transactions
        ctx = TxContext()
        ctx.include_outputs = True
        tx_query = MoneroTxQuery()
        tx_query.include_outputs = True
        txs = WalletTxsUtils.get_and_test_txs(wallet, tx_query, ctx, True, TestUtils.REGTEST)
        found: bool = False
        for tx in txs:
            if len(tx.outputs) > 0:
                found = True
            else:
                # TODO: monero-wallet-rpc: return outputs for unconfirmed txs
                assert tx.is_outgoing or (tx.is_incoming and tx.is_confirmed is False)

        assert found, "No outputs found in txs"

        # get txs with input query
        # TODO no inputs returned to filter

        # get txs with output query
        tx_query = MoneroTxQuery()
        tx_query.output_query = MoneroOutputQuery()
        tx_query.output_query.is_spent = False
        tx_query.output_query.account_index = 1
        tx_query.output_query.subaddress_index = 2
        txs = wallet.get_txs(tx_query)
        assert len(txs) > 0
        for tx in txs:
            assert len(tx.outputs) > 0
            found = False
            for output in tx.get_outputs_wallet():
                if output.is_spent is False and output.account_index == 1 and output.subaddress_index == 2:
                    found = True
                    break

            if not found:
                raise Exception("Tx does not contain specified output")

        # get unlocked txs
        tx_query = MoneroTxQuery()
        tx_query.is_locked = False
        txs = wallet.get_txs(tx_query)
        assert len(txs) > 0
        for tx in txs:
            assert tx.is_locked is False

        # get confirmed transactions sent from/to same wallet with a transfer with destinations

        tx_query = MoneroTxQuery()
        tx_query.is_incoming = True
        tx_query.is_outgoing = True
        tx_query.include_outputs = True
        tx_query.is_confirmed = True
        tx_query.transfer_query = MoneroTransferQuery()
        tx_query.transfer_query.has_destinations = True

        txs = wallet.get_txs(tx_query)
        assert len(txs) > 0, "Wallet has no incoming/outgoing txs to test; run send from/to tests"
        for tx in txs:
            assert tx.is_incoming is True
            assert tx.is_outgoing is True
            assert tx.is_confirmed is True
            assert len(tx.get_outputs_wallet()) > 0
            assert tx.outgoing_transfer is not None
            assert len(tx.outgoing_transfer.destinations) > 0

    # Can get transactions by height
    @pytest.mark.skipif(TestUtils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_get_txs_by_height(self, wallet: MoneroWallet) -> None:
        # get all confirmed txs for testing
        query: MoneroTxQuery = MoneroTxQuery()
        query.is_confirmed = True
        txs: list[MoneroTxWallet] = wallet.get_txs(query)

        # collect all tx heights
        tx_heights: list[int] = []
        for tx in txs:
            tx_height: Optional[int] = tx.get_height()
            assert tx_height is not None
            tx_heights.append(tx_height)

        # get height that most txs occur at
        height_counts: dict[int, int] = GenUtils.count_num_instances(tx_heights)
        assert len(height_counts) > 0, "Wallet has no confirmed txs; run send tests"
        height_modes: set[int] = GenUtils.get_modes(height_counts)
        mode_height: int = next(iter(height_modes))

        # fetch txs at mode height
        query = MoneroTxQuery()
        query.height = mode_height
        logger.debug(f"Getting mode txs by height; mode height {mode_height}")
        mode_txs: list[MoneroTxWallet] = wallet.get_txs(query)
        assert height_counts[mode_height] == len(mode_txs)
        for tx in mode_txs:
            assert mode_height == tx.get_height()

        # fetch txs at mode height by range
        query = MoneroTxQuery()
        query.min_height = mode_height
        query.max_height = mode_height
        logger.debug(f"Getting mode txs by range; mode height {mode_height}")
        mode_txs_by_range: list[MoneroTxWallet] = wallet.get_txs(query)
        # TODO test txs order is failing
        TxWalletUtils.assert_list_txs_equals(mode_txs, mode_txs_by_range)

        # fetch all txs by range
        query = MoneroTxQuery()
        query.min_height = txs[0].get_height()
        query.max_height = txs[-1].get_height()
        all_txs: list[MoneroTxWallet] = wallet.get_txs(query)
        # TODO test txs order is failing
        TxWalletUtils.assert_list_txs_equals(txs, all_txs)

        # test some filtered by range
        try:
            query = MoneroTxQuery()
            query.is_confirmed = True
            txs = wallet.get_txs(query)
            assert len(txs) > 0, "No transactions; run send to multiple test"

            # get and sort block heights in ascending order
            heights: list[int] = []
            for tx in txs:
                assert tx.block is not None
                assert tx.block.height is not None
                heights.append(tx.block.height)

            heights.sort()

            # pick minimum and maximum heights for filtering
            min_height: int = -1
            max_height: int = -1
            if len(heights) == 1:
                min_height = 0
                max_height = heights[0] - 1
            else:
                min_height = heights[0] + 1
                max_height = heights[-1] - 1

            # assert some transactions filtered
            unfiltered_count: int = len(txs)
            query = MoneroTxQuery()
            query.min_height = min_height
            query.max_height = max_height
            txs = WalletTxsUtils.get_and_test_txs(wallet, query, None, True, TestUtils.REGTEST)
            assert len(txs) < unfiltered_count
            for tx in txs:
                assert tx.block is not None
                assert tx.block.height is not None
                height: int = tx.block.height
                assert height >= min_height and height <= max_height

        except Exception as e:
            logger.debug(str(e))

    # Can get transactions with payment id
    @pytest.mark.skipif(TestUtils.TEST_NON_RELAYS is False or TestUtils.LITE_MODE, reason="TEST_NON_RELAYS disabled or LITE_MODE enabled")
    def test_get_txs_with_payment_ids(self, wallet: MoneroWallet) -> None:
        # get random transactions with payment ids for testing
        tx_query: MoneroTxQuery = MoneroTxQuery()
        tx_query.has_payment_id = True
        random_txs: list[MoneroTxWallet] = WalletTxsUtils.get_random_transactions(wallet, tx_query, 2, 5)
        assert len(random_txs) > 0, "No txs with payment ids to test"
        for random_tx in random_txs:
            assert random_tx.payment_id is not None and len(random_tx.payment_id) > 0

        # get transactions by payment id
        payment_ids: list[str] = []
        for tx in random_txs:
            assert tx.payment_id is not None
            payment_ids.append(tx.payment_id)

        assert len(payment_ids) > 1
        for payment_id in payment_ids:
            tx_query = MoneroTxQuery()
            tx_query.payment_id = payment_id
            txs: list[MoneroTxWallet] = WalletTxsUtils.get_and_test_txs(wallet, tx_query, None, None, TestUtils.REGTEST)
            assert len(txs) > 0
            first_payment_id: Optional[str] = txs[0].payment_id
            assert first_payment_id is not None
            MoneroUtils.validate_payment_id(first_payment_id)

        # get transactions by payment hashes
        tx_query = MoneroTxQuery()
        tx_query.payment_ids = payment_ids
        txs: list[MoneroTxWallet] = WalletTxsUtils.get_and_test_txs(wallet, tx_query, None, None, TestUtils.REGTEST)
        for tx in txs:
            assert tx.payment_id is not None
            assert tx.payment_id in payment_ids

    # Returns all known fields of txs regardless of filtering
    @pytest.mark.skipif(TestUtils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_get_txs_fields_with_filtering(self, wallet: MoneroWallet) -> None:
        # fetch wallet txs
        tx_query: MoneroTxQuery = MoneroTxQuery()
        tx_query.is_confirmed = True
        txs: list[MoneroTxWallet] = wallet.get_txs(tx_query)

        for tx in txs:
            # find tx sent to same wallet with incoming transfer in different account than src account
            if tx.outgoing_transfer is None or len(tx.incoming_transfers) == 0:
                continue
            for transfer in tx.incoming_transfers:
                if transfer.account_index == tx.outgoing_transfer.account_index:
                    continue

                # fetch tx with filtering
                tx_query = MoneroTxQuery()
                tx_query.transfer_query = MoneroTransferQuery()
                tx_query.transfer_query.incoming = True
                tx_query.transfer_query.account_index = transfer.account_index
                filtered_txs: list[MoneroTxWallet] = wallet.get_txs(tx_query)

                for filtered_tx in filtered_txs:
                    assert filtered_tx.hash is not None
                    if filtered_tx.hash == tx.hash:
                        tx.merge(filtered_tx)
                        # test is done
                        return

        raise Exception("Test requires tx sent from/to different accounts of same wallet but none found; run send tests")

    # Validates inputs when getting transactions
    @pytest.mark.skipif(TestUtils.TEST_NON_RELAYS is False or TestUtils.LITE_MODE, reason="TEST_NON_RELAYS disabled or LITE_MODE enabled")
    def test_validate_inputs_get_txs(self, wallet: MoneroWallet) -> None:
        # fetch random txs for testing
        random_txs: list[MoneroTxWallet] = WalletTxsUtils.get_random_transactions(wallet, None, 3, 5)

        # valid, invalid, and unknown tx hashes for tests
        tx_hash: str | None = random_txs[0].hash
        invalid_hash: str = "invalid_id"
        unknown_hash1: str = "6c4982f2499ece80e10b627083c4f9b992a00155e98bcba72a9588ccb91d0a61"
        unknown_hash2: str = "ff397104dd875882f5e7c66e4f852ee134f8cf45e21f0c40777c9188bc92e943"
        assert tx_hash is not None and len(tx_hash) > 0

        # fetch unknown tx hash
        fetched_tx: MoneroTxWallet | None = wallet.get_tx(unknown_hash1)
        assert fetched_tx is None

        # fetch unknown tx hash using query
        tx_query: MoneroTxQuery = MoneroTxQuery()
        tx_query.hash = unknown_hash1
        fetched_txs: list[MoneroTxWallet] = wallet.get_txs(tx_query)
        assert len(fetched_txs) == 0

        # fetch unknwon tx hash in list
        txs: list[MoneroTxWallet] = wallet.get_txs([tx_hash, unknown_hash1])
        assert len(txs) == 1
        assert txs[0].hash == tx_hash

        # fetch unknwon tx hashes in list
        txs = wallet.get_txs([tx_hash, unknown_hash1, unknown_hash2])
        assert len(txs) == 1
        assert txs[0].hash == tx_hash

        # fetch invalid hash
        fetched_tx = wallet.get_tx(invalid_hash)
        assert fetched_tx is None

        # fetch invalid hash list
        txs = wallet.get_txs([tx_hash, invalid_hash])
        assert len(txs) == 1
        assert txs[0].hash == tx_hash

        # fetch invalid hashes in list
        txs = wallet.get_txs([tx_hash, invalid_hash, "invalid_hash_2"])
        assert len(txs) == 1
        assert txs[0].hash == tx_hash

        # test collection of invalid hashes
        tx_query = MoneroTxQuery()
        tx_query.hashes = [tx_hash, invalid_hash, "invalid_hash_2"]
        txs = wallet.get_txs(tx_query)
        assert len(txs) == 1

        # test txs
        for tx in txs:
            TxWalletUtils.test_tx_wallet(tx)

    # Can get and set a transaction note
    @pytest.mark.skipif(TestUtils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_set_tx_note(self, wallet: MoneroWallet) -> None:
        txs: list[MoneroTxWallet] = WalletTxsUtils.get_random_transactions(wallet, None, 1, 5)

        # set notes
        uuid: str = StringUtils.get_random_string()

        for i, tx in enumerate(txs):
            tx_hash: str | None = tx.hash
            assert tx_hash is not None
            wallet.set_tx_note(tx_hash, f"{uuid}{i}")

        # get notes
        for i, tx in enumerate(txs):
            tx_hash: str | None = tx.hash
            assert tx_hash is not None
            assert wallet.get_tx_note(tx_hash) == f"{uuid}{i}"

    # Can get and set multiple transaction notes
    # TODO why does getting cached txs take 2 seconds when should already be cached?
    @pytest.mark.skipif(TestUtils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_set_tx_notes(self, wallet: MoneroWallet) -> None:
        # set tx notes
        uuid: str = StringUtils.get_random_string()
        txs: list[MoneroTxWallet] = wallet.get_txs()
        assert len(txs) >= 3, "Test requires 3 or more wallet transactions run send tests"
        tx_hashes: list[str] = []
        tx_notes: list[str] = []
        for i, tx_hash in enumerate(tx_hashes):
            assert tx_hash is not None
            tx_hashes.append(tx_hash)
            tx_notes.append(f"{uuid}{i}")

        wallet.set_tx_notes(tx_hashes, tx_notes)

        # get tx notes
        tx_notes: list[str] = wallet.get_tx_notes(tx_hashes)
        for i, tx_note in enumerate(tx_notes):
            assert f"{uuid}{i}" == tx_note


@pytest.mark.integration
class TestMoneroWalletFullTxs(FullWalletSupport, BaseTestMoneroWalletTxs):
    """Full wallet txs integration tests."""


@pytest.mark.integration
class TestMoneroWalletRpcTxs(RpcWalletSupport, BaseTestMoneroWalletTxs):
    """Rpc wallet txs integration tests."""


@pytest.mark.unit
class TestMoneroWalletKeysTxs(KeysWalletSupport, BaseTestMoneroWalletTxs):
    """Keys-only wallet txs unit tests."""

    @pytest.mark.not_supported
    @override
    def test_get_txs_wallet(self, wallet: MoneroWallet) -> None:
        return super().test_get_txs_wallet(wallet)

    @pytest.mark.not_supported
    @override
    def test_get_txs_by_hash(self, wallet: MoneroWallet) -> None:
        return super().test_get_txs_by_hash(wallet)

    @pytest.mark.not_supported
    @override
    def test_get_txs_with_query(self, wallet: MoneroWallet) -> None:
        return super().test_get_txs_with_query(wallet)

    @pytest.mark.not_supported
    @override
    def test_validate_inputs_get_txs(self, wallet: MoneroWallet) -> None:
        return super().test_validate_inputs_get_txs(wallet)

    @pytest.mark.not_supported
    @override
    def test_set_tx_note(self, wallet: MoneroWallet) -> None:
        return super().test_set_tx_note(wallet)

    @pytest.mark.not_supported
    @override
    def test_set_tx_notes(self, wallet: MoneroWallet) -> None:
        return super().test_set_tx_notes(wallet)

    @pytest.mark.not_supported
    @override
    def test_get_txs_by_height(self, wallet: MoneroWallet) -> None:
        return super().test_get_txs_by_height(wallet)

    @pytest.mark.not_supported
    @override
    def test_get_txs_with_payment_ids(self, wallet: MoneroWallet) -> None:
        return super().test_get_txs_with_payment_ids(wallet)

    @pytest.mark.not_supported
    @override
    def test_get_txs_fields_with_filtering(self, wallet: MoneroWallet) -> None:
        return super().test_get_txs_fields_with_filtering(wallet)
