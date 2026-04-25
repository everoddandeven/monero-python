import logging

from monero import (
    MoneroWallet, MoneroUtils,
    MoneroMultisigInitResult, MoneroMultisigInfo
)

from .wallet_utils import WalletUtils
from .test_utils import TestUtils

logger: logging.Logger = logging.getLogger("MultisigSampleCodeTester")


class MultisigSampleCodeTester:
    """Create and test a multisig wallet with M/N configuration."""

    m: int
    """Multisig threshold."""
    n: int
    """Multisig participants."""
    wallets: list[MoneroWallet]
    """Participants test wallets."""

    def __init__(self, m: int, participants: list[MoneroWallet]) -> None:
        """Initialize a new create-multisig-wallet tester.

        :param int m: multisig threshold.
        :param list[MoneroWallet] participants: participant wallets.
        """
        n: int = len(participants)
        assert m <= n, "Threshold must be less or equal to number of participants"
        self.m = m
        self.n = n
        self.wallets = participants
        self._disposed = False

    def make_multisig_wallets(self) -> list[str]:
        # prepare and collect multisig hex from each participant
        prepared_multisig_hexes: list[str] = []

        for wallet in self.wallets:
            prepared_multisig_hexes.append(wallet.prepare_multisig())

        # make each wallet multisig and collect results
        num_wallets: int = len(self.wallets)
        made_multisig_hexes: list[str] = []
        for i in range(num_wallets):
            # collect prepared multisig hexes from wallet's peers
            peer_multisig_hexes: list[str] = []
            for j in range(num_wallets):
                if j != i:
                    peer_multisig_hexes.append(prepared_multisig_hexes[j])

            # make wallet multisig and collect result hex
            multisig_hex: str = self.wallets[i].make_multisig(peer_multisig_hexes, self.m, TestUtils.WALLET_PASSWORD)
            made_multisig_hexes.append(multisig_hex)

        return made_multisig_hexes.copy()

    def test(self) -> None:
        """Test multisig wallet creation."""

        # exchange multisig keys N - M + 1 times
        multisig_hexes: list[str] = self.make_multisig_wallets()
        for i in range(self.n - self.m + 1):
            # exchange multisig keys among participants and collect results for next round if applicable
            result_multisig_hexes: list[str] = []
            for wallet in self.wallets:
                # import the multisig hex of other participants and collect results
                result: MoneroMultisigInitResult = wallet.exchange_multisig_keys(multisig_hexes, TestUtils.WALLET_PASSWORD)
                logger.debug(f"Round {i + 1}, multisig init result: {result.serialize()}")
                assert result.multisig_hex is not None
                result_multisig_hexes.append(result.multisig_hex)

            # use resulting multisig hex for next round of exchange if applicable
            multisig_hexes = result_multisig_hexes

        # wallets are now multisig
        for wallet in self.wallets:
            primary_address: str = wallet.get_address(0, 0)
            # TODO: replace with MoneroWallet.get_network_type() when all methods defined in interface
            MoneroUtils.validate_address(primary_address, TestUtils.NETWORK_TYPE)
            info: MoneroMultisigInfo = wallet.get_multisig_info()
            WalletUtils.test_multisig_info(info, self.m, self.n)
            wallet.close(True)
