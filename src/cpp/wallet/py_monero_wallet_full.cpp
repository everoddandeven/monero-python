#include "py_monero_wallet_full.h"


void PyMoneroWalletFull::close(bool save) {
  if (m_is_closed) throw std::runtime_error("Wallet already closed");
  monero::monero_wallet_full::close(save);
}

void PyMoneroWalletFull::set_account_label(uint32_t account_idx, const std::string& label) {
  set_subaddress_label(account_idx, 0, label);
}
