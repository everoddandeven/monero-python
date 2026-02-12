#include "py_monero_daemon_model.h"
#include "utils/monero_utils.h"

void PyMoneroBlockHeader::from_property_tree(const boost::property_tree::ptree& node, const std::shared_ptr<monero::monero_block_header>& header) {
  for (boost::property_tree::ptree::const_iterator it = node.begin(); it != node.end(); ++it) {
    std::string key = it->first;
    if (key == std::string("block_header")) {
      PyMoneroBlockHeader::from_property_tree(it->second, header);
      return;
    }
    else if (key == std::string("hash")) header->m_hash = it->second.data();
    else if (key == std::string("height")) header->m_height = it->second.get_value<uint64_t>();
    else if (key == std::string("timestamp")) header->m_timestamp = it->second.get_value<uint64_t>();
    else if (key == std::string("block_size")) header->m_size = it->second.get_value<uint64_t>();
    else if (key == std::string("block_weight")) header->m_weight = it->second.get_value<uint64_t>();
    else if (key == std::string("long_term_weight")) header->m_long_term_weight = it->second.get_value<uint64_t>();
    else if (key == std::string("depth")) header->m_depth = it->second.get_value<uint64_t>();
    else if (key == std::string("difficulty")) header->m_difficulty = it->second.get_value<uint64_t>();
    else if (key == std::string("cumulative_difficulty")) header->m_cumulative_difficulty = it->second.get_value<uint64_t>();
    else if (key == std::string("major_version")) header->m_major_version = it->second.get_value<uint32_t>();
    else if (key == std::string("minor_version")) header->m_minor_version = it->second.get_value<uint32_t>();
    else if (key == std::string("nonce")) header->m_nonce = it->second.get_value<uint32_t>();
    else if (key == std::string("miner_tx_hash")) header->m_miner_tx_hash = it->second.data();
    else if (key == std::string("num_txes")) header->m_num_txs = it->second.get_value<uint32_t>();
    else if (key == std::string("orphan_status")) header->m_orphan_status = it->second.get_value<bool>();
    else if (key == std::string("prev_hash") || key == std::string("prev_id")) header->m_prev_hash = it->second.data();
    else if (key == std::string("reward")) header->m_reward = it->second.get_value<uint64_t>();
    else if (key == std::string("pow_hash")) {
      std::string pow_hash = it->second.data();
      if (!pow_hash.empty()) header->m_pow_hash = pow_hash;
    }
  }
}

void PyMoneroBlockHeader::from_property_tree(const boost::property_tree::ptree& node, std::vector<std::shared_ptr<monero::monero_block_header>>& headers) {
  for (boost::property_tree::ptree::const_iterator it = node.begin(); it != node.end(); ++it) {
    std::string key = it->first;
    
    if (key == std::string("headers")) {
      auto node2 = it->second;

      for(boost::property_tree::ptree::const_iterator it2 = node2.begin(); it2 != node2.end(); ++it2) {
        auto header = std::make_shared<monero::monero_block_header>();
        PyMoneroBlockHeader::from_property_tree(it2->second, header);
        headers.push_back(header);
      }
    }
  }
}

void PyMoneroBlock::from_property_tree(const boost::property_tree::ptree& node, const std::shared_ptr<monero::monero_block>& block) {
  PyMoneroBlockHeader::from_property_tree(node, block);

  for (boost::property_tree::ptree::const_iterator it = node.begin(); it != node.end(); ++it) {
    std::string key = it->first;
    if (key == std::string("blob")) block->m_hex = it->second.data();
    else if (key == std::string("tx_hashes")) {
      for(const auto &hex : it->second) block->m_tx_hashes.push_back(hex.second.data());
    }
    else if (key == std::string("txs")) {
      for (const auto &tx_node : it->second) {
        auto tx = std::make_shared<monero::monero_tx>();
        PyMoneroTx::from_property_tree(tx_node.second, tx);
        block->m_txs.push_back(tx);
      }
    }
    else if (key == std::string("miner_tx")) {
      auto tx = std::make_shared<monero::monero_tx>();
      PyMoneroTx::from_property_tree(it->second, tx);
      tx->m_is_miner_tx = true;
      block->m_miner_tx = tx;
    }
    else if (key == std::string("json")) {
      auto json = it->second.data();
      std::istringstream iss = json.empty() ? std::istringstream() : std::istringstream(json);
      boost::property_tree::ptree json_node;
      boost::property_tree::read_json(iss, json_node);
      PyMoneroBlock::from_property_tree(json_node, block);
    }
  }
}

void PyMoneroBlock::from_property_tree(const boost::property_tree::ptree& node, const std::vector<uint64_t>& heights, std::vector<std::shared_ptr<monero::monero_block>>& blocks) {
  // used by get_blocks_by_height
  const auto& rpc_blocks = node.get_child("blocks");
  const auto& rpc_txs = node.get_child("txs");
  if (rpc_blocks.size() != rpc_txs.size()) {
    throw std::runtime_error("blocks and txs size mismatch");
  }

  auto it_block = rpc_blocks.begin();
  auto it_txs = rpc_txs.begin();
  size_t idx = 0;

  for (; it_block != rpc_blocks.end(); ++it_block, ++it_txs, ++idx) {
    // build block
    auto block = std::make_shared<monero::monero_block>();
    PyMoneroBlock::from_property_tree(it_block->second, block);
    block->m_height = heights.at(idx);
    blocks.push_back(block);

    // build transactions
    std::vector<std::shared_ptr<monero::monero_tx>> txs;
    size_t tx_idx = 0;
    for (const auto& tx_node : it_txs->second) {
      auto tx = std::make_shared<monero::monero_tx>();
      tx->m_hash = block->m_tx_hashes.at(tx_idx++);
      tx->m_is_confirmed = true;
      tx->m_in_tx_pool = false;
      tx->m_is_miner_tx = false;
      tx->m_relay = true;
      tx->m_is_relayed = true;
      tx->m_is_failed = false;
      tx->m_is_double_spend_seen = false;
      PyMoneroTx::from_property_tree(tx_node.second, tx);
      txs.push_back(tx);
    }
    // merge into one block
    block->m_txs.clear();
    for (auto& tx : txs) {
      if (tx->m_block != boost::none) block->merge(block, tx->m_block.get());
      else {
        tx->m_block = block;
        block->m_txs.push_back(tx);
      }
    }
  }
}

