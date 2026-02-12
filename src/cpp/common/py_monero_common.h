#pragma once

#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <boost/optional.hpp>

#include "net/http.h"
#include "utils/gen_utils.h"
#include "daemon/monero_daemon_model.h"

namespace py = pybind11;

namespace pybind11 { namespace detail {

  template <typename T>
  struct type_caster<boost::optional<T>> {
  private:
    using ValueCaster = make_caster<T>;

  public:
    PYBIND11_TYPE_CASTER(boost::optional<T>, _("Optional[") + ValueCaster::name + _("]"));

    bool load(handle src, bool convert) {
      if (src.is_none()) {
        value = boost::none;
        return true;
      }
      ValueCaster caster;
      if (!caster.load(src, convert)) {
        return false;
      }
      value = cast_op<T&&>(std::move(caster));
      return true;
    }

    static handle cast(const boost::optional<T>& src, return_value_policy policy, handle parent) {
      if (!src) {
        return none().inc_ref();
      }
      return ValueCaster::cast(*src, policy, parent);
    }
  };

}}

class PySerializableStruct : public monero::serializable_struct {
public:
  using serializable_struct::serializable_struct;

  virtual std::string serialize() const { return serializable_struct::serialize(); }
  rapidjson::Value to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const override { throw std::runtime_error("PySerializableStruct::to_rapid_json_value(): not implemented"); };
};

class PyMoneroError : public std::exception {
public:
  std::string message;

  PyMoneroError() {}
  PyMoneroError(const std::string& msg) : message(msg) {}

  const char* what() const noexcept override {
    return message.c_str();
  }
};

class PyMoneroRpcError : public PyMoneroError {
public:
  int code;

  PyMoneroRpcError(int error_code, const std::string& msg) : code(error_code) {
    message = msg;
  }

  PyMoneroRpcError(const std::string& msg) : code(-1) {
    message = msg;
  }
};

class PyMoneroSslOptions {
public:
  boost::optional<std::string> m_ssl_private_key_path;
  boost::optional<std::string> m_ssl_certificate_path;
  boost::optional<std::string> m_ssl_ca_file;
  std::vector<std::string> m_ssl_allowed_fingerprints;
  boost::optional<bool> m_ssl_allow_any_cert;

  PyMoneroSslOptions() {}
};

enum PyMoneroConnectionType : uint8_t {
  INVALID = 0,
  IPV4,
  IPV6,
  TOR,
  I2P
};

enum PyMoneroConnectionPollType : uint8_t {
  PRIORITIZED = 0,
  CURRENT,
  ALL,
  UNDEFINED
};

class PyMoneroConnectionPriorityComparator {
public:

  static int compare(int p1, int p2);
};

class PyGenUtils {
public:
  PyGenUtils() {}

  static py::object convert_value(const std::string& val);  
  static py::object ptree_to_pyobject(const boost::property_tree::ptree& tree);
  static boost::property_tree::ptree pyobject_to_ptree(const py::object& obj);
  static boost::property_tree::ptree parse_json_string(const std::string &json);
};

class PyMoneroRequest : public PySerializableStruct {
public:
  boost::optional<std::string> m_method;

  PyMoneroRequest() { }

  rapidjson::Value to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const override { throw std::runtime_error("PyMoneroRequest::to_rapid_json_value(): not implemented"); };
};

class PyMoneroRequestParams : public PySerializableStruct {
public:
  boost::optional<py::object> m_py_params;

  PyMoneroRequestParams() { }
  PyMoneroRequestParams(boost::optional<py::object> py_params) { m_py_params = py_params; }

  std::string serialize() const override;
  rapidjson::Value to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const override { throw std::runtime_error("PyMoneroRequestParams::to_rapid_json_value(): not implemented"); };
};

class PyMoneroRequestEmptyParams : public PyMoneroRequestParams {
  public:
    PyMoneroRequestEmptyParams() {}
  
    rapidjson::Value to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const override { rapidjson::Value root(rapidjson::kObjectType); return root; };
};

class PyMoneroPathRequest : public PyMoneroRequest {
public:
  boost::optional<std::shared_ptr<PyMoneroRequestParams>> m_params;

  PyMoneroPathRequest() { }
  
