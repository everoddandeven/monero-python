#pragma once

#include "py_monero_daemon.h"

class PyMoneroDaemonDefault : public PyMoneroDaemon {
public:

  std::vector<std::shared_ptr<PyMoneroDaemonListener>> get_listeners() override { return m_listeners; }
  void add_listener(const std::shared_ptr<PyMoneroDaemonListener> &listener) override;
  void remove_listener(const std::shared_ptr<PyMoneroDaemonListener> &listener) override;
  void remove_listeners() override;
  boost::optional<std::shared_ptr<monero::monero_tx>> get_tx(const std::string& tx_hash, bool prune = false) override;
  void relay_tx_by_hash(std::string& tx_hash) override;
  PyMoneroKeyImageSpentStatus get_key_image_spent_status(std::string& key_image) override;
  boost::optional<std::string> get_tx_hex(const std::string& tx_hash, bool prune = false);
  void submit_block(const std::string& block_blob) override;
  void set_peer_ban(const std::shared_ptr<PyMoneroBan>& ban) override;

protected:
  mutable boost::recursive_mutex m_listeners_mutex;
  std::vector<std::shared_ptr<PyMoneroDaemonListener>> m_listeners;

  virtual void refresh_listening() { }
};

