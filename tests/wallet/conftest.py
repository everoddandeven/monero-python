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

_WALLET_TYPES = ("TestMoneroWalletFull", "TestMoneroWalletRpc", "TestMoneroWalletKeys")
"""The classes of each type of wallet start with these, in the order that the types run."""


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


def pytest_collection_modifyitems(items: list[pytest.Item]) -> None:
    """The tests of tests/wallet run one type of wallet at a time, and the send tests first.

    A file of a topic has a class for each type of wallet (full, rpc and keys), and the files run in alphabetical order, so the types
    would alternate: the full wallet of a topic, the rpc wallet of the same one, and the next topic. The wallet of a type is the same for
    all its tests, and the tests of a type use what the ones before made in it, so all the tests of a type run, and then the ones of
    the next: as when they were in a class for each type.

    Inside a type the send tests are the first. Some tests use what they made in the wallet: the proofs look for transactions with
    outgoing destinations, and the ones of the payment ids for the transactions that were sent with one ("run send tests", they say). The
    sends were the first tests when all of them were in a class, the relays tests, and test_proofs.py and test_txs.py come before
    test_send.py in the alphabet.

    Only the tests of tests/wallet move, in the places that they have: everything else stays where it was. It is a stable sort, so inside
    the groups the order is the one of the files.
    """
    positions: list[int] = [i for i, item in enumerate(items) if _is_wallet_test(item)]
    if not positions:
        return
    wallet_items: list[pytest.Item] = [items[i] for i in positions]
    reordered: list[pytest.Item] = sorted(
        wallet_items,
        key=lambda item: (_wallet_type_rank(item), 0 if item.nodeid.startswith(_SEND_TESTS) else 1),
    )
    for position, item in zip(positions, reordered):
        items[position] = item