  PyMoneroPathRequest(std::string method, boost::optional<py::object> params = boost::none) {
    m_method = method;
    if (params != boost::none) m_params = std::make_shared<PyMoneroRequestParams>(params);
    m_params = std::make_shared<PyMoneroRequestEmptyParams>();
  }

  PyMoneroPathRequest(std::string method, std::shared_ptr<PyMoneroRequestParams> params) {
    m_method = method;
    m_params = params;
  }

  rapidjson::Value to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const override;
};

class PyMoneroBinaryRequest : public PyMoneroPathRequest {
public:
  PyMoneroBinaryRequest() {}

  PyMoneroBinaryRequest(std::string method, boost::optional<py::object> params = boost::none) {
    m_method = method;
    if (params != boost::none) m_params = std::make_shared<PyMoneroRequestParams>(params);
    m_params = std::make_shared<PyMoneroRequestEmptyParams>();
  }

  PyMoneroBinaryRequest(std::string method, std::shared_ptr<PyMoneroRequestParams> params) {
    m_method = method;
    m_params = params;
  }

  std::string to_binary_val() const;
};

class PyMoneroJsonRequestParams : public PyMoneroRequestParams {
public:
  PyMoneroJsonRequestParams() { }
  PyMoneroJsonRequestParams(boost::optional<py::object> py_params) { m_py_params = py_params; }

  rapidjson::Value to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const override { throw std::runtime_error("PyMoneroJsonRequestParams::to_rapid_json_value(): not implemented"); };
};

class PyMoneroJsonRequestEmptyParams : public PyMoneroJsonRequestParams {
public:
  PyMoneroJsonRequestEmptyParams() {}

  rapidjson::Value to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const override { rapidjson::Value root(rapidjson::kObjectType); return root; };
};

class PyMoneroJsonRequest : public PyMoneroRequest {
public:
  boost::optional<std::string> m_version;
  boost::optional<std::string> m_id;
  boost::optional<std::shared_ptr<PyMoneroJsonRequestParams>> m_params;

  PyMoneroJsonRequest() {
    m_version = "2.0";
    m_id = "0";
    m_params = std::make_shared<PyMoneroJsonRequestEmptyParams>();
  }

  PyMoneroJsonRequest(const PyMoneroJsonRequest& request) {
    m_version = request.m_version;
    m_id = request.m_id;
    m_method = request.m_method;
    m_params = request.m_params;
  }

  PyMoneroJsonRequest(std::string method, boost::optional<py::object> params = boost::none) {
    m_version = "2.0";
    m_id = "0";
    m_method = method;
    if (params != boost::none) {
      m_params = std::make_shared<PyMoneroJsonRequestParams>(params);
    }
    else m_params = std::make_shared<PyMoneroJsonRequestEmptyParams>();
  }

  PyMoneroJsonRequest(std::string method, std::shared_ptr<PyMoneroJsonRequestParams> params) {
    m_version = "2.0";
    m_id = "0";
    m_method = method;
    m_params = params;
  }

  rapidjson::Value to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const override;
};

class PyMoneroJsonResponse {
public:
  boost::optional<std::string> m_jsonrpc;
  boost::optional<std::string> m_id;
  boost::optional<boost::property_tree::ptree> m_result;

  static std::shared_ptr<PyMoneroJsonResponse> deserialize(const std::string& response_json);

  PyMoneroJsonResponse() {
    m_jsonrpc = "2.0";
    m_id = "0";
  }

  PyMoneroJsonResponse(const PyMoneroJsonResponse& response) {
    m_jsonrpc = response.m_jsonrpc;
    m_id = response.m_id;
    m_result = response.m_result;
  }

  PyMoneroJsonResponse(boost::optional<boost::property_tree::ptree> &result) {
    m_jsonrpc = "2.0";
    m_id = "0";
    m_result = result;
  }

  boost::optional<py::object> get_result() const;
};

class PyMoneroPathResponse {
public:
  boost::optional<boost::property_tree::ptree> m_response;

  PyMoneroPathResponse() { }

  PyMoneroPathResponse(const PyMoneroPathResponse& response) {
    m_response = response.m_response;
  }

  PyMoneroPathResponse(boost::optional<boost::property_tree::ptree> &response) {
    m_response = response;
  }

