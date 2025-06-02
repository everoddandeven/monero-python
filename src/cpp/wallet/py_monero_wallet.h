#include <pybind11/stl_bind.h>
#include <pybind11/eval.h>
#include "daemon/py_monero_daemon.h"

namespace {
  std::unordered_map<const void*, bool> wallet_closed_map;
  std::mutex wallet_map_mutex;
}

void set_wallet_closed(const void* wallet, bool value) {
  std::lock_guard<std::mutex> lock(wallet_map_mutex);
  wallet_closed_map[wallet] = value;
}

bool is_wallet_closed(const void* wallet) {
  std::lock_guard<std::mutex> lock(wallet_map_mutex);
  auto it = wallet_closed_map.find(wallet);
  return it != wallet_closed_map.end() ? it->second : false;
}

void assert_wallet_is_not_closed(const void* wallet) {
  if (is_wallet_closed(wallet)) throw std::runtime_error("Wallet is closed");
}

enum PyMoneroAddressType : uint8_t {
  PRIMARY_ADDRESS = 0,
  INTEGRATED_ADDRESS,
  SUBADDRESS
};

class PyMoneroTxQuery : public monero::monero_tx_query {
public:

  static void decontextualize(const std::shared_ptr<monero::monero_tx_query> &query) {
    query->m_is_incoming = boost::none;
    query->m_is_outgoing = boost::none;
    query->m_transfer_query = boost::none;
    query->m_input_query = boost::none;
    query->m_output_query = boost::none;
  }

  static void decontextualize(monero::monero_tx_query &query) {
    query.m_is_incoming = boost::none;
    query.m_is_outgoing = boost::none;
    query.m_transfer_query = boost::none;
    query.m_input_query = boost::none;
    query.m_output_query = boost::none;
  }

};

class PyMoneroOutputQuery : public monero::monero_output_query {
public:
  static bool is_contextual(const std::shared_ptr<monero::monero_output_query> &query) {
    if (query == nullptr) return false;
    return is_contextual(*query);
  }

  static bool is_contextual(const monero::monero_output_query &query) {
    if (query.m_tx_query == boost::none) return false;
    if (query.m_tx_query.get()->m_is_incoming != boost::none) return true;       // requires context of all transfers
    if (query.m_tx_query.get()->m_is_outgoing != boost::none) return true;
    if (query.m_tx_query.get()->m_transfer_query != boost::none) return true; // requires context of transfers
    return false;
  }
};

class PyMoneroTransferQuery : public monero::monero_transfer_query {
public:
  static bool is_contextual(const std::shared_ptr<monero::monero_transfer_query> &query) {
    if (query == nullptr) return false;
    return is_contextual(*query);
  }

  static bool is_contextual(const monero::monero_transfer_query &query) {
    if (query.m_tx_query == boost::none) return false;
    if (query.m_tx_query.get()->m_is_incoming != boost::none) return true;       // requires context of all transfers
    if (query.m_tx_query.get()->m_is_outgoing != boost::none) return true;
    if (query.m_tx_query.get()->m_input_query != boost::none) return true;    // requires context of inputs
    if (query.m_tx_query.get()->m_output_query != boost::none) return true;    // requires context of inputs
    return false;
  }
};

class PyMoneroWalletConfig : public monero::monero_wallet_config {
public:
  boost::optional<std::shared_ptr<PyMoneroConnectionManager>> m_connection_manager;

  PyMoneroWalletConfig() {}

};

class PyMoneroTxWallet : public monero::monero_tx_wallet {
public:
  static bool decode_rpc_type(const std::string &rpc_type, const std::shared_ptr<monero::monero_tx_wallet> &tx) {
    bool is_outgoing = false;
    if (rpc_type == std::string("in")) {
      is_outgoing = false;
      tx->m_is_confirmed = true;
      tx->m_in_tx_pool = false;
      tx->m_is_relayed = true;
      tx->m_relay = true;
      tx->m_is_failed = false;
      tx->m_is_miner_tx = false;
    } else if (rpc_type == std::string("out")) {
      is_outgoing = true;
      tx->m_is_confirmed = true;
      tx->m_in_tx_pool = false;
      tx->m_is_relayed = true;
      tx->m_relay = true;
      tx->m_is_failed = false;
      tx->m_is_miner_tx = false;
    } else if (rpc_type == std::string("pool")) {
      is_outgoing = false;
      tx->m_is_confirmed = false;
      tx->m_in_tx_pool = true;
      tx->m_is_relayed = true;
      tx->m_relay = true;
      tx->m_is_failed = false;
      tx->m_is_miner_tx = false;  // TODO: but could it be?
    } else if (rpc_type == std::string("pending")) {
      is_outgoing = true;
      tx->m_is_confirmed = false;
      tx->m_in_tx_pool = true;
      tx->m_is_relayed = true;
      tx->m_relay = true;
      tx->m_is_failed = false;
      tx->m_is_miner_tx = false;
    } else if (rpc_type == std::string("block")) {
      is_outgoing = false;
      tx->m_is_confirmed = true;
      tx->m_in_tx_pool = false;
      tx->m_is_relayed = true;
      tx->m_relay = true;
      tx->m_is_failed = false;
      tx->m_is_miner_tx = true;
    } else if (rpc_type == std::string("failed")) {
      is_outgoing = true;
      tx->m_is_confirmed = false;
      tx->m_in_tx_pool = false;
      tx->m_is_relayed = true;
      tx->m_relay = true;
      tx->m_is_failed = true;
      tx->m_is_miner_tx = false;
    } else {
      throw std::runtime_error(std::string("Unrecognized transfer type: ") + rpc_type);
    }
    return is_outgoing;
  }

  static void init_sent(const monero::monero_tx_config &config, std::shared_ptr<monero::monero_tx_wallet> &tx, bool copy_destinations) {
    bool relay = config.m_relay == true;
    tx->m_is_outgoing = true;
    tx->m_is_confirmed = false;
    tx->m_num_confirmations = 0;
    tx->m_in_tx_pool = relay;
    tx->m_relay = relay;
    tx->m_is_relayed = relay;
    tx->m_is_miner_tx = false;
    tx->m_is_failed = false;
    tx->m_is_locked = true;
    tx->m_ring_size = monero_utils::RING_SIZE;

    auto outgoing_transfer = std::make_shared<monero::monero_outgoing_transfer>();
    outgoing_transfer->m_tx = tx;

    if (config.m_subaddress_indices.size() == 1) {
      outgoing_transfer->m_subaddress_indices = config.m_subaddress_indices;
    }

    if (copy_destinations) {
      for(const auto &conf_dest : config.m_destinations) {
        auto dest = std::make_shared<monero::monero_destination>();
        conf_dest->copy(conf_dest, dest);
        outgoing_transfer->m_destinations.push_back(dest);
      }
    }

    tx->m_outgoing_transfer = outgoing_transfer;
    tx->m_payment_id = config.m_payment_id;
    if (tx->m_unlock_time == boost::none) tx->m_unlock_time = 0;
    if (tx->m_relay) {
      if (tx->m_last_relayed_timestamp == boost::none) {
        // TODO set current timestamp
      }
      if (tx->m_is_double_spend_seen == boost::none) tx->m_is_double_spend_seen = false;
    }
  }

  static void from_property_tree_with_transfer(const boost::property_tree::ptree& node, const std::shared_ptr<monero::monero_tx_wallet>& tx, boost::optional<bool> &is_outgoing, const monero_tx_config &config) {  
    std::shared_ptr<monero::monero_block> header = nullptr;
    std::shared_ptr<monero::monero_outgoing_transfer> outgoing_transfer = nullptr;
    std::shared_ptr<monero::monero_incoming_transfer> incoming_transfer = nullptr;

    bool key_found = false;

    for (auto it = node.begin(); it != node.end(); ++it) {
      std::string key = it->first;

      if (key == std::string("type")) {
        is_outgoing = decode_rpc_type(it->second.data(), tx);
        key_found = true;
      }
      else if (key == std::string("txid")) tx->m_hash = it->second.data();
      else if (key == std::string("tx_hash")) tx->m_hash = it->second.data();
      else if (key == std::string("fee")) tx->m_fee = it->second.get_value<uint64_t>();
      else if (key == std::string("note")) tx->m_note = it->second.data();
      else if (key == std::string("tx_key")) tx->m_key = it->second.data();
      else if (key == std::string("tx_size")) tx->m_size = it->second.get_value<uint64_t>();
      else if (key == std::string("unlock_time")) tx->m_unlock_time = it->second.get_value<uint64_t>();
      else if (key == std::string("weight")) tx->m_weight = it->second.get_value<uint64_t>();
      else if (key == std::string("locked")) tx->m_is_locked = it->second.get_value<bool>();
      else if (key == std::string("tx_blob")) tx->m_full_hex = it->second.data();
      else if (key == std::string("tx_metadata")) tx->m_metadata = it->second.data();
      else if (key == std::string("double_spend_seen")) tx->m_is_double_spend_seen = it->second.get_value<bool>();
      else if (key == std::string("block_height") || key == std::string("height")) {
        if (tx->m_is_confirmed) {
          if (header == nullptr) header = std::make_shared<monero::monero_block>();
          header->m_height = it->second.get_value<uint64_t>();
        }
      }
      else if (key == std::string("timestamp")) {
        if (tx->m_is_confirmed) {
          if (header == nullptr) header = std::make_shared<monero::monero_block>();
          header->m_timestamp = it->second.get_value<uint64_t>();
        }
      }
      else if (key == std::string("confirmations")) tx->m_num_confirmations = it->second.get_value<uint64_t>();
      else if (key == std::string("suggested_confirmations_threshold")) {
        if (is_outgoing && outgoing_transfer == nullptr) {
          outgoing_transfer = std::make_shared<monero::monero_outgoing_transfer>();
        }
        else if (!is_outgoing && incoming_transfer == nullptr) {
          incoming_transfer = std::make_shared<monero::monero_incoming_transfer>();
          incoming_transfer->m_tx = tx;
          incoming_transfer->m_num_suggested_confirmations = it->second.get_value<uint64_t>();
        }
      }
      else if (key == std::string("amount")) {
        if (is_outgoing) {
          if (outgoing_transfer == nullptr) outgoing_transfer = std::make_shared<monero::monero_outgoing_transfer>();
          incoming_transfer->m_amount = it->second.get_value<uint64_t>();
        }
        else if (!is_outgoing) {
          if (incoming_transfer == nullptr) incoming_transfer = std::make_shared<monero::monero_incoming_transfer>();
          incoming_transfer->m_tx = tx;
          incoming_transfer->m_amount = it->second.get_value<uint64_t>();
        }
      }
      else if (key == std::string("address")) {
        if (!is_outgoing) {
          if (incoming_transfer == nullptr) incoming_transfer = std::make_shared<monero::monero_incoming_transfer>();
          incoming_transfer->m_tx = tx;
          incoming_transfer->m_address = it->second.data();
        }
      }
      else if (key == std::string("payment_id")) {
        std::string payment_id = it->second.data();
        if (payment_id != std::string("") && payment_id != monero::monero_tx_wallet::DEFAULT_PAYMENT_ID) {
          tx->m_payment_id = payment_id;
        }
      }
      else if (key == std::string("subaddr_indices")) {
        if (is_outgoing) {
          if (outgoing_transfer == nullptr) outgoing_transfer = std::make_shared<monero::monero_outgoing_transfer>();
        }
        else if (!is_outgoing) {
          if (incoming_transfer == nullptr) incoming_transfer = std::make_shared<monero::monero_incoming_transfer>();
          incoming_transfer->m_tx = tx;
        }

        auto node2 = it->second;
        bool first_major = true;
        bool first_minor = true;

        for(auto it2 = node2.begin(); it2 != node2.end(); ++it2) {
          auto node3 = it2->second;

          for(auto it3 = node3.begin(); it3 != node3.end(); ++it3) {
            std::string index_key = it3->first;

            if (index_key == std::string("major") && first_major) {
              if (is_outgoing) outgoing_transfer->m_account_index = it3->second.get_value<uint32_t>();
              else incoming_transfer->m_account_index = it3->second.get_value<uint32_t>();
              first_major = false;
            }
            else if (index_key == std::string("minor")) {
              if (is_outgoing) {
                outgoing_transfer->m_subaddress_indices.push_back(it3->second.get_value<uint32_t>());
              }
              else if (first_minor) {
                incoming_transfer->m_subaddress_index = it3->second.get_value<uint32_t>();
                first_minor = false;
              }
            }
          }
        }
      }
      else if (key == std::string("destinations") || key == std::string("recipients")) {
        if (!is_outgoing) throw std::runtime_error("Expected outgoing tx");
        if (outgoing_transfer == nullptr) {
          outgoing_transfer = std::make_shared<monero::monero_outgoing_transfer>();
          outgoing_transfer->m_tx = tx;
        }
        auto node2 = it->second;

        for(auto it2 = node2.begin(); it2 != node2.end(); ++it2) {
          auto node3 = it2->second;
          auto dest = std::make_shared<monero::monero_destination>();

          for(auto it3 = node3.begin(); it3 != node3.end(); ++it3) {
            std::string _key = it3->first;

            if (_key == std::string("address")) dest->m_address = it3->second.data();
            else if (_key == std::string("amount")) dest->m_amount = it3->second.get_value<uint64_t>();
            else throw std::runtime_error(std::string("Unrecognized transaction destination field: ") + _key);
          }

          outgoing_transfer->m_destinations.push_back(dest);
        }
      }
      else if (key == std::string("amount_in")) tx->m_input_sum = it->second.get_value<uint64_t>();
      else if (key == std::string("amount_out")) tx->m_input_sum = it->second.get_value<uint64_t>();
      else if (key == std::string("change_address")) {
        std::string change_address = it->second.data();
        if (change_address != std::string("")) tx->m_change_address = it->second.data();
      }
      else if (key == std::string("change_amount")) tx->m_change_amount = it->second.get_value<uint64_t>();
      else if (key == std::string("dummy_outputs")) tx->m_num_dummy_outputs = it->second.get_value<uint64_t>();
      //else if (key == std::string("extra")) tx->m_extra = it->second.data();
      else if (key == std::string("ring_size")) tx->m_ring_size = it->second.get_value<uint32_t>();
      else if (key == std::string("spent_key_images")) {
        auto node2 = it->second;

        for(auto it2 = node2.begin(); it2 != node2.end(); ++it2) {
          std::string _key = it2->first;

          if (_key == std::string("key_images")) {
            auto node3 = it2->second;
            if (tx->m_inputs.size() > 0) throw std::runtime_error("inputs should be empty");

            for(auto it3 = node3.begin(); it3 != node3.end(); ++it3) {
              auto output = std::make_shared<monero::monero_output_wallet>();
              auto key_image = std::make_shared<monero::monero_key_image>();

              key_image->m_hex = it3->second.data();
              output->m_key_image = key_image;
              output->m_tx = tx;
              tx->m_inputs.push_back(output);
            }
          }
        }
      }
      else if (key == std::string("amounts_by_dest")) {
        if (!is_outgoing) throw std::runtime_error("Expected outgoing transaction");
        if (outgoing_transfer == nullptr) {
          outgoing_transfer = std::make_shared<monero::monero_outgoing_transfer>();
          outgoing_transfer->m_tx = tx;
        }
        auto node2 = it->second;
        std::vector<uint64_t> amounts_by_dest;
        
        for(auto it2 = node2.begin(); it2 != node2.end(); ++it2) {
          std::string _key = it2->first;

          if (_key == std::string("amounts")) {
            auto node3 = it2->second;

            for(auto it3 = node3.begin(); it3 != node.end(); ++it3) {
              amounts_by_dest.push_back(it3->second.get_value<uint64_t>());
            }
          }
        }

        if (config.m_destinations.size() != amounts_by_dest.size()) throw std::runtime_error("Expected destinations size equal to amounts by dest size");

        for(uint64_t i = 0; i < config.m_destinations.size(); i++) {
          auto dest = std::make_shared<monero::monero_destination>();
          dest->m_address = config.m_destinations[i]->m_address;
          dest->m_amount = amounts_by_dest[i];
          outgoing_transfer->m_destinations.push_back(dest);
        }
      }
    }

    if (!key_found && is_outgoing == boost::none) throw std::runtime_error("Must indicate if tx is outgoing (true) xor incoming (false) since unknown");
    if (header != nullptr) {
      auto block = std::make_shared<monero::monero_block>();
      block->copy(block, header);
      block->m_txs.push_back(tx);
      tx->m_block = block;
    }

    if (is_outgoing && outgoing_transfer != nullptr) {
      if (tx->m_is_confirmed == boost::none) tx->m_is_confirmed = false;
      if (!outgoing_transfer->m_tx->m_is_confirmed) tx->m_num_confirmations = 0;
      tx->m_is_outgoing = true;

      if (tx->m_outgoing_transfer != boost::none) {
        tx->m_outgoing_transfer.get()->merge(tx->m_outgoing_transfer.get(), outgoing_transfer);
      }
      else tx->m_outgoing_transfer = outgoing_transfer;
    }
    else if (is_outgoing != boost::none && is_outgoing == false && incoming_transfer != nullptr) {
      if (tx->m_is_confirmed == boost::none) tx->m_is_confirmed = false;
      if (!incoming_transfer->m_tx->m_is_confirmed) tx->m_num_confirmations = 0;
      tx->m_is_incoming = true;
      tx->m_incoming_transfers.push_back(incoming_transfer);
    }

  }

  static void from_property_tree_with_transfer(const boost::property_tree::ptree& node, const std::shared_ptr<monero::monero_tx_wallet>& tx, boost::optional<bool> &is_outgoing) { 
    monero::monero_tx_config config;
    from_property_tree_with_transfer(node, tx, is_outgoing, config);
  }

  static void from_property_tree_with_output(const boost::property_tree::ptree& node, const std::shared_ptr<monero::monero_tx_wallet>& tx) {  
    tx->m_is_confirmed = true;
    tx->m_is_relayed = true;
    tx->m_is_failed = false;

    auto output = std::make_shared<monero::monero_output_wallet>();
    auto key_image = std::make_shared<monero::monero_key_image>();
    output->m_tx = tx;

    for(auto it = node.begin(); it != node.end(); ++it) {
      std::string key = it->first;

      if (key == std::string("amount")) output->m_amount = it->second.get_value<uint64_t>();
      else if (key == std::string("spent")) output->m_is_spent = it->second.get_value<bool>();
      else if (key == std::string("key_image")) {
        key_image->m_hex = it->second.data();
        output->m_key_image = key_image;
      }
      else if (key == std::string("global_index")) output->m_index = it->second.get_value<uint64_t>();
      else if (key == std::string("tx_hash")) tx->m_hash = it->second.data();
      else if (key == std::string("unlocked")) tx->m_is_locked = !it->second.get_value<bool>();
      else if (key == std::string("frozen")) output->m_is_frozen = it->second.get_value<bool>();
      else if (key == std::string("pubkey")) output->m_stealth_public_key = it->second.data();
      else if (key == std::string("subaddr_index")) {

      }
      else if (key == std::string("block_height")) {
        auto block = std::make_shared<monero::monero_block>();
        block->m_height = it->second.get_value<uint64_t>();
        block->m_txs.push_back(tx);
        tx->m_block = block;
      }
    }

    tx->m_outputs.push_back(output);
  }
};

class PyMoneroTxSet : public monero::monero_tx_set {
public:

  // convert rpc sent txs to monero_tx_set
  static void from_property_tree(const boost::property_tree::ptree& node, const std::shared_ptr<monero::monero_tx_set>& set) {
    for (boost::property_tree::ptree::const_iterator it = node.begin(); it != node.end(); ++it) {
      std::string key = it->first;
      if (key == std::string("multisig_txset")) set->m_multisig_tx_hex = it->second.data();
      else if (key == std::string("unsigned_txset")) set->m_unsigned_tx_hex = it->second.data();
      else if (key == std::string("signed_txset")) set->m_signed_tx_hex = it->second.data();
    }
  }

  static void from_tx(const boost::property_tree::ptree& node, const std::shared_ptr<monero::monero_tx_set>& set, const std::shared_ptr<monero::monero_tx_wallet> &tx, bool is_outgoing, const monero_tx_config &config) {
    from_property_tree(node, set);
    boost::optional<bool> outgoing = is_outgoing;
    PyMoneroTxWallet::from_property_tree_with_transfer(node, tx, outgoing, config);
    set->m_txs.push_back(tx);
  }

  static void from_sent_txs(const boost::property_tree::ptree& node, const std::shared_ptr<monero::monero_tx_set>& set) {
    std::vector<std::shared_ptr<monero::monero_tx_wallet>> txs;
    from_sent_txs(node, set, txs, boost::none);
  }

  static void from_sent_txs(const boost::property_tree::ptree& node, const std::shared_ptr<monero::monero_tx_set>& set, std::vector<std::shared_ptr<monero::monero_tx_wallet>> &txs, const boost::optional<monero_tx_config> &conf) {
    from_property_tree(node, set);
    int num_txs = 0;
    for (boost::property_tree::ptree::const_iterator it = node.begin(); it != node.end(); ++it) {
      std::string key = it->first;
      if (key == std::string("fee_list") && num_txs == 0) {
        auto fee_list_node = it->second;
        for (auto it2 = fee_list_node.begin(); it2 != fee_list_node.end(); ++it2) {
          num_txs++;
        }
      }
      else if (key == std::string("tx_hash_list") && num_txs == 0) {
        auto tx_hash_list_node = it->second;
        for (auto it2 = tx_hash_list_node.begin(); it2 != tx_hash_list_node.end(); ++it2) {
          num_txs++;
        }
      }
    }

    if (num_txs == 0) {
      if (txs.size() > 0) throw std::runtime_error("txs should be empty");
      return;
    }

    if (txs.size() > 0) set->m_txs = txs;
    else {
      for(int i = 0; i < num_txs; i++) {
        auto tx = std::make_shared<monero::monero_tx_wallet>();
        txs.push_back(tx);
      }
    }

    for(const auto &tx : txs) {
      tx->m_tx_set = set;
      tx->m_is_outgoing = true;
    }

    set->m_txs = txs;
  
    for (boost::property_tree::ptree::const_iterator it = node.begin(); it != node.end(); ++it) {
      std::string key = it->first;
      int i = 0;
      if (key == std::string("tx_hash_list") && num_txs == 0) {
        auto node2 = it->second;
        i = 0;
        for (auto it2 = node2.begin(); it2 != node2.end(); ++it2) {
          auto tx = txs[i];
          tx->m_hash = it2->second.data();
          i++;
        }
      }
      else if (key == std::string("tx_key_list") && num_txs == 0) {
        auto node2 = it->second;
        i = 0;
        for (auto it2 = node2.begin(); it2 != node2.end(); ++it2) {
          auto tx = txs[i];
          tx->m_key = it2->second.data();
          i++;
        }
      }
      else if (key == std::string("tx_blob_list") && num_txs == 0) {
        auto node2 = it->second;
        i = 0;
        for (auto it2 = node2.begin(); it2 != node2.end(); ++it2) {
          auto tx = txs[i];
          tx->m_full_hex = it2->second.data();
          i++;
        }
      }
      else if (key == std::string("tx_metadata_list") && num_txs == 0) {
        auto node2 = it->second;
        i = 0;
        for (auto it2 = node2.begin(); it2 != node2.end(); ++it2) {
          auto tx = txs[i];
          tx->m_metadata = it2->second.data();
          i++;
        }
      }
      else if (key == std::string("fee_list") && num_txs == 0) {
        auto node2 = it->second;
        i = 0;
        for (auto it2 = node2.begin(); it2 != node2.end(); ++it2) {
          auto tx = txs[i];
          tx->m_fee = it2->second.get_value<uint64_t>();
          i++;
        }
      }
      else if (key == std::string("amount_list") && num_txs == 0) {
        auto node2 = it->second;
        i = 0;
        for (auto it2 = node2.begin(); it2 != node2.end(); ++it2) {
          auto tx = txs[i];
          auto outgoing_transfer = std::make_shared<monero::monero_outgoing_transfer>();
          outgoing_transfer->m_tx = tx;
          outgoing_transfer->m_amount = it2->second.get_value<uint64_t>();
          tx->m_outgoing_transfer = outgoing_transfer;
          i++;
        }
      }
      else if (key == std::string("weight_list") && num_txs == 0) {
        auto node2 = it->second;
        i = 0;
        for (auto it2 = node2.begin(); it2 != node2.end(); ++it2) {
          auto tx = txs[i];
          tx->m_weight = it2->second.get_value<uint64_t>();
          i++;
        }
      }
      else if (key == std::string("spent_key_images_list") && num_txs == 0) {
        auto node2 = it->second;
        i = 0;
        for (auto it2 = node2.begin(); it2 != node2.end(); ++it2) {
          auto tx = txs[i];
          if (tx->m_inputs.size() > 0) throw std::runtime_error("Expected no inputs in sent tx");
          
          auto node3 = it2->second;
          for (auto it3 = node3.begin(); it3 != node3.end(); ++it3) {
            std::string _key = it3->first;

            if (_key == std::string("key_images")) {
              auto node4 = it3->second;

              for (auto it4 = node4.begin(); it4 != node4.end(); ++it4) {
                auto output = std::make_shared<monero::monero_output_wallet>();
                output->m_key_image = std::make_shared<monero::monero_key_image>();
                output->m_key_image.get()->m_hex = it4->second.data();
                output->m_tx = tx;
                tx->m_inputs.push_back(output);
              }
            }
          }

          i++;
        }
      }
      else if (key == std::string("amounts_by_dest_list") && num_txs == 0) {
        auto node2 = it->second;
        i = 0;
        int destination_idx = 0;

        for (auto it2 = node2.begin(); it2 != node2.end(); ++it2) {
          auto tx = txs[i];
          auto node3 = it2->second;
          for (auto it3 = node3.begin(); it3 != node3.end(); ++it3) {
            std::string _key = it3->first;

            if (_key == std::string("amounts")) {
              std::vector<uint64_t> amounts_by_dest;
              auto node4 = it3->second;
              
              for(auto it4 = node4.begin(); it4 != node4.end(); ++it4) {
                amounts_by_dest.push_back(it4->second.get_value<uint64_t>());
              }

              if (tx->m_outgoing_transfer == boost::none) {
                auto outgoing_transfer = std::make_shared<monero::monero_outgoing_transfer>();
                outgoing_transfer->m_tx = tx;
                tx->m_outgoing_transfer = outgoing_transfer;
              }

              for(auto amount : amounts_by_dest) {
                if (conf == boost::none) throw std::runtime_error("Expected tx configuration");
                auto config = conf.get();
                if (config.m_destinations.size() == 1) {
                  auto dest = std::make_shared<monero::monero_destination>();
                  dest->m_address = config.m_destinations[0]->m_address;
                  dest->m_amount = amount;
                  tx->m_outgoing_transfer.get()->m_destinations.push_back(dest);
                }
                else {
                  auto dest = std::make_shared<monero::monero_destination>();
                  dest->m_address = config.m_destinations[destination_idx]->m_address;
                  dest->m_amount = amount;
                  tx->m_outgoing_transfer.get()->m_destinations.push_back(dest);
                  destination_idx++;
                }
              }
            }
          }

          i++;
        }
      }

    }
  }

