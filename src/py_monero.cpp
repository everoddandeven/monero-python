#include <pybind11/stl_bind.h>
#include <pybind11/eval.h>
#include "py_monero.h"

PYBIND11_MAKE_OPAQUE(std::vector<int>);
PYBIND11_MAKE_OPAQUE(std::vector<uint8_t>);
PYBIND11_MAKE_OPAQUE(std::vector<uint32_t>);
PYBIND11_MAKE_OPAQUE(std::vector<uint64_t>);
PYBIND11_MAKE_OPAQUE(std::vector<std::string>);
PYBIND11_MAKE_OPAQUE(std::vector<std::shared_ptr<monero::monero_block>>);
PYBIND11_MAKE_OPAQUE(std::vector<std::shared_ptr<monero::monero_block_header>>);
PYBIND11_MAKE_OPAQUE(std::vector<std::shared_ptr<monero::monero_tx>>);
PYBIND11_MAKE_OPAQUE(std::vector<std::shared_ptr<monero::monero_tx_wallet>>);
PYBIND11_MAKE_OPAQUE(std::vector<std::shared_ptr<monero::monero_output>>);
PYBIND11_MAKE_OPAQUE(std::vector<std::shared_ptr<monero::monero_output_wallet>>);
PYBIND11_MAKE_OPAQUE(std::vector<std::shared_ptr<monero::monero_transfer>>);
PYBIND11_MAKE_OPAQUE(std::vector<std::shared_ptr<monero::monero_incoming_transfer>>);
PYBIND11_MAKE_OPAQUE(std::vector<std::shared_ptr<monero::monero_outgoing_transfer>>);
PYBIND11_MAKE_OPAQUE(std::vector<monero::monero_subaddress>);
PYBIND11_MAKE_OPAQUE(std::vector<std::shared_ptr<monero_destination>>);


