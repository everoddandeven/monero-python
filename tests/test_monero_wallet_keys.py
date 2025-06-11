import pytest
from typing import Optional
from typing_extensions import override
from monero import (
  MoneroWalletKeys, MoneroWalletConfig, MoneroWallet
)
from utils import MoneroTestUtils as Utils

from test_monero_wallet_common import BaseTestMoneroWallet


class TestMoneroWalletKeys(BaseTestMoneroWallet):

  _wallet: MoneroWalletKeys = Utils.get_wallet_keys() # type: ignore

  @override
  def _create_wallet(self, config: MoneroWalletConfig):
    print(f"create_wallet()")
    # assign defaults
    if (config is None):
      config = MoneroWalletConfig()
      print(f"create_wallet(self): created config")

    random: bool = config.seed is None and config.primary_address is None and config.private_spend_key is None
    print(f"create_wallet(self): random = {random}")
    if config.path is None:
      config.path = Utils.TEST_WALLETS_DIR + "/" + Utils.get_random_string()
    if config.password is None:
      config.password = Utils.WALLET_PASSWORD
    if config.network_type is None:
      config.network_type = Utils.NETWORK_TYPE
    if (config.restore_height is None and not random):
      config.restore_height = 0
    
    # create wallet
    if random:
      wallet = MoneroWalletKeys.create_wallet_random(config)
    elif config.seed is not None and config.seed != "":
      wallet = MoneroWalletKeys.create_wallet_from_seed(config)
    elif config.primary_address is not None and config.private_view_key is not None:
      wallet = MoneroWalletKeys.create_wallet_from_keys(config)
    elif config.primary_address is not None and config.private_spend_key is not None:
      wallet = MoneroWalletKeys.create_wallet_from_keys(config)
    else:
      raise Exception("Invalid configuration")
    
    return wallet

  @override
  def _open_wallet(self, config: Optional[MoneroWalletConfig]) -> MoneroWallet:
    raise NotImplementedError("TestMoneroWalletKeys._open_wallet(): not supported")

  @override
  def _close_wallet(self, wallet: MoneroWallet, save: bool = False) -> None:
    raise NotImplementedError("TestMoneroWalletKeys._close_wallet(): not supported")

  @override
  def _get_seed_languages(self) -> list[str]:
    return self._wallet.get_seed_languages()
  
  @override
  def get_test_wallet(self) -> MoneroWallet:
    return Utils.get_wallet_keys()

  @pytest.mark.skip(reason="Not supported")
  @override
  def test_get_path(self) -> None:
    return super().test_get_path()
  
  @pytest.mark.skip(reason="Not supported")
  @override
  def test_set_daemon_connection(self):
    return super().test_set_daemon_connection()
  
  @pytest.mark.skip(reason="Not supported")
  @override
  def test_sync_without_progress(self):
    return super().test_sync_without_progress()
  