void PyMoneroOutput::from_property_tree(const boost::property_tree::ptree& node, const std::shared_ptr<monero_output>& output) {
  for (boost::property_tree::ptree::const_iterator it = node.begin(); it != node.end(); ++it) {
    std::string key = it->first;
    if (key == std::string("gen")) throw std::runtime_error("Output with 'gen' from daemon rpc is miner tx which we ignore (i.e. each miner input is null)");
    else if (key == std::string("key")) {
      auto key_node = it->second;
      for (auto it2 = key_node.begin(); it2 != key_node.end(); ++it2) {
        std::string key_key = it2->first;
        if (key_key == std::string("amount")) output->m_amount = it2->second.get_value<uint64_t>();
        else if (key_key == std::string("k_image")) {
          if (!output->m_key_image) output->m_key_image = std::make_shared<monero::monero_key_image>();
          output->m_key_image.get()->m_hex = it2->second.data();
        }
        else if (key_key == std::string("key_offsets")) {
          auto offsets_node = it2->second;

          for (auto it3 = offsets_node.begin(); it3 != offsets_node.end(); ++it3) {
            output->m_ring_output_indices.push_back(it3->second.get_value<uint64_t>());
          }
        }
      }
    }
    else if (key == std::string("amount")) output->m_amount = it->second.get_value<uint64_t>();
    else if (key == std::string("target")) {
      auto target_node = it->second;

      for(auto it2 = target_node.begin(); it2 != target_node.end(); ++it2) {
        std::string target_key = it2->first;

        if (target_key == std::string("key")) {
          output->m_stealth_public_key = it2->second.data();
        }
        else if (target_key == std::string("tagged_key")) {
          auto tagged_key_node = it2->second;

          for (auto it3 = tagged_key_node.begin(); it3 != tagged_key_node.end(); ++it3) {
            std::string tagged_key_key = it3->first;

            if (tagged_key_key == std::string("key")) {
              output->m_stealth_public_key = it3->second.data();
            }
          }
        }
      }
    }
  }
}

void PyMoneroTx::from_property_tree(const boost::property_tree::ptree& node, const std::shared_ptr<monero::monero_tx>& tx) {  
  std::shared_ptr<monero_block> block = tx->m_block == boost::none ? nullptr : tx->m_block.get();
  std::string as_json;
  std::string tx_json;

  for (boost::property_tree::ptree::const_iterator it = node.begin(); it != node.end(); ++it) {
    std::string key = it->first;
    if (key == std::string("tx_hash") || key == std::string("id_hash")) {
      std::string tx_hash = it->second.data();
      if (!tx_hash.empty()) tx->m_hash = tx_hash;
    }
    else if (key == std::string("block_timestamp")) {
      if (block == nullptr) block = std::make_shared<monero_block>();
      block->m_timestamp = it->second.get_value<uint64_t>();
    }
    else if (key == std::string("block_height")) {
      if (block == nullptr) block = std::make_shared<monero_block>();
      block->m_height = it->second.get_value<uint64_t>();
    }
    else if (key == std::string("last_relayed_time")) {
      if (block == nullptr) block = std::make_shared<monero_block>();
      tx->m_last_relayed_timestamp = it->second.get_value<uint64_t>();
    }
    else if (key == std::string("receive_time") || key == std::string("received_timestamp")) {
      if (block == nullptr) block = std::make_shared<monero_block>();
      tx->m_received_timestamp = it->second.get_value<uint64_t>();
    }
    else if (key == std::string("confirmations")) {
      if (block == nullptr) block = std::make_shared<monero_block>();
      tx->m_num_confirmations = it->second.get_value<uint64_t>();
    }
    else if (key == std::string("in_pool")) {
      if (block == nullptr) block = std::make_shared<monero_block>();
      bool in_pool = it->second.get_value<bool>();
      tx->m_is_confirmed = !in_pool;
      tx->m_in_tx_pool = in_pool;
    }
    else if (key == std::string("double_spend_seen")) {
      if (block == nullptr) block = std::make_shared<monero_block>();
      tx->m_is_double_spend_seen = it->second.get_value<bool>();
    }
    else if (key == std::string("version")) {
      if (block == nullptr) block = std::make_shared<monero_block>();
      tx->m_version = it->second.get_value<uint32_t>();
    }
    else if (key == std::string("vin")) {
      auto &rpc_inputs = it->second;
      bool is_miner_input = false;

      if (rpc_inputs.size() == 1) {
        auto first = rpc_inputs.begin()->second;
        if (first.get_child_optional("gen")) {
          is_miner_input = true;
        }
      }
      // ignore miner input
      // TODO why?
      if (!is_miner_input) {
        std::vector<std::shared_ptr<monero::monero_output>> inputs;
        for (auto &vin_entry : rpc_inputs) {
          auto output = std::make_shared<monero::monero_output>();
          PyMoneroOutput::from_property_tree(vin_entry.second, output);
          output->m_tx = tx;
          inputs.push_back(output);
        }

        tx->m_inputs = inputs;
      }
    }
    else if (key == std::string("vout")) {
      auto node2 = it->second;

      for(auto it2 = node2.begin(); it2 != node2.end(); ++it2) {
        auto output = std::make_shared<monero::monero_output>();
        PyMoneroOutput::from_property_tree(it2->second, output);
        output->m_tx = tx;
        tx->m_outputs.push_back(output);
      }
    }
    else if (key == std::string("rct_signatures")) {
      auto node2 = it->second;

      for(auto it2 = node2.begin(); it2 != node2.end(); ++it2) {
        std::string _key = it2->first;

        if (_key == std::string("txnfee")) {
          tx->m_fee = it2->second.get_value<uint64_t>();
        }
      }
    }
    else if (key == std::string("rctsig_prunable")) {
      // TODO: implement
    }
    else if (key == std::string("unlock_time")) {
      if (block == nullptr) block = std::make_shared<monero_block>();
      tx->m_unlock_time = it->second.get_value<uint64_t>();
    }
    else if (key == std::string("as_json")) as_json = it->second.data();
    else if (key == std::string("tx_json")) tx_json = it->second.data();
    else if (key == std::string("as_hex") || key == std::string("tx_blob")) tx->m_full_hex = it->second.data();
    else if (key == std::string("blob_size")) tx->m_size = it->second.get_value<uint64_t>();
    else if (key == std::string("weight")) tx->m_weight = it->second.get_value<uint64_t>();
    else if (key == std::string("fee")) tx->m_fee = it->second.get_value<uint64_t>();
    else if (key == std::string("relayed")) tx->m_is_relayed = it->second.get_value<bool>();
    else if (key == std::string("output_indices")) {
      auto node2 = it->second;
      std::vector<uint64_t> output_indices;
      for(auto it2 = node2.begin(); it2 != node2.end(); ++it2) {
        output_indices.push_back(it2->second.get_value<uint64_t>());
      }
      tx->m_output_indices = output_indices;
    }
    else if (key == std::string("do_not_relay")) tx->m_relay = !it->second.get_value<bool>();
    else if (key == std::string("kept_by_block")) tx->m_is_kept_by_block = it->second.get_value<bool>();
    else if (key == std::string("signatures")) {
      auto node2 = it->second;
      std::vector<std::string> signatures;
      for(auto it2 = node2.begin(); it2 != node2.end(); ++it2) {
        signatures.push_back(it2->second.data());
      }
      tx->m_signatures = signatures;
    }
    else if (key == std::string("last_failed_height")) {
      uint64_t last_failed_height = it->second.get_value<uint64_t>();
      if (last_failed_height == 0) tx->m_is_failed = false;
      else {
        tx->m_is_failed = true;
        tx->m_last_failed_height = last_failed_height;
      }
    }
    else if (key == std::string("last_failed_hash")) {
      std::string hash = it->second.data();
      if (hash == DEFAULT_ID) tx->m_is_failed = false;
      else {
        tx->m_is_failed = true;
        tx->m_last_failed_hash = hash;
      }
    }
    else if (key == std::string("extra")) {
      auto extra_node = it->second;
      for(auto it_extra = extra_node.begin(); it_extra != extra_node.end(); ++it_extra) {
        tx->m_extra.push_back(it_extra->second.get_value<uint8_t>());
      }
    }
    else if (key == std::string("max_used_block_height")) tx->m_max_used_block_height = it->second.get_value<uint64_t>();
    else if (key == std::string("max_used_block_id_hash")) tx->m_max_used_block_hash = it->second.data();
    else if (key == std::string("prunable_hash")) tx->m_prunable_hash = it->second.data();
    else if (key == std::string("prunable_as_hex")) tx->m_prunable_hex = it->second.data();
    else if (key == std::string("pruned_as_hex")) tx->m_pruned_hex = it->second.data();
  }

  if (block != nullptr) {
    block->m_txs.push_back(tx);
    tx->m_block = block;
  }

  // initialize remaining known fields
  if (tx->m_is_confirmed) {
    tx->m_relay = true;
    tx->m_is_relayed = true;
    tx->m_is_failed = false;
  } else {
    tx->m_num_confirmations = 0;
  }

  if (tx->m_is_failed == boost::none) tx->m_is_failed = false;
  if (!tx->m_output_indices.empty() && !tx->m_outputs.empty())  {
    if (tx->m_output_indices.size() != tx->m_outputs.size()) throw std::runtime_error("Expected outputs count equal to indices count");
    int i = 0;
    for (const auto &output : tx->m_outputs) {
      output->m_index = tx->m_output_indices[i++];
    }
  }

  if (!as_json.empty()) {
    auto n = PyGenUtils::parse_json_string(as_json);
    PyMoneroTx::from_property_tree(n, tx);
  }
  if (!tx_json.empty()) {
    auto n = PyGenUtils::parse_json_string(tx_json);
    PyMoneroTx::from_property_tree(n, tx);
  }

  if (tx->m_is_relayed != true) tx->m_last_relayed_timestamp = boost::none;
}

