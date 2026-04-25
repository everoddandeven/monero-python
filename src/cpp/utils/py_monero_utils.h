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
#pragma once

#include "common/py_monero_common.h"
#include "utils/monero_utils.h"
#include "wallet/monero_wallet.h"


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
  static std::string binary_blocks_to_json(const std::string &bin);
  static void binary_blocks_to_property_tree(const std::string &bin, boost::property_tree::ptree &node);
  static bool is_valid_language(const std::string& language);
  static std::vector<std::shared_ptr<monero_block>> get_blocks_from_txs(std::vector<std::shared_ptr<monero_tx_wallet>> txs);
  static std::vector<std::shared_ptr<monero_block>> get_blocks_from_transfers(std::vector<std::shared_ptr<monero_transfer>> transfers);
  static std::vector<std::shared_ptr<monero_block>> get_blocks_from_outputs(std::vector<std::shared_ptr<monero_output_wallet>> outputs);
  static std::string get_payment_uri(const monero_tx_config& config, monero_network_type network_type);
  static uint64_t xmr_to_atomic_units(double amount_xmr);
  static double atomic_units_to_xmr(uint64_t amount_atomic_units);

  static void sort_txs_wallet(std::vector<std::shared_ptr<monero::monero_tx_wallet>>& txs, const std::vector<std::string>& hashes);
  static std::vector<std::shared_ptr<monero::monero_tx_wallet>> get_and_sort_txs(const monero::monero_wallet& wallet, const std::vector<std::string>& tx_hashes);
  static std::vector<std::shared_ptr<monero::monero_tx_wallet>> get_and_sort_txs(const monero::monero_wallet& wallet, const monero::monero_tx_query& tx_query);

private:

  static bool is_hex_64(const std::string& value);
  static std::string make_uri(const std::string &address, const std::string &payment_id, uint64_t amount, const std::string &tx_description, const std::string &recipient_name, monero::monero_network_type network_type);
};
