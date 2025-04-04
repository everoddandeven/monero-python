#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include "../external/monero-cpp/src/utils/monero_utils.h"
#include "../external/monero-cpp/src/daemon/monero_daemon_model.h"
#include "../external/monero-cpp/src/wallet/monero_wallet_model.h"
#include "../external/monero-cpp/src/wallet/monero_wallet_full.h"
#include "../external/monero-cpp/src/wallet/monero_wallet_keys.h"

namespace py = pybind11;

class PyMoneroWallet : public monero_wallet {
public:
    using monero_wallet::monero_wallet;

    std::string get_seed() const override {
        PYBIND11_OVERRIDE_PURE(
            std::string,
            monero_wallet,
            get_seed,
        );
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

    // enum monero_network_type
    py::enum_<monero::monero_network_type>(m, "MoneroNetworkType")
        .value("MAINNET", monero::monero_network_type::MAINNET)
        .value("TESTNET", monero::monero_network_type::TESTNET)
        .value("STAGENET", monero::monero_network_type::STAGENET);

    // monero_version
    py::class_<monero::monero_version, std::shared_ptr<monero::monero_version>>(m, "MoneroVersion")
        .def(py::init<>())
        .def_property("number", 
            [](const monero::monero_version& self) { return self.m_number.value_or(0); },
            [](monero::monero_version& self, uint32_t val) { self.m_number = val; })
        .def_property("is_release", 
            [](const monero::monero_version& self) { return self.m_is_release.value_or(false); },
            [](monero::monero_version& self, bool val) { self.m_is_release = val; });

    // monero_rpc_connection
    py::class_<monero::monero_rpc_connection, std::shared_ptr<monero_rpc_connection>>(m, "MoneroRpcConnection")
        .def(py::init<>())
        .def_property("uri", 
            [](const monero::monero_rpc_connection& self) { return self.m_uri.value_or(""); },
            [](monero::monero_rpc_connection& self, std::string val) { self.m_uri = val; })
        .def_property("username", 
            [](const monero::monero_rpc_connection& self) { return self.m_username.value_or(""); },
            [](monero::monero_rpc_connection& self, std::string val) { self.m_username = val; })
        .def_property("password", 
            [](const monero::monero_rpc_connection& self) { return self.m_password.value_or(""); },
            [](monero::monero_rpc_connection& self, std::string val) { self.m_password = val; });

    // monero_block_header
    py::class_<monero::monero_block_header, std::shared_ptr<monero::monero_block_header>>(m, "MoneroBlockHeader")
        .def(py::init<>())
        .def_property("hash", 
            [](const monero::monero_block_header& self) { return self.m_hash.value_or(""); },
            [](monero::monero_block_header& self, std::string val) { self.m_hash = val; })
        .def_property("height", 
            [](const monero::monero_block_header& self) { return self.m_height.value_or(0); },
            [](monero::monero_block_header& self, uint64_t val) { self.m_height = val; })
        .def_property("timestamp", 
            [](const monero::monero_block_header& self) { return self.m_timestamp.value_or(0); },
            [](monero::monero_block_header& self, uint64_t val) { self.m_timestamp = val; })
        .def_property("size", 
            [](const monero::monero_block_header& self) { return self.m_size.value_or(0); },
            [](monero::monero_block_header& self, uint64_t val) { self.m_size = val; })
        .def_property("weight", 
            [](const monero::monero_block_header& self) { return self.m_weight.value_or(0); },
            [](monero::monero_block_header& self, uint64_t val) { self.m_weight = val; })
        .def_property("long_term_weight", 
            [](const monero::monero_block_header& self) { return self.m_long_term_weight.value_or(0); },
            [](monero::monero_block_header& self, uint64_t val) { self.m_long_term_weight = val; })
        .def_property("depth", 
            [](const monero::monero_block_header& self) { return self.m_depth.value_or(0); },
            [](monero::monero_block_header& self, uint64_t val) { self.m_depth = val; })
        .def_property("difficulty", 
            [](const monero::monero_block_header& self) { return self.m_difficulty.value_or(0); },
            [](monero::monero_block_header& self, uint64_t val) { self.m_difficulty = val; })
        .def_property("cumulative_difficulty", 
            [](const monero::monero_block_header& self) { return self.m_cumulative_difficulty.value_or(0); },
            [](monero::monero_block_header& self, uint64_t val) { self.m_cumulative_difficulty = val; })
        .def_property("major_version", 
            [](const monero::monero_block_header& self) { return self.m_major_version.value_or(0); },
            [](monero::monero_block_header& self, uint32_t val) { self.m_major_version = val; })
        .def_property("minor_version", 
            [](const monero::monero_block_header& self) { return self.m_minor_version.value_or(0); },
            [](monero::monero_block_header& self, uint32_t val) { self.m_minor_version = val; })
        .def_property("nonce", 
            [](const monero::monero_block_header& self) { return self.m_nonce.value_or(0); },
            [](monero::monero_block_header& self, uint32_t val) { self.m_nonce = val; })
        .def_property("miner_tx_hash", 
            [](const monero::monero_block_header& self) { return self.m_miner_tx_hash.value_or(""); },
            [](monero::monero_block_header& self, std::string& val) { self.m_miner_tx_hash = val; })
        .def_property("num_txs", 
            [](const monero::monero_block_header& self) { return self.m_num_txs.value_or(0); },
            [](monero::monero_block_header& self, uint32_t val) { self.m_num_txs = val; })
        .def_property("orphan_status", 
            [](const monero::monero_block_header& self) { return self.m_orphan_status.value_or(false); },
            [](monero::monero_block_header& self, bool val) { self.m_orphan_status = val; })
        .def_property("m_prev_hash", 
            [](const monero::monero_block_header& self) { return self.m_prev_hash.value_or(""); },
            [](monero::monero_block_header& self, std::string& val) { self.m_prev_hash = val; })
        .def_property("reward", 
            [](const monero::monero_block_header& self) { return self.m_reward.value_or(0); },
            [](monero::monero_block_header& self, uint64_t val) { self.m_reward = val; })
        .def_property("pow_hash", 
            [](const monero::monero_block_header& self) { return self.m_pow_hash.value_or(""); },
            [](monero::monero_block_header& self, std::string& val) { self.m_pow_hash = val; });

    // monero_block
    py::class_<monero::monero_block, monero::monero_block_header, std::shared_ptr<monero::monero_block>>(m, "MoneroBlock")
        .def(py::init<>())
        .def_property("hex", 
            [](const monero::monero_block& self) { return self.m_hex.value_or(""); },
            [](monero::monero_block& self, std::string val) { self.m_hex = val; })
        .def_property("miner_tx", 
            [](const monero::monero_block& self) { return self.m_miner_tx.value_or(nullptr); },
            [](monero::monero_block& self, std::shared_ptr<monero::monero_tx> val) { self.m_miner_tx = val; })
        .def_readwrite("txs", &monero::monero_block::m_txs)
        .def_readwrite("tx_hashes", &monero::monero_block::m_tx_hashes);

    // monero_tx
    py::class_<monero::monero_tx, std::shared_ptr<monero::monero_tx>>(m, "MoneroTx")
        .def(py::init<>())
        .def_property("block", 
            [](const monero::monero_tx& self) { return self.m_block.value_or(nullptr); },
            [](monero::monero_tx& self, std::shared_ptr<monero::monero_block> val) { self.m_block = val; })
        .def_property("hash", 
            [](const monero::monero_tx& self) { return self.m_hash.value_or(""); },
            [](monero::monero_tx& self, std::string val) { self.m_hash = val; })
        .def_property("version", 
            [](const monero::monero_tx& self) { return self.m_version.value_or(0); },
            [](monero::monero_tx& self, uint32_t val) { self.m_version = val; })
        .def_property("is_miner_tx", 
            [](const monero::monero_tx& self) { return self.m_is_miner_tx.value_or(false); },
            [](monero::monero_tx& self, bool val) { self.m_is_miner_tx = val; })
        .def_property("payment_id", 
            [](const monero::monero_tx& self) { return self.m_payment_id.value_or(""); },
            [](monero::monero_tx& self, std::string val) { self.m_payment_id = val; })
        .def_property("fee", 
            [](const monero::monero_tx& self) { return self.m_fee.value_or(0); },
            [](monero::monero_tx& self, uint64_t val) { self.m_fee = val; })
        .def_property("ring_size", 
            [](const monero::monero_tx& self) { return self.m_ring_size.value_or(0); },
            [](monero::monero_tx& self, uint32_t val) { self.m_ring_size = val; })
        .def_property("relay", 
            [](const monero::monero_tx& self) { return self.m_relay.value_or(false); },
            [](monero::monero_tx& self, bool val) { self.m_relay = val; })
        .def_property("is_relayed", 
            [](const monero::monero_tx& self) { return self.m_is_relayed.value_or(false); },
            [](monero::monero_tx& self, bool val) { self.m_is_relayed = val; })
        .def_property("is_confirmed", 
            [](const monero::monero_tx& self) { return self.m_is_confirmed.value_or(false); },
            [](monero::monero_tx& self, bool val) { self.m_is_confirmed = val; })
        .def_property("in_tx_pool", 
            [](const monero::monero_tx& self) { return self.m_in_tx_pool.value_or(false); },
            [](monero::monero_tx& self, bool val) { self.m_in_tx_pool = val; })
        .def_property("num_confirmations", 
            [](const monero::monero_tx& self) { return self.m_num_confirmations.value_or(0); },
            [](monero::monero_tx& self, uint64_t val) { self.m_num_confirmations = val; })
        .def_property("unlock_time", 
            [](const monero::monero_tx& self) { return self.m_unlock_time.value_or(0); },
            [](monero::monero_tx& self, uint64_t val) { self.m_unlock_time = val; })
        .def_property("last_relayed_timestamp", 
            [](const monero::monero_tx& self) { return self.m_last_relayed_timestamp.value_or(0); },
            [](monero::monero_tx& self, uint64_t val) { self.m_last_relayed_timestamp = val; })
        .def_property("received_timestamp", 
            [](const monero::monero_tx& self) { return self.m_received_timestamp.value_or(0); },
            [](monero::monero_tx& self, uint64_t val) { self.m_received_timestamp = val; })
        .def_property("is_double_spend_seen", 
            [](const monero::monero_tx& self) { return self.m_is_double_spend_seen.value_or(false); },
            [](monero::monero_tx& self, bool val) { self.m_is_double_spend_seen = val; })
        .def_property("key", 
            [](const monero::monero_tx& self) { return self.m_key.value_or(""); },
            [](monero::monero_tx& self, std::string val) { self.m_key = val; })
        .def_property("full_hex", 
            [](const monero::monero_tx& self) { return self.m_full_hex.value_or(""); },
            [](monero::monero_tx& self, std::string val) { self.m_full_hex = val; })
        .def_property("pruned_hex", 
            [](const monero::monero_tx& self) { return self.m_pruned_hex.value_or(""); },
            [](monero::monero_tx& self, std::string val) { self.m_pruned_hex = val; })
        .def_property("prunable_hex", 
            [](const monero::monero_tx& self) { return self.m_prunable_hex.value_or(""); },
            [](monero::monero_tx& self, std::string val) { self.m_prunable_hex = val; })
        .def_property("prunable_hash", 
            [](const monero::monero_tx& self) { return self.m_prunable_hash.value_or(""); },
            [](monero::monero_tx& self, std::string val) { self.m_prunable_hash = val; })
        .def_property("size", 
            [](const monero::monero_tx& self) { return self.m_size.value_or(0); },
            [](monero::monero_tx& self, uint64_t val) { self.m_size = val; })
        .def_property("weight", 
            [](const monero::monero_tx& self) { return self.m_weight.value_or(0); },
            [](monero::monero_tx& self, uint64_t val) { self.m_weight = val; })
        .def_readwrite("inputs", &monero::monero_tx::m_inputs)
        .def_readwrite("outputs", &monero::monero_tx::m_outputs)
        .def_readwrite("output_indices", &monero::monero_tx::m_output_indices)
        .def_property("metadata", 
            [](const monero::monero_tx& self) { return self.m_metadata.value_or(""); },
            [](monero::monero_tx& self, std::string val) { self.m_metadata = val; })
        .def_property("common_tx_sets", 
            [](const monero::monero_tx& self) { return self.m_common_tx_sets.value_or(""); },
            [](monero::monero_tx& self, std::string val) { self.m_common_tx_sets = val; })
        .def_readwrite("extra", &monero::monero_tx::m_extra)
        .def_property("rct_signatures", 
            [](const monero::monero_tx& self) { return self.m_rct_signatures.value_or(""); },
            [](monero::monero_tx& self, std::string val) { self.m_rct_signatures = val; })
        .def_property("rct_sig_prunable", 
            [](const monero::monero_tx& self) { return self.m_rct_sig_prunable.value_or(""); },
            [](monero::monero_tx& self, std::string val) { self.m_rct_sig_prunable = val; })
        .def_property("is_kept_by_block", 
            [](const monero::monero_tx& self) { return self.m_is_kept_by_block.value_or(false); },
            [](monero::monero_tx& self, bool val) { self.m_is_kept_by_block = val; })
        .def_property("is_failed", 
            [](const monero::monero_tx& self) { return self.m_is_failed.value_or(false); },
            [](monero::monero_tx& self, bool val) { self.m_is_failed = val; })
        .def_property("last_failed_height", 
            [](const monero::monero_tx& self) { return self.m_last_failed_height.value_or(0); },
            [](monero::monero_tx& self, uint64_t val) { self.m_last_failed_height = val; })
        .def_property("last_failed_hash", 
            [](const monero::monero_tx& self) { return self.m_last_failed_hash.value_or(""); },
            [](monero::monero_tx& self, std::string val) { self.m_last_failed_hash = val; })
        .def_property("max_used_block_height", 
            [](const monero::monero_tx& self) { return self.m_max_used_block_height.value_or(0); },
            [](monero::monero_tx& self, uint64_t val) { self.m_max_used_block_height = val; })
        .def_property("max_used_block_hash", 
            [](const monero::monero_tx& self) { return self.m_max_used_block_hash.value_or(""); },
            [](monero::monero_tx& self, std::string val) { self.m_max_used_block_hash = val; })
        .def_readwrite("signatures", &monero::monero_tx::m_signatures);

    // monero_key_image
    py::class_<monero::monero_key_image, std::shared_ptr<monero::monero_key_image>>(m, "MoneroKeyImage")
        .def(py::init<>())
        .def_property("hex", 
            [](const monero::monero_key_image& self) { return self.m_hex.value_or(""); },
            [](monero::monero_key_image& self, std::string val) { self.m_hex = val; })
        .def_property("signature", 
            [](const monero::monero_key_image& self) { return self.m_signature.value_or(""); },
            [](monero::monero_key_image& self, std::string val) { self.m_signature = val; });

    // monero_output
    py::class_<monero::monero_output, std::shared_ptr<monero::monero_output>>(m, "MoneroOutput")
        .def(py::init<>())
        .def_readwrite("tx", &monero::monero_output::m_tx)
        .def_property("key_image", 
            [](const monero::monero_output& self) { return self.m_key_image.value_or(nullptr); },
            [](monero::monero_output& self, std::shared_ptr<monero_key_image> val) { self.m_key_image = val; })
        .def_property("amount", 
            [](const monero::monero_output& self) { return self.m_amount.value_or(0); },
            [](monero::monero_output& self, uint64_t val) { self.m_amount = val; })
        .def_property("index", 
            [](const monero::monero_output& self) { return self.m_index.value_or(0); },
            [](monero::monero_output& self, uint64_t val) { self.m_index = val; })
        .def_property("stealth_public_key", 
            [](const monero::monero_output& self) { return self.m_stealth_public_key.value_or(""); },
            [](monero::monero_output& self, std::string val) { self.m_stealth_public_key = val; })
        .def_readwrite("ring_output_indices", &monero::monero_output::m_ring_output_indices);

    // monero_wallet_config
    py::class_<monero::monero_wallet_config, std::shared_ptr<monero::monero_wallet_config>>(m, "MoneroWalletConfig")
        .def(py::init<>())
        .def_property("path", 
            [](const monero::monero_wallet_config& self) { return self.m_path.value_or(""); },
            [](monero::monero_wallet_config& self, const std::string& val) { self.m_path = val; })
        .def_property("password", 
            [](const monero::monero_wallet_config& self) { return self.m_password.value_or(""); },
            [](monero::monero_wallet_config& self, const std::string& val) { self.m_password = val; })
        .def_property("network_type", 
            [](const monero::monero_wallet_config& self) { return self.m_network_type.value_or(monero::monero_network_type::MAINNET); },
            [](monero::monero_wallet_config& self, monero::monero_network_type nettype) { self.m_network_type = nettype; })
        .def_property("server", 
            [](const monero::monero_wallet_config& self) { return self.m_server.value_or(monero::monero_rpc_connection()); },
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
            [](const monero::monero_wallet_config& self) { return self.m_save_current.value_or(false); },
            [](monero::monero_wallet_config& self, bool val) { self.m_save_current = val; }) 
        .def_property("language", 
            [](const monero::monero_wallet_config& self) { return self.m_language.value_or(""); },
            [](monero::monero_wallet_config& self, const std::string& val) { self.m_language = val; })
        .def_property("restore_height", 
            [](const monero::monero_wallet_config& self) { return self.m_restore_height.value_or(0); },
            [](monero::monero_wallet_config& self, uint64_t height) { self.m_restore_height = height; })
        .def_property("account_lookahead", 
            [](const monero::monero_wallet_config& self) { return self.m_account_lookahead.value_or(0); },
            [](monero::monero_wallet_config& self, uint64_t val) { self.m_account_lookahead = val; }) 
        .def_property("subaddress_lookahead", 
            [](const monero::monero_wallet_config& self) { return self.m_subaddress_lookahead.value_or(0); },
            [](monero::monero_wallet_config& self, uint64_t val) { self.m_subaddress_lookahead = val; })
        .def_property("is_multisig", 
            [](const monero::monero_wallet_config& self) { return self.m_is_multisig.value_or(false); },
            [](monero::monero_wallet_config& self, bool is_multisig) { self.m_is_multisig = is_multisig; })
        .def("copy", [](monero::monero_wallet_config& self) {
            MONERO_CATCH_AND_RETHROW(self.copy());
        });

    // monero_subaddress
    py::class_<monero::monero_subaddress, std::shared_ptr<monero::monero_subaddress>>(m, "MoneroSubaddress")
        .def(py::init<>())
        .def_property("account_index", 
            [](const monero::monero_subaddress& self) { return self.m_account_index.value_or(NULL); },
            [](monero::monero_subaddress& self, uint32_t val) { self.m_account_index = val; })
        .def_property("index", 
            [](const monero::monero_subaddress& self) { return self.m_index.value_or(NULL); },
            [](monero::monero_subaddress& self, uint32_t val) { self.m_index = val; })
        .def_property("address", 
            [](const monero::monero_subaddress& self) { return self.m_address.value_or(""); },
            [](monero::monero_subaddress& self, std::string val) { self.m_address = val; })
        .def_property("label", 
            [](const monero::monero_subaddress& self) { return self.m_label.value_or(""); },
            [](monero::monero_subaddress& self, std::string val) { self.m_label = val; })
        .def_property("balance", 
            [](const monero::monero_subaddress& self) { return self.m_balance.value_or(0); },
            [](monero::monero_subaddress& self, uint64_t val) { self.m_balance = val; })
        .def_property("unlocked_balance", 
            [](const monero::monero_subaddress& self) { return self.m_unlocked_balance.value_or(0); },
            [](monero::monero_subaddress& self, uint64_t val) { self.m_unlocked_balance = val; })
        .def_property("num_unspent_outputs", 
            [](const monero::monero_subaddress& self) { return self.m_num_unspent_outputs.value_or(0); },
            [](monero::monero_subaddress& self, uint64_t val) { self.m_num_unspent_outputs = val; })
        .def_property("is_used", 
            [](const monero::monero_subaddress& self) { return self.m_is_used.value_or(NULL); },
            [](monero::monero_subaddress& self, bool val) { self.m_is_used = val; })
        .def_property("num_blocks_to_unlock", 
            [](const monero::monero_subaddress& self) { return self.m_num_blocks_to_unlock.value_or(0); },
            [](monero::monero_subaddress& self, uint64_t val) { self.m_num_blocks_to_unlock = val; });

    // monero_sync_result
    py::class_<monero::monero_sync_result, std::shared_ptr<monero::monero_sync_result>>(m, "MoneroSyncResult")
        .def_readwrite("num_blocks_fetched", &monero::monero_sync_result::m_num_blocks_fetched)
        .def_readwrite("received_money", &monero::monero_sync_result::m_received_money);

    // monero_account
    py::class_<monero::monero_account, std::shared_ptr<monero::monero_account>>(m, "MoneroAccount")
        .def(py::init<>())
        .def_property("index", 
            [](const monero::monero_account& self) { return self.m_index.value_or(NULL); },
            [](monero::monero_account& self, uint32_t val) { self.m_index = val; })
        .def_property("primary_address", 
            [](const monero::monero_account& self) { return self.m_primary_address.value_or(""); },
            [](monero::monero_account& self, std::string val) { self.m_primary_address = val; })
        .def_property("balance", 
            [](const monero::monero_account& self) { return self.m_balance.value_or(0); },
            [](monero::monero_account& self, uint64_t val) { self.m_balance = val; })
        .def_property("unlocked_balance", 
            [](const monero::monero_account& self) { return self.m_unlocked_balance.value_or(0); },
            [](monero::monero_account& self, uint64_t val) { self.m_unlocked_balance = val; })
        .def_property("tag", 
            [](const monero::monero_account& self) { return self.m_tag.value_or(""); },
            [](monero::monero_account& self, std::string val) { self.m_tag = val; })
        .def_readwrite("subaddresses", &monero::monero_account::m_subaddresses);

    // monero_destination
    py::class_<monero::monero_destination, std::shared_ptr<monero::monero_destination>>(m, "MoneroDestination")
        .def(py::init<>())
        .def_property("address", 
            [](const monero::monero_destination& self) { return self.m_address.value_or(""); },
            [](monero::monero_destination& self, std::string val) { self.m_address = val; })
        .def_property("amount", 
            [](const monero::monero_destination& self) { return self.m_amount.value_or(0); },
            [](monero::monero_destination& self, uint64_t val) { self.m_amount = val; });

    // monero_transfer
    py::class_<monero::monero_transfer, PyMoneroTransfer, std::shared_ptr<monero::monero_transfer>>(m, "MoneroTransfer")
        .def(py::init<>())
        .def_readwrite("tx", &monero::monero_transfer::m_tx)
        .def_property("account_index", 
            [](const monero::monero_transfer& self) { return self.m_account_index.value_or(NULL); },
            [](monero::monero_transfer& self, uint32_t val) { self.m_account_index = val; })
        .def_property("amount", 
            [](const monero::monero_transfer& self) { return self.m_amount.value_or(0); },
            [](monero::monero_transfer& self, uint64_t val) { self.m_amount = val; })
        .def("is_incoming", [](monero::monero_transfer& self) {
            MONERO_CATCH_AND_RETHROW(self.is_incoming().value_or(NULL));
        })
        .def("is_outgoing", [](monero::monero_transfer& self) {
            MONERO_CATCH_AND_RETHROW(self.is_outgoing().value_or(NULL));
        });
    
    // monero_incoming_transfer
    py::class_<monero::monero_incoming_transfer, monero::monero_transfer, std::shared_ptr<monero::monero_incoming_transfer>>(m, "MoneroIncomingTransfer")
        .def(py::init<>())
        .def_readwrite("tx", &monero::monero_incoming_transfer::m_tx)
        .def_property("account_index", 
            [](const monero::monero_incoming_transfer& self) { return self.m_account_index.value_or(NULL); },
            [](monero::monero_incoming_transfer& self, uint32_t val) { self.m_account_index = val; })
        .def_property("amount", 
            [](const monero::monero_incoming_transfer& self) { return self.m_amount.value_or(0); },
            [](monero::monero_incoming_transfer& self, uint64_t val) { self.m_amount = val; })
        .def("is_incoming", [](monero::monero_incoming_transfer& self) {
            MONERO_CATCH_AND_RETHROW(self.is_incoming().value_or(NULL));
        })
        .def("is_outgoing", [](monero::monero_incoming_transfer& self) {
            MONERO_CATCH_AND_RETHROW(self.is_outgoing().value_or(NULL));
        })
        .def_property("address", 
            [](const monero::monero_incoming_transfer& self) { return self.m_address.value_or(""); },
            [](monero::monero_incoming_transfer& self, std::string val) { self.m_address = val; })
        .def_property("subaddress_index", 
            [](const monero::monero_incoming_transfer& self) { return self.m_subaddress_index.value_or(NULL); },
            [](monero::monero_incoming_transfer& self, uint32_t val) { self.m_subaddress_index = val; })
        .def_property("num_suggested_confirmations", 
            [](const monero::monero_incoming_transfer& self) { return self.m_num_suggested_confirmations.value_or(NULL); },
            [](monero::monero_incoming_transfer& self, uint64_t val) { self.m_num_suggested_confirmations = val; });

    // monero_outgoing_transfer
    py::class_<monero::monero_outgoing_transfer, monero::monero_transfer, std::shared_ptr<monero::monero_outgoing_transfer>>(m, "MoneroOutgoingTransfer")
        .def(py::init<>())
        .def_readwrite("tx", &monero::monero_transfer::m_tx)
        .def_property("account_index", 
            [](const monero::monero_transfer& self) { return self.m_account_index.value_or(NULL); },
            [](monero::monero_transfer& self, uint32_t val) { self.m_account_index = val; })
        .def_property("amount", 
            [](const monero::monero_transfer& self) { return self.m_amount.value_or(0); },
            [](monero::monero_transfer& self, uint64_t val) { self.m_amount = val; })
        .def("is_incoming", [](monero::monero_transfer& self) {
            MONERO_CATCH_AND_RETHROW(self.is_incoming().value_or(NULL));
        })
        .def("is_outgoing", [](monero::monero_transfer& self) {
            MONERO_CATCH_AND_RETHROW(self.is_outgoing().value_or(NULL));
        })
        .def_readwrite("subaddress_indices", &monero::monero_outgoing_transfer::m_subaddress_indices)
        .def_readwrite("addresses", &monero::monero_outgoing_transfer::m_addresses)
        .def_readwrite("destinations", &monero::monero_outgoing_transfer::m_destinations);

    // monero_transfer_query
    py::class_<monero::monero_transfer_query, monero::monero_transfer, std::shared_ptr<monero_transfer_query>>(m, "MoneroTransferQuery")
        .def(py::init<>())
        .def_readwrite("tx", &monero::monero_transfer::m_tx)
        .def_property("account_index", 
            [](const monero::monero_transfer_query& self) { return self.m_account_index.value_or(NULL); },
            [](monero::monero_transfer_query& self, uint32_t val) { self.m_account_index = val; })
        .def_property("amount", 
            [](const monero::monero_transfer_query& self) { return self.m_amount.value_or(0); },
            [](monero::monero_transfer_query& self, uint64_t val) { self.m_amount = val; })
        .def("is_incoming", [](monero::monero_transfer_query& self) {
            MONERO_CATCH_AND_RETHROW(self.is_incoming().value_or(NULL));
        })
        .def("is_outgoing", [](monero::monero_transfer_query& self) {
            MONERO_CATCH_AND_RETHROW(self.is_outgoing().value_or(NULL));
        })
        .def_property("address", 
            [](const monero::monero_transfer_query& self) { return self.m_address.value_or(""); },
            [](monero::monero_transfer_query& self, std::string& val) { self.m_address = val; })
        .def_property("subaddress_index",
            [](const monero::monero_transfer_query& self) { return self.m_subaddress_index.value_or(NULL); },
            [](monero::monero_transfer_query& self, uint32_t val) { self.m_subaddress_index = val; })
        .def_readwrite("subaddress_indices", &monero::monero_transfer_query::m_subaddress_indices)
        .def_readwrite("destinations", &monero::monero_transfer_query::m_destinations)
        .def_property("has_destinations", 
            [](const monero::monero_transfer_query& self) { return self.m_has_destinations.value_or(false); },
            [](monero::monero_transfer_query& self, bool val) { self.m_has_destinations = val; })
        .def_property("tx_query", 
            [](const monero::monero_transfer_query& self) { return self.m_tx_query.value_or(nullptr); },
            [](monero::monero_transfer_query& self, std::shared_ptr<monero_tx_query> val) { self.m_tx_query = val; });

    // monero_output_wallet
    py::class_<monero::monero_output_wallet, monero::monero_output, std::shared_ptr<monero::monero_output_wallet>>(m, "MoneroOutputWallet")
        .def(py::init<>())
        .def_readwrite("tx", &monero::monero_output_wallet::m_tx)
        .def_property("key_image", 
            [](const monero::monero_output_wallet& self) { return self.m_key_image.value_or(nullptr); },
            [](monero::monero_output_wallet& self, std::shared_ptr<monero_key_image> val) { self.m_key_image = val; })
        .def_property("amount", 
            [](const monero::monero_output_wallet& self) { return self.m_amount.value_or(0); },
            [](monero::monero_output_wallet& self, uint64_t val) { self.m_amount = val; })
        .def_property("index", 
            [](const monero::monero_output_wallet& self) { return self.m_index.value_or(0); },
            [](monero::monero_output_wallet& self, uint64_t val) { self.m_index = val; })
        .def_property("stealth_public_key", 
            [](const monero::monero_output_wallet& self) { return self.m_stealth_public_key.value_or(""); },
            [](monero::monero_output_wallet& self, std::string val) { self.m_stealth_public_key = val; })
        .def_readwrite("ring_output_indices", &monero::monero_output_wallet::m_ring_output_indices)
        .def_property("account_index", 
            [](const monero::monero_output_wallet& self) { return self.m_account_index.value_or(0); },
            [](monero::monero_output_wallet& self, uint32_t val) { self.m_account_index = val; })
        .def_property("subaddress_index", 
            [](const monero::monero_output_wallet& self) { return self.m_subaddress_index.value_or(0); },
            [](monero::monero_output_wallet& self, uint32_t val) { self.m_subaddress_index = val; })
        .def_property("is_spent", 
            [](const monero::monero_output_wallet& self) { return self.m_is_spent.value_or(false); },
            [](monero::monero_output_wallet& self, bool val) { self.m_is_spent = val; })
        .def_property("is_frozen", 
            [](const monero::monero_output_wallet& self) { return self.m_is_frozen.value_or(false); },
            [](monero::monero_output_wallet& self, bool val) { self.m_is_frozen = val; });

    // monero_output_query
    py::class_<monero::monero_output_query, monero::monero_output_wallet, std::shared_ptr<monero::monero_output_query>>(m, "MoneroOutputQuery")
        .def(py::init<>())
        .def_readwrite("tx", &monero::monero_output_query::m_tx)
        .def_property("key_image", 
            [](const monero::monero_output_query& self) { return self.m_key_image.value_or(nullptr); },
            [](monero::monero_output_query& self, std::shared_ptr<monero_key_image> val) { self.m_key_image = val; })
        .def_property("amount", 
            [](const monero::monero_output_query& self) { return self.m_amount.value_or(0); },
            [](monero::monero_output_query& self, uint64_t val) { self.m_amount = val; })
        .def_property("index", 
            [](const monero::monero_output_query& self) { return self.m_index.value_or(0); },
            [](monero::monero_output_query& self, uint64_t val) { self.m_index = val; })
        .def_property("stealth_public_key", 
            [](const monero::monero_output_query& self) { return self.m_stealth_public_key.value_or(""); },
            [](monero::monero_output_query& self, std::string val) { self.m_stealth_public_key = val; })
        .def_readwrite("ring_output_indices", &monero::monero_output_query::m_ring_output_indices)
        .def_property("account_index", 
            [](const monero::monero_output_query& self) { return self.m_account_index.value_or(0); },
            [](monero::monero_output_query& self, uint32_t val) { self.m_account_index = val; })
        .def_property("subaddress_index", 
            [](const monero::monero_output_query& self) { return self.m_subaddress_index.value_or(0); },
            [](monero::monero_output_query& self, uint32_t val) { self.m_subaddress_index = val; })
        .def_property("is_spent", 
            [](const monero::monero_output_query& self) { return self.m_is_spent.value_or(false); },
            [](monero::monero_output_query& self, bool val) { self.m_is_spent = val; })
        .def_property("is_frozen", 
            [](const monero::monero_output_query& self) { return self.m_is_frozen.value_or(false); },
            [](monero::monero_output_query& self, bool val) { self.m_is_frozen = val; })
        .def_readwrite("subaddress_indices", &monero::monero_output_query::m_subaddress_indices)
        .def_property("min_amount", 
            [](const monero::monero_output_query& self) { return self.m_min_amount.value_or(0); },
            [](monero::monero_output_query& self, uint64_t val) { self.m_min_amount = val; })
        .def_property("max_amount", 
            [](const monero::monero_output_query& self) { return self.m_max_amount.value_or(0); },
            [](monero::monero_output_query& self, uint64_t val) { self.m_max_amount = val; })
        .def_property("min_amount", 
            [](const monero::monero_output_query& self) { return self.m_min_amount.value_or(0); },
            [](monero::monero_output_query& self, uint64_t val) { self.m_min_amount = val; })
        .def_property("tx_query", 
            [](const monero::monero_output_query& self) { return self.m_tx_query.value_or(nullptr); },
            [](monero::monero_output_query& self, std::shared_ptr<monero::monero_tx_query> val) { self.m_tx_query = val; });

    // monero_tx_wallet
    py::class_<monero::monero_tx_wallet, monero::monero_tx, std::shared_ptr<monero::monero_tx_wallet>>(m, "MoneroTxWallet")
        .def(py::init<>())
        .def_property("tx_set", 
            [](const monero::monero_tx_wallet& self) { return self.m_tx_set.value_or(nullptr); },
            [](monero::monero_tx_wallet& self, std::shared_ptr<monero_tx_set> val) { self.m_tx_set = val; })
        .def_property("is_incoming", 
            [](const monero::monero_tx_wallet& self) { return self.m_is_incoming.value_or(false); },
            [](monero::monero_tx_wallet& self, bool val) { self.m_is_incoming = val; })
        .def_property("is_outgoing", 
            [](const monero::monero_tx_wallet& self) { return self.m_is_outgoing.value_or(false); },
            [](monero::monero_tx_wallet& self, bool val) { self.m_is_outgoing = val; })
        .def_readwrite("incoming_transfers", &monero::monero_tx_wallet::m_incoming_transfers)
        .def_readwrite("outgoing_transfer", &monero::monero_tx_wallet::m_outgoing_transfer)
        .def_property("outgoing_transfer", 
            [](const monero::monero_tx_wallet& self) { return self.m_outgoing_transfer.value_or(nullptr); },
            [](monero::monero_tx_wallet& self, std::shared_ptr<monero_outgoing_transfer> val) { self.m_outgoing_transfer = val; })
        .def_property("note", 
            [](const monero::monero_tx_wallet& self) { return self.m_note.value_or(""); },
            [](monero::monero_tx_wallet& self, std::string& val) { self.m_note = val; })
        .def_property("is_locked", 
            [](const monero::monero_tx_wallet& self) { return self.m_is_locked.value_or(false); },
            [](monero::monero_tx_wallet& self, bool val) { self.m_is_locked = val; })
        .def_property("input_sum", 
            [](const monero::monero_tx_wallet& self) { return self.m_input_sum.value_or(0); },
            [](monero::monero_tx_wallet& self, uint64_t val) { self.m_input_sum = val; })
        .def_property("output_sum", 
            [](const monero::monero_tx_wallet& self) { return self.m_output_sum.value_or(0); },
            [](monero::monero_tx_wallet& self, uint64_t val) { self.m_output_sum = val; })
        .def_property("change_address", 
            [](const monero::monero_tx_wallet& self) { return self.m_change_address.value_or(""); },
            [](monero::monero_tx_wallet& self, std::string& val) { self.m_change_address = val; })
        .def_property("change_amount", 
            [](const monero::monero_tx_wallet& self) { return self.m_change_amount.value_or(0); },
            [](monero::monero_tx_wallet& self, uint64_t val) { self.m_change_amount = val; })
        .def_property("num_dummy_outputs", 
            [](const monero::monero_tx_wallet& self) { return self.m_num_dummy_outputs.value_or(0); },
            [](monero::monero_tx_wallet& self, uint32_t val) { self.m_num_dummy_outputs = val; })
        .def_property("extra_hex", 
            [](const monero::monero_tx_wallet& self) { return self.m_extra_hex.value_or(""); },
            [](monero::monero_tx_wallet& self, std::string& val) { self.m_extra_hex = val; });

    // monero_tx_query
    py::class_<monero::monero_tx_query, monero::monero_tx_wallet, std::shared_ptr<monero::monero_tx_query>>(m, "MoneroTxQuery")
        .def(py::init<>());

    // monero_tx_set
    py::class_<monero::monero_tx_set, std::shared_ptr<monero::monero_tx_set>>(m, "MoneroTxSet")
        .def(py::init<>())
        .def_readwrite("txs", &monero::monero_tx_set::m_txs)
        .def_property("signed_tx_hex", 
            [](const monero::monero_tx_set& self) { return self.m_signed_tx_hex.value_or(""); },
            [](monero::monero_tx_set& self, std::string val) { self.m_signed_tx_hex = val; })
        .def_property("unsigned_tx_hex", 
            [](const monero::monero_tx_set& self) { return self.m_unsigned_tx_hex.value_or(""); },
            [](monero::monero_tx_set& self, std::string val) { self.m_unsigned_tx_hex = val; })
        .def_property("multisig_tx_hex", 
            [](const monero::monero_tx_set& self) { return self.m_multisig_tx_hex.value_or(""); },
            [](monero::monero_tx_set& self, std::string val) { self.m_multisig_tx_hex = val; });

    // monero_integrated_address
    py::class_<monero::monero_integrated_address, std::shared_ptr<monero::monero_integrated_address>>(m, "MoneroIntegratedAddress")
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
    py::class_<monero::monero_tx_config, std::shared_ptr<monero::monero_tx_config>>(m, "MoneroTxConfig")
        .def(py::init<>())
        .def_property("address", 
            [](const monero::monero_tx_config& self) { return self.m_address.value_or(""); },
            [](monero::monero_tx_config& self, std::string val) { self.m_address = val; })
        .def_property("amount", 
            [](const monero::monero_tx_config& self) { return self.m_amount.value_or(0); },
            [](monero::monero_tx_config& self, uint64_t val) { self.m_amount = val; })
        .def_readwrite("destinations", &monero::monero_tx_config::m_destinations)
        .def_readwrite("subtract_fee_from", &monero::monero_tx_config::m_subtract_fee_from)
        .def_property("payment_id", 
            [](const monero::monero_tx_config& self) { return self.m_payment_id.value_or(""); },
            [](monero::monero_tx_config& self, std::string val) { self.m_payment_id = val; })
        .def_property("priority", 
            [](const monero::monero_tx_config& self) { return self.m_priority.value_or(monero_tx_priority::NORMAL); },
            [](monero::monero_tx_config& self, monero::monero_tx_priority val) { self.m_priority = val; })
        .def_property("ring_size", 
            [](const monero::monero_tx_config& self) { return self.m_ring_size.value_or(0); },
            [](monero::monero_tx_config& self, uint32_t val) { self.m_ring_size = val; })
        .def_property("fee", 
            [](const monero::monero_tx_config& self) { return self.m_fee.value_or(0); },
            [](monero::monero_tx_config& self, uint64_t val) { self.m_fee = val; })
        .def_property("account_index", 
            [](const monero::monero_tx_config& self) { return self.m_account_index.value_or(0); },
            [](monero::monero_tx_config& self, uint32_t val) { self.m_account_index = val; })
        .def_readwrite("subaddress_indices", &monero::monero_tx_config::m_subaddress_indices)
        .def_property("can_split", 
            [](const monero::monero_tx_config& self) { return self.m_can_split.value_or(false); },
            [](monero::monero_tx_config& self, bool val) { self.m_can_split = val; })
        .def_property("relay", 
            [](const monero::monero_tx_config& self) { return self.m_relay.value_or(false); },
            [](monero::monero_tx_config& self, bool val) { self.m_relay = val; })
        .def_property("note", 
            [](const monero::monero_tx_config& self) { return self.m_note.value_or(""); },
            [](monero::monero_tx_config& self, std::string val) { self.m_note = val; })
        .def_property("recipient_name", 
            [](const monero::monero_tx_config& self) { return self.m_recipient_name.value_or(""); },
            [](monero::monero_tx_config& self, std::string val) { self.m_recipient_name = val; })
        .def_property("below_amount", 
            [](const monero::monero_tx_config& self) { return self.m_below_amount.value_or(0); },
            [](monero::monero_tx_config& self, uint64_t val) { self.m_below_amount = val; })
        .def_property("sweep_each_subaddress", 
            [](const monero::monero_tx_config& self) { return self.m_sweep_each_subaddress.value_or(false); },
            [](monero::monero_tx_config& self, bool val) { self.m_sweep_each_subaddress = val; })
        .def_property("key_image", 
            [](const monero::monero_tx_config& self) { return self.m_key_image.value_or(""); },
            [](monero::monero_tx_config& self, std::string val) { self.m_key_image = val; });

    // monero_key_image_import_result
    py::class_<monero::monero_key_image_import_result, std::shared_ptr<monero::monero_key_image_import_result>>(m, "MoneroKeyImageImportResult")
        .def(py::init<>())
        .def_property("height", 
            [](const monero::monero_key_image_import_result& self) { return self.m_height.value_or(NULL); },
            [](monero::monero_key_image_import_result& self, uint64_t val) { self.m_height = val; })
        .def_property("spent_amount", 
            [](const monero::monero_key_image_import_result& self) { return self.m_spent_amount.value_or(NULL); },
            [](monero::monero_key_image_import_result& self, uint64_t val) { self.m_spent_amount = val; })
        .def_property("unspent_amount", 
            [](const monero::monero_key_image_import_result& self) { return self.m_unspent_amount.value_or(NULL); },
            [](monero::monero_key_image_import_result& self, uint64_t val) { self.m_unspent_amount = val; });

    // enum monero_message_signature_type
    py::enum_<monero::monero_message_signature_type>(m, "MoneroMessageSignatureType")
        .value("SIGN_WITH_SPEND_KEY", monero::monero_message_signature_type::SIGN_WITH_SPEND_KEY)
        .value("SIGN_WITH_VIEW_KEY", monero::monero_message_signature_type::SIGN_WITH_VIEW_KEY);

    // monero_message_signature_result
    py::class_<monero::monero_message_signature_result, std::shared_ptr<monero::monero_message_signature_result>>(m, "MoneroMessageSignatureResult")
        .def(py::init<>())
        .def_readwrite("is_good", &monero::monero_message_signature_result::m_is_good)
        .def_readwrite("version", &monero::monero_message_signature_result::m_version)
        .def_readwrite("is_old", &monero::monero_message_signature_result::m_is_old)
        .def_readwrite("signature_type", &monero::monero_message_signature_result::m_signature_type);

    // monero_check
    py::class_<monero::monero_check, std::shared_ptr<monero::monero_check>>(m, "MoneroCheck")
        .def(py::init<>())
        .def_readwrite("is_good", &monero::monero_check::m_is_good);
    
    // monero_check_tx
    py::class_<monero::monero_check_tx, monero::monero_check, std::shared_ptr<monero::monero_check_tx>>(m, "MoneroCheckTx")
        .def(py::init<>())
        .def_readwrite("is_good", &monero::monero_check_tx::m_is_good)
        .def_property("in_tx_pool", 
            [](const monero::monero_check_tx& self) { return self.m_in_tx_pool.value_or(false); },
            [](monero::monero_check_tx& self, bool val) { self.m_in_tx_pool = val; })
        .def_property("num_confirmations", 
            [](const monero::monero_check_tx& self) { return self.m_num_confirmations.value_or(false); },
            [](monero::monero_check_tx& self, uint64_t val) { self.m_num_confirmations = val; })
        .def_property("received_amount", 
            [](const monero::monero_check_tx& self) { return self.m_received_amount.value_or(0); },
            [](monero::monero_check_tx& self, uint64_t val) { self.m_received_amount = val; });
    
    // monero_check_reserve
    py::class_<monero::monero_check_reserve, monero::monero_check, std::shared_ptr<monero::monero_check_reserve>>(m, "MoneroCheckReserve")
        .def(py::init<>())
        .def_readwrite("is_good", &monero::monero_check_reserve::m_is_good)
        .def_property("total_amount", 
            [](const monero::monero_check_reserve& self) { return self.m_total_amount.value_or(false); },
            [](monero::monero_check_reserve& self, uint64_t val) { self.m_total_amount = val; })
        .def_property("unconfirmed_spent_amount", 
            [](const monero::monero_check_reserve& self) { return self.m_unconfirmed_spent_amount.value_or(false); },
            [](monero::monero_check_reserve& self, uint64_t val) { self.m_unconfirmed_spent_amount = val; });
    
    // monero_multisig_info
    py::class_<monero::monero_multisig_info, std::shared_ptr<monero_multisig_info>>(m, "MoneroMultisigInfo")
        .def(py::init<>())
        .def_readwrite("is_multisig", &monero::monero_multisig_info::m_is_multisig)
        .def_readwrite("is_ready", &monero::monero_multisig_info::m_is_ready)
        .def_readwrite("threshold", &monero::monero_multisig_info::m_threshold)
        .def_readwrite("num_participants", &monero::monero_multisig_info::m_num_participants);
    
    // monero_multisig_init_result
    py::class_<monero::monero_multisig_init_result, std::shared_ptr<monero_multisig_init_result>>(m, "MoneroMultisigInitResult")
        .def(py::init<>())
        .def_property("address", 
            [](const monero::monero_multisig_init_result& self) { return self.m_address.value_or(""); },
            [](monero::monero_multisig_init_result& self, std::string val) { self.m_address = val; })
        .def_property("multisig_hex", 
            [](const monero::monero_multisig_init_result& self) { return self.m_multisig_hex.value_or(""); },
            [](monero::monero_multisig_init_result& self, std::string val) { self.m_multisig_hex = val; });
        
    // monero_multisig_sign_result
    py::class_<monero::monero_multisig_sign_result, std::shared_ptr<monero::monero_multisig_sign_result>>(m, "MoneroMultisigSignResult")
        .def(py::init<>())
        .def_property("signed_multisig_tx_hex", 
            [](const monero::monero_multisig_sign_result& self) { return self.m_signed_multisig_tx_hex.value_or(""); },
            [](monero::monero_multisig_sign_result& self, std::string val) { self.m_signed_multisig_tx_hex = val; })
        .def_readwrite("tx_hashes", &monero::monero_multisig_sign_result::m_tx_hashes);

    // monero_address_book_entry
    py::class_<monero::monero_address_book_entry, std::shared_ptr<monero::monero_address_book_entry>>(m, "MoneroAddressBookEntry")
        .def(py::init<>())
        .def_property("index", 
            [](const monero::monero_address_book_entry& self) { return self.m_index.value_or(NULL); },
            [](monero::monero_address_book_entry& self, uint64_t val) { self.m_index = val; })
        .def_property("address", 
            [](const monero::monero_address_book_entry& self) { return self.m_address.value_or(""); },
            [](monero::monero_address_book_entry& self, std::string val) { self.m_address = val; })
        .def_property("description", 
            [](const monero::monero_address_book_entry& self) { return self.m_description.value_or(""); },
            [](monero::monero_address_book_entry& self, std::string val) { self.m_description = val; })
        .def_property("payment_id", 
            [](const monero::monero_address_book_entry& self) { return self.m_payment_id.value_or(""); },
            [](monero::monero_address_book_entry& self, std::string val) { self.m_payment_id = val; });
    
    // monero_wallet_listener
    py::class_<monero::monero_wallet_listener, std::shared_ptr<monero::monero_wallet_listener>>(m, "MoneroWalletListener")
        .def("on_sync_progress", [](monero::monero_wallet_listener& self, uint64_t height, uint64_t start_height, uint64_t end_height, double percent_done, const std::string& message) {
            MONERO_CATCH_AND_RETHROW(self.on_sync_progress(height, start_height, end_height, percent_done, message));
        }, py::arg("height"), py::arg("start_height"), py::arg("end_height"), py::arg("percent_done"), py::arg("message"))
        .def("on_new_block", [](monero::monero_wallet_listener& self, uint64_t height) {
            MONERO_CATCH_AND_RETHROW(self.on_new_block(height));
        }, py::arg("height"))
        .def("on_balances_changed", [](monero::monero_wallet_listener& self, uint64_t new_balance, uint64_t new_unlocked_balance) {
            MONERO_CATCH_AND_RETHROW(self.on_balances_changed(new_balance, new_unlocked_balance));
        }, py::arg("new_balance"), py::arg("new_unclocked_balance"))
        .def("on_output_received", [](monero::monero_wallet_listener& self, const monero_output_wallet& output) {
            MONERO_CATCH_AND_RETHROW(self.on_output_received(output));
        }, py::arg("output"))
        .def("on_output_spent", [](monero::monero_wallet_listener& self, const monero_output_wallet& output) {
            MONERO_CATCH_AND_RETHROW(self.on_output_spent(output));
        }, py::arg("output"));

    // monero_wallet
    py::class_<monero::monero_wallet, PyMoneroWallet, std::shared_ptr<monero::monero_wallet>>(m, "MoneroWallet")
        .def("is_view_only", [](monero::monero_wallet& self) {
            MONERO_CATCH_AND_RETHROW(self.is_view_only());
        })
        .def("set_daemon_connection", [](monero::monero_wallet& self, const monero::monero_rpc_connection& connection) {
            MONERO_CATCH_AND_RETHROW(self.set_daemon_connection(connection));
        }, py::arg("connection"))
       .def("set_daemon_connection", [](monero::monero_wallet& self, std::string uri, std::string username, std::string password) {
            MONERO_CATCH_AND_RETHROW(self.set_daemon_connection(uri, username, password));
        }, py::arg("uri") = "", py::arg("username") = "", py::arg("password") = "")       
        .def("set_daemon_proxy", [](monero::monero_wallet& self, const std::string& uri) {
            MONERO_CATCH_AND_RETHROW(self.set_daemon_proxy(uri));
        }, py::arg("uri") = "")
        .def("get_daemon_connection", [](monero::monero_wallet& self) {
            MONERO_CATCH_AND_RETHROW(self.get_daemon_connection().value_or(monero::monero_rpc_connection()));
        })
        .def("is_connected_to_daemon", [](monero::monero_wallet& self) {
            MONERO_CATCH_AND_RETHROW(self.is_connected_to_daemon());
        })
        .def("is_daemon_trusted", [](monero::monero_wallet& self) {
            MONERO_CATCH_AND_RETHROW(self.is_daemon_trusted());
        })
        .def("is_synced", [](monero::monero_wallet& self) {
            MONERO_CATCH_AND_RETHROW(self.is_synced());
        })
        .def("get_version", [](monero::monero_wallet& self) {
            MONERO_CATCH_AND_RETHROW(self.get_version());
        })
        .def("get_path", [](monero::monero_wallet& self) {
            MONERO_CATCH_AND_RETHROW(self.get_path());
        })
        .def("get_network_type", [](monero::monero_wallet& self) {
            MONERO_CATCH_AND_RETHROW(self.get_network_type());
        })
        .def("get_seed", [](monero::monero_wallet& self) {
            MONERO_CATCH_AND_RETHROW(self.get_seed());
        })
        .def("get_seed_language", [](monero::monero_wallet& self) {
            MONERO_CATCH_AND_RETHROW(self.get_seed_language());
        })
        .def("get_public_view_key", [](monero::monero_wallet& self) {
            MONERO_CATCH_AND_RETHROW(self.get_public_view_key());
        })
        .def("get_private_view_key", [](monero::monero_wallet& self) {
            MONERO_CATCH_AND_RETHROW(self.get_private_view_key());
        })
        .def("get_public_spend_key", [](monero::monero_wallet& self) {
            MONERO_CATCH_AND_RETHROW(self.get_public_spend_key());
        })
        .def("get_private_spend_key", [](monero::monero_wallet& self) {
            MONERO_CATCH_AND_RETHROW(self.get_private_spend_key());
        })
        .def("get_primary_address", [](monero::monero_wallet& self) {
            MONERO_CATCH_AND_RETHROW(self.get_primary_address());
        })
        .def("get_address", [](monero::monero_wallet& self, uint32_t account_idx, uint32_t subaddress_idx) {
            MONERO_CATCH_AND_RETHROW(self.get_address(account_idx, subaddress_idx));
        }, py::arg("account_idx"), py::arg("subaddress_idx"))
        .def("get_address_index", [](monero::monero_wallet& self, const std::string& address) {
            MONERO_CATCH_AND_RETHROW(self.get_address_index(address));
        }, py::arg("address"))
        .def("get_integrated_address", [](monero::monero_wallet& self, const std::string& standard_address, const std::string& payment_id) {
            MONERO_CATCH_AND_RETHROW(self.get_integrated_address(standard_address, payment_id));
        }, py::arg("standard_address") = "", py::arg("payment_id") = "")
        .def("decode_integrated_address", [](monero::monero_wallet& self, const std::string& integrated_address) {
            MONERO_CATCH_AND_RETHROW(self.decode_integrated_address(integrated_address));
        }, py::arg("integrated_address"))
        .def("get_height", [](monero::monero_wallet& self) {
            MONERO_CATCH_AND_RETHROW(self.get_height());
        })
        .def("get_restore_height", [](monero::monero_wallet& self) {
            MONERO_CATCH_AND_RETHROW(self.get_restore_height());
        })
        .def("set_restore_height", [](monero::monero_wallet& self, uint64_t restore_height) {
            MONERO_CATCH_AND_RETHROW(self.set_restore_height(restore_height));
        }, py::arg("restore_height"))
        .def("get_daemon_height", [](monero::monero_wallet& self) {
            MONERO_CATCH_AND_RETHROW(self.get_daemon_height());
        })
        .def("get_daemon_max_peer_height", [](monero::monero_wallet& self) {
            MONERO_CATCH_AND_RETHROW(self.get_daemon_max_peer_height());
        })
        .def("get_height_by_date", [](monero::monero_wallet& self, uint16_t year, uint8_t month, uint8_t day) {
            MONERO_CATCH_AND_RETHROW(self.get_height_by_date(year, month, day));
        }, py::arg("year"), py::arg("month"), py::arg("day"))
        .def("add_listener", [](monero::monero_wallet& self, monero::monero_wallet_listener& listener) {
            MONERO_CATCH_AND_RETHROW(self.add_listener(listener));
        }, py::arg("listener"))
        .def("remove_listener", [](monero::monero_wallet& self, monero::monero_wallet_listener& listener) {
            MONERO_CATCH_AND_RETHROW(self.remove_listener(listener));
        }, py::arg("listener"))
        .def("get_listeners", [](monero::monero_wallet& self) {
            try {
                std::set<monero::monero_wallet_listener*> listeners = self.get_listeners();
                std::vector<std::shared_ptr<monero::monero_wallet_listener>> result(listeners.size());
                //std::copy(listeners.begin() ,listeners.end(), result.begin());

                for(auto listener : listeners) {
                    result.emplace_back(listener);
                }

                return result;
            }
            catch (const std::exception& e) {
                throw py::value_error(e.what());
            }
        })
        .def("sync", [](monero::monero_wallet& self) {
            MONERO_CATCH_AND_RETHROW(self.sync());
        })
        .def("sync", [](monero::monero_wallet& self, monero::monero_wallet_listener& listener) {
            MONERO_CATCH_AND_RETHROW(self.sync(listener));
        }, py::arg("listener"))
        .def("sync", [](monero::monero_wallet& self, uint64_t start_height) {
            MONERO_CATCH_AND_RETHROW(self.sync(start_height));
        }, py::arg("start_height"))
        .def("sync", [](monero::monero_wallet& self, uint64_t start_height, monero::monero_wallet_listener& listener) {
            MONERO_CATCH_AND_RETHROW(self.sync(start_height, listener));
        }, py::arg("start_height"), py::arg("listener"))
        .def("start_syncing", [](monero::monero_wallet& self, uint64_t sync_period_in_ms) {
            MONERO_CATCH_AND_RETHROW(self.start_syncing(sync_period_in_ms));
        }, py::arg("sync_period_in_ms") = 10000)
        .def("stop_syncing", [](monero::monero_wallet& self) {
            MONERO_CATCH_AND_RETHROW(self.stop_syncing());
        })
        .def("scan_txs", [](monero::monero_wallet& self, const std::vector<std::string>& tx_hashes) {
            MONERO_CATCH_AND_RETHROW(self.scan_txs(tx_hashes));
        }, py::arg("tx_hashes"))
        .def("rescan_spent", [](monero::monero_wallet& self) {
            MONERO_CATCH_AND_RETHROW(self.rescan_spent());
        })
        .def("rescan_blockchain", [](monero::monero_wallet& self) {
            MONERO_CATCH_AND_RETHROW(self.rescan_blockchain());
        })
        .def("get_balance", [](monero::monero_wallet& self) {
            MONERO_CATCH_AND_RETHROW(self.get_balance());
        })
        .def("get_balance", [](monero::monero_wallet& self, uint32_t account_idx) {
            MONERO_CATCH_AND_RETHROW(self.get_balance(account_idx));
        }, py::arg("account_idx"))
        .def("get_balance", [](monero::monero_wallet& self, uint32_t account_idx, uint32_t subaddress_idx) {
            MONERO_CATCH_AND_RETHROW(self.get_balance(account_idx, subaddress_idx));
        }, py::arg("account_idx"), py::arg("subaddress_idx"))
        .def("get_unlocked_balance", [](monero::monero_wallet& self) {
            MONERO_CATCH_AND_RETHROW(self.get_unlocked_balance());
        })
        .def("get_unlocked_balance", [](monero::monero_wallet& self, uint32_t account_idx) {
            MONERO_CATCH_AND_RETHROW(self.get_unlocked_balance(account_idx));
        }, py::arg("account_idx"))
        .def("get_unlocked_balance", [](monero::monero_wallet& self, uint32_t account_idx, uint32_t subaddress_idx) {
            MONERO_CATCH_AND_RETHROW(self.get_unlocked_balance(account_idx, subaddress_idx));
        }, py::arg("account_idx"), py::arg("subaddress_idx"))
        .def("get_accounts", [](monero::monero_wallet& self) {
            MONERO_CATCH_AND_RETHROW(self.get_accounts());
        })
        .def("get_accounts", [](monero::monero_wallet& self, bool include_subaddresses) {
            MONERO_CATCH_AND_RETHROW(self.get_accounts(include_subaddresses));
        }, py::arg("include_subaddresses"))
        .def("get_accounts", [](monero::monero_wallet& self, const std::string& tag) {
            MONERO_CATCH_AND_RETHROW(self.get_accounts(tag));
        }, py::arg("tag"))
        .def("get_accounts", [](monero::monero_wallet& self, bool include_subaddresses, const std::string& tag) {
            MONERO_CATCH_AND_RETHROW(self.get_accounts(include_subaddresses, tag));
        }, py::arg("include_subaddresses"), py::arg("tag"))
        .def("get_account", [](monero::monero_wallet& self, uint32_t account_idx) {
            MONERO_CATCH_AND_RETHROW(self.get_account(account_idx));
        }, py::arg("account_idx"))
        .def("get_account", [](monero::monero_wallet& self, uint32_t account_idx, bool include_subaddresses) {
            MONERO_CATCH_AND_RETHROW(self.get_account(account_idx, include_subaddresses));
        }, py::arg("account_idx"), py::arg("include_subaddresses"))
        .def("create_account", [](monero::monero_wallet& self, const std::string& label) {
            MONERO_CATCH_AND_RETHROW(self.create_account(label));
        }, py::arg("label") = "")
        .def("get_subaddresses", [](monero::monero_wallet& self, uint32_t account_idx) {
            MONERO_CATCH_AND_RETHROW(self.get_subaddresses(account_idx));
        }, py::arg("account_idx"))
        .def("get_subaddresses", [](monero::monero_wallet& self, uint32_t account_idx, const std::vector<uint32_t>& subaddress_indices) {
            MONERO_CATCH_AND_RETHROW(self.get_subaddresses(account_idx, subaddress_indices));
        }, py::arg("account_idx"), py::arg("subaddress_indices"))
        .def("create_subaddress", [](monero::monero_wallet& self, uint32_t account_idx, const std::string& label) {
            MONERO_CATCH_AND_RETHROW(self.create_subaddress(account_idx, label));
        }, py::arg("account_idx"), py::arg("label") = "")
        .def("set_subaddress_label", [](monero::monero_wallet& self, uint32_t account_idx, uint32_t subaddress_idx, const std::string& label) {
            MONERO_CATCH_AND_RETHROW(self.set_subaddress_label(account_idx, subaddress_idx, label));
        }, py::arg("account_idx"), py::arg("subaddress_idx"), py::arg("label") = "")
        .def("get_txs", [](monero::monero_wallet& self) {
            MONERO_CATCH_AND_RETHROW(self.get_txs());
        })
        .def("get_txs", [](monero::monero_wallet& self, const monero::monero_tx_query& query) {
            MONERO_CATCH_AND_RETHROW(self.get_txs(query));
        }, py::arg("query"))
        .def("get_transfers", [](monero::monero_wallet& self, const monero::monero_transfer_query& query) {
            MONERO_CATCH_AND_RETHROW(self.get_transfers(query));
        }, py::arg("query"))
        .def("get_outputs", [](monero::monero_wallet& self, const monero::monero_output_query& query) {
            MONERO_CATCH_AND_RETHROW(self.get_outputs(query));
        }, py::arg("query"))
        .def("export_outputs", [](monero::monero_wallet& self, bool all) {
            MONERO_CATCH_AND_RETHROW(self.export_outputs(all));
        }, py::arg("all") = false)
        .def("import_outputs", [](monero::monero_wallet& self, const std::string& outputs_hex) {
            MONERO_CATCH_AND_RETHROW(self.import_outputs(outputs_hex));
        }, py::arg("outputs_hex"))
        .def("export_key_images", [](monero::monero_wallet& self, bool all) {
            MONERO_CATCH_AND_RETHROW(self.export_key_images(all));
        }, py::arg("all") = false)
        .def("import_key_images", [](monero::monero_wallet& self, const std::vector<std::shared_ptr<monero_key_image>>& key_images) {
            MONERO_CATCH_AND_RETHROW(self.import_key_images(key_images));
        }, py::arg("key_images"))
        .def("freeze_output", [](monero::monero_wallet& self, const std::string& key_image) {
            MONERO_CATCH_AND_RETHROW(self.freeze_output(key_image));
        }, py::arg("key_image"))
        .def("thaw_output", [](monero::monero_wallet& self, const std::string& key_image) {
            MONERO_CATCH_AND_RETHROW(self.thaw_output(key_image));
        }, py::arg("key_image"))
        .def("is_output_frozen", [](monero::monero_wallet& self, const std::string& key_image) {
            MONERO_CATCH_AND_RETHROW(self.is_output_frozen(key_image));
        }, py::arg("key_image"))
        .def("get_default_fee_priority", [](monero::monero_wallet& self) {
            MONERO_CATCH_AND_RETHROW(self.get_default_fee_priority());
        })
        .def("create_tx", [](monero::monero_wallet& self, const monero::monero_tx_config& config) {
            MONERO_CATCH_AND_RETHROW(self.create_tx(config));
        }, py::arg("config"))
        .def("create_txs", [](monero::monero_wallet& self, const monero::monero_tx_config& config) {
            MONERO_CATCH_AND_RETHROW(self.create_txs(config));
        }, py::arg("config"))
        .def("sweep_unlocked", [](monero::monero_wallet& self, const monero::monero_tx_config& config) {
            MONERO_CATCH_AND_RETHROW(self.sweep_unlocked(config));
        }, py::arg("config"))
        .def("sweep_output", [](monero::monero_wallet& self, const monero::monero_tx_config& config) {
            MONERO_CATCH_AND_RETHROW(self.sweep_output(config));
        }, py::arg("config"))
        .def("sweep_dust", [](monero::monero_wallet& self, bool relay) {
            MONERO_CATCH_AND_RETHROW(self.sweep_dust(relay));
        }, py::arg("relay") = false)
        .def("relay_tx", [](monero::monero_wallet& self, const std::string& tx_metadata) {
            MONERO_CATCH_AND_RETHROW(self.relay_tx(tx_metadata));
        }, py::arg("tx_metadata"))
        .def("relay_tx", [](monero::monero_wallet& self, const monero::monero_tx_wallet& tx) {
            MONERO_CATCH_AND_RETHROW(self.relay_tx(tx));
        }, py::arg("tx"))
        .def("relay_txs", [](monero::monero_wallet& self, const std::vector<std::shared_ptr<monero_tx_wallet>>& txs) {
            MONERO_CATCH_AND_RETHROW(self.relay_txs(txs));
        }, py::arg("txs"))
        .def("relay_txs", [](monero::monero_wallet& self, const std::vector<std::string>& tx_metadatas) {
            MONERO_CATCH_AND_RETHROW(self.relay_txs(tx_metadatas));
        }, py::arg("tx_metadatas"))
        .def("describe_tx_set", [](monero::monero_wallet& self, const monero::monero_tx_set& tx_set) {
            MONERO_CATCH_AND_RETHROW(self.describe_tx_set(tx_set));
        }, py::arg("tx_set"))
        .def("sign_txs", [](monero::monero_wallet& self, const std::string& unsigned_tx_hex) {
            MONERO_CATCH_AND_RETHROW(self.sign_txs(unsigned_tx_hex));
        }, py::arg("unsigned_tx_hex"))
        .def("submit_txs", [](monero::monero_wallet& self, const std::string& signed_tx_hex) {
            MONERO_CATCH_AND_RETHROW(self.submit_txs(signed_tx_hex));
        }, py::arg("signed_tx_hex"))
        .def("sign_message", [](monero::monero_wallet& self, const std::string& msg, monero_message_signature_type signature_type, uint32_t account_idx, uint32_t subaddress_idx) {
            MONERO_CATCH_AND_RETHROW(self.sign_message(msg, signature_type, account_idx, subaddress_idx));
        }, py::arg("msg"), py::arg("signature_type"), py::arg("account_idx") = 0, py::arg("subaddress_idx") = 0)
        .def("verify_message", [](monero::monero_wallet& self, const std::string& msg, const std::string& address, const std::string& signature) {
            MONERO_CATCH_AND_RETHROW(self.verify_message(msg, address, signature));
        }, py::arg("msg"), py::arg("address"), py::arg("signature"))

        .def("get_tx_key", [](monero::monero_wallet& self, const std::string& tx_hash) {
            MONERO_CATCH_AND_RETHROW(self.get_tx_key(tx_hash));
        }, py::arg("tx_hash"))
        .def("check_tx_key", [](monero::monero_wallet& self, const std::string& tx_hash, const std::string& tx_key, const std::string& address) {
            MONERO_CATCH_AND_RETHROW(self.check_tx_key(tx_hash, tx_key, address));
        }, py::arg("tx_hash"), py::arg("tx_key"), py::arg("address"))
        .def("get_tx_proof", [](monero::monero_wallet& self, const std::string& tx_hash, const std::string& address, const std::string& message) {
            MONERO_CATCH_AND_RETHROW(self.get_tx_proof(tx_hash, address, message));
        }, py::arg("tx_hash"), py::arg("address"), py::arg("message"))
        .def("check_tx_proof", [](monero::monero_wallet& self, const std::string& tx_hash, const std::string& address, const std::string& message, const std::string& signature) {
            MONERO_CATCH_AND_RETHROW(self.check_tx_proof(tx_hash, address, message, signature));
        }, py::arg("tx_hash"), py::arg("address"), py::arg("message"), py::arg("signature"))
        .def("get_spend_proof", [](monero::monero_wallet& self, const std::string& tx_hash, const std::string& message) {
            MONERO_CATCH_AND_RETHROW(self.get_spend_proof(tx_hash, message));
        }, py::arg("tx_hash"), py::arg("message"))
        .def("check_spend_proof", [](monero::monero_wallet& self, const std::string& tx_hash, const std::string& message, const std::string& signature) {
            MONERO_CATCH_AND_RETHROW(self.check_spend_proof(tx_hash, message, signature));
        }, py::arg("tx_hash"), py::arg("message"), py::arg("signature"))
        .def("get_reserve_proof_wallet", [](monero::monero_wallet& self, const std::string& message) {
            MONERO_CATCH_AND_RETHROW(self.get_reserve_proof_wallet(message));
        }, py::arg("message"))
        .def("get_reserve_proof_account", [](monero::monero_wallet& self, uint32_t account_idx, uint64_t amount, const std::string& message) {
            MONERO_CATCH_AND_RETHROW(self.get_reserve_proof_account(account_idx, amount, message));
        }, py::arg("account_idx"), py::arg("amount"), py::arg("message"))
        .def("check_reserve_proof", [](monero::monero_wallet& self, const std::string& address, const std::string& message, const std::string& signature) {
            MONERO_CATCH_AND_RETHROW(self.check_reserve_proof(address, message, signature));
        }, py::arg("address"), py::arg("message"), py::arg("signature"))
        .def("get_tx_note", [](monero::monero_wallet& self, const std::string& tx_hash) {
            MONERO_CATCH_AND_RETHROW(self.get_tx_note(tx_hash));
        }, py::arg("tx_hash"))
        .def("get_tx_notes", [](monero::monero_wallet& self, const std::vector<std::string>& tx_hashes) {
            MONERO_CATCH_AND_RETHROW(self.get_tx_notes(tx_hashes));
        }, py::arg("tx_hashes"))
        .def("set_tx_note", [](monero::monero_wallet& self, const std::string& tx_hash, const std::string& note) {
            MONERO_CATCH_AND_RETHROW(self.set_tx_note(tx_hash, note));
        }, py::arg("tx_hash"), py::arg("note"))
        .def("set_tx_notes", [](monero::monero_wallet& self, const std::vector<std::string>& tx_hashes, const std::vector<std::string>& notes) {
            MONERO_CATCH_AND_RETHROW(self.set_tx_notes(tx_hashes, notes));
        }, py::arg("tx_hashes"), py::arg("notes"))


        .def("get_address_book_entries", [](monero::monero_wallet& self, const std::vector<uint64_t>& indices) {
            MONERO_CATCH_AND_RETHROW(self.get_address_book_entries(indices));
        }, py::arg("indices"))
        .def("add_address_book_entry", [](monero::monero_wallet& self, const std::string& address, const std::string& description) {
            MONERO_CATCH_AND_RETHROW(self.add_address_book_entry(address, description));
        }, py::arg("address"), py::arg("description"))
        .def("edit_address_book_entry", [](monero::monero_wallet& self, uint64_t index, bool set_address, const std::string& address, bool set_description, const std::string& description) {
            MONERO_CATCH_AND_RETHROW(self.edit_address_book_entry(index, set_address, address, set_description, description));
        }, py::arg("index"), py::arg("set_address"), py::arg("address"), py::arg("set_description"), py::arg("description"))
        .def("delete_address_book_entry", [](monero::monero_wallet& self, uint64_t index) {
            MONERO_CATCH_AND_RETHROW(self.delete_address_book_entry(index));
        }, py::arg("index"))
        .def("get_payment_uri", [](monero::monero_wallet& self, const monero::monero_tx_config& config) {
            MONERO_CATCH_AND_RETHROW(self.get_payment_uri(config));
        }, py::arg("config"))
        .def("parse_payment_uri", [](monero::monero_wallet& self, const std::string& uri) {
            MONERO_CATCH_AND_RETHROW(self.parse_payment_uri(uri));
        }, py::arg("uri"))        
        .def("get_attribute", [](monero::monero_wallet& self, const std::string& key, std::string& val) {
            MONERO_CATCH_AND_RETHROW(self.get_attribute(key, val));
        }, py::arg("key"), py::arg("val"))
        .def("set_attribute", [](monero::monero_wallet& self, const std::string& key, const std::string& val) {
            MONERO_CATCH_AND_RETHROW(self.set_attribute(key, val));
        }, py::arg("key"), py::arg("val"))
        .def("stop_mining", [](monero::monero_wallet& self) {
            MONERO_CATCH_AND_RETHROW(self.stop_mining());
        }) 
        .def("wait_for_next_block", [](monero::monero_wallet& self) {
            MONERO_CATCH_AND_RETHROW(self.wait_for_next_block());
        }) 
        .def("is_multisig_import_needed", [](monero::monero_wallet& self) {
            MONERO_CATCH_AND_RETHROW(self.is_multisig_import_needed());
        })  
        .def("is_multisig", [](monero::monero_wallet& self) {
            MONERO_CATCH_AND_RETHROW(self.is_multisig());
        })  
        .def("get_multisig_info", [](monero::monero_wallet& self) {
            MONERO_CATCH_AND_RETHROW(self.get_multisig_info());
        })   
        .def("prepare_multisig", [](monero::monero_wallet& self) {
            MONERO_CATCH_AND_RETHROW(self.prepare_multisig());
        })        
        .def("make_multisig", [](monero::monero_wallet& self, const std::vector<std::string>& mutisig_hexes, int threshold, const std::string& password) {
            MONERO_CATCH_AND_RETHROW(self.make_multisig(mutisig_hexes, threshold, password));
        }, py::arg("mutisig_hexes"), py::arg("threshold"), py::arg("password"))
        .def("exchange_multisig_keys", [](monero::monero_wallet& self, const std::vector<std::string>& mutisig_hexes, const std::string& password) {
            MONERO_CATCH_AND_RETHROW(self.exchange_multisig_keys(mutisig_hexes, password));
        }, py::arg("mutisig_hexes"), py::arg("password"))
        .def("export_multisig_hex", [](monero::monero_wallet& self) {
            MONERO_CATCH_AND_RETHROW(self.export_multisig_hex());
        })
        .def("import_multisig_hex", [](monero::monero_wallet& self, const std::vector<std::string>& multisig_hexes) {
            MONERO_CATCH_AND_RETHROW(self.import_multisig_hex(multisig_hexes));
        }, py::arg("multisig_hexes"))
        .def("sign_multisig_tx_hex", [](monero::monero_wallet& self, const std::string& multisig_tx_hex) {
            MONERO_CATCH_AND_RETHROW(self.sign_multisig_tx_hex(multisig_tx_hex));
        }, py::arg("multisig_tx_hex"))
        .def("submit_multisig_tx_hex", [](monero::monero_wallet& self, const std::string& signed_multisig_tx_hex) {
            MONERO_CATCH_AND_RETHROW(self.submit_multisig_tx_hex(signed_multisig_tx_hex));
        }, py::arg("signed_multisig_tx_hex"))
        .def("change_password", [](monero::monero_wallet& self, const std::string& old_password, const std::string& new_password) {
            MONERO_CATCH_AND_RETHROW(self.change_password(old_password, new_password));
        }, py::arg("old_password"), py::arg("new_password"))
        .def("move_to", [](monero::monero_wallet& self, const std::string& path, const std::string& password) {
            MONERO_CATCH_AND_RETHROW(self.move_to(path, password));
        }, py::arg("path"), py::arg("password"))
        .def("save", [](monero::monero_wallet& self) {
            MONERO_CATCH_AND_RETHROW(self.save());
        })
        .def("close", [](monero::monero_wallet& self, bool save) {
            MONERO_CATCH_AND_RETHROW(self.close(save));
        }, py::arg("save") = false);

    // monero_wallet_keys
    py::class_<monero::monero_wallet_keys, monero::monero_wallet, std::shared_ptr<monero::monero_wallet_keys>>(m, "MoneroWalletKeys")
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
        
        .def("get_address", [](monero::monero_wallet_keys& self, uint32_t account_idx, uint32_t subaddress_idx) {
            MONERO_CATCH_AND_RETHROW(self.get_address(account_idx, subaddress_idx));
        }, py::arg("account_idx") , py::arg("subaddress_idx"))

        .def("get_integrated_address", [](monero::monero_wallet_keys& self, const std::string& standard_address, const std::string& payment_id) {
            MONERO_CATCH_AND_RETHROW(self.get_integrated_address(standard_address, payment_id));
        }, py::arg("standard_address") = "" , py::arg("payment_id") = "")

        .def("decode_integrated_address", [](monero::monero_wallet_keys& self, const std::string& integrated_address) {
            MONERO_CATCH_AND_RETHROW(self.decode_integrated_address(integrated_address));
        }, py::arg("integrated_address"))
        
        .def("get_account", [](monero::monero_wallet_keys& self, uint32_t account_idx, bool include_subaddresses) {
            MONERO_CATCH_AND_RETHROW(self.get_account(account_idx, include_subaddresses));
        }, py::arg("account_idx") , py::arg("include_subaddresses"))

        .def("get_subaddresses", [](monero::monero_wallet_keys& self, uint32_t account_idx, const std::vector<uint32_t>& subaddress_indices) {
            MONERO_CATCH_AND_RETHROW(self.get_subaddresses(account_idx, subaddress_indices));
        }, py::arg("account_idx") , py::arg("subaddress_indices"))
        
        .def("close", [](monero::monero_wallet_keys& self, bool save) {
            MONERO_CATCH_AND_RETHROW(self.close(save));
        }, py::arg("save") = false);

    // monero_wallet_full
    py::class_<monero::monero_wallet_full, monero::monero_wallet, std::shared_ptr<monero::monero_wallet_full>>(m, "MoneroWalletFull")
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

    // monero_utils
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

}