  static void from_describe_transfer(const boost::property_tree::ptree& node, const std::shared_ptr<monero::monero_tx_set>& set) {
    for (boost::property_tree::ptree::const_iterator it = node.begin(); it != node.end(); ++it) {
      std::string key = it->first;
      if (key == std::string("desc")) {
        auto node2 = it->second;

        for (auto it2 = node2.begin(); it2 != node2.end(); ++it2) {
          auto tx = std::make_shared<monero::monero_tx_wallet>();
          boost::optional<bool> outgoing = true;
          PyMoneroTxWallet::from_property_tree_with_transfer(it2->second, tx, outgoing);
          tx->m_tx_set = set;
          set->m_txs.push_back(tx);
        }
      }
    }
  }

};


class PyMoneroKeyImage : public monero::monero_key_image {
public:
  PyMoneroKeyImage() {}
  PyMoneroKeyImage(const monero::monero_key_image &key_image) {
    m_hex = key_image.m_hex;
    m_signature = key_image.m_signature;
  }

  rapidjson::Value to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const override {
    // create root
    rapidjson::Value root(rapidjson::kObjectType);

    // set string values
    rapidjson::Value value_str(rapidjson::kStringType);
    if (m_hex != boost::none) monero_utils::add_json_member("key_image", m_hex.get(), allocator, root, value_str);
    if (m_signature != boost::none) monero_utils::add_json_member("signature", m_signature.get(), allocator, root, value_str);

    // return root
    return root;
  }

  static void from_property_tree(const boost::property_tree::ptree& node, const std::shared_ptr<monero::monero_key_image>& key_image) {
    for (boost::property_tree::ptree::const_iterator it = node.begin(); it != node.end(); ++it) {
      std::string key = it->first;
      if (key == std::string("key_image")) key_image->m_hex = it->second.data();
      else if (key == std::string("signature")) key_image->m_signature = it->second.data();
    }
  }

  static void from_property_tree(const boost::property_tree::ptree& node, std::vector<std::shared_ptr<monero::monero_key_image>>& key_images) {
    for (boost::property_tree::ptree::const_iterator it = node.begin(); it != node.end(); ++it) {
      std::string key = it->first;
      if (key == std::string("signed_key_images")) {
        auto key_images_node = it->second;

        for (auto it2 = key_images_node.begin(); it2 != key_images_node.end(); ++it2) {
          auto key_image = std::make_shared<monero::monero_key_image>();
          from_property_tree(it2->second, key_image);
          key_images.push_back(key_image);
        }
      }
    }
  }
};

class PyMoneroKeyImageImportResult : public monero::monero_key_image_import_result {
public:
  static void from_property_tree(const boost::property_tree::ptree& node, const std::shared_ptr<monero::monero_key_image_import_result>& result) {
    for (boost::property_tree::ptree::const_iterator it = node.begin(); it != node.end(); ++it) {
      std::string key = it->first;
      if (key == std::string("height")) result->m_height = it->second.get_value<uint64_t>();
      else if (key == std::string("spent")) result->m_spent_amount = it->second.get_value<uint64_t>();
      else if (key == std::string("unspent")) result->m_unspent_amount = it->second.get_value<uint64_t>();
    }
  }
};

class PyMoneroMultisigInfo : public monero::monero_multisig_info {
public:
  static void from_property_tree(const boost::property_tree::ptree& node, const std::shared_ptr<monero::monero_multisig_info>& info) {
    for (boost::property_tree::ptree::const_iterator it = node.begin(); it != node.end(); ++it) {
      std::string key = it->first;
      if (key == std::string("multisig")) info->m_is_multisig = it->second.get_value<bool>();
      else if (key == std::string("ready")) info->m_is_ready = it->second.get_value<bool>();
      else if (key == std::string("threshold")) info->m_threshold = it->second.get_value<uint32_t>();
      else if (key == std::string("total")) info->m_num_participants = it->second.get_value<uint32_t>();
    }
  }
};

class PyMoneroMultisigInitResult : public monero::monero_multisig_init_result {
public:

  static void from_property_tree(const boost::property_tree::ptree& node, const std::shared_ptr<monero::monero_multisig_init_result>& info) {
    for (boost::property_tree::ptree::const_iterator it = node.begin(); it != node.end(); ++it) {
      std::string key = it->first;
      if (key == std::string("address")) info->m_address = it->second.data();
      else if (key == std::string("multisig_info")) info->m_multisig_hex = it->second.data();
    }
  }
};

class PyMoneroMultisigSignResult : public monero::monero_multisig_sign_result {
public:

  static void from_property_tree(const boost::property_tree::ptree& node, const std::shared_ptr<monero::monero_multisig_sign_result>& res) {
    for (boost::property_tree::ptree::const_iterator it = node.begin(); it != node.end(); ++it) {
      std::string key = it->first;
      if (key == std::string("tx_data_hex")) res->m_signed_multisig_tx_hex = it->second.data();
      else if (key == std::string("tx_hash_list")) {
        auto node2 = it->second;
        for (boost::property_tree::ptree::const_iterator it2 = node2.begin(); it2 != node.end(); ++it2) {
          res->m_tx_hashes.push_back(it2->second.data());
        }
      }
    }
  }
};

class PyMoneroMultisigTxDataParams : public PyMoneroJsonRequestParams {
public:
  boost::optional<std::string> m_multisig_tx_hex;

  PyMoneroMultisigTxDataParams() {}
  PyMoneroMultisigTxDataParams(const std::string& multisig_tx_hex) {
    m_multisig_tx_hex = multisig_tx_hex;
  }

  rapidjson::Value to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const override { 
    rapidjson::Value root(rapidjson::kObjectType); 
    rapidjson::Value value_str(rapidjson::kStringType);
    if (m_multisig_tx_hex != boost::none) monero_utils::add_json_member("tx_data_hex", m_multisig_tx_hex.get(), allocator, root, value_str);
    return root; 
  }
};

class PyMoneroDecodedAddress {
public:
  PyMoneroDecodedAddress(std::string& address, PyMoneroAddressType address_type, monero::monero_network_type network_type) {
    m_address = address;
    m_address_type = address_type;
    m_network_type = network_type;
  }

  std::string m_address;
  PyMoneroAddressType m_address_type;
  monero::monero_network_type m_network_type;
};

class PyMoneroAccountTag {
public:
  PyMoneroAccountTag() { }

  PyMoneroAccountTag(std::string& tag, std::string& label) {
    m_tag = tag;
    m_label = label;
  }

  PyMoneroAccountTag(std::string& tag, std::string& label, std::vector<uint32_t> account_indices) {
    m_tag = tag;
    m_label = label;
    m_account_indices = account_indices;
  }

  boost::optional<std::string> m_tag;
  boost::optional<std::string> m_label;
  std::vector<uint32_t> m_account_indices;

  static void from_property_tree(const boost::property_tree::ptree& node, const std::shared_ptr<PyMoneroAccountTag>& account_tag) {
    for (boost::property_tree::ptree::const_iterator it = node.begin(); it != node.end(); ++it) {
      std::string key = it->first;
      if (key == std::string("tag")) account_tag->m_tag = it->second.data();
      else if (key == std::string("label")) account_tag->m_label = it->second.data();
    }
  }

  static void from_property_tree(const boost::property_tree::ptree& node, std::vector<std::shared_ptr<PyMoneroAccountTag>>& account_tags) {
    for (boost::property_tree::ptree::const_iterator it = node.begin(); it != node.end(); ++it) {
      std::string key = it->first;
      if (key == std::string("account_tags")) {
        auto account_tags_node = it->second;

        for (auto it2 = account_tags_node.begin(); it2 != account_tags_node.end(); ++it2) {
          auto account_tag = std::make_shared<PyMoneroAccountTag>();
          from_property_tree(it2->second, account_tag);
          account_tags.push_back(account_tag);
        }
      }
    }
  }
};

class PyMoneroTransfer : public monero_transfer {
public:
  using monero_transfer::monero_transfer;

  boost::optional<bool> is_incoming() const override {
    PYBIND11_OVERRIDE_PURE(
      boost::optional<bool>,
      monero_transfer,
      is_incoming
    );
  }
};

class PyMoneroSubaddress : public monero::monero_subaddress {
public:

  static void from_rpc_property_tree(const boost::property_tree::ptree& node, const std::shared_ptr<monero::monero_subaddress>& subaddress) {
    for (boost::property_tree::ptree::const_iterator it = node.begin(); it != node.end(); ++it) {
      std::string key = it->first;
      if (key == std::string("account_index")) subaddress->m_account_index = it->second.get_value<uint32_t>();
      else if (key == std::string("address_index")) subaddress->m_index = it->second.get_value<uint32_t>();
      else if (key == std::string("address")) subaddress->m_address = it->second.data();
      else if (key == std::string("balance")) subaddress->m_balance = it->second.get_value<uint64_t>();
      else if (key == std::string("unlocked_balance")) subaddress->m_unlocked_balance = it->second.get_value<uint64_t>();
      else if (key == std::string("label")) subaddress->m_label = it->second.data();
      else if (key == std::string("used")) subaddress->m_is_used = it->second.get_value<bool>();
      else if (key == std::string("num_unspent_outputs")) subaddress->m_num_unspent_outputs = it->second.get_value<uint64_t>();
      else if (key == std::string("blocks_to_unlock")) subaddress->m_num_blocks_to_unlock = it->second.get_value<uint64_t>();
    }
  }

  static void from_rpc_property_tree(const boost::property_tree::ptree& node, std::vector<std::shared_ptr<monero::monero_subaddress>>& subaddresses) {
    for (boost::property_tree::ptree::const_iterator it = node.begin(); it != node.end(); ++it) {
      std::string key = it->first;
      if (key == std::string("per_subaddress")) {
        auto per_subaddress_node = it->second;

        for (auto it2 = per_subaddress_node.begin(); it2 != per_subaddress_node.end(); ++it2) {
          auto sub = std::make_shared<monero::monero_subaddress>();
          from_property_tree(it2->second, sub);
          subaddresses.push_back(sub);
        }
      }
    }
  }

  static void from_property_tree(const boost::property_tree::ptree& node, const std::shared_ptr<monero::monero_subaddress>& subaddress) {
    for (boost::property_tree::ptree::const_iterator it = node.begin(); it != node.end(); ++it) {
      std::string key = it->first;
      if (key == std::string("major")) subaddress->m_account_index = it->second.get_value<uint32_t>();
      else if (key == std::string("minor")) subaddress->m_index = it->second.get_value<uint32_t>();
      else if (key == std::string("index")) {
        auto node2 = it->second;
        from_property_tree(node2, subaddress);
      }
    }
  }
};

class PyMoneroIntegratedAddress : public monero::monero_integrated_address {
public:
  static void from_property_tree(const boost::property_tree::ptree& node, const std::shared_ptr<monero::monero_integrated_address>& subaddress) {
    for (boost::property_tree::ptree::const_iterator it = node.begin(); it != node.end(); ++it) {
      std::string key = it->first;
      if (key == std::string("integrated_address")) subaddress->m_integrated_address = it->second.data();
      else if (key == std::string("standard_address")) subaddress->m_standard_address = it->second.data();
      else if (key == std::string("payment_id")) subaddress->m_payment_id = it->second.data();
    }
  }
};

class PyMoneroAccount : public monero::monero_account {
public:

  static void from_property_tree(const boost::property_tree::ptree& node, const std::shared_ptr<monero::monero_account>& account) {
    for (boost::property_tree::ptree::const_iterator it = node.begin(); it != node.end(); ++it) {
      std::string key = it->first;
      if (key == std::string("account_index")) account->m_index = it->second.get_value<uint32_t>();
      else if (key == std::string("balance")) account->m_balance = it->second.get_value<uint64_t>();
      else if (key == std::string("unlocked_balance")) account->m_unlocked_balance = it->second.get_value<uint64_t>();
      else if (key == std::string("base_address")) account->m_primary_address = it->second.data();
      else if (key == std::string("tag")) account->m_tag = it->second.data();
      else if (key == std::string("label")) {
        // label belongs to first subaddress
      }
    }
    if (account->m_tag != boost::none && account->m_tag->empty()) account->m_tag = boost::none;
  }

  static void from_property_tree(const boost::property_tree::ptree& node, std::vector<std::shared_ptr<monero::monero_account>>& accounts) {    
    for (boost::property_tree::ptree::const_iterator it = node.begin(); it != node.end(); ++it) {
      std::string key = it->first;
      if (key == std::string("subaddress_accounts")) {
        auto accounts_node = it->second;

        for (auto it2 = accounts_node.begin(); it2 != accounts_node.end(); ++it2) {
          auto account = std::make_shared<monero::monero_account>();
          from_property_tree(it2->second, account);
          accounts.push_back(account);
        }
      }
    }
  }

  static void from_property_tree(const boost::property_tree::ptree& node, std::vector<monero::monero_account>& accounts) {    
    std::vector<std::shared_ptr<monero::monero_account>> accounts_ptr;
    from_property_tree(node, accounts_ptr);

    for (const auto &account : accounts_ptr) {
      accounts.push_back(*account);
    }
  }

};

class PyMoneroWalletGetHeightResponse {
public:
  static uint64_t from_property_tree(const boost::property_tree::ptree& node) {
    for (boost::property_tree::ptree::const_iterator it = node.begin(); it != node.end(); ++it) {
      std::string key = it->first;
      if (key == std::string("height")) return it->second.get_value<uint64_t>();
    }
    throw std::runtime_error("Invalid get_height response");
  }
};

class PyMoneroQueryKeyParams : public PyMoneroJsonRequestParams {
public:
  boost::optional<std::string> m_key_type;

  PyMoneroQueryKeyParams() { }
  PyMoneroQueryKeyParams(const std::string& key_type) {
    m_key_type = key_type;
  }

  rapidjson::Value to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const override { 
    rapidjson::Value root(rapidjson::kObjectType); 
    rapidjson::Value value_str(rapidjson::kStringType);
    if (m_key_type != boost::none) monero_utils::add_json_member("key_type", m_key_type.get(), allocator, root, value_str);
    return root; 
  }
};

class PyMoneroQueryOutputParams : public PyMoneroJsonRequestParams {
public:
  boost::optional<std::string> m_key_image;

  PyMoneroQueryOutputParams() { }
  PyMoneroQueryOutputParams(const std::string& key_image) {
    m_key_image = key_image;
  }

  rapidjson::Value to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const override { 
    rapidjson::Value root(rapidjson::kObjectType); 
    rapidjson::Value value_str(rapidjson::kStringType);
    if (m_key_image != boost::none) monero_utils::add_json_member("key_image", m_key_image.get(), allocator, root, value_str);
    return root; 
  }
};

class PyMoneroGetAddressIndexParams : public PyMoneroJsonRequestParams {
public:
  boost::optional<std::string> m_address;

  PyMoneroGetAddressIndexParams() { }
  PyMoneroGetAddressIndexParams(const std::string& address) {
    m_address = address;
  }

  rapidjson::Value to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const override { 
    rapidjson::Value root(rapidjson::kObjectType); 
    rapidjson::Value value_str(rapidjson::kStringType);
    if (m_address != boost::none) monero_utils::add_json_member("address", m_address.get(), allocator, root, value_str);
    return root; 
  }
};

class PyMoneroMakeIntegratedAddressParams : public PyMoneroJsonRequestParams {
public:
  boost::optional<std::string> m_standard_address;
  boost::optional<std::string> m_payment_id;

  PyMoneroMakeIntegratedAddressParams() { }
  PyMoneroMakeIntegratedAddressParams(const std::string& standard_address, const std::string& payment_id) {
    m_standard_address = standard_address;
    m_payment_id = payment_id;
  }

  rapidjson::Value to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const override { 
    rapidjson::Value root(rapidjson::kObjectType); 
    rapidjson::Value value_str(rapidjson::kStringType);
    if (m_standard_address != boost::none) monero_utils::add_json_member("standard_address", m_standard_address.get(), allocator, root, value_str);
    if (m_payment_id != boost::none) monero_utils::add_json_member("payment_id", m_payment_id.get(), allocator, root, value_str);
    return root; 
  }
};

class PyMoneroSplitIntegratedAddressParams : public PyMoneroJsonRequestParams {
public:
  boost::optional<std::string> m_integrated_address;

  PyMoneroSplitIntegratedAddressParams() { }
  PyMoneroSplitIntegratedAddressParams(const std::string& integrated_address) {
    m_integrated_address = integrated_address;
  }

  rapidjson::Value to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const override { 
    rapidjson::Value root(rapidjson::kObjectType); 
    rapidjson::Value value_str(rapidjson::kStringType);
    if (m_integrated_address != boost::none) monero_utils::add_json_member("integrated_address", m_integrated_address.get(), allocator, root, value_str);
    return root; 
  }
};

class PyMoneroWalletStartMiningParams : public PyMoneroJsonRequestParams {
public:
  boost::optional<int> m_num_threads;
  boost::optional<bool> m_is_background;
  boost::optional<bool> m_ignore_battery;

  PyMoneroWalletStartMiningParams() { }

  PyMoneroWalletStartMiningParams(int num_threads, bool is_background, bool ignore_battery) {
    m_num_threads = num_threads;
    m_is_background = is_background;
    m_ignore_battery = ignore_battery;
  }

  rapidjson::Value to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const override { 
    rapidjson::Value root(rapidjson::kObjectType); 
    rapidjson::Value value_str(rapidjson::kStringType);
    rapidjson::Value value_num(rapidjson::kNumberType);
    if (m_num_threads != boost::none) monero_utils::add_json_member("threads_count", m_num_threads.get(), allocator, root, value_num);
    if (m_is_background != boost::none) monero_utils::add_json_member("do_background_mining", m_is_background.get(), allocator, root);
    if (m_ignore_battery != boost::none) monero_utils::add_json_member("ignore_battery", m_ignore_battery.get(), allocator, root);
    return root;
  };
};

class PyMoneroPrepareMultisigParams : public PyMoneroJsonRequestParams {
public:
  // TODO monero-docs document this parameter
  boost::optional<bool> m_enable_multisig_experimental;
  PyMoneroPrepareMultisigParams(bool enable_multisig_experimental = true) {
    m_enable_multisig_experimental = enable_multisig_experimental;
  }

  rapidjson::Value to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const override { 
    rapidjson::Value root(rapidjson::kObjectType); 
    if (m_enable_multisig_experimental != boost::none) monero_utils::add_json_member("enable_multisig_experimental", m_enable_multisig_experimental.get(), allocator, root);
    return root; 
  }
};

class PyMoneroExportMultisigHexResponse {
public:
  static std::string from_property_tree(const boost::property_tree::ptree& node) {
    for (boost::property_tree::ptree::const_iterator it = node.begin(); it != node.end(); ++it) {
      std::string key = it->first;
      if (key == std::string("info")) return it->second.data();
    }
    throw std::runtime_error("Invalid prepare multisig response");
  }
};

class PyMoneroImportMultisigHexParams : public PyMoneroJsonRequestParams {
public:
  std::vector<std::string> m_multisig_hexes;

  PyMoneroImportMultisigHexParams() {}

  PyMoneroImportMultisigHexParams(const std::vector<std::string>& multisig_hexes) {
    m_multisig_hexes = multisig_hexes;
  }

  rapidjson::Value to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const override { 
    rapidjson::Value root(rapidjson::kObjectType); 
    if (!m_multisig_hexes.empty()) root.AddMember("info", monero_utils::to_rapidjson_val(allocator, m_multisig_hexes), allocator);
    return root;
  }
};

class PyMoneroImportMultisigHexResponse {
public:
  static int from_property_tree(const boost::property_tree::ptree& node) {
    for (boost::property_tree::ptree::const_iterator it = node.begin(); it != node.end(); ++it) {
      std::string key = it->first;
      if (key == std::string("n_outputs")) return it->second.get_value<int>();
    }
    throw std::runtime_error("Invalid prepare multisig response");
  }
};

class PyMoneroSubmitMultisigTxHexResponse {
public:
  PyMoneroSubmitMultisigTxHexResponse() {}
  static std::vector<std::string> from_property_tree(const boost::property_tree::ptree& node) {
    for (boost::property_tree::ptree::const_iterator it = node.begin(); it != node.end(); ++it) {
      std::string key = it->first;
      if (key == std::string("tx_hash_list")) {
        auto node2 = it->second;
        std::vector<std::string> hashes;
        for (auto it2 = node2.begin(); it2 != node2.end(); ++it2) {
          hashes.push_back(it2->second.data());
        }

        return hashes;
      }
    }
    throw std::runtime_error("Invalid prepare multisig response");
  }
};

class PyMoneroMakeMultisigParams : public PyMoneroJsonRequestParams {
public:
  std::vector<std::string> m_multisig_info;
  boost::optional<int> m_threshold;
  boost::optional<std::string> m_password;

  PyMoneroMakeMultisigParams(const std::vector<std::string>& multisig_hexes, int threshold, const std::string& password) {
    m_multisig_info = multisig_hexes;
    m_threshold = threshold;
    m_password = password;
  }

  rapidjson::Value to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const override { 
    rapidjson::Value root(rapidjson::kObjectType);
    rapidjson::Value val_num(rapidjson::kNumberType);
    rapidjson::Value val_str(rapidjson::kStringType);
    if (!m_multisig_info.empty()) root.AddMember("multisig_info", monero_utils::to_rapidjson_val(allocator, m_multisig_info), allocator);
    if (m_threshold != boost::none) monero_utils::add_json_member("threshold", m_threshold.get(), allocator, root, val_num);
    if (m_password != boost::none) monero_utils::add_json_member("password", m_password.get(), allocator, root, val_str);
    return root; 
  }
};
  
class PyMoneroPrepareMakeMultisigResponse {
public:
  static std::string from_property_tree(const boost::property_tree::ptree& node) {
    for (boost::property_tree::ptree::const_iterator it = node.begin(); it != node.end(); ++it) {
      std::string key = it->first;
      if (key == std::string("multisig_info")) return it->second.data();
    }
    throw std::runtime_error("Invalid prepare multisig response");
  }
};

class PyMoneroExchangeMultisigKeysParams : public PyMoneroJsonRequestParams {
public:
  std::vector<std::string> m_multisig_info;
  boost::optional<std::string> m_password;

  PyMoneroExchangeMultisigKeysParams() {}
  PyMoneroExchangeMultisigKeysParams(const std::vector<std::string>& multisig_hexes, const std::string& password) {
    m_multisig_info = multisig_hexes;
    m_password = password;
  }

  rapidjson::Value to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const override { 
    rapidjson::Value root(rapidjson::kObjectType);
    rapidjson::Value val_num(rapidjson::kNumberType);
    rapidjson::Value val_str(rapidjson::kStringType);
    if (!m_multisig_info.empty()) root.AddMember("multisig_info", monero_utils::to_rapidjson_val(allocator, m_multisig_info), allocator);
    if (m_password != boost::none) monero_utils::add_json_member("password", m_password.get(), allocator, root, val_str);
    return root; 
  }
};

