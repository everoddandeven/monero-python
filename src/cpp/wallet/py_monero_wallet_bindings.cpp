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

void py_monero_bind_wallet(py::module_& m, PyMoneroTypes& t) {
  // monero_wallet_config
  t.py_monero_wallet_config
    .def(py::init<>())
    .def(py::init<const monero_wallet_config&>(), py::arg("config"), py::keep_alive<1, 2>())
    .def_static("deserialize", [](const std::string& config_json) {
      MONERO_CATCH_AND_RETHROW(monero_wallet_config::deserialize(config_json));
    }, py::arg("config_json"))
    .def_readwrite("path", &monero_wallet_config::m_path)
    .def_readwrite("password", &monero_wallet_config::m_password)
    .def_readwrite("network_type", &monero_wallet_config::m_network_type)
    .def_readwrite("server", &monero_wallet_config::m_server)
    .def_readwrite("seed", &monero_wallet_config::m_seed)
    .def_readwrite("seed_offset", &monero_wallet_config::m_seed_offset)
    .def_readwrite("primary_address", &monero_wallet_config::m_primary_address)
    .def_readwrite("private_view_key", &monero_wallet_config::m_private_view_key)
    .def_readwrite("private_spend_key", &monero_wallet_config::m_private_spend_key)
    .def_readwrite("save_current", &monero_wallet_config::m_save_current)
    .def_readwrite("language", &monero_wallet_config::m_language)
    .def_readwrite("restore_height", &monero_wallet_config::m_restore_height)
    .def_readwrite("account_lookahead", &monero_wallet_config::m_account_lookahead)
    .def_readwrite("subaddress_lookahead", &monero_wallet_config::m_subaddress_lookahead)
    .def_readwrite("is_multisig", &monero_wallet_config::m_is_multisig)
    .def_readwrite("regtest", &monero_wallet_config::m_regtest)
    .def("copy", [](monero_wallet_config& self) {
      MONERO_CATCH_AND_RETHROW(self.copy());
    });

  // monero_subaddress
  t.py_monero_subaddress
    .def(py::init<>())
    .def_readwrite("account_index", &monero_subaddress::m_account_index)
    .def_readwrite("index", &monero_subaddress::m_index)
    .def_readwrite("address", &monero_subaddress::m_address)
    .def_readwrite("label", &monero_subaddress::m_label)
    .def_readwrite("balance", &monero_subaddress::m_balance)
    .def_readwrite("unlocked_balance", &monero_subaddress::m_unlocked_balance)
    .def_readwrite("num_unspent_outputs", &monero_subaddress::m_num_unspent_outputs)
    .def_readwrite("is_used", &monero_subaddress::m_is_used)
    .def_readwrite("num_blocks_to_unlock", &monero_subaddress::m_num_blocks_to_unlock);

  // monero_sync_result
  t.py_monero_sync_result
    .def(py::init<>())
    .def(py::init<const uint16_t, const bool>(), py::arg("num_blocks_fetched"), py::arg("received_money"))
    .def_readwrite("num_blocks_fetched", &monero_sync_result::m_num_blocks_fetched)
    .def_readwrite("received_money", &monero_sync_result::m_received_money);

  // monero_account
  t.py_monero_account
    .def(py::init<>())
    .def_readwrite("index", &monero_account::m_index)
    .def_readwrite("primary_address", &monero_account::m_primary_address)
    .def_readwrite("balance", &monero_account::m_balance)
    .def_readwrite("unlocked_balance", &monero_account::m_unlocked_balance)
    .def_readwrite("tag", &monero_account::m_tag)
    .def_readwrite("subaddresses", &monero_account::m_subaddresses);

  // monero_account_tag
  t.py_monero_account_tag
    .def(py::init<>())
    .def(py::init<std::string&, std::string&>(), py::arg("tag"), py::arg("label"))
    .def(py::init<std::string&, std::string&, std::vector<uint32_t>>(), py::arg("tag"), py::arg("label"), py::arg("account_indices"))
    .def_readwrite("tag", &monero_account_tag::m_tag)
    .def_readwrite("label", &monero_account_tag::m_label)
    .def_readwrite("account_indices", &monero_account_tag::m_account_indices);

  // monero_destination
  t.py_monero_destination
    .def(py::init<>())
    .def(py::init<std::string>(), py::arg("address"))
    .def(py::init<std::string, uint64_t>(), py::arg("address"), py::arg("amount"))
    .def_readwrite("address", &monero_destination::m_address)
    .def_readwrite("amount", &monero_destination::m_amount)
    .def("copy", [](const std::shared_ptr<monero_destination>& self) {
      auto tgt = std::make_shared<monero_destination>();
      MONERO_CATCH_AND_RETHROW(self->copy(self, tgt));
    });

  // monero_transfer
  t.py_monero_transfer
    .def(py::init<>())
    .def_readwrite("tx", &monero_transfer::m_tx)
    .def_readwrite("account_index", &monero_transfer::m_account_index)
    .def_readwrite("amount", &monero_transfer::m_amount)
    .def("is_incoming", [](monero_transfer& self) {
      MONERO_CATCH_AND_RETHROW(self.is_incoming());
    })
    .def("is_outgoing", [](monero_transfer& self) {
      MONERO_CATCH_AND_RETHROW(self.is_outgoing());
    })
    .def("merge", [](const std::shared_ptr<monero_transfer>& self, const std::shared_ptr<monero_transfer>& other) {
      MONERO_CATCH_AND_RETHROW(self->merge(self, other));
    }, py::arg("other"))
    .def("copy", [](const std::shared_ptr<monero_transfer>& self) {
      auto tgt = std::make_shared<PyMoneroTransfer>();
      MONERO_CATCH_AND_RETHROW(self->copy(self, tgt));
    });

  // monero_incoming_transfer
  t.py_monero_incoming_transfer
    .def(py::init<>())
    .def_readwrite("address", &monero_incoming_transfer::m_address)
    .def_readwrite("subaddress_index", &monero_incoming_transfer::m_subaddress_index)
    .def_readwrite("num_suggested_confirmations", &monero_incoming_transfer::m_num_suggested_confirmations)
    .def("merge", [](const std::shared_ptr<monero_incoming_transfer>& self, const std::shared_ptr<monero_incoming_transfer>& other) {
      MONERO_CATCH_AND_RETHROW(self->merge(self, other));
    }, py::arg("other"))
    .def("copy", [](const std::shared_ptr<monero_incoming_transfer>& self) {
      auto tgt = std::make_shared<monero_incoming_transfer>();
      MONERO_CATCH_AND_RETHROW(self->copy(self, tgt));
    })
    .def("__lt__", [](const monero_incoming_transfer& a, const monero_incoming_transfer& b){
      monero_incoming_transfer_comparator comp;
      return comp(a, b);
    });

  // monero_outgoing_transfer
  t.py_monero_outgoing_transfer
    .def(py::init<>())
    .def_readwrite("subaddress_indices", &monero_outgoing_transfer::m_subaddress_indices)
    .def_readwrite("addresses", &monero_outgoing_transfer::m_addresses)
    .def_readwrite("destinations", &monero_outgoing_transfer::m_destinations)
    .def("merge", [](const std::shared_ptr<monero_outgoing_transfer>& self, const std::shared_ptr<monero_outgoing_transfer>& other) {
      MONERO_CATCH_AND_RETHROW(self->merge(self, other));
    }, py::arg("other"))
    .def("copy", [](const std::shared_ptr<monero_outgoing_transfer>& self) {
      auto tgt = std::make_shared<monero_outgoing_transfer>();
      MONERO_CATCH_AND_RETHROW(self->copy(self, tgt));
    });

  // monero_transfer_query
  t.py_monero_transfer_query
    .def(py::init<>())
    .def_static("deserialize_from_block", [](const std::string& transfer_query_json) {
      MONERO_CATCH_AND_RETHROW(monero_transfer_query::deserialize_from_block(transfer_query_json));
    }, py::arg("transfer_query_json"))
    .def_readwrite("incoming", &monero_transfer_query::m_is_incoming)
    .def_property("outgoing",
      [](const monero_transfer_query& self) { return self.is_outgoing(); },
      [](monero_transfer_query& self, const boost::optional<bool>& val) {
        if (val == boost::none) self.m_is_incoming = boost::none;
        else self.m_is_incoming = !val.get();
      })
    .def_readwrite("address", &monero_transfer_query::m_address)
    .def_readwrite("addresses", &monero_transfer_query::m_addresses)
    .def_readwrite("subaddress_index", &monero_transfer_query::m_subaddress_index)
    .def_readwrite("subaddress_indices", &monero_transfer_query::m_subaddress_indices)
    .def_readwrite("destinations", &monero_transfer_query::m_destinations)
    .def_readwrite("has_destinations", &monero_transfer_query::m_has_destinations)
    .def_property("tx_query",
      [](const monero_transfer_query& self) { return self.m_tx_query; },
      [](std::shared_ptr<monero_transfer_query>& self, const std::shared_ptr<monero_tx_query>& val) {
        const auto old_query = self->m_tx_query;
        self->m_tx_query = val;
        if (val != nullptr) {
          val->m_transfer_query = self;
        }
        else self->m_tx_query = nullptr;

        if (old_query != nullptr) {
          old_query->m_transfer_query = nullptr;
        }
      })
    .def("copy", [](const std::shared_ptr<monero_transfer_query>& self) {
      auto tgt = std::make_shared<monero_transfer_query>();
      MONERO_CATCH_AND_RETHROW(self->copy(self, tgt));
    })
    .def("meets_criteria", [](monero_transfer_query& self, monero_transfer* transfer, bool query_parent) {
      MONERO_CATCH_AND_RETHROW(self.meets_criteria(transfer, query_parent));
    }, py::arg("transfer"), py::arg("query_parent") = true);

  // monero_output_wallet
  t.py_monero_output_wallet
    .def(py::init<>())
    .def_readwrite("account_index", &monero_output_wallet::m_account_index)
    .def_readwrite("subaddress_index", &monero_output_wallet::m_subaddress_index)
    .def_readwrite("is_spent", &monero_output_wallet::m_is_spent)
    .def_readwrite("is_frozen", &monero_output_wallet::m_is_frozen)
    .def("copy", [](const std::shared_ptr<monero_output_wallet>& self) {
      auto tgt = std::make_shared<monero_output_wallet>();
      MONERO_CATCH_AND_RETHROW(self->copy(self, tgt));
    })
    .def("merge", [](const std::shared_ptr<monero_output_wallet>& self,  const std::shared_ptr<monero_output_wallet>& other) {
      MONERO_CATCH_AND_RETHROW(self->merge(self, other));
    }, py::arg("other"))
    .def("__lt__", [](const monero_output_wallet& a, const monero_output_wallet& b){
      monero_output_comparator comp;
      return comp(a, b);
    });

  // monero_output_query
  t.py_monero_output_query
    .def(py::init<>())
    .def_static("deserialize_from_block", [](const std::string& output_query_json) {
      MONERO_CATCH_AND_RETHROW(monero_output_query::deserialize_from_block(output_query_json));
    }, py::arg("output_query_json"))
    .def_readwrite("subaddress_indices", &monero_output_query::m_subaddress_indices)
    .def_readwrite("min_amount", &monero_output_query::m_min_amount)
    .def_readwrite("max_amount", &monero_output_query::m_max_amount)
    .def_readonly("tx_query", &monero_output_query::m_tx_query)
    .def("set_tx_query", [](const std::shared_ptr<monero_output_query>& self, const std::shared_ptr<monero_tx_query>& val, bool output_query) {
      const auto old_query = self->m_tx_query;
      if (val != nullptr) {
        self->m_tx_query = val;
        if (output_query) val->m_output_query = self;
        else val->m_input_query = self;
      } else {
        self->m_tx_query = nullptr;
      }
      if (old_query != nullptr) {
        if (output_query) old_query->m_output_query = nullptr;
        else old_query->m_input_query = nullptr;
      }
    }, py::arg("tx_query"), py::arg("output_query"))
    .def("copy", [](const std::shared_ptr<monero_output_query>& self) {
      auto tgt = std::make_shared<monero_output_query>();
      MONERO_CATCH_AND_RETHROW(self->copy(self, tgt));
    })
    .def("meets_criteria", [](monero_output_query& self, monero_output_wallet* output, bool query_parent) {
      MONERO_CATCH_AND_RETHROW(self.meets_criteria(output, query_parent));
    }, py::arg("output"), py::arg("query_parent") = true);

  // monero_tx_wallet
  t.py_monero_tx_wallet
    .def(py::init<>())
    .def_readwrite("tx_set", &monero_tx_wallet::m_tx_set)
    .def_readwrite("is_incoming", &monero_tx_wallet::m_is_incoming)
    .def_readwrite("is_outgoing", &monero_tx_wallet::m_is_outgoing)
    .def_readwrite("incoming_transfers", &monero_tx_wallet::m_incoming_transfers)
    .def_readwrite("outgoing_transfer", &monero_tx_wallet::m_outgoing_transfer)
    .def_readwrite("note", &monero_tx_wallet::m_note)
    .def_readwrite("is_locked", &monero_tx_wallet::m_is_locked)
    .def_readwrite("input_sum", &monero_tx_wallet::m_input_sum)
    .def_readwrite("output_sum", &monero_tx_wallet::m_output_sum)
    .def_readwrite("change_address", &monero_tx_wallet::m_change_address)
    .def_readwrite("change_amount", &monero_tx_wallet::m_change_amount)
    .def_readwrite("num_dummy_outputs", &monero_tx_wallet::m_num_dummy_outputs)
    .def_readwrite("extra_hex", &monero_tx_wallet::m_extra_hex)
    .def("get_incoming_amount", [](monero_tx_wallet& self) {
      uint64_t amount = 0;
      for (const auto& transfer : self.m_incoming_transfers) {
        if (transfer->m_amount != boost::none)
          amount += transfer->m_amount.get();
      }
      return amount;
    })
    .def("get_outgoing_amount", [](monero_tx_wallet& self) {
      uint64_t amount = 0;
      if (self.m_outgoing_transfer != nullptr && self.m_outgoing_transfer->m_amount != boost::none)
        amount = self.m_outgoing_transfer->m_amount.get();
      return amount;
    })
    .def("get_transfers", [](monero_tx_wallet& self) {
      MONERO_CATCH_AND_RETHROW(self.get_transfers());
    })
    .def("get_transfers", [](monero_tx_wallet& self, const monero_transfer_query& query) {
      MONERO_CATCH_AND_RETHROW(self.get_transfers(query));
    }, py::arg("query"))
    .def("filter_transfers", [](monero_tx_wallet& self, const monero_transfer_query& query) {
      MONERO_CATCH_AND_RETHROW(self.filter_transfers(query));
    }, py::arg("query"))
    .def("get_inputs_wallet", [](monero_tx_wallet& self, const boost::optional<monero_output_query>& query) {
      std::vector<std::shared_ptr<monero_output_wallet>> inputs;
      for(const auto& i : self.m_inputs) {
        auto input = std::dynamic_pointer_cast<monero_output_wallet>(i);
        if (!input) continue;
        if (query == boost::none || query.value().meets_criteria(input.get()))
          inputs.push_back(input);
      }
      return inputs;
    }, py::arg("query") = py::none())
    .def("get_outputs_wallet", [](monero_tx_wallet& self) {
      MONERO_CATCH_AND_RETHROW(self.get_outputs_wallet());
    })
    .def("get_outputs_wallet", [](monero_tx_wallet& self, const monero_output_query& query) {
      MONERO_CATCH_AND_RETHROW(self.get_outputs_wallet(query));
    }, py::arg("query"))
    .def("filter_outputs_wallet", [](monero_tx_wallet& self, const monero_output_query& query) {
      MONERO_CATCH_AND_RETHROW(self.filter_outputs_wallet(query));
    }, py::arg("query"))
    .def("copy", [](const std::shared_ptr<monero_tx_wallet>& self) {
      auto tgt = std::make_shared<monero_tx_wallet>();
      MONERO_CATCH_AND_RETHROW(self->copy(self, tgt));
    })
    .def("merge", [](const std::shared_ptr<monero_tx_wallet> &self, const std::shared_ptr<monero_tx_wallet>& tgt) {
      MONERO_CATCH_AND_RETHROW(self->merge(self, tgt));
    }, py::arg("tgt"));

  // monero_tx_query
  t.py_monero_tx_query
    .def(py::init<>())
    .def_static("deserialize_from_block", [](const std::string& tx_query_json) {
      MONERO_CATCH_AND_RETHROW(monero_tx_query::deserialize_from_block(tx_query_json));
    }, py::arg("tx_query_json"))
    .def_readwrite("is_outgoing", &monero_tx_query::m_is_outgoing)
    .def_readwrite("is_incoming", &monero_tx_query::m_is_incoming)
    .def_readwrite("hashes", &monero_tx_query::m_hashes)
    .def_readwrite("has_payment_id", &monero_tx_query::m_has_payment_id)
    .def_readwrite("payment_ids", &monero_tx_query::m_payment_ids)
    .def_readwrite("height", &monero_tx_query::m_height)
    .def_readwrite("min_height", &monero_tx_query::m_min_height)
    .def_readwrite("max_height", &monero_tx_query::m_max_height)
    .def_readwrite("include_outputs", &monero_tx_query::m_include_outputs)
    .def_property("transfer_query",
      [](const monero_tx_query& self) { return self.m_transfer_query; },
      [](std::shared_ptr<monero_tx_query>& self, const boost::optional<std::shared_ptr<monero_transfer_query>>& val) {
        PyMoneroUtils::set_query(self, self->m_transfer_query, val);
      })
    .def_property("input_query",
      [](const monero_tx_query& self) { return self.m_input_query; },
      [](std::shared_ptr<monero_tx_query>& self, const boost::optional<std::shared_ptr<monero_output_query>>& val) {
        PyMoneroUtils::set_query(self, self->m_input_query, val);
      })
    .def_property("output_query",
      [](const monero_tx_query& self) { return self.m_output_query; },
      [](std::shared_ptr<monero_tx_query>& self, const boost::optional<std::shared_ptr<monero_output_query>>& val) {
        PyMoneroUtils::set_query(self, self->m_output_query, val);
      })
    .def("copy", [](const std::shared_ptr<monero_tx_query>& self) {
      auto tgt = std::make_shared<monero_tx_query>();
      MONERO_CATCH_AND_RETHROW(self->copy(self, tgt));
    })
    .def("meets_criteria", [](monero_tx_query& self, monero_tx_wallet* tx, bool query_children) {
      MONERO_CATCH_AND_RETHROW(self.meets_criteria(tx, query_children));
    }, py::arg("tx"), py::arg("query_children") = false);

  // monero_tx_set
  t.py_monero_tx_set
    .def(py::init<>())
    .def_static("deserialize", [](const std::string& tx_set_json) {
      MONERO_CATCH_AND_RETHROW(monero_tx_set::deserialize(tx_set_json));
    }, py::arg("tx_set_json"))
    .def_readwrite("txs", &monero_tx_set::m_txs)
    .def_readwrite("signed_tx_hex", &monero_tx_set::m_signed_tx_hex)
    .def_readwrite("unsigned_tx_hex", &monero_tx_set::m_unsigned_tx_hex)
    .def_readwrite("multisig_tx_hex", &monero_tx_set::m_multisig_tx_hex);

  // monero_integrated_address
  t.py_monero_integrated_address
    .def(py::init<>())
    .def_readwrite("standard_address", &monero_integrated_address::m_standard_address)
    .def_readwrite("payment_id", &monero_integrated_address::m_payment_id)
    .def_readwrite("integrated_address", &monero_integrated_address::m_integrated_address);

  // monero_decoded_address
  t.py_monero_decoded_address
    .def(py::init<std::string&, monero_address_type, monero_network_type>(), py::arg("address"), py::arg("address_type"), py::arg("network_type"))
    .def_readwrite("address", &monero_decoded_address::m_address)
    .def_readwrite("address_type", &monero_decoded_address::m_address_type)
    .def_readwrite("network_type", &monero_decoded_address::m_network_type);

  // monero_tx_config
  t.py_monero_tx_config
    .def(py::init<>())
    .def(py::init<monero_tx_config&>(), py::arg("config"))
    .def_static("deserialize", [](const std::string& config_json) {
      MONERO_CATCH_AND_RETHROW(monero_tx_config::deserialize(config_json));
    }, py::arg("config_json"))
    .def_readwrite("address", &monero_tx_config::m_address)
    .def_readwrite("amount", &monero_tx_config::m_amount)
    .def_readwrite("destinations", &monero_tx_config::m_destinations)
    .def_readwrite("subtract_fee_from", &monero_tx_config::m_subtract_fee_from)
    .def_readwrite("payment_id", &monero_tx_config::m_payment_id)
    .def_readwrite("priority", &monero_tx_config::m_priority)
    .def_readwrite("ring_size", &monero_tx_config::m_ring_size)
    .def_readwrite("fee", &monero_tx_config::m_fee)
    .def_readwrite("account_index", &monero_tx_config::m_account_index)
    .def_readwrite("subaddress_indices", &monero_tx_config::m_subaddress_indices)
    .def_readwrite("can_split", &monero_tx_config::m_can_split)
    .def_readwrite("relay", &monero_tx_config::m_relay)
    .def_readwrite("note", &monero_tx_config::m_note)
    .def_readwrite("recipient_name", &monero_tx_config::m_recipient_name)
    .def_readwrite("below_amount", &monero_tx_config::m_below_amount)
    .def_readwrite("sweep_each_subaddress", &monero_tx_config::m_sweep_each_subaddress)
    .def_readwrite("key_image", &monero_tx_config::m_key_image)
    .def("set_address", [](monero_tx_config& self, const std::string& address) {
      if (self.m_destinations.size() > 1) throw monero_error("Cannot set address because MoneroTxConfig already has multiple destinations");
      if (self.m_destinations.empty()) {
        auto dest = std::make_shared<monero_destination>();
        dest->m_address = address;
        self.m_destinations.push_back(dest);
      }
      else self.m_destinations[0]->m_address = address;
    })
    .def("copy", [](monero_tx_config& self) {
      MONERO_CATCH_AND_RETHROW(self.copy());
    })
    .def("get_normalized_destinations", [](monero_tx_config& self) {
      MONERO_CATCH_AND_RETHROW(self.get_normalized_destinations());
    });

  // monero_key_image_export_result
  t.py_monero_key_image_export_result
    .def(py::init<>())
    .def_readwrite("offset", &monero_key_image_export_result::m_offset)
    .def_readwrite("key_images", &monero_key_image_export_result::m_key_images);

  // monero_key_image_import_result
  t.py_monero_key_image_import_result
    .def(py::init<>())
    .def_readwrite("height", &monero_key_image_import_result::m_height)
    .def_readwrite("spent_amount", &monero_key_image_import_result::m_spent_amount)
    .def_readwrite("unspent_amount", &monero_key_image_import_result::m_unspent_amount);

  // monero_message_signature_result
  t.py_monero_message_signature_result
    .def(py::init<>())
    .def_readwrite("is_good", &monero_message_signature_result::m_is_good)
    .def_readwrite("version", &monero_message_signature_result::m_version)
    .def_readwrite("is_old", &monero_message_signature_result::m_is_old)
    .def_readwrite("signature_type", &monero_message_signature_result::m_signature_type);

  // monero_check
  t.py_monero_check
    .def(py::init<>())
    .def_readwrite("is_good", &monero_check::m_is_good);

  // monero_check_tx
  t.py_monero_check_tx
    .def(py::init<>())
    .def_readwrite("in_tx_pool", &monero_check_tx::m_in_tx_pool)
    .def_readwrite("num_confirmations", &monero_check_tx::m_num_confirmations)
    .def_readwrite("received_amount", &monero_check_tx::m_received_amount);

  // monero_check_reserve
  t.py_monero_check_reserve
    .def(py::init<>())
    .def_readwrite("total_amount", &monero_check_reserve::m_total_amount)
    .def_readwrite("unconfirmed_spent_amount", &monero_check_reserve::m_unconfirmed_spent_amount);

  // monero_multisig_info
  t.py_monero_multisig_info
    .def(py::init<>())
    .def_readwrite("is_multisig", &monero_multisig_info::m_is_multisig)
    .def_readwrite("is_ready", &monero_multisig_info::m_is_ready)
    .def_readwrite("threshold", &monero_multisig_info::m_threshold)
    .def_readwrite("num_participants", &monero_multisig_info::m_num_participants);

  // monero_multisig_init_result
  t.py_monero_multisig_init_result
    .def(py::init<>())
    .def_readwrite("address", &monero_multisig_init_result::m_address)
    .def_readwrite("multisig_hex", &monero_multisig_init_result::m_multisig_hex);

  // monero_multisig_sign_result
  t.py_monero_multisig_sign_result
    .def(py::init<>())
    .def_readwrite("signed_multisig_tx_hex", &monero_multisig_sign_result::m_signed_multisig_tx_hex)
    .def_readwrite("tx_hashes", &monero_multisig_sign_result::m_tx_hashes);

  // monero_address_book_entry
  t.py_monero_address_book_entry
    .def(py::init<>())
    .def(py::init<uint64_t, const std::string&, const std::string&>(), py::arg("index"), py::arg("address"), py::arg("description"))
    .def(py::init<uint64_t, const std::string&, const std::string&, const std::string&>(), py::arg("index"), py::arg("address"), py::arg("description"), py::arg("payment_id"))
    .def_readwrite("index", &monero_address_book_entry::m_index)
    .def_readwrite("address", &monero_address_book_entry::m_address)
    .def_readwrite("description", &monero_address_book_entry::m_description)
    .def_readwrite("payment_id", &monero_address_book_entry::m_payment_id);

  // monero_wallet_listener
  t.py_monero_wallet_listener
    .def(py::init<>())
    .def("on_sync_progress", [](monero_wallet_listener& self, uint64_t height, uint64_t start_height, uint64_t end_height, double percent_done, const std::string& message) {
      MONERO_CATCH_AND_RETHROW(self.on_sync_progress(height, start_height, end_height, percent_done, message));
    }, py::arg("height"), py::arg("start_height"), py::arg("end_height"), py::arg("percent_done"), py::arg("message"))
    .def("on_new_block", [](monero_wallet_listener& self, uint64_t height) {
      MONERO_CATCH_AND_RETHROW(self.on_new_block(height));
    }, py::arg("height"))
    .def("on_balances_changed", [](monero_wallet_listener& self, uint64_t new_balance, uint64_t new_unlocked_balance) {
      MONERO_CATCH_AND_RETHROW(self.on_balances_changed(new_balance, new_unlocked_balance));
    }, py::arg("new_balance"), py::arg("new_unlocked_balance"))
    .def("on_output_received", [](monero_wallet_listener& self, const monero_output_wallet& output) {
      MONERO_CATCH_AND_RETHROW(self.on_output_received(output));
    }, py::arg("output"))
    .def("on_output_spent", [](monero_wallet_listener& self, const monero_output_wallet& output) {
      MONERO_CATCH_AND_RETHROW(self.on_output_spent(output));
    }, py::arg("output"));

  // monero_wallet
  t.py_monero_wallet
    .def(py::init<>())
    .def_property_readonly_static("DEFAULT_LANGUAGE", [](py::object /* self */) { return std::string("English"); })
    .def("is_view_only", [](PyMoneroWallet& self) {
      MONERO_CATCH_AND_RETHROW(self.is_view_only());
    }, py::call_guard<py::gil_scoped_release>())
    .def("set_daemon_connection", [](PyMoneroWallet& self, const std::shared_ptr<monero_rpc_connection>& connection, const boost::optional<bool>& is_trusted) {
      MONERO_CATCH_AND_RETHROW(self.set_daemon_connection(connection));
    }, py::arg("connection"), py::arg("is_trusted") = py::none(), py::call_guard<py::gil_scoped_release>())
     .def("set_daemon_connection", [](PyMoneroWallet& self, const std::string& uri, const std::string& username, const std::string& password, const std::string& proxy, const boost::optional<bool>& is_trusted) {
      MONERO_CATCH_AND_RETHROW(self.set_daemon_connection(uri, username, password, proxy));
    }, py::arg("uri"), py::arg("username") = "", py::arg("password") = "", py::arg("proxy") = "", py::arg("is_trusted") = py::none(), py::call_guard<py::gil_scoped_release>())
    .def("get_daemon_connection", [](PyMoneroWallet& self) {
      MONERO_CATCH_AND_RETHROW(self.get_daemon_connection());
    }, py::call_guard<py::gil_scoped_release>())
    .def("is_connected_to_daemon", [](PyMoneroWallet& self) {
      MONERO_CATCH_AND_RETHROW(self.is_connected_to_daemon());
    }, py::call_guard<py::gil_scoped_release>())
    .def("is_daemon_trusted", [](PyMoneroWallet& self) {
      MONERO_CATCH_AND_RETHROW(self.is_daemon_trusted());
    }, py::call_guard<py::gil_scoped_release>())
    .def("is_synced", [](PyMoneroWallet& self) {
      MONERO_CATCH_AND_RETHROW(self.is_synced());
    }, py::call_guard<py::gil_scoped_release>())
    .def("get_version", [](PyMoneroWallet& self) {
      MONERO_CATCH_AND_RETHROW(self.get_version());
    }, py::call_guard<py::gil_scoped_release>())
    .def("get_path", [](PyMoneroWallet& self) {
      MONERO_CATCH_AND_RETHROW(self.get_path());
    }, py::call_guard<py::gil_scoped_release>())
    .def("get_network_type", [](PyMoneroWallet& self) {
      MONERO_CATCH_AND_RETHROW(self.get_network_type());
    }, py::call_guard<py::gil_scoped_release>())
    .def("get_seed", [](PyMoneroWallet& self) {
      MONERO_CATCH_AND_RETHROW(self.get_seed());
    }, py::call_guard<py::gil_scoped_release>())
    .def("get_seed_language", [](PyMoneroWallet& self) {
      MONERO_CATCH_AND_RETHROW(self.get_seed_language());
    }, py::call_guard<py::gil_scoped_release>())
    .def("get_public_view_key", [](PyMoneroWallet& self) {
      MONERO_CATCH_AND_RETHROW(self.get_public_view_key());
    }, py::call_guard<py::gil_scoped_release>())
    .def("get_private_view_key", [](PyMoneroWallet& self) {
      MONERO_CATCH_AND_RETHROW(self.get_private_view_key());
    }, py::call_guard<py::gil_scoped_release>())
    .def("get_public_spend_key", [](PyMoneroWallet& self) {
      MONERO_CATCH_AND_RETHROW(self.get_public_spend_key());
    }, py::call_guard<py::gil_scoped_release>())
    .def("get_private_spend_key", [](PyMoneroWallet& self) {
      MONERO_CATCH_AND_RETHROW(self.get_private_spend_key());
    }, py::call_guard<py::gil_scoped_release>())
    .def("get_primary_address", [](PyMoneroWallet& self) {
      MONERO_CATCH_AND_RETHROW(self.get_primary_address());
    }, py::call_guard<py::gil_scoped_release>())
    .def("get_address", [](PyMoneroWallet& self, uint32_t account_idx, uint32_t subaddress_idx) {
      MONERO_CATCH_AND_RETHROW(self.get_address(account_idx, subaddress_idx));
    }, py::arg("account_idx"), py::arg("subaddress_idx"), py::call_guard<py::gil_scoped_release>())
    .def("get_address_index", [](PyMoneroWallet& self, const std::string& address) {
      MONERO_CATCH_AND_RETHROW(self.get_address_index(address));
    }, py::arg("address"), py::call_guard<py::gil_scoped_release>())
    .def("get_integrated_address", [](PyMoneroWallet& self, const std::string& standard_address, const std::string& payment_id) {
      MONERO_CATCH_AND_RETHROW(self.get_integrated_address(standard_address, payment_id));
    }, py::arg("standard_address") = "", py::arg("payment_id") = "", py::call_guard<py::gil_scoped_release>())
    .def("decode_integrated_address", [](PyMoneroWallet& self, const std::string& integrated_address) {
      MONERO_CATCH_AND_RETHROW(self.decode_integrated_address(integrated_address));
    }, py::arg("integrated_address"), py::call_guard<py::gil_scoped_release>())
    .def("get_height", [](PyMoneroWallet& self) {
      MONERO_CATCH_AND_RETHROW(self.get_height());
    }, py::call_guard<py::gil_scoped_release>())
    .def("get_restore_height", [](PyMoneroWallet& self) {
      MONERO_CATCH_AND_RETHROW(self.get_restore_height());
    }, py::call_guard<py::gil_scoped_release>())
    .def("set_restore_height", [](PyMoneroWallet& self, uint64_t restore_height) {
      MONERO_CATCH_AND_RETHROW(self.set_restore_height(restore_height));
    }, py::arg("restore_height"), py::call_guard<py::gil_scoped_release>())
    .def("get_daemon_height", [](PyMoneroWallet& self) {
      MONERO_CATCH_AND_RETHROW(self.get_daemon_height());
    }, py::call_guard<py::gil_scoped_release>())
    .def("get_daemon_max_peer_height", [](PyMoneroWallet& self) {
      MONERO_CATCH_AND_RETHROW(self.get_daemon_max_peer_height());
    }, py::call_guard<py::gil_scoped_release>())
    .def("get_height_by_date", [](PyMoneroWallet& self, uint16_t year, uint8_t month, uint8_t day) {
      MONERO_CATCH_AND_RETHROW(self.get_height_by_date(year, month, day));
    }, py::arg("year"), py::arg("month"), py::arg("day"), py::call_guard<py::gil_scoped_release>())
    .def("add_listener", [](PyMoneroWallet& self, monero_wallet_listener& listener) {
      MONERO_CATCH_AND_RETHROW(self.add_listener(listener));
    }, py::arg("listener"), py::call_guard<py::gil_scoped_release>())
    .def("remove_listener", [](PyMoneroWallet& self, monero_wallet_listener& listener) {
      MONERO_CATCH_AND_RETHROW(self.remove_listener(listener));
    }, py::arg("listener"), py::call_guard<py::gil_scoped_release>())
    .def("get_listeners", [](PyMoneroWallet& self) {
      MONERO_CATCH_AND_RETHROW(self.get_listeners());
    }, py::call_guard<py::gil_scoped_release>())
    .def("sync", [](PyMoneroWallet& self) {
      MONERO_CATCH_AND_RETHROW(self.sync());
    }, py::call_guard<py::gil_scoped_release>())
    .def("sync", [](PyMoneroWallet& self, monero_wallet_listener& listener) {
      MONERO_CATCH_AND_RETHROW(self.sync(listener));
    }, py::arg("listener"), py::call_guard<py::gil_scoped_release>())
    .def("sync", [](PyMoneroWallet& self, uint64_t start_height) {
      MONERO_CATCH_AND_RETHROW(self.sync(start_height));
    }, py::arg("start_height"), py::call_guard<py::gil_scoped_release>())
    .def("sync", [](PyMoneroWallet& self, uint64_t start_height, monero_wallet_listener& listener) {
      MONERO_CATCH_AND_RETHROW(self.sync(start_height, listener));
    }, py::arg("start_height"), py::arg("listener"), py::call_guard<py::gil_scoped_release>())
    .def("start_syncing", [](PyMoneroWallet& self, uint64_t sync_period_in_ms) {
      MONERO_CATCH_AND_RETHROW(self.start_syncing(sync_period_in_ms));
    }, py::arg("sync_period_in_ms") = 10000, py::call_guard<py::gil_scoped_release>())
    .def("stop_syncing", [](PyMoneroWallet& self) {
      MONERO_CATCH_AND_RETHROW(self.stop_syncing());
    }, py::call_guard<py::gil_scoped_release>())
    .def("scan_txs", [](PyMoneroWallet& self, const std::vector<std::string>& tx_hashes) {
      MONERO_CATCH_AND_RETHROW(self.scan_txs(tx_hashes));
    }, py::arg("tx_hashes"), py::call_guard<py::gil_scoped_release>())
    .def("rescan_spent", [](PyMoneroWallet& self) {
      MONERO_CATCH_AND_RETHROW(self.rescan_spent());
    }, py::call_guard<py::gil_scoped_release>())
    .def("rescan_blockchain", [](PyMoneroWallet& self) {
      MONERO_CATCH_AND_RETHROW(self.rescan_blockchain());
    }, py::call_guard<py::gil_scoped_release>())
    .def("get_balance", [](PyMoneroWallet& self) {
      MONERO_CATCH_AND_RETHROW(self.get_balance());
    }, py::call_guard<py::gil_scoped_release>())
    .def("get_balance", [](PyMoneroWallet& self, uint32_t account_idx) {
      MONERO_CATCH_AND_RETHROW(self.get_balance(account_idx));
    }, py::arg("account_idx"), py::call_guard<py::gil_scoped_release>())
    .def("get_balance", [](PyMoneroWallet& self, uint32_t account_idx, uint32_t subaddress_idx) {
      MONERO_CATCH_AND_RETHROW(self.get_balance(account_idx, subaddress_idx));
    }, py::arg("account_idx"), py::arg("subaddress_idx"), py::call_guard<py::gil_scoped_release>())
    .def("get_unlocked_balance", [](PyMoneroWallet& self) {
      MONERO_CATCH_AND_RETHROW(self.get_unlocked_balance());
    }, py::call_guard<py::gil_scoped_release>())
    .def("get_unlocked_balance", [](PyMoneroWallet& self, uint32_t account_idx) {
      MONERO_CATCH_AND_RETHROW(self.get_unlocked_balance(account_idx));
    }, py::arg("account_idx"), py::call_guard<py::gil_scoped_release>())
    .def("get_unlocked_balance", [](PyMoneroWallet& self, uint32_t account_idx, uint32_t subaddress_idx) {
      MONERO_CATCH_AND_RETHROW(self.get_unlocked_balance(account_idx, subaddress_idx));
    }, py::arg("account_idx"), py::arg("subaddress_idx"), py::call_guard<py::gil_scoped_release>())
    .def("get_accounts", [](PyMoneroWallet& self) {
      MONERO_CATCH_AND_RETHROW(self.get_accounts());
    }, py::call_guard<py::gil_scoped_release>())
    .def("get_accounts", [](PyMoneroWallet& self, bool include_subaddresses) {
      MONERO_CATCH_AND_RETHROW(self.get_accounts(include_subaddresses));
    }, py::arg("include_subaddresses"), py::call_guard<py::gil_scoped_release>())
    .def("get_accounts", [](PyMoneroWallet& self, const std::string& tag) {
      MONERO_CATCH_AND_RETHROW(self.get_accounts(tag));
    }, py::arg("tag"), py::call_guard<py::gil_scoped_release>())
    .def("get_accounts", [](PyMoneroWallet& self, bool include_subaddresses, const std::string& tag) {
      MONERO_CATCH_AND_RETHROW(self.get_accounts(include_subaddresses, tag));
    }, py::arg("include_subaddresses"), py::arg("tag"), py::call_guard<py::gil_scoped_release>())
    .def("get_account", [](PyMoneroWallet& self, uint32_t account_idx) {
      MONERO_CATCH_AND_RETHROW(self.get_account(account_idx));
    }, py::arg("account_idx"), py::call_guard<py::gil_scoped_release>())
    .def("get_account", [](PyMoneroWallet& self, uint32_t account_idx, bool include_subaddresses) {
      MONERO_CATCH_AND_RETHROW(self.get_account(account_idx, include_subaddresses));
    }, py::arg("account_idx"), py::arg("include_subaddresses"), py::call_guard<py::gil_scoped_release>())
    .def("create_account", [](PyMoneroWallet& self, const std::string& label) {
      MONERO_CATCH_AND_RETHROW(self.create_account(label));
    }, py::arg("label") = "", py::call_guard<py::gil_scoped_release>())
    .def("get_subaddress", [](PyMoneroWallet& wallet, uint32_t account_idx, uint32_t subaddress_idx) {
      // TODO move this to monero-cpp?
      try {
        std::vector<uint32_t> subaddress_indices;
        subaddress_indices.push_back(subaddress_idx);
        auto subaddresses = wallet.get_subaddresses(account_idx, subaddress_indices);
        if (subaddresses.empty()) throw std::runtime_error("Subaddress is not initialized");
        if (subaddresses.size() != 1) throw std::runtime_error("Only 1 subaddress should be returned");
        return subaddresses[0];
      } catch (const monero_rpc_error& e) {
        throw;
      } catch (const std::exception& e) {
        throw monero_error(e.what());
      }
    }, py::arg("account_idx"), py::arg("subaddress_idx"), py::call_guard<py::gil_scoped_release>())
    .def("get_subaddresses", [](PyMoneroWallet& self, uint32_t account_idx) {
      MONERO_CATCH_AND_RETHROW(self.get_subaddresses(account_idx));
    }, py::arg("account_idx"), py::call_guard<py::gil_scoped_release>())
    .def("get_subaddresses", [](PyMoneroWallet& self, uint32_t account_idx, const std::vector<uint32_t>& subaddress_indices) {
      MONERO_CATCH_AND_RETHROW(self.get_subaddresses(account_idx, subaddress_indices));
    }, py::arg("account_idx"), py::arg("subaddress_indices"), py::call_guard<py::gil_scoped_release>())
    .def("create_subaddress", [](PyMoneroWallet& self, uint32_t account_idx, const std::string& label) {
      MONERO_CATCH_AND_RETHROW(self.create_subaddress(account_idx, label));
    }, py::arg("account_idx"), py::arg("label") = "", py::call_guard<py::gil_scoped_release>())
    .def("set_subaddress_label", [](PyMoneroWallet& self, uint32_t account_idx, uint32_t subaddress_idx, const std::string& label) {
      MONERO_CATCH_AND_RETHROW(self.set_subaddress_label(account_idx, subaddress_idx, label));
    }, py::arg("account_idx"), py::arg("subaddress_idx"), py::arg("label") = "", py::call_guard<py::gil_scoped_release>())
    .def("get_tx", [](PyMoneroWallet& self, const std::string& tx_hash) {
      std::shared_ptr<monero_tx_wallet> result = nullptr;
      monero_tx_query query;
      query.m_hashes.push_back(tx_hash);
      auto txs = self.get_txs(query);
      if (txs.size() > 0) {
        result = txs[0];
      }
      return result;
    }, py::arg("tx_hash"), py::call_guard<py::gil_scoped_release>())
    .def("get_txs", [](PyMoneroWallet& self) {
      MONERO_CATCH_AND_RETHROW(self.get_txs());
    }, py::call_guard<py::gil_scoped_release>())
    .def("get_txs", [](PyMoneroWallet& self, const monero_tx_query& query) {
      MONERO_CATCH_AND_RETHROW(PyMoneroUtils::get_and_sort_txs(self, query));
    }, py::arg("query"), py::call_guard<py::gil_scoped_release>())
    .def("get_txs", [](PyMoneroWallet& self, const std::vector<std::string>& tx_hashes) {
      MONERO_CATCH_AND_RETHROW(PyMoneroUtils::get_and_sort_txs(self, tx_hashes));
    }, py::arg("tx_hashes"), py::call_guard<py::gil_scoped_release>())
    .def("get_transfers", [](PyMoneroWallet& self, const monero_transfer_query& query) {
      MONERO_CATCH_AND_RETHROW(self.get_transfers(query));
    }, py::arg("query"), py::call_guard<py::gil_scoped_release>())
    .def("get_transfers", [](PyMoneroWallet& self) {
      monero_transfer_query query;
      MONERO_CATCH_AND_RETHROW(self.get_transfers(query));
    }, py::call_guard<py::gil_scoped_release>())
    .def("get_transfers", [](PyMoneroWallet& self, uint32_t account_index) {
      monero_transfer_query query;
      query.m_account_index = account_index;
      MONERO_CATCH_AND_RETHROW(self.get_transfers(query));
    }, py::arg("account_index"), py::call_guard<py::gil_scoped_release>())
    .def("get_transfers", [](PyMoneroWallet& self, uint32_t account_index, uint32_t subaddress_index) {
      monero_transfer_query query;
      query.m_account_index = account_index;
      query.m_subaddress_index = subaddress_index;
      MONERO_CATCH_AND_RETHROW(self.get_transfers(query));
    }, py::arg("account_index"), py::arg("subaddress_index"), py::call_guard<py::gil_scoped_release>())
    .def("get_outputs", [](PyMoneroWallet& self, const monero_output_query& query) {
      MONERO_CATCH_AND_RETHROW(self.get_outputs(query));
    }, py::arg("query"), py::call_guard<py::gil_scoped_release>())
    .def("get_outputs", [](PyMoneroWallet& self) {
      monero_output_query query;
      MONERO_CATCH_AND_RETHROW(self.get_outputs(query));
    }, py::call_guard<py::gil_scoped_release>())
    .def("export_outputs", [](PyMoneroWallet& self, bool all) {
      MONERO_CATCH_AND_RETHROW(self.export_outputs(all));
    }, py::arg("all") = false, py::call_guard<py::gil_scoped_release>())
    .def("import_outputs", [](PyMoneroWallet& self, const std::string& outputs_hex) {
      MONERO_CATCH_AND_RETHROW(self.import_outputs(outputs_hex));
    }, py::arg("outputs_hex"), py::call_guard<py::gil_scoped_release>())
    .def("export_key_images", [](PyMoneroWallet& self, bool all) {
      MONERO_CATCH_AND_RETHROW(self.export_key_images(all));
    }, py::arg("all") = false, py::call_guard<py::gil_scoped_release>())
    .def("import_key_images", [](PyMoneroWallet& self, const std::vector<std::shared_ptr<monero_key_image>>& key_images, uint64_t offset) {
      MONERO_CATCH_AND_RETHROW(self.import_key_images(key_images));
    }, py::arg("key_images"), py::arg("offset") = 0, py::call_guard<py::gil_scoped_release>())
    .def("get_new_key_images_from_last_import", [](PyMoneroWallet& self) {
      MONERO_CATCH_AND_RETHROW(self.export_key_images(false));
    }, py::call_guard<py::gil_scoped_release>())
    .def("freeze_output", [](PyMoneroWallet& self, const std::string& key_image) {
      MONERO_CATCH_AND_RETHROW(self.freeze_output(key_image));
    }, py::arg("key_image"), py::call_guard<py::gil_scoped_release>())
    .def("thaw_output", [](PyMoneroWallet& self, const std::string& key_image) {
      MONERO_CATCH_AND_RETHROW(self.thaw_output(key_image));
    }, py::arg("key_image"), py::call_guard<py::gil_scoped_release>())
    .def("is_output_frozen", [](PyMoneroWallet& self, const std::string& key_image) {
      MONERO_CATCH_AND_RETHROW(self.is_output_frozen(key_image));
    }, py::arg("key_image"), py::call_guard<py::gil_scoped_release>())
    .def("get_default_fee_priority", [](PyMoneroWallet& self) {
      MONERO_CATCH_AND_RETHROW(self.get_default_fee_priority());
    }, py::call_guard<py::gil_scoped_release>())
    .def("create_tx", [](PyMoneroWallet& self, const monero_tx_config& config) {
      MONERO_CATCH_AND_RETHROW(self.create_tx(config));
    }, py::arg("config"), py::call_guard<py::gil_scoped_release>())
    .def("create_txs", [](PyMoneroWallet& self, const monero_tx_config& config) {
      MONERO_CATCH_AND_RETHROW(self.create_txs(config));
    }, py::arg("config"), py::call_guard<py::gil_scoped_release>())
    .def("sweep_unlocked", [](PyMoneroWallet& self, const monero_tx_config& config) {
      MONERO_CATCH_AND_RETHROW(self.sweep_unlocked(config));
    }, py::arg("config"), py::call_guard<py::gil_scoped_release>())
    .def("sweep_output", [](PyMoneroWallet& self, const monero_tx_config& config) {
      MONERO_CATCH_AND_RETHROW(self.sweep_output(config));
    }, py::arg("config"), py::call_guard<py::gil_scoped_release>())
    .def("sweep_dust", [](PyMoneroWallet& self, bool relay) {
      MONERO_CATCH_AND_RETHROW(self.sweep_dust(relay));
    }, py::arg("relay") = false, py::call_guard<py::gil_scoped_release>())
    .def("relay_tx", [](PyMoneroWallet& self, const std::string& tx_metadata) {
      MONERO_CATCH_AND_RETHROW(self.relay_tx(tx_metadata));
    }, py::arg("tx_metadata"), py::call_guard<py::gil_scoped_release>())
    .def("relay_tx", [](PyMoneroWallet& self, const monero_tx_wallet& tx) {
      MONERO_CATCH_AND_RETHROW(self.relay_tx(tx));
    }, py::arg("tx"), py::call_guard<py::gil_scoped_release>())
    .def("relay_txs", [](PyMoneroWallet& self, const std::vector<std::shared_ptr<monero_tx_wallet>>& txs) {
      MONERO_CATCH_AND_RETHROW(self.relay_txs(txs));
    }, py::arg("txs"), py::call_guard<py::gil_scoped_release>())
    .def("relay_txs", [](PyMoneroWallet& self, const std::vector<std::string>& tx_metadatas) {
      MONERO_CATCH_AND_RETHROW(self.relay_txs(tx_metadatas));
    }, py::arg("tx_metadatas"), py::call_guard<py::gil_scoped_release>())
    .def("describe_tx_set", [](PyMoneroWallet& self, const monero_tx_set& tx_set) {
      MONERO_CATCH_AND_RETHROW(self.describe_tx_set(tx_set));
    }, py::arg("tx_set"), py::call_guard<py::gil_scoped_release>())
    .def("describe_unsigned_tx_set", [](PyMoneroWallet& self, const std::string& unsigned_tx_hex) {
      monero_tx_set tx_set;
      tx_set.m_unsigned_tx_hex = unsigned_tx_hex;
      MONERO_CATCH_AND_RETHROW(self.describe_tx_set(tx_set));
    }, py::arg("unsigned_tx_hex"), py::call_guard<py::gil_scoped_release>())
    .def("describe_multisig_tx_set", [](PyMoneroWallet& self, const std::string& multisig_tx_hex) {
      monero_tx_set tx_set;
      tx_set.m_multisig_tx_hex = multisig_tx_hex;
      MONERO_CATCH_AND_RETHROW(self.describe_tx_set(tx_set));
    }, py::arg("multisig_tx_hex"), py::call_guard<py::gil_scoped_release>())
    .def("sign_txs", [](PyMoneroWallet& self, const std::string& unsigned_tx_hex) {
      MONERO_CATCH_AND_RETHROW(self.sign_txs(unsigned_tx_hex));
    }, py::arg("unsigned_tx_hex"), py::call_guard<py::gil_scoped_release>())
    .def("submit_txs", [](PyMoneroWallet& self, const std::string& signed_tx_hex) {
      MONERO_CATCH_AND_RETHROW(self.submit_txs(signed_tx_hex));
    }, py::arg("signed_tx_hex"), py::call_guard<py::gil_scoped_release>())
    .def("sign_message", [](PyMoneroWallet& self, const std::string& msg, monero_message_signature_type signature_type, uint32_t account_idx, uint32_t subaddress_idx) {
      MONERO_CATCH_AND_RETHROW(self.sign_message(msg, signature_type, account_idx, subaddress_idx));
    }, py::arg("msg"), py::arg("signature_type"), py::arg("account_idx") = 0, py::arg("subaddress_idx") = 0, py::call_guard<py::gil_scoped_release>())
    .def("verify_message", [](PyMoneroWallet& self, const std::string& msg, const std::string& address, const std::string& signature) {
      try {
        return self.verify_message(msg, address, signature);
      } catch (...) {
        // TODO wallet full can differentiate incorrect from invalid address, but rpc returns -2 for both, so returning bad result for consistency
        return monero_message_signature_result();
      }
    }, py::arg("msg"), py::arg("address"), py::arg("signature"), py::call_guard<py::gil_scoped_release>())
    .def("get_tx_key", [](PyMoneroWallet& self, const std::string& tx_hash) {
      MONERO_CATCH_AND_RETHROW(self.get_tx_key(tx_hash));
    }, py::arg("tx_hash"), py::call_guard<py::gil_scoped_release>())
    .def("check_tx_key", [](PyMoneroWallet& self, const std::string& tx_hash, const std::string& tx_key, const std::string& address) {
      MONERO_CATCH_AND_RETHROW(self.check_tx_key(tx_hash, tx_key, address));
    }, py::arg("tx_hash"), py::arg("tx_key"), py::arg("address"), py::call_guard<py::gil_scoped_release>())
    .def("get_tx_proof", [](PyMoneroWallet& self, const std::string& tx_hash, const std::string& address, const std::string& message) {
      MONERO_CATCH_AND_RETHROW(self.get_tx_proof(tx_hash, address, message));
    }, py::arg("tx_hash"), py::arg("address"), py::arg("message") = "", py::call_guard<py::gil_scoped_release>())
    .def("check_tx_proof", [](PyMoneroWallet& self, const std::string& tx_hash, const std::string& address, const std::string& message, const std::string& signature) {
      MONERO_CATCH_AND_RETHROW(self.check_tx_proof(tx_hash, address, message, signature));
    }, py::arg("tx_hash"), py::arg("address"), py::arg("message"), py::arg("signature"), py::call_guard<py::gil_scoped_release>())
    .def("get_spend_proof", [](PyMoneroWallet& self, const std::string& tx_hash, const std::string& message) {
      MONERO_CATCH_AND_RETHROW(self.get_spend_proof(tx_hash, message));
    }, py::arg("tx_hash"), py::arg("message") = "", py::call_guard<py::gil_scoped_release>())
    .def("check_spend_proof", [](PyMoneroWallet& self, const std::string& tx_hash, const std::string& message, const std::string& signature) {
      MONERO_CATCH_AND_RETHROW(self.check_spend_proof(tx_hash, message, signature));
    }, py::arg("tx_hash"), py::arg("message"), py::arg("signature"), py::call_guard<py::gil_scoped_release>())
    .def("get_reserve_proof_wallet", [](PyMoneroWallet& self, const std::string& message) {
      MONERO_CATCH_AND_RETHROW(self.get_reserve_proof_wallet(message));
    }, py::arg("message"), py::call_guard<py::gil_scoped_release>())
    .def("get_reserve_proof_account", [](PyMoneroWallet& self, uint32_t account_idx, uint64_t amount, const std::string& message) {
      MONERO_CATCH_AND_RETHROW(self.get_reserve_proof_account(account_idx, amount, message));
    }, py::arg("account_idx"), py::arg("amount"), py::arg("message"), py::call_guard<py::gil_scoped_release>())
    .def("check_reserve_proof", [](PyMoneroWallet& self, const std::string& address, const std::string& message, const std::string& signature) {
      MONERO_CATCH_AND_RETHROW(self.check_reserve_proof(address, message, signature));
    }, py::arg("address"), py::arg("message"), py::arg("signature"), py::call_guard<py::gil_scoped_release>())
    .def("get_tx_note", [](PyMoneroWallet& self, const std::string& tx_hash) {
      MONERO_CATCH_AND_RETHROW(self.get_tx_note(tx_hash));
    }, py::arg("tx_hash"), py::call_guard<py::gil_scoped_release>())
    .def("get_tx_notes", [](PyMoneroWallet& self, const std::vector<std::string>& tx_hashes) {
      MONERO_CATCH_AND_RETHROW(self.get_tx_notes(tx_hashes));
    }, py::arg("tx_hashes"), py::call_guard<py::gil_scoped_release>())
    .def("set_tx_note", [](PyMoneroWallet& self, const std::string& tx_hash, const std::string& note) {
      MONERO_CATCH_AND_RETHROW(self.set_tx_note(tx_hash, note));
    }, py::arg("tx_hash"), py::arg("note"), py::call_guard<py::gil_scoped_release>())
    .def("set_tx_notes", [](PyMoneroWallet& self, const std::vector<std::string>& tx_hashes, const std::vector<std::string>& notes) {
      MONERO_CATCH_AND_RETHROW(self.set_tx_notes(tx_hashes, notes));
    }, py::arg("tx_hashes"), py::arg("notes"), py::call_guard<py::gil_scoped_release>())
    .def("get_address_book_entries", [](PyMoneroWallet& self, const std::vector<uint64_t>& indices) {
      MONERO_CATCH_AND_RETHROW(self.get_address_book_entries(indices));
    }, py::arg("indices"), py::call_guard<py::gil_scoped_release>())
    .def("get_address_book_entries", [](PyMoneroWallet& self) {
      std::vector<uint64_t> indices;
      MONERO_CATCH_AND_RETHROW(self.get_address_book_entries(indices));
    }, py::call_guard<py::gil_scoped_release>())
    .def("add_address_book_entry", [](PyMoneroWallet& self, const std::string& address, const std::string& description) {
      MONERO_CATCH_AND_RETHROW(self.add_address_book_entry(address, description));
    }, py::arg("address"), py::arg("description"), py::call_guard<py::gil_scoped_release>())
    .def("edit_address_book_entry", [](PyMoneroWallet& self, uint64_t index, bool set_address, const std::string& address, bool set_description, const std::string& description) {
      MONERO_CATCH_AND_RETHROW(self.edit_address_book_entry(index, set_address, address, set_description, description));
    }, py::arg("index"), py::arg("set_address"), py::arg("address"), py::arg("set_description"), py::arg("description"), py::call_guard<py::gil_scoped_release>())
    .def("delete_address_book_entry", [](PyMoneroWallet& self, uint64_t index) {
      MONERO_CATCH_AND_RETHROW(self.delete_address_book_entry(index));
    }, py::arg("index"), py::call_guard<py::gil_scoped_release>())
    .def("tag_accounts", [](monero_wallet& self, const std::string& tag, const std::vector<uint32_t>& account_indices) {
      MONERO_CATCH_AND_RETHROW(self.tag_accounts(tag, account_indices));
    }, py::arg("tag"), py::arg("account_indices"), py::call_guard<py::gil_scoped_release>())
    .def("untag_accounts", [](monero_wallet& self, const std::vector<uint32_t>& account_indices) {
      MONERO_CATCH_AND_RETHROW(self.untag_accounts(account_indices));
    }, py::arg("account_indices"), py::call_guard<py::gil_scoped_release>())
    .def("get_account_tags", [](const monero_wallet& self) {
      MONERO_CATCH_AND_RETHROW(self.get_account_tags());
    }, py::call_guard<py::gil_scoped_release>())
    .def("set_account_tag_label", [](monero_wallet& self, const std::string& tag, const std::string& label) {
      MONERO_CATCH_AND_RETHROW(self.set_account_tag_label(tag, label));
    }, py::arg("tag"), py::arg("label"), py::call_guard<py::gil_scoped_release>())
    .def("set_account_label", [](PyMoneroWallet& self, uint32_t account_idx, const std::string& label) {
      MONERO_CATCH_AND_RETHROW(self.set_subaddress_label(account_idx, 0, label));
    }, py::arg("account_idx"), py::arg("label"), py::call_guard<py::gil_scoped_release>())
    .def("get_payment_uri", [](PyMoneroWallet& self, const monero_tx_config& config) {
      MONERO_CATCH_AND_RETHROW(self.get_payment_uri(config));
    }, py::arg("config"), py::call_guard<py::gil_scoped_release>())
    .def("parse_payment_uri", [](PyMoneroWallet& self, const std::string& uri) {
      MONERO_CATCH_AND_RETHROW(self.parse_payment_uri(uri));
    }, py::arg("uri"), py::call_guard<py::gil_scoped_release>())
    .def("get_attribute", [](PyMoneroWallet& self, const std::string& key) {
      try {
        std::string val;
        self.get_attribute(key, val);
        return val;
      } catch (const std::exception& ex) {
        throw monero_error(ex.what());
      }
    }, py::arg("key"), py::call_guard<py::gil_scoped_release>())
    .def("set_attribute", [](PyMoneroWallet& self, const std::string& key, const std::string& val) {
      MONERO_CATCH_AND_RETHROW(self.set_attribute(key, val));
    }, py::arg("key"), py::arg("val"), py::call_guard<py::gil_scoped_release>())
    .def("start_mining", [](PyMoneroWallet& self, const boost::optional<uint64_t>& num_threads, const boost::optional<bool>& background_mining, const boost::optional<bool>& ignore_battery) {
      MONERO_CATCH_AND_RETHROW(self.start_mining(num_threads, background_mining, ignore_battery));
    }, py::arg("num_threads") = py::none(), py::arg("background_mining") = py::none(), py::arg("ignore_battery") = py::none(), py::call_guard<py::gil_scoped_release>())
    .def("stop_mining", [](PyMoneroWallet& self) {
      MONERO_CATCH_AND_RETHROW(self.stop_mining());
    }, py::call_guard<py::gil_scoped_release>())
    .def("wait_for_next_block", [](PyMoneroWallet& self) {
      MONERO_CATCH_AND_RETHROW(self.wait_for_next_block());
    }, py::call_guard<py::gil_scoped_release>())
    .def("is_multisig_import_needed", [](PyMoneroWallet& self) {
      MONERO_CATCH_AND_RETHROW(self.is_multisig_import_needed());
    }, py::call_guard<py::gil_scoped_release>())
    .def("is_multisig", [](PyMoneroWallet& self) {
      MONERO_CATCH_AND_RETHROW(self.is_multisig());
    }, py::call_guard<py::gil_scoped_release>())
    .def("get_multisig_info", [](PyMoneroWallet& self) {
      MONERO_CATCH_AND_RETHROW(self.get_multisig_info());
    }, py::call_guard<py::gil_scoped_release>())
    .def("prepare_multisig", [](PyMoneroWallet& self) {
      MONERO_CATCH_AND_RETHROW(self.prepare_multisig());
    }, py::call_guard<py::gil_scoped_release>())
    .def("make_multisig", [](PyMoneroWallet& self, const std::vector<std::string>& multisig_hexes, int threshold, const std::string& password) {
      MONERO_CATCH_AND_RETHROW(self.make_multisig(multisig_hexes, threshold, password));
    }, py::arg("multisig_hexes"), py::arg("threshold"), py::arg("password"), py::call_guard<py::gil_scoped_release>())
    .def("exchange_multisig_keys", [](PyMoneroWallet& self, const std::vector<std::string>& multisig_hexes, const std::string& password) {
      MONERO_CATCH_AND_RETHROW(self.exchange_multisig_keys(multisig_hexes, password));
    }, py::arg("multisig_hexes"), py::arg("password"), py::call_guard<py::gil_scoped_release>())
    .def("export_multisig_hex", [](PyMoneroWallet& self) {
      MONERO_CATCH_AND_RETHROW(self.export_multisig_hex());
    }, py::call_guard<py::gil_scoped_release>())
    .def("import_multisig_hex", [](PyMoneroWallet& self, const std::vector<std::string>& multisig_hexes, bool refresh_after_import) {
      MONERO_CATCH_AND_RETHROW(self.import_multisig_hex(multisig_hexes, refresh_after_import));
    }, py::arg("multisig_hexes"), py::arg("refresh_after_import") = true, py::call_guard<py::gil_scoped_release>())
    .def("sign_multisig_tx_hex", [](PyMoneroWallet& self, const std::string& multisig_tx_hex) {
      MONERO_CATCH_AND_RETHROW(self.sign_multisig_tx_hex(multisig_tx_hex));
    }, py::arg("multisig_tx_hex"), py::call_guard<py::gil_scoped_release>())
    .def("submit_multisig_tx_hex", [](PyMoneroWallet& self, const std::string& signed_multisig_tx_hex) {
      MONERO_CATCH_AND_RETHROW(self.submit_multisig_tx_hex(signed_multisig_tx_hex));
    }, py::arg("signed_multisig_tx_hex"), py::call_guard<py::gil_scoped_release>())
    .def("change_password", [](PyMoneroWallet& self, const std::string& old_password, const std::string& new_password) {
      MONERO_CATCH_AND_RETHROW(self.change_password(old_password, new_password));
    }, py::arg("old_password"), py::arg("new_password"), py::call_guard<py::gil_scoped_release>())
    .def("move_to", [](PyMoneroWallet& self, const std::string& path, const std::string& password) {
      MONERO_CATCH_AND_RETHROW(self.move_to(path, password));
    }, py::arg("path"), py::arg("password"), py::call_guard<py::gil_scoped_release>())
    .def("save", [](PyMoneroWallet& self) {
      MONERO_CATCH_AND_RETHROW(self.save());
    }, py::call_guard<py::gil_scoped_release>())
    .def("close", [](monero_wallet& self, bool save) {
      MONERO_CATCH_AND_RETHROW(self.close(save));
    }, py::arg("save") = false, py::call_guard<py::gil_scoped_release>())
    .def("is_closed", [](const monero_wallet& self) {
      MONERO_CATCH_AND_RETHROW(self.is_closed());
    }, py::call_guard<py::gil_scoped_release>());

  // monero_wallet_keys
  t.py_monero_wallet_keys
    .def_static("create_wallet_random", [](const monero_wallet_config& config) {
      MONERO_CATCH_AND_RETHROW(monero_wallet_keys::create_wallet_random(config));
    }, py::arg("config"), py::call_guard<py::gil_scoped_release>())
    .def_static("create_wallet_from_seed", [](const monero_wallet_config& config) {
      MONERO_CATCH_AND_RETHROW(monero_wallet_keys::create_wallet_from_seed(config));
    }, py::arg("config"), py::call_guard<py::gil_scoped_release>())
    .def_static("create_wallet_from_keys", [](const monero_wallet_config& config) {
      MONERO_CATCH_AND_RETHROW(monero_wallet_keys::create_wallet_from_keys(config));
    }, py::arg("config"), py::call_guard<py::gil_scoped_release>())
    .def_static("get_seed_languages", []() {
      MONERO_CATCH_AND_RETHROW(monero_wallet_keys::get_seed_languages());
    }, py::call_guard<py::gil_scoped_release>());

  // monero_wallet_full
  t.py_monero_wallet_full
    .def_static("wallet_exists", [](const std::string& path) {
      MONERO_CATCH_AND_RETHROW(monero_wallet_full::wallet_exists(path));
    }, py::arg("path"), py::call_guard<py::gil_scoped_release>())
    .def_static("open_wallet", [](const std::string& path, const std::string& password, monero_network_type nettype, bool regtest) {
      MONERO_CATCH_AND_RETHROW(monero_wallet_full::open_wallet(path, password, nettype, regtest));
    }, py::arg("path"), py::arg("password"), py::arg("nettype"), py::arg("regtest") = false, py::call_guard<py::gil_scoped_release>())
    .def_static("open_wallet_data", [](const std::string& password, monero_network_type nettype, const std::string& keys_data, const std::string& cache_data, const std::shared_ptr<monero_rpc_connection>& daemon_connection, bool regtest) {
      MONERO_CATCH_AND_RETHROW(monero_wallet_full::open_wallet_data(password, nettype, keys_data, cache_data, daemon_connection, nullptr, regtest));
    }, py::arg("password"), py::arg("nettype"), py::arg("keys_data"), py::arg("cache_data"), py::arg("daemon_connection") = std::make_shared<monero_rpc_connection>(), py::arg("regtest") = false, py::call_guard<py::gil_scoped_release>())
    .def_static("create_wallet", [](const monero_wallet_config& config) {
      try {
        return monero_wallet_full::create_wallet(config);
      } catch(const std::exception& ex) {
        std::string msg = ex.what();
        if (msg.find("file already exists") != std::string::npos && config.m_path != boost::none)
          msg = std::string("Wallet already exists: ") + config.m_path.get();
        throw monero_error(msg);
      }
    }, py::arg("config"), py::call_guard<py::gil_scoped_release>())
    .def_static("get_seed_languages", []() {
      MONERO_CATCH_AND_RETHROW(monero_wallet_full::get_seed_languages());
    }, py::call_guard<py::gil_scoped_release>())
    .def("get_keys_file_buffer", [](monero_wallet_full& self, std::string& password, bool view_only) {
      MONERO_CATCH_AND_RETHROW(self.get_keys_file_buffer(password, view_only));
    }, py::arg("password"), py::arg("view_only"), py::call_guard<py::gil_scoped_release>())
    .def("get_cache_file_buffer", [](monero_wallet_full& self) {
      MONERO_CATCH_AND_RETHROW(self.get_cache_file_buffer());
    }, py::call_guard<py::gil_scoped_release>());

  // monero_wallet_light
  t.py_monero_wallet_light
    .def_static("wallet_exists", [](const std::string& primary_address, const std::string& private_view_key, const std::shared_ptr<monero_rpc_connection>& rpc) {
      MONERO_CATCH_AND_RETHROW(monero_wallet_light::wallet_exists(primary_address, private_view_key, rpc));
    }, py::arg("primary_address"), py::arg("private_view_key"), py::arg("rpc"), py::call_guard<py::gil_scoped_release>())
    .def_static("wallet_exists", [](const monero_wallet_config& config, const std::shared_ptr<monero_rpc_connection>& rpc) {
      MONERO_CATCH_AND_RETHROW(monero_wallet_light::wallet_exists(config, rpc));
    }, py::arg("config"), py::arg("rpc"), py::call_guard<py::gil_scoped_release>())
    .def_static("open_wallet", [](const monero_wallet_config& config, const std::shared_ptr<monero_rpc_connection>& rpc) {
      MONERO_CATCH_AND_RETHROW(monero_wallet_light::open_wallet(config, rpc));
    }, py::arg("config"), py::arg("rpc"), py::call_guard<py::gil_scoped_release>())
    .def_static("create_wallet", [](const monero_wallet_config& config, const std::shared_ptr<monero_rpc_connection>& rpc) {
      MONERO_CATCH_AND_RETHROW(monero_wallet_light::create_wallet(config, rpc));
    }, py::arg("config"), py::arg("rpc"), py::call_guard<py::gil_scoped_release>())
    .def("get_rpc_connection", [](monero_wallet_rpc& self) {
      MONERO_CATCH_AND_RETHROW(self.get_rpc_connection());
    }, py::call_guard<py::gil_scoped_release>());

  // monero_wallet_rpc
  t.py_monero_wallet_rpc
    .def(py::init<const std::shared_ptr<monero_rpc_connection>&>(), py::arg("rpc_connection"), py::call_guard<py::gil_scoped_release>())
    .def(py::init<const std::string&, const std::string&, const std::string&, const std::string&, const std::string&, const boost::optional<uint32_t>&>(), py::arg("uri") = "", py::arg("username") = "", py::arg("password") = "", py::arg("proxy_uri") = "", py::arg("zmq_uri") = "", py::arg("timeout_ms") = py::none(), py::call_guard<py::gil_scoped_release>())
    .def("create_wallet", [](monero_wallet_rpc& self, const std::shared_ptr<monero_wallet_config>& config) {
      MONERO_CATCH_AND_RETHROW(self.create_wallet(config));
    }, py::arg("config"), py::call_guard<py::gil_scoped_release>())
    .def("open_wallet", [](monero_wallet_rpc& self, const std::shared_ptr<monero_wallet_config>& config) {
      MONERO_CATCH_AND_RETHROW(self.open_wallet(config));
    }, py::arg("config"), py::call_guard<py::gil_scoped_release>())
    .def("open_wallet", [](monero_wallet_rpc& self, const std::string& name, const std::string& password) {
      MONERO_CATCH_AND_RETHROW(self.open_wallet(name, password));
    }, py::arg("name"), py::arg("password"), py::call_guard<py::gil_scoped_release>())
    .def("get_seed_languages", [](monero_wallet_rpc& self) {
      MONERO_CATCH_AND_RETHROW(self.get_seed_languages());
    }, py::call_guard<py::gil_scoped_release>())
    .def("get_rpc_connection", [](monero_wallet_rpc& self) {
      MONERO_CATCH_AND_RETHROW(self.get_rpc_connection());
    }, py::call_guard<py::gil_scoped_release>())
    // this because of function hiding
    .def("set_daemon_connection", [](PyMoneroWallet& self, const std::shared_ptr<monero_rpc_connection>& connection) {
      MONERO_CATCH_AND_RETHROW(self.set_daemon_connection(connection));
    }, py::arg("connection"), py::call_guard<py::gil_scoped_release>())
     .def("set_daemon_connection", [](PyMoneroWallet& self, const std::string& uri, const std::string& username, const std::string& password, const std::string& proxy) {
      MONERO_CATCH_AND_RETHROW(self.set_daemon_connection(uri, username, password, proxy));
    }, py::arg("uri"), py::arg("username") = "", py::arg("password") = "", py::arg("proxy") = "", py::call_guard<py::gil_scoped_release>())
    .def("set_daemon_connection", [](monero_wallet_rpc& self, const std::shared_ptr<monero_rpc_connection>& connection, bool is_trusted, const boost::optional<ssl_options>& ssl_options) {
      MONERO_CATCH_AND_RETHROW(self.set_daemon_connection(connection, is_trusted, ssl_options));
    }, py::arg("connection"), py::arg("is_trusted"), py::arg("ssl_options"), py::call_guard<py::gil_scoped_release>())
    .def("stop", [](monero_wallet_rpc& self) {
      MONERO_CATCH_AND_RETHROW(self.stop());
    }, py::call_guard<py::gil_scoped_release>());

  // tx height comparator
  t.py_tx_height_comparator
    .def_static("compare", [](const std::shared_ptr<monero_tx>& tx1, const std::shared_ptr<monero_tx>& tx2) {
      monero_tx_height_comparator tx_comp;
      MONERO_CATCH_AND_RETHROW(tx_comp(tx1, tx2));
    }, py::arg("tx1"), py::arg("tx2"));

  // incoming transfer comparator
  t.py_incoming_transfer_comparator
    .def_static("compare", [](const monero_incoming_transfer& t1, const monero_incoming_transfer& t2){
      monero_incoming_transfer_comparator tr_comp;
      MONERO_CATCH_AND_RETHROW(tr_comp(t1, t2));
    }, py::arg("transfer1"), py::arg("transfer2"));

  // output comparator
  t.py_output_comparator
    .def_static("compare", [](const monero_output_wallet& o1, const monero_output_wallet& o2) {
      monero_output_comparator out_comp;
      MONERO_CATCH_AND_RETHROW(out_comp(o1, o2));
    }, py::arg("output1"), py::arg("output2"));

}
