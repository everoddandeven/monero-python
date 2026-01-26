import pytest
import logging

from monero import MoneroWallet, MoneroWalletConfig, MoneroDaemonRpc, MoneroWalletRpc

from typing_extensions import override
from utils import TestUtils as Utils
from test_monero_wallet_common import BaseTestMoneroWallet

logger: logging.Logger = logging.getLogger("TestMoneroWalletRpc")


class TestMoneroWalletRpc(BaseTestMoneroWallet):

    _daemon: MoneroDaemonRpc = Utils.get_daemon_rpc()
    _wallet: MoneroWalletRpc = Utils.get_wallet_rpc() # type: ignore

    #region Overrides

    @override
    def get_test_wallet(self) -> MoneroWallet:
        return Utils.get_wallet_rpc()

    @override
    def _open_wallet(self, config: MoneroWalletConfig | None) -> MoneroWallet:
        try:
            return Utils.open_wallet_rpc(config)
        except Exception as e:
            Utils.free_wallet_rpc_resources()
            raise e

    @override
    def _create_wallet(self, config: MoneroWalletConfig) -> MoneroWallet:
        try:
            return Utils.create_wallet_rpc(config)
        except Exception as e:
            Utils.free_wallet_rpc_resources()
            raise e

    @override
    def _close_wallet(self, wallet: MoneroWallet, save: bool = False) -> None:
        wallet.close(save)
        Utils.free_wallet_rpc_resource(wallet)

    @override
    def _get_seed_languages(self) -> list[str]:
        return self._wallet.get_seed_languages() # type: ignore

    @pytest.fixture(autouse=True)
    @override
    def before_each(self, request: pytest.FixtureRequest):
        logger.info(f"Before test {request.node.name}") # type: ignore
        yield
        Utils.free_wallet_rpc_resources()
        logger.info(f"After test {request.node.name}") # type: ignore

    @override
    def get_daemon_rpc_uri(self) -> str:
        return Utils.DAEMON_RPC_URI if not Utils.IN_CONTAINER else Utils.CONTAINER_DAEMON_RPC_URI

    #endregion

    #region Tests

    # Can indicate if multisig import is needed for correct balance information
    #@pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    @pytest.mark.skip("TODO")
    def test_is_multisig_needed(self):
        # TODO test with multisig wallet
        assert self._wallet.is_multisig_import_needed() is False, "Expected non-multisig wallet"

    # Can save the wallet
    @pytest.mark.skipif(Utils.TEST_NON_RELAYS is False, reason="TEST_NON_RELAYS disabled")
    def test_save(self):
        self._wallet.save()

    #endregion

    #region Disabled Tests

    @pytest.mark.skip(reason="Not implemented for wallet rpc")
    def test_get_daemon_max_peer_height(self) -> None:
        return super().test_get_daemon_max_peer_height()

    @pytest.mark.skip(reason="Not supported")
    def test_daemon(self) -> None:
        return super().test_daemon()

    @pytest.mark.skip(reason="Not supported")
    @override
    def test_get_seed_language(self):
        return super().test_get_seed_language()

    @pytest.mark.skip(reason="Not supported")
    @override
    def test_get_height_by_date(self):
        return super().test_get_height_by_date()

    @pytest.mark.skip(reason="TODO monero-project")
    @override
    def test_get_public_view_key(self):
        return super().test_get_public_view_key()

    @pytest.mark.skip(reason="TODO monero-project")
    @override
    def test_get_public_spend_key(self):
        return super().test_get_public_spend_key()

    @pytest.mark.skip(reason="TODO")
    @override
    def test_wallet_equality_ground_truth(self):
        return super().test_wallet_equality_ground_truth()

    @pytest.mark.skip(reason="TODO")
    @override
    def test_get_payment_uri(self):
        return super().test_get_payment_uri()

    @pytest.mark.skip(reason="TODO")
    @override
    def test_set_tx_note(self) -> None:
        return super().test_set_tx_note()

    @pytest.mark.skip(reason="TODO")
    @override
    def test_set_tx_notes(self):
        return super().test_set_tx_notes()

    @pytest.mark.skip(reason="TODO")
    @override
    def test_export_key_images(self):
        return super().test_export_key_images()

    @pytest.mark.skip(reason="TODO (monero-project): https://github.com/monero-project/monero/issues/5812")
    @override
    def test_import_key_images(self):
        return super().test_import_key_images()

    @pytest.mark.skip(reason="TODO")
    @override
    def test_get_new_key_images_from_last_import(self):
        return super().test_get_new_key_images_from_last_import()

    @pytest.mark.skip(reason="TODO")
    @override
    def test_subaddress_lookahead(self) -> None:
        return super().test_subaddress_lookahead()

    @pytest.mark.skip(reason="TODO")
    @override
    def test_get_subaddress_address_out_of_range(self):
        return super().test_get_subaddress_address_out_of_range()

    #endregion