class PyMoneroParsePaymentUriParams : public PyMoneroJsonRequestParams {
public:
  boost::optional<std::string> m_uri;

  PyMoneroParsePaymentUriParams() {}
  PyMoneroParsePaymentUriParams(const std::string& uri) {
    m_uri = uri;
  }

  rapidjson::Value to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const override { 
    rapidjson::Value root(rapidjson::kObjectType);
    rapidjson::Value val_str(rapidjson::kStringType);
    if (m_uri != boost::none) monero_utils::add_json_member("uri", m_uri.get(), allocator, root, val_str);
    return root;
  }
};

class PyMoneroParsePaymentUriResponse {
public:
  boost::optional<std::string> m_address;
  boost::optional<uint64_t> m_amount;
  boost::optional<std::string> m_payment_id;
  boost::optional<std::string> m_recipient_name;
  boost::optional<std::string> m_tx_description;

  PyMoneroParsePaymentUriResponse() {}

  std::shared_ptr<monero::monero_tx_config> to_tx_config() const {
    auto tx_config = std::make_shared<monero::monero_tx_config>();
    tx_config->m_payment_id = m_payment_id;
    tx_config->m_recipient_name = m_recipient_name;
    tx_config->m_note = m_tx_description;
    tx_config->m_amount = m_amount;
    tx_config->m_address = m_address;
    return tx_config;
  }
  
  static void from_property_tree(const boost::property_tree::ptree& node, const std::shared_ptr<PyMoneroParsePaymentUriResponse>& response) {
    for (boost::property_tree::ptree::const_iterator it = node.begin(); it != node.end(); ++it) {
      std::string key = it->first;
      if (key == std::string("address")) response->m_address = it->second.data();
      else if (key == std::string("amount")) response->m_amount = it->second.get_value<uint64_t>();
      else if (key == std::string("payment_id")) response->m_payment_id = it->second.data();
      else if (key == std::string("recipient_name")) response->m_recipient_name = it->second.data();
      else if (key == std::string("tx_description")) response->m_tx_description = it->second.data();
    }
  }
};

class PyMoneroGetPaymentUriParams : public PyMoneroJsonRequestParams {
public:
  boost::optional<std::string> m_address;
  boost::optional<uint64_t> m_amount;
  boost::optional<std::string> m_recipient_name;
  boost::optional<std::string> m_tx_description;

  PyMoneroGetPaymentUriParams() {}
  PyMoneroGetPaymentUriParams(const monero_tx_config & config) {
    m_address = config.m_address;
    m_amount = config.m_amount;
    m_recipient_name = config.m_recipient_name;
    m_tx_description = config.m_note;
  }

  rapidjson::Value to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const override { 
    rapidjson::Value root(rapidjson::kObjectType); 
    rapidjson::Value value_str(rapidjson::kStringType);
    rapidjson::Value value_num(rapidjson::kNumberType);
    if (m_address != boost::none) monero_utils::add_json_member("address", m_address.get(), allocator, root, value_str);
    if (m_amount != boost::none) monero_utils::add_json_member("amount", m_amount.get(), allocator, root, value_num);
    if (m_recipient_name != boost::none) monero_utils::add_json_member("recipient_name", m_recipient_name.get(), allocator, root, value_str);
    if (m_tx_description != boost::none) monero_utils::add_json_member("tx_description", m_tx_description.get(), allocator, root, value_str);
    return root; 
  }
};

class PyMoneroGetPaymentUriResponse {
public:
  static std::string from_property_tree(const boost::property_tree::ptree& node) {
    for (boost::property_tree::ptree::const_iterator it = node.begin(); it != node.end(); ++it) {
      std::string key = it->first;
      if (key == std::string("uri")) return it->second.data();
    }
    throw std::runtime_error("Invalid make uri response");
  }
};

class PyMoneroGetBalanceParams : public PyMoneroJsonRequestParams {
public:
  boost::optional<uint32_t> m_account_idx;
  std::vector<uint32_t> m_address_indices;
  boost::optional<bool> m_all_accounts;
  boost::optional<bool> m_strict;

  PyMoneroGetBalanceParams() {};
  PyMoneroGetBalanceParams(bool all_accounts, bool strict = false) {
    m_all_accounts = all_accounts;
    m_strict = strict;
  };

  PyMoneroGetBalanceParams(uint32_t account_idx, const std::vector<uint32_t>& address_indices, bool all_accounts = false, bool strict = false) {
    m_account_idx = account_idx;
    m_address_indices = address_indices;
    m_all_accounts = all_accounts;
    m_strict = strict;
  }
  PyMoneroGetBalanceParams(uint32_t account_idx, boost::optional<uint32_t> address_idx, bool all_accounts = false, bool strict = false) {
    m_account_idx = account_idx;
    if (address_idx != boost::none) m_address_indices.push_back(address_idx.get());
    m_all_accounts = all_accounts;
    m_strict = strict;
  }

  rapidjson::Value to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const override { 
    rapidjson::Value root(rapidjson::kObjectType); 
    rapidjson::Value value_num(rapidjson::kNumberType);
    if (m_account_idx != boost::none) monero_utils::add_json_member("account_index", m_account_idx.get(), allocator, root, value_num);
    if (!m_address_indices.empty()) root.AddMember("address_indices", monero_utils::to_rapidjson_val(allocator, m_address_indices), allocator);
    if (m_all_accounts != boost::none) monero_utils::add_json_member("all_accounts", m_all_accounts.get(), allocator, root);
    if (m_strict != boost::none) monero_utils::add_json_member("strict", m_strict.get(), allocator, root);
    return root; 
  }
};

class PyMoneroGetBalanceResponse {
public:
  boost::optional<uint64_t> m_balance;
  boost::optional<uint64_t> m_unlocked_balance;
  boost::optional<bool> m_multisig_import_needed;
  boost::optional<uint64_t> m_time_to_unlock;
  boost::optional<uint64_t> m_blocks_to_unlock;
  std::vector<std::shared_ptr<monero::monero_subaddress>> m_per_subaddress;

  PyMoneroGetBalanceResponse() {
    m_balance = 0;
    m_unlocked_balance = 0;
  }

  PyMoneroGetBalanceResponse(uint64_t balance, uint64_t unlocked_balance, bool multisig_import_needed, uint64_t time_to_unlock, uint64_t blocks_to_unlock) {
    m_balance = balance;
    m_unlocked_balance = unlocked_balance;
    m_multisig_import_needed = multisig_import_needed;
    m_time_to_unlock = time_to_unlock;
    m_blocks_to_unlock = blocks_to_unlock;
  }

  static void from_property_tree(const boost::property_tree::ptree& node, const std::shared_ptr<PyMoneroGetBalanceResponse>& response) {
    for (boost::property_tree::ptree::const_iterator it = node.begin(); it != node.end(); ++it) {
      std::string key = it->first;
      if (key == std::string("balance")) response->m_balance = it->second.get_value<uint64_t>();
      else if (key == std::string("unlocked_balance")) response->m_unlocked_balance = it->second.get_value<uint64_t>();
      else if (key == std::string("multisig_import_needed")) response->m_multisig_import_needed = it->second.get_value<bool>();
      else if (key == std::string("time_to_unlock")) response->m_time_to_unlock = it->second.get_value<uint64_t>();
      else if (key == std::string("blocks_to_unlock")) response->m_blocks_to_unlock = it->second.get_value<uint64_t>();
      else if (key == std::string("per_subaddress")) {
        auto node2 = it->second;

        for (auto it2 = node2.begin(); it2 != node2.end(); ++it2) {
          auto sub = std::make_shared<monero::monero_subaddress>();
          PyMoneroSubaddress::from_rpc_property_tree(it2->second, sub);
          response->m_per_subaddress.push_back(sub);
        }
      }
    }
  }
};

class PyMoneroCreateAccountParams : public PyMoneroJsonRequestParams {
public:
  boost::optional<std::string> m_tag;

  PyMoneroCreateAccountParams(const std::string& tag = "") {
    m_tag = tag;
  }

  rapidjson::Value to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const override { 
    rapidjson::Value root(rapidjson::kObjectType);
    rapidjson::Value value_str(rapidjson::kStringType);
    if (m_tag != boost::none) monero_utils::add_json_member("tag", m_tag.get(), allocator, root, value_str);
    return root; 
  }
};

class PyMoneroCloseWalletParams : public PyMoneroJsonRequestParams {
public:
  boost::optional<bool> m_save;

  PyMoneroCloseWalletParams(bool save = true) {
    m_save = save;
  };

  rapidjson::Value to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const override { 
    rapidjson::Value root(rapidjson::kObjectType); 
    if (m_save != boost::none) monero_utils::add_json_member("save", m_save.get(), allocator, root);
    return root; 
  }
};

class PyMoneroChangeWalletPasswordParams : public PyMoneroJsonRequestParams {
public:
  boost::optional<std::string> m_old_password;
  boost::optional<std::string> m_new_password;

  PyMoneroChangeWalletPasswordParams(const std::string& old_password, const std::string& new_password) {
    m_old_password = old_password;
    m_new_password = new_password;
  }

  rapidjson::Value to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const override { 
    rapidjson::Value root(rapidjson::kObjectType); 
    rapidjson::Value value_str(rapidjson::kStringType);
    if (m_old_password != boost::none) monero_utils::add_json_member("old_password", m_old_password.get(), allocator, root, value_str);
    if (m_new_password != boost::none) monero_utils::add_json_member("new_password", m_new_password.get(), allocator, root, value_str);
    return root; 
  }
};

class PyMoneroWalletAttributeParams : public PyMoneroJsonRequestParams {
public:
  boost::optional<std::string> m_key;
  boost::optional<std::string> m_value;

  PyMoneroWalletAttributeParams(const std::string& key, const std::string& value) {
    m_key = key;
    m_value = value;
  }

  PyMoneroWalletAttributeParams(const std::string& key) {
    m_key = key;
  }

  rapidjson::Value to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const override { 
    rapidjson::Value root(rapidjson::kObjectType); 
    rapidjson::Value value_str(rapidjson::kStringType);
    if (m_key != boost::none) monero_utils::add_json_member("key", m_key.get(), allocator, root, value_str);
    if (m_value != boost::none) monero_utils::add_json_member("value", m_value.get(), allocator, root, value_str);
    return root; 
  }

  static void from_property_tree(const boost::property_tree::ptree& node, const std::shared_ptr<PyMoneroWalletAttributeParams>& attributes) {
    for (boost::property_tree::ptree::const_iterator it = node.begin(); it != node.end(); ++it) {
      std::string key = it->first;
      if (key == std::string("key")) attributes->m_key = it->second.data();
      else if (key == std::string("value")) attributes->m_value = it->second.data();
    }
  }
};

class PyMoneroScanTxParams : public PyMoneroJsonRequestParams {
public:
  std::vector<std::string> m_tx_hashes;

  PyMoneroScanTxParams() {}
  PyMoneroScanTxParams(const std::vector<std::string>& tx_hashes) {
    m_tx_hashes = tx_hashes;
  }

  rapidjson::Value to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const override { 
    rapidjson::Value root(rapidjson::kObjectType); 
    if (!m_tx_hashes.empty()) root.AddMember("txids", monero_utils::to_rapidjson_val(allocator, m_tx_hashes), allocator);
    return root; 
  }
};

class PyMoneroSetDaemonParams : public PyMoneroJsonRequestParams {
public:
  boost::optional<std::string> m_address;
  boost::optional<std::string> m_username;
  boost::optional<std::string> m_password;
  boost::optional<bool> m_trusted;
  boost::optional<std::string> m_ssl_support;
  boost::optional<std::string> m_ssl_private_key_path;
  boost::optional<std::string> m_ssl_certificate_path;
  boost::optional<std::string> m_ssl_ca_file;
  std::vector<std::string> m_ssl_allowed_fingerprints;
  boost::optional<bool> m_ssl_allow_any_cert;

  rapidjson::Value to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const override { 
    rapidjson::Value root(rapidjson::kObjectType); 
    rapidjson::Value value_str(rapidjson::kStringType);
    if (m_address != boost::none) monero_utils::add_json_member("address", m_address.get(), allocator, root, value_str);
    if (m_username != boost::none) monero_utils::add_json_member("username", m_username.get(), allocator, root, value_str);
    if (m_password != boost::none) monero_utils::add_json_member("password", m_password.get(), allocator, root, value_str);
    if (m_trusted != boost::none) monero_utils::add_json_member("trusted", m_trusted.get(), allocator, root);
    if (m_ssl_support != boost::none) monero_utils::add_json_member("ssl_support", m_ssl_support.get(), allocator, root, value_str);
    if (m_ssl_private_key_path != boost::none) monero_utils::add_json_member("ssl_private_key_path", m_ssl_private_key_path.get(), allocator, root, value_str);
    if (m_ssl_certificate_path != boost::none) monero_utils::add_json_member("ssl_certificate_path", m_ssl_certificate_path.get(), allocator, root, value_str);
    if (m_ssl_ca_file != boost::none) monero_utils::add_json_member("ssl_ca_file", m_ssl_ca_file.get(), allocator, root, value_str);
    if (!m_ssl_allowed_fingerprints.empty()) root.AddMember("ssl_allowed_fingerprints", monero_utils::to_rapidjson_val(allocator, m_ssl_allowed_fingerprints), allocator);
    if (m_ssl_allow_any_cert != boost::none) monero_utils::add_json_member("ssl_allow_any_cert", m_ssl_allow_any_cert.get(), allocator, root);

    return root; 
  }
};

class PyMoneroAutoRefreshParams : public PyMoneroJsonRequestParams {
public:
  boost::optional<bool> m_enable;

  PyMoneroAutoRefreshParams(bool enable): m_enable(enable) { } 

  rapidjson::Value to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const override { 
    rapidjson::Value root(rapidjson::kObjectType); 
    if (m_enable != boost::none) monero_utils::add_json_member("enable", m_enable.get(), allocator, root);
    return root; 
  }
};

class PyMoneroSetAccountTagDescriptionParams : public PyMoneroJsonRequestParams {
public:
  boost::optional<std::string> m_tag;
  boost::optional<std::string> m_label;

  PyMoneroSetAccountTagDescriptionParams() {}
  PyMoneroSetAccountTagDescriptionParams(const std::string& tag, const std::string& label) {
    m_tag = tag;
    m_label = label;
  }

  rapidjson::Value to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const override { 
    rapidjson::Value root(rapidjson::kObjectType); 
    rapidjson::Value value_str(rapidjson::kStringType);
    if (m_tag != boost::none) monero_utils::add_json_member("tag", m_tag.get(), allocator, root, value_str);
    if (m_label != boost::none) monero_utils::add_json_member("label", m_label.get(), allocator, root, value_str);
    return root; 
  }
};

class PyMoneroTagAccountsParams : public PyMoneroJsonRequestParams {
public:
  std::vector<uint32_t> m_account_indices;
  boost::optional<std::string> m_tag;

  PyMoneroTagAccountsParams() {}
  PyMoneroTagAccountsParams(const std::vector<uint32_t>& account_indices) {
    m_account_indices = account_indices;
  }
  PyMoneroTagAccountsParams(const std::string& tag, const std::vector<uint32_t>& account_indices) {
    m_account_indices = account_indices;
    m_tag = tag;
  }

  rapidjson::Value to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const override { 
    rapidjson::Value root(rapidjson::kObjectType);
    rapidjson::Value value_str(rapidjson::kStringType);
    if (m_tag != boost::none) monero_utils::add_json_member("tag", m_tag.get(), allocator, root, value_str);
    if (!m_account_indices.empty()) root.AddMember("accounts", monero_utils::to_rapidjson_val(allocator, m_account_indices), allocator);
    return root; 
  }
};

class PyMoneroTxNotesParams : public PyMoneroJsonRequestParams {
public:
  std::vector<std::string> m_tx_hashes;
  std::vector<std::string> m_notes;

  PyMoneroTxNotesParams(const std::vector<std::string>& tx_hashes) {
    m_tx_hashes = tx_hashes;
  }

  PyMoneroTxNotesParams(const std::vector<std::string>& tx_hashes, const std::vector<std::string>& notes) {
    m_tx_hashes = tx_hashes;
    m_notes = notes;
  }

  rapidjson::Value to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const override { 
    rapidjson::Value root(rapidjson::kObjectType); 
    if (!m_tx_hashes.empty()) root.AddMember("txids", monero_utils::to_rapidjson_val(allocator, m_tx_hashes), allocator);
    if (!m_notes.empty()) root.AddMember("notes", monero_utils::to_rapidjson_val(allocator, m_notes), allocator);
    return root; 
  }
};

class PyMoneroAddressBookEntryParams : public PyMoneroJsonRequestParams {
public:
  boost::optional<uint64_t> m_index;  // TODO: not boost::optional
  boost::optional<bool> m_set_address;
  boost::optional<std::string> m_address;
  boost::optional<bool> m_set_description;
  boost::optional<std::string> m_description;
  std::vector<uint64_t> m_entries;

  PyMoneroAddressBookEntryParams() {}
  PyMoneroAddressBookEntryParams(uint64_t index) {
    m_index = index;
  }
  PyMoneroAddressBookEntryParams(const std::vector<uint64_t>& entries) {
    m_entries = entries;
  }
  PyMoneroAddressBookEntryParams(uint64_t index, bool set_address, const std::string& address, bool set_description, const std::string& description) {
    m_index = index;
    m_set_address = set_address;
    m_address = address;
    m_set_description = set_description;
    m_description = description;
  }
  PyMoneroAddressBookEntryParams(const std::string& address, const std::string& description) {
    m_address = address;
    m_description = description;
  }

  rapidjson::Value to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const override { 
    rapidjson::Value root(rapidjson::kObjectType);
    rapidjson::Value value_str(rapidjson::kStringType);
    rapidjson::Value value_num(rapidjson::kNumberType);
    if (m_index != boost::none) monero_utils::add_json_member("index", m_index.get(), allocator, root, value_num);
    if (m_set_address != boost::none) monero_utils::add_json_member("set_address", m_set_address.get(), allocator, root);
    if (m_address != boost::none) monero_utils::add_json_member("address", m_address.get(), allocator, root, value_str);
    if (m_set_description != boost::none) monero_utils::add_json_member("set_description", m_set_description.get(), allocator, root);
    if (m_description != boost::none) monero_utils::add_json_member("description", m_description.get(), allocator, root, value_str);
    if (!m_entries.empty()) root.AddMember("entries", monero_utils::to_rapidjson_val(allocator, m_entries), allocator);
    return root; 
  }
};

class PyMoneroAddressBookEntry : public monero::monero_address_book_entry {
public:
  static void from_property_tree(const boost::property_tree::ptree& node, const std::shared_ptr<monero::monero_address_book_entry>& entry) {
    for (boost::property_tree::ptree::const_iterator it = node.begin(); it != node.end(); ++it) {
      std::string key = it->first;

      if (key == std::string("index")) entry->m_index = it->second.get_value<uint64_t>();
      else if (key == std::string("address")) entry->m_address = it->second.data();
      else if (key == std::string("description")) entry->m_description = it->second.data();
      else if (key == std::string("payment_id")) entry->m_payment_id = it->second.data();
    }
  }

  static void from_property_tree(const boost::property_tree::ptree& node, std::vector<std::shared_ptr<monero::monero_address_book_entry>>& entries) {
    for (boost::property_tree::ptree::const_iterator it = node.begin(); it != node.end(); ++it) {
      std::string key = it->first;
      if (key == std::string("entries")) {
        auto entries_node = it->second;

        for (auto it2 = entries_node.begin(); it2 != entries_node.end(); ++it2) {
          auto entry = std::make_shared<monero::monero_address_book_entry>();
          from_property_tree(it2->second, entry);
          entries.push_back(entry);
        }
      }
    }
  }
};

class PyMoneroWalletBalance {
public:
  uint64_t m_balance;
  uint64_t m_unlocked_balance;

  PyMoneroWalletBalance(uint64_t balance = 0, uint64_t unlocked_balance = 0) {
    m_balance = balance;
    m_unlocked_balance = unlocked_balance;
  }
};

class PyMoneroGetAccountsParams : public PyMoneroJsonRequestParams {
public:
  boost::optional<std::string> m_label;

  PyMoneroGetAccountsParams() {}
  PyMoneroGetAccountsParams(const std::string& label) {
    m_label = label;
  }

  rapidjson::Value to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const override { 
    rapidjson::Value root(rapidjson::kObjectType);
    rapidjson::Value value_str(rapidjson::kStringType);
    if (m_label != boost::none) monero_utils::add_json_member("label", m_label.get(), allocator, root, value_str);
    return root;
  }
};

class PyMoneroVerifySignMessageParams : public PyMoneroJsonRequestParams {
public:
  boost::optional<std::string> m_data;
  boost::optional<std::string> m_address;
  boost::optional<std::string> m_signature;
  boost::optional<monero::monero_message_signature_type> m_signature_type;

  boost::optional<uint32_t> m_account_index;
  boost::optional<uint32_t> m_address_index;


  PyMoneroVerifySignMessageParams() {}

  PyMoneroVerifySignMessageParams(const std::string &data, const std::string &address, const std::string& signature) {
    m_data = data;
    m_address = address;
    m_signature = signature;
  }

  PyMoneroVerifySignMessageParams(const std::string &data, monero::monero_message_signature_type signature_type, uint32_t account_index, uint32_t address_index) {
    m_data = data;
    m_signature_type = signature_type;
    m_account_index = account_index;
    m_address_index = address_index;
  }

  rapidjson::Value to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const override { 
    rapidjson::Value root(rapidjson::kObjectType);
    rapidjson::Value value_str(rapidjson::kStringType);
    rapidjson::Value value_num(rapidjson::kNumberType);
    if (m_data != boost::none) monero_utils::add_json_member("data", m_data.get(), allocator, root, value_str);
    if (m_address != boost::none) monero_utils::add_json_member("address", m_address.get(), allocator, root, value_str);
    if (m_signature != boost::none) monero_utils::add_json_member("signature", m_signature.get(), allocator, root, value_str);
    if (m_signature_type != boost::none) {
      if (m_signature_type == monero::monero_message_signature_type::SIGN_WITH_VIEW_KEY) {
        monero_utils::add_json_member("signature_type", std::string("view"), allocator, root, value_str);
      }
      else {
        monero_utils::add_json_member("signature_type", std::string("spend"), allocator, root, value_str);
      }
    }
    if (m_account_index != boost::none) monero_utils::add_json_member("account_index", m_account_index.get(), allocator, root, value_num);
    if (m_address_index != boost::none) monero_utils::add_json_member("address_index", m_address_index.get(), allocator, root, value_num);

    return root;
  }
};

class PyMoneroCheckTxKeyParams : public PyMoneroJsonRequestParams {
public:
  boost::optional<std::string> m_tx_hash;
  boost::optional<std::string> m_address;
  boost::optional<std::string> m_tx_key;

  PyMoneroCheckTxKeyParams() {}

  PyMoneroCheckTxKeyParams(const std::string &tx_hash) {
    m_tx_hash = tx_hash;
  }

  PyMoneroCheckTxKeyParams(const std::string &tx_hash, const std::string &tx_key, const std::string &address) {
    m_tx_hash = tx_hash;
    m_tx_key = tx_key;
    m_address = address;
  }

  rapidjson::Value to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const override { 
    rapidjson::Value root(rapidjson::kObjectType);
    rapidjson::Value value_str(rapidjson::kStringType);
    if (m_tx_hash != boost::none) monero_utils::add_json_member("txid", m_tx_hash.get(), allocator, root, value_str);
    if (m_address != boost::none) monero_utils::add_json_member("address", m_address.get(), allocator, root, value_str);
    if (m_tx_key != boost::none) monero_utils::add_json_member("tx_key", m_tx_key.get(), allocator, root, value_str);
    return root;
  }
};

class PyMoneroSignDescribeTransferParams : public PyMoneroJsonRequestParams {
public:
  boost::optional<std::string> m_unsigned_txset;
  boost::optional<std::string> m_multisig_txset;

  PyMoneroSignDescribeTransferParams() {}

  PyMoneroSignDescribeTransferParams(const std::string &unsigned_txset) {
    m_unsigned_txset = unsigned_txset;
  }

  PyMoneroSignDescribeTransferParams(const std::string &unsigned_txset, const std::string &multisig_txset) {
    m_unsigned_txset = unsigned_txset;
    m_multisig_txset = multisig_txset;
  }

  rapidjson::Value to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const override { 
    rapidjson::Value root(rapidjson::kObjectType);
    rapidjson::Value value_str(rapidjson::kStringType);
    if (m_unsigned_txset != boost::none) monero_utils::add_json_member("unsigned_txset", m_unsigned_txset.get(), allocator, root, value_str);
    if (m_multisig_txset != boost::none) monero_utils::add_json_member("multisig_txset", m_multisig_txset.get(), allocator, root, value_str);

    return root;
  }
};

class PyMoneroWalletRelayTxParams : public PyMoneroJsonRequestParams {
public:
  boost::optional<std::string> m_hex;

