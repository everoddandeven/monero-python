#include "wallet/py_monero_wallet.h"

#define MONERO_CATCH_AND_RETHROW(expr)         \
  try {                                        \
    return expr;                               \
  } catch (const PyMoneroRpcError& e) {        \
    throw e;                                   \
  }                                            \
  catch (const std::exception& e) {            \
    throw PyMoneroError(e.what());             \
  }

class PyMoneroUtils {
public:
  inline static const uint64_t NUM_MNEMONIC_WORDS = 25;
  inline static const uint64_t XMR_AU_MULTIPLIER = 1000000000000ULL;

  PyMoneroUtils() {};
  static std::string get_version() { return std::string("0.0.1"); };
  static int get_ring_size() { return monero_utils::RING_SIZE; };
  static void set_log_level(int level) { monero_utils::set_log_level(level); };
  static void configure_logging(const std::string& path, bool console) { monero_utils::configure_logging(path, console); };
  static monero_integrated_address get_integrated_address(monero_network_type network_type, const std::string& standard_address, const std::string& payment_id = "") { return monero_utils::get_integrated_address(network_type, standard_address, payment_id); };
  static bool is_valid_address(const std::string& address, monero_network_type network_type) { return monero_utils::is_valid_address(address, network_type); };
  static bool is_valid_public_view_key(const std::string& public_view_key) { return is_hex_64(public_view_key); };
  static bool is_valid_public_spend_key(const std::string& public_spend_key) { return is_hex_64(public_spend_key); };
  static bool is_valid_private_view_key(const std::string& private_view_key) { return monero_utils::is_valid_private_view_key(private_view_key); };
  static bool is_valid_private_spend_key(const std::string& private_spend_key) { return monero_utils::is_valid_private_spend_key(private_spend_key); };
  static bool is_valid_payment_id(const std::string& payment_id) { return payment_id.size() == 16 || payment_id.size() == 64; };
  static bool is_valid_mnemonic(const std::string& mnemonic) {
    try {
      validate_mnemonic(mnemonic);
      return true;
    }
    catch (...) {
      return false;
    }
  };
  static void validate_address(const std::string& address, monero_network_type network_type) { monero_utils::validate_address(address, network_type); };
  static void validate_public_view_key(const std::string& public_view_key) { if(!is_hex_64(public_view_key)) throw std::runtime_error("Invalid public view key"); };
  static void validate_public_spend_key(const std::string& public_spend_key) { if(!is_hex_64(public_spend_key)) throw std::runtime_error("Invalid public view key"); };
  static void validate_private_view_key(const std::string& private_view_key) { monero_utils::validate_private_view_key(private_view_key); };
  static void validate_private_spend_key(const std::string& private_spend_key) { monero_utils::validate_private_spend_key(private_spend_key); };
  static void validate_payment_id(const std::string& payment_id) { if (!is_valid_payment_id(payment_id)) throw std::runtime_error("Invalid payment id"); };
  static void validate_mnemonic(const std::string& mnemonic) {
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

    if (in_word) ++count; // ultima parola

    if (count != 25) throw std::runtime_error("Mnemonic phared words must be 25");
  };
  static std::string json_to_binary(const std::string &json) {
    std::string bin;
    monero_utils::json_to_binary(json, bin);
    return bin;
  };
  static std::string dict_to_binary(const py::dict &dictionary) {
    py::object JSON = py::module_::import("json");
    py::object JSON_DUMPS = JSON.attr("dumps");
  
    py::object result_py = JSON_DUMPS(dictionary);
    std::string json = result_py.cast<std::string>();

    return json_to_binary(json);
  };
  static py::dict binary_to_dict(const std::string& bin) {
    py::object JSON = py::module_::import("json");
    py::object JSON_LOADS = JSON.attr("loads");

    std::string json = binary_to_json(bin);
  
    py::object result_py = JSON_LOADS(json);
    py::dict result = result_py.cast<py::dict>();

    return result;
  };
  static std::string binary_to_json(const std::string &bin) {
    std::string json; 
    monero_utils::binary_to_json(bin, json);
    return json;
  };
  static void binary_blocks_to_json(const std::string &bin, std::string &json) { monero_utils::binary_blocks_to_json(bin, json); };
  static bool is_valid_language(const std::string& language) { return monero_utils::is_valid_language(language); };
  static std::vector<std::shared_ptr<monero_block>> get_blocks_from_txs(std::vector<std::shared_ptr<monero_tx_wallet>> txs) { return monero_utils::get_blocks_from_txs(txs); };
  static std::vector<std::shared_ptr<monero_block>> get_blocks_from_transfers(std::vector<std::shared_ptr<monero_transfer>> transfers) { return monero_utils::get_blocks_from_transfers(transfers); };
  static std::vector<std::shared_ptr<monero_block>> get_blocks_from_outputs(std::vector<std::shared_ptr<monero_output_wallet>> outputs) { return monero_utils::get_blocks_from_outputs(outputs); };
  static std::string get_payment_uri(const monero_tx_config& config) {
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
  };
  static uint64_t xmr_to_atomic_units(double amount_xmr) {
    if (amount_xmr < 0) throw std::invalid_argument("amount_xmr cannot be negative");
    return static_cast<uint64_t>(std::round(amount_xmr * XMR_AU_MULTIPLIER));
  };
  static double atomic_units_to_xmr(uint64_t amount_atomic_units) {
    return static_cast<double>(amount_atomic_units) / static_cast<double>(XMR_AU_MULTIPLIER);
  };

private:
  static bool is_hex_64(const std::string& value) { 
    if (value.size() != 64) return false;
    const std::regex hexRegex("^-?[0-9a-fA-F]+$");
    return std::regex_match(value, hexRegex);
  }

  static std::string make_uri(const std::string &address, const std::string &payment_id, uint64_t amount, const std::string &tx_description, const std::string &recipient_name) {
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

};