  boost::optional<py::object> get_response() const;
  static std::shared_ptr<PyMoneroPathResponse> deserialize(const std::string& response_json);
};

class PyMoneroBinaryResponse {
public:
  boost::optional<std::string> m_binary;
  boost::optional<boost::property_tree::ptree> m_response;

  PyMoneroBinaryResponse() {}

  PyMoneroBinaryResponse(const std::string &binary) {
    m_binary = binary;
  }

  PyMoneroBinaryResponse(const PyMoneroBinaryResponse& response) {
    m_binary = response.m_binary;
    m_response = response.m_response;
  }

  static std::shared_ptr<PyMoneroBinaryResponse> deserialize(const std::string& response_binary);
  boost::optional<py::object> get_response() const;
};

class PyMoneroRpcConnection : public monero::monero_rpc_connection {
public:
  boost::optional<std::string> m_zmq_uri;
  int m_priority;
  uint64_t m_timeout;
  boost::optional<long> m_response_time;

  static int compare(std::shared_ptr<PyMoneroRpcConnection> c1, std::shared_ptr<PyMoneroRpcConnection> c2, std::shared_ptr<PyMoneroRpcConnection> current_connection);

  PyMoneroRpcConnection(const std::string& uri = "", const std::string& username = "", const std::string& password = "", const std::string& proxy_uri = "", const std::string& zmq_uri = "", int priority = 0, uint64_t timeout = 0) {
    m_uri = uri;
    m_username = username; 
    m_password = password;
    m_zmq_uri = zmq_uri;
    m_priority = priority;
    m_timeout = timeout;
    m_proxy_uri = proxy_uri;
    set_credentials(username, password);
  }

  PyMoneroRpcConnection(const PyMoneroRpcConnection& rpc) {
    m_uri = rpc.m_uri;
    m_username = rpc.m_username;
    m_password = rpc.m_password;
    m_zmq_uri = rpc.m_zmq_uri;
    m_proxy_uri = rpc.m_proxy_uri;
    m_is_authenticated = rpc.m_is_authenticated;
    set_credentials(m_username.value_or(""), m_password.value_or(""));
  }

  PyMoneroRpcConnection(const monero::monero_rpc_connection& rpc) {
    m_uri = rpc.m_uri;
    m_username = rpc.m_username;
    m_password = rpc.m_password;
    m_proxy_uri = rpc.m_proxy_uri;
    set_credentials(m_username.value_or(""), m_password.value_or(""));
  }

  bool is_onion() const;
  bool is_i2p() const;
  void set_credentials(const std::string& username, const std::string& password);
  void set_attribute(const std::string& key, const std::string& val);
  std::string get_attribute(const std::string& key);
  bool is_online() const;
  bool is_authenticated() const;
  bool is_connected() const;
  bool check_connection(int timeout_ms = 2000);

  template<class t_request, class t_response>
  inline int invoke_post(const boost::string_ref uri, const t_request& request, t_response& res, std::chrono::milliseconds timeout = std::chrono::seconds(15)) const {
    if (!m_http_client) throw std::runtime_error("http client not set");

    rapidjson::Document document(rapidjson::Type::kObjectType);
    rapidjson::Value req = request.to_rapidjson_val(document.GetAllocator());
    rapidjson::StringBuffer sb;
    rapidjson::Writer<rapidjson::StringBuffer> writer(sb);
    req.Accept(writer);
    std::string body = sb.GetString();

    const epee::net_utils::http::http_response_info* response = invoke_post(uri, body, timeout);

    int status_code = response->m_response_code;

    if (status_code == 200) {
      res = *t_response::deserialize(response->m_body);
    }

    return status_code;
  }

  inline const epee::net_utils::http::http_response_info* invoke_post(const boost::string_ref uri, const std::string& body, std::chrono::milliseconds timeout = std::chrono::seconds(15)) const {
    if (!m_http_client) throw std::runtime_error("http client not set");

    std::shared_ptr<epee::net_utils::http::http_response_info> _res = std::make_shared<epee::net_utils::http::http_response_info>();
    const epee::net_utils::http::http_response_info* response = _res.get();
    boost::lock_guard<boost::recursive_mutex> lock(m_mutex);

    if (!m_http_client->invoke_post(uri, body, timeout, &response)) throw std::runtime_error("Network error");

    return response;
  }

