from __future__ import annotations

import logging
import os

import pytest
from monero import MoneroKeyImage, MoneroNetworkType, MoneroWalletConfig, MoneroWalletFull

from utils import BaseTestClass, TestUtils as Utils

logger: logging.Logger = logging.getLogger("TestMoneroWalletFullOffline")


@pytest.mark.unit
class TestMoneroWalletFullOffline(BaseTestClass):
    """Full wallet unit tests that run against a disconnected wallet, no daemon needed."""

    @pytest.fixture(scope="class")
    @classmethod
    def wallet(cls) -> MoneroWalletFull:
        """Shared disconnected full wallet."""
        return Utils.get_wallet_full_offline()

    def test_get_default_ringdb_path_mainnet(self) -> None:
        path: str = MoneroWalletFull.get_default_ringdb_path(MoneroNetworkType.MAINNET)
        assert path.endswith(".shared-ringdb")
        assert not path.endswith("testnet")
        assert not path.endswith("stagenet")

    def test_get_default_ringdb_path_testnet(self) -> None:
        path: str = MoneroWalletFull.get_default_ringdb_path(MoneroNetworkType.TESTNET)
        assert path.endswith(os.path.join(".shared-ringdb", "testnet"))

    def test_get_default_ringdb_path_stagenet(self) -> None:
        path: str = MoneroWalletFull.get_default_ringdb_path(MoneroNetworkType.STAGENET)
        assert path.endswith(os.path.join(".shared-ringdb", "stagenet"))

    # import_key_images guards unset key image fields
    def test_import_key_images_hex_not_defined(self, wallet: MoneroWalletFull) -> None:
        with pytest.raises(RuntimeError) as exc_info:
            wallet.import_key_images([MoneroKeyImage()])
        assert str(exc_info.value) == "key image hex is not defined"

    def test_import_key_images_signature_not_defined(self, wallet: MoneroWalletFull) -> None:
        key_image: MoneroKeyImage = MoneroKeyImage()
        key_image.hex = "a" * 64
        with pytest.raises(RuntimeError) as exc_info:
            wallet.import_key_images([key_image])
        assert str(exc_info.value) == "key image signature is not defined"

    # Can be moved
    def test_move_to(self) -> None:
        config: MoneroWalletConfig = MoneroWalletConfig()
        config.path = ""
        config.password = Utils.WALLET_PASSWORD
        config.network_type = MoneroNetworkType.MAINNET
        wallet: MoneroWalletFull = MoneroWalletFull.create_wallet(config)
        try:
            seed: str = wallet.get_seed()
            wallet.set_attribute("mykey", "myval1")

            # move the in-memory wallet to disk
            path1: str = Utils.get_random_wallet_path()
            assert MoneroWalletFull.wallet_exists(path1) is False
            wallet.move_to(path1, Utils.WALLET_PASSWORD)
            assert MoneroWalletFull.wallet_exists(path1) is True
            assert wallet.get_seed() == seed
            assert wallet.get_attribute("mykey") == "myval1"

            # moving to the same path saves in place
            wallet.set_attribute("mykey", "myval2")
            wallet.move_to(path1, Utils.WALLET_PASSWORD)
            wallet.close()
            wallet = MoneroWalletFull.open_wallet(path1, Utils.WALLET_PASSWORD, MoneroNetworkType.MAINNET)
            assert wallet.get_seed() == seed
            assert wallet.get_attribute("mykey") == "myval2"

            # move to a new path
            path2: str = Utils.get_random_wallet_path()
            wallet.set_attribute("mykey", "myval3")
            wallet.move_to(path2, Utils.WALLET_PASSWORD)
            assert MoneroWalletFull.wallet_exists(path1) is False
            assert MoneroWalletFull.wallet_exists(path2) is True
            wallet.close()
            wallet = MoneroWalletFull.open_wallet(path2, Utils.WALLET_PASSWORD, MoneroNetworkType.MAINNET)
            assert wallet.get_seed() == seed
            assert wallet.get_attribute("mykey") == "myval3"
        finally:
            wallet.close()

    # Can export and import wallet files
    def test_export_and_import_wallet_files(self) -> None:
        config: MoneroWalletConfig = MoneroWalletConfig()
        config.path = ""
        config.password = Utils.WALLET_PASSWORD
        config.network_type = MoneroNetworkType.MAINNET
        wallet: MoneroWalletFull = MoneroWalletFull.create_wallet(config)
        from_keys: MoneroWalletFull | None = None
        from_both: MoneroWalletFull | None = None
        try:
            keys_data: bytes = wallet.get_keys_file_buffer(Utils.WALLET_PASSWORD, False)
            cache_data: bytes = wallet.get_cache_file_buffer()
            assert len(keys_data) > 0
            assert len(cache_data) > 0

            # open from the keys buffer alone, then from keys + cache
            from_keys = MoneroWalletFull.open_wallet_data(Utils.WALLET_PASSWORD, MoneroNetworkType.MAINNET, keys_data, b"", None, Utils.REGTEST)
            from_both = MoneroWalletFull.open_wallet_data(Utils.WALLET_PASSWORD, MoneroNetworkType.MAINNET, keys_data, cache_data, None, Utils.REGTEST)

            for restored in (from_keys, from_both):
                assert restored.get_seed() == wallet.get_seed()
                assert restored.get_primary_address() == wallet.get_primary_address()
                assert restored.get_private_view_key() == wallet.get_private_view_key()
                assert restored.get_private_spend_key() == wallet.get_private_spend_key()
        finally:
            wallet.close()
            if from_keys is not None:
                from_keys.close()
            if from_both is not None:
                from_both.close()
