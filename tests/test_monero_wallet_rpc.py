import pytest
import logging

from monero import MoneroWallet, MoneroWalletConfig, MoneroWalletRpc

from typing_extensions import override
from utils import TestUtils as Utils
from test_monero_wallet_common import BaseTestMoneroWallet

logger: logging.Logger = logging.getLogger("TestMoneroWalletRpc")


@pytest.mark.integration
class TestMoneroWalletRpc(BaseTestMoneroWallet):
    """Rpc wallet integration tests"""

    #region Overrides

    @pytest.fixture(scope="class")
    @override
    def wallet(self) -> MoneroWalletRpc:
        """Test rpc wallet instance"""
        return Utils.get_wallet_rpc()

    @override
    def get_test_wallet(self) -> MoneroWalletRpc:
        return Utils.get_wallet_rpc()

    @override
    def _open_wallet(self, config: MoneroWalletConfig | None) -> MoneroWallet:
        try:
            return Utils.open_wallet_rpc(config)
        except Exception:
            Utils.free_wallet_rpc_resources()
            raise

    @override
    def _create_wallet(self, config: MoneroWalletConfig) -> MoneroWallet:
        try:
            return Utils.create_wallet_rpc(config)
        except Exception:
            Utils.free_wallet_rpc_resources()
            raise

    @override
    def _close_wallet(self, wallet: MoneroWallet, save: bool = False) -> None:
        wallet.close(save)
        Utils.free_wallet_rpc_resource(wallet)

    @override
    def _get_seed_languages(self) -> list[str]:
        return self.get_test_wallet().get_seed_languages()

    @override
    def before_all(self) -> None:
        super().before_all()
        # if full tests ran, wait for full wallet's pool txs to confirm
        if Utils.WALLET_FULL_TESTS_RUN:
            Utils.clear_wallet_full_txs_pool()

    @override
    def after_each(self, request: pytest.FixtureRequest) -> None:
        Utils.free_wallet_rpc_resources()
        super().after_each(request)

    @override
    def get_daemon_rpc_uri(self) -> str:
        return Utils.DAEMON_RPC_URI if not Utils.IN_CONTAINER else Utils.CONTAINER_DAEMON_RPC_URI

    #endregion

    #region Tests

    # Can indicate if multisig import is needed for correct balance information
    #@pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    @pytest.mark.skip("TODO")
    def test_is_multisig_needed(self, wallet: MoneroWallet) -> None:
        # TODO test with multisig wallet
        assert wallet.is_multisig_import_needed() is False, "Expected non-multisig wallet"

    # Can save the wallet
    @pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_save(self, wallet: MoneroWallet) -> None:
        wallet.save()

    #endregion

    #region Not Supported Tests

    @pytest.mark.not_supported
    @override
    def test_get_daemon_max_peer_height(self, wallet: MoneroWallet) -> None:
        return super().test_get_daemon_max_peer_height(wallet)

    @pytest.mark.not_supported
    @override
    def test_daemon(self, wallet: MoneroWallet) -> None:
        return super().test_daemon(wallet)

    @pytest.mark.not_supported
    @override
    def test_get_seed_language(self, wallet: MoneroWallet) -> None:
        return super().test_get_seed_language(wallet)

    @pytest.mark.not_supported
    @override
    def test_get_height_by_date(self, wallet: MoneroWallet) -> None:
        return super().test_get_height_by_date(wallet)

    #endregion

    #region Disabled Tests

    @pytest.mark.skip(reason="TODO implement get_txs")
    @override
    def test_send(self, wallet: MoneroWallet) -> None:
        return super().test_send(wallet)

    @pytest.mark.skip(reason="TODO implement get_txs")
    @override
    def test_send_with_payment_id(self, wallet: MoneroWallet) -> None:
        raise Exception("Not supported")

    @pytest.mark.skip(reason="TODO implement get_txs")
    @override
    def test_send_split(self, wallet: MoneroWallet) -> None:
        return super().test_send_split(wallet)

    @pytest.mark.not_supported
    @override
    def test_create_then_relay(self, wallet: MoneroWallet) -> None:
        return super().test_create_then_relay(wallet)

    @pytest.mark.skip(reason="TODO implement get_txs")
    @override
    def test_create_then_relay_split(self, wallet: MoneroWallet) -> None:
        return super().test_create_then_relay_split(wallet)

    @pytest.mark.skip(reason="TODO implement get_txs")
    @override
    def test_get_txs_wallet(self, wallet: MoneroWallet) -> None:
        return super().test_get_txs_wallet(wallet)

    @pytest.mark.skip(reason="TODO monero-project")
    @override
    def test_get_public_view_key(self, wallet: MoneroWallet) -> None:
        return super().test_get_public_view_key(wallet)

    @pytest.mark.skip(reason="TODO monero-project")
    @override
    def test_get_public_spend_key(self, wallet: MoneroWallet) -> None:
        return super().test_get_public_spend_key(wallet)

    @pytest.mark.skip(reason="TODO")
    @override
    def test_wallet_equality_ground_truth(self, wallet: MoneroWallet) -> None:
        return super().test_wallet_equality_ground_truth(wallet)

    @pytest.mark.skip(reason="TODO")
    @override
    def test_set_tx_note(self, wallet: MoneroWallet) -> None:
        return super().test_set_tx_note(wallet)

    @pytest.mark.skip(reason="TODO")
    @override
    def test_set_tx_notes(self, wallet: MoneroWallet) -> None:
        return super().test_set_tx_notes(wallet)

    @pytest.mark.skip(reason="TODO")
    @override
    def test_export_key_images(self, wallet: MoneroWallet) -> None:
        return super().test_export_key_images(wallet)

    @pytest.mark.skip(reason="TODO (monero-project): https://github.com/monero-project/monero/issues/5812")
    @override
    def test_import_key_images(self, wallet: MoneroWallet) -> None:
        return super().test_import_key_images(wallet)

    @pytest.mark.skip(reason="TODO")
    @override
    def test_get_new_key_images_from_last_import(self, wallet: MoneroWallet) -> None:
        return super().test_get_new_key_images_from_last_import(wallet)

    @pytest.mark.skip(reason="TODO")
    @override
    def test_subaddress_lookahead(self, wallet: MoneroWallet) -> None:
        return super().test_subaddress_lookahead(wallet)

    @pytest.mark.skip(reason="TODO")
    @override
    def test_get_subaddress_address_out_of_range(self, wallet: MoneroWallet) -> None:
        return super().test_get_subaddress_address_out_of_range(wallet)

    #endregion
