import logging

from abc import ABC
from typing import Optional


from monero import (
    MoneroTxWallet, MoneroUtils,
    MoneroTxSet, MoneroTxQuery,
    MoneroNetworkType, MoneroCheckTx,
    MoneroCheckReserve
)

from .assert_utils import AssertUtils
from .gen_utils import GenUtils
from .context import TxContext
from .transfer_utils import TransferUtils

from .tx_wallet_tester import TxWalletTester
from .txs_structure_tester import TxsStructureTester


logger: logging.Logger = logging.getLogger("TxWalletUtils")


class TxWalletUtils(ABC):

    MAX_FEE: int = 7500000*10000
    """Max tx fee."""

    @classmethod
    def test_tx_wallet(cls, tx: Optional[MoneroTxWallet], context: Optional[TxContext] = None) -> None:
        """Test monero tx wallet.

        :param MoneroTxWallet | None tx: wallet transaction to test.
        :param TxContext | None context: test context (default `None`).
        """
        assert tx is not None
        tester: TxWalletTester = TxWalletTester(tx, context)
        tester.run()

        # TODO test deep copy
        #if ctx.is_copy is not True:
        #    cls.test_tx_wallet_copy(tx, ctx)

    @classmethod
    def test_txs_wallet(cls, txs: list[MoneroTxWallet], context: Optional[TxContext]) -> None:
        """Test a list of transactions.

        :param list[MoneroTxWallet] txs: transactions to test.
        :param TxContext | None context: test context.
        """
        for tx in txs:
            cls.test_tx_wallet(tx, context)

    @classmethod
    def test_described_tx_set(cls, described_tx_set: MoneroTxSet, network_type: MoneroNetworkType) -> None:
        """Test described tx set.

        :param MoneroTxSet described_tx_set: described tx set to test.
        :param MoneroNetworkType network_type: tx set network type.
        """
        assert len(described_tx_set.txs) > 0
        assert described_tx_set.signed_tx_hex is None
        assert described_tx_set.unsigned_tx_hex is None

        # test each transaction
        # TODO use common tx wallet test?
        assert described_tx_set.multisig_tx_hex is None
        for parsed_tx in described_tx_set.txs:
            # TODO monero-cpp full wallet is not assigning tx set to parsed txs
            #assert parsed_tx.tx_set is not None
            #assert parsed_tx.tx_set == described_tx_set, f"{parsed_tx.tx_set.serialize()} != {described_tx_set.serialize()}"
            GenUtils.test_unsigned_big_integer(parsed_tx.input_sum, True)
            GenUtils.test_unsigned_big_integer(parsed_tx.output_sum, True)
            GenUtils.test_unsigned_big_integer(parsed_tx.fee)
            GenUtils.test_unsigned_big_integer(parsed_tx.change_amount)
            if parsed_tx.change_amount == 0:
                assert parsed_tx.change_address is None
            else:
                assert parsed_tx.change_address is not None
                MoneroUtils.validate_address(parsed_tx.change_address, network_type)
            assert parsed_tx.ring_size is not None
            assert parsed_tx.ring_size > 1
            assert parsed_tx.unlock_time is not None
            assert parsed_tx.unlock_time >= 0
            assert parsed_tx.num_dummy_outputs is not None
            assert parsed_tx.num_dummy_outputs >= 0
            assert parsed_tx.extra_hex is not None
            assert len(parsed_tx.extra_hex) > 0
            assert parsed_tx.payment_id is None or len(parsed_tx.payment_id) > 0
            assert parsed_tx.is_outgoing is True
            assert parsed_tx.outgoing_transfer is not None
            assert len(parsed_tx.outgoing_transfer.destinations) > 0
            assert parsed_tx.is_incoming is None
            for destination in parsed_tx.outgoing_transfer.destinations:
                TransferUtils.test_destination(destination)

    @classmethod
    def test_get_txs_structure(cls, txs: list[MoneroTxWallet], query: Optional[MoneroTxQuery], regtest: bool) -> None:
        """
        Tests the integrity of the full structure in the given txs from the block down
        to transfers / destinations.

        :param list[MoneroTxWallet] txs: list of txs to get structure from.
        :param MoneroTxQuery | None query: filter txs by query, if set.
        :param bool regtest: indicates if running test on regtest network.
        """
        tester: TxsStructureTester = TxsStructureTester(txs, query, regtest)
        tester.run()

    @classmethod
    def test_common_tx_sets(cls, txs: list[MoneroTxWallet], has_signed: bool, has_unsigned: bool, has_multisig: bool) -> None:
        """Test common tx set in txs.

        :param list[MoneroTxWallet] txs: txs to test common sets.
        :param bool has_signed: expects signed tx hex to be defined in tx set.
        :param bool has_unsigned: expects unsigned tx hex to be defined in tx set.
        :param bool has_multisig: expects multisig tx hex to be defined in tx set.
        """
        assert len(txs) > 0
        # assert that all sets are same reference
        tx_set: Optional[MoneroTxSet] = None
        for i, tx in enumerate(txs):
            assert isinstance(tx, MoneroTxWallet)
            if i == 0:
                tx_set = tx.tx_set
            else:
                assert tx.tx_set == tx_set

        # test expected set
        assert tx_set is not None

        if has_signed:
            # check signed tx hex
            assert tx_set.signed_tx_hex is not None
            assert len(tx_set.signed_tx_hex) > 0

        if has_unsigned:
            # check unsigned tx hex
            assert tx_set.unsigned_tx_hex is not None
            assert len(tx_set.unsigned_tx_hex) > 0

        if has_multisig:
            # check multisign tx hex
            assert tx_set.multisig_tx_hex is not None
            assert len(tx_set.multisig_tx_hex) > 0

    @classmethod
    def test_spend_tx(cls, spend_tx: Optional[MoneroTxWallet]) -> None:
        """Test spend transaction.

        :param MoneroTxWallet | None spend_tx: Spend transaction to test.
        """
        # validate spend tx
        assert spend_tx is not None
        assert len(spend_tx.inputs) > 0
        # validate tx inputs
        for input_wallet in spend_tx.inputs:
            assert input_wallet.key_image is not None
            assert input_wallet.key_image.hex is not None
            assert len(input_wallet.key_image.hex) > 0

    @classmethod
    def test_check_tx(cls, tx: Optional[MoneroTxWallet], check: MoneroCheckTx) -> None:
        """Test tx with check result.

        :param MoneroTxWallet | None tx: transaction to test.
        :param MoneroCheckTx check: transaction check result to test.
        """
        assert tx is not None
        assert check.is_good is not None
        if check.is_good is True:
            assert check.num_confirmations is not None
            assert check.num_confirmations >= 0
            assert check.in_tx_pool is not None
            GenUtils.test_unsigned_big_integer(check.received_amount)
            if check.in_tx_pool is True:
                assert check.num_confirmations == 0
            else:
                # TODO (monero-wall-rpc) this fails (confirmations is 0) for (at least one) transaction
                # that has 1 confirmation on test_check_tx_key()
                assert check.num_confirmations > 0
        else:
            assert check.in_tx_pool is None
            assert check.num_confirmations is None
            assert check.received_amount is None

    @classmethod
    def test_check_reserve(cls, check: MoneroCheckReserve) -> None:
        """Test wallet check reserve.

        :param MoneroCheckReserve check: reserve check to test.
        """
        assert check.is_good is not None
        if check.is_good is True:
            assert check.total_amount is not None
            GenUtils.test_unsigned_big_integer(check.total_amount)
            assert check.total_amount >= 0

            assert check.unconfirmed_spent_amount is not None
            GenUtils.test_unsigned_big_integer(check.unconfirmed_spent_amount)
            assert check.unconfirmed_spent_amount >= 0
        else:
            assert check.total_amount is None
            assert check.unconfirmed_spent_amount is None

    @classmethod
    def set_block_copy(cls, copy: MoneroTxWallet, tx: MoneroTxWallet) -> None:
        """
        Replace tx block reference with copy.

        :param MoneroTxWallet copy: copy transaction reference.
        :param MoneroTxWallet tx: original transaction reference.
        """
        # skip unconfirmed tx
        if copy.is_confirmed is not True:
            return

        # copy block
        assert tx.block is not None
        block = tx.block.copy()

        # set copy tx in block copy
        block.txs = [copy]

        # set block copy reference to tx copy
        copy.block = block

    @classmethod
    def txs_mergeable(cls, tx1: MoneroTxWallet, tx2: MoneroTxWallet) -> bool:
        """Check if txs are mergeable.

        :param MoneroTxWallet tx1: first tx to check merge with.
        :param MoneroTxWallet tx2: second tx to check merge with.
        :returns bool: `True` if txs are mergeable, `False` otherwise.
        """
        try:
            # copy txs
            copy1 = tx1.copy()
            copy2 = tx2.copy()
            # set block copies
            cls.set_block_copy(copy1, tx1)
            cls.set_block_copy(copy2, tx2)
            # test merge
            copy1.merge(copy2)
            return True
        except Exception as e:
            # merge failed
            logger.warning(f"Txs are not mergeable: {e}")
            return False

    @classmethod
    def assert_list_txs_equals(cls, txs1: list[MoneroTxWallet], txs2: list[MoneroTxWallet], check_order: bool = False) -> None:
        """Checks txs lists equality.

        :param list[MoneroTxWallet] txs1: first list to check equality.
        :param list[MoneroTxWallet] txs2: second list to check equality.
        :param bool check_order: check also order (default `False`).
        """
        # assert lists have same size
        assert len(txs1) == len(txs2), "Txs lists count doesn't equal"

        if check_order:
            # check lists have same objects and order
            AssertUtils.assert_list_equals(txs1, txs2, "Txs lists doesn't equal")
            return

        # collect tx hashes
        tx_hashes1: list[str] = []
        tx_hashes2: list[str] = []

        for i, tx1 in enumerate(txs1):
            tx2: MoneroTxWallet = txs2[i]
            assert tx1.hash is not None
            assert tx2.hash is not None
            tx_hashes1.append(tx1.hash)
            tx_hashes2.append(tx2.hash)

        # assert that lists have same hashes
        for tx_hash1 in tx_hashes1:
            assert tx_hash1 in tx_hashes2