  PyMoneroWalletRelayTxParams() {}

  PyMoneroWalletRelayTxParams(const std::string &hex) {
    m_hex = hex;
  }

  rapidjson::Value to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const override { 
    rapidjson::Value root(rapidjson::kObjectType);
    rapidjson::Value value_str(rapidjson::kStringType);
    if (m_hex != boost::none) monero_utils::add_json_member("hex", m_hex.get(), allocator, root, value_str);
    return root;
  }
};

class PyMoneroSweepParams : public PyMoneroJsonRequestParams {
public:
  boost::optional<std::string> m_address;
  boost::optional<uint32_t> m_account_index;
  std::vector<uint32_t> m_subaddr_indices;
  boost::optional<std::string> m_key_image;
  boost::optional<bool> m_relay;
  boost::optional<monero_tx_priority> m_priority;
  boost::optional<std::string> m_payment_id;
  boost::optional<uint64_t> m_below_amount;
  boost::optional<bool> m_get_tx_key;
  boost::optional<bool> m_get_tx_hex;
  boost::optional<bool> m_get_tx_metadata;
  
  PyMoneroSweepParams(bool relay = false) {
    m_relay = relay;
  }

  PyMoneroSweepParams(const monero_tx_config& config) {
    m_address = config.m_address;
    m_account_index = config.m_account_index;
    m_subaddr_indices = config.m_subaddress_indices;
    m_key_image = config.m_key_image;
    m_relay = config.m_relay;
    m_priority = config.m_priority;
    m_payment_id = config.m_payment_id;
    m_below_amount = config.m_below_amount;
    m_get_tx_key = true;
    m_get_tx_hex = true;
    m_get_tx_metadata = true;
  }

  rapidjson::Value to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const override { 
    rapidjson::Value root(rapidjson::kObjectType);
    rapidjson::Value val_str(rapidjson::kStringType);
    rapidjson::Value val_num(rapidjson::kNumberType);

    if (m_address != boost::none) monero_utils::add_json_member("address", m_address.get(), allocator, root, val_str);
    if (m_account_index != boost::none) monero_utils::add_json_member("account_index", m_account_index.get(), allocator, root, val_num);
    if (m_subaddr_indices.size() > 0) root.AddMember("subaddr_indices", monero_utils::to_rapidjson_val(allocator, m_subaddr_indices), allocator);
    if (m_key_image != boost::none) monero_utils::add_json_member("key_image", m_key_image.get(), allocator, root, val_str);
    if (m_priority != boost::none) monero_utils::add_json_member("priority", m_priority.get(), allocator, root, val_num);
    if (m_payment_id != boost::none) monero_utils::add_json_member("payment_id", m_payment_id.get(), allocator, root, val_str);
    if (m_get_tx_key != boost::none) monero_utils::add_json_member("get_tx_key", m_get_tx_key.get(), allocator, root);
    if (m_get_tx_hex != boost::none) monero_utils::add_json_member("get_tx_hex", m_get_tx_hex.get(), allocator, root);
    if (m_get_tx_metadata != boost::none) monero_utils::add_json_member("get_tx_metadata", m_get_tx_metadata.get(), allocator, root);
    if (m_relay != boost::none) monero_utils::add_json_member("do_not_relay", !m_relay.get(), allocator, root);
    return root;
  }
};

class PyMoneroSubmitTransferParams : public PyMoneroJsonRequestParams {
public:
  boost::optional<std::string> m_signed_tx_hex;

  PyMoneroSubmitTransferParams() {}
  PyMoneroSubmitTransferParams(const std::string& signed_tx_hex) {
    m_signed_tx_hex = signed_tx_hex;
  }

  rapidjson::Value to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const override { 
    rapidjson::Value root(rapidjson::kObjectType);
    rapidjson::Value val_str(rapidjson::kStringType);
    if (m_signed_tx_hex != boost::none) monero_utils::add_json_member("tx_data_hex", m_signed_tx_hex.get(), allocator, root, val_str);
    return root;
  }
};

class PyMoneroCreateSubaddressParams : public PyMoneroJsonRequestParams {
public:
  boost::optional<std::string> m_label;
  boost::optional<uint32_t> m_account_index;
  boost::optional<uint32_t> m_subaddress_index;

  PyMoneroCreateSubaddressParams() {}
  PyMoneroCreateSubaddressParams(uint32_t account_idx, const std::string& label) {
    m_account_index = account_idx;
    m_label = label;
  }

  rapidjson::Value to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const override { 
    rapidjson::Value root(rapidjson::kObjectType);
    rapidjson::Value val_str(rapidjson::kStringType);
    rapidjson::Value val_num(rapidjson::kNumberType);
    if (m_label != boost::none) monero_utils::add_json_member("label", m_label.get(), allocator, root, val_str);
    if (m_account_index != boost::none) monero_utils::add_json_member("account_index", m_account_index.get(), allocator, root, val_num);
    return root;
  }
};

class PyMoneroSetSubaddressLabelParams : public PyMoneroJsonRequestParams {
public:
  boost::optional<std::string> m_label;
  boost::optional<uint32_t> m_account_index;
  boost::optional<uint32_t> m_subaddress_index;

  PyMoneroSetSubaddressLabelParams() {}
  PyMoneroSetSubaddressLabelParams(uint32_t account_idx, uint32_t subaddress_idx, const std::string& label) {
    m_account_index = account_idx;
    m_subaddress_index = subaddress_idx;
    m_label = label;
  }

  rapidjson::Value to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const override { 
    rapidjson::Value root(rapidjson::kObjectType);
    rapidjson::Value val_str(rapidjson::kStringType);
    rapidjson::Value val_num(rapidjson::kNumberType);
    if (m_label != boost::none) monero_utils::add_json_member("label", m_label.get(), allocator, root, val_str);
    if (m_account_index != boost::none && m_subaddress_index != boost::none) {
      rapidjson::Value index(rapidjson::kObjectType);
      monero_utils::add_json_member("major", m_account_index.get(), allocator, root, val_num);
      monero_utils::add_json_member("minor", m_subaddress_index.get(), allocator, root, val_num);
      root.AddMember("index", index, allocator);
    }
    return root;
  }
};

class PyMoneroImportExportOutputsParams : public PyMoneroJsonRequestParams {
public:
  boost::optional<std::string> m_outputs_hex;
  boost::optional<bool> m_all;

  PyMoneroImportExportOutputsParams() {}
  PyMoneroImportExportOutputsParams(bool all) {
    m_all = all;
  }
  PyMoneroImportExportOutputsParams(const std::string& outputs_hex) {
    m_outputs_hex = outputs_hex;
  }

  rapidjson::Value to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const override { 
    rapidjson::Value root(rapidjson::kObjectType);
    rapidjson::Value val_str(rapidjson::kStringType);
    if (m_all != boost::none) monero_utils::add_json_member("all", m_all.get(), allocator, root);
    if (m_outputs_hex != boost::none) monero_utils::add_json_member("outputs_data_hex", m_outputs_hex.get(), allocator, root, val_str);
    return root;
  }
};

class PyMoneroImportExportKeyImagesParams : public PyMoneroJsonRequestParams {
public:
  boost::optional<bool> m_all;
  std::vector<std::shared_ptr<PyMoneroKeyImage>> m_key_images;

  PyMoneroImportExportKeyImagesParams() {}
  PyMoneroImportExportKeyImagesParams(const std::vector<std::shared_ptr<monero::monero_key_image>> &key_images) {
    for(const auto &key_image : key_images) {
      m_key_images.push_back(std::make_shared<PyMoneroKeyImage>(*key_image));
    }
  }
  PyMoneroImportExportKeyImagesParams(const std::vector<std::shared_ptr<PyMoneroKeyImage>> &key_images) {
    m_key_images = key_images;
  }
  PyMoneroImportExportKeyImagesParams(bool all) {
    m_all = all;
  }

  rapidjson::Value to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const override { 
    rapidjson::Value root(rapidjson::kObjectType);
    rapidjson::Value val_str(rapidjson::kStringType);
    if (m_all != boost::none) monero_utils::add_json_member("all", m_all.get(), allocator, root);
    else if (m_key_images.size() > 0) {
      rapidjson::Value value_arr(rapidjson::kArrayType);

      for (const auto &key_image : m_key_images) {
        value_arr.PushBack(key_image->to_rapidjson_val(allocator), allocator);
      }
      root.AddMember("signed_key_images", value_arr, allocator);
      return root;
    }
    return root;
  }
};

class PyMoneroCreateOpenWalletParams : public PyMoneroJsonRequestParams {
public:
  boost::optional<std::string> m_filename;
  boost::optional<std::string> m_password;
  boost::optional<std::string> m_language;
  boost::optional<std::string> m_seed;
  boost::optional<std::string> m_seed_offset;
  boost::optional<uint64_t> m_restore_height;
  boost::optional<bool> m_autosave_current;
  boost::optional<bool> m_enable_multisig_experimental;
  boost::optional<std::string> m_address;
  boost::optional<std::string> m_view_key;
  boost::optional<std::string> m_spend_key;

  PyMoneroCreateOpenWalletParams() {}

  PyMoneroCreateOpenWalletParams(const std::string& filename, const std::string &password) {
    m_filename = filename;
    m_password = password;
  }

  PyMoneroCreateOpenWalletParams(const std::string& filename, const std::string &password, const std::string &language) {
    m_filename = filename;
    m_password = password;
    m_language = language;
  }

  PyMoneroCreateOpenWalletParams(const std::string& filename, const std::string &password, const std::string &seed, const std::string &seed_offset, uint64_t restore_height, const std::string &language, bool autosave_current, bool enable_multisig_experimental) {
    m_filename = filename;
    m_password = password;
    m_seed = seed;
    m_seed_offset = seed_offset;
    m_restore_height = restore_height;
    m_language = language;
    m_autosave_current = autosave_current;
    m_enable_multisig_experimental = enable_multisig_experimental;
  }

  PyMoneroCreateOpenWalletParams(const std::string& filename, const std::string &password, const std::string &address, const std::string &view_key, const std::string &spend_key, uint64_t restore_height, bool autosave_current) {
    m_filename = filename;
    m_password = password;
    m_address = address;
    m_view_key = view_key;
    m_spend_key = spend_key;
    m_restore_height = restore_height;
    m_autosave_current = autosave_current;
  }

  rapidjson::Value to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const override { 
    rapidjson::Value root(rapidjson::kObjectType);
    rapidjson::Value val_str(rapidjson::kStringType);
    rapidjson::Value val_num(rapidjson::kNumberType);
    if (m_filename != boost::none) monero_utils::add_json_member("filename", m_filename.get(), allocator, root, val_str);
    if (m_password != boost::none) monero_utils::add_json_member("password", m_password.get(), allocator, root, val_str);
    if (m_language != boost::none) monero_utils::add_json_member("language", m_language.get(), allocator, root, val_str);
    if (m_seed != boost::none) monero_utils::add_json_member("seed", m_seed.get(), allocator, root, val_str);
    if (m_seed_offset != boost::none) monero_utils::add_json_member("seed_offset", m_seed_offset.get(), allocator, root, val_str);
    if (m_restore_height != boost::none) monero_utils::add_json_member("restore_height", m_restore_height.get(), allocator, root, val_num);
    if (m_autosave_current != boost::none) monero_utils::add_json_member("autosave_current", m_autosave_current.get(), allocator, root);
    if (m_enable_multisig_experimental != boost::none) monero_utils::add_json_member("enable_multisig_experimental", m_enable_multisig_experimental.get(), allocator, root);
    if (m_address != boost::none) monero_utils::add_json_member("address", m_address.get(), allocator, root, val_str);
    if (m_view_key != boost::none && !m_view_key->empty()) monero_utils::add_json_member("viewkey", m_view_key.get(), allocator, root, val_str);
    if (m_spend_key != boost::none && !m_spend_key->empty()) monero_utils::add_json_member("spendkey", m_spend_key.get(), allocator, root, val_str);
    return root;
  }
};

class PyMoneroReserveProofParams : public PyMoneroJsonRequestParams {
public:
  boost::optional<bool> m_all;
  boost::optional<std::string> m_message;
  boost::optional<std::string> m_tx_hash;
  boost::optional<uint32_t> m_account_index;
  boost::optional<uint64_t> m_amount;
  boost::optional<std::string> m_address;
  boost::optional<std::string> m_signature;

  PyMoneroReserveProofParams() {}

  PyMoneroReserveProofParams(const std::string &message, bool all = true) {
    m_all = all;
    m_message = message;
  }

  PyMoneroReserveProofParams(const std::string &address, const std::string &message, const std::string &signature) {
    m_address = address;
    m_message = message;
    m_signature = signature;
  }

  PyMoneroReserveProofParams(const std::string &tx_hash, const std::string &address, const std::string &message, const std::string &signature) {
    m_tx_hash = tx_hash;
    m_address = address;
    m_message = message;
    m_signature = signature;
  }

  PyMoneroReserveProofParams(const std::string &tx_hash, const std::string &message) {
    m_tx_hash = tx_hash;
    m_message = message;
  }

  PyMoneroReserveProofParams(uint32_t account_index, uint64_t amount, const std::string &message) {
    m_account_index = account_index;
    m_amount = amount;
    m_message = message;
  }

  rapidjson::Value to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const override { 
    rapidjson::Value root(rapidjson::kObjectType);
    rapidjson::Value value_str(rapidjson::kStringType);
    rapidjson::Value value_num(rapidjson::kNumberType);
    if (m_all != boost::none) monero_utils::add_json_member("all", m_all.get(), allocator, root);
    if (m_message != boost::none) monero_utils::add_json_member("message", m_message.get(), allocator, root, value_str);
    if (m_tx_hash != boost::none) monero_utils::add_json_member("txid", m_tx_hash.get(), allocator, root, value_str);
    if (m_account_index != boost::none) monero_utils::add_json_member("account_index", m_account_index.get(), allocator, root, value_num);
    if (m_amount != boost::none) monero_utils::add_json_member("amount", m_amount.get(), allocator, root, value_num);
    if (m_address != boost::none) monero_utils::add_json_member("address", m_address.get(), allocator, root, value_str);
    if (m_signature != boost::none) monero_utils::add_json_member("signature", m_signature.get(), allocator, root, value_str);
    return root;
  }
};

class PyMoneroRefreshWalletParams : public PyMoneroJsonRequestParams {
public:
  boost::optional<bool> m_enable;
  boost::optional<uint64_t> m_period;
  boost::optional<uint64_t> m_start_height;

  PyMoneroRefreshWalletParams() {}

  PyMoneroRefreshWalletParams(bool enable, uint64_t period) {
    m_enable = enable;
    m_period = period;
  }

  PyMoneroRefreshWalletParams(uint64_t start_height) {
    m_start_height = start_height;
  }

  rapidjson::Value to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const override { 
    rapidjson::Value root(rapidjson::kObjectType);
    rapidjson::Value value_num(rapidjson::kNumberType);
    if (m_enable != boost::none) monero_utils::add_json_member("enable", m_enable.get(), allocator, root);
    if (m_period != boost::none) monero_utils::add_json_member("period", m_period.get(), allocator, root, value_num);
    if (m_start_height != boost::none) monero_utils::add_json_member("start_height", m_start_height.get(), allocator, root, value_num);
    return root;
  }
};

class PyMoneroTransferParams : public PyMoneroJsonRequestParams {
public:
  std::vector<uint32_t> m_subtract_fee_from_outputs;
  boost::optional<uint32_t> m_account_index;
  std::vector<uint32_t> m_subaddress_indices;
  boost::optional<std::string> m_payment_id;
  boost::optional<bool> m_do_not_relay;
  boost::optional<int> m_priority;
  boost::optional<bool> m_get_tx_hex;
  boost::optional<bool> m_get_tx_metadata;
  boost::optional<bool> m_get_tx_keys;
  boost::optional<bool> m_get_tx_key;

  std::vector<std::shared_ptr<monero::monero_destination>> m_destinations;

  PyMoneroTransferParams() {}
  PyMoneroTransferParams(const monero::monero_tx_config &config) {
    for (const auto sub_idx : config.m_subaddress_indices) {
      m_subaddress_indices.push_back(sub_idx);
    }
    
    for (const auto &dest : config.m_destinations) {
      if (dest->m_address == boost::none) throw std::runtime_error("Destination address is not defined");
      if (dest->m_amount == boost::none) throw std::runtime_error("Destination amount is not defined");

      m_destinations.push_back(dest);
    }

    m_subtract_fee_from_outputs = config.m_subtract_fee_from;
    m_account_index = config.m_account_index;
    m_payment_id = config.m_payment_id;
    if (config.m_relay == true) {
      m_do_not_relay = false;
    }
    else {
      m_do_not_relay = false;
    }
    if (config.m_priority == monero_tx_priority::DEFAULT) {
      m_priority = 0;
    }
    else if (config.m_priority == monero_tx_priority::UNIMPORTANT) {
      m_priority = 1;
    }
    else if (config.m_priority == monero_tx_priority::NORMAL) {
      m_priority = 2;
    }
    else if (config.m_priority == monero_tx_priority::ELEVATED) {
      m_priority = 3;
    }
    m_get_tx_hex = true;
    if (config.m_can_split) m_get_tx_keys = true;
    else m_get_tx_key = true;
  }

  rapidjson::Value to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const override { 
    rapidjson::Value root(rapidjson::kObjectType);
    rapidjson::Value value_num(rapidjson::kNumberType);
    rapidjson::Value value_str(rapidjson::kStringType);
    if (!m_subtract_fee_from_outputs.empty()) root.AddMember("subtract_fee_from_outputs", monero_utils::to_rapidjson_val(allocator, m_subtract_fee_from_outputs), allocator);
    if (m_account_index != boost::none) monero_utils::add_json_member("account_index", m_account_index.get(), allocator, root, value_num);
    if (!m_subaddress_indices.empty()) root.AddMember("subaddress_indices", monero_utils::to_rapidjson_val(allocator, m_subaddress_indices), allocator);
    if (m_payment_id != boost::none) monero_utils::add_json_member("payment_id", m_payment_id.get(), allocator, root, value_str);
    if (m_do_not_relay != boost::none) monero_utils::add_json_member("do_not_relay", m_do_not_relay.get(), allocator, root);
    if (m_priority != boost::none) monero_utils::add_json_member("priority", m_priority.get(), allocator, root, value_num);
    if (m_get_tx_hex != boost::none) monero_utils::add_json_member("get_tx_hex", m_get_tx_hex.get(), allocator, root);
    if (m_get_tx_metadata != boost::none) monero_utils::add_json_member("get_tx_metadata", m_get_tx_metadata.get(), allocator, root);
    if (m_get_tx_keys != boost::none) monero_utils::add_json_member("get_tx_keys", m_get_tx_keys.get(), allocator, root);
    if (m_get_tx_key != boost::none) monero_utils::add_json_member("get_tx_key", m_get_tx_key.get(), allocator, root);
    if (!m_destinations.empty()) {
      rapidjson::Value value_arr(rapidjson::kArrayType);

      for (const auto &dest : m_destinations) {
        value_arr.PushBack(dest->to_rapidjson_val(allocator), allocator);
      }

      root.AddMember("destinations", value_arr, allocator);
    }
    return root;
  }
};

class PyMoneroCheckReserve : public monero::monero_check_reserve {
public:

  static void from_property_tree(const boost::property_tree::ptree& node, const std::shared_ptr<monero::monero_check_reserve>& check) {
    for (boost::property_tree::ptree::const_iterator it = node.begin(); it != node.end(); ++it) {
      std::string key = it->first;
      if (key == std::string("good")) check->m_is_good = it->second.get_value<bool>();
      else if (key == std::string("total")) check->m_total_amount = it->second.get_value<uint64_t>();
      else if (key == std::string("spent")) check->m_unconfirmed_spent_amount = it->second.get_value<uint64_t>();
    }
  }
};

class PyMoneroCheckTxProof : public monero::monero_check_tx {
public:

  static void from_property_tree(const boost::property_tree::ptree& node, const std::shared_ptr<monero::monero_check_tx>& check) {
    for (boost::property_tree::ptree::const_iterator it = node.begin(); it != node.end(); ++it) {
      std::string key = it->first;
      if (key == std::string("good")) check->m_is_good = it->second.get_value<bool>();
      if (key == std::string("in_pool")) check->m_in_tx_pool = it->second.get_value<bool>();
      else if (key == std::string("confirmations")) check->m_num_confirmations = it->second.get_value<uint64_t>();
      else if (key == std::string("received")) check->m_received_amount = it->second.get_value<uint64_t>();
    }
  }
};

class PyMoneroReserveProofSignature {
public:

  static std::string from_property_tree(const boost::property_tree::ptree& node) {
    for (boost::property_tree::ptree::const_iterator it = node.begin(); it != node.end(); ++it) {
      std::string key = it->first;
      if (key == std::string("signature")) return it->second.data();
    }

    throw std::runtime_error("Invalid reserve proof response");
  }
};

class PyMoneroMessageSignatureResult : public monero::monero_message_signature_result {
public:
  static void from_property_tree(const boost::property_tree::ptree& node, const std::shared_ptr<monero::monero_message_signature_result> result) {
    for (boost::property_tree::ptree::const_iterator it = node.begin(); it != node.end(); ++it) {
      std::string key = it->first;
      if (key == std::string("good")) result->m_is_good = it->second.get_value<bool>();
      else if (key == std::string("old")) result->m_is_old = it->second.get_value<bool>();
      else if (key == std::string("signature_type")) {
        std::string sig_type = it->second.data();
        if (sig_type == std::string("view")) {
          result->m_signature_type = monero::monero_message_signature_type::SIGN_WITH_VIEW_KEY;
        }
        else {
          result->m_signature_type = monero::monero_message_signature_type::SIGN_WITH_SPEND_KEY;
        }
      }
      else if (key == std::string("version")) result->m_version = it->second.get_value<uint32_t>();
    }
  }
};

class PyMoneroWalletConnectionManagerListener : public PyMoneroConnectionManagerListener {
public:
  PyMoneroWalletConnectionManagerListener(monero::monero_wallet* wallet) {
    m_wallet = wallet;
  }

  void on_connection_changed(std::shared_ptr<PyMoneroRpcConnection> &connection) {
    if (m_wallet != nullptr) m_wallet->set_daemon_connection(*connection);
  }

private:
  monero::monero_wallet *m_wallet;
};

class PyMoneroWalletListener : public monero_wallet_listener {
public:
  
  void on_sync_progress(uint64_t height, uint64_t start_height, uint64_t end_height, double percent_done, const std::string& message) override {
    PYBIND11_OVERRIDE(
      void,                               
      monero_wallet_listener,
      on_sync_progress,
      height, start_height, end_height, percent_done, message
    );
  }
  
  void on_new_block(uint64_t height) override {
    PYBIND11_OVERRIDE(
      void,                               
      monero_wallet_listener,
      on_new_block,
      height
    );
  };
  
  void on_balances_changed(uint64_t new_balance, uint64_t new_unlocked_balance) override {
    PYBIND11_OVERRIDE(
      void,                               
      monero_wallet_listener,
      on_balances_changed,
      new_balance, new_unlocked_balance
    );
  };
  
  void on_output_received(const monero_output_wallet& output) override {
    PYBIND11_OVERRIDE(
      void,                               
      monero_wallet_listener,
      on_output_received,
      output
    );
  };

  void on_output_spent(const monero_output_wallet& output) override {
    PYBIND11_OVERRIDE(
      void,                               
      monero_wallet_listener,
      on_output_spent,
      output
    );
  };
};

PYBIND11_MAKE_OPAQUE(std::vector<std::string>);
PYBIND11_MAKE_OPAQUE(std::vector<std::shared_ptr<monero::monero_block>>);
PYBIND11_MAKE_OPAQUE(std::vector<std::shared_ptr<monero::monero_block_header>>);
PYBIND11_MAKE_OPAQUE(std::vector<std::shared_ptr<monero::monero_tx>>);
PYBIND11_MAKE_OPAQUE(std::vector<std::shared_ptr<monero::monero_tx_wallet>>);
PYBIND11_MAKE_OPAQUE(std::vector<std::shared_ptr<monero::monero_output>>);
PYBIND11_MAKE_OPAQUE(std::vector<std::shared_ptr<monero::monero_output_wallet>>);
PYBIND11_MAKE_OPAQUE(std::vector<std::shared_ptr<monero::monero_transfer>>);
PYBIND11_MAKE_OPAQUE(std::vector<std::shared_ptr<monero::monero_incoming_transfer>>);
PYBIND11_MAKE_OPAQUE(std::vector<std::shared_ptr<monero::monero_outgoing_transfer>>);
PYBIND11_MAKE_OPAQUE(std::vector<monero::monero_subaddress>);
PYBIND11_MAKE_OPAQUE(std::vector<std::shared_ptr<monero_destination>>);

class PyMoneroWallet : public monero::monero_wallet {
public:
  using monero::monero_wallet::monero_wallet;

  virtual void tag_accounts(const std::string& tag, const std::vector<uint32_t>& account_indices) {
    PYBIND11_OVERRIDE_PURE(
      void,
      PyMoneroWallet,
      tag_accounts,
    );
  }

