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

void py_monero_bind_vectors_and_maps(py::module_& m) {

  py::bind_vector<VectorInt>(m, "VectorInt")
    .def("copy", [](const VectorInt& v) {
        return VectorInt(v);
    });
  py::bind_vector<VectorUint8>(m, "VectorUint8")
    .def("copy", [](const VectorUint8& v) {
        return VectorUint8(v);
    });
  py::bind_vector<VectorUint32>(m, "VectorUint32")
    .def("copy", [](const VectorUint32& v) {
        return VectorUint32(v);
    });
  py::bind_vector<VectorUint64>(m, "VectorUint64")
    .def("copy", [](const VectorUint64& v) {
        return VectorUint64(v);
    });
  py::bind_vector<VectorString>(m, "VectorString")
    .def("copy", [](const VectorString& v) {
        return VectorString(v);
    });
  py::bind_vector<std::vector<std::shared_ptr<monero_account_tag>>>(m, "VectorMoneroAccountTagPtr")
    .def("copy", [](const std::vector<std::shared_ptr<monero_account_tag>>& v) {
        return std::vector<std::shared_ptr<monero_account_tag>>(v);
    });
  py::bind_vector<std::vector<std::shared_ptr<monero_key_image>>>(m, "VectorKeyImagePtr")
    .def("copy", [](const std::vector<std::shared_ptr<monero_key_image>>& v) {
        return std::vector<std::shared_ptr<monero_key_image>>(v);
    });
  py::bind_vector<std::vector<std::shared_ptr<monero_block>>>(m, "VectorMoneroBlock")
    .def("copy", [](const std::vector<std::shared_ptr<monero_block>>& v) {
        return std::vector<std::shared_ptr<monero_block>>(v);
    });
  py::bind_vector<std::vector<std::shared_ptr<monero_block_header>>>(m, "VectorMoneroBlockHeader")
    .def("copy", [](const std::vector<std::shared_ptr<monero_block_header>>& v) {
        return std::vector<std::shared_ptr<monero_block_header>>(v);
    });
  py::bind_vector<VectorMoneroTx>(m, "VectorMoneroTx")
    .def("sort", [](VectorMoneroTx &v) {
        std::sort(v.begin(), v.end(), monero_tx_height_comparator());
    })
    .def("copy", [](const VectorMoneroTx& v) {
        return VectorMoneroTx(v);
    });
  py::bind_vector<VectorMoneroTxWallet>(m, "VectorMoneroTxWallet")
    .def("sort", [](VectorMoneroTxWallet &v) {
        std::sort(v.begin(), v.end(), monero_tx_height_comparator());
    })
    .def("copy", [](const VectorMoneroTxWallet& v) {
        return VectorMoneroTxWallet(v);
    });
  py::bind_vector<std::vector<std::shared_ptr<monero_output>>>(m, "VectorMoneroOutput")
    .def("copy", [](const std::vector<std::shared_ptr<monero_output>>& v) {
        return std::vector<std::shared_ptr<monero_output>>(v);
    });
  py::bind_vector<std::vector<std::shared_ptr<monero_output_wallet>>>(m, "VectorMoneroOutputWallet")
    .def("copy", [](const std::vector<std::shared_ptr<monero_output_wallet>>& v) {
        return std::vector<std::shared_ptr<monero_output_wallet>>(v);
    });
  py::bind_vector<std::vector<std::shared_ptr<monero_transfer>>>(m, "VectorMoneroTransfer")
    .def("copy", [](const std::vector<std::shared_ptr<monero_transfer>>& v) {
        return std::vector<std::shared_ptr<monero_transfer>>(v);
    });
  py::bind_vector<VectorMoneroIncomingTransfer>(m, "VectorMoneroIncomingTransfer")
    .def("sort", [](VectorMoneroIncomingTransfer &v) {
        std::sort(v.begin(), v.end(), monero_incoming_transfer_comparator());
    })
    .def("copy", [](const VectorMoneroIncomingTransfer& v) {
        return VectorMoneroIncomingTransfer(v);
    });
  py::bind_vector<VectorMoneroOutgoingTransfer>(m, "VectorMoneroOutgoingTransfer")
    .def("copy", [](const VectorMoneroOutgoingTransfer& v) {
        return VectorMoneroOutgoingTransfer(v);
    });
  py::bind_vector<VectorMoneroSubaddress>(m, "VectorMoneroSubaddress")
    .def("copy", [](const VectorMoneroSubaddress& v) {
        return VectorMoneroSubaddress(v);
    });
  py::bind_vector<VectorMoneroDestination>(m, "VectorMoneroDestination")
    .def("copy", [](const VectorMoneroDestination& v) {
        return VectorMoneroDestination(v);
    });

  py::implicitly_convertible<py::iterable, VectorInt>();
  py::implicitly_convertible<py::iterable, VectorUint8>();
  py::implicitly_convertible<py::iterable, VectorUint32>();
  py::implicitly_convertible<py::iterable, VectorUint64>();
  py::implicitly_convertible<py::iterable, std::vector<std::string>>();
  py::implicitly_convertible<py::iterable, std::vector<std::shared_ptr<monero_account_tag>>>();
  py::implicitly_convertible<py::iterable, std::vector<std::shared_ptr<monero_key_image>>>();
  py::implicitly_convertible<py::iterable, std::vector<std::shared_ptr<monero_block>>>();
  py::implicitly_convertible<py::iterable, std::vector<std::shared_ptr<monero_block_header>>>();
  py::implicitly_convertible<py::iterable, VectorMoneroTx>();
  py::implicitly_convertible<py::iterable, VectorMoneroTxWallet>();
  py::implicitly_convertible<py::iterable, std::vector<std::shared_ptr<monero_output>>>();
  py::implicitly_convertible<py::iterable, std::vector<std::shared_ptr<monero_output_wallet>>>();
  py::implicitly_convertible<py::iterable, std::vector<std::shared_ptr<monero_transfer>>>();
  py::implicitly_convertible<py::iterable, VectorMoneroIncomingTransfer>();
  py::implicitly_convertible<py::iterable, std::vector<std::shared_ptr<monero_outgoing_transfer>>>();
  py::implicitly_convertible<py::iterable, std::vector<monero_subaddress>>();
  py::implicitly_convertible<py::iterable, std::vector<std::shared_ptr<monero_destination>>>();

}

