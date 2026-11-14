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


def _is_wallet_test(item: pytest.Item) -> bool:
    """A test of tests/wallet that is not about the models, which are unit tests that make nothing."""
    return item.nodeid.startswith("tests/wallet/") and not item.nodeid.startswith("tests/wallet/model/")


def pytest_collection_modifyitems(items: list[pytest.Item]) -> None:
    """The send tests of the wallets run before the other ones of tests/wallet.

    Some tests use what the send tests made in the wallet: the proofs look for transactions with outgoing destinations, and the ones of the
    payment ids for the transactions that were sent with one ("run send tests", they say). The sends were the first tests when all of them
    were in a class, the relays tests, and the files run in alphabetical order, so test_proofs.py and test_txs.py ran before test_send.py.
    Only the send tests move: they take the first places that the tests of tests/wallet have, and everything else stays where it was.
    """
    positions: list[int] = [i for i, item in enumerate(items) if _is_wallet_test(item)]
    if not positions:
        return
    wallet_items: list[pytest.Item] = [items[i] for i in positions]
    # a stable sort: the order inside the send tests, and inside the others, is the one of the files
    reordered: list[pytest.Item] = sorted(wallet_items, key=lambda item: 0 if item.nodeid.startswith(_SEND_TESTS) else 1)
    for position, item in zip(positions, reordered):
        items[position] = item