void PyMoneroTx::from_property_tree(const boost::property_tree::ptree& node, std::vector<std::shared_ptr<monero::monero_tx>>& txs) {
  for (boost::property_tree::ptree::const_iterator it = node.begin(); it != node.end(); ++it) {
    std::string key = it->first;
    
    if (key == std::string("transactions")) {
      auto node2 = it->second;

      for(boost::property_tree::ptree::const_iterator it2 = node2.begin(); it2 != node2.end(); ++it2) {
        auto node3 = it2->second;
        auto tx = std::make_shared<monero::monero_tx>();
        tx->m_is_confirmed = false;
        tx->m_is_miner_tx = false;
        tx->m_in_tx_pool = true;
        tx->m_num_confirmations = 0;
        from_property_tree(node3, tx);
        txs.push_back(tx);
      }

      return;
    }
    else if (key == std::string("txs")) {
      auto node2 = it->second;

      for(boost::property_tree::ptree::const_iterator it2 = node2.begin(); it2 != node2.end(); ++it2) {
        auto node3 = it2->second;
        auto tx = std::make_shared<monero::monero_tx>();
        tx->m_is_miner_tx = false;
        from_property_tree(node3, tx);
        txs.push_back(tx);
      }

      return;
    }
  }
}

void PyMoneroVersion::from_property_tree(const boost::property_tree::ptree& node, const std::shared_ptr<PyMoneroVersion>& version) {
  for (boost::property_tree::ptree::const_iterator it = node.begin(); it != node.end(); ++it) {
    std::string key = it->first;
    if (key == std::string("version")) version->m_number = it->second.get_value<uint32_t>();
    else if (key == std::string("release")) version->m_is_release = it->second.get_value<bool>();
  }
}

void PyMoneroAltChain::from_property_tree(const boost::property_tree::ptree& node, const std::shared_ptr<PyMoneroAltChain>& alt_chain) {
  for (boost::property_tree::ptree::const_iterator it = node.begin(); it != node.end(); ++it) {
    std::string key = it->first;
    if (key == std::string("difficulty")) alt_chain->m_difficulty = it->second.get_value<uint64_t>();
    else if (key == std::string("block_hashes")) {
      for (const auto& child : it->second) alt_chain->m_block_hashes.push_back(child.second.data());
    }
    else if (key == std::string("height")) alt_chain->m_height = it->second.get_value<uint64_t>();
    else if (key == std::string("length")) alt_chain->m_length = it->second.get_value<uint64_t>();
    else if (key == std::string("main_chain_parent_block")) alt_chain->m_main_chain_parent_block_hash = it->second.data();
  }
}

void PyMoneroGetBlockCountResult::from_property_tree(const boost::property_tree::ptree& node, const std::shared_ptr<PyMoneroGetBlockCountResult>& result) {
  for (boost::property_tree::ptree::const_iterator it = node.begin(); it != node.end(); ++it) {
    std::string key = it->first;
    if (key == std::string("count")) result->m_count = it->second.get_value<uint64_t>();
  }
}

void PyMoneroBan::from_property_tree(const boost::property_tree::ptree& node, const std::shared_ptr<PyMoneroBan>& ban) {
  for (boost::property_tree::ptree::const_iterator it = node.begin(); it != node.end(); ++it) {
    std::string key = it->first;
    if (key == std::string("host")) ban->m_host = it->second.data();
    else if (key == std::string("ip")) ban->m_ip = it->second.get_value<int>();
    else if (key == std::string("ban")) ban->m_is_banned = it->second.get_value<bool>();
    else if (key == std::string("seconds")) ban->m_seconds = it->second.get_value<uint64_t>();
  }
}

void PyMoneroBan::from_property_tree(const boost::property_tree::ptree& node, std::vector<std::shared_ptr<PyMoneroBan>>& bans) {
  for (boost::property_tree::ptree::const_iterator it = node.begin(); it != node.end(); ++it) {
    std::string key = it->first;
    if (key == std::string("bans")) {
      auto node2 = it->second;
      for (auto it2 = node2.begin(); it2 != node2.end(); ++it2) {
        auto ban = std::make_shared<PyMoneroBan>();
        PyMoneroBan::from_property_tree(it2->second, ban);
        bans.push_back(ban);
      }
    }
  }
}

