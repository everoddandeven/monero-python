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
#include "common/monero_error.h"
#include "daemon/py_monero_daemon.h"
#include "daemon/monero_daemon_rpc.h"
#include "wallet/py_monero_wallet.h"
#include "wallet/monero_wallet_rpc.h"
#include "wallet/monero_wallet_keys.h"
#include "wallet/monero_wallet_full.h"
#include "utils/py_monero_utils.h"

#define MONERO_CATCH_AND_RETHROW(expr)         \
  try {                                        \
    return expr;                               \
  } catch (const monero_rpc_error& e) {        \
    throw;                                     \
  } catch (const monero_error& e) {           \
    throw;                                     \
  }                                            \
  catch (const std::exception& e) {            \
    throw monero_error(e.what());             \
  }

using VectorInt = std::vector<int>;
using VectorUint8 = std::vector<uint8_t>;
using VectorUint32 = std::vector<uint32_t>;
using VectorUint64 = std::vector<uint64_t>;
using VectorString = std::vector<std::string>;

using VectorMoneroOutgoingTransfer = std::vector<std::shared_ptr<monero_outgoing_transfer>>;
using VectorMoneroIncomingTransfer = std::vector<std::shared_ptr<monero_incoming_transfer>>;
using VectorMoneroTx = std::vector<std::shared_ptr<monero_tx>>;
using VectorMoneroTxWallet = std::vector<std::shared_ptr<monero_tx_wallet>>;
using VectorMoneroSubaddress = std::vector<monero_subaddress>;
using VectorMoneroDestination = std::vector<std::shared_ptr<monero_destination>>;


PYBIND11_MAKE_OPAQUE(VectorInt);
PYBIND11_MAKE_OPAQUE(VectorUint8);
PYBIND11_MAKE_OPAQUE(VectorUint32);
PYBIND11_MAKE_OPAQUE(VectorUint64);


