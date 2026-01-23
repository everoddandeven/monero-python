#include "py_monero_daemon_default.h"


void PyMoneroDaemonDefault::add_listener(const std::shared_ptr<PyMoneroDaemonListener> &listener) {
  boost::lock_guard<boost::recursive_mutex> lock(m_listeners_mutex);
  m_listeners.push_back(listener);
  refresh_listening();
}

void PyMoneroDaemonDefault::remove_listener(const std::shared_ptr<PyMoneroDaemonListener> &listener) {
  boost::lock_guard<boost::recursive_mutex> lock(m_listeners_mutex);
  m_listeners.erase(std::remove_if(m_listeners.begin(), m_listeners.end(), [&listener](std::shared_ptr<PyMoneroDaemonListener> iter){ return iter == listener; }), m_listeners.end());
  refresh_listening();
}

void PyMoneroDaemonDefault::remove_listeners() {
  boost::lock_guard<boost::recursive_mutex> lock(m_listeners_mutex);
  m_listeners.clear();
  refresh_listening();
}

boost::optional<std::shared_ptr<monero::monero_tx>> PyMoneroDaemonDefault::get_tx(const std::string& tx_hash, bool prune) { 
  std::vector<std::string> hashes;
  hashes.push_back(tx_hash);
  auto txs = get_txs(hashes, prune);
  boost::optional<std::shared_ptr<monero::monero_tx>> tx;

  if (txs.size() > 0) {
    tx = txs[0];
  }

  return tx;
}

void PyMoneroDaemonDefault::relay_tx_by_hash(std::string& tx_hash) { 
  std::vector<std::string> tx_hashes;
  tx_hashes.push_back(tx_hash);
  relay_txs_by_hash(tx_hashes);
}

PyMoneroKeyImageSpentStatus PyMoneroDaemonDefault::get_key_image_spent_status(std::string& key_image) { 
  std::vector<std::string> key_images;
  key_images.push_back(key_image);
  auto statuses = get_key_image_spent_statuses(key_images);
  if (statuses.empty()) throw std::runtime_error("Could not get key image spent status");
  return statuses[0];
}

boost::optional<std::string> PyMoneroDaemonDefault::get_tx_hex(const std::string& tx_hash, bool prune) { 
  std::vector<std::string> hashes;
  hashes.push_back(tx_hash);
  auto hexes = get_tx_hexes(hashes, prune);
  boost::optional<std::string> hex;
  if (hexes.size() > 0) {
    hex = hexes[0];
  }

  return hex;
}

void PyMoneroDaemonDefault::submit_block(const std::string& block_blob) { 
  std::vector<std::string> block_blobs;
  block_blobs.push_back(block_blob);
  return submit_blocks(block_blobs);
}

void PyMoneroDaemonDefault::set_peer_ban(const std::shared_ptr<PyMoneroBan>& ban) {
  if (ban == nullptr) throw std::runtime_error("Ban is none");
  std::vector<std::shared_ptr<PyMoneroBan>> bans;
  bans.push_back(ban);
  set_peer_bans(bans);
}