void PyMoneroPruneResult::from_property_tree(const boost::property_tree::ptree& node, const std::shared_ptr<PyMoneroPruneResult>& result) {
  for (boost::property_tree::ptree::const_iterator it = node.begin(); it != node.end(); ++it) {
    std::string key = it->first;
    if (key == std::string("pruned")) result->m_is_pruned = it->second.get_value<bool>();
    else if (key == std::string("pruning_seed")) result->m_pruning_seed = it->second.get_value<int>();
  }
}

void PyMoneroMiningStatus::from_property_tree(const boost::property_tree::ptree& node, const std::shared_ptr<PyMoneroMiningStatus>& status) {
  for (boost::property_tree::ptree::const_iterator it = node.begin(); it != node.end(); ++it) {
    std::string key = it->first;
    if (key == std::string("active")) status->m_is_active = it->second.get_value<bool>();
    else if (key == std::string("is_background_mining_enabled")) status->m_is_background = it->second.get_value<bool>();
    else if (key == std::string("address") && !it->second.data().empty()) status->m_address = it->second.data();
    else if (key == std::string("speed")) status->m_speed = it->second.get_value<uint64_t>();
    else if (key == std::string("threads_count")) status->m_num_threads = it->second.get_value<int>();
  }

  if (status->m_is_active != boost::none && *status->m_is_active == false) {
    status->m_is_background = boost::none;
    status->m_address = boost::none;
  }
}

std::vector<std::string> PyMoneroTxHashes::from_property_tree(const boost::property_tree::ptree& node) {
  std::vector<std::string> result;
  for (boost::property_tree::ptree::const_iterator it = node.begin(); it != node.end(); ++it) {
    std::string key = it->first;
    
    if (key == std::string("tx_hashes")) {
      auto node2 = it->second;

      for(boost::property_tree::ptree::const_iterator it2 = node2.begin(); it2 != node2.end(); ++it2) {
        result.push_back(it2->second.data());
      }
    }
  }
  return result;
}

void PyMoneroMinerTxSum::from_property_tree(const boost::property_tree::ptree& node, const std::shared_ptr<PyMoneroMinerTxSum>& sum) {
  for (boost::property_tree::ptree::const_iterator it = node.begin(); it != node.end(); ++it) {
    std::string key = it->first;
    if (key == std::string("emission_amount")) sum->m_emission_sum = it->second.get_value<uint64_t>();
    else if (key == std::string("fee_amount")) sum->m_fee_sum = it->second.get_value<uint64_t>();
  }
}

void PyMoneroBlockTemplate::from_property_tree(const boost::property_tree::ptree& node, const std::shared_ptr<PyMoneroBlockTemplate>& tmplt) {
  for (boost::property_tree::ptree::const_iterator it = node.begin(); it != node.end(); ++it) {
    std::string key = it->first;
    if (key == std::string("blocktemplate_blob")) tmplt->m_block_template_blob = it->second.data();
    else if (key == std::string("blockhashing_blob")) tmplt->m_block_hashing_blob = it->second.data();
    else if (key == std::string("difficulty")) tmplt->m_difficulty = it->second.get_value<uint64_t>();
    else if (key == std::string("expected_reward")) tmplt->m_expected_reward = it->second.get_value<uint64_t>();
    else if (key == std::string("height")) tmplt->m_height = it->second.get_value<uint64_t>();
    else if (key == std::string("prev_hash")) tmplt->m_prev_hash = it->second.data();
    else if (key == std::string("reserved_offset")) tmplt->m_reserved_offset = it->second.get_value<uint64_t>();
    else if (key == std::string("seed_height")) tmplt->m_seed_height = it->second.get_value<uint64_t>();
    else if (key == std::string("seed_hash")) tmplt->m_seed_hash = it->second.data();
    else if (key == std::string("next_seed_hash")) tmplt->m_next_seed_hash = it->second.data();
  }
}

void PyMoneroConnectionSpan::from_property_tree(const boost::property_tree::ptree& node, const std::shared_ptr<PyMoneroConnectionSpan>& span) {
  for (boost::property_tree::ptree::const_iterator it = node.begin(); it != node.end(); ++it) {
    std::string key = it->first;
    if (key == std::string("connection_id")) span->m_connection_id = it->second.data();
    else if (key == std::string("nblocks")) span->m_num_blocks = it->second.get_value<uint64_t>();
    else if (key == std::string("remote_address")) span->m_remote_address = it->second.data();
    else if (key == std::string("rate")) span->m_rate = it->second.get_value<uint64_t>();
    else if (key == std::string("speed")) span->m_speed = it->second.get_value<uint64_t>();
    else if (key == std::string("size")) span->m_size = it->second.get_value<uint64_t>();
    else if (key == std::string("start_block_height")) span->m_start_height = it->second.get_value<uint64_t>();
  }
}

void PyMoneroPeer::from_property_tree(const boost::property_tree::ptree& node, const std::shared_ptr<PyMoneroPeer>& peer) {
  for (boost::property_tree::ptree::const_iterator it = node.begin(); it != node.end(); ++it) {
    std::string key = it->first;
    if (key == std::string("host")) peer->m_host = it->second.data();
    else if (key == std::string("address")) peer->m_address = it->second.data();
    else if (key == std::string("current_download")) peer->m_current_download = it->second.get_value<uint64_t>();
    else if (key == std::string("current_upload")) peer->m_current_upload = it->second.get_value<uint64_t>();
    else if (key == std::string("avg_download")) peer->m_avg_download = it->second.get_value<uint64_t>();
    else if (key == std::string("avg_upload")) peer->m_avg_upload = it->second.get_value<uint64_t>();
    else if (key == std::string("connection_id")) peer->m_hash = it->second.data();
    else if (key == std::string("height")) peer->m_height = it->second.get_value<uint64_t>();
    else if (key == std::string("incoming")) peer->m_is_incoming = it->second.get_value<bool>();
    else if (key == std::string("live_time")) peer->m_live_time = it->second.get_value<uint64_t>();
    else if (key == std::string("local_ip")) peer->m_is_local_ip = it->second.get_value<bool>();
    else if (key == std::string("localhost")) peer->m_is_local_host = it->second.get_value<bool>();
    else if (key == std::string("recv_count")) peer->m_num_receives = it->second.get_value<int>();
    else if (key == std::string("send_count")) peer->m_num_sends = it->second.get_value<int>();
    else if (key == std::string("recv_idle_time")) peer->m_receive_idle_time = it->second.get_value<uint64_t>();
    else if (key == std::string("send_idle_time")) peer->m_send_idle_time = it->second.get_value<uint64_t>();
    else if (key == std::string("state")) peer->m_state = it->second.data();
    else if (key == std::string("support_flags")) peer->m_num_support_flags = it->second.get_value<int>();
    else if (key == std::string("id") || key == std::string("peer_id")) peer->m_id = it->second.data();
    else if (key == std::string("last_seen")) peer->m_last_seen_timestamp = it->second.get_value<uint64_t>();
    else if (key == std::string("port")) peer->m_port = it->second.get_value<int>();
    else if (key == std::string("rpc_port")) peer->m_rpc_port = it->second.get_value<int>();
    else if (key == std::string("pruning_seed")) peer->m_pruning_seed = it->second.get_value<int>();
    else if (key == std::string("rpc_credits_per_hash")) peer->m_rpc_credits_per_hash = it->second.get_value<uint64_t>();
    else if (key == std::string("address_type")) {
      int rpc_type = it->second.get_value<int>();
      if (rpc_type == 0) {
        peer->m_connection_type = PyMoneroConnectionType::INVALID;
      }
      else if (rpc_type == 1) {
        peer->m_connection_type = PyMoneroConnectionType::IPV4;
      }
      else if (rpc_type == 2) {
        peer->m_connection_type = PyMoneroConnectionType::IPV6;
      }
      else if (rpc_type == 3) {
        peer->m_connection_type = PyMoneroConnectionType::TOR;
      }
      else if (rpc_type == 4) {
        peer->m_connection_type = PyMoneroConnectionType::I2P;
      }
      else throw std::runtime_error("Invalid RPC peer type, expected 0-4: " + std::to_string(rpc_type));
    }
  }
}

