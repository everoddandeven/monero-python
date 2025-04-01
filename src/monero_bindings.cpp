#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include "../external/monero-cpp/src/utils/monero_utils.h"
#include "../external/monero-cpp/src/daemon/monero_daemon_model.h"
#include "../external/monero-cpp/src/wallet/monero_wallet_model.h"
#include "../external/monero-cpp/src/wallet/monero_wallet_full.h"
#include "../external/monero-cpp/src/wallet/monero_wallet_keys.h"

namespace py = pybind11;

class MoneroUtils {
public:
    MoneroUtils() {};
    static int get_ring_size() { return monero_utils::RING_SIZE; };
    static void set_log_level(int level) { monero_utils::set_log_level(level); };
    static void configure_logging(const std::string& path, bool console) { monero_utils::configure_logging(path, console); };
    static monero_integrated_address get_integrated_address(monero_network_type network_type, const std::string& standard_address, const std::string& payment_id) { return monero_utils::get_integrated_address(network_type, standard_address, payment_id); };
    static bool is_valid_address(const std::string& address, monero_network_type network_type) { return monero_utils::is_valid_address(address, network_type); };
    static bool is_valid_private_view_key(const std::string& private_view_key) { return monero_utils::is_valid_private_view_key(private_view_key); };
    static bool is_valid_private_spend_key(const std::string& private_spend_key) { return monero_utils::is_valid_private_spend_key(private_spend_key); };
    static void validate_address(const std::string& address, monero_network_type network_type) { monero_utils::validate_address(address, network_type); };
    static void validate_private_view_key(const std::string& private_view_key) { monero_utils::validate_private_view_key(private_view_key); };
    static void validate_private_spend_key(const std::string& private_spend_key) { monero_utils::validate_private_spend_key(private_spend_key); };
    static void json_to_binary(const std::string &json, std::string &bin) { monero_utils::json_to_binary(json, bin); };
    static void binary_to_json(const std::string &bin, std::string &json) { monero_utils::binary_to_json(bin, json); };
    static void binary_blocks_to_json(const std::string &bin, std::string &json) { monero_utils::binary_blocks_to_json(bin, json); };
    static bool is_valid_language(const std::string& language) { return monero_utils::is_valid_language(language); };
};

#define MONERO_CATCH_AND_RETHROW(expr)           \
    try {                                        \
        return expr;                             \
    } catch (const std::exception& e) {          \
        throw py::value_error(e.what());      \
    }
    
