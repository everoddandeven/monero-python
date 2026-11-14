from __future__ import annotations

import logging

import pytest
from monero import (
    MoneroKeyImage,
    MoneroOutput,
    MoneroOutputDistributionEntry,
    MoneroOutputHistogramEntry,
    MoneroTx,
)

from utils import AssertUtils, BaseTestClass

logger: logging.Logger = logging.getLogger("TestMoneroDaemonModelOutputs")


@pytest.mark.unit
class TestMoneroDaemonModelOutputs(BaseTestClass):
    """Daemon outputs model unit tests."""

    def test_key_image_deserialize(self) -> None:
        key_image: MoneroKeyImage = MoneroKeyImage()
        key_image.hex = "a" * 64
        key_image.signature = "b" * 128
        AssertUtils.assert_serialization_integrity(key_image)

    def test_key_image_deserialize_key_images(self) -> None:
        json_str: str = (
            '{"keyImages": ['
            '{"hex": "' + "a" * 64 + '", "signature": "' + "b" * 128 + '"}, '
            '{"hex": "' + "c" * 64 + '"}'
            ']}'
        )
        key_images: list[MoneroKeyImage] = MoneroKeyImage.deserialize_key_images(json_str)
        assert len(key_images) == 2
        assert key_images[0].hex == "a" * 64
        assert key_images[0].signature == "b" * 128
        assert key_images[1].hex == "c" * 64
        assert key_images[1].signature is None

        # a missing or empty keyImages array yields no key images
        assert MoneroKeyImage.deserialize_key_images("{}") == []
        assert MoneroKeyImage.deserialize_key_images('{"keyImages": []}') == []

        # an empty string is not valid json
        with pytest.raises(Exception):
            MoneroKeyImage.deserialize_key_images("")

    def test_output_deserialize(self) -> None:
        output: MoneroOutput = MoneroOutput()
        output.amount = 1000000
        output.index = 5
        key_image: MoneroKeyImage = MoneroKeyImage()
        key_image.hex = "a" * 64
        key_image.signature = "b" * 128
        output.key_image = key_image
        AssertUtils.assert_serialization_integrity(output)

    def test_output_ring_output_indices_and_stealth_public_key_deserialize(self) -> None:
        output: MoneroOutput = MoneroOutput()
        output.amount = 1000000
        output.index = 5
        output.ring_output_indices = [10, 20, 30]
        output.stealth_public_key = "a" * 64
        output.mask = "b" * 64
        AssertUtils.assert_serialization_integrity(output)

    def test_output_distribution_entry_deserialize(self) -> None:
        entry: MoneroOutputDistributionEntry = MoneroOutputDistributionEntry()
        entry.amount = 0
        entry.base = 100
        entry.distribution = [1, 2, 3, 4]
        entry.start_height = 0
        AssertUtils.assert_serialization_integrity(entry)

    def test_output_histogram_entry_deserialize(self) -> None:
        entry: MoneroOutputHistogramEntry = MoneroOutputHistogramEntry()
        entry.amount = 0
        entry.num_instances = 10
        entry.unlocked_instances = 8
        entry.recent_instances = 2
        AssertUtils.assert_serialization_integrity(entry)

    def test_key_image_copy(self) -> None:
        key_image: MoneroKeyImage = MoneroKeyImage()
        key_image.hex = "a" * 64
        key_image.signature = "b" * 128

        copy: MoneroKeyImage = key_image.copy()
        assert copy is not key_image
        assert copy.serialize() == key_image.serialize()

    def test_key_image_merge(self) -> None:
        a: MoneroKeyImage = MoneroKeyImage()
        a.hex = "a" * 64
        b: MoneroKeyImage = a.copy()
        b.signature = "b" * 128  # a.signature is unset -> merge fills the gap
        a.merge(b)
        assert a.signature == "b" * 128

    def test_output_copy(self) -> None:
        output: MoneroOutput = MoneroOutput()
        output.amount = 1000000
        output.index = 5
        key_image: MoneroKeyImage = MoneroKeyImage()
        key_image.hex = "a" * 64
        output.key_image = key_image

        copy: MoneroOutput = output.copy()
        assert copy is not output
        assert copy.key_image is not output.key_image  # key_image is deep copied
        assert copy.serialize() == output.serialize()

    def test_output_merge(self) -> None:
        a: MoneroOutput = MoneroOutput()
        a.amount = 1000000
        a.index = 5
        b: MoneroOutput = a.copy()  # preserves the (unset) tx reference, so merge won't recurse into tx merge
        b.key_image = MoneroKeyImage()
        b.key_image.hex = "a" * 64
        a.merge(b)  # a.key_image is unset -> merge adopts b's key_image
        assert a.key_image is not None
        assert a.key_image.hex == "a" * 64

    def test_output_merge_recurses_into_tx_merge(self) -> None:
        tx_a: MoneroTx = MoneroTx()
        tx_a.hash = "a" * 64
        tx_a.is_confirmed = True

        tx_b: MoneroTx = MoneroTx()
        tx_b.hash = "a" * 64
        tx_b.is_confirmed = True
        tx_b.num_confirmations = 9  # only tx merge reconciles this

        out_a: MoneroOutput = MoneroOutput()
        out_a.tx = tx_a
        out_a.stealth_public_key = "s" * 64
        tx_a.outputs = [out_a]

        out_b: MoneroOutput = MoneroOutput()
        out_b.tx = tx_b
        out_b.stealth_public_key = "s" * 64
        tx_b.outputs = [out_b]

        # outputs on different txs -> merge delegates to tx merge (which comes back to merging outputs)
        out_a.merge(out_b)
        assert tx_a.num_confirmations == 9

    def test_output_merge_ring_output_indices_and_stealth_public_key(self) -> None:
        a: MoneroOutput = MoneroOutput()
        a.amount = 1000000
        a.index = 5
        b: MoneroOutput = a.copy()  # preserves the (unset) tx reference, so merge won't recurse into tx merge
        b.ring_output_indices = [10, 20, 30]
        b.stealth_public_key = "a" * 64
        b.mask = "b" * 64
        a.merge(b)  # a's fields are unset -> merge should adopt b's
        assert a.ring_output_indices == [10, 20, 30]
        assert a.stealth_public_key == "a" * 64
        assert a.mask == "b" * 64