  virtual void untag_accounts(const std::vector<uint32_t>& account_indices) {
    PYBIND11_OVERRIDE_PURE(
      void,
      PyMoneroWallet,
      untag_accounts,
    );
  }

  virtual std::vector<std::shared_ptr<PyMoneroAccountTag>> get_account_tags() {
    PYBIND11_OVERRIDE_PURE(
      std::vector<std::shared_ptr<PyMoneroAccountTag>>,
      PyMoneroWallet,
      get_account_tags,
    );
  }

  virtual void set_account_tag_label(const std::string& tag, const std::string& label) {
    PYBIND11_OVERRIDE_PURE(
      void,
      PyMoneroWallet,
      set_account_tag_label,
    );
  }

  bool is_view_only() const override {
    PYBIND11_OVERRIDE(
      bool,                               
      monero_wallet,
      is_view_only
    );
  }

  void set_daemon_connection(const std::string& uri, const std::string& username = "", const std::string& password = "") override {
    PYBIND11_OVERRIDE(
      void,                               
      monero_wallet,
      set_daemon_connection,
      uri, username, password
    );
  }

  void set_daemon_connection(const boost::optional<monero_rpc_connection>& connection) override {
    PYBIND11_OVERRIDE(
      void,                               
      monero_wallet,
      set_daemon_connection,
      connection
    );
  }

  void set_daemon_proxy(const std::string& uri = "") override {
    PYBIND11_OVERRIDE(
      void,                               
      monero_wallet,
      set_daemon_proxy,
      uri
    );
  }

  boost::optional<monero_rpc_connection> get_daemon_connection() const override {
    PYBIND11_OVERRIDE(
      boost::optional<monero_rpc_connection>,                               
      monero_wallet,
      get_daemon_connection
    );
  }

  bool is_connected_to_daemon() const override {
    PYBIND11_OVERRIDE(
      bool,                               
      monero_wallet,
      is_connected_to_daemon
    );
  }

  bool is_daemon_synced() const override {
    PYBIND11_OVERRIDE(
      bool,                               
      monero_wallet,
      is_daemon_synced
    );
  }

  bool is_daemon_trusted() const override {
    PYBIND11_OVERRIDE(
      bool,                               
      monero_wallet,
      is_daemon_trusted
    );
  }

  bool is_synced() const override {
    PYBIND11_OVERRIDE(
      bool,                               
      monero_wallet,
      is_synced
    );
  }

  monero_version get_version() const override {
    PYBIND11_OVERRIDE(
      monero_version,                               
      monero_wallet,
      get_version
    );
  }

  monero_network_type get_network_type() const override {
    PYBIND11_OVERRIDE(
      monero_network_type,                               
      monero_wallet,
      get_network_type
    );
  }

  std::string get_seed() const override {
    PYBIND11_OVERRIDE(
      std::string,                               
      monero_wallet,
      get_seed
    );
  }

  std::string get_seed_language() const override {
    PYBIND11_OVERRIDE(
      std::string,                               
      monero_wallet,
      get_seed_language
    );
  }

  std::string get_public_view_key() const override {
    PYBIND11_OVERRIDE(
      std::string,                               
      monero_wallet,
      get_public_view_key
    );
  }

  std::string get_private_view_key() const override {
    PYBIND11_OVERRIDE(
      std::string,                               
      monero_wallet,
      get_private_view_key
    );
  }

  std::string get_public_spend_key() const override {
    PYBIND11_OVERRIDE(
      std::string,                               
      monero_wallet,
      get_public_spend_key
    );
  }

  std::string get_private_spend_key() const override {
    PYBIND11_OVERRIDE(
      std::string,                               
      monero_wallet,
      get_private_spend_key
    );
  }

  std::string get_primary_address() const override {
    PYBIND11_OVERRIDE(
      std::string,                               
      monero_wallet,
      get_primary_address
    );
  }

  std::string get_address(const uint32_t account_idx, const uint32_t subaddress_idx) const override {
    PYBIND11_OVERRIDE(
      std::string,                               
      monero_wallet,
      get_address,
      account_idx, subaddress_idx
    );
  }

  monero_subaddress get_address_index(const std::string& address) const override {
    PYBIND11_OVERRIDE(
      monero_subaddress,                               
      monero_wallet,
      get_address_index,
      address
    );
  }

  monero_integrated_address get_integrated_address(const std::string& standard_address = "", const std::string& payment_id = "") const override {
    PYBIND11_OVERRIDE(
      monero_integrated_address,                               
      monero_wallet,
      get_integrated_address,
      standard_address, payment_id
    );
  }

  monero_integrated_address decode_integrated_address(const std::string& integrated_address) const override {
    PYBIND11_OVERRIDE(
      monero_integrated_address,                               
      monero_wallet,
      decode_integrated_address,
      integrated_address
    );
  }

  uint64_t get_height() const override {
    PYBIND11_OVERRIDE(
      uint64_t,                               
      monero_wallet,
      get_height
    );
  }

  uint64_t get_restore_height() const override {
    PYBIND11_OVERRIDE(
      uint64_t,                               
      monero_wallet,
      get_restore_height
    );
  }

  void set_restore_height(uint64_t restore_height) override {
    PYBIND11_OVERRIDE(
      void,                               
      monero_wallet,
      set_restore_height,
      restore_height
    );
  }

  uint64_t get_daemon_height() const override {
    PYBIND11_OVERRIDE(
      uint64_t,                               
      monero_wallet,
      get_daemon_height
    );
  }

  uint64_t get_daemon_max_peer_height() const override {
    PYBIND11_OVERRIDE(
      uint64_t,                               
      monero_wallet,
      get_daemon_max_peer_height
    );
  }

  uint64_t get_height_by_date(uint16_t year, uint8_t month, uint8_t day) const override {
    PYBIND11_OVERRIDE(
      uint64_t,                               
      monero_wallet,
      get_height_by_date,
      year, month, day
    );
  }

  void add_listener(monero_wallet_listener& listener) override {
    m_listeners.insert(&listener);
  }

  void remove_listener(monero_wallet_listener& listener) override {
    m_listeners.erase(&listener);
  }
  
  std::set<monero_wallet_listener*> get_listeners() override {
    return m_listeners;
  }

  monero_sync_result sync() override {
    PYBIND11_OVERRIDE(
      monero_sync_result,                               
      monero_wallet,
      sync
    );
  }

  monero_sync_result sync(monero_wallet_listener& listener) override {
    PYBIND11_OVERRIDE(
      monero_sync_result,                               
      monero_wallet,
      sync,
      listener
    );
  }

  monero_sync_result sync(uint64_t start_height) override {
    PYBIND11_OVERRIDE(
      monero_sync_result,                               
      monero_wallet,
      sync,
      start_height
    );
  }

  monero_sync_result sync(uint64_t start_height, monero_wallet_listener& listener) override {
    PYBIND11_OVERRIDE(
      monero_sync_result,                               
      monero_wallet,
      sync,
      start_height, listener
    );
  }

  void start_syncing(uint64_t sync_period_in_ms = 10000) override {
    PYBIND11_OVERRIDE(
      void,                               
      monero_wallet,
      start_syncing,
      sync_period_in_ms
    );
  }

  void scan_txs(const std::vector<std::string>& tx_hashes) override {
    PYBIND11_OVERRIDE(
      void,                               
      monero_wallet,
      scan_txs,
      tx_hashes
    );
  }

  void rescan_spent() override {
    PYBIND11_OVERRIDE(
      void,                               
      monero_wallet,
      rescan_spent
    );
  }

  void rescan_blockchain() override {
    PYBIND11_OVERRIDE(
      void,                               
      monero_wallet,
      rescan_blockchain
    );
  }

  uint64_t get_balance() const override {
    PYBIND11_OVERRIDE(
      uint64_t,                               
      monero_wallet,
      get_balance
    );
  }

  uint64_t get_balance(uint32_t account_idx) const override {
    PYBIND11_OVERRIDE(
      uint64_t,                               
      monero_wallet,
      get_balance,
      account_idx
    );
  }

  uint64_t get_balance(uint32_t account_idx, uint32_t subaddress_idx) const override {
    PYBIND11_OVERRIDE(
      uint64_t,                               
      monero_wallet,
      get_balance,
      account_idx, subaddress_idx
    );
  }

  uint64_t get_unlocked_balance() const override {
    PYBIND11_OVERRIDE(
      uint64_t,                               
      monero_wallet,
      get_unlocked_balance
    );
  }

  uint64_t get_unlocked_balance(uint32_t account_idx) const override {
    PYBIND11_OVERRIDE(
      uint64_t,                               
      monero_wallet,
      get_unlocked_balance,
      account_idx
    );
  }

  uint64_t get_unlocked_balance(uint32_t account_idx, uint32_t subaddress_idx) const override {
    PYBIND11_OVERRIDE(
      uint64_t,                               
      monero_wallet,
      get_unlocked_balance,
      account_idx, subaddress_idx
    );
  }

  std::vector<monero_account> get_accounts() const override {
    PYBIND11_OVERRIDE(
      std::vector<monero_account>,                               
      monero_wallet,
      get_accounts
    );
  }

  std::vector<monero_account> get_accounts(bool include_subaddresses) const override {
    PYBIND11_OVERRIDE(
      std::vector<monero_account>,                               
      monero_wallet,
      get_accounts,
      include_subaddresses
    );
  }

  std::vector<monero_account> get_accounts(const std::string& tag) const override {
    PYBIND11_OVERRIDE(
      std::vector<monero_account>,                               
      monero_wallet,
      get_accounts,
      tag
    );
  }

  std::vector<monero_account> get_accounts(bool include_subaddresses, const std::string& tag) const override {
    PYBIND11_OVERRIDE(
      std::vector<monero_account>,                               
      monero_wallet,
      get_accounts,
      include_subaddresses, tag
    );
  }

  monero_account get_account(uint32_t account_idx) const override {
    PYBIND11_OVERRIDE(
      monero_account,                               
      monero_wallet,
      get_account,
      account_idx
    );
  }

  monero_account get_account(const uint32_t account_idx, bool include_subaddresses) const {
    PYBIND11_OVERRIDE(
      monero_account,                               
      monero_wallet,
      get_account,
      account_idx, include_subaddresses
    );
  }

  monero_account create_account(const std::string& label = "") override {
    PYBIND11_OVERRIDE(
      monero_account,                               
      monero_wallet,
      create_account,
      label
    );
  }

  std::vector<monero_subaddress> get_subaddresses(uint32_t account_idx) const override {
    PYBIND11_OVERRIDE(
      std::vector<monero_subaddress>,                               
      monero_wallet,
      get_subaddresses,
      account_idx
    );
  }

  std::vector<monero_subaddress> get_subaddresses(uint32_t account_idx, const std::vector<uint32_t>& subaddress_indices) const override {
    PYBIND11_OVERRIDE(
      std::vector<monero_subaddress>,                               
      monero_wallet,
      get_subaddresses,
      account_idx, subaddress_indices
    );
  }

  monero_subaddress get_subaddress(uint32_t account_idx, uint32_t subaddress_idx) const override {
    PYBIND11_OVERRIDE(
      monero_subaddress,                               
      monero_wallet,
      get_subaddress,
      account_idx, subaddress_idx
    );
  }

  monero_subaddress create_subaddress(uint32_t account_idx, const std::string& label = "") override {
    PYBIND11_OVERRIDE(
      monero_subaddress,                               
      monero_wallet,
      create_subaddress,
      account_idx, label
    );
  }

  void set_subaddress_label(uint32_t account_idx, uint32_t subaddress_idx, const std::string& label = "") override {
    PYBIND11_OVERRIDE(
      void,                               
      monero_wallet,
      set_subaddress_label,
      account_idx, subaddress_idx, label
    );
  }

  std::vector<std::shared_ptr<monero_tx_wallet>> get_txs() const override {
    PYBIND11_OVERRIDE(
      std::vector<std::shared_ptr<monero_tx_wallet>>,                               
      monero_wallet,
      get_txs
    );
  }

  std::vector<std::shared_ptr<monero_tx_wallet>> get_txs(const monero_tx_query& query) const override {
    PYBIND11_OVERRIDE(
      std::vector<std::shared_ptr<monero_tx_wallet>>,                               
      monero_wallet,
      get_txs,
      query
    );
  }

  std::vector<std::shared_ptr<monero_transfer>> get_transfers(const monero_transfer_query& query) const override {
    PYBIND11_OVERRIDE(
      std::vector<std::shared_ptr<monero_transfer>>,                               
      monero_wallet,
      get_transfers,
      query
    );
  }

  std::vector<std::shared_ptr<monero_output_wallet>> get_outputs(const monero_output_query& query) const override {
    PYBIND11_OVERRIDE(
      std::vector<std::shared_ptr<monero_output_wallet>>,                               
      monero_wallet,
      get_outputs,
      query
    );
  }

  std::string export_outputs(bool all = false) const override {
    PYBIND11_OVERRIDE(
      std::string,                               
      monero_wallet,
      export_outputs,
      all
    );
  }

  int import_outputs(const std::string& outputs_hex) override {
    PYBIND11_OVERRIDE(
      int,                               
      monero_wallet,
      import_outputs,
      outputs_hex
    );
  }

  std::vector<std::shared_ptr<monero_key_image>> export_key_images(bool all = false) const override {
    PYBIND11_OVERRIDE(
      std::vector<std::shared_ptr<monero_key_image>>,                               
      monero_wallet,
      export_key_images,
      all
    );  
  }

  std::shared_ptr<monero_key_image_import_result> import_key_images(const std::vector<std::shared_ptr<monero_key_image>>& key_images) override {
    PYBIND11_OVERRIDE(
      std::shared_ptr<monero_key_image_import_result>,                               
      monero_wallet,
      import_key_images,
      key_images
    ); 
  }

  void freeze_output(const std::string& key_image) override {
    PYBIND11_OVERRIDE(
      void,
      monero_wallet,
      freeze_output,
      key_image
    ); 
  }

  void thaw_output(const std::string& key_image) override {
    PYBIND11_OVERRIDE(
      void,
      monero_wallet,
      thaw_output,
      key_image
    ); 
  }

  bool is_output_frozen(const std::string& key_image) override {
    PYBIND11_OVERRIDE(
      bool,
      monero_wallet,
      is_output_frozen,
      key_image
    ); 
  }

  monero_tx_priority get_default_fee_priority() const override {
    PYBIND11_OVERRIDE(
      monero_tx_priority,
      monero_wallet,
      get_default_fee_priority
    );
  }

  std::shared_ptr<monero_tx_wallet> create_tx(const monero_tx_config& config) override {
    PYBIND11_OVERRIDE(
      std::shared_ptr<monero_tx_wallet>,
      monero_wallet,
      create_tx,
      config
    );
  }

  std::vector<std::shared_ptr<monero_tx_wallet>> create_txs(const monero_tx_config& config) override {
    PYBIND11_OVERRIDE(
      std::vector<std::shared_ptr<monero_tx_wallet>>,
      monero_wallet,
      create_txs,
      config
    );
  }

  std::vector<std::shared_ptr<monero_tx_wallet>> sweep_unlocked(const monero_tx_config& config) override {
    PYBIND11_OVERRIDE(
      std::vector<std::shared_ptr<monero_tx_wallet>>,
      monero_wallet,
      sweep_unlocked,
      config
    );
  }

  std::shared_ptr<monero_tx_wallet> sweep_output(const monero_tx_config& config) override {
    PYBIND11_OVERRIDE(
      std::shared_ptr<monero_tx_wallet>,
      monero_wallet,
      sweep_output,
      config
    );
  }

  std::vector<std::shared_ptr<monero_tx_wallet>> sweep_dust(bool relay) override {
    PYBIND11_OVERRIDE(
      std::vector<std::shared_ptr<monero_tx_wallet>>,
      monero_wallet,
      sweep_dust,
      relay
    );
  }

  std::string relay_tx(const std::string& tx_metadata) override {
    PYBIND11_OVERRIDE(
      std::string,
      monero_wallet,
      relay_tx,
      tx_metadata
    );
  }

  std::string relay_tx(const monero_tx_wallet& tx) override {
    PYBIND11_OVERRIDE(
      std::string,
      monero_wallet,
      relay_tx,
      tx
    );
  }

  std::vector<std::string> relay_txs(const std::vector<std::shared_ptr<monero_tx_wallet>>& txs) override {
    PYBIND11_OVERRIDE(
      std::vector<std::string>,
      monero_wallet,
      relay_txs,
      txs
    );
  }

  std::vector<std::string> relay_txs(const std::vector<std::string>& tx_metadatas) override {
    PYBIND11_OVERRIDE(
      std::vector<std::string>,
      monero_wallet,
      relay_txs,
      tx_metadatas
    );
  }

  monero_tx_set describe_tx_set(const monero_tx_set& tx_set) override {
    PYBIND11_OVERRIDE(
      monero_tx_set,
      monero_wallet,
      describe_tx_set,
      tx_set
    );
  }

  monero_tx_set sign_txs(const std::string& unsigned_tx_hex) override {
    PYBIND11_OVERRIDE(
      monero_tx_set,
      monero_wallet,
      sign_txs,
      unsigned_tx_hex
    );
  }

  std::vector<std::string> submit_txs(const std::string& signed_tx_hex) override {
    PYBIND11_OVERRIDE(
      std::vector<std::string>,
      monero_wallet,
      submit_txs,
      signed_tx_hex
    );
  }

  std::string sign_message(const std::string& msg, monero_message_signature_type signature_type, uint32_t account_idx = 0, uint32_t subaddress_idx = 0) const override {
    PYBIND11_OVERRIDE(
      std::string,
      monero_wallet,
      sign_message,
      msg, signature_type, account_idx, subaddress_idx
    );
  }

  monero_message_signature_result verify_message(const std::string& msg, const std::string& address, const std::string& signature) const override {
    PYBIND11_OVERRIDE(
      monero_message_signature_result,
      monero_wallet,
      verify_message,
      msg, address, signature
    );
  }

  std::string get_tx_key(const std::string& tx_hash) const override {
    PYBIND11_OVERRIDE(
      std::string,
      monero_wallet,
      get_tx_key,
      tx_hash
    );
  }

  std::shared_ptr<monero_check_tx> check_tx_key(const std::string& tx_hash, const std::string& tx_key, const std::string& address) const override {
    PYBIND11_OVERRIDE(
      std::shared_ptr<monero_check_tx>,
      monero_wallet,
      check_tx_key,
      tx_hash, tx_key, address
    );
  }

  std::string get_tx_proof(const std::string& tx_hash, const std::string& address, const std::string& message) const override {
    PYBIND11_OVERRIDE(
      std::string,
      monero_wallet,
      get_tx_proof,
      tx_hash, address, message
    );
  }

  std::shared_ptr<monero_check_tx> check_tx_proof(const std::string& tx_hash, const std::string& address, const std::string& message, const std::string& signature) const override {
    PYBIND11_OVERRIDE(
      std::shared_ptr<monero_check_tx>,
      monero_wallet,
      check_tx_proof,
      tx_hash, address, message, signature
    );
  }

  std::string get_spend_proof(const std::string& tx_hash, const std::string& message) const override {
    PYBIND11_OVERRIDE(
      std::string,
      monero_wallet,
      get_spend_proof,
      tx_hash, message
    );
  }

  bool check_spend_proof(const std::string& tx_hash, const std::string& message, const std::string& signature) const override {
    PYBIND11_OVERRIDE(
      bool,
      monero_wallet,
      check_spend_proof,
      tx_hash, message, signature
    );
  }

  std::string get_reserve_proof_wallet(const std::string& message) const override {
    PYBIND11_OVERRIDE(
      std::string,
      monero_wallet,
      get_reserve_proof_wallet,
      message
    );
  }

  std::string get_reserve_proof_account(uint32_t account_idx, uint64_t amount, const std::string& message) const override {
    PYBIND11_OVERRIDE(
      std::string,
      monero_wallet,
      get_reserve_proof_account,
      account_idx, amount, message
    );
  }

  std::shared_ptr<monero_check_reserve> check_reserve_proof(const std::string& address, const std::string& message, const std::string& signature) const override {
    PYBIND11_OVERRIDE(
      std::shared_ptr<monero_check_reserve>,
      monero_wallet,
      check_reserve_proof,
      address, message, signature
    );
  }

  std::string get_tx_note(const std::string& tx_hash) const override {
    PYBIND11_OVERRIDE(
      std::string,
      monero_wallet,
      get_tx_note,
      tx_hash
    );
  }

  std::vector<std::string> get_tx_notes(const std::vector<std::string>& tx_hashes) const override {
    PYBIND11_OVERRIDE(
      std::vector<std::string>,
      monero_wallet,
      get_tx_notes,
      tx_hashes
    );
  }

  void set_tx_note(const std::string& tx_hash, const std::string& note) override {
    PYBIND11_OVERRIDE(
      void,
      monero_wallet,
      set_tx_note,
      tx_hash, note
    );
  }

  void set_tx_notes(const std::vector<std::string>& tx_hashes, const std::vector<std::string>& notes) override {
    PYBIND11_OVERRIDE(
      void,
      monero_wallet,
      set_tx_notes,
      tx_hashes, notes
    );
  }

  std::vector<monero_address_book_entry> get_address_book_entries(const std::vector<uint64_t>& indices) const override {
    PYBIND11_OVERRIDE(
      std::vector<monero_address_book_entry>,
      monero_wallet,
      get_address_book_entries,
      indices
    );
  }

  uint64_t add_address_book_entry(const std::string& address, const std::string& description) override {
    PYBIND11_OVERRIDE(
      uint64_t,
      monero_wallet,
      add_address_book_entry,
      address, description
    );
  }

  void edit_address_book_entry(uint64_t index, bool set_address, const std::string& address, bool set_description, const std::string& description) override {
    PYBIND11_OVERRIDE(
      void,
      monero_wallet,
      edit_address_book_entry,
      index, set_address, address, set_description, description
    );
  }

  void delete_address_book_entry(uint64_t index) override {
    PYBIND11_OVERRIDE(
      void,
      monero_wallet,
      delete_address_book_entry,
      index
    );
  }

  std::string get_payment_uri(const monero_tx_config& config) const override {
    PYBIND11_OVERRIDE(
      std::string,
      monero_wallet,
      get_payment_uri,
      config
    );
  }

  std::shared_ptr<monero_tx_config> parse_payment_uri(const std::string& uri) const override {
    PYBIND11_OVERRIDE(
      std::shared_ptr<monero_tx_config>,
      monero_wallet,
      parse_payment_uri,
      uri
    );
  }

  bool get_attribute(const std::string& key, std::string& value) const override {
    PYBIND11_OVERRIDE(
      bool,
      monero_wallet,
      get_attribute,
      key, value
    );
  }

  void set_attribute(const std::string& key, const std::string& val) override {
    PYBIND11_OVERRIDE(
      void,
      monero_wallet,
      set_attribute,
      key, val
    );
  }

  void start_mining(boost::optional<uint64_t> num_threads, boost::optional<bool> background_mining, boost::optional<bool> ignore_battery) {
    PYBIND11_OVERRIDE(
      void,
      monero_wallet,
      start_mining,
      num_threads,
      background_mining,
      ignore_battery
    );
  }

  void stop_mining() override {
    PYBIND11_OVERRIDE(
      void,
      monero_wallet,
      stop_mining
    );
  }

  uint64_t wait_for_next_block() override {
    PYBIND11_OVERRIDE(
      uint64_t,
      monero_wallet,
      wait_for_next_block
    );
  }

  bool is_multisig_import_needed() const override {
    PYBIND11_OVERRIDE(
      bool,
      monero_wallet,
      is_multisig_import_needed
    );
  }

  bool is_multisig() const override {
    PYBIND11_OVERRIDE(
      bool,
      monero_wallet,
      is_multisig
    );
  }

  monero_multisig_info get_multisig_info() const override {
    PYBIND11_OVERRIDE(
      monero_multisig_info,
      monero_wallet,
      get_multisig_info
    );
  }

  std::string prepare_multisig() override {
    PYBIND11_OVERRIDE(
      std::string,
      monero_wallet,
      prepare_multisig
    );
  }

  std::string make_multisig(const std::vector<std::string>& multisig_hexes, int threshold, const std::string& password) override {
    PYBIND11_OVERRIDE(
      std::string,
      monero_wallet,
      make_multisig,
      multisig_hexes, threshold, password
    );
  }

  monero_multisig_init_result exchange_multisig_keys(const std::vector<std::string>& multisig_hexes, const std::string& password) override {
    PYBIND11_OVERRIDE(
      monero_multisig_init_result,
      monero_wallet,
      exchange_multisig_keys,
      multisig_hexes, password
    );
  }

  std::string export_multisig_hex() override {
    PYBIND11_OVERRIDE(
      std::string,
      monero_wallet,
      export_multisig_hex
    );
  }

  int import_multisig_hex(const std::vector<std::string>& multisig_hexes) override {
    PYBIND11_OVERRIDE(
      int,
      monero_wallet,
      import_multisig_hex,
      multisig_hexes
    );
  }