  inline const std::shared_ptr<PyMoneroJsonResponse> send_json_request(const PyMoneroJsonRequest &request, std::chrono::milliseconds timeout = std::chrono::seconds(15)) {
    PyMoneroJsonResponse response;

    int result = invoke_post("/json_rpc", request, response, timeout);

    if (result != 200) throw std::runtime_error("HTTP error: code " + std::to_string(result));

    return std::make_shared<PyMoneroJsonResponse>(response);
  }

  inline const std::shared_ptr<PyMoneroPathResponse> send_path_request(const PyMoneroPathRequest &request, std::chrono::milliseconds timeout = std::chrono::seconds(15)) {
    PyMoneroPathResponse response;

    if (request.m_method == boost::none || request.m_method->empty()) throw std::runtime_error("No RPC method set in path request");
    int result = invoke_post(std::string("/") + request.m_method.get(), request, response, timeout);

    if (result != 200) throw std::runtime_error("HTTP error: code " + std::to_string(result));

    return std::make_shared<PyMoneroPathResponse>(response);
  }

  inline const std::shared_ptr<PyMoneroBinaryResponse> send_binary_request(const PyMoneroBinaryRequest &request, std::chrono::milliseconds timeout = std::chrono::seconds(15)) {
    if (request.m_method == boost::none || request.m_method->empty()) throw std::runtime_error("No RPC method set in binary request");
    if (!m_http_client) throw std::runtime_error("http client not set");

    std::string uri = std::string("/") + request.m_method.get();
    std::string body = request.to_binary_val();

    const epee::net_utils::http::http_response_info* response = invoke_post(uri, body, timeout);
    int result = response->m_response_code;
    if (result != 200) throw std::runtime_error("HTTP error: code " + std::to_string(result));

    auto res = std::make_shared<PyMoneroBinaryResponse>();
    res->m_binary = response->m_body;

    return res;
  }

  // exposed python methods

  inline boost::optional<py::object> send_json_request(const std::string method, boost::optional<py::object> parameters) {
    PyMoneroJsonRequest request(method, parameters);
    auto response = send_json_request(request);

    return response->get_result();
  }

  inline boost::optional<py::object> send_path_request(const std::string method, boost::optional<py::object> parameters) {
    PyMoneroPathRequest request(method, parameters);
    auto response = send_path_request(request);

    return response->get_response();
  }

  inline boost::optional<py::object> send_binary_request(const std::string method, boost::optional<py::object> parameters) {
    PyMoneroBinaryRequest request(method, parameters);
    auto response = send_binary_request(request);

    return response->get_response();
  }

protected:
  mutable boost::recursive_mutex m_mutex;
  std::string m_server;
  boost::optional<epee::net_utils::http::login> m_credentials;
  std::unique_ptr<epee::net_utils::http::abstract_http_client> m_http_client;
  std::unordered_map<std::string, std::string> m_attributes;
  boost::optional<bool> m_is_online;
  boost::optional<bool> m_is_authenticated;
};

struct monero_connection_manager_listener {
public:
  virtual void on_connection_changed(std::shared_ptr<PyMoneroRpcConnection> &connection) {
    throw std::runtime_error("monero_connection_manager_listener::on_connection_changed(): not implemented");
  }
};

class PyMoneroConnectionManagerListener : public monero_connection_manager_listener {
public:
  void on_connection_changed(std::shared_ptr<PyMoneroRpcConnection> &connection) override {
    PYBIND11_OVERRIDE_PURE(void, monero_connection_manager_listener, on_connection_changed, connection);
  }
};

class PyMoneroConnectionManager {
public:

  PyMoneroConnectionManager() { }

  PyMoneroConnectionManager(const PyMoneroConnectionManager &connection_manager) {
    m_listeners = connection_manager.get_listeners();
    m_connections = connection_manager.get_connections();
    m_current_connection = connection_manager.get_connection();
    m_auto_switch = connection_manager.get_auto_switch();
    m_timeout = connection_manager.get_timeout();
  }