PYBIND11_MODULE(monero, m) {
    m.doc() = "Python bindings for monero-cpp library";

    py::register_exception<std::runtime_error>(m, "MoneroError");

    py::class_<MoneroUtils>(m, "MoneroUtils")
        .def_static("get_ring_size", []() {
            MONERO_CATCH_AND_RETHROW(MoneroUtils::get_ring_size());
        })
        .def_static("set_log_level", [](int loglevel) {
            MONERO_CATCH_AND_RETHROW(MoneroUtils::set_log_level(loglevel));
        }, py::arg("loglevel"))
        .def_static("configure_logging", [](const std::string& path, bool console) {
            MONERO_CATCH_AND_RETHROW(MoneroUtils::configure_logging(path, console));
        }, py::arg("path"), py::arg("console"))
        .def_static("get_integrated_address", [](monero_network_type network_type, const std::string& standard_address, const std::string& payment_id) {
            MONERO_CATCH_AND_RETHROW(MoneroUtils::get_integrated_address(network_type, standard_address, payment_id));
        }, py::arg("network_type"), py::arg("standard_address"), py::arg("payment_id"))
        .def_static("is_valid_address", [](const std::string& address, monero_network_type network_type) {
            MONERO_CATCH_AND_RETHROW(MoneroUtils::is_valid_address(address, network_type));
        }, py::arg("address"), py::arg("network_type"))
        .def_static("is_valid_private_view_key", [](const std::string& private_view_key) {
            MONERO_CATCH_AND_RETHROW(MoneroUtils::is_valid_private_view_key(private_view_key));
        }, py::arg("private_view_key"))
        .def_static("is_valid_private_spend_key", [](const std::string& private_spend_key) {
            MONERO_CATCH_AND_RETHROW(MoneroUtils::is_valid_private_spend_key(private_spend_key));
        }, py::arg("private_spend_key"))
        .def_static("validate_address", [](const std::string& address, monero_network_type network_type) {
            MONERO_CATCH_AND_RETHROW(MoneroUtils::validate_address(address, network_type));
        }, py::arg("address"), py::arg("network_type"))
        .def_static("validate_private_view_key", [](const std::string& private_view_key) {
            MONERO_CATCH_AND_RETHROW(MoneroUtils::validate_private_view_key(private_view_key));
        }, py::arg("private_view_key"))
        .def_static("validate_private_spend_key", [](const std::string& private_spend_key) {
            MONERO_CATCH_AND_RETHROW(MoneroUtils::validate_private_spend_key(private_spend_key));
        }, py::arg("private_spend_key"))
        .def_static("is_valid_language", [](const std::string& language) {
            MONERO_CATCH_AND_RETHROW(MoneroUtils::is_valid_language(language));
        }, py::arg("language"));


    // enum monero_network_type
    py::enum_<monero::monero_network_type>(m, "MoneroNetworkType")
        .value("MAINNET", monero::monero_network_type::MAINNET)
        .value("TESTNET", monero::monero_network_type::TESTNET)
        .value("STAGENET", monero::monero_network_type::STAGENET);

    // monero_version
    py::class_<monero::monero_version>(m, "MoneroVersion")
        .def(py::init<>())
        .def_readwrite("number", &monero::monero_version::m_number)
        .def_readwrite("is_release", &monero::monero_version::m_is_release);

    // monero_rpc_connection
    py::class_<monero::monero_rpc_connection>(m, "MoneroRpcConnection")
        .def(py::init<>())
        .def_readwrite("uri", &monero::monero_rpc_connection::m_uri)
        .def_readwrite("username", &monero::monero_rpc_connection::m_username)
        .def_readwrite("password", &monero::monero_rpc_connection::m_password);

    // monero_block_header
    py::class_<monero::monero_block_header>(m, "MoneroBlockHeader")
        .def(py::init<>())
        .def_readwrite("hash", &monero::monero_block_header::m_hash)
        .def_readwrite("height", &monero::monero_block_header::m_height)
        .def_readwrite("timestamp", &monero::monero_block_header::m_timestamp)
        .def_readwrite("size", &monero::monero_block_header::m_size)
        .def_readwrite("weight", &monero::monero_block_header::m_weight)
        .def_readwrite("long_term_weight", &monero::monero_block_header::m_long_term_weight)
        .def_readwrite("depth", &monero::monero_block_header::m_depth)
        .def_readwrite("difficulty", &monero::monero_block_header::m_difficulty)
        .def_readwrite("cumulative_difficulty", &monero::monero_block_header::m_cumulative_difficulty)
        .def_readwrite("major_version", &monero::monero_block_header::m_major_version)
        .def_readwrite("minor_version", &monero::monero_block_header::m_minor_version)
        .def_readwrite("nonce", &monero::monero_block_header::m_nonce)
        .def_readwrite("miner_tx_hash", &monero::monero_block_header::m_miner_tx_hash)
        .def_readwrite("num_txs", &monero::monero_block_header::m_num_txs)
        .def_readwrite("orphan_status", &monero::monero_block_header::m_orphan_status)
        .def_readwrite("prev_hash", &monero::monero_block_header::m_prev_hash)
        .def_readwrite("reward", &monero::monero_block_header::m_reward)
        .def_readwrite("m_pow_hash", &monero::monero_block_header::m_pow_hash);

    // monero_block
    py::class_<monero::monero_block>(m, "MoneroBlock")
        .def(py::init<>())
        .def_readwrite("hex", &monero::monero_block::m_hex)
        .def_readwrite("miner_tx", &monero::monero_block::m_miner_tx)
        .def_readwrite("txs", &monero::monero_block::m_txs)
        .def_readwrite("tx_hashes", &monero::monero_block::m_tx_hashes);

    // monero_tx
    py::class_<monero::monero_tx>(m, "MoneroTx")
        .def(py::init<>())
        .def_readwrite("block", &monero::monero_tx::m_block)
        .def_readwrite("hash", &monero::monero_tx::m_hash)
        .def_readwrite("version", &monero::monero_tx::m_version)
        .def_readwrite("is_miner_tx", &monero::monero_tx::m_is_miner_tx)
        .def_readwrite("payment_id", &monero::monero_tx::m_payment_id)
        .def_readwrite("fee", &monero::monero_tx::m_fee)
        .def_readwrite("ring_size", &monero::monero_tx::m_ring_size)
        .def_readwrite("relay", &monero::monero_tx::m_relay)
        .def_readwrite("is_relayed", &monero::monero_tx::m_is_relayed)
        .def_readwrite("is_confirmed", &monero::monero_tx::m_is_confirmed)
        .def_readwrite("in_tx_pool", &monero::monero_tx::m_in_tx_pool)
        .def_readwrite("num_confirmations", &monero::monero_tx::m_num_confirmations)
        .def_readwrite("unlock_time", &monero::monero_tx::m_unlock_time)
        .def_readwrite("last_relayed_timestamp", &monero::monero_tx::m_last_relayed_timestamp)
        .def_readwrite("received_timestamp", &monero::monero_tx::m_received_timestamp)
        .def_readwrite("is_double_spend_seen", &monero::monero_tx::m_is_double_spend_seen)
        .def_readwrite("key", &monero::monero_tx::m_key)
        .def_readwrite("full_hex", &monero::monero_tx::m_full_hex)
        .def_readwrite("pruned_hex", &monero::monero_tx::m_pruned_hex)
        .def_readwrite("prunable_hex", &monero::monero_tx::m_prunable_hex)
        .def_readwrite("prunable_hash", &monero::monero_tx::m_prunable_hash)
        .def_readwrite("size", &monero::monero_tx::m_size)
        .def_readwrite("weight", &monero::monero_tx::m_weight)
        .def_readwrite("inputs", &monero::monero_tx::m_inputs)
        .def_readwrite("outputs", &monero::monero_tx::m_outputs)
        .def_readwrite("output_indices", &monero::monero_tx::m_output_indices)
        .def_readwrite("metadata", &monero::monero_tx::m_metadata)
        .def_readwrite("common_tx_sets", &monero::monero_tx::m_common_tx_sets)
        .def_readwrite("extra", &monero::monero_tx::m_extra)
        .def_readwrite("rct_signatures", &monero::monero_tx::m_rct_signatures)
        .def_readwrite("rct_sig_prunable", &monero::monero_tx::m_rct_sig_prunable)
        .def_readwrite("is_kept_by_block", &monero::monero_tx::m_is_kept_by_block)
        .def_readwrite("is_failed", &monero::monero_tx::m_is_failed)
        .def_readwrite("last_failed_height", &monero::monero_tx::m_last_failed_height)
        .def_readwrite("last_failed_hash", &monero::monero_tx::m_last_failed_hash)
        .def_readwrite("max_used_block_height", &monero::monero_tx::m_max_used_block_height)
        .def_readwrite("max_used_block_hash", &monero::monero_tx::m_max_used_block_hash)
        .def_readwrite("signatures", &monero::monero_tx::m_signatures);

    // monero_key_image
    py::class_<monero::monero_key_image>(m, "MoneroKeyImage")
        .def(py::init<>())
        .def_readwrite("hex", &monero::monero_key_image::m_hex)
        .def_readwrite("signature", &monero::monero_key_image::m_signature);

    // monero_output
    py::class_<monero::monero_output>(m, "MoneroOutput")
        .def(py::init<>())
        .def_readwrite("tx", &monero::monero_output::m_tx)
        .def_readwrite("key_image", &monero::monero_output::m_key_image)
        .def_readwrite("amount", &monero::monero_output::m_amount)
        .def_readwrite("index", &monero::monero_output::m_index)
        .def_readwrite("ring_output_indices", &monero::monero_output::m_ring_output_indices)
        .def_readwrite("stealth_public_key", &monero::monero_output::m_stealth_public_key);

    // monero_wallet_config
    py::class_<monero::monero_wallet_config, std::shared_ptr<monero::monero_wallet_config>>(m, "MoneroWalletConfig")
        .def(py::init<>())
        .def_property("path", 
            [](const monero::monero_wallet_config& self) { return self.m_path; },
            [](monero::monero_wallet_config& self, const std::string& val) { self.m_path = val; })
        .def_property("password", 
            [](const monero::monero_wallet_config& self) { return self.m_password; },
            [](monero::monero_wallet_config& self, const std::string& val) { self.m_password = val; })
        .def_property("network_type", 
            [](const monero::monero_wallet_config& self) { return self.m_network_type; },
            [](monero::monero_wallet_config& self, monero::monero_network_type nettype) { self.m_network_type = nettype; })
        .def_property("server", 
            [](const monero::monero_wallet_config& self) { return self.m_server; },
            [](monero::monero_wallet_config& self, monero::monero_rpc_connection& server) { self.m_server = server; })
        .def_property("seed", 
            [](const monero::monero_wallet_config& self) { return self.m_seed.value_or(""); },
            [](monero::monero_wallet_config& self, const std::string& val) { self.m_seed = val; })
        .def_property("seed_offset", 
            [](const monero::monero_wallet_config& self) { return self.m_seed_offset.value_or(""); },
            [](monero::monero_wallet_config& self, const std::string& val) { self.m_seed_offset = val; })
        .def_property("primary_address", 
            [](const monero::monero_wallet_config& self) { return self.m_primary_address.value_or(""); },
            [](monero::monero_wallet_config& self, const std::string& val) { self.m_primary_address = val; })
        .def_property("private_view_key", 
            [](const monero::monero_wallet_config& self) { return self.m_private_view_key.value_or(""); },
            [](monero::monero_wallet_config& self, const std::string& val) { self.m_private_view_key = val; })
        .def_property("private_spend_key", 
            [](const monero::monero_wallet_config& self) { return self.m_private_spend_key.value_or(""); },
            [](monero::monero_wallet_config& self, const std::string& val) { self.m_private_spend_key = val; })
        .def_property("save_current", 
            [](const monero::monero_wallet_config& self) { return self.m_save_current; },
            [](monero::monero_wallet_config& self, bool val) { self.m_save_current = val; }) 
        .def_property("language", 
            [](const monero::monero_wallet_config& self) { return self.m_language.value_or(""); },
            [](monero::monero_wallet_config& self, const std::string& val) { self.m_language = val; })
        .def_property("restore_height", 
            [](const monero::monero_wallet_config& self) { return self.m_restore_height; },
            [](monero::monero_wallet_config& self, uint64_t height) { self.m_restore_height = height; })
        .def_property("account_lookahead", 
            [](const monero::monero_wallet_config& self) { return self.m_account_lookahead; },
            [](monero::monero_wallet_config& self, uint64_t val) { self.m_account_lookahead = val; }) 
        .def_property("subaddress_lookahead", 
            [](const monero::monero_wallet_config& self) { return self.m_subaddress_lookahead; },
            [](monero::monero_wallet_config& self, uint64_t val) { self.m_subaddress_lookahead = val; })
        .def_property("is_multisig", 
            [](const monero::monero_wallet_config& self) { return self.m_is_multisig; },
            [](monero::monero_wallet_config& self, uint64_t is_multisig) { self.m_is_multisig = is_multisig; });

    // monero_subaddress
    py::class_<monero::monero_subaddress>(m, "MoneroSubaddress")
        .def(py::init<>())
        .def_readwrite("account_index", &monero::monero_subaddress::m_account_index)
        .def_readwrite("index", &monero::monero_subaddress::m_index)
        .def_readwrite("address", &monero::monero_subaddress::m_address)
        .def_readwrite("label", &monero::monero_subaddress::m_label)
        .def_readwrite("balance", &monero::monero_subaddress::m_balance)
        .def_readwrite("unlocked_balance", &monero::monero_subaddress::m_unlocked_balance)
        .def_readwrite("num_unspent_outputs", &monero::monero_subaddress::m_num_unspent_outputs)
        .def_readwrite("is_used", &monero::monero_subaddress::m_is_used)
        .def_readwrite("num_blocks_to_unlock", &monero::monero_subaddress::m_num_blocks_to_unlock);

    // monero_sync_result
    py::class_<monero::monero_sync_result>(m, "MoneroSyncResult")
        .def_readwrite("num_blocks_fetched", &monero::monero_sync_result::m_num_blocks_fetched)
        .def_readwrite("received_money", &monero::monero_sync_result::m_received_money);

    // monero_account
    py::class_<monero::monero_account>(m, "MoneroAccount")
        .def(py::init<>())
        .def_readwrite("index", &monero::monero_account::m_index)
        .def_readwrite("primary_address", &monero::monero_account::m_primary_address)
        .def_readwrite("balance", &monero::monero_account::m_balance)
        .def_readwrite("unlocked_balance", &monero::monero_account::m_unlocked_balance)
        .def_readwrite("tag", &monero::monero_account::m_tag)
        .def_readwrite("subaddresses", &monero::monero_account::m_subaddresses);

    // monero_destination
    py::class_<monero::monero_destination>(m, "MoneroDestination")
        .def(py::init<>())
        .def_readwrite("address", &monero::monero_destination::m_address)
        .def_readwrite("amount", &monero::monero_destination::m_amount);

    
    /*
    // monero_transfer
    py::class_<monero::monero_transfer>(m, "MoneroTransfer")
        .def(py::init<>())
        .def_readwrite("tx", &monero::monero_transfer::m_tx)
        .def_readwrite("account_index", &monero::monero_transfer::m_account_index)
        .def_readwrite("amount", &monero::monero_transfer::m_amount);
    */
    
    // monero_incoming_transfer
    py::class_<monero::monero_incoming_transfer>(m, "MoneroIncomingTransfer")
        .def(py::init<>())
        .def("is_incoming", [](monero::monero_incoming_transfer& self) {
            MONERO_CATCH_AND_RETHROW(self.is_incoming());
        })
        .def("is_outgoing", [](monero::monero_incoming_transfer& self) {
            MONERO_CATCH_AND_RETHROW(self.is_outgoing());
        })
        .def_readwrite("tx", &monero::monero_incoming_transfer::m_tx)
        .def_readwrite("account_index", &monero::monero_incoming_transfer::m_account_index)
        .def_readwrite("address", &monero::monero_incoming_transfer::m_address)
        .def_readwrite("subaddress_index", &monero::monero_incoming_transfer::m_subaddress_index)
        .def_readwrite("num_suggested_confirmations", &monero::monero_incoming_transfer::m_num_suggested_confirmations)
        .def_readwrite("amount", &monero::monero_incoming_transfer::m_amount);

    // monero_outgoing_transfer
    py::class_<monero::monero_outgoing_transfer>(m, "MoneroOutgoingTransfer")
        .def(py::init<>())
        .def("is_incoming", [](monero::monero_outgoing_transfer& self) {
            MONERO_CATCH_AND_RETHROW(self.is_incoming());
        })
        .def("is_outgoing", [](monero::monero_outgoing_transfer& self) {
            MONERO_CATCH_AND_RETHROW(self.is_outgoing());
        })
        .def_readwrite("tx", &monero::monero_outgoing_transfer::m_tx)
        .def_readwrite("account_index", &monero::monero_outgoing_transfer::m_account_index)
        .def_readwrite("amount", &monero::monero_outgoing_transfer::m_amount)
        .def_readwrite("subaddress_indices", &monero::monero_outgoing_transfer::m_subaddress_indices)
        .def_readwrite("addresses", &monero::monero_outgoing_transfer::m_addresses)
        .def_readwrite("destinations", &monero::monero_outgoing_transfer::m_destinations);

    // monero_transfer_query
    py::class_<monero::monero_transfer_query>(m, "MoneroTransferQuery")
        .def(py::init<>())
        .def_readwrite("tx", &monero::monero_transfer_query::m_tx)
        .def_readwrite("account_index", &monero::monero_transfer_query::m_account_index)
        .def_readwrite("amount", &monero::monero_transfer_query::m_amount)
        .def_readwrite("is_incoming", &monero::monero_transfer_query::m_is_incoming)
        .def_readwrite("address", &monero::monero_transfer_query::m_address)
        .def_readwrite("addresses", &monero::monero_transfer_query::m_addresses)
        .def_readwrite("subaddress_index", &monero::monero_transfer_query::m_subaddress_index)
        .def_readwrite("subaddress_indices", &monero::monero_transfer_query::m_subaddress_indices)
        .def_readwrite("destinations", &monero::monero_transfer_query::m_destinations)
        .def_readwrite("tx_query", &monero::monero_transfer_query::m_tx_query);

    // monero_output_wallet
    py::class_<monero::monero_output_wallet>(m, "MoneroOutputWallet")
        .def(py::init<>())
        .def_readwrite("tx", &monero::monero_output_wallet::m_tx)
        .def_readwrite("key_image", &monero::monero_output_wallet::m_key_image)
        .def_readwrite("amount", &monero::monero_output_wallet::m_amount)
        .def_readwrite("index", &monero::monero_output_wallet::m_index)
        .def_readwrite("ring_output_indices", &monero::monero_output_wallet::m_ring_output_indices)
        .def_readwrite("stealth_public_key", &monero::monero_output_wallet::m_stealth_public_key)
        .def_readwrite("account_index", &monero::monero_output_wallet::m_account_index)
        .def_readwrite("subaddress_index", &monero::monero_output_wallet::m_subaddress_index)
        .def_readwrite("is_spent", &monero::monero_output_wallet::m_is_spent)
        .def_readwrite("is_frozen", &monero::monero_output_wallet::m_is_frozen);

    // monero_output_query
    py::class_<monero::monero_output_query>(m, "MoneroOutputQuery")
        .def(py::init<>())
        .def_readwrite("tx", &monero::monero_output_query::m_tx)
        .def_readwrite("key_image", &monero::monero_output_query::m_key_image)
        .def_readwrite("amount", &monero::monero_output_query::m_amount)
        .def_readwrite("index", &monero::monero_output_query::m_index)
        .def_readwrite("ring_output_indices", &monero::monero_output_query::m_ring_output_indices)
        .def_readwrite("stealth_public_key", &monero::monero_output_query::m_stealth_public_key)
        .def_readwrite("account_index", &monero::monero_output_query::m_account_index)
        .def_readwrite("subaddress_index", &monero::monero_output_query::m_subaddress_index)
        .def_readwrite("is_spent", &monero::monero_output_query::m_is_spent)
        .def_readwrite("is_frozen", &monero::monero_output_query::m_is_frozen)
        .def_readwrite("subaddress_indices", &monero::monero_output_query::m_subaddress_indices)
        .def_readwrite("min_amount", &monero::monero_output_query::m_min_amount)
        .def_readwrite("max_amount", &monero::monero_output_query::m_max_amount)
        .def_readwrite("tx_query", &monero::monero_output_query::m_tx_query);

    // monero_tx_wallet
    py::class_<monero::monero_tx_wallet>(m, "MoneroTxWallet")
        .def(py::init<>())
        .def_readwrite("block", &monero::monero_tx_wallet::m_block)
        .def_readwrite("hash", &monero::monero_tx_wallet::m_hash)
        .def_readwrite("version", &monero::monero_tx_wallet::m_version)
        .def_readwrite("is_miner_tx", &monero::monero_tx_wallet::m_is_miner_tx)
        .def_readwrite("payment_id", &monero::monero_tx_wallet::m_payment_id)
        .def_readwrite("fee", &monero::monero_tx_wallet::m_fee)
        .def_readwrite("ring_size", &monero::monero_tx_wallet::m_ring_size)
        .def_readwrite("relay", &monero::monero_tx_wallet::m_relay)
        .def_readwrite("is_relayed", &monero::monero_tx_wallet::m_is_relayed)
        .def_readwrite("is_confirmed", &monero::monero_tx_wallet::m_is_confirmed)
        .def_readwrite("in_tx_pool", &monero::monero_tx_wallet::m_in_tx_pool)
        .def_readwrite("num_confirmations", &monero::monero_tx_wallet::m_num_confirmations)
        .def_readwrite("unlock_time", &monero::monero_tx_wallet::m_unlock_time)
        .def_readwrite("last_relayed_timestamp", &monero::monero_tx_wallet::m_last_relayed_timestamp)
        .def_readwrite("received_timestamp", &monero::monero_tx_wallet::m_received_timestamp)
        .def_readwrite("is_double_spend_seen", &monero::monero_tx_wallet::m_is_double_spend_seen)
        .def_readwrite("key", &monero::monero_tx_wallet::m_key)
        .def_readwrite("full_hex", &monero::monero_tx_wallet::m_full_hex)
        .def_readwrite("pruned_hex", &monero::monero_tx_wallet::m_pruned_hex)
        .def_readwrite("prunable_hex", &monero::monero_tx_wallet::m_prunable_hex)
        .def_readwrite("prunable_hash", &monero::monero_tx_wallet::m_prunable_hash)
        .def_readwrite("size", &monero::monero_tx_wallet::m_size)
        .def_readwrite("weight", &monero::monero_tx_wallet::m_weight)
        .def_readwrite("inputs", &monero::monero_tx_wallet::m_inputs)
        .def_readwrite("outputs", &monero::monero_tx_wallet::m_outputs)
        .def_readwrite("output_indices", &monero::monero_tx_wallet::m_output_indices)
        .def_readwrite("metadata", &monero::monero_tx_wallet::m_metadata)
        .def_readwrite("common_tx_sets", &monero::monero_tx_wallet::m_common_tx_sets)
        .def_readwrite("extra", &monero::monero_tx_wallet::m_extra)
        .def_readwrite("rct_signatures", &monero::monero_tx_wallet::m_rct_signatures)
        .def_readwrite("rct_sig_prunable", &monero::monero_tx_wallet::m_rct_sig_prunable)
        .def_readwrite("is_kept_by_block", &monero::monero_tx_wallet::m_is_kept_by_block)
        .def_readwrite("is_failed", &monero::monero_tx_wallet::m_is_failed)
        .def_readwrite("last_failed_height", &monero::monero_tx_wallet::m_last_failed_height)
        .def_readwrite("last_failed_hash", &monero::monero_tx_wallet::m_last_failed_hash)
        .def_readwrite("max_used_block_height", &monero::monero_tx_wallet::m_max_used_block_height)
        .def_readwrite("max_used_block_hash", &monero::monero_tx_wallet::m_max_used_block_hash)
        .def_readwrite("signatures", &monero::monero_tx_wallet::m_signatures)
        
        .def_readwrite("tx_set", &monero::monero_tx_wallet::m_tx_set)
        .def_readwrite("is_incoming", &monero::monero_tx_wallet::m_is_incoming)
        .def_readwrite("is_outgoing", &monero::monero_tx_wallet::m_is_outgoing)
        .def_readwrite("incoming_transfers", &monero::monero_tx_wallet::m_incoming_transfers)
        .def_readwrite("outgoing_transfer", &monero::monero_tx_wallet::m_outgoing_transfer)
        .def_readwrite("note", &monero::monero_tx_wallet::m_note)
        .def_readwrite("is_locked", &monero::monero_tx_wallet::m_is_locked)
        .def_readwrite("input_sum", &monero::monero_tx_wallet::m_input_sum)
        .def_readwrite("output_sum", &monero::monero_tx_wallet::m_output_sum)
        .def_readwrite("change_address", &monero::monero_tx_wallet::m_change_address)
        .def_readwrite("change_amount", &monero::monero_tx_wallet::m_change_amount)
        .def_readwrite("num_dummy_outputs", &monero::monero_tx_wallet::m_num_dummy_outputs)
        .def_readwrite("extra_hex", &monero::monero_tx_wallet::m_extra_hex);

    // monero_tx_set
    py::class_<monero::monero_tx_set>(m, "MoneroTxSet")
        .def(py::init<>())
        .def_readwrite("txs", &monero::monero_tx_set::m_txs)
        .def_readwrite("signed_tx_hex", &monero::monero_tx_set::m_signed_tx_hex)
        .def_readwrite("unsigned_tx_hex", &monero::monero_tx_set::m_unsigned_tx_hex)
        .def_readwrite("multisig_tx_hex", &monero::monero_tx_set::m_multisig_tx_hex);

    // monero_integrated_address
    py::class_<monero::monero_integrated_address>(m, "MoneroIntegratedAddress")
        .def(py::init<>())
        .def_readwrite("standard_address", &monero::monero_integrated_address::m_standard_address)
        .def_readwrite("payment_id", &monero::monero_integrated_address::m_payment_id)
        .def_readwrite("integrated_address", &monero::monero_integrated_address::m_integrated_address);

    // enum monero_tx_priority
    py::enum_<monero::monero_tx_priority>(m, "MoneroTxPriority")
        .value("DEFAULT", monero::monero_tx_priority::DEFAULT)
        .value("UNIMPORTANT", monero::monero_tx_priority::UNIMPORTANT)
        .value("NORMAL", monero::monero_tx_priority::NORMAL)
        .value("ELEVATED", monero::monero_tx_priority::ELEVATED);

    // monero_tx_config
    py::class_<monero::monero_tx_config>(m, "MoneroTxConfig")
        .def(py::init<>())
        .def_readwrite("address", &monero::monero_tx_config::m_address)
        .def_readwrite("amount", &monero::monero_tx_config::m_amount)
        .def_readwrite("destinations", &monero::monero_tx_config::m_destinations)
        .def_readwrite("subtract_fee_from", &monero::monero_tx_config::m_subtract_fee_from)
        .def_readwrite("payment_id", &monero::monero_tx_config::m_payment_id)
        .def_readwrite("priority", &monero::monero_tx_config::m_priority)
        .def_readwrite("ring_size", &monero::monero_tx_config::m_ring_size)
        .def_readwrite("fee", &monero::monero_tx_config::m_fee)
        .def_readwrite("account_index", &monero::monero_tx_config::m_account_index)
        .def_readwrite("subaddress_indices", &monero::monero_tx_config::m_subaddress_indices)
        .def_readwrite("can_split", &monero::monero_tx_config::m_can_split)
        .def_readwrite("relay", &monero::monero_tx_config::m_relay)
        .def_readwrite("note", &monero::monero_tx_config::m_note)
        .def_readwrite("recipient_name", &monero::monero_tx_config::m_recipient_name)
        .def_readwrite("below_amount", &monero::monero_tx_config::m_below_amount)
        .def_readwrite("sweep_each_subaddress", &monero::monero_tx_config::m_sweep_each_subaddress)
        .def_readwrite("key_image", &monero::monero_tx_config::m_key_image);

    // monero_key_image_import_result
    py::class_<monero::monero_key_image_import_result>(m, "MoneroKeyImageImportResult")
        .def(py::init<>())
        .def_readwrite("height", &monero::monero_key_image_import_result::m_height)
        .def_readwrite("spent_amount", &monero::monero_key_image_import_result::m_spent_amount)
        .def_readwrite("unspent_amount", &monero::monero_key_image_import_result::m_unspent_amount);

    // enum monero_message_signature_type
    py::enum_<monero::monero_message_signature_type>(m, "MoneroMessageSignatureType")
        .value("SIGN_WITH_SPEND_KEY", monero::monero_message_signature_type::SIGN_WITH_SPEND_KEY)
        .value("SIGN_WITH_VIEW_KEY", monero::monero_message_signature_type::SIGN_WITH_VIEW_KEY);

    // monero_message_signature_result
    py::class_<monero::monero_message_signature_result>(m, "MoneroMessageSignatureResult")
        .def(py::init<>())
        .def_readwrite("is_good", &monero::monero_message_signature_result::m_is_good)
        .def_readwrite("version", &monero::monero_message_signature_result::m_version)
        .def_readwrite("is_old", &monero::monero_message_signature_result::m_is_old)
        .def_readwrite("signature_type", &monero::monero_message_signature_result::m_signature_type);

    // monero_check
    py::class_<monero::monero_check>(m, "MoneroCheck")
        .def(py::init<>())
        .def_readwrite("is_good", &monero::monero_check::m_is_good);
    
    // monero_check_tx
    py::class_<monero::monero_check_tx>(m, "MoneroCheckTx")
        .def(py::init<>())
        .def_readwrite("is_good", &monero::monero_check_tx::m_is_good)
        .def_readwrite("in_tx_pool", &monero::monero_check_tx::m_in_tx_pool)
        .def_readwrite("num_confirmations", &monero::monero_check_tx::m_num_confirmations)
        .def_readwrite("received_amount", &monero::monero_check_tx::m_received_amount);
    
    // monero_check_reserve
    py::class_<monero::monero_check_reserve>(m, "MoneroCheckReserve")
        .def(py::init<>())
        .def_readwrite("is_good", &monero::monero_check_reserve::m_is_good)
        .def_readwrite("total_amount", &monero::monero_check_reserve::m_total_amount)
        .def_readwrite("unconfirmed_spent_amount", &monero::monero_check_reserve::m_unconfirmed_spent_amount);
    
    // monero_multisig_info
    py::class_<monero::monero_multisig_info>(m, "MoneroMultisigInfo")
        .def(py::init<>())
        .def_readwrite("is_multisig", &monero::monero_multisig_info::m_is_multisig)
        .def_readwrite("is_ready", &monero::monero_multisig_info::m_is_ready)
        .def_readwrite("threshold", &monero::monero_multisig_info::m_threshold)
        .def_readwrite("num_participants", &monero::monero_multisig_info::m_num_participants);
    
    // monero_multisig_init_result
    py::class_<monero::monero_multisig_init_result>(m, "MoneroMultisigInitResult")
        .def(py::init<>())
        .def_readwrite("address", &monero::monero_multisig_init_result::m_address)
        .def_readwrite("multisig_hex", &monero::monero_multisig_init_result::m_multisig_hex);
        
    // monero_multisig_sign_result
    py::class_<monero::monero_multisig_sign_result>(m, "MoneroMultisigSignResult")
        .def(py::init<>())
        .def_readwrite("signed_multisig_tx_hex", &monero::monero_multisig_sign_result::m_signed_multisig_tx_hex)
        .def_readwrite("tx_hashes", &monero::monero_multisig_sign_result::m_tx_hashes);

    // monero_address_book_entry
    py::class_<monero::monero_address_book_entry>(m, "MoneroAddressBookEntry")
        .def(py::init<>())
        .def_readwrite("index", &monero::monero_address_book_entry::m_index)
        .def_readwrite("address", &monero::monero_address_book_entry::m_address)
        .def_readwrite("description", &monero::monero_address_book_entry::m_description)
        .def_readwrite("payment_id", &monero::monero_address_book_entry::m_payment_id);
    
    // monero_wallet_keys
    py::class_<monero::monero_wallet_keys, std::shared_ptr<monero::monero_wallet_keys>>(m, "MoneroWalletKeys")
        .def_static("create_wallet_random", [](const monero::monero_wallet_config& config) {
            MONERO_CATCH_AND_RETHROW(monero::monero_wallet_keys::create_wallet_random(config));
        }, py::arg("config"))

        .def_static("create_wallet_from_seed", [](const monero::monero_wallet_config& config) {
            MONERO_CATCH_AND_RETHROW(monero::monero_wallet_keys::create_wallet_from_seed(config));
        }, py::arg("config"))

        .def_static("create_wallet_from_keys", [](const monero::monero_wallet_config& config) {
            MONERO_CATCH_AND_RETHROW(monero::monero_wallet_keys::create_wallet_from_keys(config));
        }, py::arg("config"))

        .def_static("get_seed_languages", []() {
            MONERO_CATCH_AND_RETHROW(monero::monero_wallet_keys::get_seed_languages());
        })
        
        .def("is_view_only", [](monero::monero_wallet_keys& self) {
            MONERO_CATCH_AND_RETHROW(self.is_view_only());
        })

        .def("get_network_type", [](monero::monero_wallet_keys& self) {
            MONERO_CATCH_AND_RETHROW(self.get_network_type());
        })
        
        .def("get_seed", [](monero::monero_wallet_keys& self) {
            MONERO_CATCH_AND_RETHROW(self.get_seed());
        })

        .def("get_seed", [](monero::monero_wallet_keys& self) {
            MONERO_CATCH_AND_RETHROW(self.get_seed());
        })

        .def("get_seed_language", [](monero::monero_wallet_keys& self) {
            MONERO_CATCH_AND_RETHROW(self.get_seed_language());
        })

        .def("get_private_view_key", [](monero::monero_wallet_keys& self) {
            MONERO_CATCH_AND_RETHROW(self.get_private_view_key());
        })

        .def("get_private_spend_key", [](monero::monero_wallet_keys& self) {
            MONERO_CATCH_AND_RETHROW(self.get_private_spend_key());
        })
        
        .def("get_public_view_key", [](monero::monero_wallet_keys& self) {
            MONERO_CATCH_AND_RETHROW(self.get_public_view_key());
        })
         
        .def("get_public_spend_key", [](monero::monero_wallet_keys& self) {
            MONERO_CATCH_AND_RETHROW(self.get_public_spend_key());
        })
        
        .def("get_primary_address", [](monero::monero_wallet_keys& self) {
            MONERO_CATCH_AND_RETHROW(self.get_primary_address());
        })
        
        .def("get_primary_address", [](monero::monero_wallet_keys& self) {
            MONERO_CATCH_AND_RETHROW(self.get_primary_address());
        })
        
        .def("get_address", [](monero::monero_wallet_full& self, uint32_t account_idx, uint32_t subaddress_idx) {
            MONERO_CATCH_AND_RETHROW(self.get_address(account_idx, subaddress_idx));
        }, py::arg("account_idx") , py::arg("subaddress_idx"))

        .def("get_integrated_address", [](monero::monero_wallet_full& self, const std::string& standard_address, const std::string& payment_id) {
            MONERO_CATCH_AND_RETHROW(self.get_integrated_address(standard_address, payment_id));
        }, py::arg("standard_address") = "" , py::arg("payment_id") = "")

        .def("decode_integrated_address", [](monero::monero_wallet_full& self, const std::string& integrated_address) {
            MONERO_CATCH_AND_RETHROW(self.decode_integrated_address(integrated_address));
        }, py::arg("integrated_address"))
        
        .def("get_account", [](monero::monero_wallet_full& self, uint32_t account_idx, bool include_subaddresses) {
            MONERO_CATCH_AND_RETHROW(self.get_account(account_idx, include_subaddresses));
        }, py::arg("account_idx") , py::arg("include_subaddresses"))

        .def("get_subaddresses", [](monero::monero_wallet_full& self, uint32_t account_idx, const std::vector<uint32_t>& subaddress_indices) {
            MONERO_CATCH_AND_RETHROW(self.get_subaddresses(account_idx, subaddress_indices));
        }, py::arg("account_idx") , py::arg("subaddress_indices"))
        
        .def("close", [](monero::monero_wallet_keys& self, bool save) {
            MONERO_CATCH_AND_RETHROW(self.close(save));
        }, py::arg("save") = false);

    // monero_wallet_full
    py::class_<monero::monero_wallet_full, std::shared_ptr<monero::monero_wallet_full>>(m, "MoneroWalletFull")
        .def_static("wallet_exists", [](const std::string& path) {
            MONERO_CATCH_AND_RETHROW(monero::monero_wallet_full::wallet_exists(path));
        }, py::arg("path"))

        .def_static("open_wallet", [](const std::string& path, const std::string& password, monero::monero_network_type nettype) {
            MONERO_CATCH_AND_RETHROW(monero::monero_wallet_full::open_wallet(path, password, nettype));
        }, py::arg("path"), py::arg("password"), py::arg("network_type"))

        .def_static("create_wallet", [](const monero::monero_wallet_config& config) {
            MONERO_CATCH_AND_RETHROW(monero::monero_wallet_full::create_wallet(config));
        }, py::arg("config"))

        .def("is_view_only", [](monero::monero_wallet_full& self) {
            MONERO_CATCH_AND_RETHROW(self.is_view_only());
        })

        .def("get_balance", [](monero::monero_wallet_full& self, uint32_t idx) {
            MONERO_CATCH_AND_RETHROW(self.get_balance(idx));
        }, py::arg("account_idx") = 0)

        .def("sync", [](monero::monero_wallet_full& self) {
            MONERO_CATCH_AND_RETHROW(self.sync());
        })

        .def("close", [](monero::monero_wallet_full& self, bool save) {
            MONERO_CATCH_AND_RETHROW(self.close(save));
        }, py::arg("save") = true);

}
