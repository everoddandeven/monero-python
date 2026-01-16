#include "py_monero_wallet_full.h"


void PyMoneroWalletFull::close(bool save) {
  if (m_is_closed) throw std::runtime_error("Wallet already closed");
  monero::monero_wallet_full::close(save);
}

void PyMoneroWalletFull::set_account_label(uint32_t account_idx, const std::string& label) {
  set_subaddress_label(account_idx, 0, label);
}

monero_wallet_full* PyMoneroWalletFull::create_wallet(const monero_wallet_config& config, std::unique_ptr<epee::net_utils::http::http_client_factory> http_client_factory) {
  try {
    return monero_wallet_full::create_wallet(config, std::move(http_client_factory));
  } catch(const std::exception& ex) {
    std::string msg = ex.what();
    if (msg.find("file already exists") != std::string::npos && config.m_path != boost::none)
      msg = std::string("Wallet already exists: ") + config.m_path.get();
    throw PyMoneroError(msg);
  }
}