PYBIND11_MODULE(monero, m) {
  m.doc() = "";

  auto py_serializable_struct = py::class_<monero::serializable_struct, PySerializableStruct, std::shared_ptr<monero::serializable_struct>>(m, "SerializableStruct");
  auto py_monero_version = py::class_<monero::monero_version, monero::serializable_struct, std::shared_ptr<monero::monero_version>>(m, "MoneroVersion");
  auto py_monero_block_header = py::class_<monero::monero_block_header, monero::serializable_struct, std::shared_ptr<monero::monero_block_header>>(m, "MoneroBlockHeader");
  auto py_monero_block = py::class_<monero::monero_block, monero::monero_block_header, std::shared_ptr<monero::monero_block>>(m, "MoneroBlock");
  auto py_monero_tx = py::class_<monero::monero_tx, monero::serializable_struct, std::shared_ptr<monero::monero_tx>>(m, "MoneroTx");
  auto py_monero_key_image = py::class_<monero::monero_key_image, monero::serializable_struct, std::shared_ptr<monero::monero_key_image>>(m, "MoneroKeyImage");
  auto py_monero_output = py::class_<monero::monero_output, monero::serializable_struct, std::shared_ptr<monero::monero_output>>(m, "MoneroOutput");
  auto py_monero_wallet_config = py::class_<monero::monero_wallet_config, PyMoneroWalletConfig, std::shared_ptr<monero::monero_wallet_config>>(m, "MoneroWalletConfig");
  auto py_monero_subaddress = py::class_<monero::monero_subaddress, monero::serializable_struct, std::shared_ptr<monero::monero_subaddress>>(m, "MoneroSubaddress");
  auto py_monero_sync_result = py::class_<monero::monero_sync_result, monero::serializable_struct, std::shared_ptr<monero::monero_sync_result>>(m, "MoneroSyncResult");
  auto py_monero_account = py::class_<monero::monero_account, monero::serializable_struct, std::shared_ptr<monero::monero_account>>(m, "MoneroAccount");
  auto py_monero_account_tag = py::class_<PyMoneroAccountTag, std::shared_ptr<PyMoneroAccountTag>>(m, "MoneroAccountTag");
  auto py_monero_destination = py::class_<monero::monero_destination, std::shared_ptr<monero::monero_destination>>(m, "MoneroDestination");
  auto py_monero_transfer = py::class_<monero::monero_transfer, PyMoneroTransfer, std::shared_ptr<monero::monero_transfer>>(m, "MoneroTransfer");
  auto py_monero_incoming_transfer = py::class_<monero::monero_incoming_transfer, monero::monero_transfer, std::shared_ptr<monero::monero_incoming_transfer>>(m, "MoneroIncomingTransfer");
  auto py_monero_outgoing_transfer = py::class_<monero::monero_outgoing_transfer, monero::monero_transfer, std::shared_ptr<monero::monero_outgoing_transfer>>(m, "MoneroOutgoingTransfer");
  auto py_monero_transfer_query = py::class_<monero::monero_transfer_query, monero::monero_transfer, std::shared_ptr<monero_transfer_query>>(m, "MoneroTransferQuery");
  auto py_monero_output_wallet = py::class_<monero::monero_output_wallet, monero::monero_output, std::shared_ptr<monero::monero_output_wallet>>(m, "MoneroOutputWallet");
  auto py_monero_output_query = py::class_<monero::monero_output_query, monero::monero_output_wallet, std::shared_ptr<monero::monero_output_query>>(m, "MoneroOutputQuery");
  auto py_monero_tx_wallet = py::class_<monero::monero_tx_wallet, monero::monero_tx, std::shared_ptr<monero::monero_tx_wallet>>(m, "MoneroTxWallet");
  auto py_monero_tx_query = py::class_<monero::monero_tx_query, monero::monero_tx_wallet, std::shared_ptr<monero::monero_tx_query>>(m, "MoneroTxQuery");
  auto py_monero_tx_set = py::class_<monero::monero_tx_set, monero::serializable_struct, std::shared_ptr<monero::monero_tx_set>>(m, "MoneroTxSet");
  auto py_monero_integrated_address = py::class_<monero::monero_integrated_address,  monero::serializable_struct, std::shared_ptr<monero::monero_integrated_address>>(m, "MoneroIntegratedAddress");
  auto py_monero_decoded_address = py::class_<PyMoneroDecodedAddress, std::shared_ptr<PyMoneroDecodedAddress>>(m, "MoneroDecodedAddress");
  auto py_monero_tx_config = py::class_<monero::monero_tx_config, monero::serializable_struct, std::shared_ptr<monero::monero_tx_config>>(m, "MoneroTxConfig");
  auto py_monero_key_image_import_result = py::class_<monero::monero_key_image_import_result, monero::serializable_struct, std::shared_ptr<monero::monero_key_image_import_result>>(m, "MoneroKeyImageImportResult");
  auto py_monero_message_signature_result = py::class_<monero::monero_message_signature_result,  monero::serializable_struct, std::shared_ptr<monero::monero_message_signature_result>>(m, "MoneroMessageSignatureResult");
  auto py_monero_check = py::class_<monero::monero_check,  monero::serializable_struct, std::shared_ptr<monero::monero_check>>(m, "MoneroCheck");
  auto py_monero_check_tx = py::class_<monero::monero_check_tx, monero::monero_check, std::shared_ptr<monero::monero_check_tx>>(m, "MoneroCheckTx");
  auto py_monero_check_reserve = py::class_<monero::monero_check_reserve, monero::monero_check, std::shared_ptr<monero::monero_check_reserve>>(m, "MoneroCheckReserve");
  auto py_monero_multisig_info = py::class_<monero::monero_multisig_info, std::shared_ptr<monero_multisig_info>>(m, "MoneroMultisigInfo");
  auto py_monero_multisig_init_result = py::class_<monero::monero_multisig_init_result, std::shared_ptr<monero_multisig_init_result>>(m, "MoneroMultisigInitResult");
  auto py_monero_multisig_sign_result = py::class_<monero::monero_multisig_sign_result, std::shared_ptr<monero::monero_multisig_sign_result>>(m, "MoneroMultisigSignResult");
  auto py_monero_address_book_entry = py::class_<monero::monero_address_book_entry, std::shared_ptr<monero::monero_address_book_entry>>(m, "MoneroAddressBookEntry");
  auto py_monero_wallet_listener = py::class_<monero::monero_wallet_listener, PyMoneroWalletListener, std::shared_ptr<monero::monero_wallet_listener>>(m, "MoneroWalletListener");
  auto py_monero_daemon_listener = py::class_<PyMoneroDaemonListener, std::shared_ptr<PyMoneroDaemonListener>>(m, "MoneroDaemonListener");
  auto py_monero_daemon = py::class_<PyMoneroDaemon, std::shared_ptr<PyMoneroDaemon>>(m, "MoneroDaemon");
  auto py_monero_daemon_default = py::class_<PyMoneroDaemonDefault, PyMoneroDaemon, std::shared_ptr<PyMoneroDaemonDefault>>(m, "MoneroDaemonDefault");
  auto py_monero_daemon_rpc = py::class_<PyMoneroDaemonRpc, PyMoneroDaemonDefault, std::shared_ptr<PyMoneroDaemonRpc>>(m, "MoneroDaemonRpc");
  auto py_monero_wallet = py::class_<monero::monero_wallet, PyMoneroWallet, std::shared_ptr<monero::monero_wallet>>(m, "MoneroWallet");
  auto py_monero_wallet_keys = py::class_<monero::monero_wallet_keys, monero::monero_wallet, std::shared_ptr<monero::monero_wallet_keys>>(m, "MoneroWalletKeys");
  auto py_monero_wallet_full = py::class_<monero::monero_wallet_full, monero::monero_wallet, PyMoneroWalletFull, std::shared_ptr<monero_wallet_full>>(m, "MoneroWalletFull");
  auto py_monero_wallet_rpc = py::class_<PyMoneroWalletRpc, PyMoneroWallet, std::shared_ptr<PyMoneroWalletRpc>>(m, "MoneroWalletRpc");
  auto py_monero_utils = py::class_<PyMoneroUtils>(m, "MoneroUtils");


  py::bind_vector<std::vector<int>>(m, "VectorInt");
  py::bind_vector<std::vector<uint8_t>>(m, "VectorUint8");
  py::bind_vector<std::vector<uint32_t>>(m, "VectorUint32");
  py::bind_vector<std::vector<uint64_t>>(m, "VectorUint64");
  py::bind_vector<std::vector<std::string>>(m, "VectorString");
  py::bind_vector<std::vector<std::shared_ptr<monero::monero_block>>>(m, "VectorMoneroBlock");
  py::bind_vector<std::vector<std::shared_ptr<monero::monero_block_header>>>(m, "VectorMoneroBlockHeader");
  py::bind_vector<std::vector<std::shared_ptr<monero::monero_tx>>>(m, "VectorMoneroTx");
  py::bind_vector<std::vector<std::shared_ptr<monero::monero_tx_wallet>>>(m, "VectorMoneroTxWallet");
  py::bind_vector<std::vector<std::shared_ptr<monero::monero_output>>>(m, "VectorMoneroOutput");
  py::bind_vector<std::vector<std::shared_ptr<monero::monero_output_wallet>>>(m, "VectorMoneroOutputWallet");
  py::bind_vector<std::vector<std::shared_ptr<monero::monero_transfer>>>(m, "VectorMoneroTransfer");
  py::bind_vector<std::vector<std::shared_ptr<monero::monero_incoming_transfer>>>(m, "VectorMoneroIncomingTransfer");
  py::bind_vector<std::vector<std::shared_ptr<monero::monero_outgoing_transfer>>>(m, "VectorMoneroOutgoingTransfer");
  py::bind_vector<std::vector<monero::monero_subaddress>>(m, "VectorMoneroSubaddress");
  py::bind_vector<std::vector<std::shared_ptr<monero_destination>>>(m, "VectorMoneroDestination");

  // monero_error
  py::register_exception<std::runtime_error>(m, "MoneroError");

  py::exec(R"pybind(
    class MoneroRpcError(RuntimeError):
        def __init__(self, code: int, aMessage: str):
          self.code = code
          self.message = aMessage
          super().__init__(aMessage)
        def get_code(self) -> int:
          return self.code
        def get_message(self) -> str:
          return self.message
    )pybind",
    m.attr("__dict__"), m.attr("__dict__"));

  py::register_exception_translator([](std::exception_ptr p) {
    const auto setPyException = [](const char* pyTypeName, const auto& exc) {
      const py::object pyClass = py::module_::import("monero").attr(pyTypeName);
      const py::object pyInstance = pyClass(exc.code, exc.what());
      PyErr_SetObject(pyClass.ptr(), pyInstance.ptr());
    };

    try {
      if (p) std::rethrow_exception(p);
    }
    catch (const MoneroRpcError& exc) {
      setPyException("MoneroRpcError", exc);
    }
  });

  // enum monero_network_type
  py::enum_<monero::monero_network_type>(m, "MoneroNetworkType")
    .value("MAINNET", monero::monero_network_type::MAINNET)
    .value("TESTNET", monero::monero_network_type::TESTNET)
    .value("STAGENET", monero::monero_network_type::STAGENET);

  // enum monero_connection_type
  py::enum_<PyMoneroConnectionType>(m, "MoneroConnectionType")
    .value("INVALID", PyMoneroConnectionType::INVALID)
    .value("IPV4", PyMoneroConnectionType::IPV4)
    .value("IPV6", PyMoneroConnectionType::IPV6)
    .value("TOR", PyMoneroConnectionType::TOR)
    .value("I2P", PyMoneroConnectionType::I2P);

  // enum monero_key_image_spent_status
  py::enum_<PyMoneroKeyImageSpentStatus>(m, "MoneroKeyImageSpentStatus")
    .value("NOT_SPENT", PyMoneroKeyImageSpentStatus::NOT_SPENT)
    .value("CONFIRMED", PyMoneroKeyImageSpentStatus::CONFIRMED)
    .value("TX_POOL", PyMoneroKeyImageSpentStatus::TX_POOL);

  // enum monero_connection_pool_type
  py::enum_<PyMoneroConnectionPollType>(m, "MoneroConnectionPollType")
    .value("PRIORITIZED", PyMoneroConnectionPollType::PRIORITIZED)
    .value("CURRENT", PyMoneroConnectionPollType::CURRENT)
    .value("ALL", PyMoneroConnectionPollType::ALL)
    .value("UNDEFINED", PyMoneroConnectionPollType::UNDEFINED);

  // enum address_type
  py::enum_<PyMoneroAddressType>(m, "MoneroAddressType")
    .value("PRIMARY_ADDRESS", PyMoneroAddressType::PRIMARY_ADDRESS)
    .value("INTEGRATED_ADDRESS", PyMoneroAddressType::INTEGRATED_ADDRESS)
    .value("SUBADDRESS", PyMoneroAddressType::SUBADDRESS);
  
  // enum monero_tx_priority
  py::enum_<monero::monero_tx_priority>(m, "MoneroTxPriority")
    .value("DEFAULT", monero::monero_tx_priority::DEFAULT)
    .value("UNIMPORTANT", monero::monero_tx_priority::UNIMPORTANT)
    .value("NORMAL", monero::monero_tx_priority::NORMAL)
    .value("ELEVATED", monero::monero_tx_priority::ELEVATED);

  // enum monero_message_signature_type
  py::enum_<monero::monero_message_signature_type>(m, "MoneroMessageSignatureType")
    .value("SIGN_WITH_SPEND_KEY", monero::monero_message_signature_type::SIGN_WITH_SPEND_KEY)
    .value("SIGN_WITH_VIEW_KEY", monero::monero_message_signature_type::SIGN_WITH_VIEW_KEY);


  // serializable_struct
  py_serializable_struct
    .def(py::init<>())
    .def("serialize", [](monero::serializable_struct& self) {
      MONERO_CATCH_AND_RETHROW(self.serialize());
    });

  // monero_json_request_params
  py::class_<PyMoneroJsonRequestParams, PySerializableStruct, std::shared_ptr<PyMoneroJsonRequestParams>>(m, "MoneroJsonRequestParams")
    .def(py::init());

  // monero_json_request_empty_params
  py::class_<PyMoneroJsonRequestEmptyParams, PyMoneroJsonRequestParams, std::shared_ptr<PyMoneroJsonRequestEmptyParams>>(m, "MoneroJsonRequestEmptyParams")
    .def(py::init<>());
  
  // monero_request
  py::class_<PyMoneroRequest, PySerializableStruct, std::shared_ptr<PyMoneroRequest>>(m, "MoneroRequest")
    .def(py::init<>())
    .def_readwrite("method", &PyMoneroRequest::m_method);

  // monero_path_request
  py::class_<PyMoneroPathRequest, PyMoneroRequest, std::shared_ptr<PyMoneroPathRequest>>(m, "MoneroPathRequest")
    .def(py::init<>());
  
  // monero_json_request
  py::class_<PyMoneroJsonRequest, PyMoneroRequest, std::shared_ptr<PyMoneroJsonRequest>>(m, "MoneroJsonRequest")
    .def(py::init<>())
    .def(py::init<const PyMoneroJsonRequest&>(), py::arg("request"))
    .def(py::init<std::string&>(), py::arg("method"))
    .def(py::init<std::string&, std::shared_ptr<PyMoneroJsonRequestParams>>(), py::arg("method"), py::arg("params"))
    .def_readwrite("version", &PyMoneroJsonRequest::m_version)
    .def_readwrite("id", &PyMoneroJsonRequest::m_id)
    .def_readwrite("params", &PyMoneroJsonRequest::m_params);
  
  // monero_json_response
  py::class_<PyMoneroJsonResponse, std::shared_ptr<PyMoneroJsonResponse>>(m, "MoneroJsonResponse")
    .def(py::init<>())
    .def(py::init<const PyMoneroJsonResponse&>(), py::arg("response"))
    .def_static("deserialize", [](const std::string& response_json) {
      MONERO_CATCH_AND_RETHROW(PyMoneroJsonResponse::deserialize(response_json));
    }, py::arg("response_json"))
    .def_readwrite("jsonrpc", &PyMoneroJsonResponse::m_jsonrpc)
    .def_readwrite("id", &PyMoneroJsonResponse::m_id)
    .def("get_result", [](PyMoneroJsonResponse& self) {
      MONERO_CATCH_AND_RETHROW(self.get_result());
    });

  // monero_fee_estimate
  py::class_<PyMoneroFeeEstimate, std::shared_ptr<PyMoneroFeeEstimate>>(m, "MoneroFeeEstimate")
    .def(py::init<>())
    .def_readwrite("fee", &PyMoneroFeeEstimate::m_fee)
    .def_readwrite("fees", &PyMoneroFeeEstimate::m_fees)
    .def_readwrite("quantization_mask", &PyMoneroFeeEstimate::m_quantization_mask);

  // monero_tx_backlog_entry
  py::class_<PyMoneroTxBacklogEntry, std::shared_ptr<PyMoneroTxBacklogEntry>>(m, "MoneroTxBacklogEntry")
    .def(py::init<>());
  
  // monero_version
  py_monero_version
    .def(py::init<>())
    .def_readwrite("number", &monero::monero_version::m_number)
    .def_readwrite("is_release", &monero::monero_version::m_is_release);

  // monero_connection_priority_comparator
  py::class_<PyMoneroConnectionPriorityComparator, std::shared_ptr<PyMoneroConnectionPriorityComparator>>(m, "MoneroConnectionProriotyComparator")
    .def_static("compare", [](int p1, int p2) {
      MONERO_CATCH_AND_RETHROW(PyMoneroConnectionPriorityComparator::compare(p1, p2));
    }, py::arg("p1"), py::arg("p2"));

  // monero_rpc_connection
  py::class_<monero::monero_rpc_connection, PyMoneroRpcConnection, std::shared_ptr<monero_rpc_connection>>(m, "MoneroRpcConnection")
    .def(py::init<const std::string&, const std::string&, const::std::string&, const std::string&, int, uint64_t>(), py::arg("uri") = "", py::arg("username") = "", py::arg("password") = "", py::arg("zmq_uri") = "", py::arg("priority") = 0, py::arg("timeout") = 0)
    .def(py::init<PyMoneroRpcConnection&>(), py::arg("rpc"))
    .def_static("compare", [](const std::shared_ptr<PyMoneroRpcConnection> c1, const std::shared_ptr<PyMoneroRpcConnection> c2, std::shared_ptr<PyMoneroRpcConnection> current_connection) {
      MONERO_CATCH_AND_RETHROW(PyMoneroRpcConnection::compare(c1, c2, current_connection));
    }, py::arg("c1"), py::arg("c2"), py::arg("current_connection"))
    .def_readwrite("uri", &PyMoneroRpcConnection::m_uri)
    .def_readwrite("username", &PyMoneroRpcConnection::m_username)
    .def_readwrite("password", &PyMoneroRpcConnection::m_password)
    .def_property("proxy", 
      [](const PyMoneroRpcConnection& self) { return self.m_proxy; },
      [](PyMoneroRpcConnection& self, std::optional<std::string> val) { 
        if (val.has_value()) self.m_proxy = val.value();
        else self.m_proxy = boost::none; 
      })
    .def_property("zmq_uri", 
      [](const PyMoneroRpcConnection& self) { return self.m_zmq_uri; },
      [](PyMoneroRpcConnection& self, std::optional<std::string> val) { 
        if (val.has_value()) self.m_zmq_uri = val.value();
        else self.m_zmq_uri = boost::none; 
      })
    .def_property("priority", 
      [](const PyMoneroRpcConnection& self) { return self.m_priority; },
      [](PyMoneroRpcConnection& self, int val) { self.m_priority = val; })
    .def_property("timeout", 
      [](const PyMoneroRpcConnection& self) { return self.m_timeout; },
      [](PyMoneroRpcConnection& self, uint64_t val) { self.m_timeout = val; })
    .def_property("response_time", 
      [](const PyMoneroRpcConnection& self) { return self.m_response_time; },
      [](PyMoneroRpcConnection& self, std::optional<long> val) { 
        if (val.has_value()) self.m_response_time = val.value();
        else self.m_response_time = boost::none;
      })
    .def("set_attribute", [](PyMoneroRpcConnection& self, const std::string& key, const std::string& value) {
      MONERO_CATCH_AND_RETHROW(self.set_attribute(key, value));
    }, py::arg("key"), py::arg("value"))
    .def("get_attribute", [](PyMoneroRpcConnection& self, const std::string& key) {
      MONERO_CATCH_AND_RETHROW(self.get_attribute(key));
    }, py::arg("key"))
    .def("set_credentials", [](PyMoneroRpcConnection& self, const std::string& username, const std::string& password) {
      MONERO_CATCH_AND_RETHROW(self.set_credentials(username, password));
    }, py::arg("username"), py::arg("password"))
    .def("is_onion", [](PyMoneroRpcConnection& self) {
      MONERO_CATCH_AND_RETHROW(self.is_onion());
    })
    .def("is_i2p", [](PyMoneroRpcConnection& self) {
      MONERO_CATCH_AND_RETHROW(self.is_i2p());
    })
    .def("is_online", [](PyMoneroRpcConnection& self) {
      MONERO_CATCH_AND_RETHROW(self.is_online());
    })
    .def("is_authenticated", [](PyMoneroRpcConnection& self) {
      MONERO_CATCH_AND_RETHROW(self.is_authenticated());
    })
    .def("is_connected", [](PyMoneroRpcConnection& self) {
      MONERO_CATCH_AND_RETHROW(self.is_connected());
    })
    .def("check_connection", [](PyMoneroRpcConnection& self, int timeout_ms) {
      MONERO_CATCH_AND_RETHROW(self.check_connection(timeout_ms));
    }, py::arg("timeout_ms") = 2000)
    .def("send_json_request", [](PyMoneroRpcConnection& self, const std::string &method, const boost::optional<py::object> parameters) {
      MONERO_CATCH_AND_RETHROW(self.send_json_request(method, parameters));
    }, py::arg("method"), py::arg("parameters") = py::none())
    .def("send_path_request", [](PyMoneroRpcConnection& self, const std::string &method, const boost::optional<py::object> parameters) {
      MONERO_CATCH_AND_RETHROW(self.send_path_request(method, parameters));
    }, py::arg("method"), py::arg("parameters") = py::none())
    .def("send_binary_request", [](PyMoneroRpcConnection& self, const std::string &method, const boost::optional<py::object> parameters) {
      MONERO_CATCH_AND_RETHROW(self.send_binary_request(method, parameters));
    }, py::arg("method"), py::arg("parameters") = py::none());

  // monero_connection_manager_listener
  py::class_<monero_connection_manager_listener, PyMoneroConnectionManagerListener, std::shared_ptr<monero_connection_manager_listener>>(m, "MoneroConnectionManagerListener")
    .def(py::init<>())
    .def("on_connection_changed", [](monero_connection_manager_listener& self, std::shared_ptr<PyMoneroRpcConnection> &connection) {
      MONERO_CATCH_AND_RETHROW(self.on_connection_changed(connection));
    }, py::arg("connection"));

  // monero_connection_manager
  py::class_<PyMoneroConnectionManager, std::shared_ptr<PyMoneroConnectionManager>>(m, "MoneroConnectionManager")
    .def(py::init<>())
    .def("add_listener", [](PyMoneroConnectionManager& self, std::shared_ptr<PyMoneroConnectionManagerListener> &listener) {
      MONERO_CATCH_AND_RETHROW(self.add_listener(listener));
    }, py::arg("listener"))
    .def("remove_listener", [](PyMoneroConnectionManager& self, std::shared_ptr<PyMoneroConnectionManagerListener> &listener) {
      MONERO_CATCH_AND_RETHROW(self.remove_listener(listener));
    }, py::arg("listener"))
    .def("remove_listeners", [](PyMoneroConnectionManager& self) {
      MONERO_CATCH_AND_RETHROW(self.remove_listeners());
    })
    .def("get_listeners", [](PyMoneroConnectionManager& self) {
      MONERO_CATCH_AND_RETHROW(self.get_listeners());
    })
    .def("get_connection_by_uri", [](PyMoneroConnectionManager& self, const std::string& uri) {
      MONERO_CATCH_AND_RETHROW(self.get_connection_by_uri(uri));
    }, py::arg("uri"))
    .def("add_connection", [](PyMoneroConnectionManager& self, std::shared_ptr<PyMoneroRpcConnection> &connection) {
      MONERO_CATCH_AND_RETHROW(self.add_connection(connection));
    }, py::arg("connection"))
    .def("add_connection", [](PyMoneroConnectionManager& self, const std::string &uri) {
      MONERO_CATCH_AND_RETHROW(self.add_connection(uri));
    }, py::arg("uri"))
    .def("remove_connection", [](PyMoneroConnectionManager& self, const std::string &uri) {
      MONERO_CATCH_AND_RETHROW(self.remove_connection(uri));
    }, py::arg("uri"))
    .def("set_connection", [](PyMoneroConnectionManager& self, std::shared_ptr<PyMoneroRpcConnection> &connection) {
      MONERO_CATCH_AND_RETHROW(self.set_connection(connection));
    }, py::arg("connection"))
    .def("set_connection", [](PyMoneroConnectionManager& self, const std::string &uri) {
      MONERO_CATCH_AND_RETHROW(self.set_connection(uri));
    }, py::arg("uri"))
    .def("get_connection", [](PyMoneroConnectionManager& self) {
      MONERO_CATCH_AND_RETHROW(self.get_connection());
    })
    .def("has_connection", [](PyMoneroConnectionManager& self, const std::string &uri) {
      MONERO_CATCH_AND_RETHROW(self.has_connection(uri));
    }, py::arg("uri"))
    .def("get_connections", [](PyMoneroConnectionManager& self) {
      MONERO_CATCH_AND_RETHROW(self.get_connections());
    })
    .def("is_connected", [](PyMoneroConnectionManager& self) {
      MONERO_CATCH_AND_RETHROW(self.is_connected());
    })
    .def("check_connection", [](PyMoneroConnectionManager& self) {
      MONERO_CATCH_AND_RETHROW(self.check_connection());
    })
    .def("start_polling", [](PyMoneroConnectionManager& self, std::optional<uint64_t> period_ms, std::optional<bool> auto_switch, std::optional<uint64_t> timeout_ms, std::optional<PyMoneroConnectionPollType> poll_type, std::optional<std::vector<std::shared_ptr<PyMoneroRpcConnection>>> excluded_connections) {
      MONERO_CATCH_AND_RETHROW(self.start_polling(period_ms, auto_switch, timeout_ms, poll_type, excluded_connections));
    }, py::arg("period_ms") = py::none(), py::arg("auto_switch") = py::none(), py::arg("timeout_ms") = py::none(), py::arg("poll_type") = py::none(), py::arg("excluded_connections") = py::none())
    .def("stop_polling", [](PyMoneroConnectionManager& self) {
      MONERO_CATCH_AND_RETHROW(self.stop_polling());
    })
    .def("set_auto_switch", [](PyMoneroConnectionManager& self, bool auto_switch) {
      MONERO_CATCH_AND_RETHROW(self.set_auto_switch(auto_switch));
    }, py::arg("auto_switch"))
    .def("get_auto_switch", [](PyMoneroConnectionManager& self) {
      MONERO_CATCH_AND_RETHROW(self.get_auto_switch());
    })
    .def("set_timeout", [](PyMoneroConnectionManager& self, uint64_t timeout_ms) {
      MONERO_CATCH_AND_RETHROW(self.set_timeout(timeout_ms));
    }, py::arg("timeout_ms"))
    .def("get_timeout", [](PyMoneroConnectionManager& self) {
      MONERO_CATCH_AND_RETHROW(self.get_timeout());
    })
    .def("get_peer_connections", [](PyMoneroConnectionManager& self) {
      MONERO_CATCH_AND_RETHROW(self.get_peer_connections());
    })
    .def("disconnect", [](PyMoneroConnectionManager& self) {
      MONERO_CATCH_AND_RETHROW(self.disconnect());
    })
    .def("clear", [](PyMoneroConnectionManager& self) {
      MONERO_CATCH_AND_RETHROW(self.clear());
    })
    .def("reset", [](PyMoneroConnectionManager& self) {
      MONERO_CATCH_AND_RETHROW(self.reset());
    })
    .def("get_best_available_connection", [](PyMoneroConnectionManager& self, const std::set<std::shared_ptr<PyMoneroRpcConnection>>& excluded_connections) {
        MONERO_CATCH_AND_RETHROW(self.get_best_available_connection(excluded_connections));
    }, py::arg("excluded_connections"))
    .def("get_best_available_connection", [](PyMoneroConnectionManager& self, std::shared_ptr<PyMoneroRpcConnection>& excluded_connection) {
      MONERO_CATCH_AND_RETHROW(self.get_best_available_connection(excluded_connection));
    }, py::arg("excluded_connection"))
    .def("get_best_available_connection", [](PyMoneroConnectionManager& self) {
        MONERO_CATCH_AND_RETHROW(self.get_best_available_connection());
    })
    .def("check_connections", [](PyMoneroConnectionManager& self) {
        MONERO_CATCH_AND_RETHROW(self.check_connections());
    });

  // monero_block_header
  py_monero_block_header
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
    .def_readwrite("pow_hash", &monero::monero_block_header::m_pow_hash)
    .def("copy", [](monero::monero_block_header& self, const std::shared_ptr<monero::monero_block_header> &src,  const std::shared_ptr<monero::monero_block_header> &tgt) {
      MONERO_CATCH_AND_RETHROW(self.copy(src, tgt));
    }, py::arg("src"), py::arg("tgt"))
    .def("merge", [](monero::monero_block_header& self, const std::shared_ptr<monero::monero_block_header> _self, const std::shared_ptr<monero::monero_block_header> other) {
      MONERO_CATCH_AND_RETHROW(self.merge(_self, other));
    }, py::arg("_self"), py::arg("other"));

  // monero_block (needs: monero_tx)
  py_monero_block
    .def(py::init<>())
    .def_readwrite("hex", &monero::monero_block::m_hex)
    .def_readwrite("miner_tx", &monero::monero_block::m_miner_tx)
    .def_readwrite("txs", &monero::monero_block::m_txs)
    .def_readwrite("tx_hashes", &monero::monero_block::m_tx_hashes)
    .def("copy", [](monero::monero_block& self, const std::shared_ptr<monero::monero_block> &src,  const std::shared_ptr<monero::monero_block> &tgt) {
      MONERO_CATCH_AND_RETHROW(self.copy(src, tgt));
    }, py::arg("src"), py::arg("tgt"))
    .def("merge", [](monero::monero_block& self, const std::shared_ptr<monero::monero_block> _self, const std::shared_ptr<monero::monero_block> other) {
      MONERO_CATCH_AND_RETHROW(self.merge(_self, other));
    }, py::arg("_self"), py::arg("other"))
    .def("merge", [](monero::monero_block& self, const std::shared_ptr<monero::monero_block_header> _self, const std::shared_ptr<monero::monero_block_header> other) {
      MONERO_CATCH_AND_RETHROW(self.merge(_self, other));
    }, py::arg("_self"), py::arg("other"));

  // monero_block_template
  py::class_<PyMoneroBlockTemplate, std::shared_ptr<PyMoneroBlockTemplate>>(m, "MoneroBlockTemplate")
    .def(py::init<>())
    .def_readwrite("block_template_blob", &PyMoneroBlockTemplate::m_block_template_blob)
    .def_readwrite("block_hashing_blob", &PyMoneroBlockTemplate::m_block_hashing_blob)
    .def_readwrite("difficulty", &PyMoneroBlockTemplate::m_difficulty)
    .def_readwrite("expected_reward", &PyMoneroBlockTemplate::m_expected_reward)
    .def_readwrite("height", &PyMoneroBlockTemplate::m_height)
    .def_readwrite("prev_hash", &PyMoneroBlockTemplate::m_prev_hash)
    .def_readwrite("reserved_offset", &PyMoneroBlockTemplate::m_reserved_offset)
    .def_readwrite("seed_height", &PyMoneroBlockTemplate::m_seed_height)
    .def_readwrite("seed_hash", &PyMoneroBlockTemplate::m_seed_hash)
    .def_readwrite("next_seed_hash", &PyMoneroBlockTemplate::m_next_seed_hash);

  // monero_connection_span
  py::class_<PyMoneroConnectionSpan, std::shared_ptr<PyMoneroConnectionSpan>>(m, "MoneroConnectionSpan")
    .def(py::init<>())
    .def_readwrite("connection_id", &PyMoneroConnectionSpan::m_connection_id)
    .def_readwrite("num_blocks", &PyMoneroConnectionSpan::m_num_blocks)
    .def_readwrite("remote_address", &PyMoneroConnectionSpan::m_remote_address)
    .def_readwrite("rate", &PyMoneroConnectionSpan::m_rate)
    .def_readwrite("speed", &PyMoneroConnectionSpan::m_speed)
    .def_readwrite("size", &PyMoneroConnectionSpan::m_size)
    .def_readwrite("start_height", &PyMoneroConnectionSpan::m_start_height);

  // monero_peer
  py::class_<PyMoneroPeer, std::shared_ptr<PyMoneroPeer>>(m, "MoneroPeer")
    .def(py::init<>())
    .def_readwrite("id", &PyMoneroPeer::m_id)
    .def_readwrite("address", &PyMoneroPeer::m_address)
    .def_readwrite("host", &PyMoneroPeer::m_host)
    .def_readwrite("port", &PyMoneroPeer::m_port)
    .def_readwrite("is_online", &PyMoneroPeer::m_is_online)
    .def_readwrite("last_seen_timestamp", &PyMoneroPeer::m_last_seen_timestamp)
    .def_readwrite("pruning_seed", &PyMoneroPeer::m_pruning_seed)
    .def_readwrite("rpc_port", &PyMoneroPeer::m_rpc_port)
    .def_readwrite("rpc_credits_per_hash", &PyMoneroPeer::m_rpc_credits_per_hash)
    .def_readwrite("hash", &PyMoneroPeer::m_hash)
    .def_readwrite("avg_download", &PyMoneroPeer::m_avg_download)
    .def_readwrite("avg_upload", &PyMoneroPeer::m_avg_upload)
    .def_readwrite("current_download", &PyMoneroPeer::m_current_download)
    .def_readwrite("current_upload", &PyMoneroPeer::m_current_upload)
    .def_readwrite("height", &PyMoneroPeer::m_height)
    .def_readwrite("is_incoming", &PyMoneroPeer::m_is_incoming)
    .def_readwrite("live_time", &PyMoneroPeer::m_live_time)
    .def_readwrite("is_local_ip", &PyMoneroPeer::m_is_local_ip)
    .def_readwrite("is_local_host", &PyMoneroPeer::m_is_local_host)
    .def_readwrite("num_receives", &PyMoneroPeer::m_num_receives)
    .def_readwrite("num_sends", &PyMoneroPeer::m_num_sends)
    .def_readwrite("receive_idle_time", &PyMoneroPeer::m_receive_idle_time)
    .def_readwrite("send_idle_time", &PyMoneroPeer::m_send_idle_time)
    .def_readwrite("state", &PyMoneroPeer::m_state)
    .def_readwrite("num_support_flags", &PyMoneroPeer::m_num_support_flags)
    .def_readwrite("connection_type", &PyMoneroPeer::m_connection_type);

  // monero_alt_chain
  py::class_<PyMoneroAltChain, std::shared_ptr<PyMoneroAltChain>>(m, "MoneroAltChain")
    .def(py::init<>())
    .def_readwrite("block_hashes", &PyMoneroAltChain::m_block_hashes)
    .def_readwrite("difficulty", &PyMoneroAltChain::m_difficulty)
    .def_readwrite("height", &PyMoneroAltChain::m_height)
    .def_readwrite("length", &PyMoneroAltChain::m_length)
    .def_readwrite("main_chain_parent_block_hash", &PyMoneroAltChain::m_main_chain_parent_block_hash);

  // monero_ban
  py::class_<PyMoneroBan, std::shared_ptr<PyMoneroBan>>(m, "MoneroBan")
    .def(py::init<>())
    .def_readwrite("host", &PyMoneroBan::m_host)
    .def_readwrite("ip", &PyMoneroBan::m_ip)
    .def_readwrite("is_banned", &PyMoneroBan::m_is_banned)
    .def_readwrite("seconds", &PyMoneroBan::m_seconds);
  
  // monero_output_distribution_entry
  py::class_<PyMoneroOutputDistributionEntry, std::shared_ptr<PyMoneroOutputDistributionEntry>>(m, "MoneroOutputDistributionEntry")
    .def(py::init<>())
    .def_readwrite("amount", &PyMoneroOutputDistributionEntry::m_amount)
    .def_readwrite("base", &PyMoneroOutputDistributionEntry::m_base)
    .def_readwrite("distribution", &PyMoneroOutputDistributionEntry::m_distribution)
    .def_readwrite("start_height", &PyMoneroOutputDistributionEntry::m_start_height);

  // monero_output_histogram_entry
  py::class_<PyMoneroOutputHistogramEntry, std::shared_ptr<PyMoneroOutputHistogramEntry>>(m, "MoneroOutputHistogramEntry")
    .def(py::init<>())
    .def_readwrite("amount", &PyMoneroOutputHistogramEntry::m_amount)
    .def_readwrite("num_instances", &PyMoneroOutputHistogramEntry::m_num_instances)
    .def_readwrite("unlocked_instances", &PyMoneroOutputHistogramEntry::m_unlocked_instances)
    .def_readwrite("recent_instances", &PyMoneroOutputHistogramEntry::m_recent_instances);

  // monero_hard_fork_info
  py::class_<PyMoneroHardForkInfo, std::shared_ptr<PyMoneroHardForkInfo>>(m, "MoneroHardForkInfo")
    .def(py::init<>())
    .def_readwrite("earliest_height", &PyMoneroHardForkInfo::m_earliest_height)
    .def_readwrite("is_enabled", &PyMoneroHardForkInfo::m_is_enabled)
    .def_readwrite("state", &PyMoneroHardForkInfo::m_state)
    .def_readwrite("threshold", &PyMoneroHardForkInfo::m_threshold)
    .def_readwrite("version", &PyMoneroHardForkInfo::m_version)
    .def_readwrite("num_votes", &PyMoneroHardForkInfo::m_num_votes)
    .def_readwrite("window", &PyMoneroHardForkInfo::m_window)
    .def_readwrite("voting", &PyMoneroHardForkInfo::m_voting)
    .def_readwrite("credits", &PyMoneroHardForkInfo::m_credits)
    .def_readwrite("top_block_hash", &PyMoneroHardForkInfo::m_top_block_hash);

  // monero_prune_result
  py::class_<PyMoneroPruneResult, std::shared_ptr<PyMoneroPruneResult>>(m, "MoneroPruneResult")
    .def(py::init<>())
    .def_readwrite("is_pruned", &PyMoneroPruneResult::m_is_pruned)
    .def_readwrite("pruning_seed", &PyMoneroPruneResult::m_pruning_seed);
  
  // monero_daemon_sync_info
  py::class_<PyMoneroDaemonSyncInfo, std::shared_ptr<PyMoneroDaemonSyncInfo>>(m, "MoneroDaemonSyncInfo")
    .def(py::init<>())
    .def_readwrite("height", &PyMoneroDaemonSyncInfo::m_height)
    .def_readwrite("peers", &PyMoneroDaemonSyncInfo::m_peers)
    .def_readwrite("spans", &PyMoneroDaemonSyncInfo::m_spans)
    .def_readwrite("target_height", &PyMoneroDaemonSyncInfo::m_target_height)
    .def_readwrite("next_needed_pruning_seed", &PyMoneroDaemonSyncInfo::m_next_needed_pruning_seed)
    .def_readwrite("overview", &PyMoneroDaemonSyncInfo::m_overview)
    .def_readwrite("credits", &PyMoneroDaemonSyncInfo::m_credits)
    .def_readwrite("top_block_hash", &PyMoneroDaemonSyncInfo::m_top_block_hash);
  
  // monero_daemon_info
  py::class_<PyMoneroDaemonInfo, std::shared_ptr<PyMoneroDaemonInfo>>(m, "MoneroDaemonInfo")
    .def(py::init<>())
    .def_readwrite("version", &PyMoneroDaemonInfo::m_version)
    .def_readwrite("num_alt_blocks", &PyMoneroDaemonInfo::m_num_alt_blocks)
    .def_readwrite("block_size_limit", &PyMoneroDaemonInfo::m_block_size_limit)
    .def_readwrite("block_size_median", &PyMoneroDaemonInfo::m_block_size_median)
    .def_readwrite("block_weight_limit", &PyMoneroDaemonInfo::m_block_weight_limit)
    .def_readwrite("block_weight_median", &PyMoneroDaemonInfo::m_block_weight_median)
    .def_readwrite("bootstrap_daemon_address", &PyMoneroDaemonInfo::m_bootstrap_daemon_address)
    .def_readwrite("difficulty", &PyMoneroDaemonInfo::m_difficulty)
    .def_readwrite("cumulative_difficulty", &PyMoneroDaemonInfo::m_cumulative_difficulty)
    .def_readwrite("free_space", &PyMoneroDaemonInfo::m_free_space)
    .def_readwrite("num_offline_peers", &PyMoneroDaemonInfo::m_num_offline_peers)
    .def_readwrite("num_online_peers", &PyMoneroDaemonInfo::m_num_online_peers)
    .def_readwrite("height", &PyMoneroDaemonInfo::m_height)
    .def_readwrite("height_without_bootstrap", &PyMoneroDaemonInfo::m_height_without_bootstrap)
    .def_readwrite("network_type", &PyMoneroDaemonInfo::m_network_type)
    .def_readwrite("is_offline", &PyMoneroDaemonInfo::m_is_offline)
    .def_readwrite("num_incoming_connections", &PyMoneroDaemonInfo::m_num_incoming_connections)
    .def_readwrite("num_outgoing_connections", &PyMoneroDaemonInfo::m_num_outgoing_connections)
    .def_readwrite("num_rpc_connections", &PyMoneroDaemonInfo::m_num_rpc_connections)
    .def_readwrite("start_timestamp", &PyMoneroDaemonInfo::m_start_timestamp)
    .def_readwrite("adjusted_timestamp", &PyMoneroDaemonInfo::m_adjusted_timestamp)
    .def_readwrite("target", &PyMoneroDaemonInfo::m_target)
    .def_readwrite("target_height", &PyMoneroDaemonInfo::m_target_height)
    .def_readwrite("top_block_hash", &PyMoneroDaemonInfo::m_top_block_hash)
    .def_readwrite("num_txs", &PyMoneroDaemonInfo::m_num_txs)
    .def_readwrite("num_txs_pool", &PyMoneroDaemonInfo::m_num_txs_pool)
    .def_readwrite("was_bootstrap_ever_used", &PyMoneroDaemonInfo::m_was_bootstrap_ever_used)
    .def_readwrite("database_size", &PyMoneroDaemonInfo::m_database_size)
    .def_readwrite("update_available", &PyMoneroDaemonInfo::m_update_available)
    .def_readwrite("credits", &PyMoneroDaemonInfo::m_credits)
    .def_readwrite("is_busy_syncing", &PyMoneroDaemonInfo::m_is_busy_syncing)
    .def_readwrite("is_synchronized", &PyMoneroDaemonInfo::m_is_synchronized)
    .def_readwrite("is_restricted", &PyMoneroDaemonInfo::m_is_restricted);

  // monero_daemon_update_check_result
  py::class_<PyMoneroDaemonUpdateCheckResult, std::shared_ptr<PyMoneroDaemonUpdateCheckResult>>(m, "MoneroDaemonUpdateCheckResult")
    .def(py::init<>())
    .def_readwrite("is_update_available", &PyMoneroDaemonUpdateCheckResult::m_is_update_available)
    .def_readwrite("version", &PyMoneroDaemonUpdateCheckResult::m_version)
    .def_readwrite("hash", &PyMoneroDaemonUpdateCheckResult::m_hash)
    .def_readwrite("auto_uri", &PyMoneroDaemonUpdateCheckResult::m_auto_uri)
    .def_readwrite("user_uri", &PyMoneroDaemonUpdateCheckResult::m_user_uri);

  // monero_daemon_update_check_result
  py::class_<PyMoneroDaemonUpdateDownloadResult, PyMoneroDaemonUpdateCheckResult, std::shared_ptr<PyMoneroDaemonUpdateDownloadResult>>(m, "MoneroDaemonUpdateDownloadResult")
    .def(py::init<>())
    .def_readwrite("download_path", &PyMoneroDaemonUpdateDownloadResult::m_download_path);

  // monero_submit_tx_result
  py::class_<PyMoneroSubmitTxResult, std::shared_ptr<PyMoneroSubmitTxResult>>(m, "MoneroSubmitTxResult")
    .def(py::init<>())
    .def_readwrite("is_good", &PyMoneroSubmitTxResult::m_is_good)
    .def_readwrite("is_relayed", &PyMoneroSubmitTxResult::m_is_relayed)
    .def_readwrite("is_double_spend", &PyMoneroSubmitTxResult::m_is_double_spend)
    .def_readwrite("is_fee_too_low", &PyMoneroSubmitTxResult::m_is_fee_too_low)
    .def_readwrite("is_mixin_too_low", &PyMoneroSubmitTxResult::m_is_mixin_too_low)
    .def_readwrite("has_invalid_input", &PyMoneroSubmitTxResult::m_has_invalid_input)
    .def_readwrite("has_invalid_output", &PyMoneroSubmitTxResult::m_has_invalid_output)
    .def_readwrite("has_too_few_outputs", &PyMoneroSubmitTxResult::m_has_too_few_outputs)
    .def_readwrite("is_overspend", &PyMoneroSubmitTxResult::m_is_overspend)
    .def_readwrite("is_too_big", &PyMoneroSubmitTxResult::m_is_too_big)
    .def_readwrite("sanity_check_failed", &PyMoneroSubmitTxResult::m_sanity_check_failed)
    .def_readwrite("reason", &PyMoneroSubmitTxResult::m_reason)
    .def_readwrite("credits", &PyMoneroSubmitTxResult::m_credits)
    .def_readwrite("top_block_hash", &PyMoneroSubmitTxResult::m_top_block_hash)
    .def_readwrite("is_tx_extra_too_big", &PyMoneroSubmitTxResult::m_is_tx_extra_too_big)
    .def_readwrite("is_nonzero_unlock_time", &PyMoneroSubmitTxResult::m_is_nonzero_unlock_time);

  // monero_tx_pool_stats
  py::class_<PyMoneroTxPoolStats, std::shared_ptr<PyMoneroTxPoolStats>>(m, "MoneroTxPoolStats")
    .def(py::init<>())
    .def_readwrite("num_txs", &PyMoneroTxPoolStats::m_num_txs)
    .def_readwrite("num_not_relayed", &PyMoneroTxPoolStats::m_num_not_relayed)
    .def_readwrite("num_failing", &PyMoneroTxPoolStats::m_num_failing)
    .def_readwrite("num_double_spends", &PyMoneroTxPoolStats::m_num_double_spends)
    .def_readwrite("num10m", &PyMoneroTxPoolStats::m_num10m)
    .def_readwrite("fee_total", &PyMoneroTxPoolStats::m_fee_total)
    .def_readwrite("bytes_max", &PyMoneroTxPoolStats::m_bytes_max)
    .def_readwrite("bytes_med", &PyMoneroTxPoolStats::m_bytes_med)
    .def_readwrite("bytes_min", &PyMoneroTxPoolStats::m_bytes_min)
    .def_readwrite("bytes_total", &PyMoneroTxPoolStats::m_bytes_total)
    .def_readwrite("histo98pc", &PyMoneroTxPoolStats::m_histo98pc)
    .def_readwrite("oldest_timestamp", &PyMoneroTxPoolStats::m_oldest_timestamp);
  
  // monero_mining_status
  py::class_<PyMoneroMiningStatus, std::shared_ptr<PyMoneroMiningStatus>>(m, "MoneroMiningStatus")
    .def(py::init<>())
    .def_readwrite("is_active", &PyMoneroMiningStatus::m_is_active)
    .def_readwrite("is_background", &PyMoneroMiningStatus::m_is_background)
    .def_readwrite("address", &PyMoneroMiningStatus::m_address)
    .def_readwrite("speed", &PyMoneroMiningStatus::m_speed)
    .def_readwrite("num_threads", &PyMoneroMiningStatus::m_num_threads);

  // monero_miner_tx_sum
  py::class_<PyMoneroMinerTxSum, std::shared_ptr<PyMoneroMinerTxSum>>(m, "MoneroMinerTxSum")
    .def(py::init<>())
    .def_readwrite("emission_sum", &PyMoneroMinerTxSum::m_emission_sum)
    .def_readwrite("fee_sum", &PyMoneroMinerTxSum::m_fee_sum);

  // monero_tx
  py_monero_tx
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
    .def_readwrite("signatures", &monero::monero_tx::m_signatures)
    .def("copy", [](monero::monero_tx& self, const std::shared_ptr<monero::monero_tx> &src,  const std::shared_ptr<monero::monero_tx> &tgt) {
      MONERO_CATCH_AND_RETHROW(self.copy(src, tgt));
    }, py::arg("src"), py::arg("tgt"))
    .def("merge", [](monero::monero_tx& self, const std::shared_ptr<monero::monero_tx> _self, const std::shared_ptr<monero::monero_tx> other) {
      MONERO_CATCH_AND_RETHROW(self.merge(_self, other));
    }, py::arg("_self"), py::arg("other"))
    .def("get_height", [](monero::monero_tx& self) {
      std::optional<uint64_t> height;
      boost::optional<uint64_t> b_height = self.get_height();
      if (b_height != boost::none) height = b_height.value();
      return height;
    });

  // monero_key_image
  py_monero_key_image
    .def(py::init<>())
    .def_static("deserialize_key_images", [](const std::string& key_images_json) {
      MONERO_CATCH_AND_RETHROW(monero::monero_key_image::deserialize_key_images(key_images_json));
    }, py::arg("key_images_json"))
    .def_readwrite("hex", &monero::monero_key_image::m_hex)
    .def_readwrite("signature", &monero::monero_key_image::m_signature)
    .def("copy", [](monero::monero_key_image& self, const std::shared_ptr<monero::monero_key_image> &src,  const std::shared_ptr<monero::monero_key_image> &tgt) {
      MONERO_CATCH_AND_RETHROW(self.copy(src, tgt));
    }, py::arg("src"), py::arg("tgt"))
    .def("merge", [](monero::monero_key_image& self, const std::shared_ptr<monero::monero_key_image> _self, const std::shared_ptr<monero::monero_key_image> other) {
      MONERO_CATCH_AND_RETHROW(self.merge(_self, other));
    }, py::arg("_self"), py::arg("other"));

  // monero_output
  py_monero_output
    .def(py::init<>())
    .def_readwrite("tx", &monero::monero_output::m_tx)
    .def_readwrite("key_image", &monero::monero_output::m_key_image)
    .def_readwrite("amount", &monero::monero_output::m_amount)
    .def_readwrite("index", &monero::monero_output::m_index)
    .def_readwrite("stealth_public_key", &monero::monero_output::m_stealth_public_key)
    .def_readwrite("ring_output_indices", &monero::monero_output::m_ring_output_indices)
    .def("copy", [](monero::monero_output& self, const std::shared_ptr<monero::monero_output> &src,  const std::shared_ptr<monero::monero_output> &tgt) {
      MONERO_CATCH_AND_RETHROW(self.copy(src, tgt));
    }, py::arg("src"), py::arg("tgt"))
    .def("merge", [](monero::monero_output& self, const std::shared_ptr<monero::monero_output> _self, const std::shared_ptr<monero::monero_output> other) {
      MONERO_CATCH_AND_RETHROW(self.merge(_self, other));
    }, py::arg("_self"), py::arg("other"));

  // monero_wallet_config
  py_monero_wallet_config
    .def(py::init<>())
    .def(py::init<const PyMoneroWalletConfig&>(), py::arg("config"))
    .def_static("deserialize", [](const std::string& config_json) {
      MONERO_CATCH_AND_RETHROW(monero::monero_wallet_config::deserialize(config_json));
    }, py::arg("config_json"))
    .def_readwrite("path", &monero::monero_wallet_config::m_path)
    .def_readwrite("password", &monero::monero_wallet_config::m_password)
    .def_readwrite("network_type", &monero::monero_wallet_config::m_network_type)
    .def_readwrite("server", &monero::monero_wallet_config::m_server)
    .def_readwrite("seed", &monero::monero_wallet_config::m_seed)
    .def_readwrite("seed_offset", &monero::monero_wallet_config::m_seed_offset)
    .def_readwrite("primary_address", &monero::monero_wallet_config::m_primary_address)
    .def_readwrite("private_view_key", &monero::monero_wallet_config::m_private_view_key)
    .def_readwrite("private_spend_key", &monero::monero_wallet_config::m_private_spend_key)
    .def_readwrite("save_current", &monero::monero_wallet_config::m_save_current)
    .def_readwrite("language", &monero::monero_wallet_config::m_language)
    .def_readwrite("restore_height", &monero::monero_wallet_config::m_restore_height)
    .def_readwrite("account_lookahead", &monero::monero_wallet_config::m_account_lookahead)
    .def_readwrite("subaddress_lookahead", &monero::monero_wallet_config::m_subaddress_lookahead)
    .def_readwrite("is_multisig", &monero::monero_wallet_config::m_is_multisig)
    .def_property("connection_manager", 
      [](const PyMoneroWalletConfig& self) { return self.m_connection_manager; },
      [](PyMoneroWalletConfig& self, std::optional<std::shared_ptr<PyMoneroConnectionManager>> val) { 
        if (val.has_value()) self.m_connection_manager = val.value();
        else self.m_connection_manager = boost::none; 
      })
    .def("copy", [](monero::monero_wallet_config& self) {
      MONERO_CATCH_AND_RETHROW(self.copy());
    });

  // monero_subaddress
  py_monero_subaddress
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
  py_monero_sync_result
    .def(py::init<>())
    .def(py::init<const uint16_t, const bool>(), py::arg("num_blocks_fetched"), py::arg("received_money"))
    .def_readwrite("num_blocks_fetched", &monero::monero_sync_result::m_num_blocks_fetched)
    .def_readwrite("received_money", &monero::monero_sync_result::m_received_money);

  // monero_account
  py_monero_account
    .def(py::init<>())
    .def_readwrite("index", &monero::monero_account::m_index)
    .def_readwrite("primary_address", &monero::monero_account::m_primary_address)
    .def_readwrite("balance", &monero::monero_account::m_balance)
    .def_readwrite("unlocked_balance", &monero::monero_account::m_unlocked_balance)
    .def_readwrite("tag", &monero::monero_account::m_tag)
    .def_readwrite("subaddresses", &monero::monero_account::m_subaddresses);

  // monero_account_tag
  py_monero_account_tag
    .def(py::init<>())
    .def(py::init<std::string&, std::string&>(), py::arg("tag"), py::arg("label"))
    .def(py::init<std::string&, std::string&, std::vector<uint32_t>>(), py::arg("tag"), py::arg("label"), py::arg("account_indices"))
    .def_readwrite("tag", &PyMoneroAccountTag::m_tag)
    .def_readwrite("label", &PyMoneroAccountTag::m_label)
    .def_readwrite("account_indices", &PyMoneroAccountTag::m_account_indices);

  // monero_destination
  py_monero_destination
    .def(py::init<>())
    .def(py::init<std::string>(), py::arg("address"))
    .def(py::init<std::string, uint64_t>(), py::arg("address"), py::arg("amount"))
    .def_readwrite("address", &monero::monero_destination::m_address)
    .def_readwrite("amount", &monero::monero_destination::m_amount)
    .def("copy", [](monero::monero_destination& self, const std::shared_ptr<monero_destination>& src, const std::shared_ptr<monero_destination>& tgt) {
      MONERO_CATCH_AND_RETHROW(self.copy(src, tgt));
    }, py::arg("src"), py::arg("tgt"));

  // monero_transfer
  py_monero_transfer
    .def(py::init<>())
    .def_readwrite("tx", &monero::monero_transfer::m_tx)
    .def_readwrite("account_index", &monero::monero_transfer::m_account_index)
    .def_readwrite("amount", &monero::monero_transfer::m_amount)
    .def("is_incoming", [](monero::monero_transfer& self) {
      MONERO_CATCH_AND_RETHROW(self.is_incoming());
    })
    .def("is_outgoing", [](monero::monero_transfer& self) {
      MONERO_CATCH_AND_RETHROW(self.is_outgoing());
    })
    .def("merge", [](monero::monero_transfer& self, const std::shared_ptr<monero::monero_transfer> _self, const std::shared_ptr<monero::monero_transfer> other) {
      MONERO_CATCH_AND_RETHROW(self.merge(_self, other));
    }, py::arg("_self"), py::arg("other"))
    .def("copy", [](monero::monero_transfer& self, const std::shared_ptr<monero::monero_transfer> &src,  const std::shared_ptr<monero::monero_transfer> &tgt) {
      MONERO_CATCH_AND_RETHROW(self.copy(src, tgt));
    }, py::arg("src"), py::arg("tgt"));
  
  // monero_incoming_transfer
  py_monero_incoming_transfer
    .def(py::init<>())
    .def_readwrite("address", &monero::monero_incoming_transfer::m_address)
    .def_readwrite("subaddress_index", &monero::monero_incoming_transfer::m_subaddress_index)
    .def_readwrite("num_suggested_confirmations", &monero::monero_incoming_transfer::m_num_suggested_confirmations)
    .def("merge", [](monero::monero_incoming_transfer& self, const std::shared_ptr<monero::monero_incoming_transfer> _self, const std::shared_ptr<monero::monero_incoming_transfer> other) {
      MONERO_CATCH_AND_RETHROW(self.merge(_self, other));
    }, py::arg("_self"), py::arg("other"))
    .def("copy", [](monero::monero_incoming_transfer& self, const std::shared_ptr<monero::monero_incoming_transfer> &src,  const std::shared_ptr<monero::monero_incoming_transfer> &tgt) {
      MONERO_CATCH_AND_RETHROW(self.copy(src, tgt));
    }, py::arg("src"), py::arg("tgt"))
    .def("copy", [](monero::monero_incoming_transfer& self, const std::shared_ptr<monero::monero_transfer> &src,  const std::shared_ptr<monero::monero_transfer> &tgt) {
      MONERO_CATCH_AND_RETHROW(self.copy(src, tgt));
    }, py::arg("src"), py::arg("tgt"));

  // monero_outgoing_transfer
  py_monero_outgoing_transfer
    .def(py::init<>())
    .def_readwrite("subaddress_indices", &monero::monero_outgoing_transfer::m_subaddress_indices)
    .def_readwrite("addresses", &monero::monero_outgoing_transfer::m_addresses)
    .def_readwrite("destinations", &monero::monero_outgoing_transfer::m_destinations)
    .def("merge", [](monero::monero_outgoing_transfer& self, const std::shared_ptr<monero::monero_outgoing_transfer> _self, const std::shared_ptr<monero::monero_outgoing_transfer> other) {
      MONERO_CATCH_AND_RETHROW(self.merge(_self, other));
    }, py::arg("_self"), py::arg("other"))
    .def("copy", [](monero::monero_outgoing_transfer& self, const std::shared_ptr<monero::monero_outgoing_transfer> &src,  const std::shared_ptr<monero::monero_incoming_transfer> &tgt) {
      MONERO_CATCH_AND_RETHROW(self.copy(src, tgt));
    }, py::arg("src"), py::arg("tgt"))
    .def("copy", [](monero::monero_outgoing_transfer& self, const std::shared_ptr<monero::monero_transfer> &src,  const std::shared_ptr<monero::monero_transfer> &tgt) {
      MONERO_CATCH_AND_RETHROW(self.copy(src, tgt));
    }, py::arg("src"), py::arg("tgt"));

  // monero_transfer_query
  py_monero_transfer_query
    .def(py::init<>())
    .def_static("deserialize_from_block", [](const std::string& transfer_query_json) {
      MONERO_CATCH_AND_RETHROW(monero::monero_transfer_query::deserialize_from_block(transfer_query_json));
    }, py::arg("transfer_query_json"))
    .def_readwrite("incoming", &monero::monero_transfer_query::m_is_incoming)
    .def_readwrite("address", &monero::monero_transfer_query::m_address)
    .def_readwrite("addresses", &monero::monero_transfer_query::m_addresses)
    .def_readwrite("address", &monero::monero_transfer_query::m_subaddress_index)
    .def_readwrite("subaddress_indices", &monero::monero_transfer_query::m_subaddress_indices)
    .def_readwrite("destinations", &monero::monero_transfer_query::m_destinations)
    .def_readwrite("has_destinations", &monero::monero_transfer_query::m_has_destinations)
    .def_readwrite("tx_query", &monero::monero_transfer_query::m_tx_query)
    .def("copy", [](monero::monero_transfer_query& self, const std::shared_ptr<monero::monero_transfer_query> &src,  const std::shared_ptr<monero::monero_transfer_query> &tgt) {
      MONERO_CATCH_AND_RETHROW(self.copy(src, tgt));
    }, py::arg("src"), py::arg("tgt"))
    .def("copy", [](monero::monero_transfer_query& self, const std::shared_ptr<monero::monero_transfer> &src,  const std::shared_ptr<monero::monero_transfer> &tgt) {
      MONERO_CATCH_AND_RETHROW(self.copy(src, tgt));
    }, py::arg("src"), py::arg("tgt"))
    .def("meets_criteria", [](monero::monero_transfer_query& self, monero_transfer_query* transfer, bool query_parent) {
      MONERO_CATCH_AND_RETHROW(self.meets_criteria(transfer, query_parent));
    }, py::arg("transfer"), py::arg("query_parent") = true);

  // monero_output_wallet
  py_monero_output_wallet
    .def(py::init<>())
    .def_readwrite("account_index", &monero::monero_output_wallet::m_account_index)
    .def_readwrite("subaddress_index", &monero::monero_output_wallet::m_subaddress_index)
    .def_readwrite("is_spent", &monero::monero_output_wallet::m_is_spent)
    .def_readwrite("is_frozen", &monero::monero_output_wallet::m_is_frozen)
    .def("copy", [](monero::monero_output_wallet& self, const std::shared_ptr<monero::monero_output_wallet> &src,  const std::shared_ptr<monero::monero_output_wallet> &tgt) {
      MONERO_CATCH_AND_RETHROW(self.copy(src, tgt));
    }, py::arg("src"), py::arg("tgt"))  
    .def("copy", [](monero::monero_output_wallet& self, const std::shared_ptr<monero::monero_output> &src,  const std::shared_ptr<monero::monero_output> &tgt) {
      MONERO_CATCH_AND_RETHROW(self.copy(src, tgt));
    }, py::arg("src"), py::arg("tgt"))
    .def("merge", [](monero::monero_output_wallet& self, const std::shared_ptr<monero::monero_output_wallet> &_self,  const std::shared_ptr<monero::monero_output_wallet> &other) {
      MONERO_CATCH_AND_RETHROW(self.merge(_self, other));
    }, py::arg("_self"), py::arg("other"))
    .def("merge", [](monero::monero_output_wallet& self, const std::shared_ptr<monero::monero_output> &_self,  const std::shared_ptr<monero::monero_output> &other) {
      MONERO_CATCH_AND_RETHROW(self.merge(_self, other));
    }, py::arg("_self"), py::arg("other"));

  // monero_output_query
  py_monero_output_query
    .def(py::init<>())
    .def_static("deserialize_from_block", [](const std::string& output_query_json) {
      MONERO_CATCH_AND_RETHROW(monero::monero_output_query::deserialize_from_block(output_query_json));
    }, py::arg("output_query_json"))
    .def_readwrite("subaddress_indices", &monero::monero_output_query::m_subaddress_indices)
    .def_readwrite("min_amount", &monero::monero_output_query::m_min_amount)
    .def_readwrite("max_amount", &monero::monero_output_query::m_max_amount)
    .def_readwrite("tx_query", &monero::monero_output_query::m_tx_query)
    .def("copy", [](monero::monero_output_query& self, const std::shared_ptr<monero::monero_output_query> &src,  const std::shared_ptr<monero::monero_output_query> &tgt) {
      MONERO_CATCH_AND_RETHROW(self.copy(src, tgt));
    }, py::arg("src"), py::arg("tgt"))  
    .def("copy", [](monero::monero_output_query& self, const std::shared_ptr<monero::monero_output_wallet> &src,  const std::shared_ptr<monero::monero_output_wallet> &tgt) {
      MONERO_CATCH_AND_RETHROW(self.copy(src, tgt));
    }, py::arg("src"), py::arg("tgt"))
    .def("copy", [](monero::monero_output_query& self, const std::shared_ptr<monero::monero_output> &src,  const std::shared_ptr<monero::monero_output> &tgt) {
      MONERO_CATCH_AND_RETHROW(self.copy(src, tgt));
    }, py::arg("src"), py::arg("tgt"))
    .def("meets_criteria", [](monero::monero_output_query& self, monero_output_wallet* output, bool query_parent) {
      MONERO_CATCH_AND_RETHROW(self.meets_criteria(output, query_parent));
    }, py::arg("output"), py::arg("query_parent") = true);

  // monero_tx_wallet
  py_monero_tx_wallet
    .def(py::init<>())
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
    .def_readwrite("extra_hex", &monero::monero_tx_wallet::m_extra_hex)
    .def("get_transfers", [](monero::monero_tx_wallet& self) {
      MONERO_CATCH_AND_RETHROW(self.get_transfers());
    })
    .def("get_transfers", [](monero::monero_tx_wallet& self, const monero_transfer_query& query) {
      MONERO_CATCH_AND_RETHROW(self.get_transfers(query));
    }, py::arg("query"))
    .def("filter_transfers", [](monero::monero_tx_wallet& self, const monero_transfer_query& query) {
      MONERO_CATCH_AND_RETHROW(self.filter_transfers(query));
    }, py::arg("query"))
    .def("get_outputs_wallet", [](monero::monero_tx_wallet& self) {
      MONERO_CATCH_AND_RETHROW(self.get_outputs_wallet());
    })
    .def("get_outputs_wallet", [](monero::monero_tx_wallet& self, const monero_output_query& query) {
      MONERO_CATCH_AND_RETHROW(self.get_outputs_wallet(query));
    }, py::arg("query"))
    .def("filter_outputs_wallet", [](monero::monero_tx_wallet& self, const monero_output_query& query) {
      MONERO_CATCH_AND_RETHROW(self.filter_outputs_wallet(query));
    }, py::arg("query"))
    .def("copy", [](monero::monero_tx_wallet& self, const std::shared_ptr<monero::monero_tx_wallet> &src,  const std::shared_ptr<monero::monero_tx_wallet> &tgt) {
      MONERO_CATCH_AND_RETHROW(self.copy(src, tgt));
    }, py::arg("src"), py::arg("tgt"))  
    .def("copy", [](monero::monero_tx_wallet& self, const std::shared_ptr<monero::monero_tx> &src,  const std::shared_ptr<monero::monero_tx> &tgt) {
      MONERO_CATCH_AND_RETHROW(self.copy(src, tgt));
    }, py::arg("src"), py::arg("tgt"))
    .def("merge", [](monero::monero_tx_wallet& self, const std::shared_ptr<monero::monero_tx_wallet> &_self,  const std::shared_ptr<monero::monero_tx_wallet> &tgt) {
      MONERO_CATCH_AND_RETHROW(self.merge(_self, tgt));
    }, py::arg("_self"), py::arg("tgt"))
    .def("merge", [](monero::monero_tx_wallet& self, const std::shared_ptr<monero::monero_tx> &_self,  const std::shared_ptr<monero::monero_tx> &tgt) {
      MONERO_CATCH_AND_RETHROW(self.merge(_self, tgt));
    }, py::arg("_self"), py::arg("tgt"));

  // monero_tx_query
  py_monero_tx_query
    .def(py::init<>())
    .def_static("deserialize_from_block", [](const std::string& tx_query_json) {
      MONERO_CATCH_AND_RETHROW(monero::monero_tx_query::deserialize_from_block(tx_query_json));
    }, py::arg("tx_query_json"))
    .def_readwrite("is_outgoing", &monero::monero_tx_query::m_is_outgoing)
    .def_readwrite("is_incoming", &monero::monero_tx_query::m_is_incoming)
    .def_readwrite("hashes", &monero::monero_tx_query::m_hashes)
    .def_readwrite("has_payment_id", &monero::monero_tx_query::m_has_payment_id)
    .def_readwrite("payment_ids", &monero::monero_tx_query::m_payment_ids)
    .def_readwrite("height", &monero::monero_tx_query::m_height)
    .def_readwrite("min_height", &monero::monero_tx_query::m_min_height)
    .def_readwrite("max_height", &monero::monero_tx_query::m_max_height)
    .def_readwrite("include_outputs", &monero::monero_tx_query::m_include_outputs)
    .def_readwrite("transfer_query", &monero::monero_tx_query::m_transfer_query)
    .def_readwrite("input_query", &monero::monero_tx_query::m_input_query)
    .def_readwrite("output_query", &monero::monero_tx_query::m_output_query)
    .def("copy", [](monero::monero_tx_query& self, const std::shared_ptr<monero::monero_tx_query> &src,  const std::shared_ptr<monero::monero_tx_query> &tgt) {
      MONERO_CATCH_AND_RETHROW(self.copy(src, tgt));
    }, py::arg("src"), py::arg("tgt"))  
    .def("copy", [](monero::monero_tx_query& self, const std::shared_ptr<monero::monero_tx_wallet> &src,  const std::shared_ptr<monero::monero_tx_wallet> &tgt) {
      MONERO_CATCH_AND_RETHROW(self.copy(src, tgt));
    }, py::arg("src"), py::arg("tgt"))
    .def("copy", [](monero::monero_tx_query& self, const std::shared_ptr<monero::monero_tx> &src,  const std::shared_ptr<monero::monero_tx> &tgt) {
      MONERO_CATCH_AND_RETHROW(self.copy(src, tgt));
    }, py::arg("src"), py::arg("tgt"))
    .def("meets_criteria", [](monero::monero_tx_query& self, monero_tx_wallet* tx, bool query_children) {
      MONERO_CATCH_AND_RETHROW(self.meets_criteria(tx, query_children));
    }, py::arg("tx"), py::arg("query_children") = false);

  // monero_tx_set
  py_monero_tx_set
    .def(py::init<>())
    .def_static("deserialize", [](const std::string& tx_set_json) {
      MONERO_CATCH_AND_RETHROW(monero::monero_tx_set::deserialize(tx_set_json));
    }, py::arg("tx_set_json"))
    .def_readwrite("txs", &monero::monero_tx_set::m_txs)
    .def_readwrite("signed_tx_hex", &monero::monero_tx_set::m_signed_tx_hex)
    .def_readwrite("unsigned_tx_hex", &monero::monero_tx_set::m_unsigned_tx_hex)
    .def_readwrite("multisig_tx_hex", &monero::monero_tx_set::m_multisig_tx_hex);

  // monero_integrated_address
  py_monero_integrated_address
    .def(py::init<>())
    .def_readwrite("standard_address", &monero::monero_integrated_address::m_standard_address)
    .def_readwrite("payment_id", &monero::monero_integrated_address::m_payment_id)
    .def_readwrite("integrated_address", &monero::monero_integrated_address::m_integrated_address);

  // monero_decoded_address
  py_monero_decoded_address
    .def(py::init<std::string&, PyMoneroAddressType, monero::monero_network_type>(), py::arg("address"), py::arg("address_type"), py::arg("network_type"))
    .def_readwrite("address", &PyMoneroDecodedAddress::m_address)
    .def_readwrite("address_type", &PyMoneroDecodedAddress::m_address_type)
    .def_readwrite("network_type", &PyMoneroDecodedAddress::m_network_type);

  // monero_tx_config
  py_monero_tx_config
    .def(py::init<>())
    .def(py::init<monero::monero_tx_config&>(), py::arg("config"))
    .def_static("deserialize", [](const std::string& config_json) {
      MONERO_CATCH_AND_RETHROW(monero::monero_tx_config::deserialize(config_json));
    }, py::arg("config_json"))
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
    .def_readwrite("key_image", &monero::monero_tx_config::m_key_image)
    .def("copy", [](monero::monero_tx_config& self) {
      MONERO_CATCH_AND_RETHROW(self.copy());
    })
    .def("get_normalized_destinations", [](monero::monero_tx_config& self) {
      MONERO_CATCH_AND_RETHROW(self.get_normalized_destinations());
    });    

  // monero_key_image_import_result
  py_monero_key_image_import_result
    .def(py::init<>())
    .def_readwrite("height", &monero::monero_key_image_import_result::m_height)
    .def_readwrite("spent_amount", &monero::monero_key_image_import_result::m_spent_amount)
    .def_readwrite("unspent_amount", &monero::monero_key_image_import_result::m_unspent_amount);

  // monero_message_signature_result
  py_monero_message_signature_result
    .def(py::init<>())
    .def_readwrite("is_good", &monero::monero_message_signature_result::m_is_good)
    .def_readwrite("version", &monero::monero_message_signature_result::m_version)
    .def_readwrite("is_old", &monero::monero_message_signature_result::m_is_old)
    .def_readwrite("signature_type", &monero::monero_message_signature_result::m_signature_type);

  // monero_check
  py_monero_check
    .def(py::init<>())
    .def_readwrite("is_good", &monero::monero_check::m_is_good);
  
  // monero_check_tx
  py_monero_check_tx
    .def(py::init<>())
    .def_readwrite("in_tx_pool", &monero::monero_check_tx::m_in_tx_pool)
    .def_readwrite("num_confirmations", &monero::monero_check_tx::m_num_confirmations)
    .def_readwrite("received_amount", &monero::monero_check_tx::m_received_amount);
  
  // monero_check_reserve
  py_monero_check_reserve
    .def(py::init<>())
    .def_readwrite("total_amount", &monero::monero_check_reserve::m_total_amount)
    .def_readwrite("unconfirmed_spent_amount", &monero::monero_check_reserve::m_unconfirmed_spent_amount);
 
  // monero_multisig_info
  py_monero_multisig_info
    .def(py::init<>())
    .def_readwrite("is_multisig", &monero::monero_multisig_info::m_is_multisig)
    .def_readwrite("is_ready", &monero::monero_multisig_info::m_is_ready)
    .def_readwrite("threshold", &monero::monero_multisig_info::m_threshold)
    .def_readwrite("num_participants", &monero::monero_multisig_info::m_num_participants);
  
  // monero_multisig_init_result
  py_monero_multisig_init_result
    .def(py::init<>())
    .def_readwrite("address", &monero::monero_multisig_init_result::m_address)
    .def_readwrite("multisig_hex", &monero::monero_multisig_init_result::m_multisig_hex);

  // monero_multisig_sign_result
  py_monero_multisig_sign_result
    .def(py::init<>())
    .def_readwrite("signed_multisig_tx_hex", &monero::monero_multisig_sign_result::m_signed_multisig_tx_hex)
    .def_readwrite("tx_hashes", &monero::monero_multisig_sign_result::m_tx_hashes);

  // monero_address_book_entry
  py_monero_address_book_entry
    .def(py::init<>())
    .def(py::init<uint64_t, const std::string&, const std::string&>(), py::arg("index"), py::arg("address"), py::arg("description"))
    .def(py::init<uint64_t, const std::string&, const std::string&, const std::string&>(), py::arg("index"), py::arg("address"), py::arg("description"), py::arg("payment_id"))
    .def_readwrite("index", &monero::monero_address_book_entry::m_index)
    .def_readwrite("address", &monero::monero_address_book_entry::m_address)
    .def_readwrite("description", &monero::monero_address_book_entry::m_description)
    .def_readwrite("payment_id", &monero::monero_address_book_entry::m_payment_id);
  
  // monero_wallet_listener
  py_monero_wallet_listener
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
  
  // monero_daemon_listener
  py_monero_daemon_listener
    .def(py::init<>())
    .def_readwrite("last_header", &PyMoneroDaemonListener::m_last_header)
    .def("on_block_header", [](PyMoneroDaemonListener& self, const std::shared_ptr<monero::monero_block_header>& header) {
      MONERO_CATCH_AND_RETHROW(self.on_block_header(header));
    }, py::arg("header"));

  // monero_daemon
  py_monero_daemon
    .def(py::init<>())
    .def("add_listener", [](PyMoneroDaemon& self, const std::shared_ptr<PyMoneroDaemonListener> &listener) {
      MONERO_CATCH_AND_RETHROW(self.add_listener(listener));
    }, py::arg("listener"))
    .def("remove_listener", [](PyMoneroDaemon& self, const std::shared_ptr<PyMoneroDaemonListener> &listener) {
      MONERO_CATCH_AND_RETHROW(self.remove_listener(listener));
    }, py::arg("listener"))
    .def("get_listeners", [](PyMoneroDaemon& self) {
      MONERO_CATCH_AND_RETHROW(self.get_listeners());
    })
    .def("get_version", [](PyMoneroDaemon& self) {
      MONERO_CATCH_AND_RETHROW(self.get_version());
    })
    .def("is_trusted", [](PyMoneroDaemon& self) {
      MONERO_CATCH_AND_RETHROW(self.is_trusted());
    })
    .def("get_height", [](PyMoneroDaemon& self) {
      MONERO_CATCH_AND_RETHROW(self.get_height());
    })
    .def("get_block_hash", [](PyMoneroDaemon& self, uint64_t height) {
      MONERO_CATCH_AND_RETHROW(self.get_block_hash(height));
    }, py::arg("height"))
    .def("get_block_template", [](PyMoneroDaemon& self, std::string& wallet_address) {
      MONERO_CATCH_AND_RETHROW(self.get_block_template(wallet_address));
    }, py::arg("wallet_address"))
    .def("get_block_template", [](PyMoneroDaemon& self, std::string& wallet_address, int reserve_size) {
      MONERO_CATCH_AND_RETHROW(self.get_block_template(wallet_address, reserve_size));
    }, py::arg("wallet_address"), py::arg("reserve_size"))
    .def("get_last_block_header", [](PyMoneroDaemon& self) {
      MONERO_CATCH_AND_RETHROW(self.get_last_block_header());
    })
    .def("get_block_header_by_hash", [](PyMoneroDaemon& self, std::string& hash) {
      MONERO_CATCH_AND_RETHROW(self.get_block_header_by_hash(hash));
    }, py::arg("hash"))
    .def("get_block_header_by_height", [](PyMoneroDaemon& self, uint64_t height) {
      MONERO_CATCH_AND_RETHROW(self.get_block_header_by_height(height));
    }, py::arg("height"))
    .def("get_block_headers_by_range", [](PyMoneroDaemon& self, uint64_t start_height, uint64_t end_height) {
      MONERO_CATCH_AND_RETHROW(self.get_block_headers_by_range(start_height, end_height));
    }, py::arg("start_height"), py::arg("end_height"))
    .def("get_block_by_hash", [](PyMoneroDaemon& self, std::string& hash) {
      MONERO_CATCH_AND_RETHROW(self.get_block_by_hash(hash));
    }, py::arg("hash"))
    .def("get_blocks_by_hash", [](PyMoneroDaemon& self, const std::vector<std::string>& block_hashes, uint64_t start_height, bool prune) {
      MONERO_CATCH_AND_RETHROW(self.get_blocks_by_hash(block_hashes, start_height, prune));
    }, py::arg("block_hashes"), py::arg("start_height"), py::arg("prune"))
    .def("get_block_by_height", [](PyMoneroDaemon& self, uint64_t height) {
      MONERO_CATCH_AND_RETHROW(self.get_block_by_height(height));
    }, py::arg("height"))
    .def("get_blocks_by_height", [](PyMoneroDaemon& self, std::vector<uint64_t> heights) {
      MONERO_CATCH_AND_RETHROW(self.get_blocks_by_height(heights));
    }, py::arg("heights"))
    .def("get_blocks_by_range", [](PyMoneroDaemon& self, uint64_t start_height, uint64_t end_height) {
      MONERO_CATCH_AND_RETHROW(self.get_blocks_by_range(start_height, end_height));
    }, py::arg("start_height"), py::arg("end_height"))
    .def("get_blocks_by_range_chunked", [](PyMoneroDaemon& self, uint64_t start_height, uint64_t end_height) {
      MONERO_CATCH_AND_RETHROW(self.get_blocks_by_range_chunked(start_height, end_height));
    }, py::arg("start_height"), py::arg("end_height"))
    .def("get_blocks_by_range_chunked", [](PyMoneroDaemon& self, uint64_t start_height, uint64_t end_height, uint64_t max_chunk_size) {
      MONERO_CATCH_AND_RETHROW(self.get_blocks_by_range_chunked(start_height, end_height, max_chunk_size));
    }, py::arg("start_height"), py::arg("end_height"), py::arg("max_chunk_size"))
    .def("get_block_hashes", [](PyMoneroDaemon& self, const std::vector<std::string>& block_hashes, uint64_t start_height) {
      MONERO_CATCH_AND_RETHROW(self.get_block_hashes(block_hashes, start_height));
    }, py::arg("block_hashes"), py::arg("start_height"))
    .def("get_tx", [](PyMoneroDaemon& self, const std::string& tx_hash, bool prune) {
      MONERO_CATCH_AND_RETHROW(self.get_tx(tx_hash, prune));
    }, py::arg("tx_hash"), py::arg("prune") = false)
    .def("get_txs", [](PyMoneroDaemon& self, const std::vector<std::string>& tx_hashes, bool prune) {
      MONERO_CATCH_AND_RETHROW(self.get_txs(tx_hashes, prune));
    }, py::arg("tx_hashes"), py::arg("prune") = false)
    .def("get_tx_hex", [](PyMoneroDaemon& self, const std::string& tx_hash, bool prune) {
      MONERO_CATCH_AND_RETHROW(self.get_tx_hex(tx_hash, prune));
    }, py::arg("tx_hash"), py::arg("prune") = false)
    .def("get_tx_hexes", [](PyMoneroDaemon& self, const std::vector<std::string>& tx_hashes, bool prune) {
      MONERO_CATCH_AND_RETHROW(self.get_tx_hexes(tx_hashes, prune));
    }, py::arg("tx_hashes"), py::arg("prune") = false)
    .def("get_miner_tx_sum", [](PyMoneroDaemon& self, uint64_t height, uint64_t num_blocks) {
      MONERO_CATCH_AND_RETHROW(self.get_miner_tx_sum(height, num_blocks));
    }, py::arg("height"), py::arg("num_blocks"))
    .def("get_fee_estimate", [](PyMoneroDaemon& self, uint64_t grace_blocks) {
      MONERO_CATCH_AND_RETHROW(self.get_fee_estimate(grace_blocks));
    }, py::arg("grace_blocks") = 0)
    .def("submit_tx_hex", [](PyMoneroDaemon& self, std::string& tx_hex, bool do_not_relay) {
      MONERO_CATCH_AND_RETHROW(self.submit_tx_hex(tx_hex, do_not_relay));
    }, py::arg("tx_hex"), py::arg("do_not_relay") = false)
    .def("relay_tx_by_hash", [](PyMoneroDaemon& self, std::string& tx_hash) {
      MONERO_CATCH_AND_RETHROW(self.relay_tx_by_hash(tx_hash));
    }, py::arg("tx_hash"))
    .def("relay_txs_by_hash", [](PyMoneroDaemon& self, std::vector<std::string>& tx_hashes) {
      MONERO_CATCH_AND_RETHROW(self.relay_txs_by_hash(tx_hashes));
    }, py::arg("tx_hashes"))
    .def("get_tx_pool", [](PyMoneroDaemon& self) {
      MONERO_CATCH_AND_RETHROW(self.get_tx_pool());
    })
    .def("get_tx_pool_hashes", [](PyMoneroDaemon& self) {
      MONERO_CATCH_AND_RETHROW(self.get_tx_pool_hashes());
    })
    .def("get_tx_pool_backlog", [](PyMoneroDaemon& self) {
      MONERO_CATCH_AND_RETHROW(self.get_tx_pool_backlog());
    })
    .def("get_tx_pool_stats", [](PyMoneroDaemon& self) {
      MONERO_CATCH_AND_RETHROW(self.get_tx_pool_stats());
    })
    .def("flush_tx_pool", [](PyMoneroDaemon& self) {
      MONERO_CATCH_AND_RETHROW(self.flush_tx_pool());
    })
    .def("flush_tx_pool", [](PyMoneroDaemon& self, std::vector<std::string>& hashes) {
      MONERO_CATCH_AND_RETHROW(self.flush_tx_pool(hashes));
    }, py::arg("hashes"))
    .def("get_key_image_spent_status", [](PyMoneroDaemon& self, std::string& key_image) {
      MONERO_CATCH_AND_RETHROW(self.get_key_image_spent_status(key_image));
    }, py::arg("key_image"))
    .def("get_key_image_spent_statuses", [](PyMoneroDaemon& self, std::vector<std::string>& key_images) {
      MONERO_CATCH_AND_RETHROW(self.get_key_image_spent_statuses(key_images));
    }, py::arg("key_images"))
    .def("get_outputs", [](PyMoneroDaemon& self, std::vector<monero::monero_output>& outputs) {
      MONERO_CATCH_AND_RETHROW(self.get_outputs(outputs));
    }, py::arg("outputs"))
    .def("get_output_histogram", [](PyMoneroDaemon& self, std::vector<uint64_t>& amounts, int min_count, int max_count, bool is_unlocked, int recent_cutoff) {
      MONERO_CATCH_AND_RETHROW(self.get_output_histogram(amounts, min_count, max_count, is_unlocked, recent_cutoff));
    }, py::arg("amounts"), py::arg("min_count"), py::arg("max_count"), py::arg("is_unlocked"), py::arg("recent_cutoff"))
    .def("get_output_distribution", [](PyMoneroDaemon& self, std::vector<uint64_t>& amounts) {
      MONERO_CATCH_AND_RETHROW(self.get_output_distribution(amounts));
    }, py::arg("amounts"))
    .def("get_output_distribution", [](PyMoneroDaemon& self, std::vector<uint64_t>& amounts, bool is_cumulative, uint64_t start_height, uint64_t end_height) {
      MONERO_CATCH_AND_RETHROW(self.get_output_distribution(amounts, is_cumulative, start_height, end_height));
    }, py::arg("amounts"), py::arg("is_cumulative"), py::arg("start_height"), py::arg("end_height"))
    .def("get_info", [](PyMoneroDaemon& self) {
      MONERO_CATCH_AND_RETHROW(self.get_info());
    })
    .def("get_sync_info", [](PyMoneroDaemon& self) {
      MONERO_CATCH_AND_RETHROW(self.get_sync_info());
    })
    .def("get_hard_fork_info", [](PyMoneroDaemon& self) {
      MONERO_CATCH_AND_RETHROW(self.get_hard_fork_info());
    })
    .def("get_alt_chains", [](PyMoneroDaemon& self) {
      MONERO_CATCH_AND_RETHROW(self.get_alt_chains());
    })
    .def("get_alt_block_hashes", [](PyMoneroDaemon& self) {
      MONERO_CATCH_AND_RETHROW(self.get_alt_block_hashes());
    })
    .def("get_download_limit", [](PyMoneroDaemon& self) {
      MONERO_CATCH_AND_RETHROW(self.get_download_limit());
    })
    .def("set_download_limit", [](PyMoneroDaemon& self, int limit) {
      MONERO_CATCH_AND_RETHROW(self.set_download_limit(limit));
    }, py::arg("limit"))
    .def("reset_download_limit", [](PyMoneroDaemon& self) {
      MONERO_CATCH_AND_RETHROW(self.reset_download_limit());
    })
    .def("get_upload_limit", [](PyMoneroDaemon& self) {
      MONERO_CATCH_AND_RETHROW(self.get_upload_limit());
    })
    .def("set_upload_limit", [](PyMoneroDaemon& self, int limit) {
      MONERO_CATCH_AND_RETHROW(self.set_upload_limit(limit));
    }, py::arg("limit"))
    .def("reset_upload_limit", [](PyMoneroDaemon& self) {
      MONERO_CATCH_AND_RETHROW(self.reset_upload_limit());
    })
    .def("get_peers", [](PyMoneroDaemon& self) {
      MONERO_CATCH_AND_RETHROW(self.get_peers());
    })
    .def("get_known_peers", [](PyMoneroDaemon& self) {
      MONERO_CATCH_AND_RETHROW(self.get_known_peers());
    })
    .def("set_outgoing_peer_limit", [](PyMoneroDaemon& self, int limit) {
      MONERO_CATCH_AND_RETHROW(self.set_outgoing_peer_limit(limit));
    }, py::arg("limit"))
    .def("set_incoming_peer_limit", [](PyMoneroDaemon& self, int limit) {
      MONERO_CATCH_AND_RETHROW(self.set_incoming_peer_limit(limit));
    }, py::arg("limit"))
    .def("get_peer_bans", [](PyMoneroDaemon& self) {
      MONERO_CATCH_AND_RETHROW(self.get_peer_bans());
    })
    .def("set_peer_bans", [](PyMoneroDaemon& self, std::vector<std::shared_ptr<PyMoneroBan>> bans) {
      MONERO_CATCH_AND_RETHROW(self.set_peer_bans(bans));
    }, py::arg("bans"))
    .def("set_peer_ban", [](PyMoneroDaemon& self, std::shared_ptr<PyMoneroBan> ban) {
      MONERO_CATCH_AND_RETHROW(self.set_peer_ban(ban));
    }, py::arg("ban"))
    .def("start_mining", [](PyMoneroDaemon& self, std::string& address, uint64_t num_threads, bool is_background, bool ignore_battery) {
      MONERO_CATCH_AND_RETHROW(self.start_mining(address, num_threads, is_background, ignore_battery));
    }, py::arg("address"), py::arg("num_threads"), py::arg("is_background"), py::arg("ignore_battery"))
    .def("stop_mining", [](PyMoneroDaemon& self) {
      MONERO_CATCH_AND_RETHROW(self.stop_mining());
    })
    .def("get_mining_status", [](PyMoneroDaemon& self) {
      MONERO_CATCH_AND_RETHROW(self.get_mining_status());
    })
    .def("submit_block", [](PyMoneroDaemon& self, std::string& block_blob) {
      MONERO_CATCH_AND_RETHROW(self.submit_block(block_blob));
    }, py::arg("block_blob"))
    .def("submit_blocks", [](PyMoneroDaemon& self, std::vector<std::string>& block_blobs) {
      MONERO_CATCH_AND_RETHROW(self.submit_blocks(block_blobs));
    }, py::arg("block_blobs"))
    .def("prune_blockchain", [](PyMoneroDaemon& self, bool check) {
      MONERO_CATCH_AND_RETHROW(self.prune_blockchain(check));
    }, py::arg("check"))
    .def("check_for_update", [](PyMoneroDaemon& self) {
      MONERO_CATCH_AND_RETHROW(self.check_for_update());
    })
    .def("download_update", [](PyMoneroDaemon& self) {
      MONERO_CATCH_AND_RETHROW(self.download_update());
    })
    .def("download_update", [](PyMoneroDaemon& self, std::string& download_path) {
      MONERO_CATCH_AND_RETHROW(self.download_update(download_path));
    }, py::arg("download_path"))
    .def("stop", [](PyMoneroDaemon& self) {
      MONERO_CATCH_AND_RETHROW(self.stop());
    })
    .def("wait_for_next_block_header", [](PyMoneroDaemon& self) {
      MONERO_CATCH_AND_RETHROW(self.wait_for_next_block_header());
    });

  // monero_daemon_default
  py_monero_daemon_default
    .def(py::init<>());
  // monero_daemon_rpc
  py_monero_daemon_rpc
    .def(py::init<>())
    .def(py::init<std::shared_ptr<PyMoneroRpcConnection>>(), py::arg("rpc"))
    .def(py::init<std::string&, std::string&, std::string&>(), py::arg("uri"), py::arg("username") = "", py::arg("password") = "")
    .def("get_rpc_connection", [](const PyMoneroDaemonRpc& self) {
      MONERO_CATCH_AND_RETHROW(self.get_rpc_connection());
    })
    .def("is_connected", [](PyMoneroDaemonRpc& self) {
      MONERO_CATCH_AND_RETHROW(self.is_connected());
    });

  // monero_wallet
  py_monero_wallet
    .def(py::init<>())
    .def("is_closed", [](const monero::monero_wallet& self) {
      return is_wallet_closed(&self);
    })
    .def("is_view_only", [](PyMoneroWallet& self) {
      MONERO_CATCH_AND_RETHROW(self.is_view_only());
    })
    .def("set_connection_manager", [](PyMoneroWallet& self, const std::optional<std::shared_ptr<PyMoneroConnectionManager>> &connection_manager) {
      if (connection_manager.has_value()) {
        MONERO_CATCH_AND_RETHROW(self.set_connection_manager(connection_manager.value()));
      }
      else {
        MONERO_CATCH_AND_RETHROW(self.set_connection_manager(nullptr));
      }
    }, py::arg("connection_manager"))
    .def("get_connection_manager", [](PyMoneroWallet& self) {
      MONERO_CATCH_AND_RETHROW(self.get_connection_manager());
    })
    .def("set_daemon_connection", [](PyMoneroWallet& self, const monero::monero_rpc_connection& connection) {
      MONERO_CATCH_AND_RETHROW(self.set_daemon_connection(connection));
    }, py::arg("connection"))
     .def("set_daemon_connection", [](PyMoneroWallet& self, std::string uri, std::string username, std::string password) {
      MONERO_CATCH_AND_RETHROW(self.set_daemon_connection(uri, username, password));
    }, py::arg("uri") = "", py::arg("username") = "", py::arg("password") = "")       
    .def("set_daemon_proxy", [](PyMoneroWallet& self, const std::string& uri) {
      MONERO_CATCH_AND_RETHROW(self.set_daemon_proxy(uri));
    }, py::arg("uri") = "")
    .def("get_daemon_connection", [](PyMoneroWallet& self) {
      MONERO_CATCH_AND_RETHROW(self.get_daemon_connection());
    })
    .def("is_connected_to_daemon", [](PyMoneroWallet& self) {
      MONERO_CATCH_AND_RETHROW(self.is_connected_to_daemon());
    })
    .def("is_daemon_trusted", [](PyMoneroWallet& self) {
      MONERO_CATCH_AND_RETHROW(self.is_daemon_trusted());
    })
    .def("is_synced", [](PyMoneroWallet& self) {
      MONERO_CATCH_AND_RETHROW(self.is_synced());
    })
    .def("get_version", [](PyMoneroWallet& self) {
      MONERO_CATCH_AND_RETHROW(self.get_version());
    })
    .def("get_path", [](PyMoneroWallet& self) {
      MONERO_CATCH_AND_RETHROW(self.get_path());
    })
    .def("get_network_type", [](PyMoneroWallet& self) {
      MONERO_CATCH_AND_RETHROW(self.get_network_type());
    })
    .def("get_seed", [](PyMoneroWallet& self) {
      MONERO_CATCH_AND_RETHROW(self.get_seed());
    })
    .def("get_seed_language", [](PyMoneroWallet& self) {
      MONERO_CATCH_AND_RETHROW(self.get_seed_language());
    })
    .def("get_public_view_key", [](PyMoneroWallet& self) {
      MONERO_CATCH_AND_RETHROW(self.get_public_view_key());
    })
    .def("get_private_view_key", [](PyMoneroWallet& self) {
      MONERO_CATCH_AND_RETHROW(self.get_private_view_key());
    })
    .def("get_public_spend_key", [](PyMoneroWallet& self) {
      MONERO_CATCH_AND_RETHROW(self.get_public_spend_key());
    })
    .def("get_private_spend_key", [](PyMoneroWallet& self) {
      MONERO_CATCH_AND_RETHROW(self.get_private_spend_key());
    })
    .def("get_primary_address", [](PyMoneroWallet& self) {
      MONERO_CATCH_AND_RETHROW(self.get_primary_address());
    })
    .def("get_address", [](PyMoneroWallet& self, uint32_t account_idx, uint32_t subaddress_idx) {
      MONERO_CATCH_AND_RETHROW(self.get_address(account_idx, subaddress_idx));
    }, py::arg("account_idx"), py::arg("subaddress_idx"))
    .def("get_address_index", [](PyMoneroWallet& self, const std::string& address) {
      MONERO_CATCH_AND_RETHROW(self.get_address_index(address));
    }, py::arg("address"))
    .def("get_integrated_address", [](PyMoneroWallet& self, const std::string& standard_address, const std::string& payment_id) {
      MONERO_CATCH_AND_RETHROW(self.get_integrated_address(standard_address, payment_id));
    }, py::arg("standard_address") = "", py::arg("payment_id") = "")
    .def("decode_integrated_address", [](PyMoneroWallet& self, const std::string& integrated_address) {
      MONERO_CATCH_AND_RETHROW(self.decode_integrated_address(integrated_address));
    }, py::arg("integrated_address"))
    .def("get_height", [](PyMoneroWallet& self) {
      MONERO_CATCH_AND_RETHROW(self.get_height());
    })
    .def("get_restore_height", [](PyMoneroWallet& self) {
      MONERO_CATCH_AND_RETHROW(self.get_restore_height());
    })
    .def("set_restore_height", [](PyMoneroWallet& self, uint64_t restore_height) {
      MONERO_CATCH_AND_RETHROW(self.set_restore_height(restore_height));
    }, py::arg("restore_height"))
    .def("get_daemon_height", [](PyMoneroWallet& self) {
      MONERO_CATCH_AND_RETHROW(self.get_daemon_height());
    })
    .def("get_daemon_max_peer_height", [](PyMoneroWallet& self) {
      MONERO_CATCH_AND_RETHROW(self.get_daemon_max_peer_height());
    })
    .def("get_height_by_date", [](PyMoneroWallet& self, uint16_t year, uint8_t month, uint8_t day) {
      MONERO_CATCH_AND_RETHROW(self.get_height_by_date(year, month, day));
    }, py::arg("year"), py::arg("month"), py::arg("day"))
    .def("add_listener", [](PyMoneroWallet& self, monero::monero_wallet_listener& listener) {
      MONERO_CATCH_AND_RETHROW(self.add_listener(listener));
    }, py::arg("listener"))
    .def("remove_listener", [](PyMoneroWallet& self, monero::monero_wallet_listener& listener) {
      MONERO_CATCH_AND_RETHROW(self.remove_listener(listener));
    }, py::arg("listener"))
    .def("get_listeners", [](PyMoneroWallet& self) {
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
    .def("sync", [](PyMoneroWallet& self) {
      MONERO_CATCH_AND_RETHROW(self.sync());
    })
    .def("sync", [](PyMoneroWallet& self, monero::monero_wallet_listener& listener) {
      MONERO_CATCH_AND_RETHROW(self.sync(listener));
    }, py::arg("listener"))
    .def("sync", [](PyMoneroWallet& self, uint64_t start_height) {
      MONERO_CATCH_AND_RETHROW(self.sync(start_height));
    }, py::arg("start_height"))
    .def("sync", [](PyMoneroWallet& self, uint64_t start_height, monero::monero_wallet_listener& listener) {
      MONERO_CATCH_AND_RETHROW(self.sync(start_height, listener));
    }, py::arg("start_height"), py::arg("listener"))
    .def("start_syncing", [](PyMoneroWallet& self, uint64_t sync_period_in_ms) {
      MONERO_CATCH_AND_RETHROW(self.start_syncing(sync_period_in_ms));
    }, py::arg("sync_period_in_ms") = 10000)
    .def("stop_syncing", [](PyMoneroWallet& self) {
      MONERO_CATCH_AND_RETHROW(self.stop_syncing());
    })
    .def("scan_txs", [](PyMoneroWallet& self, const std::vector<std::string>& tx_hashes) {
      MONERO_CATCH_AND_RETHROW(self.scan_txs(tx_hashes));
    }, py::arg("tx_hashes"))
    .def("rescan_spent", [](PyMoneroWallet& self) {
      MONERO_CATCH_AND_RETHROW(self.rescan_spent());
    })
    .def("rescan_blockchain", [](PyMoneroWallet& self) {
      MONERO_CATCH_AND_RETHROW(self.rescan_blockchain());
    })
    .def("get_balance", [](PyMoneroWallet& self) {
      MONERO_CATCH_AND_RETHROW(self.get_balance());
    })
    .def("get_balance", [](PyMoneroWallet& self, uint32_t account_idx) {
      MONERO_CATCH_AND_RETHROW(self.get_balance(account_idx));
    }, py::arg("account_idx"))
    .def("get_balance", [](PyMoneroWallet& self, uint32_t account_idx, uint32_t subaddress_idx) {
      MONERO_CATCH_AND_RETHROW(self.get_balance(account_idx, subaddress_idx));
    }, py::arg("account_idx"), py::arg("subaddress_idx"))
    .def("get_unlocked_balance", [](PyMoneroWallet& self) {
      MONERO_CATCH_AND_RETHROW(self.get_unlocked_balance());
    })
    .def("get_unlocked_balance", [](PyMoneroWallet& self, uint32_t account_idx) {
      MONERO_CATCH_AND_RETHROW(self.get_unlocked_balance(account_idx));
    }, py::arg("account_idx"))
    .def("get_unlocked_balance", [](PyMoneroWallet& self, uint32_t account_idx, uint32_t subaddress_idx) {
      MONERO_CATCH_AND_RETHROW(self.get_unlocked_balance(account_idx, subaddress_idx));
    }, py::arg("account_idx"), py::arg("subaddress_idx"))
    .def("get_accounts", [](PyMoneroWallet& self) {
      MONERO_CATCH_AND_RETHROW(self.get_accounts());
    })
    .def("get_accounts", [](PyMoneroWallet& self, bool include_subaddresses) {
      MONERO_CATCH_AND_RETHROW(self.get_accounts(include_subaddresses));
    }, py::arg("include_subaddresses"))
    .def("get_accounts", [](PyMoneroWallet& self, const std::string& tag) {
      MONERO_CATCH_AND_RETHROW(self.get_accounts(tag));
    }, py::arg("tag"))
    .def("get_accounts", [](PyMoneroWallet& self, bool include_subaddresses, const std::string& tag) {
      MONERO_CATCH_AND_RETHROW(self.get_accounts(include_subaddresses, tag));
    }, py::arg("include_subaddresses"), py::arg("tag"))
    .def("get_account", [](PyMoneroWallet& self, uint32_t account_idx) {
      MONERO_CATCH_AND_RETHROW(self.get_account(account_idx));
    }, py::arg("account_idx"))
    .def("get_account", [](PyMoneroWallet& self, uint32_t account_idx, bool include_subaddresses) {
      MONERO_CATCH_AND_RETHROW(self.get_account(account_idx, include_subaddresses));
    }, py::arg("account_idx"), py::arg("include_subaddresses"))
    .def("create_account", [](PyMoneroWallet& self, const std::string& label) {
      MONERO_CATCH_AND_RETHROW(self.create_account(label));
    }, py::arg("label") = "")
    .def("get_subaddress", [](PyMoneroWallet& self, uint32_t account_idx, uint32_t subaddress_idx) {
      MONERO_CATCH_AND_RETHROW(self.get_subaddress(account_idx, subaddress_idx));
    }, py::arg("account_idx"), py::arg("subaddress_idx"))
    .def("get_subaddresses", [](PyMoneroWallet& self, uint32_t account_idx) {
      MONERO_CATCH_AND_RETHROW(self.get_subaddresses(account_idx));
    }, py::arg("account_idx"))
    .def("get_subaddresses", [](PyMoneroWallet& self, uint32_t account_idx, const std::vector<uint32_t>& subaddress_indices) {
      MONERO_CATCH_AND_RETHROW(self.get_subaddresses(account_idx, subaddress_indices));
    }, py::arg("account_idx"), py::arg("subaddress_indices"))
    .def("create_subaddress", [](PyMoneroWallet& self, uint32_t account_idx, const std::string& label) {
      MONERO_CATCH_AND_RETHROW(self.create_subaddress(account_idx, label));
    }, py::arg("account_idx"), py::arg("label") = "")
    .def("set_subaddress_label", [](PyMoneroWallet& self, uint32_t account_idx, uint32_t subaddress_idx, const std::string& label) {
      MONERO_CATCH_AND_RETHROW(self.set_subaddress_label(account_idx, subaddress_idx, label));
    }, py::arg("account_idx"), py::arg("subaddress_idx"), py::arg("label") = "")
    .def("get_txs", [](PyMoneroWallet& self) {
      MONERO_CATCH_AND_RETHROW(self.get_txs());
    })
    .def("get_txs", [](PyMoneroWallet& self, const monero::monero_tx_query& query) {
      MONERO_CATCH_AND_RETHROW(self.get_txs(query));
    }, py::arg("query"))
    .def("get_transfers", [](PyMoneroWallet& self, const monero::monero_transfer_query& query) {
      MONERO_CATCH_AND_RETHROW(self.get_transfers(query));
    }, py::arg("query"))
    .def("get_outputs", [](PyMoneroWallet& self, const monero::monero_output_query& query) {
      MONERO_CATCH_AND_RETHROW(self.get_outputs(query));
    }, py::arg("query"))
    .def("export_outputs", [](PyMoneroWallet& self, bool all) {
      MONERO_CATCH_AND_RETHROW(self.export_outputs(all));
    }, py::arg("all") = false)
    .def("import_outputs", [](PyMoneroWallet& self, const std::string& outputs_hex) {
      MONERO_CATCH_AND_RETHROW(self.import_outputs(outputs_hex));
    }, py::arg("outputs_hex"))
    .def("export_key_images", [](PyMoneroWallet& self, bool all) {
      MONERO_CATCH_AND_RETHROW(self.export_key_images(all));
    }, py::arg("all") = false)
    .def("import_key_images", [](PyMoneroWallet& self, const std::vector<std::shared_ptr<monero_key_image>>& key_images) {
      MONERO_CATCH_AND_RETHROW(self.import_key_images(key_images));
    }, py::arg("key_images"))
    .def("freeze_output", [](PyMoneroWallet& self, const std::string& key_image) {
      MONERO_CATCH_AND_RETHROW(self.freeze_output(key_image));
    }, py::arg("key_image"))
    .def("thaw_output", [](PyMoneroWallet& self, const std::string& key_image) {
      MONERO_CATCH_AND_RETHROW(self.thaw_output(key_image));
    }, py::arg("key_image"))
    .def("is_output_frozen", [](PyMoneroWallet& self, const std::string& key_image) {
      MONERO_CATCH_AND_RETHROW(self.is_output_frozen(key_image));
    }, py::arg("key_image"))
    .def("get_default_fee_priority", [](PyMoneroWallet& self) {
      MONERO_CATCH_AND_RETHROW(self.get_default_fee_priority());
    })
    .def("create_tx", [](PyMoneroWallet& self, const monero::monero_tx_config& config) {
      MONERO_CATCH_AND_RETHROW(self.create_tx(config));
    }, py::arg("config"))
    .def("create_txs", [](PyMoneroWallet& self, const monero::monero_tx_config& config) {
      MONERO_CATCH_AND_RETHROW(self.create_txs(config));
    }, py::arg("config"))
    .def("sweep_unlocked", [](PyMoneroWallet& self, const monero::monero_tx_config& config) {
      MONERO_CATCH_AND_RETHROW(self.sweep_unlocked(config));
    }, py::arg("config"))
    .def("sweep_output", [](PyMoneroWallet& self, const monero::monero_tx_config& config) {
      MONERO_CATCH_AND_RETHROW(self.sweep_output(config));
    }, py::arg("config"))
    .def("sweep_dust", [](PyMoneroWallet& self, bool relay) {
      MONERO_CATCH_AND_RETHROW(self.sweep_dust(relay));
    }, py::arg("relay") = false)
    .def("relay_tx", [](PyMoneroWallet& self, const std::string& tx_metadata) {
      MONERO_CATCH_AND_RETHROW(self.relay_tx(tx_metadata));
    }, py::arg("tx_metadata"))
    .def("relay_tx", [](PyMoneroWallet& self, const monero::monero_tx_wallet& tx) {
      MONERO_CATCH_AND_RETHROW(self.relay_tx(tx));
    }, py::arg("tx"))
    .def("relay_txs", [](PyMoneroWallet& self, const std::vector<std::shared_ptr<monero_tx_wallet>>& txs) {
      MONERO_CATCH_AND_RETHROW(self.relay_txs(txs));
    }, py::arg("txs"))
    .def("relay_txs", [](PyMoneroWallet& self, const std::vector<std::string>& tx_metadatas) {
      MONERO_CATCH_AND_RETHROW(self.relay_txs(tx_metadatas));
    }, py::arg("tx_metadatas"))
    .def("describe_tx_set", [](PyMoneroWallet& self, const monero::monero_tx_set& tx_set) {
      MONERO_CATCH_AND_RETHROW(self.describe_tx_set(tx_set));
    }, py::arg("tx_set"))
    .def("sign_txs", [](PyMoneroWallet& self, const std::string& unsigned_tx_hex) {
      MONERO_CATCH_AND_RETHROW(self.sign_txs(unsigned_tx_hex));
    }, py::arg("unsigned_tx_hex"))
    .def("submit_txs", [](PyMoneroWallet& self, const std::string& signed_tx_hex) {
      MONERO_CATCH_AND_RETHROW(self.submit_txs(signed_tx_hex));
    }, py::arg("signed_tx_hex"))
    .def("sign_message", [](PyMoneroWallet& self, const std::string& msg, monero_message_signature_type signature_type, uint32_t account_idx, uint32_t subaddress_idx) {
      MONERO_CATCH_AND_RETHROW(self.sign_message(msg, signature_type, account_idx, subaddress_idx));
    }, py::arg("msg"), py::arg("signature_type"), py::arg("account_idx") = 0, py::arg("subaddress_idx") = 0)
    .def("verify_message", [](PyMoneroWallet& self, const std::string& msg, const std::string& address, const std::string& signature) {
      MONERO_CATCH_AND_RETHROW(self.verify_message(msg, address, signature));
    }, py::arg("msg"), py::arg("address"), py::arg("signature"))
    .def("get_tx_key", [](PyMoneroWallet& self, const std::string& tx_hash) {
      MONERO_CATCH_AND_RETHROW(self.get_tx_key(tx_hash));
    }, py::arg("tx_hash"))
    .def("check_tx_key", [](PyMoneroWallet& self, const std::string& tx_hash, const std::string& tx_key, const std::string& address) {
      MONERO_CATCH_AND_RETHROW(self.check_tx_key(tx_hash, tx_key, address));
    }, py::arg("tx_hash"), py::arg("tx_key"), py::arg("address"))
    .def("get_tx_proof", [](PyMoneroWallet& self, const std::string& tx_hash, const std::string& address, const std::string& message) {
      MONERO_CATCH_AND_RETHROW(self.get_tx_proof(tx_hash, address, message));
    }, py::arg("tx_hash"), py::arg("address"), py::arg("message"))
    .def("check_tx_proof", [](PyMoneroWallet& self, const std::string& tx_hash, const std::string& address, const std::string& message, const std::string& signature) {
      MONERO_CATCH_AND_RETHROW(self.check_tx_proof(tx_hash, address, message, signature));
    }, py::arg("tx_hash"), py::arg("address"), py::arg("message"), py::arg("signature"))
    .def("get_spend_proof", [](PyMoneroWallet& self, const std::string& tx_hash, const std::string& message) {
      MONERO_CATCH_AND_RETHROW(self.get_spend_proof(tx_hash, message));
    }, py::arg("tx_hash"), py::arg("message"))
    .def("check_spend_proof", [](PyMoneroWallet& self, const std::string& tx_hash, const std::string& message, const std::string& signature) {
      MONERO_CATCH_AND_RETHROW(self.check_spend_proof(tx_hash, message, signature));
    }, py::arg("tx_hash"), py::arg("message"), py::arg("signature"))
    .def("get_reserve_proof_wallet", [](PyMoneroWallet& self, const std::string& message) {
      MONERO_CATCH_AND_RETHROW(self.get_reserve_proof_wallet(message));
    }, py::arg("message"))
    .def("get_reserve_proof_account", [](PyMoneroWallet& self, uint32_t account_idx, uint64_t amount, const std::string& message) {
      MONERO_CATCH_AND_RETHROW(self.get_reserve_proof_account(account_idx, amount, message));
    }, py::arg("account_idx"), py::arg("amount"), py::arg("message"))
    .def("check_reserve_proof", [](PyMoneroWallet& self, const std::string& address, const std::string& message, const std::string& signature) {
      MONERO_CATCH_AND_RETHROW(self.check_reserve_proof(address, message, signature));
    }, py::arg("address"), py::arg("message"), py::arg("signature"))
    .def("get_tx_note", [](PyMoneroWallet& self, const std::string& tx_hash) {
      MONERO_CATCH_AND_RETHROW(self.get_tx_note(tx_hash));
    }, py::arg("tx_hash"))
    .def("get_tx_notes", [](PyMoneroWallet& self, const std::vector<std::string>& tx_hashes) {
      MONERO_CATCH_AND_RETHROW(self.get_tx_notes(tx_hashes));
    }, py::arg("tx_hashes"))
    .def("set_tx_note", [](PyMoneroWallet& self, const std::string& tx_hash, const std::string& note) {
      MONERO_CATCH_AND_RETHROW(self.set_tx_note(tx_hash, note));
    }, py::arg("tx_hash"), py::arg("note"))
    .def("set_tx_notes", [](PyMoneroWallet& self, const std::vector<std::string>& tx_hashes, const std::vector<std::string>& notes) {
      MONERO_CATCH_AND_RETHROW(self.set_tx_notes(tx_hashes, notes));
    }, py::arg("tx_hashes"), py::arg("notes"))
    .def("get_address_book_entries", [](PyMoneroWallet& self, const std::vector<uint64_t>& indices) {
      MONERO_CATCH_AND_RETHROW(self.get_address_book_entries(indices));
    }, py::arg("indices"))
    .def("add_address_book_entry", [](PyMoneroWallet& self, const std::string& address, const std::string& description) {
      MONERO_CATCH_AND_RETHROW(self.add_address_book_entry(address, description));
    }, py::arg("address"), py::arg("description"))
    .def("edit_address_book_entry", [](PyMoneroWallet& self, uint64_t index, bool set_address, const std::string& address, bool set_description, const std::string& description) {
      MONERO_CATCH_AND_RETHROW(self.edit_address_book_entry(index, set_address, address, set_description, description));
    }, py::arg("index"), py::arg("set_address"), py::arg("address"), py::arg("set_description"), py::arg("description"))
    .def("delete_address_book_entry", [](PyMoneroWallet& self, uint64_t index) {
      MONERO_CATCH_AND_RETHROW(self.delete_address_book_entry(index));
    }, py::arg("index"))
    .def("tag_accounts", [](PyMoneroWallet& self, const std::string& tag, const std::vector<uint32_t>& account_indices) {
      MONERO_CATCH_AND_RETHROW(self.tag_accounts(tag, account_indices));
    }, py::arg("tag"), py::arg("account_indices"))
    .def("untag_accounts", [](PyMoneroWallet& self, const std::vector<uint32_t>& account_indices) {
      MONERO_CATCH_AND_RETHROW(self.untag_accounts(account_indices));
    }, py::arg("account_indices"))
    .def("get_account_tags", [](PyMoneroWallet& self) {
      MONERO_CATCH_AND_RETHROW(self.get_account_tags());
    })
    .def("set_account_tag_label", [](PyMoneroWallet& self, const std::string& tag, const std::string& label) {
      MONERO_CATCH_AND_RETHROW(self.set_account_tag_label(tag, label));
    }, py::arg("tag"), py::arg("label"))
    .def("get_payment_uri", [](PyMoneroWallet& self, const monero::monero_tx_config& config) {
      MONERO_CATCH_AND_RETHROW(self.get_payment_uri(config));
    }, py::arg("config"))
    .def("parse_payment_uri", [](PyMoneroWallet& self, const std::string& uri) {
      MONERO_CATCH_AND_RETHROW(self.parse_payment_uri(uri));
    }, py::arg("uri"))        
    .def("get_attribute", [](PyMoneroWallet& self, const std::string& key, std::string& val) {
      MONERO_CATCH_AND_RETHROW(self.get_attribute(key, val));
    }, py::arg("key"), py::arg("val"))
    .def("set_attribute", [](PyMoneroWallet& self, const std::string& key, const std::string& val) {
      MONERO_CATCH_AND_RETHROW(self.set_attribute(key, val));
    }, py::arg("key"), py::arg("val"))
    .def("start_mining", [](PyMoneroWallet& self, boost::optional<uint64_t> num_threads, boost::optional<bool> background_mining, boost::optional<bool> ignore_battery) {
      MONERO_CATCH_AND_RETHROW(self.start_mining(num_threads, background_mining, ignore_battery));
    }, py::arg("num_threads") = py::none(), py::arg("background_mining") = py::none(), py::arg("ignore_battery") = py::none())
    .def("stop_mining", [](PyMoneroWallet& self) {
      MONERO_CATCH_AND_RETHROW(self.stop_mining());
    }) 
    .def("wait_for_next_block", [](PyMoneroWallet& self) {
      MONERO_CATCH_AND_RETHROW(self.wait_for_next_block());
    }) 
    .def("is_multisig_import_needed", [](PyMoneroWallet& self) {
      MONERO_CATCH_AND_RETHROW(self.is_multisig_import_needed());
    })  
    .def("is_multisig", [](PyMoneroWallet& self) {
      MONERO_CATCH_AND_RETHROW(self.is_multisig());
    })  
    .def("get_multisig_info", [](PyMoneroWallet& self) {
      MONERO_CATCH_AND_RETHROW(self.get_multisig_info());
    })   
    .def("prepare_multisig", [](PyMoneroWallet& self) {
      MONERO_CATCH_AND_RETHROW(self.prepare_multisig());
    })        
    .def("make_multisig", [](PyMoneroWallet& self, const std::vector<std::string>& mutisig_hexes, int threshold, const std::string& password) {
      MONERO_CATCH_AND_RETHROW(self.make_multisig(mutisig_hexes, threshold, password));
    }, py::arg("mutisig_hexes"), py::arg("threshold"), py::arg("password"))
    .def("exchange_multisig_keys", [](PyMoneroWallet& self, const std::vector<std::string>& mutisig_hexes, const std::string& password) {
      MONERO_CATCH_AND_RETHROW(self.exchange_multisig_keys(mutisig_hexes, password));
    }, py::arg("mutisig_hexes"), py::arg("password"))
    .def("export_multisig_hex", [](PyMoneroWallet& self) {
      MONERO_CATCH_AND_RETHROW(self.export_multisig_hex());
    })
    .def("import_multisig_hex", [](PyMoneroWallet& self, const std::vector<std::string>& multisig_hexes) {
      MONERO_CATCH_AND_RETHROW(self.import_multisig_hex(multisig_hexes));
    }, py::arg("multisig_hexes"))
    .def("sign_multisig_tx_hex", [](PyMoneroWallet& self, const std::string& multisig_tx_hex) {
      MONERO_CATCH_AND_RETHROW(self.sign_multisig_tx_hex(multisig_tx_hex));
    }, py::arg("multisig_tx_hex"))
    .def("submit_multisig_tx_hex", [](PyMoneroWallet& self, const std::string& signed_multisig_tx_hex) {
      MONERO_CATCH_AND_RETHROW(self.submit_multisig_tx_hex(signed_multisig_tx_hex));
    }, py::arg("signed_multisig_tx_hex"))
    .def("change_password", [](PyMoneroWallet& self, const std::string& old_password, const std::string& new_password) {
      MONERO_CATCH_AND_RETHROW(self.change_password(old_password, new_password));
    }, py::arg("old_password"), py::arg("new_password"))
    .def("move_to", [](PyMoneroWallet& self, const std::string& path, const std::string& password) {
      MONERO_CATCH_AND_RETHROW(self.move_to(path, password));
    }, py::arg("path"), py::arg("password"))
    .def("save", [](PyMoneroWallet& self) {
      MONERO_CATCH_AND_RETHROW(self.save());
    })
    .def("close", [](monero::monero_wallet& self, bool save) {
      self.close(save);
      set_wallet_closed(&self, true);
    }, py::arg("save") = false);

  // monero_wallet_keys
  py_monero_wallet_keys
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
    });

  // monero_wallet_full
  py_monero_wallet_full
    .def_static("wallet_exists", [](const std::string& path) {
      MONERO_CATCH_AND_RETHROW(monero::monero_wallet_full::wallet_exists(path));
    }, py::arg("path"))
    .def_static("open_wallet", [](const std::string& path, const std::string& password, monero::monero_network_type nettype) {
      MONERO_CATCH_AND_RETHROW(monero::monero_wallet_full::open_wallet(path, password, nettype));
    }, py::arg("path"), py::arg("password"), py::arg("nettype"))
    .def_static("open_wallet_data", [](const std::string& password, monero::monero_network_type nettype, const std::string& keys_data, const std::string& cache_data) {
      MONERO_CATCH_AND_RETHROW(monero::monero_wallet_full::open_wallet_data(password, nettype, keys_data, cache_data, monero::monero_rpc_connection()));
    }, py::arg("password"), py::arg("nettype"), py::arg("keys_data"), py::arg("cache_data"))
    .def_static("open_wallet_data", [](const std::string& password, monero::monero_network_type nettype, const std::string& keys_data, const std::string& cache_data, const monero_rpc_connection& daemon_connection) {
      MONERO_CATCH_AND_RETHROW(monero::monero_wallet_full::open_wallet_data(password, nettype, keys_data, cache_data, daemon_connection));
    }, py::arg("password"), py::arg("nettype"), py::arg("keys_data"), py::arg("cache_data"), py::arg("daemon_connection"))
    .def_static("create_wallet", [](const monero::monero_wallet_config& config) {
      MONERO_CATCH_AND_RETHROW(monero::monero_wallet_full::create_wallet(config));
    }, py::arg("config"))
    .def_static("get_seed_languages", []() {
      MONERO_CATCH_AND_RETHROW(monero::monero_wallet_full::get_seed_languages());
    })
    .def("get_keys_file_buffer", [](monero::monero_wallet_full& self, std::string& password, bool view_only) {
      MONERO_CATCH_AND_RETHROW(self.get_keys_file_buffer(password, view_only));
    }, py::arg("password"), py::arg("view_only"))
    .def("get_cache_file_buffer", [](monero::monero_wallet_full& self) {
      MONERO_CATCH_AND_RETHROW(self.get_cache_file_buffer());
    });

  // monero_wallet_rpc
  py_monero_wallet_rpc
    .def(py::init<std::shared_ptr<PyMoneroRpcConnection>>(), py::arg("rpc_connection"))
    .def(py::init<const std::string&, const std::string&, const std::string&>(), py::arg("uri") = "", py::arg("username") = "", py::arg("password") = "")
    .def("create_wallet", [](PyMoneroWalletRpc& self, const std::shared_ptr<PyMoneroWalletConfig> config) {
      MONERO_CATCH_AND_RETHROW(self.create_wallet(config));
    }, py::arg("config"))
    .def("open_wallet", [](PyMoneroWalletRpc& self, const std::shared_ptr<PyMoneroWalletConfig> config) {
      MONERO_CATCH_AND_RETHROW(self.open_wallet(config));
    }, py::arg("config"))
    .def("open_wallet", [](PyMoneroWalletRpc& self, const std::string& name, const std::string& password) {
      MONERO_CATCH_AND_RETHROW(self.open_wallet(name, password));
    }, py::arg("name"), py::arg("password"))
    .def("get_rpc_connection", [](PyMoneroWalletRpc& self) {
      MONERO_CATCH_AND_RETHROW(self.get_rpc_connection());
    })
    .def("get_accounts", [](PyMoneroWalletRpc& self, bool include_subaddresses, const std::string& tag, bool skip_balances) {
      MONERO_CATCH_AND_RETHROW(self.get_accounts(include_subaddresses, tag, skip_balances));
    }, py::arg("include_subaddresses"), py::arg("tag"), py::arg("skip_balances"))
    .def("stop", [](PyMoneroWalletRpc& self) {
      MONERO_CATCH_AND_RETHROW(self.stop());
    });

  // monero_utils
  py_monero_utils
    .def_static("get_version", []() {
      MONERO_CATCH_AND_RETHROW(PyMoneroUtils::get_version());
    })
    .def_static("get_ring_size", []() {
      MONERO_CATCH_AND_RETHROW(PyMoneroUtils::get_ring_size());
    })
    .def_static("set_log_level", [](int loglevel) {
      MONERO_CATCH_AND_RETHROW(PyMoneroUtils::set_log_level(loglevel));
    }, py::arg("loglevel"))
    .def_static("configure_logging", [](const std::string& path, bool console) {
      MONERO_CATCH_AND_RETHROW(PyMoneroUtils::configure_logging(path, console));
    }, py::arg("path"), py::arg("console"))
    .def_static("get_integrated_address", [](monero_network_type network_type, const std::string& standard_address, const std::string& payment_id) {
      MONERO_CATCH_AND_RETHROW(PyMoneroUtils::get_integrated_address(network_type, standard_address, payment_id));
    }, py::arg("network_type"), py::arg("standard_address"), py::arg("payment_id") = "")
    .def_static("is_valid_address", [](const std::string& address, monero_network_type network_type) {
      MONERO_CATCH_AND_RETHROW(PyMoneroUtils::is_valid_address(address, network_type));
    }, py::arg("address"), py::arg("network_type"))
    .def_static("is_valid_public_view_key", [](const std::string& public_view_key) {
      MONERO_CATCH_AND_RETHROW(PyMoneroUtils::is_valid_public_view_key(public_view_key));
    }, py::arg("public_view_key"))
    .def_static("is_valid_public_spend_key", [](const std::string& public_spend_key) {
      MONERO_CATCH_AND_RETHROW(PyMoneroUtils::is_valid_public_spend_key(public_spend_key));
    }, py::arg("public_spend_key"))
    .def_static("is_valid_private_view_key", [](const std::string& private_view_key) {
      MONERO_CATCH_AND_RETHROW(PyMoneroUtils::is_valid_private_view_key(private_view_key));
    }, py::arg("private_view_key"))
    .def_static("is_valid_private_spend_key", [](const std::string& private_spend_key) {
      MONERO_CATCH_AND_RETHROW(PyMoneroUtils::is_valid_private_spend_key(private_spend_key));
    }, py::arg("private_spend_key"))
    .def_static("is_valid_payment_id", [](const std::string& payment_id) {
      MONERO_CATCH_AND_RETHROW(PyMoneroUtils::is_valid_payment_id(payment_id));
    }, py::arg("payment_id"))
    .def_static("is_valid_mnemonic", [](const std::string& mnemonic) {
      MONERO_CATCH_AND_RETHROW(PyMoneroUtils::is_valid_mnemonic(mnemonic));
    }, py::arg("mnemonic"))
    .def_static("validate_address", [](const std::string& address, monero_network_type network_type) {
      MONERO_CATCH_AND_RETHROW(PyMoneroUtils::validate_address(address, network_type));
    }, py::arg("address"), py::arg("network_type"))
    .def_static("validate_public_view_key", [](const std::string& public_view_key) {
      MONERO_CATCH_AND_RETHROW(PyMoneroUtils::validate_public_view_key(public_view_key));
    }, py::arg("public_view_key"))
    .def_static("validate_public_spend_key", [](const std::string& public_spend_key) {
      MONERO_CATCH_AND_RETHROW(PyMoneroUtils::validate_public_spend_key(public_spend_key));
    }, py::arg("public_spend_key"))
    .def_static("validate_private_view_key", [](const std::string& private_view_key) {
      MONERO_CATCH_AND_RETHROW(PyMoneroUtils::validate_private_view_key(private_view_key));
    }, py::arg("private_view_key"))
    .def_static("validate_private_spend_key", [](const std::string& private_spend_key) {
      MONERO_CATCH_AND_RETHROW(PyMoneroUtils::validate_private_spend_key(private_spend_key));
    }, py::arg("private_spend_key"))
    .def_static("validate_payment_id", [](const std::string& payment_id) {
      MONERO_CATCH_AND_RETHROW(PyMoneroUtils::validate_payment_id(payment_id));
    }, py::arg("payment_id"))
    .def_static("validate_mnemonic", [](const std::string& mnemonic) {
      MONERO_CATCH_AND_RETHROW(PyMoneroUtils::validate_mnemonic(mnemonic));
    }, py::arg("mnemonic"))
    .def_static("is_valid_language", [](const std::string& language) {
      MONERO_CATCH_AND_RETHROW(PyMoneroUtils::is_valid_language(language));
    }, py::arg("language"))
    .def_static("get_blocks_from_txs", [](std::vector<std::shared_ptr<monero::monero_tx_wallet>> txs) {
      MONERO_CATCH_AND_RETHROW(PyMoneroUtils::get_blocks_from_txs(txs));
    }, py::arg("txs"))
    .def_static("get_blocks_from_transfers", [](std::vector<std::shared_ptr<monero::monero_transfer>> transfers) {
      MONERO_CATCH_AND_RETHROW(PyMoneroUtils::get_blocks_from_transfers(transfers));
    }, py::arg("transfers"))
    .def_static("get_blocks_from_outputs", [](std::vector<std::shared_ptr<monero::monero_output_wallet>> outputs) {
      MONERO_CATCH_AND_RETHROW(PyMoneroUtils::get_blocks_from_outputs(outputs));
    }, py::arg("outputs"))
    .def_static("get_payment_uri", [](const monero::monero_tx_config &config) {
      MONERO_CATCH_AND_RETHROW(PyMoneroUtils::get_payment_uri(config));
    }, py::arg("config"))
    .def_static("xmr_to_atomic_units", [](double amount_xmr) {
      MONERO_CATCH_AND_RETHROW(PyMoneroUtils::xmr_to_atomic_units(amount_xmr));
    }, py::arg("amount_xmr"))
    .def_static("atomic_units_to_xmr", [](uint64_t amount_atomic_units) {
      MONERO_CATCH_AND_RETHROW(PyMoneroUtils::atomic_units_to_xmr(amount_atomic_units));
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
    }, py::arg("bin"));

}
