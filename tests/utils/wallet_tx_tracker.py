from time import sleep

from monero import MoneroDaemon, MoneroWallet
from .const import MINING_ADDRESS


class WalletTxTracker:

  _clearedWallets: set[MoneroWallet]

  def __init__(self) -> None:
    self._clearedWallets = set()

  def reset(self) -> None:
    self._clearedWallets.clear()

  def wait_for_wallet_txs_to_clear_pool(self, daemon: MoneroDaemon, sync_period_ms: int, wallets: list[MoneroWallet]) -> None:
    
    # get wallet tx hashes
    txHashesWallet: set[str] = set()

    for wallet in wallets:
      if wallet not in self._clearedWallets:
        wallet.sync()
        for tx in wallet.get_txs():
          assert tx.hash is not None
          txHashesWallet.add(tx.hash)
    
    # loop until all wallet txs clear from pool
    isFirst: bool = True
    miningStarted: bool = False
    # daemon = TestUtils.getDaemonRpc()
    while True:

      # get hashes of relayed, non-failed txs in the pool
      txHashesPool: set[str] = set()
      for tx in daemon.get_tx_pool():
        assert tx.hash is not None
        if not tx.is_relayed:
          continue
        elif tx.is_failed:
          daemon.flush_tx_pool(tx.hash)  # flush tx if failed
        else:
          txHashesPool.add(tx.hash)
      
      # get hashes to wait for as intersection of wallet and pool txs
      txHashesPool = txHashesPool.intersection(txHashesWallet)
      
      # break if no txs to wait for
      if len(txHashesPool) == 0:
        break

      # if first time waiting, log message and start mining
      if isFirst:
        isFirst = False
        print("Waiting for wallet txs to clear from the pool in order to fully sync and avoid double spend attempts (known issue)")
        miningStatus = daemon.get_mining_status()
        if (not miningStatus.is_active):
          try:
            daemon.start_mining(MINING_ADDRESS, 1, False, False)
            miningStarted = True
          except: # no problem
            pass
      
      # sleep for a moment
      sleep(sync_period_ms)
    
    # stop mining if started mining
    if (miningStarted): 
      daemon.stop_mining()
    
    # sync wallets with the pool
    for wallet in wallets:
      wallet.sync()
      self._clearedWallets.add(wallet)

  def wait_for_unlocked_balance(self, daemon: MoneroDaemon, sync_period_ms: int, wallet: MoneroWallet, accountIndex: int, subaddressIndex: int | None, minAmount: int | None = None):
    if minAmount is None:
      minAmount = 0
    
    # check if wallet has balance
    if (subaddressIndex is not None and wallet.get_balance(accountIndex, subaddressIndex) < minAmount):
      raise Exception("Wallet does not have enough balance to wait for")
    elif subaddressIndex is None and wallet.get_balance(accountIndex) < minAmount:
      raise Exception("Wallet does not have enough balance to wait for")
    
    # check if wallet has unlocked balance
    if subaddressIndex is not None:
      unlockedBalance = wallet.get_unlocked_balance(accountIndex, subaddressIndex)
    else:
      unlockedBalance = wallet.get_unlocked_balance(accountIndex)

    if (unlockedBalance > minAmount):
      return unlockedBalance
   
    # start mining
    # daemon = TestUtils.getDaemonRpc()
    miningStarted: bool = False
    if not daemon.get_mining_status().is_active:
      try:
        daemon.start_mining(MINING_ADDRESS, 1, False, False)
        miningStarted = True
      except:
        pass # it's all ok my friend ...
    
    # wait for unlocked balance // TODO: promote to MoneroWallet interface?
    print("Waiting for unlocked balance")
    while (unlockedBalance < minAmount):
      if subaddressIndex is not None:
        unlockedBalance = wallet.get_unlocked_balance(accountIndex, subaddressIndex)
      else:
        unlockedBalance = wallet.get_unlocked_balance(accountIndex)
        
      try: 
        sleep(sync_period_ms)
      except:
        pass

    # stop mining if started
    if (miningStarted):
      daemon.stop_mining()
    
    return unlockedBalance
