#include "py_monero_common.h"

int PyMoneroConnectionPriorityComparator::compare(int p1, int p2) {
  if (p1 == p2) return 0;
  if (p1 == 0) return -1;
  if (p2 == 0) return 1;
  return p2 - p1;
}

int PyMoneroTxHeightComparator::compare(const std::shared_ptr<monero::monero_tx> &tx1, const std::shared_ptr<monero::monero_tx> &tx2) {
  if (tx1->get_height() == boost::none && tx2->get_height() == boost::none) return 0; // both unconfirmed
  else if (tx1->get_height() == boost::none) return 1;   // tx1 is unconfirmed
  else if (tx2->get_height() == boost::none) return -1;  // tx2 is unconfirmed
  int diff = tx1->get_height().get() - tx2->get_height().get();
  if (diff != 0) return diff;
  auto txs1 = tx1->m_block.get()->m_txs;
  auto txs2 = tx2->m_block.get()->m_txs;
  auto it1 = find(txs1.begin(), txs1.end(), tx1);
  auto it2 = find(txs2.begin(), txs2.end(), tx2);
  if (it1 == txs1.end() && it2 == txs2.end()) return 0;
  else if (it1 == txs1.end()) return 1;
  else if (it2 == txs2.end()) return -1;

  return std::distance(txs1.begin(), it1) - std::distance(txs2.begin(), it2); // txs are in the same block so retain their original order
}

py::object PyGenUtils::convert_value(const std::string& val) {
  if (val == "true") return py::bool_(true);
  if (val == "false") return py::bool_(false);

  try {
    std::size_t pos;
    int i = std::stoi(val, &pos);
    if (pos == val.size()) return py::int_(i);
  } catch (...) {}

  try {
    std::size_t pos;
    double d = std::stod(val, &pos);
    if (pos == val.size()) return py::float_(d);
  } catch (...) {}

  return py::str(val);
}

py::object PyGenUtils::ptree_to_pyobject(const boost::property_tree::ptree& tree) {
  if (tree.empty()) {
    return convert_value(tree.get_value<std::string>());
  }

  bool is_array = true;
  for (const auto& child : tree) {
    if (child.first != "") {
      is_array = false;
      break;
    }
  }

  if (is_array) {
    py::list lst;
    for (const auto& child : tree) {
      lst.append(ptree_to_pyobject(child.second));
    }
    return lst;
  } 
  else {
    py::dict d;
    if (!tree.get_value<std::string>().empty()) {
      d["__value__"] = convert_value(tree.get_value<std::string>());
    }
    for (const auto& child : tree) {
      d[py::str(child.first)] = ptree_to_pyobject(child.second);
    }

    return d;
  }
}

boost::property_tree::ptree PyGenUtils::pyobject_to_ptree(const py::object& obj) {
  boost::property_tree::ptree tree;

  if (py::isinstance<py::dict>(obj)) {
    py::dict d = obj.cast<py::dict>();
    for (auto item : d) {
      std::string key = py::str(item.first);
      py::object val = py::reinterpret_borrow<py::object>(item.second);

      if (key == "__value__") {
        tree.put_value(py::str(val));
        continue;
      }

      boost::property_tree::ptree child = pyobject_to_ptree(val);
      tree.add_child(key, child);
    }
  }
  else if (py::isinstance<py::list>(obj) || py::isinstance<py::tuple>(obj)) {
    py::sequence seq = obj.cast<py::sequence>();
    for (py::handle item : seq) {
      py::object val = py::reinterpret_borrow<py::object>(item);
      tree.push_back(std::make_pair("", pyobject_to_ptree(val)));
    }
  } 
  else if (py::isinstance<py::bool_>(obj)) {
    tree.put_value(obj.cast<bool>() ? "true" : "false");
  } 
  else if (py::isinstance<py::int_>(obj)) {
    tree.put_value(std::to_string(obj.cast<int>()));
  } 
  else if (py::isinstance<py::float_>(obj)) {
    tree.put_value(std::to_string(obj.cast<double>()));
  } 
  else {
    tree.put_value(obj.cast<std::string>());
  }

  return tree;
}

int PyMoneroUtils::get_ring_size() {
  return monero_utils::RING_SIZE;
}

void PyMoneroUtils::set_log_level(int level) {
  monero_utils::set_log_level(level);
}

void PyMoneroUtils::configure_logging(const std::string& path, bool console) {
  monero_utils::configure_logging(path, console);
}

