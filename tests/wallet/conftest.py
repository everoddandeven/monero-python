from __future__ import annotations

from typing import Any, Generator

import pytest

from utils import TestUtils


@pytest.fixture(scope="session", autouse=True)
def close_test_wallets() -> Generator[None, Any, None]:
    """The wallet of each type is open for all the tests of its type, in all the files, and is closed at the end."""
    yield
    TestUtils.close_wallets()


_SEND_TESTS = "tests/wallet/test_send.py"

_SWEEP_TESTS = "tests/wallet/test_sweep.py"

_WALLET_TYPES = ("TestMoneroWalletFull", "TestMoneroWalletRpc", "TestMoneroWalletKeys", "TestMoneroWalletLight")
"""The classes of each type of wallet start with these, in the order that the types run."""

_LIGHT_RANK = _WALLET_TYPES.index("TestMoneroWalletLight")
"""The place of the light wallet in `_WALLET_TYPES`."""

_WALLET_TYPE_MARKERS = ("wallet_full", "wallet_rpc", "wallet_keys", "wallet_light")
"""The marker of each type in `_WALLET_TYPES`, so that `pytest -m wallet_rpc` runs only the tests of the rpc wallet."""


def _is_wallet_test(item: pytest.Item) -> bool:
    """A test of tests/wallet that is not about the models, which are unit tests that make nothing."""
    return item.nodeid.startswith("tests/wallet/") and not item.nodeid.startswith("tests/wallet/model/")


def _wallet_type_rank(item: pytest.Item) -> int:
    """The place of the type of wallet that a test is for, in `_WALLET_TYPES`. The tests that are not for a type come after."""
    parts: list[str] = item.nodeid.split("::")
    test_class: str = parts[1] if len(parts) > 2 else ""
    for rank, prefix in enumerate(_WALLET_TYPES):
        if test_class.startswith(prefix):
            return rank
    return len(_WALLET_TYPES)


def _place_in_type(item: pytest.Item) -> int:
    """The place of a test among the ones of its type: the send tests first, the sweep tests of the light wallet last, the rest between."""
    if item.nodeid.startswith(_SEND_TESTS):
        return 0
    if item.nodeid.startswith(_SWEEP_TESTS) and _wallet_type_rank(item) == _LIGHT_RANK:
        return 2
    return 1


@pytest.hookimpl(tryfirst=True)
def pytest_collection_modifyitems(items: list[pytest.Item]) -> None:
    """The tests of tests/wallet run one type of wallet at a time, and the send tests first.

    A file of a topic has a class for each type of wallet (full, rpc, keys and light), and the files run in alphabetical order, so the types
    would alternate: the full wallet of a topic, the rpc wallet of the same one, and the next topic. The wallet of a type is the same for
    all its tests, and the tests of a type use what the ones before made in it, so all the tests of a type run, and then the ones of
    the next: as when they were in a class for each type.

    Inside a type the send tests are the first. Some tests use what they made in the wallet: the proofs look for transactions with
    outgoing destinations, and the ones of the payment ids for the transactions that were sent with one ("run send tests", they say). The
    sends were the first tests when all of them were in a class, the relays tests, and test_proofs.py and test_txs.py come before
    test_send.py in the alphabet.

    The sweep tests of the light wallet are the last ones of its type: they sweep the whole wallet, and the tests that look for the outputs
    of its subaddresses (test_get_txs_with_query) need them unspent. They were kept last in its class for it.

    Only the tests of tests/wallet move, in the places that they have: everything else stays where it was. It is a stable sort, so inside
    the groups the order is the one of the files.
    """
    positions: list[int] = [i for i, item in enumerate(items) if _is_wallet_test(item)]
    if not positions:
        return
    # the marker of the type goes first: `-m` selects the tests after the hooks that add markers ran
    for i in positions:
        rank: int = _wallet_type_rank(items[i])
        if rank < len(_WALLET_TYPE_MARKERS):
            items[i].add_marker(_WALLET_TYPE_MARKERS[rank])
    wallet_items: list[pytest.Item] = [items[i] for i in positions]
    reordered: list[pytest.Item] = sorted(
        wallet_items,
        key=lambda item: (_wallet_type_rank(item), _place_in_type(item)),
    )
    for position, item in zip(positions, reordered):
        items[position] = item