void PyMoneroPeer::from_property_tree(const boost::property_tree::ptree& node, std::vector<std::shared_ptr<PyMoneroPeer>>& peers) {
  for (boost::property_tree::ptree::const_iterator it = node.begin(); it != node.end(); ++it) {
    std::string key = it->first;
    bool is_online = key == std::string("white_list");
    if (key == std::string("connections") || is_online || key == std::string("gray_list") ) {
      auto node2 = it->second;
      for (auto it2 = node2.begin(); it2 != node2.end(); ++it2) {
        auto peer = std::make_shared<PyMoneroPeer>();
        PyMoneroPeer::from_property_tree(it2->second, peer);
        peer->m_is_online = is_online;
        peers.push_back(peer);
      }
    }
  }
}

void PyMoneroSubmitTxResult::from_property_tree(const boost::property_tree::ptree& node, const std::shared_ptr<PyMoneroSubmitTxResult>& result) {
  for (boost::property_tree::ptree::const_iterator it = node.begin(); it != node.end(); ++it) {
    std::string key = it->first;
    if (key == std::string("double_spend")) result->m_is_double_spend = it->second.get_value<bool>();
    else if (key == std::string("fee_too_low")) result->m_is_fee_too_low = it->second.get_value<bool>();
    else if (key == std::string("invalid_input")) result->m_has_invalid_input = it->second.get_value<bool>();
    else if (key == std::string("invalid_output")) result->m_has_invalid_output = it->second.get_value<bool>();
    else if (key == std::string("too_few_outputs")) result->m_has_too_few_outputs = it->second.get_value<bool>();
    else if (key == std::string("low_mixin")) result->m_is_mixin_too_low = it->second.get_value<bool>();
    else if (key == std::string("not_relayed")) result->m_is_relayed = !it->second.get_value<bool>();
    else if (key == std::string("overspend")) result->m_is_overspend = it->second.get_value<bool>();
    else if (key == std::string("reason")) result->m_reason = it->second.data();
    else if (key == std::string("too_big")) result->m_is_too_big = it->second.get_value<bool>();
    else if (key == std::string("sanity_check_failed")) result->m_sanity_check_failed = it->second.get_value<bool>();
    else if (key == std::string("credits")) result->m_credits = it->second.get_value<uint64_t>();
    else if (key == std::string("top_hash")) {
      std::string top_hash = it->second.data();
      if (!top_hash.empty()) result->m_top_block_hash = top_hash;
    }
    else if (key == std::string("tx_extra_too_big")) result->m_is_tx_extra_too_big = it->second.get_value<bool>();
    else if (key == std::string("nonzero_unlock_time")) result->m_is_nonzero_unlock_time = it->second.get_value<bool>();
  }
}

void PyMoneroOutputDistributionEntry::from_property_tree(const boost::property_tree::ptree& node, const std::shared_ptr<PyMoneroOutputDistributionEntry>& entry) {
  for (boost::property_tree::ptree::const_iterator it = node.begin(); it != node.end(); ++it) {
    std::string key = it->first;
    if (key == std::string("amount")) entry->m_amount = it->second.get_value<uint64_t>();
    else if (key == std::string("base")) entry->m_base = it->second.get_value<int>();
    else if (key == std::string("distribution")) {
      auto node2 = it->second;
      for(auto it2 = node2.begin(); it2 != node2.end(); ++it2) {
        entry->m_distribution.push_back(it2->second.get_value<int>());
      }
    }
    else if (key == std::string("start_height")) entry->m_start_height = it->second.get_value<uint64_t>();
  }
}

void PyMoneroOutputHistogramEntry::from_property_tree(const boost::property_tree::ptree& node, const std::shared_ptr<PyMoneroOutputHistogramEntry>& entry) {
  for (boost::property_tree::ptree::const_iterator it = node.begin(); it != node.end(); ++it) {
    std::string key = it->first;
    if (key == std::string("amount")) entry->m_amount = it->second.get_value<uint64_t>();
    else if (key == std::string("total_instances")) entry->m_num_instances = it->second.get_value<uint64_t>();
    else if (key == std::string("unlocked_instances")) entry->m_unlocked_instances = it->second.get_value<uint64_t>();
    else if (key == std::string("recent_instances")) entry->m_recent_instances = it->second.get_value<uint64_t>();
  }
}

void PyMoneroOutputHistogramEntry::from_property_tree(const boost::property_tree::ptree& node, std::vector<std::shared_ptr<PyMoneroOutputHistogramEntry>>& entries) {
  for (boost::property_tree::ptree::const_iterator it = node.begin(); it != node.end(); ++it) {
    std::string key = it->first;
    
    if (key == std::string("histogram")) {
      auto node2 = it->second;

      for(boost::property_tree::ptree::const_iterator it2 = node2.begin(); it2 != node2.end(); ++it2) {
        auto entry = std::make_shared<PyMoneroOutputHistogramEntry>();
        from_property_tree(node2, entry);
        entries.push_back(entry);
      }
    }
  }
}

