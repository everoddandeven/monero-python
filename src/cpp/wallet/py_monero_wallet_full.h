#pragma once

#include "py_monero_wallet.h"


class PyMoneroWalletFull : public monero::monero_wallet_full {
public:

  bool is_closed() const { return m_is_closed; }
  void close(bool save = false) override;
  void set_account_label(uint32_t account_idx, const std::string& label);

  std::vector<std::shared_ptr<monero_key_image>> get_new_key_images_from_last_import() {
    throw std::runtime_error("get_new_key_images_from_last_import(): not implemented");
  }

protected:
  bool m_is_closed = false;
};
