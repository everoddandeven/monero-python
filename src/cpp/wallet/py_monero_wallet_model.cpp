#include "py_monero_wallet_model.h"
#include "utils/monero_utils.h"

void PyMoneroTxQuery::decontextualize(const std::shared_ptr<monero::monero_tx_query> &query) {
  query->m_is_incoming = boost::none;
  query->m_is_outgoing = boost::none;
  query->m_transfer_query = boost::none;
  query->m_input_query = boost::none;
  query->m_output_query = boost::none;
}

void PyMoneroTxQuery::decontextualize(monero::monero_tx_query &query) {
  query.m_is_incoming = boost::none;
  query.m_is_outgoing = boost::none;
  query.m_transfer_query = boost::none;
  query.m_input_query = boost::none;
  query.m_output_query = boost::none;
}

bool PyMoneroOutputQuery::is_contextual(const std::shared_ptr<monero::monero_output_query> &query) {
  if (query == nullptr) return false;
  return is_contextual(*query);
}

bool PyMoneroOutputQuery::is_contextual(const monero::monero_output_query &query) {
  if (query.m_tx_query == boost::none) return false;
  if (query.m_tx_query.get()->m_is_incoming != boost::none) return true;       // requires context of all transfers
  if (query.m_tx_query.get()->m_is_outgoing != boost::none) return true;
  if (query.m_tx_query.get()->m_transfer_query != boost::none) return true; // requires context of transfers
  return false;
}

bool PyMoneroTransferQuery::is_contextual(const std::shared_ptr<monero::monero_transfer_query> &query) {
  if (query == nullptr) return false;
  return is_contextual(*query);
}

bool PyMoneroTransferQuery::is_contextual(const monero::monero_transfer_query &query) {
  if (query.m_tx_query == boost::none) return false;
  if (query.m_tx_query.get()->m_is_incoming != boost::none) return true;       // requires context of all transfers
  if (query.m_tx_query.get()->m_is_outgoing != boost::none) return true;
  if (query.m_tx_query.get()->m_input_query != boost::none) return true;    // requires context of inputs
  if (query.m_tx_query.get()->m_output_query != boost::none) return true;    // requires context of inputs
  return false;
}