void py_monero_bind_errors_and_enums(py::module_& m) {
  // bind maps
  py::bind_map<std::map<uint64_t, uint64_t>>(m, "UInt64Map");

  // monero_error
  py::exception<monero_error> pyMoneroError(m, "MoneroError");

  // python subclass
  py::exec(R"(
  class MoneroRpcError(MoneroError):
      def __init__(self, message, code=-1):
          super().__init__(message)
          self.code = code
  )", m.attr("__dict__"));

  py::register_exception_translator([](std::exception_ptr p) {
    try {
      if (p) std::rethrow_exception(p);
    }
    catch (const monero_rpc_error& e) {
      py::object cls = py::module_::import("monero").attr("MoneroRpcError");
      py::object exc = cls(e.what(), e.code);
      PyErr_SetObject(cls.ptr(), exc.ptr());
    }
  });

  // enum monero_network_type
  py::enum_<monero_network_type>(m, "MoneroNetworkType")
    .value("MAINNET", monero_network_type::MAINNET)
    .value("TESTNET", monero_network_type::TESTNET)
    .value("STAGENET", monero_network_type::STAGENET);

  // enum monero_connection_type
  py::enum_<monero_connection_type>(m, "MoneroConnectionType")
    .value("INVALID", monero_connection_type::INVALID)
    .value("IPV4", monero_connection_type::IPV4)
    .value("IPV6", monero_connection_type::IPV6)
    .value("TOR", monero_connection_type::TOR)
    .value("I2P", monero_connection_type::I2P);

  // enum monero_key_image_spent_status
  py::enum_<monero_key_image_spent_status>(m, "MoneroKeyImageSpentStatus")
    .value("NOT_SPENT", monero_key_image_spent_status::NOT_SPENT)
    .value("CONFIRMED", monero_key_image_spent_status::CONFIRMED)
    .value("TX_POOL", monero_key_image_spent_status::TX_POOL);

  // enum address_type
  py::enum_<monero_address_type>(m, "MoneroAddressType")
    .value("PRIMARY_ADDRESS", monero_address_type::PRIMARY_ADDRESS)
    .value("INTEGRATED_ADDRESS", monero_address_type::INTEGRATED_ADDRESS)
    .value("SUBADDRESS", monero_address_type::SUBADDRESS);

  // enum monero_tx_priority
  py::enum_<monero_tx_priority>(m, "MoneroTxPriority")
    .value("DEFAULT", monero_tx_priority::DEFAULT)
    .value("UNIMPORTANT", monero_tx_priority::UNIMPORTANT)
    .value("NORMAL", monero_tx_priority::NORMAL)
    .value("ELEVATED", monero_tx_priority::ELEVATED);

  // enum monero_message_signature_type
  py::enum_<monero_message_signature_type>(m, "MoneroMessageSignatureType")
    .value("SIGN_WITH_SPEND_KEY", monero_message_signature_type::SIGN_WITH_SPEND_KEY)
    .value("SIGN_WITH_VIEW_KEY", monero_message_signature_type::SIGN_WITH_VIEW_KEY);

}