  void add_listener(const std::shared_ptr<monero_connection_manager_listener> &listener);
  void remove_listener(const std::shared_ptr<monero_connection_manager_listener> &listener);
  void remove_listeners();
  std::vector<std::shared_ptr<monero_connection_manager_listener>> get_listeners() const;
  std::shared_ptr<PyMoneroRpcConnection> get_connection_by_uri(const std::string &uri);
  void add_connection(std::shared_ptr<PyMoneroRpcConnection> connection);
  void add_connection(const std::string &uri);
  void remove_connection(const std::string &uri);
  void set_connection(std::shared_ptr<PyMoneroRpcConnection> connection);
  void set_connection(const std::string& uri);
  bool has_connection(const std::string& uri);
  std::shared_ptr<PyMoneroRpcConnection> get_connection() const { return m_current_connection; }
  std::vector<std::shared_ptr<PyMoneroRpcConnection>> get_connections() const { return m_connections; }
  bool get_auto_switch() const { return m_auto_switch; }
  void set_timeout(uint64_t timeout_ms) { m_timeout = timeout_ms; }
  uint64_t get_timeout() const { return m_timeout; }
  bool is_connected() const;
  void check_connection();
  void set_auto_switch(bool auto_switch);
  void stop_polling();
  void start_polling(boost::optional<uint64_t> period_ms, boost::optional<bool> auto_switch, boost::optional<uint64_t> timeout_ms, boost::optional<PyMoneroConnectionPollType> poll_type, boost::optional<std::vector<std::shared_ptr<PyMoneroRpcConnection>>> &excluded_connections);
  std::vector<std::shared_ptr<PyMoneroRpcConnection>> get_peer_connections() const { throw std::runtime_error("PyMoneroConnectionManager::get_peer_connections(): not implemented"); }
  std::shared_ptr<PyMoneroRpcConnection> get_best_available_connection(const std::set<std::shared_ptr<PyMoneroRpcConnection>>& excluded_connections = {});
  std::shared_ptr<PyMoneroRpcConnection> get_best_available_connection(std::shared_ptr<PyMoneroRpcConnection>& excluded_connection);
  void check_connections();
  void disconnect();
  void clear();
  void reset();

private:
  // static variables
  inline static const uint64_t DEFAULT_TIMEOUT = 5000;
  inline static const uint64_t DEFAULT_POLL_PERIOD = 20000;
  inline static const bool DEFAULT_AUTO_SWITCH = true;
  inline static const int MIN_BETTER_RESPONSES = 3;
  mutable boost::recursive_mutex m_listeners_mutex;
  mutable boost::recursive_mutex m_connections_mutex;
  std::vector<std::shared_ptr<monero_connection_manager_listener>> m_listeners;
  std::vector<std::shared_ptr<PyMoneroRpcConnection>> m_connections;
  std::shared_ptr<PyMoneroRpcConnection> m_current_connection;
  bool m_auto_switch = true;
  uint64_t m_timeout = 5000;
  std::map<std::shared_ptr<PyMoneroRpcConnection>, std::vector<boost::optional<long>>> m_response_times;
  bool m_is_polling = false;
  std::thread m_thread;

  void on_connection_changed(std::shared_ptr<PyMoneroRpcConnection> connection);
  std::vector<std::vector<std::shared_ptr<PyMoneroRpcConnection>>> get_connections_in_ascending_priority();
  void start_polling_connection(uint64_t period_ms);
  void start_polling_connections(uint64_t period_ms);
  void start_polling_prioritized_connections(uint64_t period_ms, boost::optional<std::vector<std::shared_ptr<PyMoneroRpcConnection>>> excluded_connections);
  bool check_connections(const std::vector<std::shared_ptr<PyMoneroRpcConnection>>& connections, const std::set<std::shared_ptr<PyMoneroRpcConnection>>& excluded_connections = {});
  void check_prioritized_connections(boost::optional<std::vector<std::shared_ptr<PyMoneroRpcConnection>>> excluded_connections);
  std::shared_ptr<PyMoneroRpcConnection> process_responses(const std::vector<std::shared_ptr<PyMoneroRpcConnection>>& responses);
  std::shared_ptr<PyMoneroRpcConnection> get_best_connection_from_prioritized_responses(const std::vector<std::shared_ptr<PyMoneroRpcConnection>>& responses);
  std::shared_ptr<PyMoneroRpcConnection> update_best_connection_in_priority();
};