  monero_multisig_sign_result sign_multisig_tx_hex(const std::string& multisig_tx_hex) override {
    PYBIND11_OVERRIDE(
      monero_multisig_sign_result,
      monero_wallet,
      sign_multisig_tx_hex,
      multisig_tx_hex
    );
  }

  std::vector<std::string> submit_multisig_tx_hex(const std::string& signed_multisig_tx_hex) override {
    PYBIND11_OVERRIDE(
      std::vector<std::string>,
      monero_wallet,
      submit_multisig_tx_hex,
      signed_multisig_tx_hex
    );
  }

  void change_password(const std::string& old_password, const std::string& new_password) override {
    PYBIND11_OVERRIDE(
      void,
      monero_wallet,
      change_password,
      old_password, new_password
    );
  }

  void move_to(const std::string& path, const std::string& password) override {
    PYBIND11_OVERRIDE(
      void,
      monero_wallet,
      move_to,
      path, password
    );
  }

  void save() override {
    PYBIND11_OVERRIDE(
      void,
      monero_wallet,
      save
    );
  }

  void close(bool save = false) override {
    PYBIND11_OVERRIDE(
      void,
      monero_wallet,
      close,
      save
    );
  }

  virtual void set_connection_manager(const std::shared_ptr<PyMoneroConnectionManager> &connection_manager) {
    if (m_connection_manager != nullptr) m_connection_manager->remove_listener(m_connection_manager_listener);
    m_connection_manager = connection_manager;
    if (m_connection_manager == nullptr) return;
    if (m_connection_manager_listener == nullptr) m_connection_manager_listener = std::make_shared<PyMoneroWalletConnectionManagerListener>(this);
    connection_manager->add_listener(m_connection_manager_listener);
    set_daemon_connection(*connection_manager->get_connection());
  };

  virtual std::optional<std::shared_ptr<PyMoneroConnectionManager>> get_connection_manager() const {
    std::optional<std::shared_ptr<PyMoneroConnectionManager>> result;
    if (m_connection_manager != nullptr) result = m_connection_manager;
    return result;
  }

  virtual bool is_closed() const { return m_is_closed; }

  virtual void announce_new_block(uint64_t height) {
    for (const auto &listener : m_listeners) {
      try {
        listener->on_new_block(height);
      } catch (const std::exception &e) {
        std::cout << "Error: " << e.what() << std::endl;
      }
    }
  }

  virtual void announce_sync_progress(uint64_t height, uint64_t start_height, uint64_t end_height, float percent_done, const std::string &message) {
    for (const auto &listener : m_listeners) {
      try {
        listener->on_sync_progress(height, start_height, end_height, percent_done, message);
      } catch (const std::exception &e) {
        std::cout << "Error: " << e.what() << std::endl;
      }
    }
  }

  virtual void announce_balances_changed(uint64_t balance, uint64_t unlocked_balance) {
    for (const auto &listener : m_listeners) {
      try {
        listener->on_balances_changed(balance, unlocked_balance);
      } catch (const std::exception &e) {
        std::cout << "Error: " << e.what() << std::endl;
      }
    }
  }

  virtual void announce_output_spent(const std::shared_ptr<monero::monero_output_wallet> &output) {
    for (const auto &listener : m_listeners) {
      try {
        listener->on_output_spent(*output);
      } catch (const std::exception &e) {
        std::cout << "Error: " << e.what() << std::endl;
      }
    }
  }

  virtual void announce_output_received(const std::shared_ptr<monero::monero_output_wallet> &output) {
    for (const auto &listener : m_listeners) {
      try {
        listener->on_output_received(*output);
      } catch (const std::exception &e) {
        std::cout << "Error: " << e.what() << std::endl;
      }
    }
  }

  virtual std::shared_ptr<PyMoneroWalletBalance> get_balances(boost::optional<uint32_t> account_idx, boost::optional<uint32_t> subaddress_idx) const {
    throw std::runtime_error("MoneroWallet::get_balances(): not implemented");
  }

protected:
  bool m_is_closed = false;
  std::shared_ptr<PyMoneroConnectionManager> m_connection_manager;
  std::shared_ptr<PyMoneroWalletConnectionManagerListener> m_connection_manager_listener;
  std::set<monero::monero_wallet_listener*> m_listeners;
};

class PyMoneroWalletFull : public monero::monero_wallet_full {
public:

  bool is_closed() const { 
    std::cout << "calling PyMoneroWalletFull::is_closed" << std::endl;

    return m_is_closed; 
  }

  void close(bool save = false) override {
    if (m_is_closed) throw std::runtime_error("Wallet already closed");
    monero::monero_wallet_full::close(save);
  }

protected:
  bool m_is_closed = false;
};

class PyMoneroWalletPoller {
public:
  explicit PyMoneroWalletPoller(PyMoneroWallet *wallet) {
    m_wallet = wallet;
    m_is_polling = false;
    m_num_polling = 0;
  }

  ~PyMoneroWalletPoller() {
    set_is_polling(false);
  }

  void set_is_polling(bool is_polling) {
    if (is_polling == m_is_polling) return;
    m_is_polling = is_polling;

    if (m_is_polling) {
      m_thread = std::thread([this]() {
        loop();
      });
      m_thread.detach();
    } else {
      if (m_thread.joinable()) m_thread.join();
    }
  }

  void set_period_in_ms(uint64_t period_ms) {
    m_poll_period_ms = period_ms;
  }

  bool is_polling() const { return m_is_polling; }

  void poll() {
    if (m_num_polling > 1) return;
    m_num_polling++;

    boost::lock_guard<boost::recursive_mutex> lock(m_mutex);
    try {
      // skip if wallet is closed
      if (m_wallet->is_closed()) {
        m_num_polling--;
        return;
      }

      if (m_prev_balances == boost::none) {
        m_prev_height = m_wallet->get_height();
        monero::monero_tx_query tx_query;
        tx_query.m_is_locked = true;
        m_prev_locked_txs = m_wallet->get_txs(tx_query);
        m_prev_balances = m_wallet->get_balances(boost::none, boost::none);
        m_num_polling--;
        return;
      }

      // announce height changes
      uint64_t height = m_wallet->get_height();
      if (m_prev_height.get() != height) {
        for (uint64_t i = m_prev_height.get(); i < height; i++) {
          on_new_block(i);
        }

        m_prev_height = height;
      }
      
      // get locked txs for comparison to previous
      uint64_t min_height = 0; // only monitor recent txs
      if (height > 70) min_height = height - 70; 
      monero::monero_tx_query tx_query;
      tx_query.m_is_locked = true;
      tx_query.m_min_height = min_height;
      tx_query.m_include_outputs = true;

      auto locked_txs = m_wallet->get_txs(tx_query);

      // collect hashes of txs no longer locked
      std::vector<std::string> no_longer_locked_hashes;
      for (const auto &prev_locked_tx : m_prev_locked_txs) {
        if (get_tx(locked_txs, prev_locked_tx->m_hash.get()) == nullptr) {
          no_longer_locked_hashes.push_back(prev_locked_tx->m_hash.get());
        }
      }
      m_prev_locked_txs = locked_txs;
      std::vector<std::shared_ptr<monero::monero_tx_wallet>> unlocked_txs;

      if (!no_longer_locked_hashes.empty()) {
        monero_tx_query tx_query;
        tx_query.m_is_locked = false;
        tx_query.m_min_height = min_height;
        tx_query.m_hashes = no_longer_locked_hashes;
        tx_query.m_include_outputs = true;
        unlocked_txs = m_wallet->get_txs(tx_query);
      }

      // announce new unconfirmed and confirmed txs
      for (const auto &locked_tx : locked_txs) {
        if (locked_tx->m_is_confirmed) {
          m_prev_confirmed_notifications.push_back(locked_tx->m_hash.get());
          notify_outputs(locked_tx);
        }
        else {
          m_prev_unconfirmed_notifications.push_back(locked_tx->m_hash.get());
        }
      }
      
      // announce new unlocked outputs
      for (const auto &unlocked_tx : unlocked_txs) {
        std::string tx_hash = unlocked_tx->m_hash.get();
        m_prev_confirmed_notifications.erase(std::remove_if(m_prev_confirmed_notifications.begin(), m_prev_confirmed_notifications.end(), [&tx_hash](std::string iter){ return iter == tx_hash; }), m_prev_confirmed_notifications.end());
        m_prev_unconfirmed_notifications.erase(std::remove_if(m_prev_unconfirmed_notifications.begin(), m_prev_unconfirmed_notifications.end(), [&tx_hash](std::string iter){ return iter == tx_hash; }), m_prev_unconfirmed_notifications.end());
        notify_outputs(unlocked_tx);
      }

      check_for_changed_balances();

      m_num_polling--;
    }
    catch (const std::exception &e) {
      m_num_polling--;
      if (m_is_polling) {
        std::cout << "Failed to background poll wallet " << m_wallet->get_path() << ": " << e.what() << std::endl;
      }
    }
  }

protected:
  mutable boost::recursive_mutex m_mutex;
  PyMoneroWallet *m_wallet;
  std::atomic<bool> m_is_polling;
  uint64_t m_poll_period_ms;
  std::thread m_thread;
  int m_num_polling;
  std::vector<std::string> m_prev_unconfirmed_notifications;
  std::vector<std::string> m_prev_confirmed_notifications;

  boost::optional<std::shared_ptr<PyMoneroWalletBalance>> m_prev_balances;
  boost::optional<uint64_t> m_prev_height;
  std::vector<std::shared_ptr<monero::monero_tx_wallet>> m_prev_locked_txs;

  std::shared_ptr<monero::monero_tx_wallet> get_tx(const std::vector<std::shared_ptr<monero::monero_tx_wallet>> txs, std::string tx_hash) {
    for (auto &tx : txs) {
      if (tx->m_hash == tx_hash) return tx;
    }

    return nullptr;
  }

  void loop() {
    while (m_is_polling) {
      try {
        poll();
      } catch (const std::exception& e) {
        std::cout << "ERROR " << e.what() << std::endl;
      }

      std::this_thread::sleep_for(std::chrono::milliseconds(m_poll_period_ms));
    }
  }

  void on_new_block(uint64_t height) {
    m_wallet->announce_new_block(height);
  }

  void notify_outputs(const std::shared_ptr<monero::monero_tx_wallet> &tx) {
    if (tx->m_outgoing_transfer != boost::none) {
      auto outgoing_transfer = tx->m_outgoing_transfer.get();
      if (!tx->m_inputs.empty()) throw std::runtime_error("Tx inputs should be empty");
      auto output = std::make_shared<monero::monero_output_wallet>();
      output->m_amount = outgoing_transfer->m_amount.get() + tx->m_fee.get();
      output->m_account_index = outgoing_transfer->m_account_index;
      output->m_tx = tx;
      if (outgoing_transfer->m_subaddress_indices.size() == 1) {
        output->m_subaddress_index = outgoing_transfer->m_subaddress_indices[0];
      }
      tx->m_inputs.push_back(output);
      m_wallet->announce_output_spent(output);
    }

    if (tx->m_incoming_transfers.size() > 0) {
      if (!tx->m_outputs.empty()) {
        for(const auto &output : tx->get_outputs_wallet()) {
          m_wallet->announce_output_received(output);
        }
      }
      else {
        for (const auto &transfer : tx->m_incoming_transfers) {
          auto output = std::make_shared<monero::monero_output_wallet>();
          output->m_account_index = transfer->m_account_index;
          output->m_subaddress_index = transfer->m_subaddress_index;
          output->m_amount = transfer->m_amount.get();
          output->m_tx = tx;
          tx->m_outputs.push_back(output);
        }

        for (const auto &output : tx->get_outputs_wallet()) {
          m_wallet->announce_output_received(output);
        }
      }
    }
  } 

  bool check_for_changed_balances() {
    auto balances = m_wallet->get_balances(boost::none, boost::none);
    if (balances->m_balance != m_prev_balances.get()->m_balance || balances->m_unlocked_balance != m_prev_balances.get()->m_unlocked_balance) {
      m_prev_balances = balances;
      m_wallet->announce_balances_changed(balances->m_balance, balances->m_unlocked_balance);
      return true;
    }
    return false;
  }
};

class PyMoneroWalletRpc : public PyMoneroWallet {
public:

  PyMoneroWalletRpc() {
    m_rpc = std::make_shared<PyMoneroRpcConnection>();
  }

  PyMoneroWalletRpc(std::shared_ptr<PyMoneroRpcConnection> rpc_connection) {
    m_rpc = rpc_connection;
  }

  PyMoneroWalletRpc(const std::string& uri = "", const std::string& username = "", const std::string& password = "")
  {
    m_rpc = std::make_shared<PyMoneroRpcConnection>(uri, username, password);
    m_rpc->check_connection();
  }

  boost::optional<monero::monero_rpc_connection> get_rpc_connection() const {
    if (m_rpc == nullptr) return boost::none;
    return boost::optional<monero::monero_rpc_connection>(*m_rpc);
  }

  PyMoneroWalletRpc* open_wallet(const std::shared_ptr<PyMoneroWalletConfig> &config) {
    if (config == nullptr) throw std::runtime_error("Must provide configuration of wallet to open");
    if (config->m_path == boost::none || config->m_path->empty()) throw std::runtime_error("Filename is not initialized");
    std::string path = config->m_path.get();
    std::string password = std::string("");
    if (config->m_password != boost::none) password = config->m_password.get();

    auto params = std::make_shared<PyMoneroCreateOpenWalletParams>(path, password);
    PyMoneroJsonRequest request("open_wallet", params);
    m_rpc->send_json_request(request);
    clear();

    if (config->m_connection_manager != boost::none) {
      if (config->m_server != boost::none) throw std::runtime_error("Wallet can be opened with a server or connection manager but not both");
      set_connection_manager(config->m_connection_manager.get());
    }
    else if (config->m_server != boost::none) {
      set_daemon_connection(config->m_server);
    }
    
    return this;
  }

  PyMoneroWalletRpc* open_wallet(const std::string& name, const std::string& password) {
    auto config = std::make_shared<PyMoneroWalletConfig>();
    config->m_path = name;
    config->m_password = password;
    return open_wallet(config);
  }

  PyMoneroWalletRpc* create_wallet(const std::shared_ptr<PyMoneroWalletConfig> &config) {
    if (!config) throw std::runtime_error("Must specify config to create wallet");
    if (config->m_network_type != boost::none) throw std::runtime_error("Cannot specify network type when creating RPC wallet");
    if (config->m_seed != boost::none && (config->m_primary_address != boost::none || config->m_private_view_key != boost::none || config->m_private_spend_key != boost::none)) {
      throw std::runtime_error("Wallet can be initialized with a seed or keys but not both");
    }
    if (config->m_account_lookahead != boost::none || config->m_subaddress_lookahead != boost::none) throw std::runtime_error("monero-wallet-rpc does not support creating wallets with subaddress lookahead over rpc");

    if (config->m_connection_manager != boost::none) {
      if (config->m_server != boost::none) throw std::runtime_error("Wallet can be opened with a server or connection manager but not both");
      config->m_server = *config->m_connection_manager.get()->get_connection();
    }

    if (config->m_seed != boost::none) create_wallet_from_seed(config);
    else if (config->m_private_spend_key != boost::none || config->m_primary_address != boost::none) create_wallet_from_keys(config);
    else create_wallet_random(config);

    if (config->m_connection_manager != boost::none) {
      set_connection_manager(config->m_connection_manager.get());
    }
    else if (config->m_server != boost::none) {
      set_daemon_connection(config->m_server);
    }

    return this;
  }

  std::vector<std::string> get_seed_languages() const {
    PyMoneroJsonRequest request("get_languages");
    std::shared_ptr<PyMoneroJsonResponse> response = m_rpc->send_json_request(request);

    if (response->m_result == boost::none) throw std::runtime_error("Invalid Monero JSONRPC response");
    auto node = response->m_result.get();
    std::vector<std::string> languages;

    for (auto it = node.begin(); it != node.end(); ++it) {
      std::string key = it->first;

      if (key == std::string("languages")) {
        auto languages_node = it->second;

        for (auto it2 = languages_node.begin(); it2 != languages_node.end(); ++it2) {
          languages.push_back(it2->second.data());
        }
      }
    }

    return languages;
  }

  void stop() {
    PyMoneroJsonRequest request("stop_wallet");
    std::shared_ptr<PyMoneroJsonResponse> response = m_rpc->send_json_request(request);
  }  
 
  bool is_view_only() const override {
    try {
      std::string key = "mnemonic";
      query_key(key);
      return false;
    }
    catch (const PyMoneroRpcError& e) {
      if (e.code == -29) return true;
      if (e.code == -1) return false;
      throw e;
    }
  }

  boost::optional<monero::monero_rpc_connection> get_daemon_connection() const override {
    if (m_daemon_connection == nullptr) return boost::none;
    return boost::optional<monero::monero_rpc_connection>(*m_daemon_connection);
  }
  
  void set_daemon_connection(const boost::optional<monero_rpc_connection>& connection, bool is_trusted, const boost::optional<std::shared_ptr<PyMoneroSslOptions>> ssl_options) {
    auto params = std::make_shared<PyMoneroSetDaemonParams>();
    if (connection == boost::none) {
      params->m_address = "placeholder";
      params->m_username = "";
      params->m_password = "";
    }
    else { 
      params->m_address = connection->m_uri;
      params->m_username = connection->m_username;
      params->m_password = connection->m_password;
    }

    params->m_trusted = is_trusted;
    params->m_ssl_support = "autodetect";

    if (ssl_options != boost::none) {
      params->m_ssl_private_key_path = ssl_options.get()->m_ssl_private_key_path;
      params->m_ssl_certificate_path = ssl_options.get()->m_ssl_certificate_path;
      params->m_ssl_ca_file = ssl_options.get()->m_ssl_ca_file;
      params->m_ssl_allowed_fingerprints = ssl_options.get()->m_ssl_allowed_fingerprints;
      params->m_ssl_allow_any_cert = ssl_options.get()->m_ssl_allow_any_cert;
    }

    PyMoneroJsonRequest request("set_daemon", params);
    m_rpc->send_json_request(request);

    if (connection == boost::none || connection->m_uri == boost::none || connection->m_uri->empty()) {
      m_daemon_connection = nullptr;
    }
    else {
      m_daemon_connection = std::make_shared<PyMoneroRpcConnection>(connection.get());
    }
  }

  void set_daemon_connection(const boost::optional<monero_rpc_connection>& connection) override {
    set_daemon_connection(connection, false, boost::none);
  }

  bool is_connected_to_daemon() const override {
    try {
      check_reserve_proof(get_primary_address(), "", "");
      return false;
    }
    catch (const PyMoneroRpcError& e) {
      if (e.message == std::string("Failed to connect to daemon")) return false;
      return true;
    }
  }

  monero::monero_version get_version() const override { 
    PyMoneroJsonRequest request("get_version");
    std::shared_ptr<PyMoneroJsonResponse> response = m_rpc->send_json_request(request);

    if (response->m_result == boost::none) throw std::runtime_error("Invalid Monero JSONRPC response");
    auto res = response->m_result.get();

    std::shared_ptr<PyMoneroVersion> info = std::make_shared<PyMoneroVersion>();
    PyMoneroVersion::from_property_tree(res, info);
    return *info;
  }

  std::string get_path() const override {
    return m_path;
  }

  std::string get_seed() const override {
    std::string key = "mnemonic";
    return query_key(key);
  }

  std::string get_seed_language() const override {
    throw std::runtime_error("MoneroWalletRpc::get_seed_language() not supported");
  }

  std::string get_public_view_key() const override {
    std::string key = "public_view_key";
    return query_key(key);
  }

  std::string get_private_view_key() const override {
    std::string key = "view_key";
    return query_key(key);
  }

  std::string get_public_spend_key() const override {
    std::string key = "public_spend_key";
    return query_key(key);
  }

  std::string get_private_spend_key() const override {
    std::string key = "spend_key";
    return query_key(key);
  }

  std::string get_address(const uint32_t account_idx, const uint32_t subaddress_idx) const override {
    auto it = m_address_cache.find(account_idx);
    std::vector<uint32_t> empty_indices;
    if (it == m_address_cache.end()) {
      get_subaddresses(account_idx, empty_indices, true);
      return get_address(account_idx, subaddress_idx);
    }
    
    auto subaddress_map = it->second;
    auto it2 = subaddress_map.find(subaddress_idx);

    if (it2 == subaddress_map.end()) {
      get_subaddresses(account_idx, empty_indices, true);
      return get_address(account_idx, subaddress_idx);
    }

    return it2->second.data();
  }

  monero_subaddress get_address_index(const std::string& address) const override {
    auto params = std::make_shared<PyMoneroGetAddressIndexParams>(address);
    PyMoneroJsonRequest request("get_address_index", params);
    std::shared_ptr<PyMoneroJsonResponse> response = m_rpc->send_json_request(request);

    if (response->m_result == boost::none) throw std::runtime_error("Invalid Monero JSONRPC response");
    auto res = response->m_result.get();

    auto tmplt = std::make_shared<monero::monero_subaddress>();
    PyMoneroSubaddress::from_property_tree(res, tmplt);
    return *tmplt;
  }
  
  monero_integrated_address get_integrated_address(const std::string& standard_address = "", const std::string& payment_id = "") const override {
    auto params = std::make_shared<PyMoneroMakeIntegratedAddressParams>(standard_address, payment_id);
    PyMoneroJsonRequest request("make_integrated_address", params);
    std::shared_ptr<PyMoneroJsonResponse> response = m_rpc->send_json_request(request);

    if (response->m_result == boost::none) throw std::runtime_error("Invalid Monero JSONRPC response");
    auto res = response->m_result.get();

    auto tmplt = std::make_shared<monero::monero_integrated_address>();
    PyMoneroIntegratedAddress::from_property_tree(res, tmplt);
    return decode_integrated_address(tmplt->m_integrated_address);
  }

  monero_integrated_address decode_integrated_address(const std::string& integrated_address) const override {
    auto params = std::make_shared<PyMoneroSplitIntegratedAddressParams>(integrated_address);
    PyMoneroJsonRequest request("split_integrated_address", params);
    std::shared_ptr<PyMoneroJsonResponse> response = m_rpc->send_json_request(request);
    if (response->m_result == boost::none) throw std::runtime_error("Invalid Monero JSONRPC response");
    auto res = response->m_result.get();
    auto tmplt = std::make_shared<monero::monero_integrated_address>();
    PyMoneroIntegratedAddress::from_property_tree(res, tmplt);
    tmplt->m_integrated_address = integrated_address;
    return *tmplt;
  }

  uint64_t get_height() const override {
    PyMoneroJsonRequest request("get_height");
    std::shared_ptr<PyMoneroJsonResponse> response = m_rpc->send_json_request(request);
    if (response->m_result == boost::none) throw std::runtime_error("Invalid Monero JSONRPC response");
    auto res = response->m_result.get();
    return PyMoneroWalletGetHeightResponse::from_property_tree(res);
  }

  uint64_t get_daemon_height() const override {
    throw std::runtime_error("monero-wallet-rpc does not support getting the chain height");
  }

  uint64_t get_height_by_date(uint16_t year, uint8_t month, uint8_t day) const override {
    throw std::runtime_error("monero-wallet-rpc does not support getting a height by date");
  }

  monero_sync_result sync() override {
    auto params = std::make_shared<PyMoneroRefreshWalletParams>();
    boost::lock_guard<boost::recursive_mutex> lock(m_sync_mutex);
    PyMoneroJsonRequest request("refresh", params);
    poll();
    auto response = m_rpc->send_json_request(request);
    if (response->m_result == boost::none) throw std::runtime_error("Invalid Monero JSONRPC response");
    auto node = response->m_result.get();
    monero_sync_result sync_result(0, false);

    for (auto it = node.begin(); it != node.end(); ++it) {
      std::string key = it->first;

      if (key == std::string("blocks_fetched")) sync_result.m_num_blocks_fetched = it->second.get_value<uint64_t>();
      else if (key == std::string("received_money")) sync_result.m_received_money = it->second.get_value<bool>();
    }

    return sync_result;
  }

  monero_sync_result sync(monero_wallet_listener& listener) override {
    throw std::runtime_error("Monero Wallet RPC does not support reporting sync progress");
  }

  monero_sync_result sync(uint64_t start_height, monero_wallet_listener& listener) override {
    throw std::runtime_error("Monero Wallet RPC does not support reporting sync progress");
  }

  monero_sync_result sync(uint64_t start_height) override {
    auto params = std::make_shared<PyMoneroRefreshWalletParams>(start_height);
    boost::lock_guard<boost::recursive_mutex> lock(m_sync_mutex);
    PyMoneroJsonRequest request("refresh", params);
    auto response = m_rpc->send_json_request(request);
    poll();
    if (response->m_result == boost::none) throw std::runtime_error("Invalid Monero JSONRPC response");
    auto node = response->m_result.get();
    monero_sync_result sync_result(0, false);

    for (auto it = node.begin(); it != node.end(); ++it) {
      std::string key = it->first;

      if (key == std::string("blocks_fetched")) sync_result.m_num_blocks_fetched = it->second.get_value<uint64_t>();
      else if (key == std::string("received_money")) sync_result.m_received_money = it->second.get_value<bool>();
    }

    return sync_result;
  }