PYBIND11_MODULE(monero, m) {
  m.doc() = "";

  auto py_serializable_struct = py::class_<serializable_struct, std::shared_ptr<serializable_struct>>(m, "SerializableStruct");
  auto py_monero_rpc_payment_info =py::class_<monero_rpc_payment_info, serializable_struct, std::shared_ptr<monero_rpc_payment_info>>(m, "MoneroRpcPaymentInfo");
  auto py_monero_rpc_connection = py::class_<monero_rpc_connection, serializable_struct, std::shared_ptr<monero_rpc_connection>>(m, "MoneroRpcConnection");

  auto py_monero_ssl_options = py::class_<ssl_options, serializable_struct, std::shared_ptr<ssl_options>>(m, "SslOptions");
  auto py_monero_version = py::class_<monero_version, serializable_struct, std::shared_ptr<monero_version>>(m, "MoneroVersion");
  auto py_monero_block_header = py::class_<monero_block_header, serializable_struct, std::shared_ptr<monero_block_header>>(m, "MoneroBlockHeader");
  auto py_monero_block = py::class_<monero_block, monero_block_header, std::shared_ptr<monero_block>>(m, "MoneroBlock");
  auto py_monero_tx = py::class_<monero_tx, serializable_struct, std::shared_ptr<monero_tx>>(m, "MoneroTx");
  auto py_monero_key_image = py::class_<monero_key_image, serializable_struct, std::shared_ptr<monero_key_image>>(m, "MoneroKeyImage");
  auto py_monero_output = py::class_<monero_output, serializable_struct, std::shared_ptr<monero_output>>(m, "MoneroOutput");
  auto py_monero_wallet_config = py::class_<monero_wallet_config, serializable_struct, std::shared_ptr<monero_wallet_config>>(m, "MoneroWalletConfig");
  auto py_monero_subaddress = py::class_<monero_subaddress, serializable_struct, std::shared_ptr<monero_subaddress>>(m, "MoneroSubaddress");
  auto py_monero_sync_result = py::class_<monero_sync_result, serializable_struct, std::shared_ptr<monero_sync_result>>(m, "MoneroSyncResult");
  auto py_monero_account = py::class_<monero_account, serializable_struct, std::shared_ptr<monero_account>>(m, "MoneroAccount");
  auto py_monero_account_tag = py::class_<monero_account_tag, serializable_struct, std::shared_ptr<monero_account_tag>>(m, "MoneroAccountTag");
  auto py_monero_destination = py::class_<monero_destination, serializable_struct, std::shared_ptr<monero_destination>>(m, "MoneroDestination");
  auto py_monero_transfer = py::class_<monero_transfer, serializable_struct, PyMoneroTransfer, std::shared_ptr<monero_transfer>>(m, "MoneroTransfer");
  auto py_monero_incoming_transfer = py::class_<monero_incoming_transfer, monero_transfer, std::shared_ptr<monero_incoming_transfer>>(m, "MoneroIncomingTransfer");
  auto py_monero_outgoing_transfer = py::class_<monero_outgoing_transfer, monero_transfer, std::shared_ptr<monero_outgoing_transfer>>(m, "MoneroOutgoingTransfer");
  auto py_monero_transfer_query = py::class_<monero_transfer_query, monero_transfer, std::shared_ptr<monero_transfer_query>>(m, "MoneroTransferQuery");
  auto py_monero_output_wallet = py::class_<monero_output_wallet, monero_output, std::shared_ptr<monero_output_wallet>>(m, "MoneroOutputWallet");
  auto py_monero_output_query = py::class_<monero_output_query, monero_output_wallet, std::shared_ptr<monero_output_query>>(m, "MoneroOutputQuery");
  auto py_monero_tx_wallet = py::class_<monero_tx_wallet, monero_tx, std::shared_ptr<monero_tx_wallet>>(m, "MoneroTxWallet");
  auto py_monero_tx_query = py::class_<monero_tx_query, monero_tx_wallet, std::shared_ptr<monero_tx_query>>(m, "MoneroTxQuery");
  auto py_monero_tx_set = py::class_<monero_tx_set, serializable_struct, std::shared_ptr<monero_tx_set>>(m, "MoneroTxSet");
  auto py_monero_integrated_address = py::class_<monero_integrated_address,  serializable_struct, std::shared_ptr<monero_integrated_address>>(m, "MoneroIntegratedAddress");
  auto py_monero_decoded_address = py::class_<monero_decoded_address, serializable_struct, std::shared_ptr<monero_decoded_address>>(m, "MoneroDecodedAddress");
  auto py_monero_tx_config = py::class_<monero_tx_config, serializable_struct, std::shared_ptr<monero_tx_config>>(m, "MoneroTxConfig");
  auto py_monero_key_image_export_result = py::class_<monero_key_image_export_result, serializable_struct, std::shared_ptr<monero_key_image_export_result>>(m, "MoneroKeyImageExportResult");
  auto py_monero_key_image_import_result = py::class_<monero_key_image_import_result, serializable_struct, std::shared_ptr<monero_key_image_import_result>>(m, "MoneroKeyImageImportResult");
  auto py_monero_message_signature_result = py::class_<monero_message_signature_result,  serializable_struct, std::shared_ptr<monero_message_signature_result>>(m, "MoneroMessageSignatureResult");
  auto py_monero_check = py::class_<monero_check,  serializable_struct, std::shared_ptr<monero_check>>(m, "MoneroCheck");
  auto py_monero_check_tx = py::class_<monero_check_tx, monero_check, std::shared_ptr<monero_check_tx>>(m, "MoneroCheckTx");
  auto py_monero_check_reserve = py::class_<monero_check_reserve, monero_check, std::shared_ptr<monero_check_reserve>>(m, "MoneroCheckReserve");
  auto py_monero_multisig_info = py::class_<monero_multisig_info, serializable_struct, std::shared_ptr<monero_multisig_info>>(m, "MoneroMultisigInfo");
  auto py_monero_multisig_init_result = py::class_<monero_multisig_init_result, serializable_struct, std::shared_ptr<monero_multisig_init_result>>(m, "MoneroMultisigInitResult");
  auto py_monero_multisig_sign_result = py::class_<monero_multisig_sign_result, serializable_struct, std::shared_ptr<monero_multisig_sign_result>>(m, "MoneroMultisigSignResult");
  auto py_monero_address_book_entry = py::class_<monero_address_book_entry, serializable_struct, std::shared_ptr<monero_address_book_entry>>(m, "MoneroAddressBookEntry");
  auto py_monero_wallet_listener = py::class_<monero_wallet_listener, PyMoneroWalletListener, std::shared_ptr<monero_wallet_listener>>(m, "MoneroWalletListener");
  auto py_monero_daemon_listener = py::class_<monero_daemon_listener, PyMoneroDaemonListener, std::shared_ptr<monero_daemon_listener>>(m, "MoneroDaemonListener");
  auto py_monero_daemon = py::class_<monero_daemon, std::shared_ptr<monero_daemon>>(m, "MoneroDaemon");
  auto py_monero_daemon_rpc = py::class_<monero_daemon_rpc, monero_daemon, std::shared_ptr<monero_daemon_rpc>>(m, "MoneroDaemonRpc");
  auto py_monero_wallet = py::class_<monero_wallet, PyMoneroWallet, std::shared_ptr<monero_wallet>>(m, "MoneroWallet");
  auto py_monero_wallet_keys = py::class_<monero_wallet_keys, monero_wallet, std::shared_ptr<monero_wallet_keys>>(m, "MoneroWalletKeys");
  auto py_monero_wallet_full = py::class_<monero_wallet_full, monero_wallet, std::shared_ptr<monero_wallet_full>>(m, "MoneroWalletFull");
  auto py_monero_wallet_rpc = py::class_<monero_wallet_rpc, monero_wallet, std::shared_ptr<monero_wallet_rpc>>(m, "MoneroWalletRpc");
  auto py_monero_utils = py::class_<PyMoneroUtils>(m, "MoneroUtils");

  auto py_tx_height_comparator = py::class_<monero_tx_height_comparator, std::shared_ptr<monero_tx_height_comparator>>(m, "TxHeightComparator");
  auto py_incoming_transfer_comparator = py::class_<monero_incoming_transfer_comparator, std::shared_ptr<monero_incoming_transfer_comparator>>(m, "IncomingTransferComparator");
  auto py_output_comparator = py::class_<monero_output_comparator, std::shared_ptr<monero_output_comparator>>(m, "OutputComparator");

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

  // serializable_struct
  py_serializable_struct
    .def("serialize", [](serializable_struct& self) {
      MONERO_CATCH_AND_RETHROW(self.serialize());
    });

  // monero_rpc_payment_info
  py_monero_rpc_payment_info
    .def(py::init<>())
    .def_readwrite("credits", &monero_rpc_payment_info::m_credits)
    .def_readwrite("top_block_hash", &monero_rpc_payment_info::m_top_block_hash);

  // monero_ssl_options
  py_monero_ssl_options
    .def(py::init<>())
    .def_readwrite("ssl_private_key_path", &ssl_options::m_ssl_private_key_path)
    .def_readwrite("ssl_certificate_path", &ssl_options::m_ssl_certificate_path)
    .def_readwrite("ssl_ca_file", &ssl_options::m_ssl_ca_file)
    .def_readwrite("ssl_allowed_fingerprints", &ssl_options::m_ssl_allowed_fingerprints)
    .def_readwrite("ssl_allow_any_cert", &ssl_options::m_ssl_allow_any_cert);

  // monero_fee_estimate
  py::class_<monero_fee_estimate, serializable_struct, std::shared_ptr<monero_fee_estimate>>(m, "MoneroFeeEstimate")
    .def(py::init<>())
    .def_readwrite("fee", &monero_fee_estimate::m_fee)
    .def_readwrite("fees", &monero_fee_estimate::m_fees)
    .def_readwrite("quantization_mask", &monero_fee_estimate::m_quantization_mask);

  // monero_tx_backlog_entry
  py::class_<monero_tx_backlog_entry, std::shared_ptr<monero_tx_backlog_entry>>(m, "MoneroTxBacklogEntry")
    .def(py::init<>());

  // monero_version
  py_monero_version
    .def(py::init<>())
    .def_readwrite("number", &monero_version::m_number)
    .def_readwrite("is_release", &monero_version::m_is_release);

  // monero_rpc_connection
  py_monero_rpc_connection
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

  // monero_block_header
  py_monero_block_header
    .def(py::init<>())
    .def("__str__", &monero_block_header::serialize)
    .def_readwrite("hash", &monero_block_header::m_hash)
    .def_readwrite("height", &monero_block_header::m_height)
    .def_readwrite("timestamp", &monero_block_header::m_timestamp)
    .def_readwrite("size", &monero_block_header::m_size)
    .def_readwrite("weight", &monero_block_header::m_weight)
    .def_readwrite("long_term_weight", &monero_block_header::m_long_term_weight)
    .def_readwrite("depth", &monero_block_header::m_depth)
    .def_readwrite("difficulty_high", &monero_block_header::m_difficulty_high)
    .def_readwrite("difficulty_low", &monero_block_header::m_difficulty_low)
    .def_readwrite("cumulative_difficulty_high", &monero_block_header::m_cumulative_difficulty_high)
    .def_readwrite("cumulative_difficulty_low", &monero_block_header::m_cumulative_difficulty_low)
    .def_readwrite("major_version", &monero_block_header::m_major_version)
    .def_readwrite("minor_version", &monero_block_header::m_minor_version)
    .def_readwrite("nonce", &monero_block_header::m_nonce)
    .def_readwrite("miner_tx_hash", &monero_block_header::m_miner_tx_hash)
    .def_readwrite("num_txs", &monero_block_header::m_num_txs)
    .def_readwrite("orphan_status", &monero_block_header::m_orphan_status)
    .def_readwrite("prev_hash", &monero_block_header::m_prev_hash)
    .def_readwrite("reward", &monero_block_header::m_reward)
    .def_readwrite("pow_hash", &monero_block_header::m_pow_hash)
    .def("copy", [](const std::shared_ptr<monero_block_header>& self) {
      auto tgt = std::make_shared<monero_block_header>();
      MONERO_CATCH_AND_RETHROW(self->copy(self, tgt));
    })
    .def("merge", [](const std::shared_ptr<monero_block_header>& self, const std::shared_ptr<monero_block_header>& other) {
      MONERO_CATCH_AND_RETHROW(self->merge(self, other));
    }, py::arg("other"));

  // monero_block (needs: monero_tx)
  py_monero_block
    .def(py::init<>())
    .def("__str__", &monero_block::serialize)
    .def_readwrite("hex", &monero_block::m_hex)
    .def_readwrite("miner_tx", &monero_block::m_miner_tx)
    .def_readwrite("txs", &monero_block::m_txs)
    .def_readwrite("tx_hashes", &monero_block::m_tx_hashes)
    .def("copy", [](const std::shared_ptr<monero_block>& self) {
      auto tgt = std::make_shared<monero_block>();
      MONERO_CATCH_AND_RETHROW(self->copy(self, tgt));
    })
    .def("merge", [](const std::shared_ptr<monero_block>& self, const std::shared_ptr<monero_block>& other) {
      MONERO_CATCH_AND_RETHROW(self->merge(self, other));
    }, py::arg("other"));

  // monero_block_template
  py::class_<monero_block_template, serializable_struct, std::shared_ptr<monero_block_template>>(m, "MoneroBlockTemplate")
    .def(py::init<>())
    .def_readwrite("block_template_blob", &monero_block_template::m_block_template_blob)
    .def_readwrite("block_hashing_blob", &monero_block_template::m_block_hashing_blob)
    .def_readwrite("difficulty_low", &monero_block_template::m_difficulty_low)
    .def_readwrite("difficulty_high", &monero_block_template::m_difficulty_high)
    .def_readwrite("expected_reward", &monero_block_template::m_expected_reward)
    .def_readwrite("height", &monero_block_template::m_height)
    .def_readwrite("prev_hash", &monero_block_template::m_prev_hash)
    .def_readwrite("reserved_offset", &monero_block_template::m_reserved_offset)
    .def_readwrite("seed_height", &monero_block_template::m_seed_height)
    .def_readwrite("seed_hash", &monero_block_template::m_seed_hash)
    .def_readwrite("next_seed_hash", &monero_block_template::m_next_seed_hash);

  // monero_connection_span
  py::class_<monero_connection_span, serializable_struct, std::shared_ptr<monero_connection_span>>(m, "MoneroConnectionSpan")
    .def(py::init<>())
    .def_readwrite("connection_id", &monero_connection_span::m_connection_id)
    .def_readwrite("num_blocks", &monero_connection_span::m_num_blocks)
    .def_readwrite("remote_address", &monero_connection_span::m_remote_address)
    .def_readwrite("rate", &monero_connection_span::m_rate)
    .def_readwrite("speed", &monero_connection_span::m_speed)
    .def_readwrite("size", &monero_connection_span::m_size)
    .def_readwrite("start_height", &monero_connection_span::m_start_height);

  // monero_peer
  py::class_<monero_peer, serializable_struct, std::shared_ptr<monero_peer>>(m, "MoneroPeer")
    .def(py::init<>())
    .def_readwrite("id", &monero_peer::m_id)
    .def_readwrite("address", &monero_peer::m_address)
    .def_readwrite("host", &monero_peer::m_host)
    .def_readwrite("port", &monero_peer::m_port)
    .def_readwrite("is_online", &monero_peer::m_is_online)
    .def_readwrite("last_seen_timestamp", &monero_peer::m_last_seen_timestamp)
    .def_readwrite("pruning_seed", &monero_peer::m_pruning_seed)
    .def_readwrite("rpc_port", &monero_peer::m_rpc_port)
    .def_readwrite("rpc_credits_per_hash", &monero_peer::m_rpc_credits_per_hash)
    .def_readwrite("hash", &monero_peer::m_hash)
    .def_readwrite("avg_download", &monero_peer::m_avg_download)
    .def_readwrite("avg_upload", &monero_peer::m_avg_upload)
    .def_readwrite("current_download", &monero_peer::m_current_download)
    .def_readwrite("current_upload", &monero_peer::m_current_upload)
    .def_readwrite("height", &monero_peer::m_height)
    .def_readwrite("is_incoming", &monero_peer::m_is_incoming)
    .def_readwrite("live_time", &monero_peer::m_live_time)
    .def_readwrite("is_local_ip", &monero_peer::m_is_local_ip)
    .def_readwrite("is_local_host", &monero_peer::m_is_local_host)
    .def_readwrite("num_receives", &monero_peer::m_num_receives)
    .def_readwrite("num_sends", &monero_peer::m_num_sends)
    .def_readwrite("receive_idle_time", &monero_peer::m_receive_idle_time)
    .def_readwrite("send_idle_time", &monero_peer::m_send_idle_time)
    .def_readwrite("state", &monero_peer::m_state)
    .def_readwrite("num_support_flags", &monero_peer::m_num_support_flags)
    .def_readwrite("connection_type", &monero_peer::m_connection_type);

  // monero_alt_chain
  py::class_<monero_alt_chain, serializable_struct, std::shared_ptr<monero_alt_chain>>(m, "MoneroAltChain")
    .def(py::init<>())
    .def_readwrite("block_hashes", &monero_alt_chain::m_block_hashes)
    .def_readwrite("difficulty_low", &monero_alt_chain::m_difficulty_low)
    .def_readwrite("difficulty_high", &monero_alt_chain::m_difficulty_high)
    .def_readwrite("height", &monero_alt_chain::m_height)
    .def_readwrite("length", &monero_alt_chain::m_length)
    .def_readwrite("main_chain_parent_block_hash", &monero_alt_chain::m_main_chain_parent_block_hash);

  // monero_ban
  py::class_<monero_ban, serializable_struct, std::shared_ptr<monero_ban>>(m, "MoneroBan")
    .def(py::init<>())
    .def_readwrite("host", &monero_ban::m_host)
    .def_readwrite("ip", &monero_ban::m_ip)
    .def_readwrite("is_banned", &monero_ban::m_is_banned)
    .def_readwrite("seconds", &monero_ban::m_seconds);

  // monero_output_distribution_entry
  py::class_<monero_output_distribution_entry, serializable_struct, std::shared_ptr<monero_output_distribution_entry>>(m, "MoneroOutputDistributionEntry")
    .def(py::init<>())
    .def_readwrite("amount", &monero_output_distribution_entry::m_amount)
    .def_readwrite("base", &monero_output_distribution_entry::m_base)
    .def_readwrite("distribution", &monero_output_distribution_entry::m_distribution)
    .def_readwrite("start_height", &monero_output_distribution_entry::m_start_height);

  // monero_output_histogram_entry
  py::class_<monero_output_histogram_entry, serializable_struct, std::shared_ptr<monero_output_histogram_entry>>(m, "MoneroOutputHistogramEntry")
    .def(py::init<>())
    .def_readwrite("amount", &monero_output_histogram_entry::m_amount)
    .def_readwrite("num_instances", &monero_output_histogram_entry::m_num_instances)
    .def_readwrite("unlocked_instances", &monero_output_histogram_entry::m_unlocked_instances)
    .def_readwrite("recent_instances", &monero_output_histogram_entry::m_recent_instances);

  // monero_hard_fork_info
  py::class_<monero_hard_fork_info, monero_rpc_payment_info, std::shared_ptr<monero_hard_fork_info>>(m, "MoneroHardForkInfo")
    .def(py::init<>())
    .def_readwrite("earliest_height", &monero_hard_fork_info::m_earliest_height)
    .def_readwrite("is_enabled", &monero_hard_fork_info::m_is_enabled)
    .def_readwrite("state", &monero_hard_fork_info::m_state)
    .def_readwrite("threshold", &monero_hard_fork_info::m_threshold)
    .def_readwrite("version", &monero_hard_fork_info::m_version)
    .def_readwrite("num_votes", &monero_hard_fork_info::m_num_votes)
    .def_readwrite("window", &monero_hard_fork_info::m_window)
    .def_readwrite("voting", &monero_hard_fork_info::m_voting);

  // monero_prune_result
  py::class_<monero_prune_result, serializable_struct, std::shared_ptr<monero_prune_result>>(m, "MoneroPruneResult")
    .def(py::init<>())
    .def_readwrite("is_pruned", &monero_prune_result::m_is_pruned)
    .def_readwrite("pruning_seed", &monero_prune_result::m_pruning_seed);

  // monero_daemon_sync_info
  py::class_<monero_daemon_sync_info, monero_rpc_payment_info, std::shared_ptr<monero_daemon_sync_info>>(m, "MoneroDaemonSyncInfo")
    .def(py::init<>())
    .def_readwrite("height", &monero_daemon_sync_info::m_height)
    .def_readwrite("peers", &monero_daemon_sync_info::m_peers)
    .def_readwrite("spans", &monero_daemon_sync_info::m_spans)
    .def_readwrite("target_height", &monero_daemon_sync_info::m_target_height)
    .def_readwrite("next_needed_pruning_seed", &monero_daemon_sync_info::m_next_needed_pruning_seed)
    .def_readwrite("overview", &monero_daemon_sync_info::m_overview);

  // monero_daemon_info
  py::class_<monero_daemon_info, monero_rpc_payment_info, std::shared_ptr<monero_daemon_info>>(m, "MoneroDaemonInfo")
    .def(py::init<>())
    .def_readwrite("version", &monero_daemon_info::m_version)
    .def_readwrite("num_alt_blocks", &monero_daemon_info::m_num_alt_blocks)
    .def_readwrite("block_size_limit", &monero_daemon_info::m_block_size_limit)
    .def_readwrite("block_size_median", &monero_daemon_info::m_block_size_median)
    .def_readwrite("block_weight_limit", &monero_daemon_info::m_block_weight_limit)
    .def_readwrite("block_weight_median", &monero_daemon_info::m_block_weight_median)
    .def_readwrite("bootstrap_daemon_address", &monero_daemon_info::m_bootstrap_daemon_address)
    .def_readwrite("difficulty_low", &monero_daemon_info::m_difficulty_low)
    .def_readwrite("difficulty_high", &monero_daemon_info::m_difficulty_high)
    .def_readwrite("cumulative_difficulty_low", &monero_daemon_info::m_cumulative_difficulty_low)
    .def_readwrite("cumulative_difficulty_high", &monero_daemon_info::m_cumulative_difficulty_high)
    .def_readwrite("free_space", &monero_daemon_info::m_free_space)
    .def_readwrite("num_offline_peers", &monero_daemon_info::m_num_offline_peers)
    .def_readwrite("num_online_peers", &monero_daemon_info::m_num_online_peers)
    .def_readwrite("height", &monero_daemon_info::m_height)
    .def_readwrite("height_without_bootstrap", &monero_daemon_info::m_height_without_bootstrap)
    .def_readwrite("network_type", &monero_daemon_info::m_network_type)
    .def_readwrite("is_offline", &monero_daemon_info::m_is_offline)
    .def_readwrite("num_incoming_connections", &monero_daemon_info::m_num_incoming_connections)
    .def_readwrite("num_outgoing_connections", &monero_daemon_info::m_num_outgoing_connections)
    .def_readwrite("num_rpc_connections", &monero_daemon_info::m_num_rpc_connections)
    .def_readwrite("start_timestamp", &monero_daemon_info::m_start_timestamp)
    .def_readwrite("adjusted_timestamp", &monero_daemon_info::m_adjusted_timestamp)
    .def_readwrite("target", &monero_daemon_info::m_target)
    .def_readwrite("target_height", &monero_daemon_info::m_target_height)
    .def_readwrite("num_txs", &monero_daemon_info::m_num_txs)
    .def_readwrite("num_txs_pool", &monero_daemon_info::m_num_txs_pool)
    .def_readwrite("was_bootstrap_ever_used", &monero_daemon_info::m_was_bootstrap_ever_used)
    .def_readwrite("database_size", &monero_daemon_info::m_database_size)
    .def_readwrite("update_available", &monero_daemon_info::m_update_available)
    .def_readwrite("is_busy_syncing", &monero_daemon_info::m_is_busy_syncing)
    .def_readwrite("is_synchronized", &monero_daemon_info::m_is_synchronized)
    .def_readwrite("is_restricted", &monero_daemon_info::m_is_restricted);

  // monero_daemon_update_check_result
  py::class_<monero_daemon_update_check_result, serializable_struct, std::shared_ptr<monero_daemon_update_check_result>>(m, "MoneroDaemonUpdateCheckResult")
    .def(py::init<>())
    .def_readwrite("is_update_available", &monero_daemon_update_check_result::m_is_update_available)
    .def_readwrite("version", &monero_daemon_update_check_result::m_version)
    .def_readwrite("hash", &monero_daemon_update_check_result::m_hash)
    .def_readwrite("auto_uri", &monero_daemon_update_check_result::m_auto_uri)
    .def_readwrite("user_uri", &monero_daemon_update_check_result::m_user_uri);

  // monero_daemon_update_check_result
  py::class_<monero_daemon_update_download_result, monero_daemon_update_check_result, std::shared_ptr<monero_daemon_update_download_result>>(m, "MoneroDaemonUpdateDownloadResult")
    .def(py::init<>())
    .def_readwrite("download_path", &monero_daemon_update_download_result::m_download_path);

  // monero_submit_tx_result
  py::class_<monero_submit_tx_result, monero_rpc_payment_info, std::shared_ptr<monero_submit_tx_result>>(m, "MoneroSubmitTxResult")
    .def(py::init<>())
    .def_readwrite("is_good", &monero_submit_tx_result::m_is_good)
    .def_readwrite("is_relayed", &monero_submit_tx_result::m_is_relayed)
    .def_readwrite("is_double_spend", &monero_submit_tx_result::m_is_double_spend)
    .def_readwrite("is_fee_too_low", &monero_submit_tx_result::m_is_fee_too_low)
    .def_readwrite("is_mixin_too_low", &monero_submit_tx_result::m_is_mixin_too_low)
    .def_readwrite("has_invalid_input", &monero_submit_tx_result::m_has_invalid_input)
    .def_readwrite("has_invalid_output", &monero_submit_tx_result::m_has_invalid_output)
    .def_readwrite("has_too_few_outputs", &monero_submit_tx_result::m_has_too_few_outputs)
    .def_readwrite("is_overspend", &monero_submit_tx_result::m_is_overspend)
    .def_readwrite("is_too_big", &monero_submit_tx_result::m_is_too_big)
    .def_readwrite("sanity_check_failed", &monero_submit_tx_result::m_sanity_check_failed)
    .def_readwrite("reason", &monero_submit_tx_result::m_reason)
    .def_readwrite("is_tx_extra_too_big", &monero_submit_tx_result::m_is_tx_extra_too_big)
    .def_readwrite("is_nonzero_unlock_time", &monero_submit_tx_result::m_is_nonzero_unlock_time);

  // monero_generate_blocks_result
  py::class_<monero_generate_blocks_result, serializable_struct, std::shared_ptr<monero_generate_blocks_result>>(m, "MoneroGenerateBlocksResult")
    .def(py::init<>())
    .def_readwrite("block_hashes", &monero_generate_blocks_result::m_block_hashes)
    .def_readwrite("height", &monero_generate_blocks_result::m_height);

  // monero_tx_pool_stats
  py::class_<monero_tx_pool_stats, serializable_struct, std::shared_ptr<monero_tx_pool_stats>>(m, "MoneroTxPoolStats")
    .def(py::init<>())
    .def_readwrite("num_txs", &monero_tx_pool_stats::m_num_txs)
    .def_readwrite("num_not_relayed", &monero_tx_pool_stats::m_num_not_relayed)
    .def_readwrite("num_failing", &monero_tx_pool_stats::m_num_failing)
    .def_readwrite("num_double_spends", &monero_tx_pool_stats::m_num_double_spends)
    .def_readwrite("num10m", &monero_tx_pool_stats::m_num10m)
    .def_readwrite("fee_total", &monero_tx_pool_stats::m_fee_total)
    .def_readwrite("bytes_max", &monero_tx_pool_stats::m_bytes_max)
    .def_readwrite("bytes_med", &monero_tx_pool_stats::m_bytes_med)
    .def_readwrite("bytes_min", &monero_tx_pool_stats::m_bytes_min)
    .def_readwrite("bytes_total", &monero_tx_pool_stats::m_bytes_total)
    .def_readwrite("histo98pc", &monero_tx_pool_stats::m_histo98pc)
    .def_readwrite("oldest_timestamp", &monero_tx_pool_stats::m_oldest_timestamp)
    .def_readwrite("histo", &monero_tx_pool_stats::m_histo, py::return_value_policy::reference_internal);

  // monero_mining_status
  py::class_<monero_mining_status, serializable_struct, std::shared_ptr<monero_mining_status>>(m, "MoneroMiningStatus")
    .def(py::init<>())
    .def_readwrite("is_active", &monero_mining_status::m_is_active)
    .def_readwrite("is_background", &monero_mining_status::m_is_background)
    .def_readwrite("address", &monero_mining_status::m_address)
    .def_readwrite("speed", &monero_mining_status::m_speed)
    .def_readwrite("num_threads", &monero_mining_status::m_num_threads);

  // monero_miner_tx_sum
  py::class_<monero_miner_tx_sum, serializable_struct, std::shared_ptr<monero_miner_tx_sum>>(m, "MoneroMinerTxSum")
    .def(py::init<>())
    .def_readwrite("emission_sum_low", &monero_miner_tx_sum::m_emission_sum_low)
    .def_readwrite("emission_sum_high", &monero_miner_tx_sum::m_emission_sum_high)
    .def_readwrite("fee_sum_low", &monero_miner_tx_sum::m_fee_sum_low)
    .def_readwrite("fee_sum_high", &monero_miner_tx_sum::m_fee_sum_high);

  // monero_tx
  py_monero_tx
    .def(py::init<>())
    .def_property_readonly_static("DEFAULT_PAYMENT_ID", [](py::object /* self */) { return monero_tx::DEFAULT_PAYMENT_ID; })
    .def_readwrite("block", &monero_tx::m_block)
    .def_readwrite("hash", &monero_tx::m_hash)
    .def_readwrite("version", &monero_tx::m_version)
    .def_readwrite("is_miner_tx", &monero_tx::m_is_miner_tx)
    .def_readwrite("payment_id", &monero_tx::m_payment_id)
    .def_readwrite("fee", &monero_tx::m_fee)
    .def_readwrite("ring_size", &monero_tx::m_ring_size)
    .def_readwrite("relay", &monero_tx::m_relay)
    .def_readwrite("is_relayed", &monero_tx::m_is_relayed)
    .def_readwrite("is_confirmed", &monero_tx::m_is_confirmed)
    .def_readwrite("in_tx_pool", &monero_tx::m_in_tx_pool)
    .def_readwrite("num_confirmations", &monero_tx::m_num_confirmations)
    .def_readwrite("unlock_time", &monero_tx::m_unlock_time)
    .def_readwrite("last_relayed_timestamp", &monero_tx::m_last_relayed_timestamp)
    .def_readwrite("received_timestamp", &monero_tx::m_received_timestamp)
    .def_readwrite("is_double_spend_seen", &monero_tx::m_is_double_spend_seen)
    .def_readwrite("key", &monero_tx::m_key)
    .def_readwrite("full_hex", &monero_tx::m_full_hex)
    .def_readwrite("pruned_hex", &monero_tx::m_pruned_hex)
    .def_readwrite("prunable_hex", &monero_tx::m_prunable_hex)
    .def_readwrite("prunable_hash", &monero_tx::m_prunable_hash)
    .def_readwrite("size", &monero_tx::m_size)
    .def_readwrite("weight", &monero_tx::m_weight)
    .def_readwrite("inputs", &monero_tx::m_inputs)
    .def_readwrite("outputs", &monero_tx::m_outputs)
    .def_readwrite("output_indices", &monero_tx::m_output_indices)
    .def_readwrite("metadata", &monero_tx::m_metadata)
    .def_readwrite("common_tx_sets", &monero_tx::m_common_tx_sets)
    .def_readwrite("extra", &monero_tx::m_extra)
    .def_readwrite("rct_signatures", &monero_tx::m_rct_signatures)
    .def_readwrite("rct_sig_prunable", &monero_tx::m_rct_sig_prunable)
    .def_readwrite("is_kept_by_block", &monero_tx::m_is_kept_by_block)
    .def_readwrite("is_failed", &monero_tx::m_is_failed)
    .def_readwrite("last_failed_height", &monero_tx::m_last_failed_height)
    .def_readwrite("last_failed_hash", &monero_tx::m_last_failed_hash)
    .def_readwrite("max_used_block_height", &monero_tx::m_max_used_block_height)
    .def_readwrite("max_used_block_hash", &monero_tx::m_max_used_block_hash)
    .def_readwrite("signatures", &monero_tx::m_signatures)
    .def("copy", [](const std::shared_ptr<monero_tx>& self) {
      auto tgt = std::make_shared<monero_tx>();
      MONERO_CATCH_AND_RETHROW(self->copy(self, tgt));
    })
    .def("merge", [](const std::shared_ptr<monero_tx>& self, const std::shared_ptr<monero_tx>& other) {
      MONERO_CATCH_AND_RETHROW(self->merge(self, other));
    }, py::arg("other"))
    .def("get_height", [](monero_tx& self) {
      MONERO_CATCH_AND_RETHROW(self.get_height());
    })
    .def("__lt__", [](const std::shared_ptr<monero_tx>& a, const std::shared_ptr<monero_tx>& b){
      monero_tx_height_comparator comp;
      return comp(a, b);
    });

  // monero_key_image
  py_monero_key_image
    .def(py::init<>())
    .def_static("deserialize_key_images", [](const std::string& key_images_json) {
      MONERO_CATCH_AND_RETHROW(monero_key_image::deserialize_key_images(key_images_json));
    }, py::arg("key_images_json"))
    .def_readwrite("hex", &monero_key_image::m_hex)
    .def_readwrite("signature", &monero_key_image::m_signature)
    .def("copy", [](const std::shared_ptr<monero_key_image>& self) {
      auto tgt = std::make_shared<monero_key_image>();
      MONERO_CATCH_AND_RETHROW(self->copy(self, tgt));
    })
    .def("merge", [](const std::shared_ptr<monero_key_image>& self, const std::shared_ptr<monero_key_image>& other) {
      MONERO_CATCH_AND_RETHROW(self->merge(self, other));
    }, py::arg("other"));

  // monero_output
  py_monero_output
    .def(py::init<>())
    .def_readwrite("tx", &monero_output::m_tx)
    .def_readwrite("key_image", &monero_output::m_key_image)
    .def_readwrite("amount", &monero_output::m_amount)
    .def_readwrite("index", &monero_output::m_index)
    .def_readwrite("stealth_public_key", &monero_output::m_stealth_public_key)
    .def_readwrite("ring_output_indices", &monero_output::m_ring_output_indices)
    .def("copy", [](const std::shared_ptr<monero_output>& self) {
      auto tgt = std::make_shared<monero_output>();
      MONERO_CATCH_AND_RETHROW(self->copy(self, tgt));
    })
    .def("merge", [](const std::shared_ptr<monero_output>& self, const std::shared_ptr<monero_output>& other) {
      MONERO_CATCH_AND_RETHROW(self->merge(self, other));
    }, py::arg("other"));

  // monero_wallet_config
  py_monero_wallet_config
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
  py_monero_subaddress
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
  py_monero_sync_result
    .def(py::init<>())
    .def(py::init<const uint16_t, const bool>(), py::arg("num_blocks_fetched"), py::arg("received_money"))
    .def_readwrite("num_blocks_fetched", &monero_sync_result::m_num_blocks_fetched)
    .def_readwrite("received_money", &monero_sync_result::m_received_money);

  // monero_account
  py_monero_account
    .def(py::init<>())
    .def_readwrite("index", &monero_account::m_index)
    .def_readwrite("primary_address", &monero_account::m_primary_address)
    .def_readwrite("balance", &monero_account::m_balance)
    .def_readwrite("unlocked_balance", &monero_account::m_unlocked_balance)
    .def_readwrite("tag", &monero_account::m_tag)
    .def_readwrite("subaddresses", &monero_account::m_subaddresses);

  // monero_account_tag
  py_monero_account_tag
    .def(py::init<>())
    .def(py::init<std::string&, std::string&>(), py::arg("tag"), py::arg("label"))
    .def(py::init<std::string&, std::string&, std::vector<uint32_t>>(), py::arg("tag"), py::arg("label"), py::arg("account_indices"))
    .def_readwrite("tag", &monero_account_tag::m_tag)
    .def_readwrite("label", &monero_account_tag::m_label)
    .def_readwrite("account_indices", &monero_account_tag::m_account_indices);

  // monero_destination
  py_monero_destination
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
  py_monero_transfer
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
  py_monero_incoming_transfer
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
  py_monero_outgoing_transfer
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
  py_monero_transfer_query
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
  py_monero_output_wallet
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
  py_monero_output_query
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
  py_monero_tx_wallet
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
  py_monero_tx_query
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
  py_monero_tx_set
    .def(py::init<>())
    .def_static("deserialize", [](const std::string& tx_set_json) {
      MONERO_CATCH_AND_RETHROW(monero_tx_set::deserialize(tx_set_json));
    }, py::arg("tx_set_json"))
    .def_readwrite("txs", &monero_tx_set::m_txs)
    .def_readwrite("signed_tx_hex", &monero_tx_set::m_signed_tx_hex)
    .def_readwrite("unsigned_tx_hex", &monero_tx_set::m_unsigned_tx_hex)
    .def_readwrite("multisig_tx_hex", &monero_tx_set::m_multisig_tx_hex);

  // monero_integrated_address
  py_monero_integrated_address
    .def(py::init<>())
    .def_readwrite("standard_address", &monero_integrated_address::m_standard_address)
    .def_readwrite("payment_id", &monero_integrated_address::m_payment_id)
    .def_readwrite("integrated_address", &monero_integrated_address::m_integrated_address);

  // monero_decoded_address
  py_monero_decoded_address
    .def(py::init<std::string&, monero_address_type, monero_network_type>(), py::arg("address"), py::arg("address_type"), py::arg("network_type"))
    .def_readwrite("address", &monero_decoded_address::m_address)
    .def_readwrite("address_type", &monero_decoded_address::m_address_type)
    .def_readwrite("network_type", &monero_decoded_address::m_network_type);

  // monero_tx_config
  py_monero_tx_config
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
  py_monero_key_image_export_result
    .def(py::init<>())
    .def_readwrite("offset", &monero_key_image_export_result::m_offset)
    .def_readwrite("key_images", &monero_key_image_export_result::m_key_images);

  // monero_key_image_import_result
  py_monero_key_image_import_result
    .def(py::init<>())
    .def_readwrite("height", &monero_key_image_import_result::m_height)
    .def_readwrite("spent_amount", &monero_key_image_import_result::m_spent_amount)
    .def_readwrite("unspent_amount", &monero_key_image_import_result::m_unspent_amount);

  // monero_message_signature_result
  py_monero_message_signature_result
    .def(py::init<>())
    .def_readwrite("is_good", &monero_message_signature_result::m_is_good)
    .def_readwrite("version", &monero_message_signature_result::m_version)
    .def_readwrite("is_old", &monero_message_signature_result::m_is_old)
    .def_readwrite("signature_type", &monero_message_signature_result::m_signature_type);

  // monero_check
  py_monero_check
    .def(py::init<>())
    .def_readwrite("is_good", &monero_check::m_is_good);

  // monero_check_tx
  py_monero_check_tx
    .def(py::init<>())
    .def_readwrite("in_tx_pool", &monero_check_tx::m_in_tx_pool)
    .def_readwrite("num_confirmations", &monero_check_tx::m_num_confirmations)
    .def_readwrite("received_amount", &monero_check_tx::m_received_amount);

  // monero_check_reserve
  py_monero_check_reserve
    .def(py::init<>())
    .def_readwrite("total_amount", &monero_check_reserve::m_total_amount)
    .def_readwrite("unconfirmed_spent_amount", &monero_check_reserve::m_unconfirmed_spent_amount);

  // monero_multisig_info
  py_monero_multisig_info
    .def(py::init<>())
    .def_readwrite("is_multisig", &monero_multisig_info::m_is_multisig)
    .def_readwrite("is_ready", &monero_multisig_info::m_is_ready)
    .def_readwrite("threshold", &monero_multisig_info::m_threshold)
    .def_readwrite("num_participants", &monero_multisig_info::m_num_participants);

  // monero_multisig_init_result
  py_monero_multisig_init_result
    .def(py::init<>())
    .def_readwrite("address", &monero_multisig_init_result::m_address)
    .def_readwrite("multisig_hex", &monero_multisig_init_result::m_multisig_hex);

  // monero_multisig_sign_result
  py_monero_multisig_sign_result
    .def(py::init<>())
    .def_readwrite("signed_multisig_tx_hex", &monero_multisig_sign_result::m_signed_multisig_tx_hex)
    .def_readwrite("tx_hashes", &monero_multisig_sign_result::m_tx_hashes);

  // monero_address_book_entry
  py_monero_address_book_entry
    .def(py::init<>())
    .def(py::init<uint64_t, const std::string&, const std::string&>(), py::arg("index"), py::arg("address"), py::arg("description"))
    .def(py::init<uint64_t, const std::string&, const std::string&, const std::string&>(), py::arg("index"), py::arg("address"), py::arg("description"), py::arg("payment_id"))
    .def_readwrite("index", &monero_address_book_entry::m_index)
    .def_readwrite("address", &monero_address_book_entry::m_address)
    .def_readwrite("description", &monero_address_book_entry::m_description)
    .def_readwrite("payment_id", &monero_address_book_entry::m_payment_id);

  // monero_wallet_listener
  py_monero_wallet_listener
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

  // monero_daemon_listener
  py_monero_daemon_listener
    .def(py::init<>())
    .def_readwrite("last_header", &monero_daemon_listener::m_last_header)
    .def("on_block_header", [](monero_daemon_listener& self, const std::shared_ptr<monero_block_header>& header) {
      MONERO_CATCH_AND_RETHROW(self.on_block_header(header));
    }, py::arg("header"));

  // monero_daemon
  py_monero_daemon
    .def(py::init<>())
    .def("add_listener", [](monero_daemon& self, monero_daemon_listener& listener) {
      MONERO_CATCH_AND_RETHROW(self.add_listener(listener));
    }, py::arg("listener"), py::call_guard<py::gil_scoped_release>())
    .def("remove_listener", [](monero_daemon& self, monero_daemon_listener& listener) {
      MONERO_CATCH_AND_RETHROW(self.remove_listener(listener));
    }, py::arg("listener"), py::call_guard<py::gil_scoped_release>())
    .def("get_listeners", [](monero_daemon& self) {
      MONERO_CATCH_AND_RETHROW(self.get_listeners());
    }, py::call_guard<py::gil_scoped_release>())
    .def("get_version", [](monero_daemon& self) {
      MONERO_CATCH_AND_RETHROW(self.get_version());
    }, py::call_guard<py::gil_scoped_release>())
    .def("is_trusted", [](monero_daemon& self) {
      MONERO_CATCH_AND_RETHROW(self.is_trusted());
    }, py::call_guard<py::gil_scoped_release>())
    .def("get_height", [](monero_daemon& self) {
      MONERO_CATCH_AND_RETHROW(self.get_height());
    }, py::call_guard<py::gil_scoped_release>())
    .def("get_block_hash", [](monero_daemon& self, uint64_t height) {
      MONERO_CATCH_AND_RETHROW(self.get_block_hash(height));
    }, py::arg("height"), py::call_guard<py::gil_scoped_release>())
    .def("get_block_template", [](monero_daemon& self, const std::string& wallet_address, const boost::optional<int>& reserve_size) {
      MONERO_CATCH_AND_RETHROW(self.get_block_template(wallet_address, reserve_size));
    }, py::arg("wallet_address"), py::arg("reserve_size") = py::none(), py::call_guard<py::gil_scoped_release>())
    .def("get_last_block_header", [](monero_daemon& self) {
      MONERO_CATCH_AND_RETHROW(self.get_last_block_header());
    }, py::call_guard<py::gil_scoped_release>())
    .def("get_block_header_by_hash", [](monero_daemon& self, const std::string& hash) {
      MONERO_CATCH_AND_RETHROW(self.get_block_header_by_hash(hash));
    }, py::arg("hash"), py::call_guard<py::gil_scoped_release>())
    .def("get_block_header_by_height", [](monero_daemon& self, uint64_t height) {
      MONERO_CATCH_AND_RETHROW(self.get_block_header_by_height(height));
    }, py::arg("height"), py::call_guard<py::gil_scoped_release>())
    .def("get_block_headers_by_range", [](monero_daemon& self, uint64_t start_height, uint64_t end_height) {
      MONERO_CATCH_AND_RETHROW(self.get_block_headers_by_range(start_height, end_height));
    }, py::arg("start_height"), py::arg("end_height"), py::call_guard<py::gil_scoped_release>())
    .def("get_block_by_hash", [](monero_daemon& self, const std::string& hash) {
      MONERO_CATCH_AND_RETHROW(self.get_block_by_hash(hash));
    }, py::arg("hash"), py::call_guard<py::gil_scoped_release>())
    .def("get_blocks_by_hash", [](monero_daemon& self, const std::vector<std::string>& block_hashes, uint64_t start_height, bool prune) {
      MONERO_CATCH_AND_RETHROW(self.get_blocks_by_hash(block_hashes, start_height, prune));
    }, py::arg("block_hashes"), py::arg("start_height"), py::arg("prune"), py::call_guard<py::gil_scoped_release>())
    .def("get_block_by_height", [](monero_daemon& self, uint64_t height) {
      MONERO_CATCH_AND_RETHROW(self.get_block_by_height(height));
    }, py::arg("height"), py::call_guard<py::gil_scoped_release>())
    .def("get_blocks_by_height", [](monero_daemon& self, const std::vector<uint64_t>& heights) {
      MONERO_CATCH_AND_RETHROW(self.get_blocks_by_height(heights));
    }, py::arg("heights"), py::call_guard<py::gil_scoped_release>())
    .def("get_blocks_by_range", [](monero_daemon& self, const boost::optional<uint64_t>& start_height, const boost::optional<uint64_t>& end_height) {
      MONERO_CATCH_AND_RETHROW(self.get_blocks_by_range(start_height, end_height));
    }, py::arg("start_height"), py::arg("end_height"), py::call_guard<py::gil_scoped_release>())
    .def("get_blocks_by_range_chunked", [](monero_daemon& self, const boost::optional<uint64_t>& start_height, const boost::optional<uint64_t>& end_height, const boost::optional<uint64_t>& max_chunk_size) {
      MONERO_CATCH_AND_RETHROW(self.get_blocks_by_range_chunked(start_height, end_height, max_chunk_size));
    }, py::arg("start_height"), py::arg("end_height"), py::arg("max_chunk_size") = py::none(), py::call_guard<py::gil_scoped_release>())
    .def("get_block_hashes", [](monero_daemon& self, const std::vector<std::string>& block_hashes, uint64_t start_height) {
      MONERO_CATCH_AND_RETHROW(self.get_block_hashes(block_hashes, start_height));
    }, py::arg("block_hashes"), py::arg("start_height"), py::call_guard<py::gil_scoped_release>())
    .def("get_tx", [](monero_daemon& self, const std::string& tx_hash, bool prune) {
      MONERO_CATCH_AND_RETHROW(self.get_tx(tx_hash, prune));
    }, py::arg("tx_hash"), py::arg("prune") = false, py::call_guard<py::gil_scoped_release>())
    .def("get_txs", [](monero_daemon& self, const std::vector<std::string>& tx_hashes, bool prune) {
      MONERO_CATCH_AND_RETHROW(self.get_txs(tx_hashes, prune));
    }, py::arg("tx_hashes"), py::arg("prune") = false, py::call_guard<py::gil_scoped_release>())
    .def("get_tx_hex", [](monero_daemon& self, const std::string& tx_hash, bool prune) {
      MONERO_CATCH_AND_RETHROW(self.get_tx_hex(tx_hash, prune));
    }, py::arg("tx_hash"), py::arg("prune") = false, py::call_guard<py::gil_scoped_release>())
    .def("get_tx_hexes", [](monero_daemon& self, const std::vector<std::string>& tx_hashes, bool prune) {
      MONERO_CATCH_AND_RETHROW(self.get_tx_hexes(tx_hashes, prune));
    }, py::arg("tx_hashes"), py::arg("prune") = false, py::call_guard<py::gil_scoped_release>())
    .def("get_miner_tx_sum", [](monero_daemon& self, uint64_t height, uint64_t num_blocks) {
      MONERO_CATCH_AND_RETHROW(self.get_miner_tx_sum(height, num_blocks));
    }, py::arg("height"), py::arg("num_blocks"), py::call_guard<py::gil_scoped_release>())
    .def("get_fee_estimate", [](monero_daemon& self, uint64_t grace_blocks) {
      MONERO_CATCH_AND_RETHROW(self.get_fee_estimate(grace_blocks));
    }, py::arg("grace_blocks") = 0, py::call_guard<py::gil_scoped_release>())
    .def("submit_tx_hex", [](monero_daemon& self, const std::string& tx_hex, bool do_not_relay) {
      MONERO_CATCH_AND_RETHROW(self.submit_tx_hex(tx_hex, do_not_relay));
    }, py::arg("tx_hex"), py::arg("do_not_relay") = false, py::call_guard<py::gil_scoped_release>())
    .def("relay_tx_by_hash", [](monero_daemon& self, const std::string& tx_hash) {
      MONERO_CATCH_AND_RETHROW(self.relay_tx_by_hash(tx_hash));
    }, py::arg("tx_hash"), py::call_guard<py::gil_scoped_release>())
    .def("relay_txs_by_hash", [](monero_daemon& self, const std::vector<std::string>& tx_hashes) {
      MONERO_CATCH_AND_RETHROW(self.relay_txs_by_hash(tx_hashes));
    }, py::arg("tx_hashes"), py::call_guard<py::gil_scoped_release>())
    .def("get_tx_pool", [](monero_daemon& self) {
      MONERO_CATCH_AND_RETHROW(self.get_tx_pool());
    }, py::call_guard<py::gil_scoped_release>())
    .def("get_tx_pool_hashes", [](monero_daemon& self) {
      MONERO_CATCH_AND_RETHROW(self.get_tx_pool_hashes());
    }, py::call_guard<py::gil_scoped_release>())
    .def("get_tx_pool_backlog", [](monero_daemon& self) {
      MONERO_CATCH_AND_RETHROW(self.get_tx_pool_backlog());
    }, py::call_guard<py::gil_scoped_release>())
    .def("get_tx_pool_stats", [](monero_daemon& self) {
      MONERO_CATCH_AND_RETHROW(self.get_tx_pool_stats());
    }, py::call_guard<py::gil_scoped_release>())
    .def("flush_tx_pool", [](monero_daemon& self) {
      MONERO_CATCH_AND_RETHROW(self.flush_tx_pool());
    }, py::call_guard<py::gil_scoped_release>())
    .def("flush_tx_pool", [](monero_daemon& self, const std::vector<std::string>& hashes) {
      MONERO_CATCH_AND_RETHROW(self.flush_tx_pool(hashes));
    }, py::arg("hashes"), py::call_guard<py::gil_scoped_release>())
    .def("flush_tx_pool", [](monero_daemon& self, const std::string& hash) {
      MONERO_CATCH_AND_RETHROW(self.flush_tx_pool(hash));
    }, py::arg("hash"), py::call_guard<py::gil_scoped_release>())
    .def("get_key_image_spent_status", [](monero_daemon& self, const std::string& key_image) {
      MONERO_CATCH_AND_RETHROW(self.get_key_image_spent_status(key_image));
    }, py::arg("key_image"), py::call_guard<py::gil_scoped_release>())
    .def("get_key_image_spent_statuses", [](monero_daemon& self, const std::vector<std::string>& key_images) {
      MONERO_CATCH_AND_RETHROW(self.get_key_image_spent_statuses(key_images));
    }, py::arg("key_images"), py::call_guard<py::gil_scoped_release>())
    .def("get_outputs", [](monero_daemon& self, const std::vector<monero_output>& outputs) {
      MONERO_CATCH_AND_RETHROW(self.get_outputs(outputs));
    }, py::arg("outputs"), py::call_guard<py::gil_scoped_release>())
    .def("get_output_histogram", [](monero_daemon& self, const std::vector<uint64_t>& amounts, const boost::optional<int>& min_count, const boost::optional<int>& max_count, const boost::optional<bool>& is_unlocked, const boost::optional<int>& recent_cutoff) {
      MONERO_CATCH_AND_RETHROW(self.get_output_histogram(amounts, min_count, max_count, is_unlocked, recent_cutoff));
    }, py::arg("amounts"), py::arg("min_count"), py::arg("max_count"), py::arg("is_unlocked"), py::arg("recent_cutoff"), py::call_guard<py::gil_scoped_release>())
    .def("get_output_distribution", [](monero_daemon& self, const std::vector<uint64_t>& amounts, const boost::optional<bool>& is_cumulative, const boost::optional<uint64_t>& start_height, const boost::optional<uint64_t>& end_height) {
      MONERO_CATCH_AND_RETHROW(self.get_output_distribution(amounts, is_cumulative, start_height, end_height));
    }, py::arg("amounts"), py::arg("is_cumulative") = py::none(), py::arg("start_height") = py::none(), py::arg("end_height") = py::none(), py::call_guard<py::gil_scoped_release>())
    .def("get_info", [](monero_daemon& self) {
      MONERO_CATCH_AND_RETHROW(self.get_info());
    }, py::call_guard<py::gil_scoped_release>())
    .def("get_sync_info", [](monero_daemon& self) {
      MONERO_CATCH_AND_RETHROW(self.get_sync_info());
    }, py::call_guard<py::gil_scoped_release>())
    .def("get_hard_fork_info", [](monero_daemon& self) {
      MONERO_CATCH_AND_RETHROW(self.get_hard_fork_info());
    }, py::call_guard<py::gil_scoped_release>())
    .def("get_alt_chains", [](monero_daemon& self) {
      MONERO_CATCH_AND_RETHROW(self.get_alt_chains());
    }, py::call_guard<py::gil_scoped_release>())
    .def("get_alt_block_hashes", [](monero_daemon& self) {
      MONERO_CATCH_AND_RETHROW(self.get_alt_block_hashes());
    }, py::call_guard<py::gil_scoped_release>())
    .def("get_download_limit", [](monero_daemon& self) {
      MONERO_CATCH_AND_RETHROW(self.get_download_limit());
    }, py::call_guard<py::gil_scoped_release>())
    .def("set_download_limit", [](monero_daemon& self, int limit) {
      MONERO_CATCH_AND_RETHROW(self.set_download_limit(limit));
    }, py::arg("limit"), py::call_guard<py::gil_scoped_release>())
    .def("reset_download_limit", [](monero_daemon& self) {
      MONERO_CATCH_AND_RETHROW(self.reset_download_limit());
    }, py::call_guard<py::gil_scoped_release>())
    .def("get_upload_limit", [](monero_daemon& self) {
      MONERO_CATCH_AND_RETHROW(self.get_upload_limit());
    }, py::call_guard<py::gil_scoped_release>())
    .def("set_upload_limit", [](monero_daemon& self, int limit) {
      MONERO_CATCH_AND_RETHROW(self.set_upload_limit(limit));
    }, py::arg("limit"), py::call_guard<py::gil_scoped_release>())
    .def("reset_upload_limit", [](monero_daemon& self) {
      MONERO_CATCH_AND_RETHROW(self.reset_upload_limit());
    }, py::call_guard<py::gil_scoped_release>())
    .def("get_peers", [](monero_daemon& self) {
      MONERO_CATCH_AND_RETHROW(self.get_peers());
    }, py::call_guard<py::gil_scoped_release>())
    .def("get_known_peers", [](monero_daemon& self) {
      MONERO_CATCH_AND_RETHROW(self.get_known_peers());
    }, py::call_guard<py::gil_scoped_release>())
    .def("set_outgoing_peer_limit", [](monero_daemon& self, int limit) {
      MONERO_CATCH_AND_RETHROW(self.set_outgoing_peer_limit(limit));
    }, py::arg("limit"), py::call_guard<py::gil_scoped_release>())
    .def("set_incoming_peer_limit", [](monero_daemon& self, int limit) {
      MONERO_CATCH_AND_RETHROW(self.set_incoming_peer_limit(limit));
    }, py::arg("limit"), py::call_guard<py::gil_scoped_release>())
    .def("get_peer_bans", [](monero_daemon& self) {
      MONERO_CATCH_AND_RETHROW(self.get_peer_bans());
    }, py::call_guard<py::gil_scoped_release>())
    .def("set_peer_bans", [](monero_daemon& self, const std::vector<std::shared_ptr<monero_ban>>& bans) {
      MONERO_CATCH_AND_RETHROW(self.set_peer_bans(bans));
    }, py::arg("bans"), py::call_guard<py::gil_scoped_release>())
    .def("set_peer_ban", [](monero_daemon& self, const std::shared_ptr<monero_ban>& ban) {
      MONERO_CATCH_AND_RETHROW(self.set_peer_ban(ban));
    }, py::arg("ban"), py::call_guard<py::gil_scoped_release>())
    .def("start_mining", [](monero_daemon& self, const std::string& address, const boost::optional<uint64_t>& num_threads, const boost::optional<bool>& is_background, const boost::optional<bool>& ignore_battery) {
      MONERO_CATCH_AND_RETHROW(self.start_mining(address, num_threads, is_background, ignore_battery));
    }, py::arg("address"), py::arg("num_threads"), py::arg("is_background"), py::arg("ignore_battery"), py::call_guard<py::gil_scoped_release>())
    .def("stop_mining", [](monero_daemon& self) {
      MONERO_CATCH_AND_RETHROW(self.stop_mining());
    }, py::call_guard<py::gil_scoped_release>())
    .def("get_mining_status", [](monero_daemon& self) {
      MONERO_CATCH_AND_RETHROW(self.get_mining_status());
    }, py::call_guard<py::gil_scoped_release>())
    .def("generate_blocks", [](monero_daemon& self,const std::string& wallet_address, uint64_t num_blocks, const boost::optional<std::string>& prev_block_hash, const boost::optional<uint32_t>& starting_nonce) {
      MONERO_CATCH_AND_RETHROW(self.generate_blocks(wallet_address, num_blocks, prev_block_hash, starting_nonce));
    }, py::arg("wallet_address"), py::arg("num_blocks"), py::arg("prev_block_hash") = py::none(), py::arg("starting_nonce") = py::none(), py::call_guard<py::gil_scoped_release>())
    .def("submit_block", [](monero_daemon& self, const std::string& block_blob) {
      MONERO_CATCH_AND_RETHROW(self.submit_block(block_blob));
    }, py::arg("block_blob"), py::call_guard<py::gil_scoped_release>())
    .def("submit_blocks", [](monero_daemon& self, const std::vector<std::string>& block_blobs) {
      MONERO_CATCH_AND_RETHROW(self.submit_blocks(block_blobs));
    }, py::arg("block_blobs"), py::call_guard<py::gil_scoped_release>())
    .def("prune_blockchain", [](monero_daemon& self, bool check) {
      MONERO_CATCH_AND_RETHROW(self.prune_blockchain(check));
    }, py::arg("check"), py::call_guard<py::gil_scoped_release>())
    .def("check_for_update", [](monero_daemon& self) {
      MONERO_CATCH_AND_RETHROW(self.check_for_update());
    }, py::call_guard<py::gil_scoped_release>())
    .def("download_update", [](monero_daemon& self, const std::string& path) {
      MONERO_CATCH_AND_RETHROW(self.download_update(path));
    }, py::arg("path") = "", py::call_guard<py::gil_scoped_release>())
    .def("stop", [](monero_daemon& self) {
      MONERO_CATCH_AND_RETHROW(self.stop());
    }, py::call_guard<py::gil_scoped_release>())
    .def("wait_for_next_block_header", [](monero_daemon& self) {
      MONERO_CATCH_AND_RETHROW(self.wait_for_next_block_header());
    }, py::call_guard<py::gil_scoped_release>());

  // monero_daemon_rpc
  py_monero_daemon_rpc
    .def(py::init<const std::shared_ptr<monero_rpc_connection>&>(), py::arg("rpc"), py::call_guard<py::gil_scoped_release>())
    .def(py::init<const std::string&, const std::string&, const std::string&, const std::string&, const std::string&, const boost::optional<uint32_t>&>(), py::arg("uri"), py::arg("username") = "", py::arg("password") = "", py::arg("proxy_uri") = "", py::arg("zmq_uri") = "", py::arg("timeout_ms") = py::none(), py::call_guard<py::gil_scoped_release>())
    .def("get_rpc_connection", [](const monero_daemon_rpc& self) {
      MONERO_CATCH_AND_RETHROW(self.get_rpc_connection());
    })
    .def("is_connected", [](monero_daemon_rpc& self) {
      MONERO_CATCH_AND_RETHROW(self.is_connected());
    }, py::call_guard<py::gil_scoped_release>());

  // monero_wallet
  py_monero_wallet
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
  py_monero_wallet_keys
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
  py_monero_wallet_full
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

  // monero_wallet_rpc
  py_monero_wallet_rpc
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

  // monero_utils
  py_monero_utils
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

  // tx height comparator
  py_tx_height_comparator
    .def_static("compare", [](const std::shared_ptr<monero_tx>& tx1, const std::shared_ptr<monero_tx>& tx2) {
      monero_tx_height_comparator tx_comp;
      MONERO_CATCH_AND_RETHROW(tx_comp(tx1, tx2));
    }, py::arg("tx1"), py::arg("tx2"));

  // incoming transfer comparator
  py_incoming_transfer_comparator
    .def_static("compare", [](const monero_incoming_transfer& t1, const monero_incoming_transfer& t2){
      monero_incoming_transfer_comparator tr_comp;
      MONERO_CATCH_AND_RETHROW(tr_comp(t1, t2));
    }, py::arg("transfer1"), py::arg("transfer2"));

  // output comparator
  py_output_comparator
    .def_static("compare", [](const monero_output_wallet& o1, const monero_output_wallet& o2) {
      monero_output_comparator out_comp;
      MONERO_CATCH_AND_RETHROW(out_comp(o1, o2));
    }, py::arg("output1"), py::arg("output2"));

}
