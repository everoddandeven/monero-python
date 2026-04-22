from abc import ABC
from typing import Optional

from monero import (
    MoneroWallet, MoneroTransfer,
    MoneroTransferQuery
)

from .assert_utils import AssertUtils
from .context import TxContext
from .tx_wallet_utils import TxWalletUtils


class WalletTransfersUtils(ABC):
    """Wallet transfers utilities."""

    @classmethod
    def get_and_test_transfers(
        cls,
        wallet: MoneroWallet,
        query: Optional[MoneroTransferQuery],
        ctx: Optional[TxContext],
        is_expected: Optional[bool]
    ) -> list[MoneroTransfer]:
        """Get and test transfers from wallet.

        :param MoneroWallet wallet: wallet to get transfers from.
        :param MoneroTransferQuery | None query: filter wallet transfers by query if defined.
        :param TxContext | None ctx: transaction context.
        :param bool | None is_expected: expects empty/non-empty transfers.
        """
        copy: Optional[MoneroTransferQuery] = query.copy() if query is not None else None
        transfers = wallet.get_transfers(query) if query is not None else wallet.get_transfers(MoneroTransferQuery())

        if is_expected is False:
            assert len(transfers) == 0
        elif is_expected is True:
            assert len(transfers) > 0, "Transfers were expected but not found; run send tests?"

        if ctx is None:
            ctx = TxContext()

        ctx.wallet = wallet
        for transfer in transfers:
            TxWalletUtils.test_tx_wallet(transfer.tx, ctx)

        if query is not None:
            AssertUtils.assert_equals(copy, query)

        return transfers
