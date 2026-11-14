from __future__ import annotations

import logging

import pytest
from monero import MoneroKeyImage, MoneroOutputWallet, MoneroTx, OutputComparator

from utils import AssertUtils, BaseTestClass

logger: logging.Logger = logging.getLogger("TestMoneroWalletModelOutputs")


@pytest.mark.unit
class TestMoneroWalletModelOutputs(BaseTestClass):
    """Wallet output model unit tests."""

    def test_output_wallet_deserialize(self) -> None:
        output_wallet: MoneroOutputWallet = MoneroOutputWallet()
        output_wallet.amount = 1000000
        output_wallet.index = 2
        key_image: MoneroKeyImage = MoneroKeyImage()
        key_image.hex = "a" * 64
        key_image.signature = "b" * 128
        output_wallet.key_image = key_image
        output_wallet.account_index = 0
        output_wallet.subaddress_index = 1
        output_wallet.is_spent = False
        output_wallet.is_frozen = False
        AssertUtils.assert_serialization_integrity(output_wallet)

    def test_output_wallet_copy(self) -> None:
        output: MoneroOutputWallet = MoneroOutputWallet()
        output.amount = 1000000
        output.index = 2
        output.account_index = 0
        output.subaddress_index = 1
        output.is_spent = False
        output.is_frozen = False

        copy: MoneroOutputWallet = output.copy()
        assert copy is not output
        assert copy.serialize() == output.serialize()

    def test_output_wallet_merge(self) -> None:
        a: MoneroOutputWallet = MoneroOutputWallet()
        a.amount = 1000000
        a.index = 2
        a.account_index = 0
        a.subaddress_index = 1
        # a.tx is left unset on both sides so merge() won't recurse into tx merge

        b: MoneroOutputWallet = a.copy()
        b.is_spent = True  # a.is_spent is unset -> merge fills the gap
        a.merge(b)
        assert a.is_spent is True

    def test_output_wallet_lt_comparator(self) -> None:
        o1: MoneroOutputWallet = MoneroOutputWallet()
        o1.tx = MoneroTx()
        o1.account_index = 0
        o1.subaddress_index = 0
        o1.index = 0
        o1.key_image = MoneroKeyImage()
        o1.key_image.hex = "a" * 64

        o2: MoneroOutputWallet = MoneroOutputWallet()
        o2.tx = MoneroTx()
        o2.account_index = 0
        o2.subaddress_index = 0
        o2.index = 1
        o2.key_image = MoneroKeyImage()
        o2.key_image.hex = "b" * 64

        assert o1 < o2
        assert not (o2 < o1)
        assert OutputComparator.compare(o1, o2)
        assert not OutputComparator.compare(o2, o1)

    def test_output_wallet_lt_comparator_account_index(self) -> None:
        tx: MoneroTx = MoneroTx()
        o1: MoneroOutputWallet = MoneroOutputWallet()
        o1.tx = tx
        o1.account_index = 0
        o1.subaddress_index = 0
        o1.index = 0
        o1.key_image = MoneroKeyImage()
        o1.key_image.hex = "a" * 64

        o2: MoneroOutputWallet = o1.copy()
        o2.account_index = 1  # only the account index differs

        assert OutputComparator.compare(o1, o2)
        assert not OutputComparator.compare(o2, o1)

    def test_output_wallet_lt_comparator_subaddress_index(self) -> None:
        tx: MoneroTx = MoneroTx()
        o1: MoneroOutputWallet = MoneroOutputWallet()
        o1.tx = tx
        o1.account_index = 0
        o1.subaddress_index = 0
        o1.index = 0
        o1.key_image = MoneroKeyImage()
        o1.key_image.hex = "a" * 64

        o2: MoneroOutputWallet = o1.copy()
        o2.subaddress_index = 1  # same account index, only the subaddress index differs

        assert OutputComparator.compare(o1, o2)
        assert not OutputComparator.compare(o2, o1)

    def test_output_wallet_lt_comparator_key_image(self) -> None:
        tx: MoneroTx = MoneroTx()
        o1: MoneroOutputWallet = MoneroOutputWallet()
        o1.tx = tx
        o1.account_index = 0
        o1.subaddress_index = 0
        o1.index = 0
        o1.key_image = MoneroKeyImage()
        o1.key_image.hex = "a" * 64

        o2: MoneroOutputWallet = o1.copy()
        o2.key_image = MoneroKeyImage()
        o2.key_image.hex = "b" * 64  # account/subaddress/index tied -> falls back to key image hex

        assert OutputComparator.compare(o1, o2)
        assert not OutputComparator.compare(o2, o1)

        outputs: list[MoneroOutputWallet] = [o2, o1]
        outputs.sort()
        assert outputs[0] is o1
        assert outputs[1] is o2