void py_monero_bind_common(py::module_& m, PyMoneroTypes& t) {
  // serializable_struct
  t.py_serializable_struct
    .def("serialize", [](serializable_struct& self) {
      MONERO_CATCH_AND_RETHROW(self.serialize());
    });

  // monero_rpc_payment_info
  t.py_monero_rpc_payment_info
    .def(py::init<>())
    .def_readwrite("credits", &monero_rpc_payment_info::m_credits)
    .def_readwrite("top_block_hash", &monero_rpc_payment_info::m_top_block_hash);

  // monero_ssl_options
  t.py_monero_ssl_options
    .def(py::init<>())
    .def_readwrite("ssl_private_key_path", &ssl_options::m_ssl_private_key_path)
    .def_readwrite("ssl_certificate_path", &ssl_options::m_ssl_certificate_path)
    .def_readwrite("ssl_ca_file", &ssl_options::m_ssl_ca_file)
    .def_readwrite("ssl_allowed_fingerprints", &ssl_options::m_ssl_allowed_fingerprints)
    .def_readwrite("ssl_allow_any_cert", &ssl_options::m_ssl_allow_any_cert);

  // monero_rpc_connection
  t.py_monero_rpc_connection
    .def(py::init<const std::string&, const std::string&, const::std::string&, const std::string&, const std::string&, int, const boost::optional<uint32_t>&>(), py::arg("uri") = "", py::arg("username") = "", py::arg("password") = "", py::arg("proxy_uri") = "", py::arg("zmq_uri") = "", py::arg("priority") = 0, py::arg("timeout_ms") = py::none())
    .def(py::init<const monero_rpc_connection&>(), py::arg("rpc"))
    .def_static("compare", [](int p1, int p2) {
      MONERO_CATCH_AND_RETHROW(monero_rpc_connection::compare(p1, p2));
    }, py::arg("p1"), py::arg("p2"))
    .def_property("uri",
      [](const monero_rpc_connection& self) { return self.m_uri; },
      [](monero_rpc_connection& self, const boost::optional<std::string>& val) {
        // normalize uri
        if (val != boost::none && !val->empty()) {
          self.m_uri = val;
        } else self.m_uri = boost::none;
      })
    .def_readonly("username", &monero_rpc_connection::m_username)
    .def_readonly("password", &monero_rpc_connection::m_password)
    .def_property_readonly("response_time",
      [](const monero_rpc_connection& self) { return self.m_response_time; })
    .def_property("proxy_uri",
      [](const monero_rpc_connection& self) { return self.m_proxy_uri; },
      [](monero_rpc_connection& self, const boost::optional<std::string>& val) {
        // normalize proxy uri
        if (val != boost::none && !val->empty()) {
          self.m_proxy_uri = val;
        } else self.m_proxy_uri = boost::none;
      })
    .def_property("zmq_uri",
      [](const monero_rpc_connection& self) { return self.m_zmq_uri; },
      [](monero_rpc_connection& self, const boost::optional<std::string>& val) {
        // normalize zmq uri
        if (val != boost::none && !val->empty()) {
          self.m_zmq_uri = val;
        } else self.m_zmq_uri = boost::none;
      })
    .def_property("priority",
      [](const monero_rpc_connection& self) { return self.m_priority; },
      [](monero_rpc_connection& self, int val) { self.m_priority = val; })
    .def_property("timeout_ms",
      [](const monero_rpc_connection& self) { return self.m_timeout_ms; },
      [](monero_rpc_connection& self, uint64_t val) { self.m_timeout_ms = val; })
    .def("set_attribute", [](monero_rpc_connection& self, const std::string& key, const std::string& value) {
      MONERO_CATCH_AND_RETHROW(self.set_attribute(key, value));
    }, py::arg("key"), py::arg("value"))
    .def("get_attribute", [](const monero_rpc_connection& self, const std::string& key) {
      MONERO_CATCH_AND_RETHROW(self.get_attribute(key));
    }, py::arg("key"))
    .def("set_credentials", [](monero_rpc_connection& self, const std::string& username, const std::string& password) {
      MONERO_CATCH_AND_RETHROW(self.set_credentials(username, password));
    }, py::arg("username"), py::arg("password"), py::call_guard<py::gil_scoped_release>())
    .def("is_onion", [](const monero_rpc_connection& self) {
      MONERO_CATCH_AND_RETHROW(self.is_onion());
    })
    .def("is_i2p", [](const monero_rpc_connection& self) {
      MONERO_CATCH_AND_RETHROW(self.is_i2p());
    })
    .def("is_online", [](const monero_rpc_connection& self) {
      MONERO_CATCH_AND_RETHROW(self.is_online());
    })
    .def("is_authenticated", [](const monero_rpc_connection& self) {
      MONERO_CATCH_AND_RETHROW(self.is_authenticated());
    })
    .def("is_connected", [](const monero_rpc_connection& self) {
      MONERO_CATCH_AND_RETHROW(self.is_connected());
    })
    .def("check_connection", [](monero_rpc_connection& self, const boost::optional<uint32_t>& timeout_ms) {
      MONERO_CATCH_AND_RETHROW(self.check_connection(timeout_ms));
    }, py::arg("timeout_ms") = py::none(), py::call_guard<py::gil_scoped_release>())
    .def("send_json_request", [](monero_rpc_connection& self, const std::string &method, const boost::optional<py::object>& parameters) {
      monero_rpc_request request(method, std::make_shared<PyMoneroRequestParams>(parameters));
      auto response = self.send_json_request(request);
      boost::optional<py::object> res;
      if (response.m_result != boost::none) res = PyGenUtils::ptree_to_pyobject(*response.m_result);
      return res;
    }, py::arg("method"), py::arg("parameters") = py::none())
    .def("send_path_request", [](monero_rpc_connection& self, const std::string &method, const boost::optional<py::object>& parameters) {
      monero_rpc_request request(method, std::make_shared<PyMoneroRequestParams>(parameters));
      auto response = self.send_path_request(request);
      boost::optional<py::object> res;
      if (response.m_response != boost::none) res = PyGenUtils::ptree_to_pyobject(*response.m_response);
      return res;
    }, py::arg("method"), py::arg("parameters") = py::none())
    .def("send_binary_request", [](monero_rpc_connection& self, const std::string &method, const boost::optional<py::object>& parameters) {
      monero_rpc_request request(method, std::make_shared<PyMoneroRequestParams>(parameters), false);
      auto response = self.send_binary_request(request);
      boost::optional<py::bytes> result;

      if (response.m_binary != boost::none && !response.m_binary->empty()) {
        result = py::bytes(response.m_binary.get());
      }
      // convert binary string to py::bytes
      return result;
    }, py::arg("method"), py::arg("parameters") = py::none());
}
