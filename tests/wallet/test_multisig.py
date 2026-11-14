from __future__ import annotations

import logging

import pytest
from monero import MoneroWallet
from typing_extensions import override

from utils import TestUtils, TestUtils as Utils
from .base_test_monero_wallet import BaseTestMoneroWallet
from .wallet_support import FullWalletSupport, RpcWalletSupport, KeysWalletSupport

logger: logging.Logger = logging.getLogger("TestMoneroWalletMultisig")


class BaseTestMoneroWalletMultisig(BaseTestMoneroWallet):
    """Common wallet multisig tests."""

    # Can indicate if multisig import is needed for correct balance information
    @pytest.mark.skipif(TestUtils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_is_multisig_needed(self, wallet: MoneroWallet) -> None:
        # TODO test with multisig wallet
        multisig_import_needed: bool = wallet.is_multisig_import_needed()
        assert multisig_import_needed is False, "Expected non-multisig wallet"


@pytest.mark.integration
class TestMoneroWalletFullMultisig(FullWalletSupport, BaseTestMoneroWalletMultisig):
    """Full wallet multisig integration tests."""

    # Supports multisig sample code
    @pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_multisig_sample(self) -> None:
        self._test_multisig_sample(1, 2)
        self._test_multisig_sample(1, 4)
        self._test_multisig_sample(2, 2)
        self._test_multisig_sample(2, 3)
        self._test_multisig_sample(2, 4)


@pytest.mark.integration
class TestMoneroWalletRpcMultisig(RpcWalletSupport, BaseTestMoneroWalletMultisig):
    """Rpc wallet multisig integration tests."""

    # Supports multisig sample code
    @pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_multisig_sample(self) -> None:
        self._test_multisig_sample(1, 2)
        self._test_multisig_sample(2, 2)


@pytest.mark.unit
class TestMoneroWalletKeysMultisig(KeysWalletSupport, BaseTestMoneroWalletMultisig):
    """Keys-only wallet multisig unit tests."""

    @pytest.mark.not_supported
    @override
    def test_is_multisig_needed(self, wallet: MoneroWallet) -> None:
        return super().test_is_multisig_needed(wallet)