monero_integrated_address PyMoneroUtils::get_integrated_address(monero_network_type network_type, const std::string& standard_address, const std::string& payment_id) {
  return monero_utils::get_integrated_address(network_type, standard_address, payment_id);
}

bool PyMoneroUtils::is_valid_address(const std::string& address, monero_network_type network_type) {
  return monero_utils::is_valid_address(address, network_type);
}

bool PyMoneroUtils::is_valid_public_view_key(const std::string& public_view_key) {
  return is_hex_64(public_view_key);
}

bool PyMoneroUtils::is_valid_public_spend_key(const std::string& public_spend_key) {
  return is_hex_64(public_spend_key);
}

bool PyMoneroUtils::is_valid_private_view_key(const std::string& private_view_key) {
  return monero_utils::is_valid_private_view_key(private_view_key);
}

bool PyMoneroUtils::is_valid_private_spend_key(const std::string& private_spend_key) {
  return monero_utils::is_valid_private_spend_key(private_spend_key);
}

bool PyMoneroUtils::is_valid_payment_id(const std::string& payment_id) {
  return payment_id.size() == 16 || payment_id.size() == 64;
}

bool PyMoneroUtils::is_valid_mnemonic(const std::string& mnemonic) {
  try {
    validate_mnemonic(mnemonic);
    return true;
  }
  catch (...) {
    return false;
  }
}

void PyMoneroUtils::validate_address(const std::string& address, monero_network_type network_type) {
  monero_utils::validate_address(address, network_type);
}

void PyMoneroUtils::validate_public_view_key(const std::string& public_view_key) {
  if(!is_hex_64(public_view_key)) throw std::runtime_error("Invalid public view key");
}

void PyMoneroUtils::validate_public_spend_key(const std::string& public_spend_key) {
  if(!is_hex_64(public_spend_key)) throw std::runtime_error("Invalid public view key");
}

void PyMoneroUtils::validate_private_view_key(const std::string& private_view_key) {
  monero_utils::validate_private_view_key(private_view_key);
}

void PyMoneroUtils::validate_private_spend_key(const std::string& private_spend_key) {
  monero_utils::validate_private_spend_key(private_spend_key);
}

void PyMoneroUtils::validate_payment_id(const std::string& payment_id) {
  if (!is_valid_payment_id(payment_id)) throw std::runtime_error("Invalid payment id");
}

void PyMoneroUtils::validate_mnemonic(const std::string& mnemonic) {
  if (mnemonic.empty()) throw std::runtime_error("Mnemonic phrase is empty");

  size_t count = 0;
  bool in_word = false;

  for (char c : mnemonic) {
    if (std::isspace(c)) {
      if (in_word) {
        ++count;
        in_word = false;
      }
    } else {
      in_word = true;
    }
  }

  if (in_word) ++count;

  if (count != 25) throw std::runtime_error("Mnemonic phared words must be 25");
}

std::string PyMoneroUtils::json_to_binary(const std::string &json) {
  std::string bin;
  monero_utils::json_to_binary(json, bin);
  return bin;
}

std::string PyMoneroUtils::dict_to_binary(const py::dict &dictionary) {
  py::object JSON = py::module_::import("json");
  py::object JSON_DUMPS = JSON.attr("dumps");

  py::object result_py = JSON_DUMPS(dictionary);
  std::string json = result_py.cast<std::string>();

  return json_to_binary(json);
}

py::dict PyMoneroUtils::binary_to_dict(const std::string& bin) {
  py::object JSON = py::module_::import("json");
  py::object JSON_LOADS = JSON.attr("loads");

  std::string json = binary_to_json(bin);

  py::object result_py = JSON_LOADS(json);
  py::dict result = result_py.cast<py::dict>();

  return result;
}

std::string PyMoneroUtils::binary_to_json(const std::string &bin) {
  std::string json; 
  monero_utils::binary_to_json(bin, json);
  return json;
}

void PyMoneroUtils::binary_blocks_to_json(const std::string &bin, std::string &json) { 
  monero_utils::binary_blocks_to_json(bin, json);
}

void PyMoneroUtils::binary_blocks_to_property_tree(const std::string &bin, boost::property_tree::ptree &node) {
  std::string response_json;
  monero_utils::binary_blocks_to_json(bin, response_json);
  std::istringstream iss = response_json.empty() ? std::istringstream() : std::istringstream(response_json);
  boost::property_tree::read_json(iss, node);
}

bool PyMoneroUtils::is_valid_language(const std::string& language) { 
  return monero_utils::is_valid_language(language);
}