bool PyMoneroTxWallet::decode_rpc_type(const std::string &rpc_type, const std::shared_ptr<monero::monero_tx_wallet> &tx) {
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

void PyMoneroTxWallet::init_sent(const monero::monero_tx_config &config, std::shared_ptr<monero::monero_tx_wallet> &tx, bool copy_destinations) {
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

void PyMoneroTxWallet::from_property_tree_with_transfer(const boost::property_tree::ptree& node, const std::shared_ptr<monero::monero_tx_wallet>& tx, boost::optional<bool> &is_outgoing, const monero_tx_config &config) {  
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
      else {
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
      else {
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

void PyMoneroTxWallet::from_property_tree_with_transfer(const boost::property_tree::ptree& node, const std::shared_ptr<monero::monero_tx_wallet>& tx, boost::optional<bool> &is_outgoing) { 
  monero::monero_tx_config config;
  from_property_tree_with_transfer(node, tx, is_outgoing, config);
}

void PyMoneroTxWallet::from_property_tree_with_output(const boost::property_tree::ptree& node, const std::shared_ptr<monero::monero_tx_wallet>& tx) {  
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

void PyMoneroTxSet::from_property_tree(const boost::property_tree::ptree& node, const std::shared_ptr<monero::monero_tx_set>& set) {
  for (boost::property_tree::ptree::const_iterator it = node.begin(); it != node.end(); ++it) {
    std::string key = it->first;
    if (key == std::string("multisig_txset")) set->m_multisig_tx_hex = it->second.data();
    else if (key == std::string("unsigned_txset")) set->m_unsigned_tx_hex = it->second.data();
    else if (key == std::string("signed_txset")) set->m_signed_tx_hex = it->second.data();
  }
}

void PyMoneroTxSet::from_tx(const boost::property_tree::ptree& node, const std::shared_ptr<monero::monero_tx_set>& set, const std::shared_ptr<monero::monero_tx_wallet> &tx, bool is_outgoing, const monero_tx_config &config) {
  from_property_tree(node, set);
  boost::optional<bool> outgoing = is_outgoing;
  PyMoneroTxWallet::from_property_tree_with_transfer(node, tx, outgoing, config);
  set->m_txs.push_back(tx);
}

void PyMoneroTxSet::from_sent_txs(const boost::property_tree::ptree& node, const std::shared_ptr<monero::monero_tx_set>& set) {
  std::vector<std::shared_ptr<monero::monero_tx_wallet>> txs;
  from_sent_txs(node, set, txs, boost::none);
}

void PyMoneroTxSet::from_sent_txs(const boost::property_tree::ptree& node, const std::shared_ptr<monero::monero_tx_set>& set, std::vector<std::shared_ptr<monero::monero_tx_wallet>> &txs, const boost::optional<monero_tx_config> &conf) {
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
    if (key == std::string("tx_hash_list")) {
      auto node2 = it->second;
      int i = 0;
      for (auto it2 = node2.begin(); it2 != node2.end(); ++it2) {
        auto tx = txs[i];
        tx->m_hash = it2->second.data();
        i++;
      }
    }
    else if (key == std::string("tx_key_list")) {
      auto node2 = it->second;
      int i = 0;
      for (auto it2 = node2.begin(); it2 != node2.end(); ++it2) {
        auto tx = txs[i];
        tx->m_key = it2->second.data();
        i++;
      }
    }
    else if (key == std::string("tx_blob_list")) {
      auto node2 = it->second;
      int i = 0;
      for (auto it2 = node2.begin(); it2 != node2.end(); ++it2) {
        auto tx = txs[i];
        tx->m_full_hex = it2->second.data();
        i++;
      }
    }
    else if (key == std::string("tx_metadata_list")) {
      auto node2 = it->second;
      int i = 0;
      for (auto it2 = node2.begin(); it2 != node2.end(); ++it2) {
        auto tx = txs[i];
        tx->m_metadata = it2->second.data();
        i++;
      }
    }
    else if (key == std::string("fee_list")) {
      auto node2 = it->second;
      int i = 0;
      for (auto it2 = node2.begin(); it2 != node2.end(); ++it2) {
        auto tx = txs[i];
        tx->m_fee = it2->second.get_value<uint64_t>();
        i++;
      }
    }
    else if (key == std::string("amount_list")) {
      auto node2 = it->second;
      int i = 0;
      for (auto it2 = node2.begin(); it2 != node2.end(); ++it2) {
        auto tx = txs[i];
        auto outgoing_transfer = std::make_shared<monero::monero_outgoing_transfer>();
        outgoing_transfer->m_tx = tx;
        outgoing_transfer->m_amount = it2->second.get_value<uint64_t>();
        tx->m_outgoing_transfer = outgoing_transfer;
        i++;
      }
    }
    else if (key == std::string("weight_list")) {
      auto node2 = it->second;
      int i = 0;
      for (auto it2 = node2.begin(); it2 != node2.end(); ++it2) {
        auto tx = txs[i];
        tx->m_weight = it2->second.get_value<uint64_t>();
        i++;
      }
    }
    else if (key == std::string("spent_key_images_list")) {
      auto node2 = it->second;
      int i = 0;
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
    else if (key == std::string("amounts_by_dest_list")) {
      auto node2 = it->second;
      int i = 0;
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

void PyMoneroTxSet::from_describe_transfer(const boost::property_tree::ptree& node, const std::shared_ptr<monero::monero_tx_set>& set) {
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

rapidjson::Value PyMoneroKeyImage::to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const {
  // create root
  rapidjson::Value root(rapidjson::kObjectType);

  // set string values
  rapidjson::Value value_str(rapidjson::kStringType);
  if (m_hex != boost::none) monero_utils::add_json_member("key_image", m_hex.get(), allocator, root, value_str);
  if (m_signature != boost::none) monero_utils::add_json_member("signature", m_signature.get(), allocator, root, value_str);

  // return root
  return root;
}

void PyMoneroKeyImage::from_property_tree(const boost::property_tree::ptree& node, const std::shared_ptr<monero::monero_key_image>& key_image) {
  for (boost::property_tree::ptree::const_iterator it = node.begin(); it != node.end(); ++it) {
    std::string key = it->first;
    if (key == std::string("key_image")) key_image->m_hex = it->second.data();
    else if (key == std::string("signature")) key_image->m_signature = it->second.data();
  }
}

void PyMoneroKeyImage::from_property_tree(const boost::property_tree::ptree& node, std::vector<std::shared_ptr<monero::monero_key_image>>& key_images) {
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

void PyMoneroKeyImageImportResult::from_property_tree(const boost::property_tree::ptree& node, const std::shared_ptr<monero::monero_key_image_import_result>& result) {
  for (boost::property_tree::ptree::const_iterator it = node.begin(); it != node.end(); ++it) {
    std::string key = it->first;
    if (key == std::string("height")) result->m_height = it->second.get_value<uint64_t>();
    else if (key == std::string("spent")) result->m_spent_amount = it->second.get_value<uint64_t>();
    else if (key == std::string("unspent")) result->m_unspent_amount = it->second.get_value<uint64_t>();
  }
}

void PyMoneroMultisigInfo::from_property_tree(const boost::property_tree::ptree& node, const std::shared_ptr<monero::monero_multisig_info>& info) {
  for (boost::property_tree::ptree::const_iterator it = node.begin(); it != node.end(); ++it) {
    std::string key = it->first;
    if (key == std::string("multisig")) info->m_is_multisig = it->second.get_value<bool>();
    else if (key == std::string("ready")) info->m_is_ready = it->second.get_value<bool>();
    else if (key == std::string("threshold")) info->m_threshold = it->second.get_value<uint32_t>();
    else if (key == std::string("total")) info->m_num_participants = it->second.get_value<uint32_t>();
  }
}

void PyMoneroMultisigInitResult::from_property_tree(const boost::property_tree::ptree& node, const std::shared_ptr<monero::monero_multisig_init_result>& info) {
  for (boost::property_tree::ptree::const_iterator it = node.begin(); it != node.end(); ++it) {
    std::string key = it->first;
    if (key == std::string("address")) info->m_address = it->second.data();
    else if (key == std::string("multisig_info")) info->m_multisig_hex = it->second.data();
  }
}

void PyMoneroMultisigSignResult::from_property_tree(const boost::property_tree::ptree& node, const std::shared_ptr<monero::monero_multisig_sign_result>& res) {
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

rapidjson::Value PyMoneroMultisigTxDataParams::to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const { 
  rapidjson::Value root(rapidjson::kObjectType); 
  rapidjson::Value value_str(rapidjson::kStringType);
  if (m_multisig_tx_hex != boost::none) monero_utils::add_json_member("tx_data_hex", m_multisig_tx_hex.get(), allocator, root, value_str);
  return root; 
}

void PyMoneroAccountTag::from_property_tree(const boost::property_tree::ptree& node, const std::shared_ptr<PyMoneroAccountTag>& account_tag) {
  for (boost::property_tree::ptree::const_iterator it = node.begin(); it != node.end(); ++it) {
    std::string key = it->first;
    if (key == std::string("tag")) account_tag->m_tag = it->second.data();
    else if (key == std::string("label") && !it->second.data().empty()) account_tag->m_label = it->second.data();
  }
}

void PyMoneroAccountTag::from_property_tree(const boost::property_tree::ptree& node, std::vector<std::shared_ptr<PyMoneroAccountTag>>& account_tags) {
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

void PyMoneroSubaddress::from_rpc_property_tree(const boost::property_tree::ptree& node, const std::shared_ptr<monero::monero_subaddress>& subaddress) {
  for (boost::property_tree::ptree::const_iterator it = node.begin(); it != node.end(); ++it) {
    std::string key = it->first;
    if (key == std::string("account_index")) subaddress->m_account_index = it->second.get_value<uint32_t>();
    else if (key == std::string("address_index")) subaddress->m_index = it->second.get_value<uint32_t>();
    else if (key == std::string("address")) subaddress->m_address = it->second.data();
    else if (key == std::string("balance")) subaddress->m_balance = it->second.get_value<uint64_t>();
    else if (key == std::string("unlocked_balance")) subaddress->m_unlocked_balance = it->second.get_value<uint64_t>();
    else if (key == std::string("label") && !it->second.data().empty()) subaddress->m_label = it->second.data();
    else if (key == std::string("used")) subaddress->m_is_used = it->second.get_value<bool>();
    else if (key == std::string("num_unspent_outputs")) subaddress->m_num_unspent_outputs = it->second.get_value<uint64_t>();
    else if (key == std::string("blocks_to_unlock")) subaddress->m_num_blocks_to_unlock = it->second.get_value<uint64_t>();
  }
}

void PyMoneroSubaddress::from_rpc_property_tree(const boost::property_tree::ptree& node, std::vector<std::shared_ptr<monero::monero_subaddress>>& subaddresses) {
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

void PyMoneroSubaddress::from_property_tree(const boost::property_tree::ptree& node, const std::shared_ptr<monero::monero_subaddress>& subaddress) {
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

void PyMoneroIntegratedAddress::from_property_tree(const boost::property_tree::ptree& node, const std::shared_ptr<monero::monero_integrated_address>& subaddress) {
  for (boost::property_tree::ptree::const_iterator it = node.begin(); it != node.end(); ++it) {
    std::string key = it->first;
    if (key == std::string("integrated_address")) subaddress->m_integrated_address = it->second.data();
    else if (key == std::string("standard_address")) subaddress->m_standard_address = it->second.data();
    else if (key == std::string("payment_id")) subaddress->m_payment_id = it->second.data();
  }
}

void PyMoneroAccount::from_property_tree(const boost::property_tree::ptree& node, const std::shared_ptr<monero::monero_account>& account) {
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

void PyMoneroAccount::from_property_tree(const boost::property_tree::ptree& node, std::vector<std::shared_ptr<monero::monero_account>>& accounts) {    
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

void PyMoneroAccount::from_property_tree(const boost::property_tree::ptree& node, std::vector<monero::monero_account>& accounts) {    
  std::vector<std::shared_ptr<monero::monero_account>> accounts_ptr;
  from_property_tree(node, accounts_ptr);

  for (const auto &account : accounts_ptr) {
    accounts.push_back(*account);
  }
}

uint64_t PyMoneroWalletGetHeightResponse::from_property_tree(const boost::property_tree::ptree& node) {
  for (boost::property_tree::ptree::const_iterator it = node.begin(); it != node.end(); ++it) {
    std::string key = it->first;
    if (key == std::string("height")) return it->second.get_value<uint64_t>();
  }
  throw std::runtime_error("Invalid get_height response");
}

rapidjson::Value PyMoneroQueryKeyParams::to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const { 
  rapidjson::Value root(rapidjson::kObjectType); 
  rapidjson::Value value_str(rapidjson::kStringType);
  if (m_key_type != boost::none) monero_utils::add_json_member("key_type", m_key_type.get(), allocator, root, value_str);
  return root; 
}

rapidjson::Value PyMoneroQueryOutputParams::to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const { 
  rapidjson::Value root(rapidjson::kObjectType); 
  rapidjson::Value value_str(rapidjson::kStringType);
  if (m_key_image != boost::none) monero_utils::add_json_member("key_image", m_key_image.get(), allocator, root, value_str);
  return root; 
}

rapidjson::Value PyMoneroGetAddressParams::to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const { 
  rapidjson::Value root(rapidjson::kObjectType);
  rapidjson::Value value_num(rapidjson::kNumberType);
  if (!m_subaddress_indices.empty()) root.AddMember("address_index", monero_utils::to_rapidjson_val(allocator, m_subaddress_indices), allocator);
  if (m_account_index != boost::none) monero_utils::add_json_member("account_index", m_account_index.get(), allocator, root, value_num);
  return root; 
}

rapidjson::Value PyMoneroGetAddressIndexParams::to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const { 
  rapidjson::Value root(rapidjson::kObjectType); 
  rapidjson::Value value_str(rapidjson::kStringType);
  if (m_address != boost::none) monero_utils::add_json_member("address", m_address.get(), allocator, root, value_str);
  return root; 
}

rapidjson::Value PyMoneroMakeIntegratedAddressParams::to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const { 
  rapidjson::Value root(rapidjson::kObjectType); 
  rapidjson::Value value_str(rapidjson::kStringType);
  if (m_standard_address != boost::none) monero_utils::add_json_member("standard_address", m_standard_address.get(), allocator, root, value_str);
  if (m_payment_id != boost::none) monero_utils::add_json_member("payment_id", m_payment_id.get(), allocator, root, value_str);
  return root; 
}

rapidjson::Value PyMoneroSplitIntegratedAddressParams::to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const { 
  rapidjson::Value root(rapidjson::kObjectType); 
  rapidjson::Value value_str(rapidjson::kStringType);
  if (m_integrated_address != boost::none) monero_utils::add_json_member("integrated_address", m_integrated_address.get(), allocator, root, value_str);
  return root; 
}

rapidjson::Value PyMoneroWalletStartMiningParams::to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const { 
  rapidjson::Value root(rapidjson::kObjectType); 
  rapidjson::Value value_str(rapidjson::kStringType);
  rapidjson::Value value_num(rapidjson::kNumberType);
  if (m_num_threads != boost::none) monero_utils::add_json_member("threads_count", m_num_threads.get(), allocator, root, value_num);
  if (m_is_background != boost::none) monero_utils::add_json_member("do_background_mining", m_is_background.get(), allocator, root);
  if (m_ignore_battery != boost::none) monero_utils::add_json_member("ignore_battery", m_ignore_battery.get(), allocator, root);
  return root;
}

rapidjson::Value PyMoneroPrepareMultisigParams::to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const { 
  rapidjson::Value root(rapidjson::kObjectType); 
  if (m_enable_multisig_experimental != boost::none) monero_utils::add_json_member("enable_multisig_experimental", m_enable_multisig_experimental.get(), allocator, root);
  return root; 
}

std::string PyMoneroExportMultisigHexResponse::from_property_tree(const boost::property_tree::ptree& node) {
  for (boost::property_tree::ptree::const_iterator it = node.begin(); it != node.end(); ++it) {
    std::string key = it->first;
    if (key == std::string("info")) return it->second.data();
  }
  throw std::runtime_error("Invalid prepare multisig response");
}

rapidjson::Value PyMoneroImportMultisigHexParams::to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const { 
  rapidjson::Value root(rapidjson::kObjectType); 
  if (!m_multisig_hexes.empty()) root.AddMember("info", monero_utils::to_rapidjson_val(allocator, m_multisig_hexes), allocator);
  return root;
}

int PyMoneroImportMultisigHexResponse::from_property_tree(const boost::property_tree::ptree& node) {
  for (boost::property_tree::ptree::const_iterator it = node.begin(); it != node.end(); ++it) {
    std::string key = it->first;
    if (key == std::string("n_outputs")) return it->second.get_value<int>();
  }
  throw std::runtime_error("Invalid prepare multisig response");
}

std::vector<std::string> PyMoneroSubmitMultisigTxHexResponse::from_property_tree(const boost::property_tree::ptree& node) {
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

rapidjson::Value PyMoneroMakeMultisigParams::to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const { 
  rapidjson::Value root(rapidjson::kObjectType);
  rapidjson::Value val_num(rapidjson::kNumberType);
  rapidjson::Value val_str(rapidjson::kStringType);
  if (!m_multisig_info.empty()) root.AddMember("multisig_info", monero_utils::to_rapidjson_val(allocator, m_multisig_info), allocator);
  if (m_threshold != boost::none) monero_utils::add_json_member("threshold", m_threshold.get(), allocator, root, val_num);
  if (m_password != boost::none) monero_utils::add_json_member("password", m_password.get(), allocator, root, val_str);
  return root; 
}

std::string PyMoneroPrepareMakeMultisigResponse::from_property_tree(const boost::property_tree::ptree& node) {
  for (boost::property_tree::ptree::const_iterator it = node.begin(); it != node.end(); ++it) {
    std::string key = it->first;
    if (key == std::string("multisig_info")) return it->second.data();
  }
  throw std::runtime_error("Invalid prepare multisig response");
}

rapidjson::Value PyMoneroExchangeMultisigKeysParams::to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const { 
  rapidjson::Value root(rapidjson::kObjectType);
  rapidjson::Value val_num(rapidjson::kNumberType);
  rapidjson::Value val_str(rapidjson::kStringType);
  if (!m_multisig_info.empty()) root.AddMember("multisig_info", monero_utils::to_rapidjson_val(allocator, m_multisig_info), allocator);
  if (m_password != boost::none) monero_utils::add_json_member("password", m_password.get(), allocator, root, val_str);
  return root; 
}

rapidjson::Value PyMoneroParsePaymentUriParams::to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const { 
  rapidjson::Value root(rapidjson::kObjectType);
  rapidjson::Value val_str(rapidjson::kStringType);
  if (m_uri != boost::none) monero_utils::add_json_member("uri", m_uri.get(), allocator, root, val_str);
  return root;
}

std::shared_ptr<monero::monero_tx_config> PyMoneroParsePaymentUriResponse::to_tx_config() const {
  auto tx_config = std::make_shared<monero::monero_tx_config>();
  tx_config->m_payment_id = m_payment_id;
  tx_config->m_recipient_name = m_recipient_name;
  tx_config->m_note = m_tx_description;
  tx_config->m_amount = m_amount;
  tx_config->m_address = m_address;
  return tx_config;
}

void PyMoneroParsePaymentUriResponse::from_property_tree(const boost::property_tree::ptree& node, const std::shared_ptr<PyMoneroParsePaymentUriResponse>& response) {
  for (boost::property_tree::ptree::const_iterator it = node.begin(); it != node.end(); ++it) {
    std::string key = it->first;
    if (key == std::string("address")) response->m_address = it->second.data();
    else if (key == std::string("amount")) response->m_amount = it->second.get_value<uint64_t>();
    else if (key == std::string("payment_id")) response->m_payment_id = it->second.data();
    else if (key == std::string("recipient_name")) response->m_recipient_name = it->second.data();
    else if (key == std::string("tx_description")) response->m_tx_description = it->second.data();
  }
}

rapidjson::Value PyMoneroGetPaymentUriParams::to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const { 
  rapidjson::Value root(rapidjson::kObjectType); 
  rapidjson::Value value_str(rapidjson::kStringType);
  rapidjson::Value value_num(rapidjson::kNumberType);
  if (m_address != boost::none) monero_utils::add_json_member("address", m_address.get(), allocator, root, value_str);
  if (m_amount != boost::none) monero_utils::add_json_member("amount", m_amount.get(), allocator, root, value_num);
  if (m_recipient_name != boost::none) monero_utils::add_json_member("recipient_name", m_recipient_name.get(), allocator, root, value_str);
  if (m_tx_description != boost::none) monero_utils::add_json_member("tx_description", m_tx_description.get(), allocator, root, value_str);
  return root; 
}

std::string PyMoneroGetPaymentUriResponse::from_property_tree(const boost::property_tree::ptree& node) {
  for (boost::property_tree::ptree::const_iterator it = node.begin(); it != node.end(); ++it) {
    std::string key = it->first;
    if (key == std::string("uri")) return it->second.data();
  }
  throw std::runtime_error("Invalid make uri response");
}

rapidjson::Value PyMoneroGetBalanceParams::to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const { 
  rapidjson::Value root(rapidjson::kObjectType); 
  rapidjson::Value value_num(rapidjson::kNumberType);
  if (m_account_idx != boost::none) monero_utils::add_json_member("account_index", m_account_idx.get(), allocator, root, value_num);
  if (!m_address_indices.empty()) root.AddMember("address_indices", monero_utils::to_rapidjson_val(allocator, m_address_indices), allocator);
  if (m_all_accounts != boost::none) monero_utils::add_json_member("all_accounts", m_all_accounts.get(), allocator, root);
  if (m_strict != boost::none) monero_utils::add_json_member("strict", m_strict.get(), allocator, root);
  return root; 
}

void PyMoneroGetBalanceResponse::from_property_tree(const boost::property_tree::ptree& node, const std::shared_ptr<PyMoneroGetBalanceResponse>& response) {
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

rapidjson::Value PyMoneroCreateAccountParams::to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const { 
  rapidjson::Value root(rapidjson::kObjectType);
  rapidjson::Value value_str(rapidjson::kStringType);
  if (m_tag != boost::none) monero_utils::add_json_member("label", m_tag.get(), allocator, root, value_str);
  return root;
}

rapidjson::Value PyMoneroCloseWalletParams::to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const { 
  rapidjson::Value root(rapidjson::kObjectType); 
  if (m_save != boost::none) monero_utils::add_json_member("autosave_current", m_save.get(), allocator, root);
  return root; 
}

rapidjson::Value PyMoneroChangeWalletPasswordParams::to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const { 
  rapidjson::Value root(rapidjson::kObjectType); 
  rapidjson::Value value_str(rapidjson::kStringType);
  if (m_old_password != boost::none) monero_utils::add_json_member("old_password", m_old_password.get(), allocator, root, value_str);
  if (m_new_password != boost::none) monero_utils::add_json_member("new_password", m_new_password.get(), allocator, root, value_str);
  return root; 
}

rapidjson::Value PyMoneroWalletAttributeParams::to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const { 
  rapidjson::Value root(rapidjson::kObjectType); 
  rapidjson::Value value_str(rapidjson::kStringType);
  if (m_key != boost::none) monero_utils::add_json_member("key", m_key.get(), allocator, root, value_str);
  if (m_value != boost::none) monero_utils::add_json_member("value", m_value.get(), allocator, root, value_str);
  return root; 
}

void PyMoneroWalletAttributeParams::from_property_tree(const boost::property_tree::ptree& node, const std::shared_ptr<PyMoneroWalletAttributeParams>& attributes) {
  attributes->m_key = boost::none;
  attributes->m_value = boost::none;

  for (boost::property_tree::ptree::const_iterator it = node.begin(); it != node.end(); ++it) {
    std::string key = it->first;
    if (key == std::string("key")) attributes->m_key = it->second.data();
    else if (key == std::string("value")) attributes->m_value = it->second.data();
  }
}

rapidjson::Value PyMoneroScanTxParams::to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const { 
  rapidjson::Value root(rapidjson::kObjectType); 
  if (!m_tx_hashes.empty()) root.AddMember("txids", monero_utils::to_rapidjson_val(allocator, m_tx_hashes), allocator);
  return root; 
}

rapidjson::Value PyMoneroSetDaemonParams::to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const { 
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

rapidjson::Value PyMoneroAutoRefreshParams::to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const { 
  rapidjson::Value root(rapidjson::kObjectType); 
  if (m_enable != boost::none) monero_utils::add_json_member("enable", m_enable.get(), allocator, root);
  return root; 
}

rapidjson::Value PyMoneroSetAccountTagDescriptionParams::to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const { 
  rapidjson::Value root(rapidjson::kObjectType); 
  rapidjson::Value value_str(rapidjson::kStringType);
  if (m_tag != boost::none) monero_utils::add_json_member("tag", m_tag.get(), allocator, root, value_str);
  if (m_label != boost::none) monero_utils::add_json_member("label", m_label.get(), allocator, root, value_str);
  return root; 
}

rapidjson::Value PyMoneroTagAccountsParams::to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const { 
  rapidjson::Value root(rapidjson::kObjectType);
  rapidjson::Value value_str(rapidjson::kStringType);
  if (m_tag != boost::none) monero_utils::add_json_member("tag", m_tag.get(), allocator, root, value_str);
  if (!m_account_indices.empty()) root.AddMember("accounts", monero_utils::to_rapidjson_val(allocator, m_account_indices), allocator);
  return root; 
}

rapidjson::Value PyMoneroTxNotesParams::to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const { 
  rapidjson::Value root(rapidjson::kObjectType); 
  if (!m_tx_hashes.empty()) root.AddMember("txids", monero_utils::to_rapidjson_val(allocator, m_tx_hashes), allocator);
  if (!m_notes.empty()) root.AddMember("notes", monero_utils::to_rapidjson_val(allocator, m_notes), allocator);
  return root; 
}

rapidjson::Value PyMoneroAddressBookEntryParams::to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const { 
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

void PyMoneroAddressBookEntry::from_property_tree(const boost::property_tree::ptree& node, const std::shared_ptr<monero::monero_address_book_entry>& entry) {
  for (boost::property_tree::ptree::const_iterator it = node.begin(); it != node.end(); ++it) {
    std::string key = it->first;

    if (key == std::string("index")) entry->m_index = it->second.get_value<uint64_t>();
    else if (key == std::string("address")) entry->m_address = it->second.data();
    else if (key == std::string("description")) entry->m_description = it->second.data();
    else if (key == std::string("payment_id")) entry->m_payment_id = it->second.data();
  }
}

void PyMoneroAddressBookEntry::from_property_tree(const boost::property_tree::ptree& node, std::vector<std::shared_ptr<monero::monero_address_book_entry>>& entries) {
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

rapidjson::Value PyMoneroGetAccountsParams::to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const { 
  rapidjson::Value root(rapidjson::kObjectType);
  rapidjson::Value value_str(rapidjson::kStringType);
  if (m_label != boost::none) monero_utils::add_json_member("label", m_label.get(), allocator, root, value_str);
  return root;
}

rapidjson::Value PyMoneroVerifySignMessageParams::to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const { 
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

rapidjson::Value PyMoneroCheckTxKeyParams::to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const { 
  rapidjson::Value root(rapidjson::kObjectType);
  rapidjson::Value value_str(rapidjson::kStringType);
  if (m_tx_hash != boost::none) monero_utils::add_json_member("txid", m_tx_hash.get(), allocator, root, value_str);
  if (m_address != boost::none) monero_utils::add_json_member("address", m_address.get(), allocator, root, value_str);
  if (m_tx_key != boost::none) monero_utils::add_json_member("tx_key", m_tx_key.get(), allocator, root, value_str);
  return root;
}

rapidjson::Value PyMoneroSignDescribeTransferParams::to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const { 
  rapidjson::Value root(rapidjson::kObjectType);
  rapidjson::Value value_str(rapidjson::kStringType);
  if (m_unsigned_txset != boost::none) monero_utils::add_json_member("unsigned_txset", m_unsigned_txset.get(), allocator, root, value_str);
  if (m_multisig_txset != boost::none) monero_utils::add_json_member("multisig_txset", m_multisig_txset.get(), allocator, root, value_str);

  return root;
}

rapidjson::Value PyMoneroWalletRelayTxParams::to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const { 
  rapidjson::Value root(rapidjson::kObjectType);
  rapidjson::Value value_str(rapidjson::kStringType);
  if (m_hex != boost::none) monero_utils::add_json_member("hex", m_hex.get(), allocator, root, value_str);
  return root;
}

PyMoneroSweepParams::PyMoneroSweepParams(const monero_tx_config& config):
  m_address(config.m_address),
  m_account_index(config.m_account_index),
  m_subaddr_indices(config.m_subaddress_indices),
  m_key_image(config.m_key_image),
  m_relay(config.m_relay),
  m_priority(config.m_priority),
  m_payment_id(config.m_payment_id),
  m_below_amount(config.m_below_amount),
  m_get_tx_key(true),
  m_get_tx_hex(true),
  m_get_tx_metadata(true) {
}

rapidjson::Value PyMoneroSweepParams::to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const { 
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

rapidjson::Value PyMoneroSubmitTransferParams::to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const { 
  rapidjson::Value root(rapidjson::kObjectType);
  rapidjson::Value val_str(rapidjson::kStringType);
  if (m_signed_tx_hex != boost::none) monero_utils::add_json_member("tx_data_hex", m_signed_tx_hex.get(), allocator, root, val_str);
  return root;
}

rapidjson::Value PyMoneroCreateSubaddressParams::to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const { 
  rapidjson::Value root(rapidjson::kObjectType);
  rapidjson::Value val_str(rapidjson::kStringType);
  rapidjson::Value val_num(rapidjson::kNumberType);
  if (m_label != boost::none) monero_utils::add_json_member("label", m_label.get(), allocator, root, val_str);
  if (m_account_index != boost::none) monero_utils::add_json_member("account_index", m_account_index.get(), allocator, root, val_num);
  return root;
}

rapidjson::Value PyMoneroSetSubaddressLabelParams::to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const { 
  rapidjson::Value root(rapidjson::kObjectType);
  rapidjson::Value val_str(rapidjson::kStringType);
  rapidjson::Value val_num(rapidjson::kNumberType);
  if (m_label != boost::none) monero_utils::add_json_member("label", m_label.get(), allocator, root, val_str);
  if (m_account_index != boost::none && m_subaddress_index != boost::none) {
    rapidjson::Value index(rapidjson::kObjectType);
    monero_utils::add_json_member("major", m_account_index.get(), allocator, index, val_num);
    monero_utils::add_json_member("minor", m_subaddress_index.get(), allocator, index, val_num);
    root.AddMember("index", index, allocator);
  }
  return root;
}

rapidjson::Value PyMoneroImportExportOutputsParams::to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const { 
  rapidjson::Value root(rapidjson::kObjectType);
  rapidjson::Value val_str(rapidjson::kStringType);
  if (m_all != boost::none) monero_utils::add_json_member("all", m_all.get(), allocator, root);
  if (m_outputs_hex != boost::none) monero_utils::add_json_member("outputs_data_hex", m_outputs_hex.get(), allocator, root, val_str);
  return root;
}

rapidjson::Value PyMoneroImportExportKeyImagesParams::to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const { 
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

PyMoneroCreateOpenWalletParams::PyMoneroCreateOpenWalletParams(const boost::optional<std::string>& filename, const boost::optional<std::string> &password):
  m_filename(filename), m_password(password), m_autosave_current(false) {
}

PyMoneroCreateOpenWalletParams::PyMoneroCreateOpenWalletParams(const boost::optional<std::string>& filename, const boost::optional<std::string> &password, const boost::optional<std::string> &language):
  m_filename(filename), m_password(password), m_language(language), m_autosave_current(false) {
}

PyMoneroCreateOpenWalletParams::PyMoneroCreateOpenWalletParams(const boost::optional<std::string>& filename, const boost::optional<std::string> &password, const boost::optional<std::string> &seed, const boost::optional<std::string> &seed_offset, const boost::optional<uint64_t> &restore_height, const boost::optional<std::string> &language, const boost::optional<bool> &autosave_current, const boost::optional<bool> &enable_multisig_experimental): 
  m_filename(filename),
  m_password(password),
  m_seed(seed),
  m_seed_offset(seed_offset),
  m_restore_height(restore_height),
  m_language(language),
  m_autosave_current(autosave_current),
  m_enable_multisig_experimental(enable_multisig_experimental) {
}

PyMoneroCreateOpenWalletParams::PyMoneroCreateOpenWalletParams(const boost::optional<std::string>& filename, const boost::optional<std::string> &password, const boost::optional<std::string> &address, const boost::optional<std::string> &view_key, const boost::optional<std::string> &spend_key, const boost::optional<uint64_t> &restore_height, const boost::optional<bool> &autosave_current):
  m_filename(filename),
  m_password(password),
  m_address(address),
  m_view_key(view_key),
  m_spend_key(spend_key),
  m_restore_height(restore_height),
  m_autosave_current(autosave_current) {
}

rapidjson::Value PyMoneroCreateOpenWalletParams::to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const { 
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

PyMoneroReserveProofParams::PyMoneroReserveProofParams(const std::string &message, bool all):
  m_all(all), m_message(message) {
}

PyMoneroReserveProofParams::PyMoneroReserveProofParams(const std::string &address, const std::string &message, const std::string &signature): 
  m_address(address), m_message(message), m_signature(signature) {
}

PyMoneroReserveProofParams::PyMoneroReserveProofParams(const std::string &tx_hash, const std::string &address, const std::string &message, const std::string &signature):
  m_tx_hash(tx_hash), m_address(address), m_message(message), m_signature(signature) {
}

PyMoneroReserveProofParams::PyMoneroReserveProofParams(const std::string &tx_hash, const std::string &message):
  m_tx_hash(tx_hash), m_message(message) {
}

PyMoneroReserveProofParams::PyMoneroReserveProofParams(uint32_t account_index, uint64_t amount, const std::string &message):
  m_account_index(account_index), m_amount(amount), m_message(message) {
}

rapidjson::Value PyMoneroReserveProofParams::to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const { 
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

rapidjson::Value PyMoneroRefreshWalletParams::to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const { 
  rapidjson::Value root(rapidjson::kObjectType);
  rapidjson::Value value_num(rapidjson::kNumberType);
  if (m_enable != boost::none) monero_utils::add_json_member("enable", m_enable.get(), allocator, root);
  if (m_period != boost::none) monero_utils::add_json_member("period", m_period.get(), allocator, root, value_num);
  if (m_start_height != boost::none) monero_utils::add_json_member("start_height", m_start_height.get(), allocator, root, value_num);
  return root;
}

PyMoneroTransferParams::PyMoneroTransferParams(const monero::monero_tx_config &config) {
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

rapidjson::Value PyMoneroTransferParams::to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const { 
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

void PyMoneroCheckReserve::from_property_tree(const boost::property_tree::ptree& node, const std::shared_ptr<monero::monero_check_reserve>& check) {
  for (boost::property_tree::ptree::const_iterator it = node.begin(); it != node.end(); ++it) {
    std::string key = it->first;
    if (key == std::string("good")) check->m_is_good = it->second.get_value<bool>();
    else if (key == std::string("total")) check->m_total_amount = it->second.get_value<uint64_t>();
    else if (key == std::string("spent")) check->m_unconfirmed_spent_amount = it->second.get_value<uint64_t>();
  }
}

void PyMoneroCheckTxProof::from_property_tree(const boost::property_tree::ptree& node, const std::shared_ptr<monero::monero_check_tx>& check) {
  for (boost::property_tree::ptree::const_iterator it = node.begin(); it != node.end(); ++it) {
    std::string key = it->first;
    if (key == std::string("good")) check->m_is_good = it->second.get_value<bool>();
    if (key == std::string("in_pool")) check->m_in_tx_pool = it->second.get_value<bool>();
    else if (key == std::string("confirmations")) check->m_num_confirmations = it->second.get_value<uint64_t>();
    else if (key == std::string("received")) check->m_received_amount = it->second.get_value<uint64_t>();
  }
}

std::string PyMoneroReserveProofSignature::from_property_tree(const boost::property_tree::ptree& node) {
  for (boost::property_tree::ptree::const_iterator it = node.begin(); it != node.end(); ++it) {
    std::string key = it->first;
    if (key == std::string("signature")) return it->second.data();
  }

  throw std::runtime_error("Invalid reserve proof response");
}

void PyMoneroMessageSignatureResult::from_property_tree(const boost::property_tree::ptree& node, const std::shared_ptr<monero::monero_message_signature_result> result) {
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
