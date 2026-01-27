#pragma once

#include "common/py_monero_common.h"
#include "utils/monero_utils.h"


class PyMoneroUtils {
public:
  inline static const uint64_t NUM_MNEMONIC_WORDS = 25;
  inline static const uint64_t XMR_AU_MULTIPLIER = 1000000000000ULL;

  PyMoneroUtils() {};
  static std::string get_version() { return std::string("0.0.1"); };
  static int get_ring_size();
  static void set_log_level(int level);
  static void configure_logging(const std::string& path, bool console);
  static monero_integrated_address get_integrated_address(monero_network_type network_type, const std::string& standard_address, const std::string& payment_id = "");
  static bool is_valid_address(const std::string& address, monero_network_type network_type);
  static bool is_valid_public_view_key(const std::string& public_view_key);
  static bool is_valid_public_spend_key(const std::string& public_spend_key);
  static bool is_valid_private_view_key(const std::string& private_view_key);
  static bool is_valid_private_spend_key(const std::string& private_spend_key);
  static bool is_valid_payment_id(const std::string& payment_id);
  static bool is_valid_mnemonic(const std::string& mnemonic);
  static void validate_address(const std::string& address, monero_network_type network_type);
  static void validate_public_view_key(const std::string& public_view_key);
  static void validate_public_spend_key(const std::string& public_spend_key);
  static void validate_private_view_key(const std::string& private_view_key);
  static void validate_private_spend_key(const std::string& private_spend_key);
  static void validate_payment_id(const std::string& payment_id);
  static void validate_mnemonic(const std::string& mnemonic);

  static std::string json_to_binary(const std::string &json);
  static std::string dict_to_binary(const py::dict &dictionary);
  static py::dict binary_to_dict(const std::string& bin);
  static std::string binary_to_json(const std::string &bin);
  static void binary_blocks_to_json(const std::string &bin, std::string &json);
  static void binary_blocks_to_property_tree(const std::string &bin, boost::property_tree::ptree &node);
  static bool is_valid_language(const std::string& language);
  static std::vector<std::shared_ptr<monero_block>> get_blocks_from_txs(std::vector<std::shared_ptr<monero_tx_wallet>> txs);
  static std::vector<std::shared_ptr<monero_block>> get_blocks_from_transfers(std::vector<std::shared_ptr<monero_transfer>> transfers);
  static std::vector<std::shared_ptr<monero_block>> get_blocks_from_outputs(std::vector<std::shared_ptr<monero_output_wallet>> outputs);
  static std::string get_payment_uri(const monero_tx_config& config);
  static uint64_t xmr_to_atomic_units(double amount_xmr);
  static double atomic_units_to_xmr(uint64_t amount_atomic_units);

private:

  static bool is_hex_64(const std::string& value);
  static std::string make_uri(const std::string &address, const std::string &payment_id, uint64_t amount, const std::string &tx_description, const std::string &recipient_name);
};
