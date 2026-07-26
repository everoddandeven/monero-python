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
#include <regex>
#include "cryptonote_basic/cryptonote_format_utils.h"
#include "py_monero_utils.h"


std::string PyMoneroUtils::json_to_binary(const std::string &json) {
  std::string bin;
  monero_utils::json_to_binary(json, bin);
  return bin;
}

std::string PyMoneroUtils::dict_to_binary(const py::dict &dictionary) {
  std::string json = PyGenUtils::serialize(dictionary);
  return json_to_binary(json);
}

py::dict PyMoneroUtils::binary_to_dict(const std::string& bin) {
  std::string json = binary_to_json(bin);
  return PyGenUtils::deserialize(json);
}

std::string PyMoneroUtils::binary_to_json(const std::string &bin) {
  std::string json;
  monero_utils::binary_to_json(bin, json);
  return json;
}

std::string PyMoneroUtils::binary_blocks_to_json(const std::string &bin) {
  std::string json;
  monero_utils::binary_blocks_to_json(bin, json);
  return json;
}

void PyMoneroUtils::sort_txs_wallet(std::vector<std::shared_ptr<monero_tx_wallet>>& txs, const std::vector<std::string>& hashes) {
  bool empty = hashes.empty();
  std::vector<std::string> tx_hashes;
  std::unordered_map<std::string, std::shared_ptr<monero_tx_wallet>> tx_map;

  for (const auto& tx : txs) {
    std::string tx_hash = tx->m_hash.get();
    tx_map.emplace(tx_hash, tx);
    if (empty) tx_hashes.push_back(tx_hash);
  }

  std::vector<std::shared_ptr<monero_tx_wallet>> sorted_txs;
  sorted_txs.reserve(hashes.size());

  const auto& v_hashes = empty ? tx_hashes : hashes;

  for (const auto& tx_hash : v_hashes) {
    auto it = tx_map.find(tx_hash);
    if (it != tx_map.end()) {
      sorted_txs.push_back(it->second);
    }
  }

  txs = std::move(sorted_txs);
}

std::vector<std::shared_ptr<monero_tx_wallet>> PyMoneroUtils::get_and_sort_txs(const monero_wallet& wallet, const monero_tx_query& tx_query) {
  auto txs = wallet.get_txs(tx_query);
  sort_txs_wallet(txs, tx_query.m_hashes);
  return txs;
}

std::vector<std::shared_ptr<monero_tx_wallet>> PyMoneroUtils::get_and_sort_txs(const monero_wallet& wallet, const std::vector<std::string>& tx_hashes) {
  monero_tx_query tx_query;
  tx_query.m_hashes = tx_hashes;
  return get_and_sort_txs(wallet, tx_query);
}