  void start_syncing(uint64_t sync_period_in_ms = 10000) override {
    // convert ms to seconds for rpc parameter
    uint64_t sync_period_in_seconds = sync_period_in_ms / 1000;
    
    // send rpc request
    auto params = std::make_shared<PyMoneroRefreshWalletParams>(true, sync_period_in_seconds);
    PyMoneroJsonRequest request("auto_refresh", params);
    auto response = m_rpc->send_json_request(request);
    
    // update sync period for poller
    m_sync_period_in_ms = sync_period_in_seconds * 1000;
    if (m_poller != nullptr) m_poller->set_period_in_ms(m_sync_period_in_ms.get());
    
    // poll if listening
    poll();
  }

  void stop_syncing() override {
    auto params = std::make_shared<PyMoneroAutoRefreshParams>(false);
    PyMoneroJsonRequest request("auto_refresh", params);
    m_rpc->send_json_request(request);
  }

  void scan_txs(const std::vector<std::string>& tx_hashes) override {
    if (tx_hashes.empty()) throw std::runtime_error("No tx hashes given to scan");
    auto params = std::make_shared<PyMoneroScanTxParams>(tx_hashes);
    PyMoneroJsonRequest request("scan_tx", params);
    m_rpc->send_json_request(request);
    poll();
  }

  void rescan_spent() override {
    PyMoneroJsonRequest request("rescan_spent");
    m_rpc->send_json_request(request);
  }

  void rescan_blockchain() override {
    PyMoneroJsonRequest request("rescan_blockchain");
    m_rpc->send_json_request(request);
  }

  uint64_t get_balance() const override {
    auto wallet_balance = get_balances(boost::none, boost::none);
    return wallet_balance->m_balance;
    return 0;
  }

  uint64_t get_balance(uint32_t account_index) const override {
    auto wallet_balance = get_balances(account_index, boost::none);
    return wallet_balance->m_balance;
  }

  uint64_t get_balance(uint32_t account_idx, uint32_t subaddress_idx) const override {
    auto wallet_balance = get_balances(account_idx, subaddress_idx);
    return wallet_balance->m_balance;
  }

  uint64_t get_unlocked_balance() const override {
    auto wallet_balance = get_balances(boost::none, boost::none);
    return wallet_balance->m_unlocked_balance;
  }

  uint64_t get_unlocked_balance(uint32_t account_index) const override {
    auto wallet_balance = get_balances(account_index, boost::none);
    return wallet_balance->m_unlocked_balance;
  }

  uint64_t get_unlocked_balance(uint32_t account_idx, uint32_t subaddress_idx) const override {
    auto wallet_balance = get_balances(account_idx, subaddress_idx);
    return wallet_balance->m_unlocked_balance;
  }

  std::vector<monero_account> get_accounts(bool include_subaddresses, const std::string& tag, bool skip_balances) const {
    auto params = std::make_shared<PyMoneroGetAccountsParams>(tag);
    PyMoneroJsonRequest request("get_accounts", params);
    auto response = m_rpc->send_json_request(request);
    if (response->m_result == boost::none) throw std::runtime_error("Invalid Monero JSONRPC response");
    auto node = response->m_result.get();
    std::vector<monero_account> accounts;
    PyMoneroAccount::from_property_tree(node, accounts);
    std::vector<uint32_t> empty_indices;

    if (include_subaddresses) {

      for (auto &account : accounts) {
        account.m_subaddresses = get_subaddresses(account.m_index.get(), empty_indices, true);

        if (!skip_balances) {
          for (auto &subaddress : account.m_subaddresses) {
            subaddress.m_balance = 0;
            subaddress.m_unlocked_balance = 0;
            subaddress.m_num_unspent_outputs = 0;
            subaddress.m_num_blocks_to_unlock = 0;
          }
        }
      }

      if (!skip_balances) {
        auto params2 = std::make_shared<PyMoneroGetBalanceParams>(true);
        PyMoneroJsonRequest request2("get_balance", params2);
        auto response2 = m_rpc->send_json_request(request2);
        if (response2->m_result == boost::none) throw std::runtime_error("Invalid Monero JSONRPC response");
        auto node2 = response2->m_result.get();
        auto bal_res = std::make_shared<PyMoneroGetBalanceResponse>();
        PyMoneroGetBalanceResponse::from_property_tree(node2, bal_res);

        for (const auto &subaddress : bal_res->m_per_subaddress) {
          // merge info
          auto account = &accounts[subaddress->m_account_index.get()];
          if (account->m_index != subaddress->m_account_index) throw std::runtime_error("RPC accounts are out of order"); 
          auto tgt_subaddress = &account->m_subaddresses[subaddress->m_account_index.get()];
          if (tgt_subaddress->m_index != subaddress->m_index) throw std::runtime_error("RPC subaddresses are out of order");

          if (subaddress->m_balance != boost::none) tgt_subaddress->m_balance = subaddress->m_balance;
          if (subaddress->m_unlocked_balance != boost::none) tgt_subaddress->m_unlocked_balance = subaddress->m_unlocked_balance;
          if (subaddress->m_num_unspent_outputs != boost::none) tgt_subaddress->m_num_unspent_outputs = subaddress->m_num_unspent_outputs;
          if (subaddress->m_num_blocks_to_unlock != boost::none) tgt_subaddress->m_num_blocks_to_unlock = subaddress->m_num_blocks_to_unlock;
        }
      }
    }

    return accounts;
  }

  monero_account create_account(const std::string& label = "") override {
    auto params = std::make_shared<PyMoneroCreateAccountParams>(label);
    PyMoneroJsonRequest request("create_account", params);
    auto response = m_rpc->send_json_request(request);
    if (response->m_result == boost::none) throw std::runtime_error("Invalid Monero JSONRPC response");
    auto node = response->m_result.get();
    monero_account res;
    bool found_index = false;
    bool address_found = false;
    
    for (auto it = node.begin(); it != node.end(); ++it) {
      std::string key = it->first;

      if (key == std::string("account_index")) {
        found_index = true;
        res.m_index = it->second.get_value<uint32_t>();
      }
      else if (key == std::string("address")) {
        address_found = true;
        res.m_primary_address = it->second.data();
      }
    }

    if (!found_index || !address_found) throw std::runtime_error("Could not create account");

    return res;
  }

  std::vector<monero_subaddress> get_subaddresses(const uint32_t account_idx, const std::vector<uint32_t>& subaddress_indices, bool skip_balances) const {
    throw std::runtime_error("get_subaddresses() not supported");
  }

  std::vector<monero_subaddress> get_subaddresses(uint32_t account_idx, const std::vector<uint32_t>& subaddress_indices) const override {
    return get_subaddresses(account_idx, subaddress_indices, false);
  }

  std::vector<monero_subaddress> get_subaddresses(const uint32_t account_idx) const override {
    std::vector<uint32_t> subaddress_indices;
    return get_subaddresses(account_idx, subaddress_indices);
  }

  monero_subaddress get_subaddress(const uint32_t account_idx, const uint32_t subaddress_idx) const override {
    std::vector<uint32_t> subaddress_indices;
    subaddress_indices.push_back(subaddress_idx);
    auto subaddresses = get_subaddresses(account_idx, subaddress_indices);
    if (subaddresses.empty()) throw std::runtime_error("Subaddress is not initialized");
    if (subaddresses.size() != 1) throw std::runtime_error("Only 1 subaddress should be returned");
    return subaddresses[0];
  }

  monero_subaddress create_subaddress(uint32_t account_idx, const std::string& label = "") override {
    auto params = std::make_shared<PyMoneroCreateSubaddressParams>(account_idx, label);
    PyMoneroJsonRequest request("create_address", params);
    auto response = m_rpc->send_json_request(request);
    if (response->m_result == boost::none) throw std::runtime_error("Invalid Monero JSONRPC response");
    auto node = response->m_result.get();
    monero_subaddress sub;
    sub.m_account_index = account_idx;
    sub.m_label = label;
    sub.m_balance = 0;
    sub.m_unlocked_balance = 0;
    sub.m_num_unspent_outputs = 0;
    sub.m_is_used = false;
    sub.m_num_blocks_to_unlock = 0;

    for(auto it = node.begin(); it != node.end(); ++it) {
      std::string key = it->first;
      if (key == std::string("address_index")) sub.m_index = it->second.get_value<uint32_t>();
      else if (key == std::string("address")) sub.m_address = it->second.data();
    }

    return sub;
  }

  void set_subaddress_label(uint32_t account_idx, uint32_t subaddress_idx, const std::string& label = "") override {
    auto params = std::make_shared<PyMoneroSetSubaddressLabelParams>(account_idx, subaddress_idx, label);
    PyMoneroJsonRequest request("label_address", params);
    m_rpc->send_json_request(request);
  }

  std::string export_outputs(bool all = false) const override {
    auto params = std::make_shared<PyMoneroImportExportOutputsParams>(all);
    PyMoneroJsonRequest request("export_outputs", params);
    auto response = m_rpc->send_json_request(request);
    if (response->m_result == boost::none) throw std::runtime_error("Invalid Monero JSONRPC response");
    auto node = response->m_result.get();

    for (auto it = node.begin(); it != node.end(); ++it) {
      std::string key = it->first;

      if (key == std::string("outputs_data_hex")) return it->second.data();
    }

    throw std::runtime_error("Could not get outputs hex");
  }

  int import_outputs(const std::string& outputs_hex) override {
    auto params = std::make_shared<PyMoneroImportExportOutputsParams>(outputs_hex);
    PyMoneroJsonRequest request("import_outputs", params);
    auto response = m_rpc->send_json_request(request);
    if (response->m_result == boost::none) throw std::runtime_error("Invalid Monero JSONRPC response");
    auto node = response->m_result.get();

    for (auto it = node.begin(); it != node.end(); ++it) {
      std::string key = it->first;

      if (key == std::string("num_imported")) return it->second.get_value<int>();
    }

    return 0;
  }

  std::vector<std::shared_ptr<monero_key_image>> export_key_images(bool all = false) const override {
    auto params = std::make_shared<PyMoneroImportExportKeyImagesParams>(all);
    PyMoneroJsonRequest request("export_key_images", params);
    auto response = m_rpc->send_json_request(request);
    if (response->m_result == boost::none) throw std::runtime_error("Invalid Monero JSONRPC response");
    auto node = response->m_result.get();
    std::vector<std::shared_ptr<monero::monero_key_image>> key_images;
    PyMoneroKeyImage::from_property_tree(node, key_images);
    return key_images;
  }
  
  std::shared_ptr<monero_key_image_import_result> import_key_images(const std::vector<std::shared_ptr<monero_key_image>>& key_images) override {
    auto params = std::make_shared<PyMoneroImportExportKeyImagesParams>(key_images);
    PyMoneroJsonRequest request("import_key_images", params);
    auto response = m_rpc->send_json_request(request);
    if (response->m_result == boost::none) throw std::runtime_error("Invalid Monero JSONRPC response");
    auto node = response->m_result.get();
    auto import_result = std::make_shared<monero_key_image_import_result>();
    PyMoneroKeyImageImportResult::from_property_tree(node, import_result);
    return import_result;
  }

  void freeze_output(const std::string& key_image) override {
    auto params = std::make_shared<PyMoneroQueryOutputParams>(key_image);
    PyMoneroJsonRequest request("freeze", params);
    m_rpc->send_json_request(request);
  }

  void thaw_output(const std::string& key_image) override {
    auto params = std::make_shared<PyMoneroQueryOutputParams>(key_image);
    PyMoneroJsonRequest request("thaw", params);
    m_rpc->send_json_request(request);
  }

  bool is_output_frozen(const std::string& key_image) override {
    auto params = std::make_shared<PyMoneroQueryOutputParams>(key_image);
    PyMoneroJsonRequest request("frozen", params);
    auto response = m_rpc->send_json_request(request);
    if (response->m_result == boost::none) throw std::runtime_error("Invalid Monero JSONRPC response");
    auto node = response->m_result.get();

    for(auto it = node.begin(); it != node.end(); ++it) {
      std::string key = it->first;

      if (key == std::string("frozen")) return it->second.get_value<bool>();
    }

    throw std::runtime_error("Could not get output");
  }

  monero_tx_priority get_default_fee_priority() const override {
    PyMoneroJsonRequest request("get_default_fee_priority");
    auto response = m_rpc->send_json_request(request);
    if (response->m_result == boost::none) throw std::runtime_error("Invalid Monero JSONRPC response");
    auto node = response->m_result.get();

    for(auto it = node.begin(); it != node.end(); ++it) {
      std::string key = it->first;

      if (key == std::string("priority")) {
        int priority = it->second.get_value<int>();

        if (priority == 0) return monero_tx_priority::DEFAULT;
        else if (priority == 1) return monero_tx_priority::UNIMPORTANT;
        else if (priority == 2) return monero_tx_priority::NORMAL; 
        else if (priority == 3) return monero_tx_priority::ELEVATED; 
      }
    }

    throw std::runtime_error("Could not get default fee priority");
  }

  std::vector<std::shared_ptr<monero_tx_wallet>> create_txs(const monero_tx_config& conf) override {
    // validate, copy, and normalize request
    monero_tx_config config = conf;
    if (config.m_destinations.empty()) throw std::runtime_error("Destinations cannot be empty");
    if (config.m_sweep_each_subaddress != boost::none) throw std::runtime_error("Sweep each subaddress not supported");
    if (config.m_below_amount != boost::none) throw std::runtime_error("Below amount not supported");
    
    if (config.m_can_split == boost::none) {
      config = config.copy();
      config.m_can_split = true;
    }
    if (config.m_relay == true && is_multisig()) throw std::runtime_error("Cannot relay multisig transaction until co-signed");
    
    // determine account and subaddresses to send from
    if (config.m_account_index == boost::none) throw std::runtime_error("Must specify the account index to send from");
    auto account_idx = config.m_account_index.get();

    // cannot apply subtractFeeFrom with `transfer_split` call
    if (config.m_can_split && config.m_subtract_fee_from.size() > 0) {
      throw std::runtime_error("subtractfeefrom transfers cannot be split over multiple transactions yet");
    }

    // build request parameters
    auto params = std::make_shared<PyMoneroTransferParams>(config);
    std::string request_path = "transfer";
    if (config.m_can_split) request_path = "transfer_split";

    PyMoneroJsonRequest request(request_path, params);
    auto response = m_rpc->send_json_request(request);
    if (response->m_result == boost::none) throw std::runtime_error("Invalid Monero JSONRPC response");
    auto node = response->m_result.get();

    // pre-initialize txs iff present. multisig and view-only wallets will have tx set without transactions
    std::vector<std::shared_ptr<monero_tx_wallet>> txs;
    int num_txs = 0;
    
    for(auto it = node.begin(); it != node.end(); ++it) {
      std::string key = it->first;

      if (config.m_can_split && key == std::string("fee_list")) {
        auto fee_list_node = it->second;

        for(auto it2 = fee_list_node.begin(); it2 != fee_list_node.end(); ++it2) {
          num_txs++;
        }
      }
    }
        
    bool copy_destinations = num_txs == 1;
    for (int i = 0; i < num_txs; i++) {
      auto tx = std::make_shared<monero::monero_tx_wallet>();
      PyMoneroTxWallet::init_sent(config, tx, copy_destinations);
      tx->m_outgoing_transfer.get()->m_account_index = account_idx;

      if (config.m_subaddress_indices.size() == 1) {
        tx->m_outgoing_transfer.get()->m_subaddress_indices = config.m_subaddress_indices;
      }

      txs.push_back(tx);
    }
    
    // notify of changes
    if (config.m_relay) poll();
    
    // initialize tx set from rpc response with pre-initialized txs
    auto tx_set = std::make_shared<monero::monero_tx_set>();
    if (config.m_can_split) {
      PyMoneroTxSet::from_sent_txs(node, tx_set, txs, config);
    }
    else {
      if (txs.empty()) {
        auto __tx = std::make_shared<monero::monero_tx_wallet>();
        PyMoneroTxSet::from_tx(node, tx_set, __tx, true, config);
      }
      else {
        PyMoneroTxSet::from_tx(node, tx_set, txs[0], true, config);
      }
    }

    return tx_set->m_txs;
  }

  std::shared_ptr<monero_tx_wallet> sweep_output(const monero_tx_config& config) override {
    auto params = std::make_shared<PyMoneroSweepParams>(config);
    PyMoneroJsonRequest request("sweep_single", params);
    auto response = m_rpc->send_json_request(request);
    if (response->m_result == boost::none) throw std::runtime_error("Invalid Monero JSONRPC response");
    auto node = response->m_result.get();
    if (config.m_relay) poll();
    auto set = std::make_shared<monero_tx_set>();
    auto tx = std::make_shared<monero::monero_tx_wallet>();
    PyMoneroTxWallet::init_sent(config, tx, true);
    PyMoneroTxSet::from_tx(node, set, tx, true, config);
    return tx;
  }

  std::vector<std::shared_ptr<monero_tx_wallet>> sweep_dust(bool relay = false) override {
    auto params = std::make_shared<PyMoneroSweepParams>(relay);
    PyMoneroJsonRequest request("sweep_dust", params);
    auto response = m_rpc->send_json_request(request);
    if (response->m_result == boost::none) throw std::runtime_error("Invalid Monero JSONRPC response");
    auto node = response->m_result.get();
    auto set = std::make_shared<monero_tx_set>();
    PyMoneroTxSet::from_sent_txs(node, set);
    return set->m_txs;
  }

  std::vector<std::string> relay_txs(const std::vector<std::string>& tx_metadatas) override {
    if (tx_metadatas.empty()) throw std::runtime_error("Must provide an array of tx metadata to relay");
  
    std::vector<std::string> tx_hashes;

    for (const auto &tx_metadata : tx_metadatas) {
      auto params = std::make_shared<PyMoneroWalletRelayTxParams>(tx_metadata);
      PyMoneroJsonRequest request("relay_tx", params);
      auto response = m_rpc->send_json_request(request);
      if (response->m_result == boost::none) throw std::runtime_error("Invalid Monero JSONRPC response");
      auto node = response->m_result.get();

      for (auto it = node.begin(); it != node.end(); ++it) {
        std::string key = it->first;
        if (key == std::string("tx_hash")) tx_hashes.push_back(it->second.data());
      }
    }

    return tx_hashes;
  }

  monero_tx_set describe_tx_set(const monero_tx_set& tx_set) override {
    auto params = std::make_shared<PyMoneroSignDescribeTransferParams>();
    params->m_multisig_txset = tx_set.m_multisig_tx_hex;
    params->m_unsigned_txset = tx_set.m_unsigned_tx_hex;
    PyMoneroJsonRequest request("describe_transfer", params);
    auto response = m_rpc->send_json_request(request);
    if (response->m_result == boost::none) throw std::runtime_error("Invalid Monero JSONRPC response");
    auto node = response->m_result.get();
    auto set = std::make_shared<monero_tx_set>();
    PyMoneroTxSet::from_describe_transfer(node, set);
    return *set;
  }

  monero_tx_set sign_txs(const std::string& unsigned_tx_hex) override {
    auto params = std::make_shared<PyMoneroSignDescribeTransferParams>(unsigned_tx_hex);
    PyMoneroJsonRequest request("sign_transfer", params);
    auto response = m_rpc->send_json_request(request);
    if (response->m_result == boost::none) throw std::runtime_error("Invalid Monero JSONRPC response");
    auto node = response->m_result.get();
    auto set = std::make_shared<monero_tx_set>();
    PyMoneroTxSet::from_sent_txs(node, set);
    return *set;
  }

  std::vector<std::string> submit_txs(const std::string& signed_tx_hex) override {
    auto params = std::make_shared<PyMoneroSubmitTransferParams>(signed_tx_hex);
    PyMoneroJsonRequest request("submit_transfer", params);
    auto response = m_rpc->send_json_request(request);
    if (response->m_result == boost::none) throw std::runtime_error("Invalid Monero JSONRPC response");
    auto node = response->m_result.get();
    poll();
    std::vector<std::string> hashes;

    for (auto it = node.begin(); it != node.end(); ++it) {
      std::string key = it->first;

      if (key == std::string("tx_hash_list")) {
        auto hashes_node = it->second;

        for (auto it2 = hashes_node.begin(); it2 != hashes_node.end(); ++it2) {
          hashes.push_back(it2->second.data());
        }
      }
    }

    return hashes;
  }

  std::string sign_message(const std::string& msg, monero_message_signature_type signature_type, uint32_t account_idx = 0, uint32_t subaddress_idx = 0) const override {
    auto params = std::make_shared<PyMoneroVerifySignMessageParams>(msg, signature_type, account_idx, subaddress_idx);
    PyMoneroJsonRequest request("sign", params);
    auto response = m_rpc->send_json_request(request);
    if (response->m_result == boost::none) throw std::runtime_error("Invalid Monero JSONRPC response");
    auto node = response->m_result.get();
    return PyMoneroReserveProofSignature::from_property_tree(node);
  }

  monero_message_signature_result verify_message(const std::string& msg, const std::string& address, const std::string& signature) const override {
    auto params = std::make_shared<PyMoneroVerifySignMessageParams>(msg, address, signature);
    PyMoneroJsonRequest request("verify", params);
    auto response = m_rpc->send_json_request(request);
    if (response->m_result == boost::none) throw std::runtime_error("Invalid Monero JSONRPC response");
    auto node = response->m_result.get();
    auto sig_result = std::make_shared<monero_message_signature_result>();
    PyMoneroMessageSignatureResult::from_property_tree(node, sig_result);
    return *sig_result;
  }

  std::string get_tx_key(const std::string& tx_hash) const override {
    auto params = std::make_shared<PyMoneroCheckTxKeyParams>(tx_hash);
    PyMoneroJsonRequest request("get_tx_key", params);
    auto response = m_rpc->send_json_request(request);
    if (response->m_result == boost::none) throw std::runtime_error("Invalid Monero JSONRPC response");
    auto node = response->m_result.get();
    for (auto it = node.begin(); it != node.end(); ++it) {
      std::string key = it->first;

      if (key == std::string("tx_key")) {
        return it->second.data();
      }
    }

    throw std::runtime_error("Could not get tx key");
  }

  std::shared_ptr<monero_check_tx> check_tx_key(const std::string& tx_hash, const std::string& tx_key, const std::string& address) const override {
    auto params = std::make_shared<PyMoneroCheckTxKeyParams>(tx_hash, tx_key, address);
    PyMoneroJsonRequest request("check_tx_key", params);
    auto response = m_rpc->send_json_request(request);
    if (response->m_result == boost::none) throw std::runtime_error("Invalid Monero JSONRPC response");
    auto node = response->m_result.get();
    auto check = std::make_shared<monero::monero_check_tx>();
    PyMoneroCheckTxProof::from_property_tree(node, check);
    return check;
  }

  std::string get_tx_proof(const std::string& tx_hash, const std::string& address, const std::string& message) const override {
    auto params = std::make_shared<PyMoneroReserveProofParams>(tx_hash, message);
    params->m_address = address;
    PyMoneroJsonRequest request("get_tx_proof", params);
    auto response = m_rpc->send_json_request(request);
    if (response->m_result == boost::none) throw std::runtime_error("Invalid Monero JSONRPC response");
    auto node = response->m_result.get();
    return PyMoneroReserveProofSignature::from_property_tree(node);
  }

  std::shared_ptr<monero_check_tx> check_tx_proof(const std::string& tx_hash, const std::string& address, const std::string& message, const std::string& signature) const {
    auto params = std::make_shared<PyMoneroReserveProofParams>(tx_hash, address, message, signature);
    PyMoneroJsonRequest request("check_tx_proof", params);
    auto response = m_rpc->send_json_request(request);
    if (response->m_result == boost::none) throw std::runtime_error("Invalid Monero JSONRPC response");
    auto node = response->m_result.get();
    auto check = std::make_shared<monero::monero_check_tx>();
    PyMoneroCheckTxProof::from_property_tree(node, check);
    return check;
  }

  std::string get_spend_proof(const std::string& tx_hash, const std::string& message) const override {
    auto params = std::make_shared<PyMoneroReserveProofParams>(tx_hash, message);
    PyMoneroJsonRequest request("get_spend_proof", params);
    auto response = m_rpc->send_json_request(request);
    if (response->m_result == boost::none) throw std::runtime_error("Invalid Monero JSONRPC response");
    auto node = response->m_result.get();
    return PyMoneroReserveProofSignature::from_property_tree(node);
  }

  bool check_spend_proof(const std::string& tx_hash, const std::string& message, const std::string& signature) const override {
    auto params = std::make_shared<PyMoneroReserveProofParams>(tx_hash, message, signature);
    PyMoneroJsonRequest request("check_spend_proof", params);
    auto response = m_rpc->send_json_request(request);
    if (response->m_result == boost::none) throw std::runtime_error("Invalid Monero JSONRPC response");
    auto node = response->m_result.get();
    auto proof = std::make_shared<monero::monero_check_reserve>();
    PyMoneroCheckReserve::from_property_tree(node, proof);
    return proof->m_is_good;
  }

