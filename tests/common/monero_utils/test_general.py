from __future__ import annotations

import logging
import re

import pytest
from monero import MoneroIntegratedAddress, MoneroNetworkType, MoneroUtils
from pathlib import Path

from .base_test_monero_utils import BaseTestMoneroUtils

logger: logging.Logger = logging.getLogger("TestMoneroUtilsGeneral")


@pytest.mark.unit
class TestMoneroUtilsGeneral(BaseTestMoneroUtils):
    """Monero utilities general unit tests."""

    # Can get integrated addresses
    def test_get_integrated_address(self, config: BaseTestMoneroUtils.Config) -> None:
        primary_address: str = config.stagenet.primary_address_4
        subaddress: str = config.stagenet.subaddress_4
        payment_id: str = "03284e41c342f036"
        network_type: MoneroNetworkType = MoneroNetworkType.STAGENET

        # get integrated address with randomly generated payment id
        integrated_address: MoneroIntegratedAddress = MoneroUtils.get_integrated_address(network_type, primary_address, "")
        assert primary_address == integrated_address.standard_address
        assert 16 == len(integrated_address.payment_id)
        assert 106 == len(integrated_address.integrated_address)

        # get integrated address with specific payment id
        integrated_address = MoneroUtils.get_integrated_address(network_type, primary_address, payment_id)
        assert primary_address == integrated_address.standard_address
        assert payment_id == integrated_address.payment_id
        assert 106 == len(integrated_address.integrated_address)

        # get integrated address with subaddress
        integrated_address = MoneroUtils.get_integrated_address(network_type, subaddress, payment_id)
        assert subaddress == integrated_address.standard_address
        assert payment_id == integrated_address.payment_id
        assert 106 == len(integrated_address.integrated_address)

        # get integrated address with invalid payment id
        try:
          MoneroUtils.get_integrated_address(network_type, primary_address, "123")
          raise Exception("Getting integrated address with invalid payment id should have failed")
        except Exception as err:
          assert "Invalid payment id" == str(err)

    # Can get version, which is the one declared in pyproject.toml
    def test_get_version(self) -> None:
        version: str = MoneroUtils.get_version()
        logger.debug(f"Testing monero-python version: {version}")
        assert version != "", "Version is empty"
        # the repository root, two folders above tests/ and three above this file: the tests are not in tests/ itself anymore
        root: Path = next(p for p in Path(__file__).resolve().parents if (p / "pyproject.toml").is_file())
        pyproject: str = (root / "pyproject.toml").read_text(encoding="utf-8")
        declared = re.search(r'^version = "(\d+\.\d+\.\d+)"$', pyproject, re.MULTILINE)
        assert declared is not None, "Version not found in pyproject.toml"
        assert version == declared.group(1)

    # Can get ring size
    def test_get_ring_size(self) -> None:
        size: int = MoneroUtils.get_ring_size()
        assert size == 16