void PyMoneroTxPoolStats::from_property_tree(const boost::property_tree::ptree& node, const std::shared_ptr<PyMoneroTxPoolStats>& stats) {
  for (boost::property_tree::ptree::const_iterator it = node.begin(); it != node.end(); ++it) {
    std::string key = it->first;
    if (key == std::string("txs_total")) stats->m_num_txs = it->second.get_value<int>();
    else if (key == std::string("num_not_relayed")) stats->m_num_not_relayed = it->second.get_value<int>();
    else if (key == std::string("num_failing")) stats->m_num_failing = it->second.get_value<int>();
    else if (key == std::string("num_double_spends")) stats->m_num_double_spends = it->second.get_value<int>();
    else if (key == std::string("num10m")) stats->m_num10m = it->second.get_value<int>();
    else if (key == std::string("fee_total")) stats->m_fee_total = it->second.get_value<uint64_t>();
    else if (key == std::string("bytes_max")) stats->m_bytes_max = it->second.get_value<uint64_t>();
    else if (key == std::string("bytes_med")) stats->m_bytes_med = it->second.get_value<uint64_t>();
    else if (key == std::string("bytes_min")) stats->m_bytes_min = it->second.get_value<uint64_t>();
    else if (key == std::string("bytes_total")) stats->m_bytes_total = it->second.get_value<uint64_t>();
    else if (key == std::string("histo_98pc")) stats->m_histo98pc = it->second.get_value<uint64_t>();
    else if (key == std::string("oldest")) stats->m_oldest_timestamp = it->second.get_value<uint64_t>();
  }
}

void PyMoneroDaemonUpdateCheckResult::from_property_tree(const boost::property_tree::ptree& node, const std::shared_ptr<PyMoneroDaemonUpdateCheckResult>& check) {
  for (boost::property_tree::ptree::const_iterator it = node.begin(); it != node.end(); ++it) {
    std::string key = it->first;
    if (key == std::string("update")) check->m_is_update_available = it->second.get_value<bool>();
    else if (key == std::string("version") && !it->second.data().empty()) check->m_version = it->second.data();
    else if (key == std::string("hash") && !it->second.data().empty()) check->m_hash = it->second.data();
    else if (key == std::string("auto_uri") && !it->second.data().empty()) check->m_auto_uri = it->second.data();
    else if (key == std::string("user_uri") && !it->second.data().empty()) check->m_user_uri = it->second.data();
  }
}

void PyMoneroDaemonUpdateDownloadResult::from_property_tree(const boost::property_tree::ptree& node, const std::shared_ptr<PyMoneroDaemonUpdateDownloadResult>& check) {
  PyMoneroDaemonUpdateCheckResult::from_property_tree(node, check);
  
  for (boost::property_tree::ptree::const_iterator it = node.begin(); it != node.end(); ++it) {
    std::string key = it->first;
    if (key == std::string("download_path") && !it->second.data().empty()) check->m_download_path = it->second.data();
  }
}

void PyMoneroFeeEstimate::from_property_tree(const boost::property_tree::ptree& node, const std::shared_ptr<PyMoneroFeeEstimate>& estimate) {    
  for (boost::property_tree::ptree::const_iterator it = node.begin(); it != node.end(); ++it) {
    std::string key = it->first;
    if (key == std::string("fee")) estimate->m_fee = it->second.get_value<uint64_t>();
    else if (key == std::string("quantization_mask")) estimate->m_quantization_mask = it->second.get_value<uint64_t>();
    else if (key == std::string("fees")) {
      auto node2 = it->second;
      for (boost::property_tree::ptree::const_iterator it2 = node2.begin(); it2 != node2.end(); ++it2) {
        uint64_t fee = it2->second.get_value<uint64_t>();
        estimate->m_fees.push_back(fee);
      }
    }
  }
}

void PyMoneroDaemonInfo::from_property_tree(const boost::property_tree::ptree& node, const std::shared_ptr<PyMoneroDaemonInfo>& info) {
  for (boost::property_tree::ptree::const_iterator it = node.begin(); it != node.end(); ++it) {
    std::string key = it->first;
    if (key == std::string("version")) info->m_version = it->second.data();
    else if (key == std::string("alt_blocks_count")) info->m_num_alt_blocks = it->second.get_value<uint64_t>();
    else if (key == std::string("block_size_limit")) info->m_block_size_limit = it->second.get_value<uint64_t>();
    else if (key == std::string("block_size_median")) info->m_block_size_median = it->second.get_value<uint64_t>();
    else if (key == std::string("block_weight_limit")) info->m_block_weight_limit = it->second.get_value<uint64_t>();
    else if (key == std::string("block_weight_median")) info->m_block_weight_median = it->second.get_value<uint64_t>();
    else if (key == std::string("bootstrap_daemon_address") && !it->second.data().empty()) info->m_bootstrap_daemon_address = it->second.data();
    else if (key == std::string("difficulty")) info->m_difficulty = it->second.get_value<uint64_t>();
    else if (key == std::string("cumulative_difficulty")) info->m_cumulative_difficulty = it->second.get_value<uint64_t>();
    else if (key == std::string("free_space")) info->m_free_space = it->second.get_value<uint64_t>();
    else if (key == std::string("grey_peerlist_size")) info->m_num_offline_peers = it->second.get_value<int>();
    else if (key == std::string("white_peerlist_size")) info->m_num_online_peers = it->second.get_value<int>();
    else if (key == std::string("height")) info->m_height = it->second.get_value<uint64_t>();
    else if (key == std::string("height_without_bootstrap")) info->m_height_without_bootstrap = it->second.get_value<uint64_t>();
    else if (key == std::string("nettype")) {
      std::string nettype = it->second.data();
      if (nettype == std::string("mainnet") || nettype == std::string("fakechain")) info->m_network_type = monero::monero_network_type::MAINNET;
      else if (nettype == std::string("testnet")) info->m_network_type = monero::monero_network_type::TESTNET;
      else if (nettype == std::string("stagenet")) info->m_network_type = monero::monero_network_type::STAGENET;
    }
    else if (key == std::string("offline")) info->m_is_offline = it->second.get_value<bool>();
    else if (key == std::string("incoming_connections_count")) info->m_num_incoming_connections = it->second.get_value<int>();
    else if (key == std::string("outgoing_connections_count")) info->m_num_outgoing_connections = it->second.get_value<int>();
    else if (key == std::string("rpc_connections_count")) info->m_num_rpc_connections = it->second.get_value<int>();
    else if (key == std::string("start_time")) info->m_start_timestamp = it->second.get_value<uint64_t>();
    else if (key == std::string("adjusted_time")) info->m_adjusted_timestamp = it->second.get_value<uint64_t>();
    else if (key == std::string("target")) info->m_target = it->second.get_value<uint64_t>();
    else if (key == std::string("target_height")) info->m_target_height = it->second.get_value<uint64_t>();
    else if (key == std::string("top_block_hash") || key == std::string("top_hash")) {
      std::string top_hash = it->second.data();
      if (!top_hash.empty()) info->m_top_block_hash = top_hash;
    }
    else if (key == std::string("tx_count")) info->m_num_txs = it->second.get_value<int>();
    else if (key == std::string("tx_pool_size")) info->m_num_txs_pool = it->second.get_value<int>();
    else if (key == std::string("was_bootstrap_ever_used")) info->m_was_bootstrap_ever_used = it->second.get_value<bool>();
    else if (key == std::string("database_size")) info->m_database_size = it->second.get_value<uint64_t>();
    else if (key == std::string("update_available")) info->m_update_available = it->second.get_value<bool>();
    else if (key == std::string("credits")) info->m_credits = it->second.get_value<uint64_t>();
    else if (key == std::string("busy_syncing")) info->m_is_busy_syncing = it->second.get_value<bool>();
    else if (key == std::string("synchronized")) info->m_is_synchronized = it->second.get_value<bool>();
    else if (key == std::string("restricted")) info->m_is_restricted = it->second.get_value<bool>();
  }
}