  std::string get_reserve_proof_wallet(const std::string& message) const override {
    auto params = std::make_shared<PyMoneroReserveProofParams>(message);
    PyMoneroJsonRequest request("get_reserve_proof", params);
    auto response = m_rpc->send_json_request(request);
    if (response->m_result == boost::none) throw std::runtime_error("Invalid Monero JSONRPC response");
    auto node = response->m_result.get();
    return PyMoneroReserveProofSignature::from_property_tree(node);
  }

  std::string get_reserve_proof_account(uint32_t account_idx, uint64_t amount, const std::string& message) const override {
    auto params = std::make_shared<PyMoneroReserveProofParams>(account_idx, amount, message);
    PyMoneroJsonRequest request("get_reserve_proof", params);
    auto response = m_rpc->send_json_request(request);
    if (response->m_result == boost::none) throw std::runtime_error("Invalid Monero JSONRPC response");
    auto node = response->m_result.get();
    return PyMoneroReserveProofSignature::from_property_tree(node);
  }

  std::shared_ptr<monero_check_reserve> check_reserve_proof(const std::string& address, const std::string& message, const std::string& signature) const override {
    auto params = std::make_shared<PyMoneroReserveProofParams>(address, message, signature);
    PyMoneroJsonRequest request("check_reserve_proof", params);
    auto response = m_rpc->send_json_request(request);
    if (response->m_result == boost::none) throw std::runtime_error("Invalid Monero JSONRPC response");
    auto node = response->m_result.get();
    auto proof = std::make_shared<monero::monero_check_reserve>();
    PyMoneroCheckReserve::from_property_tree(node, proof);
    return proof;
  }

  std::vector<std::string> get_tx_notes(const std::vector<std::string>& tx_hashes) const override {
    auto params = std::make_shared<PyMoneroTxNotesParams>(tx_hashes);
    PyMoneroJsonRequest request("get_tx_notes", params);
    auto response = m_rpc->send_json_request(request);
    if (response->m_result == boost::none) throw std::runtime_error("Invalid Monero JSONRPC response");
    auto node = response->m_result.get();
    std::vector<std::string> notes;

    for (auto it = node.begin(); it != node.end(); ++it) {
      std::string key = it->first;

      if (key == std::string("notes")) {
        auto notes_node = it->second;

        for (auto it2 = notes_node.begin(); it2 != notes_node.end(); ++it2) {
          notes.push_back(it2->second.data());
        }
      }
    }

    return notes;
  }

  void set_tx_notes(const std::vector<std::string>& tx_hashes, const std::vector<std::string>& notes) override {
    auto params = std::make_shared<PyMoneroTxNotesParams>(tx_hashes, notes);
    PyMoneroJsonRequest request("set_tx_notes", params);
    m_rpc->send_json_request(request);
  }

  std::vector<monero_address_book_entry> get_address_book_entries(const std::vector<uint64_t>& indices) const override {
    auto params = std::make_shared<PyMoneroAddressBookEntryParams>(indices);
    PyMoneroJsonRequest request("get_address_book", params);
    auto response = m_rpc->send_json_request(request);
    if (response->m_result == boost::none) throw std::runtime_error("Invalid Monero JSONRPC response");
    auto node = response->m_result.get();
    std::vector<std::shared_ptr<monero_address_book_entry>> entries_ptr;
    PyMoneroAddressBookEntry::from_property_tree(node, entries_ptr);
    std::vector<monero_address_book_entry> entries;

    for (const auto &entry : entries_ptr) {
      entries.push_back(*entry);
    }

    return entries;
  }

  uint64_t add_address_book_entry(const std::string& address, const std::string& description) override {
    auto params = std::make_shared<PyMoneroAddressBookEntryParams>(address, description);
    PyMoneroJsonRequest request("add_address_book", params);
    auto response = m_rpc->send_json_request(request);
    if (response->m_result == boost::none) throw std::runtime_error("Invalid Monero JSONRPC response");
    auto node = response->m_result.get();

    for (auto it = node.begin(); it != node.end(); ++it) {
      std::string key = it->first;

      if (key == std::string("index")) {
        return it->second.get_value<uint64_t>();
      }
    }

    throw std::runtime_error("Invalid response from wallet rpc");
  }

  void edit_address_book_entry(uint64_t index, bool set_address, const std::string& address, bool set_description, const std::string& description) override {
    auto params = std::make_shared<PyMoneroAddressBookEntryParams>(index, set_address, address, set_description, description);
    PyMoneroJsonRequest request("edit_address_book", params);
    m_rpc->send_json_request(request);
  }

  void delete_address_book_entry(uint64_t index) override {
    auto params = std::make_shared<PyMoneroAddressBookEntryParams>(index);
    PyMoneroJsonRequest request("delete_address_book", params);
    m_rpc->send_json_request(request);
  }

  void tag_accounts(const std::string& tag, const std::vector<uint32_t>& account_indices) override {
    auto params = std::make_shared<PyMoneroTagAccountsParams>(tag, account_indices);
    PyMoneroJsonRequest request("tag_accounts", params);
    m_rpc->send_json_request(request);
  }

  void untag_accounts(const std::vector<uint32_t>& account_indices) override {
    auto params = std::make_shared<PyMoneroTagAccountsParams>(account_indices);
    PyMoneroJsonRequest request("untag_accounts", params);
    m_rpc->send_json_request(request);
  }

  std::vector<std::shared_ptr<PyMoneroAccountTag>> get_account_tags() override {
    PyMoneroJsonRequest request("get_account_tags");
    std::shared_ptr<PyMoneroJsonResponse> response = m_rpc->send_json_request(request);
    if (response->m_result == boost::none) throw std::runtime_error("Invalid Monero JSONRPC response");
    auto res = response->m_result.get();
    std::vector<std::shared_ptr<PyMoneroAccountTag>> account_tags;
    PyMoneroAccountTag::from_property_tree(res, account_tags);
    return account_tags;
  }

  void set_account_tag_label(const std::string& tag, const std::string& label) override {
    auto params = std::make_shared<PyMoneroSetAccountTagDescriptionParams>(tag, label);
    PyMoneroJsonRequest request("set_account_tag_description", params);
    m_rpc->send_json_request(request);
  }

  std::string get_payment_uri(const monero_tx_config& config) const override {
    auto params = std::make_shared<PyMoneroGetPaymentUriParams>(config);
    PyMoneroJsonRequest request("make_uri", params);
    std::shared_ptr<PyMoneroJsonResponse> response = m_rpc->send_json_request(request);
    if (response->m_result == boost::none) throw std::runtime_error("Invalid Monero JSONRPC response");
    auto res = response->m_result.get();
    return PyMoneroGetPaymentUriResponse::from_property_tree(res);
  }

  std::shared_ptr<monero_tx_config> parse_payment_uri(const std::string& uri) const {
    auto params = std::make_shared<PyMoneroParsePaymentUriParams>(uri);
    PyMoneroJsonRequest request("parse_uri", params);
    std::shared_ptr<PyMoneroJsonResponse> response = m_rpc->send_json_request(request);
    if (response->m_result == boost::none) throw std::runtime_error("Invalid Monero JSONRPC response");
    auto res = response->m_result.get();
    auto uri_response = std::make_shared<PyMoneroParsePaymentUriResponse>();
    PyMoneroParsePaymentUriResponse::from_property_tree(res, uri_response);
    return uri_response->to_tx_config();
  }

  void set_attribute(const std::string& key, const std::string& val) override {
    auto params = std::make_shared<PyMoneroWalletAttributeParams>(key, val);
    PyMoneroJsonRequest request("set_attribute");
    std::shared_ptr<PyMoneroJsonResponse> response = m_rpc->send_json_request(request);
  }

  bool get_attribute(const std::string& key, std::string& value) const override {
    try {
      auto params = std::make_shared<PyMoneroWalletAttributeParams>(key);
      PyMoneroJsonRequest request("get_attribute");
      std::shared_ptr<PyMoneroJsonResponse> response = m_rpc->send_json_request(request);
      if (response->m_result == boost::none) throw std::runtime_error("Invalid Monero JSONRPC response");
      auto res = response->m_result.get();
      PyMoneroWalletAttributeParams::from_property_tree(res, params);
      if (params->m_value == boost::none) return false;
      value = params->m_value.get();
      return true;
    }
    catch (...) {
      return false;
    }
  }

  void start_mining(boost::optional<uint64_t> num_threads, boost::optional<bool> background_mining, boost::optional<bool> ignore_battery) override {
    auto params = std::make_shared<PyMoneroWalletStartMiningParams>(num_threads.value_or(0), background_mining.value_or(false), ignore_battery.value_or(false));
    PyMoneroJsonRequest request("start_mining", params);
    auto response = m_rpc->send_json_request(request);
    PyMoneroDaemonRpc::check_response_status(response);
  }

  void stop_mining() override {
    PyMoneroJsonRequest request("stop_mining");
    m_rpc->send_json_request(request);
  }

  bool is_multisig_import_needed() const override {
    PyMoneroJsonRequest request("get_balance");
    auto response = m_rpc->send_json_request(request);
    if (response->m_result == boost::none) throw std::runtime_error("Invalid Monero JSONRPC response");
    auto res = response->m_result.get();
    auto balance = std::make_shared<PyMoneroGetBalanceResponse>();
    PyMoneroGetBalanceResponse::from_property_tree(res, balance);
    if (balance->m_multisig_import_needed) return true;
    return false;
  }

  monero_multisig_info get_multisig_info() const override {
    PyMoneroJsonRequest request("is_multisig");
    auto response = m_rpc->send_json_request(request);
    if (response->m_result == boost::none) throw std::runtime_error("Invalid Monero JSONRPC response");
    auto res = response->m_result.get();
    auto info = std::make_shared<monero::monero_multisig_info>();
    PyMoneroMultisigInfo::from_property_tree(res, info);
    return *info;
  }

  std::string prepare_multisig() override {
    auto params = std::make_shared<PyMoneroPrepareMultisigParams>();
    PyMoneroJsonRequest request("prepare_multisig", params);
    auto response = m_rpc->send_json_request(request);
    clear_address_cache();
    if (response->m_result == boost::none) throw std::runtime_error("Invalid Monero JSONRPC response");
    auto res = response->m_result.get();
    return PyMoneroPrepareMakeMultisigResponse::from_property_tree(res);
  }

  std::string make_multisig(const std::vector<std::string>& multisig_hexes, int threshold, const std::string& password) override {
    auto params = std::make_shared<PyMoneroMakeMultisigParams>(multisig_hexes, threshold, password);
    PyMoneroJsonRequest request("make_multisig", params);
    auto response = m_rpc->send_json_request(request);
    clear_address_cache();
    if (response->m_result == boost::none) throw std::runtime_error("Invalid Monero JSONRPC response");
    auto res = response->m_result.get();
    return PyMoneroPrepareMakeMultisigResponse::from_property_tree(res);
  }

  monero_multisig_init_result exchange_multisig_keys(const std::vector<std::string>& multisig_hexes, const std::string& password) {
    auto params = std::make_shared<PyMoneroExchangeMultisigKeysParams>(multisig_hexes, password);
    PyMoneroJsonRequest request("exchange_multisig_keys", params);
    auto response = m_rpc->send_json_request(request);
    clear_address_cache();
    if (response->m_result == boost::none) throw std::runtime_error("Invalid Monero JSONRPC response");
    auto res = response->m_result.get();
    auto multisig_init = std::make_shared<monero_multisig_init_result>();
    PyMoneroMultisigInitResult::from_property_tree(res, multisig_init);
    return *multisig_init;
  }

  std::string export_multisig_hex() override {
    PyMoneroJsonRequest request("export_multisig_info");
    auto response = m_rpc->send_json_request(request);
    if (response->m_result == boost::none) throw std::runtime_error("Invalid Monero JSONRPC response");
    auto res = response->m_result.get();
    return PyMoneroExportMultisigHexResponse::from_property_tree(res);
  }
  
  int import_multisig_hex(const std::vector<std::string>& multisig_hexes) override {
    auto params = std::make_shared<PyMoneroImportMultisigHexParams>(multisig_hexes);
    PyMoneroJsonRequest request("import_multisig_info", params);
    auto response = m_rpc->send_json_request(request);
    if (response->m_result == boost::none) throw std::runtime_error("Invalid Monero JSONRPC response");
    auto res = response->m_result.get();
    return PyMoneroImportMultisigHexResponse::from_property_tree(res);
  }

  monero_multisig_sign_result sign_multisig_tx_hex(const std::string& multisig_tx_hex) override {
    auto params = std::make_shared<PyMoneroMultisigTxDataParams>(multisig_tx_hex);
    PyMoneroJsonRequest request("sign_multisig", params);
    auto response = m_rpc->send_json_request(request);
    if (response->m_result == boost::none) throw std::runtime_error("Invalid Monero JSONRPC response");
    auto res = response->m_result.get();
    auto multisig_result = std::make_shared<monero::monero_multisig_sign_result>();
    PyMoneroMultisigSignResult::from_property_tree(res, multisig_result);
    return *multisig_result;
  }

  std::vector<std::string> submit_multisig_tx_hex(const std::string& signed_multisig_tx_hex) {
    auto params = std::make_shared<PyMoneroMultisigTxDataParams>(signed_multisig_tx_hex);
    PyMoneroJsonRequest request("submit_multisig", params);
    auto response = m_rpc->send_json_request(request);
    if (response->m_result == boost::none) throw std::runtime_error("Invalid Monero JSONRPC response");
    auto res = response->m_result.get();
    return PyMoneroSubmitMultisigTxHexResponse::from_property_tree(res);
  }

  void change_password(const std::string& old_password, const std::string& new_password) override {
    auto params = std::make_shared<PyMoneroChangeWalletPasswordParams>(old_password, new_password);
    PyMoneroJsonRequest request("change_wallet_password", params);
    m_rpc->send_json_request(request);
  }

  void save() override {
    PyMoneroJsonRequest request("store");
    m_rpc->send_json_request(request);
  }

  void close(bool save = false) override {
    auto params = std::make_shared<PyMoneroCloseWalletParams>(save);
    PyMoneroJsonRequest request("close_wallet", params);
    m_rpc->send_json_request(request);
  }

  std::shared_ptr<PyMoneroWalletBalance> get_balances(boost::optional<uint32_t> account_idx, boost::optional<uint32_t> subaddress_idx) const override {
    auto balance = std::make_shared<PyMoneroWalletBalance>();

    if (account_idx == boost::none) {
      if (subaddress_idx != boost::none) throw std::runtime_error("Must provide account index with subaddress index");
    
      auto accounts = monero::monero_wallet::get_accounts();

      for(const auto &account : accounts) {
        balance->m_balance += account.m_balance.get();
        balance->m_unlocked_balance += account.m_unlocked_balance.get();
      }

      return balance;
    }
    else {
      auto params = std::make_shared<PyMoneroGetBalanceParams>(account_idx.get(), subaddress_idx);
      PyMoneroJsonRequest request("get_balance", params);
      auto response = m_rpc->send_json_request(request);
      if (response->m_result == boost::none) throw std::runtime_error("Invalid Monero JSONRPC response");
      auto res = response->m_result.get();
      auto bal_res = std::make_shared<PyMoneroGetBalanceResponse>();
      PyMoneroGetBalanceResponse::from_property_tree(res, bal_res);

      if (subaddress_idx == boost::none) {
        balance->m_balance = bal_res->m_balance.get();
        balance->m_unlocked_balance = bal_res->m_unlocked_balance.get();
        return balance;
      }
      else if (bal_res->m_per_subaddress.size() > 0) {
        auto sub = bal_res->m_per_subaddress[0];
        balance->m_balance = sub->m_balance.get();
        balance->m_unlocked_balance = sub->m_unlocked_balance.get();
      }
    }

    return balance;
  }

protected:
  inline static const uint64_t DEFAULT_SYNC_PERIOD_IN_MS = 20000;
  boost::optional<uint64_t> m_sync_period_in_ms;
  std::string m_path = "";
  std::shared_ptr<PyMoneroRpcConnection> m_rpc;
  std::shared_ptr<PyMoneroRpcConnection> m_daemon_connection;
  std::shared_ptr<PyMoneroWalletPoller> m_poller;

  mutable boost::recursive_mutex m_sync_mutex;
  serializable_unordered_map<uint32_t, serializable_unordered_map<uint32_t, std::string>> m_address_cache;
  
  PyMoneroWalletRpc* create_wallet_random(const std::shared_ptr<PyMoneroWalletConfig> &conf) {
    // validate and normalize config
    auto config = conf->copy();
    if (config.m_seed_offset != boost::none) throw std::runtime_error("Cannot specify seed offset when creating random wallet");
    if (config.m_restore_height != boost::none) throw std::runtime_error("Cannot specify restore height when creating random wallet");
    if (config.m_save_current != boost::none && config.m_save_current == false) throw std::runtime_error("Current wallet is saved automatically when creating random wallet");
    if (config.m_path == boost::none || config.m_path->empty()) throw std::runtime_error("Wallet name is not initialized");
    if (config.m_language == boost::none || config.m_language->empty()) config.m_language = "English";

    // send request
    std::string filename = config.m_path.get();
    std::string password = config.m_password.get();
    std::string language = config.m_language.get();

    auto params = std::make_shared<PyMoneroCreateOpenWalletParams>(filename, password, language);
    PyMoneroJsonRequest request("create_wallet", params);
    m_rpc->send_json_request(request);
    clear();
    m_path = config.m_path.get();
    return this;
  }

  PyMoneroWalletRpc* create_wallet_from_seed(const std::shared_ptr<PyMoneroWalletConfig> &conf) {
    auto config = conf->copy();
    if (config.m_language == boost::none || config.m_language->empty()) config.m_language = "English";
    std::string filename = config.m_path.get();
    std::string password = config.m_password.get();
    std::string seed = config.m_seed.get();
    std::string seed_offset = config.m_seed_offset.get();
    uint64_t restore_height = config.m_restore_height.get();
    std::string language = config.m_language.get();
    bool autosave_current = false;
    bool enable_multisig_experimental = false;
    if (config.m_save_current != boost::none) autosave_current = config.m_save_current.get();
    if (config.m_is_multisig != boost::none) enable_multisig_experimental = config.m_is_multisig.get();
    auto params = std::make_shared<PyMoneroCreateOpenWalletParams>(filename, password, seed, seed_offset, restore_height, language, autosave_current, enable_multisig_experimental);
    PyMoneroJsonRequest request("restore_deterministic_wallet", params);
    m_rpc->send_json_request(request);
    clear();
    m_path = config.m_path.get();
    return this;
  }

  PyMoneroWalletRpc* create_wallet_from_keys(const std::shared_ptr<PyMoneroWalletConfig> &config) {
    if (config->m_seed_offset != boost::none) throw std::runtime_error("Cannot specify seed offset when creating wallet from keys");
    if (config->m_restore_height == boost::none) config->m_restore_height = 0;
    std::string filename = config->m_path.get();
    std::string password = config->m_password.get();
    std::string address = config->m_primary_address.get();
    std::string view_key = "";
    std::string spend_key = "";
    if (config->m_private_view_key != boost::none) view_key = config->m_private_view_key.get();
    if (config->m_private_spend_key != boost::none) spend_key = config->m_private_spend_key.get();
    uint64_t restore_height = config->m_restore_height.get();
    bool autosave_current = false;
    if (config->m_save_current != boost::none) autosave_current = config->m_save_current.get();
    auto params = std::make_shared<PyMoneroCreateOpenWalletParams>(filename, password, address, view_key, spend_key, restore_height, autosave_current);
    PyMoneroJsonRequest request("generate_from_keys", params);
    m_rpc->send_json_request(request);
    clear();
    m_path = config->m_path.get();
    return this;
  }

  std::string query_key(const std::string& key_type) const {
    auto params = std::make_shared<PyMoneroQueryKeyParams>(key_type);
    PyMoneroJsonRequest request("query_key", params);
    std::shared_ptr<PyMoneroJsonResponse> response = m_rpc->send_json_request(request);

    if (response->m_result == boost::none) throw std::runtime_error("Invalid Monero JSONRPC response");
    auto node = response->m_result.get();

    for (boost::property_tree::ptree::const_iterator it = node.begin(); it != node.end(); ++it) {
      std::string key = it->first;
      if (key == std::string("key")) return it->second.data();
    }

    throw std::runtime_error(std::string("Cloud not query key: ") + key_type);
  }

  std::vector<std::shared_ptr<monero_tx_wallet>> sweep_account(const monero_tx_config &conf) {
    auto config = conf.copy();
    if (config.m_account_index == boost::none) throw std::runtime_error("Must specify an account index to sweep from");
    if (config.m_destinations.size() != 1) throw std::runtime_error("Must specify exactly one destination to sweep to");
    if (config.m_destinations[0]->m_address == boost::none) throw std::runtime_error("Must specify destination address to sweep to");
    if (config.m_destinations[0]->m_amount != boost::none) throw std::runtime_error("Cannot specify amount in sweep request");
    if (config.m_key_image != boost::none) throw std::runtime_error("Key image defined; use sweepOutput() to sweep an output by its key image");
    //if (config.m_subaddress_indices.size() == 0) throw std::runtime_error("Empty list given for subaddresses indices to sweep");
    if (config.m_sweep_each_subaddress) throw std::runtime_error("Cannot sweep each subaddress with RPC `sweep_all`");
    if (config.m_subtract_fee_from.size() > 0) throw std::runtime_error("Sweeping output does not support subtracting fees from destinations");
    
    // sweep from all subaddresses if not otherwise defined
    if (config.m_subaddress_indices.empty()) {
      uint32_t account_idx = config.m_account_index.get();
      auto subaddresses = get_subaddresses(account_idx);
      for (const auto &subaddress : subaddresses) {
        config.m_subaddress_indices.push_back(subaddress.m_index.get());
      }
    }
    if (config.m_subaddress_indices.size() == 0) throw std::runtime_error("No subaddresses to sweep from");
    bool relay = config.m_relay == true;
    auto params = std::make_shared<PyMoneroSweepParams>(config);
    PyMoneroJsonRequest request("sweep_all", params);
    auto response = m_rpc->send_json_request(request);
    if (response->m_result == boost::none) throw std::runtime_error("Invalid Monero JSONRPC response");
    auto node = response->m_result.get();
    if (config.m_relay) poll();
    std::vector<std::shared_ptr<monero_tx_wallet>> txs;
    auto set = std::make_shared<monero_tx_set>();
    PyMoneroTxSet::from_sent_txs(node, set, txs, config);

    for (auto &tx : set->m_txs) {
      tx->m_is_locked = true;
      tx->m_is_confirmed = false;
      tx->m_num_confirmations = 0;
      tx->m_relay = relay;
      tx->m_in_tx_pool = relay;
      tx->m_is_relayed = relay;
      tx->m_is_miner_tx = false;
      tx->m_is_failed = false;
      tx->m_ring_size = monero_utils::RING_SIZE;
      auto transfer = tx->m_outgoing_transfer.get();
      transfer->m_account_index = config.m_account_index;
      if (config.m_subaddress_indices.size() == 1) 
      {
        transfer->m_subaddress_indices = config.m_subaddress_indices;
      }
      auto destination = std::make_shared<monero_destination>();
      destination->m_address = config.m_destinations[0]->m_address;
      destination->m_amount = config.m_destinations[0]->m_amount;
      std::vector<std::shared_ptr<monero_destination>> destinations;
      destinations.push_back(destination);
      transfer->m_destinations = destinations;
      tx->m_payment_id = config.m_payment_id;
      if (tx->m_unlock_time == boost::none) tx->m_unlock_time = 0;
      if (tx->m_relay) {
        if (tx->m_last_relayed_timestamp == boost::none) {
          //tx.setLastRelayedTimestamp(System.currentTimeMillis());  // TODO (monero-wallet-rpc): provide timestamp on response; unconfirmed timestamps vary
        }  
        if (tx->m_is_double_spend_seen == boost::none) tx->m_is_double_spend_seen = false;
      }
    }

    return set->m_txs;
  }

  void clear_address_cache() {
    m_address_cache.clear();
  }

  void refresh_listening() {
    if (m_rpc->m_zmq_uri == boost::none) {
      if (m_poller == nullptr && m_listeners.size() > 0) m_poller = std::make_shared<PyMoneroWalletPoller>(this);
      if (m_poller != nullptr) m_poller->set_is_polling(m_listeners.size() > 0);
    } 
    /*
    else {
      if (m_zmq_listener == nullptr && m_listeners.size() > 0) m_zmq_listener = std::make_shared<PyMoneroWalletRpcZmqListener>();
      if (m_zmq_listener != nullptr) m_zmq_listener.set_is_polling(m_listeners.size() > 0);
    }
    */
  }

  void poll() {
    if (m_poller != nullptr && m_poller->is_polling()) m_poller->poll(); 
  }

  void clear() {
    m_listeners.clear();
    refresh_listening();
    clear_address_cache();
    m_path = "";
  }
};
