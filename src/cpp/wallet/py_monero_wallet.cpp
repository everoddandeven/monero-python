#include "py_monero_wallet.h"


void PyMoneroWalletListener::on_sync_progress(uint64_t height, uint64_t start_height, uint64_t end_height, double percent_done, const std::string& message) {
  PYBIND11_OVERRIDE(void, monero_wallet_listener, on_sync_progress, height, start_height, end_height, percent_done, message);
}

void PyMoneroWalletListener::on_new_block(uint64_t height) {
  PYBIND11_OVERRIDE(void, monero_wallet_listener, on_new_block, height);
}

void PyMoneroWalletListener::on_balances_changed(uint64_t new_balance, uint64_t new_unlocked_balance) {
  PYBIND11_OVERRIDE(void, monero_wallet_listener, on_balances_changed, new_balance, new_unlocked_balance);
}

void PyMoneroWalletListener::on_output_received(const monero_output_wallet& output) {
  PYBIND11_OVERRIDE(void, monero_wallet_listener, on_output_received, output);
}

void PyMoneroWalletListener::on_output_spent(const monero_output_wallet& output) {
  PYBIND11_OVERRIDE(void, monero_wallet_listener, on_output_spent, output);
}

void PyMoneroWallet::announce_new_block(uint64_t height) {
  for (const auto &listener : m_listeners) {
    try {
      listener->on_new_block(height);
    } catch (const std::exception &e) {
      std::cout << "Error: " << e.what() << std::endl;
    }
  }
}

void PyMoneroWallet::announce_sync_progress(uint64_t height, uint64_t start_height, uint64_t end_height, float percent_done, const std::string &message) {
  for (const auto &listener : m_listeners) {
    try {
      listener->on_sync_progress(height, start_height, end_height, percent_done, message);
    } catch (const std::exception &e) {
      std::cout << "Error: " << e.what() << std::endl;
    }
  }
}

void PyMoneroWallet::announce_balances_changed(uint64_t balance, uint64_t unlocked_balance) {
  for (const auto &listener : m_listeners) {
    try {
      listener->on_balances_changed(balance, unlocked_balance);
    } catch (const std::exception &e) {
      std::cout << "Error: " << e.what() << std::endl;
    }
  }
}

void PyMoneroWallet::announce_output_spent(const std::shared_ptr<monero::monero_output_wallet> &output) {
  for (const auto &listener : m_listeners) {
    try {
      listener->on_output_spent(*output);
    } catch (const std::exception &e) {
      std::cout << "Error: " << e.what() << std::endl;
    }
  }
}

void PyMoneroWallet::announce_output_received(const std::shared_ptr<monero::monero_output_wallet> &output) {
  for (const auto &listener : m_listeners) {
    try {
      listener->on_output_received(*output);
    } catch (const std::exception &e) {
      std::cout << "Error: " << e.what() << std::endl;
    }
  }
}

std::shared_ptr<PyMoneroWalletBalance> PyMoneroWallet::get_balances(boost::optional<uint32_t> account_idx, boost::optional<uint32_t> subaddress_idx) const {
  throw std::runtime_error("MoneroWallet::get_balances(): not implemented");
}