void PyMoneroDaemonSyncInfo::from_property_tree(const boost::property_tree::ptree& node, const std::shared_ptr<PyMoneroDaemonSyncInfo>& info) {
  for (boost::property_tree::ptree::const_iterator it = node.begin(); it != node.end(); ++it) {
    std::string key = it->first;
    if (key == std::string("height")) info->m_height = it->second.get_value<uint64_t>();
    else if (key == std::string("target_height")) info->m_target_height = it->second.get_value<uint64_t>();
    else if (key == std::string("next_needed_pruning_seed")) info->m_next_needed_pruning_seed = it->second.get_value<int>();
    // TODO implement overview field
    //else if (key == std::string("overview") && !it->second.data().empty()) info->m_overview = it->second.data();
    else if (key == std::string("credits")) info->m_credits = it->second.get_value<uint64_t>();
    else if (key == std::string("top_hash")) {
      std::string top_hash = it->second.data();
      if (!top_hash.empty()) info->m_top_block_hash = top_hash;
    }
  }
}

void PyMoneroHardForkInfo::from_property_tree(const boost::property_tree::ptree& node, const std::shared_ptr<PyMoneroHardForkInfo>& info) {
  for (boost::property_tree::ptree::const_iterator it = node.begin(); it != node.end(); ++it) {
    std::string key = it->first;
    if (key == std::string("earliest_height")) info->m_earliest_height = it->second.get_value<uint64_t>();
    else if (key == std::string("enabled")) info->m_is_enabled = it->second.get_value<bool>();
    else if (key == std::string("state")) info->m_state = it->second.get_value<int>();
    else if (key == std::string("threshold")) info->m_threshold = it->second.get_value<int>();
    else if (key == std::string("version")) info->m_version = it->second.get_value<int>();
    else if (key == std::string("votes")) info->m_num_votes = it->second.get_value<int>();
    else if (key == std::string("window")) info->m_window = it->second.get_value<int>();
    else if (key == std::string("voting")) info->m_voting = it->second.get_value<int>();
    else if (key == std::string("credits")) info->m_credits = it->second.get_value<uint64_t>();
    else if (key == std::string("top_hash")) {
      std::string top_hash = it->second.data();
      if (!top_hash.empty()) info->m_top_block_hash = top_hash;
    }
  }
}

void PyMoneroGetAltBlocksHashesResponse::from_property_tree(const boost::property_tree::ptree& node, std::vector<std::string>& block_hashes) {
  for (boost::property_tree::ptree::const_iterator it = node.begin(); it != node.end(); ++it) {
    std::string key = it->first;
    if (key == std::string("blks_hashes")) {
      auto node2 = it->second;
      for(auto it2 = node2.begin(); it2 != node2.end(); ++it2) {
        block_hashes.push_back(it2->second.data());
      }
    }
  }
}

void PyMoneroBandwithLimits::from_property_tree(const boost::property_tree::ptree& node, const std::shared_ptr<PyMoneroBandwithLimits>& limits) {
  for (boost::property_tree::ptree::const_iterator it = node.begin(); it != node.end(); ++it) {
    std::string key = it->first;
    if (key == std::string("limit_up")) limits->m_up = it->second.get_value<int>();
    else if (key == std::string("limit_down")) limits->m_down = it->second.get_value<int>();
  }
}

void PyMoneroGetHeightResponse::from_property_tree(const boost::property_tree::ptree& node, const std::shared_ptr<PyMoneroGetHeightResponse>& response) {
  for (boost::property_tree::ptree::const_iterator it = node.begin(); it != node.end(); ++it) {
    std::string key = it->first;
    if (key == std::string("height")) response->m_height = it->second.get_value<uint64_t>();
    else if (key == std::string("untrusted")) response->m_untrusted = it->second.get_value<bool>();
  }
}

rapidjson::Value PyMoneroDownloadUpdateParams::to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const { 
  rapidjson::Value root(rapidjson::kObjectType); 
  rapidjson::Value value_str(rapidjson::kStringType);

  if (m_command != boost::none) monero_utils::add_json_member("command", m_command.get(), allocator, root, value_str);
  if (m_path != boost::none) monero_utils::add_json_member("path", m_path.get(), allocator, root, value_str);

  return root;
}

rapidjson::Value PyMoneroCheckUpdateParams::to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const { 
  rapidjson::Value root(rapidjson::kObjectType); 
  rapidjson::Value value_str(rapidjson::kStringType);
  if (m_command != boost::none) monero_utils::add_json_member("command", m_command.get(), allocator, root, value_str);
  return root;
}

rapidjson::Value PyMoneroStartMiningParams::to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const { 
  rapidjson::Value root(rapidjson::kObjectType); 
  rapidjson::Value value_str(rapidjson::kStringType);
  rapidjson::Value value_num(rapidjson::kNumberType);
  if (m_address != boost::none) monero_utils::add_json_member("miner_address", m_address.get(), allocator, root, value_str);
  if (m_num_threads != boost::none) monero_utils::add_json_member("threads_count", m_num_threads.get(), allocator, root, value_num);
  if (m_is_background != boost::none) monero_utils::add_json_member("do_background_mining", m_is_background.get(), allocator, root);
  if (m_ignore_battery != boost::none) monero_utils::add_json_member("ignore_battery", m_ignore_battery.get(), allocator, root);
  return root;
}

rapidjson::Value PyMoneroPruneBlockchainParams::to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const { 
  rapidjson::Value root(rapidjson::kObjectType); 
  if (m_check != boost::none) monero_utils::add_json_member("check", m_check.get(), allocator, root);
  return root;
}

rapidjson::Value PyMoneroSubmitBlocksParams::to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const {
  return monero_utils::to_rapidjson_val(allocator, m_block_blobs);
}

rapidjson::Value PyMoneroGetBlockParams::to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const { 
  rapidjson::Value root(rapidjson::kObjectType); 
  rapidjson::Value value_str(rapidjson::kStringType);
  rapidjson::Value value_num(rapidjson::kNumberType);

  if (m_hash != boost::none) monero_utils::add_json_member("hash", m_hash.get(), allocator, root, value_str);
  if (m_height != boost::none) monero_utils::add_json_member("height", m_height.get(), allocator, root, value_num);
  if (m_fill_pow_hash != boost::none) monero_utils::add_json_member("fill_pow_hash", m_fill_pow_hash.get(), allocator, root);

  return root; 
}

