#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include "../external/monero-cpp/src/wallet/monero_wallet_full.h"
#include "../external/monero-cpp/src/wallet/monero_wallet_keys.h"
#include "../external/monero-cpp/src/wallet/monero_wallet_model.h"

namespace py = pybind11;

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
    py::enum_<monero::monero_network_type>(m, "NetworkType")
        .value("MAINNET", monero::monero_network_type::MAINNET)
        .value("TESTNET", monero::monero_network_type::TESTNET)
        .value("STAGENET", monero::monero_network_type::STAGENET);

    // monero_wallet_config
    py::class_<monero::monero_wallet_config, std::shared_ptr<monero::monero_wallet_config>>(m, "WalletConfig")
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
        .def_property("seed", 
            [](const monero::monero_wallet_config& self) { return self.m_seed.value_or(""); },
            [](monero::monero_wallet_config& self, const std::string& val) { self.m_seed = val; })
        .def_property("language", 
            [](const monero::monero_wallet_config& self) { return self.m_language.value_or(""); },
            [](monero::monero_wallet_config& self, const std::string& val) { self.m_language = val; })
        .def_property("restore_height", 
            [](const monero::monero_wallet_config& self) { return self.m_restore_height; },
            [](monero::monero_wallet_config& self, uint64_t height) { self.m_restore_height = height; });


    // monero_wallet_keys
    py::class_<monero::monero_wallet_keys, std::shared_ptr<monero::monero_wallet_keys>>(m, "WalletKeys")
        .def_static("create_wallet_random", [](const monero::monero_wallet_config& config) {
            MONERO_CATCH_AND_RETHROW(monero::monero_wallet_keys::create_wallet_random(config));
        }, py::arg("config"))

        .def_static("create_wallet_from_seed", [](const monero::monero_wallet_config& config) {
            MONERO_CATCH_AND_RETHROW(monero::monero_wallet_keys::create_wallet_from_seed(config));
        }, py::arg("config"))

        .def_static("create_wallet_from_keys", [](const monero::monero_wallet_config& config) {
            MONERO_CATCH_AND_RETHROW(monero::monero_wallet_keys::create_wallet_from_keys(config));
        }, py::arg("config"))

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
        });

    // monero_wallet_full
    py::class_<monero::monero_wallet_full, std::shared_ptr<monero::monero_wallet_full>>(m, "WalletFull")
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

    // monero_account
    py::class_<monero::monero_account>(m, "Account")
        .def(py::init<>())
        .def_readwrite("index", &monero::monero_account::m_index)
        .def_readwrite("primary_address", &monero::monero_account::m_primary_address)
        .def_readwrite("balance", &monero::monero_account::m_balance)
        .def_readwrite("unlocked_balance", &monero::monero_account::m_unlocked_balance);

    // monero_subaddress
    py::class_<monero::monero_subaddress>(m, "Subaddress")
        .def(py::init<>())
        .def_readwrite("account_index", &monero::monero_subaddress::m_account_index)
        .def_readwrite("index", &monero::monero_subaddress::m_index)
        .def_readwrite("address", &monero::monero_subaddress::m_address)
        .def_readwrite("balance", &monero::monero_subaddress::m_balance);

    // monero_sync_result
    py::class_<monero::monero_sync_result>(m, "SyncResult")
        .def_readwrite("num_blocks_fetched", &monero::monero_sync_result::m_num_blocks_fetched)
        .def_readwrite("received_money", &monero::monero_sync_result::m_received_money);
}
