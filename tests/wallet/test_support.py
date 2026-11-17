from __future__ import annotations

import logging
from pathlib import Path

import pytest
import yaml
from monero import (
    MoneroRpcConnection, MoneroWallet, MoneroWalletConfig, MoneroWalletFull, MoneroWalletKeys, MoneroWalletLight, MoneroWalletRpc
)

from utils import BaseTestClass, TestUtils as Utils, WalletCall, WALLET_CALLS

logger: logging.Logger = logging.getLogger("TestMoneroWalletSupport")

# the support matrix of the docs, which these tests keep true
SUPPORT_FILE: Path = Path(__file__).parent / "wallet_support.yml"
WALLETS: tuple[str, ...] = ("full", "rpc", "light", "keys")
STATES: tuple[str, ...] = ("supported", "partial", "todo", "unsupported")
# every method once, in the order of the calls: close() is the last one
METHODS: list[str] = list(dict.fromkeys(call.method for call in WALLET_CALLS))


@pytest.mark.unit
class TestMoneroWalletSupport(BaseTestClass):
    """Checks the support matrix of the docs (tests/wallet/wallet_support.yml) against the bindings: every method of the interface is
    called on a full, an rpc, a light and a keys-only wallet, and the methods that a wallet does not implement raise "not supported"."""

    @pytest.fixture(scope="class")
    @classmethod
    def support(cls) -> dict[str, dict[str, str]]:
        """The entries of the matrix by method, without their sections."""
        with open(SUPPORT_FILE, encoding="utf-8") as file:
            sections: dict[str, dict[str, dict[str, str]]] = yaml.safe_load(file)
        return {method: entry for methods in sections.values() for method, entry in methods.items()}

    @pytest.fixture(scope="class")
    @classmethod
    def wallets(cls) -> dict[str, MoneroWallet]:
        """A wallet of each type, of its own: the calls change and close them. None of them reaches the network: the full one has no
        daemon, the rpc one has no server and the server of the light one does not exist, so their calls fail at once when they are
        implemented."""
        full_config: MoneroWalletConfig = MoneroWalletConfig()
        full_config.path = ""
        full_config.password = Utils.WALLET_PASSWORD
        full_config.network_type = Utils.NETWORK_TYPE
        keys_config: MoneroWalletConfig = MoneroWalletConfig()
        keys_config.network_type = Utils.NETWORK_TYPE
        light_config: MoneroWalletConfig = MoneroWalletConfig()
        light_config.network_type = Utils.NETWORK_TYPE
        return {
            "full": MoneroWalletFull.create_wallet(full_config),
            "rpc": MoneroWalletRpc(),
            "light": MoneroWalletLight.create_wallet(light_config, MoneroRpcConnection(Utils.OFFLINE_SERVER_URI)),
            "keys": MoneroWalletKeys.create_wallet_random(keys_config),
        }

    #region Tests

    # Every public method of MoneroWallet has a call, so a new one has a row in the matrix
    def test_every_method_is_called(self) -> None:
        methods: set[str] = {name for name in dir(MoneroWallet) if not name.startswith("_") and callable(getattr(MoneroWallet, name))}
        assert methods - set(METHODS) == set(), "methods of MoneroWallet with no call in WALLET_CALLS"
        assert set(METHODS) - methods == set(), "calls in WALLET_CALLS of methods that MoneroWallet does not have"

    # Every method is in the matrix once, with a known state for each wallet
    def test_matrix_is_complete(self, support: dict[str, dict[str, str]]) -> None:
        assert set(METHODS) - set(support) == set(), f"methods missing from {SUPPORT_FILE.name}"
        assert set(support) - set(METHODS) == set(), f"methods in {SUPPORT_FILE.name} that MoneroWallet does not have"
        for method, entry in support.items():
            for wallet in WALLETS:
                assert entry.get(wallet) in STATES, f"{method}: the state of the {wallet} wallet is {entry.get(wallet)}, not one of {STATES}"
            partial: bool = "partial" in (entry[wallet] for wallet in WALLETS)
            assert partial == ("note" in entry), f"{method}: a note is for a partial support, and a partial support needs one"

    # Each wallet implements the methods that the matrix says, and not the others
    @pytest.mark.parametrize("method", METHODS)
    def test_support(self, wallets: dict[str, MoneroWallet], support: dict[str, dict[str, str]], method: str) -> None:
        calls: list[WalletCall] = [call for call in WALLET_CALLS if call.method == method]
        for name, wallet in wallets.items():
            state: str = support[method][name]
            if state in ("supported", "partial") and any(call.waits for call in calls):
                # it would wait for the network: the wallet is said to implement it, and the other wallets are checked
                continue
            implemented: list[bool] = [call.is_implemented_by(wallet) for call in calls]
            if state == "supported":
                assert all(implemented), f"{method} on the {name} wallet: supported, but it does not implement {self._missing(calls, implemented)}"
            elif state == "partial":
                assert any(implemented) and not all(implemented), \
                    f"{method} on the {name} wallet: partial, but it implements {'every' if all(implemented) else 'no'} overload"
            else:
                assert not any(implemented), f"{method} on the {name} wallet: {state}, but it implements it"

    #endregion

    @staticmethod
    def _missing(calls: list[WalletCall], implemented: list[bool]) -> str:
        return ", ".join(str(call) for call, done in zip(calls, implemented) if not done)