rapidjson::Value PyMoneroGetBlockRangeParams::to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const { 
  rapidjson::Value root(rapidjson::kObjectType); 
  rapidjson::Value value_num(rapidjson::kNumberType);

  if (m_start_height != boost::none) monero_utils::add_json_member("start_height", m_start_height.get(), allocator, root, value_num);
  if (m_end_height != boost::none) monero_utils::add_json_member("end_height", m_end_height.get(), allocator, root, value_num);

  return root;
}

rapidjson::Value PyMoneroGetBlockHashParams::to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const {
  std::vector<uint64_t> params;
  if (m_height != boost::none) params.push_back(m_height.get());
  return monero_utils::to_rapidjson_val(allocator, params);
}

rapidjson::Value PyMoneroGetBlockTemplateParams::to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const { 
  rapidjson::Value root(rapidjson::kObjectType); 
  rapidjson::Value value_str(rapidjson::kStringType);
  rapidjson::Value value_num(rapidjson::kNumberType);

  if (m_wallet_address != boost::none) monero_utils::add_json_member("wallet_address", m_wallet_address.get(), allocator, root, value_str);
  if (m_reserve_size != boost::none) monero_utils::add_json_member("reserve_size", m_reserve_size.get(), allocator, root, value_num);

  return root; 
}

rapidjson::Value PyMoneroGetBlocksByHeightRequest::to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const {
  rapidjson::Value root(rapidjson::kObjectType);
  if (!m_heights.empty()) root.AddMember("heights", monero_utils::to_rapidjson_val(allocator, m_heights), allocator);
  return root;
}

rapidjson::Value PyMoneroBan::to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const { 
  rapidjson::Value root(rapidjson::kObjectType); 
  rapidjson::Value value_str(rapidjson::kStringType);
  rapidjson::Value value_num(rapidjson::kNumberType);
  if (m_host != boost::none) monero_utils::add_json_member("host", m_host.get(), allocator, root, value_str);
  if (m_ip != boost::none) monero_utils::add_json_member("ip", m_ip.get(), allocator, root, value_num);
  if (m_is_banned != boost::none) monero_utils::add_json_member("ban", m_is_banned.get(), allocator, root);
  if (m_seconds != boost::none) monero_utils::add_json_member("seconds", m_seconds.get(), allocator, root, value_num);
  return root;
}

rapidjson::Value PyMoneroSubmitTxParams::to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const { 
  rapidjson::Value root(rapidjson::kObjectType); 
  rapidjson::Value value_str(rapidjson::kStringType);
  if (m_tx_hex != boost::none) monero_utils::add_json_member("tx_as_hex", m_tx_hex.get(), allocator, root, value_str);
  if (m_do_not_relay != boost::none) monero_utils::add_json_member("do_not_relay", m_do_not_relay.get(), allocator, root);
  return root; 
}

rapidjson::Value PyMoneroRelayTxParams::to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const { 
  rapidjson::Value root(rapidjson::kObjectType); 
  if (!m_tx_hashes.empty()) root.AddMember("txids", monero_utils::to_rapidjson_val(allocator, m_tx_hashes), allocator);
  return root; 
}

rapidjson::Value PyMoneroBandwithLimits::to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const { 
  rapidjson::Value root(rapidjson::kObjectType); 
  rapidjson::Value value_num(rapidjson::kNumberType);
  if (m_up != boost::none) monero_utils::add_json_member("limit_up", m_up.get(), allocator, root, value_num);
  if (m_down != boost::none) monero_utils::add_json_member("limit_down", m_down.get(), allocator, root, value_num);
  return root; 
}

rapidjson::Value PyMoneroPeerLimits::to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const { 
  rapidjson::Value root(rapidjson::kObjectType); 
  rapidjson::Value value_num(rapidjson::kNumberType);
  if (m_in_peers != boost::none) monero_utils::add_json_member("in_peers", m_in_peers.get(), allocator, root, value_num);
  if (m_out_peers != boost::none) monero_utils::add_json_member("out_peers", m_out_peers.get(), allocator, root, value_num);
  return root; 
}

rapidjson::Value PyMoneroGetMinerTxSumParams::to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const { 
  rapidjson::Value root(rapidjson::kObjectType); 
  rapidjson::Value value_num(rapidjson::kNumberType);
  if (m_height != boost::none) monero_utils::add_json_member("height", m_height.get(), allocator, root, value_num);
  if (m_count != boost::none) monero_utils::add_json_member("count", m_count.get(), allocator, root, value_num);
  return root; 
}

rapidjson::Value PyMoneroGetFeeEstimateParams::to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const { 
  rapidjson::Value root(rapidjson::kObjectType); 
  rapidjson::Value value_num(rapidjson::kNumberType);
  if (m_grace_blocks != boost::none) monero_utils::add_json_member("grace_blocks", m_grace_blocks.get(), allocator, root, value_num);
  return root; 
}

rapidjson::Value PyMoneroSetBansParams::to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const { 
  rapidjson::Value root(rapidjson::kObjectType); 
  if (!m_bans.empty()) root.AddMember("bans", monero_utils::to_rapidjson_val(allocator, m_bans), allocator);
  return root; 
}

rapidjson::Value PyMoneroGetTxsParams::to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const { 
  rapidjson::Value root(rapidjson::kObjectType); 
  if (!m_tx_hashes.empty()) root.AddMember("txs_hashes", monero_utils::to_rapidjson_val(allocator, m_tx_hashes), allocator);
  if (m_prune != boost::none) monero_utils::add_json_member("prune", m_prune.get(), allocator, root);
  if (m_decode_as_json != boost::none) monero_utils::add_json_member("decode_as_json", m_decode_as_json.get(), allocator, root);
  return root; 
}

rapidjson::Value PyMoneroGetOutputHistrogramParams::to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const { 
  rapidjson::Value root(rapidjson::kObjectType); 
  rapidjson::Value value_num(rapidjson::kNumberType);
  if (!m_amounts.empty()) root.AddMember("amounts", monero_utils::to_rapidjson_val(allocator, m_amounts), allocator);
  if (m_min_count != boost::none) monero_utils::add_json_member("min_count", m_min_count.get(), allocator, root, value_num);
  if (m_max_count != boost::none) monero_utils::add_json_member("max_count", m_max_count.get(), allocator, root, value_num);
  if (m_is_unlocked != boost::none) monero_utils::add_json_member("is_unlocked", m_is_unlocked.get(), allocator, root);
  if (m_recent_cutoff != boost::none) monero_utils::add_json_member("recent_cutoff", m_recent_cutoff.get(), allocator, root, value_num);
  return root; 
}

rapidjson::Value PyMoneroIsKeyImageSpentParams::to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const { 
  rapidjson::Value root(rapidjson::kObjectType); 
  if (!m_key_images.empty()) root.AddMember("key_images", monero_utils::to_rapidjson_val(allocator, m_key_images), allocator);
  return root; 
}