std::vector<std::shared_ptr<monero_block>> PyMoneroUtils::get_blocks_from_txs(std::vector<std::shared_ptr<monero_tx_wallet>> txs) {
  return monero_utils::get_blocks_from_txs(txs);
}

std::vector<std::shared_ptr<monero_block>> PyMoneroUtils::get_blocks_from_transfers(std::vector<std::shared_ptr<monero_transfer>> transfers) {
  return monero_utils::get_blocks_from_transfers(transfers);
}

std::vector<std::shared_ptr<monero_block>> PyMoneroUtils::get_blocks_from_outputs(std::vector<std::shared_ptr<monero_output_wallet>> outputs) {
  return monero_utils::get_blocks_from_outputs(outputs);
}

std::string PyMoneroUtils::get_payment_uri(const monero_tx_config& config) {
  // validate config
  std::vector<std::shared_ptr<monero_destination>> destinations = config.get_normalized_destinations();
  if (destinations.size() != 1) throw std::runtime_error("Cannot make URI from supplied parameters: must provide exactly one destination to send funds");
  if (destinations.at(0)->m_address == boost::none) throw std::runtime_error("Cannot make URI from supplied parameters: must provide destination address");
  if (destinations.at(0)->m_amount == boost::none) throw std::runtime_error("Cannot make URI from supplied parameters: must provide destination amount");

  // prepare wallet2 params
  std::string address = destinations.at(0)->m_address.get();
  std::string payment_id = config.m_payment_id == boost::none ? "" : config.m_payment_id.get();
  uint64_t amount = destinations.at(0)->m_amount.get();
  std::string note = config.m_note == boost::none ? "" : config.m_note.get();
  std::string m_recipient_name = config.m_recipient_name == boost::none ? "" : config.m_recipient_name.get();

  // make uri
  std::string uri = make_uri(address, payment_id, amount, note, m_recipient_name);
  if (uri.empty()) throw std::runtime_error("Cannot make URI from supplied parameters");
  return uri;
}

uint64_t PyMoneroUtils::xmr_to_atomic_units(double amount_xmr) {
  if (amount_xmr < 0) throw std::invalid_argument("amount_xmr cannot be negative");
  return static_cast<uint64_t>(std::round(amount_xmr * XMR_AU_MULTIPLIER));
}

double PyMoneroUtils::atomic_units_to_xmr(uint64_t amount_atomic_units) {
  return static_cast<double>(amount_atomic_units) / static_cast<double>(XMR_AU_MULTIPLIER);
}

bool PyMoneroUtils::is_hex_64(const std::string& value) { 
  if (value.size() != 64) return false;
  const std::regex hexRegex("^-?[0-9a-fA-F]+$");
  return std::regex_match(value, hexRegex);
}

std::string PyMoneroUtils::make_uri(const std::string &address, const std::string &payment_id, uint64_t amount, const std::string &tx_description, const std::string &recipient_name) {
  cryptonote::address_parse_info info;

  if(!get_account_address_from_str(info, cryptonote::MAINNET, address))
  {
    if(!get_account_address_from_str(info, cryptonote::TESTNET, address))
    {
      if(!get_account_address_from_str(info, cryptonote::STAGENET, address))
      {
        throw std::runtime_error(std::string("wrong address: ") + address);
      }            
    }
  }
  
  // we want only one payment id
  if (info.has_payment_id && !payment_id.empty())
  {
    throw std::runtime_error("A single payment id is allowed");
  }
  
  if (!payment_id.empty())
  {
    throw std::runtime_error("Standalone payment id deprecated, use integrated address instead");
  }
  
  std::string uri = "monero:" + address;
  unsigned int n_fields = 0;
  
  if (!payment_id.empty())
  {
    uri += (n_fields++ ? "&" : "?") + std::string("tx_payment_id=") + payment_id;
  }
  
  if (amount > 0)
  {
    // URI encoded amount is in decimal units, not atomic units
    uri += (n_fields++ ? "&" : "?") + std::string("tx_amount=") + cryptonote::print_money(amount);
  }
  
  if (!recipient_name.empty())
  {
    uri += (n_fields++ ? "&" : "?") + std::string("recipient_name=") + epee::net_utils::conver_to_url_format(recipient_name);
  }
  
  if (!tx_description.empty())
  {
    uri += (n_fields++ ? "&" : "?") + std::string("tx_description=") + epee::net_utils::conver_to_url_format(tx_description);
  }
  
  return uri;
}
