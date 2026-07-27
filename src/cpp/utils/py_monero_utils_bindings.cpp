/**
 * Copyright (c) everoddandeven
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in all
 * copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
 *
 * Parts of this file are originally copyright (c) 2025-2026 woodser
 *
 * Parts of this file are originally copyright (c) 2014-2019, The Monero Project
 *
 * Redistribution and use in source and binary forms, with or without modification, are
 * permitted provided that the following conditions are met:
 *
 * All rights reserved.
 *
 * 1. Redistributions of source code must retain the above copyright notice, this list of
 *    conditions and the following disclaimer.
 *
 * 2. Redistributions in binary form must reproduce the above copyright notice, this list
 *    of conditions and the following disclaimer in the documentation and/or other
 *    materials provided with the distribution.
 *
 * 3. Neither the name of the copyright holder nor the names of its contributors may be
 *    used to endorse or promote products derived from this software without specific
 *    prior written permission.
 *
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY
 * EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
 * MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL
 * THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
 * SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
 * PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
 * INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT,
 * STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF
 * THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
 *
 * Parts of this file are originally copyright (c) 2012-2013 The Cryptonote developers
 */
#include "py_monero_types.h"

void py_monero_bind_utils(py::module_& m, PyMoneroTypes& t) {
  // monero_utils
  t.py_monero_utils
    .def_static("get_version", []() {
      MONERO_CATCH_AND_RETHROW(PyMoneroUtils::get_version());
    })
    .def_static("get_ring_size", []() {
      return monero_utils::RING_SIZE;
    })
    .def_static("set_log_level", [](int loglevel) {
      MONERO_CATCH_AND_RETHROW(monero_utils::set_log_level(loglevel));
    }, py::arg("loglevel"))
    .def_static("set_log_categories", [](const std::string& categories) {
      MONERO_CATCH_AND_RETHROW(monero_utils::set_log_categories(categories));
    }, py::arg("categories"))
    .def_static("configure_logging", [](const std::string& path, bool console) {
      MONERO_CATCH_AND_RETHROW(monero_utils::configure_logging(path, console));
    }, py::arg("path"), py::arg("console"))
    .def_static("get_integrated_address", [](monero_network_type network_type, const std::string& standard_address, const std::string& payment_id) {
      MONERO_CATCH_AND_RETHROW(monero_utils::get_integrated_address(network_type, standard_address, payment_id));
    }, py::arg("network_type"), py::arg("standard_address"), py::arg("payment_id") = "")
    .def_static("is_valid_address", [](const std::string& address, monero_network_type network_type) {
      return monero_utils::is_valid_address(address, network_type);
    }, py::arg("address"), py::arg("network_type"))
    .def_static("is_valid_public_view_key", [](const std::string& public_view_key) {
      MONERO_CATCH_AND_RETHROW(monero_utils::is_valid_public_view_key(public_view_key));
    }, py::arg("public_view_key"))
    .def_static("is_valid_public_spend_key", [](const std::string& public_spend_key) {
      MONERO_CATCH_AND_RETHROW(monero_utils::is_valid_public_spend_key(public_spend_key));
    }, py::arg("public_spend_key"))
    .def_static("is_valid_private_view_key", [](const std::string& private_view_key) {
      return monero_utils::is_valid_private_view_key(private_view_key);
    }, py::arg("private_view_key"))
    .def_static("is_valid_private_spend_key", [](const std::string& private_spend_key) {
      MONERO_CATCH_AND_RETHROW(monero_utils::is_valid_private_spend_key(private_spend_key));
    }, py::arg("private_spend_key"))
    .def_static("is_valid_payment_id", [](const std::string& payment_id) {
      MONERO_CATCH_AND_RETHROW(monero_utils::is_valid_payment_id(payment_id));
    }, py::arg("payment_id"))
    .def_static("is_valid_mnemonic", [](const std::string& mnemonic, const std::string& language) {
      MONERO_CATCH_AND_RETHROW(monero_utils::is_valid_mnemonic(mnemonic, language));
    }, py::arg("mnemonic"), py::arg("language") = "")
    .def_static("is_valid_language", [](const std::string& language) {
      return monero_utils::is_valid_language(language);
    }, py::arg("language"))
    .def_static("validate_address", [](const std::string& address, monero_network_type network_type) {
      MONERO_CATCH_AND_RETHROW(monero_utils::validate_address(address, network_type));
    }, py::arg("address"), py::arg("network_type"))
    .def_static("validate_public_view_key", [](const std::string& public_view_key) {
      MONERO_CATCH_AND_RETHROW(monero_utils::validate_public_view_key(public_view_key));
    }, py::arg("public_view_key"))
    .def_static("validate_public_spend_key", [](const std::string& public_spend_key) {
      MONERO_CATCH_AND_RETHROW(monero_utils::validate_public_spend_key(public_spend_key));
    }, py::arg("public_spend_key"))
    .def_static("validate_private_view_key", [](const std::string& private_view_key) {
      MONERO_CATCH_AND_RETHROW(monero_utils::validate_private_view_key(private_view_key));
    }, py::arg("private_view_key"))
    .def_static("validate_private_spend_key", [](const std::string& private_spend_key) {
      MONERO_CATCH_AND_RETHROW(monero_utils::validate_private_spend_key(private_spend_key));
    }, py::arg("private_spend_key"))
    .def_static("validate_payment_id", [](const std::string& payment_id) {
      MONERO_CATCH_AND_RETHROW(monero_utils::validate_payment_id(payment_id));
    }, py::arg("payment_id"))
    .def_static("validate_mnemonic", [](const std::string& mnemonic, const std::string& language) {
      MONERO_CATCH_AND_RETHROW(monero_utils::validate_mnemonic(mnemonic, language));
    }, py::arg("mnemonic"), py::arg("language") = "")
    .def_static("get_blocks_from_txs", [](const std::vector<std::shared_ptr<monero_tx_wallet>>& txs) {
      MONERO_CATCH_AND_RETHROW(monero_utils::get_blocks_from_txs(txs));
    }, py::arg("txs"))
    .def_static("get_blocks_from_transfers", [](const std::vector<std::shared_ptr<monero_transfer>>& transfers) {
      MONERO_CATCH_AND_RETHROW(monero_utils::get_blocks_from_transfers(transfers));
    }, py::arg("transfers"))
    .def_static("get_blocks_from_outputs", [](const std::vector<std::shared_ptr<monero_output_wallet>>& outputs) {
      MONERO_CATCH_AND_RETHROW(monero_utils::get_blocks_from_outputs(outputs));
    }, py::arg("outputs"))
    .def_static("get_payment_uri", [](const monero_tx_config &config, monero_network_type network_type) {
      MONERO_CATCH_AND_RETHROW(monero_utils::get_payment_uri(config, network_type));
    }, py::arg("config"), py::arg("network_type") = monero_network_type::MAINNET)
    .def_static("xmr_to_atomic_units", [](double amount_xmr) {
      MONERO_CATCH_AND_RETHROW(monero_utils::xmr_to_atomic_units(amount_xmr));
    }, py::arg("amount_xmr"))
    .def_static("atomic_units_to_xmr", [](uint64_t amount_atomic_units) {
      MONERO_CATCH_AND_RETHROW(monero_utils::atomic_units_to_xmr(amount_atomic_units));
    }, py::arg("amount_atomic_units"))
    .def_static("json_to_binary", [](const std::string &json) {
      MONERO_CATCH_AND_RETHROW(py::bytes(PyMoneroUtils::json_to_binary(json)));
    }, py::arg("json"))
    .def_static("binary_to_json", [](const py::bytes &bin) {
      std::string b{bin};
      MONERO_CATCH_AND_RETHROW(PyMoneroUtils::binary_to_json(b));
    }, py::arg("bin"))
    .def_static("dict_to_binary", [](const py::dict &dictionary) {
      MONERO_CATCH_AND_RETHROW(py::bytes(PyMoneroUtils::dict_to_binary(dictionary)));
    }, py::arg("dictionary"))
    .def_static("binary_to_dict", [](const py::bytes &bin) {
      std::string b{bin};
      MONERO_CATCH_AND_RETHROW(PyMoneroUtils::binary_to_dict(b));
    }, py::arg("bin"))
    .def_static("binary_blocks_to_json", [](const py::bytes &bin) {
      std::string b{bin};
      MONERO_CATCH_AND_RETHROW(PyMoneroUtils::binary_blocks_to_json(b));
    }, py::arg("bin"))
    .def_static("log_debug", [](const std::string &message) {
      MDEBUG(message);
    }, py::arg("message"))
    .def_static("log_trace", [](const std::string &message) {
      MTRACE(message);
    }, py::arg("message"))
    .def_static("log_info", [](const std::string &message) {
      MINFO(message);
    }, py::arg("message"))
    .def_static("log_warning", [](const std::string &message) {
      MWARNING(message);
    }, py::arg("message"))
    .def_static("log_error", [](const std::string &message) {
      MERROR(message);
    }, py::arg("message"));

}
