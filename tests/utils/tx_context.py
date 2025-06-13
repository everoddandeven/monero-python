from __future__ import annotations

from typing import Optional
from monero import MoneroWallet, MoneroTxConfig


class TxContext:

  wallet: Optional[MoneroWallet]
  config: Optional[MoneroTxConfig]
  hasOutgoingTransfer: Optional[bool]
  hasIncomingTransfers: Optional[bool]
  hasDestinations: Optional[bool]
  isCopy: Optional[bool] # indicates if a copy is being tested which means back references won't be the same
  includeOutputs: Optional[bool]
  isSendResponse: Optional[bool]
  isSweepResponse: Optional[bool]
  isSweepOutputResponse: Optional[bool]  # TODO monero-wallet-rpc: this only necessary because sweep_output does not return account index
  
  def __init__(self, ctx: Optional[TxContext] = None) -> None:
    if ctx is not None:
      self.wallet = ctx.wallet
      self.config = ctx.config
      self.hasOutgoingTransfer = ctx.hasOutgoingTransfer
      self.hasIncomingTransfers = ctx.hasIncomingTransfers
      self.hasDestinations = ctx.hasDestinations
      self.isCopy = ctx.isCopy
      self.includeOutputs = ctx.includeOutputs
      self.isSendResponse = ctx.isSendResponse
      self.isSweepResponse = ctx.isSweepResponse
      self.isSweepOutputResponse = ctx.isSweepOutputResponse
