import logging

from abc import ABC
from typing import Optional

from monero import (
    MoneroWallet, MoneroOutputQuery,
    MoneroOutput, MoneroKeyImage, MoneroOutputWallet
)

from .gen_utils import GenUtils
from .assert_utils import AssertUtils
from .context import TestContext

logger: logging.Logger = logging.getLogger("OutputUtils")


class OutputUtils(ABC):

    @classmethod
    def test_key_image(cls, image: Optional[MoneroKeyImage], context: Optional[TestContext] = None) -> None:
        """Test monero key image.

        :param MoneroKeyImage | None image: key image to test.
        :param TestContext context: test context (default `None`).
        """
        assert image is not None
        assert image.hex is not None
        assert len(image.hex) > 0
        if image.signature is not None:
            assert len(image.signature) > 0

    @classmethod
    def test_output(cls, output: Optional[MoneroOutput], context: Optional[TestContext] = None) -> None:
        """Test monero output.

        :param MoneroOutput | None output: output to test.
        :param TestContext | None: test context (default `None`).
        """
        assert output is not None
        GenUtils.test_unsigned_big_integer(output.amount)
        if context is None:
            return
        assert output.tx is not None
        ctx = TestContext(context)
        if output.tx.in_tx_pool or ctx.has_output_indices is False:
            assert output.index is None
        else:
            assert output.index is not None
            assert output.index >= 0
            assert output.stealth_public_key is not None
            assert len(output.stealth_public_key) > 0

    @classmethod
    def test_input(cls, xmr_input: Optional[MoneroOutput], ctx: Optional[TestContext]) -> None:
        """Test monero input.

        :param MoneroOutput | None zmr_input: input to test.
        :param TestContext | None ctx: test context (default `None`).
        """
        assert xmr_input is not None
        cls.test_output(xmr_input)
        cls.test_key_image(xmr_input.key_image, ctx)
        assert len(xmr_input.ring_output_indices) > 0

    @classmethod
    def test_input_wallet(cls, xmr_input: Optional[MoneroOutputWallet]) -> None:
        """Test monero input wallet.

        :param MoneroOutputWallet xmr_input: wallet input to test.
        """
        assert xmr_input is not None
        assert xmr_input.key_image is not None
        assert xmr_input.key_image.hex is not None
        assert len(xmr_input.key_image.hex) > 0
        assert xmr_input.amount is None

    @classmethod
    def test_output_wallet(cls, output: Optional[MoneroOutputWallet]) -> None:
        """Test monero output wallet.

        :param MoneroOutputWallet | None output: wallet output to test.
        """
        assert output is not None
        assert output.account_index is not None
        assert output.account_index >= 0
        assert output.subaddress_index is not None
        assert output.subaddress_index >= 0
        assert output.index is not None
        assert output.index >= 0
        assert output.is_spent is not None
        # TODO implement is_locked
        #assert output.is_locked is not None
        assert output.is_frozen is not None
        assert output.key_image is not None
        assert output.key_image.hex is not None
        assert len(output.key_image.hex) > 0
        GenUtils.test_unsigned_big_integer(output.amount, True)

        # output has circular reference to its transaction which has some initialized fields
        tx = output.tx
        assert tx is not None
        assert output in tx.outputs
        assert tx.hash is not None
        # TODO implement is_locked
        #assert tx.is_locked is not None
        # TODO monero-wallet-rpc: possible to get unconfirmed outputs?
        assert tx.is_confirmed is True
        assert tx.is_relayed is True
        assert tx.is_failed is False
        tx_height = tx.get_height()
        assert tx_height is not None
        assert tx_height > 0

        # test copying
        copy = output.copy()
        assert copy != output
        AssertUtils.assert_equals(copy, output)
        # TODO: should output copy do deep copy of tx so models are graph instead of tree?  Would need to work out circular references
        # monero-cpp gives non-null output tx
        # assert copy.tx is None
        assert copy.tx is not None
        assert copy.tx == output.tx

    @classmethod
    def get_and_test_outputs(cls, wallet: MoneroWallet, query: Optional[MoneroOutputQuery], is_expected: Optional[bool]) -> list[MoneroOutputWallet]:
        """Fetches and tests wallet outputs (i.e. wallet tx outputs) according to the given query.

        :param MoneroWallet wallet: wallet to get outputs from.
        :param MoneroOutputQuery | None query: output query.
        :param bool | None is_expected: expected non-empty outputs.
        """

        copy = query.copy() if query is not None else None
        outputs = wallet.get_outputs(query) if query is not None else wallet.get_outputs(MoneroOutputQuery())
        AssertUtils.assert_equals(copy, query)

        if is_expected is False:
            assert len(outputs) == 0
        elif is_expected is True:
            assert len(outputs) > 0, "Outputs were expected but not found; run send tests"

        for output in outputs:
            OutputUtils.test_output_wallet(output)

        return outputs
