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

class PyThreadPoller {
public:

  ~PyThreadPoller();

  bool is_polling() const { return m_is_polling; }
  void set_is_polling(bool is_polling);
  void set_period_in_ms(uint64_t period_ms);
  virtual void poll() = 0;

protected:
  std::string m_name;
  boost::recursive_mutex m_mutex;
  boost::mutex m_polling_mutex;
  boost::thread m_thread;
  std::atomic<bool> m_is_polling;
  std::atomic<bool> m_poll_loop_running;
  std::atomic<uint64_t> m_poll_period_ms;
  boost::condition_variable m_poll_cv;

  void init_common(const std::string& name);
  void run_poll_loop();
};

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

class PyMoneroConnectionPriorityComparator {
public:

  static bool compare(int p1, int p2);
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
  PyMoneroRequestParams(const boost::optional<py::object>& py_params): m_py_params(py_params) {}

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
  PyMoneroPathRequest(const std::string& method, const boost::optional<py::object>& params = boost::none);
  PyMoneroPathRequest(const std::string& method, const std::shared_ptr<PyMoneroRequestParams>& params);

  rapidjson::Value to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const override;
};

class PyMoneroBinaryRequest : public PyMoneroPathRequest {
public:
  PyMoneroBinaryRequest() { }
  PyMoneroBinaryRequest(const std::string& method, const boost::optional<py::object>& params = boost::none);
  PyMoneroBinaryRequest(const std::string& method, const std::shared_ptr<PyMoneroRequestParams>& params);

  std::string to_binary_val() const;
};

class PyMoneroJsonRequestParams : public PyMoneroRequestParams {
public:
  PyMoneroJsonRequestParams() { }
  PyMoneroJsonRequestParams(const boost::optional<py::object>& py_params);

  rapidjson::Value to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const override { throw std::runtime_error("PyMoneroJsonRequestParams::to_rapid_json_value(): not implemented"); };
};

class PyMoneroJsonRequestEmptyParams : public PyMoneroJsonRequestParams {
public:
  PyMoneroJsonRequestEmptyParams() { }

  rapidjson::Value to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const override { rapidjson::Value root(rapidjson::kObjectType); return root; };
};

class PyMoneroJsonRequest : public PyMoneroRequest {
public:
  boost::optional<std::string> m_version;
  boost::optional<std::string> m_id;
  boost::optional<std::shared_ptr<PyMoneroJsonRequestParams>> m_params;

  PyMoneroJsonRequest();
  PyMoneroJsonRequest(const PyMoneroJsonRequest& request);
  PyMoneroJsonRequest(const std::string& method, const boost::optional<py::object>& params = boost::none);
  PyMoneroJsonRequest(const std::string& method, const std::shared_ptr<PyMoneroJsonRequestParams>& params);

  rapidjson::Value to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const override;
};

class PyMoneroJsonResponse {
public:
  boost::optional<std::string> m_jsonrpc;
  boost::optional<std::string> m_id;
  boost::optional<boost::property_tree::ptree> m_result;

  static std::shared_ptr<PyMoneroJsonResponse> deserialize(const std::string& response_json);

  PyMoneroJsonResponse(const PyMoneroJsonResponse& response): m_jsonrpc("2.0"), m_id("0"), m_result(response.m_result) {}
  PyMoneroJsonResponse(const boost::optional<boost::property_tree::ptree> &result = boost::none): m_jsonrpc("2.0"), m_id("0"), m_result(result) {}

  boost::optional<py::object> get_result() const;
};

class PyMoneroPathResponse {
public:
  boost::optional<boost::property_tree::ptree> m_response;

  PyMoneroPathResponse() { }
  PyMoneroPathResponse(const PyMoneroPathResponse& response): m_response(response.m_response) {}
  PyMoneroPathResponse(const boost::optional<boost::property_tree::ptree> &response): m_response(response) {}

  boost::optional<py::object> get_response() const;
  static std::shared_ptr<PyMoneroPathResponse> deserialize(const std::string& response_json);
};

class PyMoneroBinaryResponse {
public:
  boost::optional<std::string> m_binary;
  boost::optional<boost::property_tree::ptree> m_response;

  PyMoneroBinaryResponse() {}
  PyMoneroBinaryResponse(const std::string &binary): m_binary(binary) {}
  PyMoneroBinaryResponse(const PyMoneroBinaryResponse& response): m_binary(response.m_binary), m_response(response.m_response) {}

  static std::shared_ptr<PyMoneroBinaryResponse> deserialize(const std::string& response_binary);
  boost::optional<py::object> get_response() const;
};

// TODO refactory
class PyMoneroGetBlocksByHeightRequest : public PyMoneroBinaryRequest {
public:
  std::vector<uint64_t> m_heights;

  PyMoneroGetBlocksByHeightRequest(uint64_t num_blocks);
  PyMoneroGetBlocksByHeightRequest(const std::vector<uint64_t>& heights): m_heights(heights) { m_method = "get_blocks_by_height.bin"; }

  rapidjson::Value to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const override;
};

/**
 * Maintains a connection and sends requests to a Monero RPC API.
 *
 * TODO: refactor monero_rpc_connection extends monero_connection?
 */
class PyMoneroRpcConnection : public monero::monero_rpc_connection {
public:
  boost::optional<std::string> m_zmq_uri;  // TODO implement zmq listener
  int m_priority;                          // priority relative to other connections. 1 is highest, then priority 2, etc. Default prorioty is 0, lowest priority.
  uint64_t m_timeout;                      // RPC request timeout in milliseconds.
  boost::optional<long> m_response_time;   // automatically set by calling check_connection()

  /**
   * Checks rpc connection order.
   *
   * @param c1 first RPC connection to compare.
   * @param c2 second RPC connection to compare.
   * @param current_connection connection with highest priority.
   */
  static bool before(const std::shared_ptr<PyMoneroRpcConnection>& c1, const std::shared_ptr<PyMoneroRpcConnection>& c2, const std::shared_ptr<PyMoneroRpcConnection>& current_connection);

  /**
   * Initialize a new RPC connection.
   *
   * @param uri RPC connection uri.
   * @param username RPC connection authentication username.
   * @param password RPC connection authentication password.
   * @param proxy_uri RPC connection proxy uri.
   * @param zmq_uri RPC connection zmq uri.
   * @param priority RPC connection priority.
   * @param timeout RPC connection timeout in milliseconds.
   */
  PyMoneroRpcConnection(const std::string& uri = "", const std::string& username = "", const std::string& password = "", const std::string& proxy_uri = "", const std::string& zmq_uri = "", int priority = 0, uint64_t timeout = 20000);

  /**
   * Copy a RPC connection.
   *
   * @param rpc RPC connection to copy.
   */
  PyMoneroRpcConnection(const monero::monero_rpc_connection& rpc);

  /**
   * Indicates if the connection uri is a TOR server.
   *
   * @return true or false to indicate if connection uri is a TOR server.
   */
  bool is_onion() const;

  /**
   * Indicates if the connection uri is a I2P server.
   *
   * @return true or false to indicate if connection uri is a I2P server.
   */
  bool is_i2p() const;

  /**
   * Set connection credentials.
   *
   * @param username username to use in RPC authentication.
   * @param password password to use in RPC authentication.
   */
  void set_credentials(const std::string& username, const std::string& password);

  /**
   * Set connection attribute.
   *
   * @param key is the attribute key
   * @param val is the attribute value
   */
  void set_attribute(const std::string& key, const std::string& val);

  /**
   * Get connection attribute.
   *
   * @param key is the attribute to get the value of
   * @return key's value if set
   */
  std::string get_attribute(const std::string& key) const;

  /**
   * Indicates if the connection is online, which is set automatically by calling check_connection().
   *
   * @return true or false to indicate if online, or null if check_connection() has not been called
   */
  boost::optional<bool> is_online() const { return m_is_online; }

  /**
   * Indicates if the connection is authenticated, which is set automatically by calling check_connection().
   *
   * @return true if authenticated or no authentication, false if not authenticated, or null if not set
   */
  boost::optional<bool> is_authenticated() const { return m_is_authenticated; }

  /**
   * Indicates if the connection is connected, which is set automatically by calling check_connection().
   *
   * @return true or false to indicate if connected, or null if check_connection() has not been called
   */
  boost::optional<bool> is_connected() const;

  /**
   * Check the connection and update online, authentication, and response time status.
   *
   * @param timeout_ms the maximum response time before considered offline
   * @return
   */
  bool check_connection(const boost::optional<int>& timeout_ms = boost::none);

  /**
   * Resets the current connection.
   */
  void reset();

  /**
   * Send a request to the RPC API.
   *
   * @param path specifies the method to request
   * @param params are the request's input parameters
   * @return the RPC API response as a map
   */
  inline const boost::property_tree::ptree send_json_request(const std::string& path, const std::shared_ptr<PyMoneroJsonRequestParams>& params = nullptr) {
    PyMoneroJsonRequest request(path, params);
    auto response = send_json_request(request);

    if (response->m_result == boost::none) throw std::runtime_error("Invalid Monero JSONRPC response");
    return response->m_result.get();
  }

  /**
   * Send a request to the RPC API.
   *
   * @param request specifies the method to request with parameters
   * @param timeout request timeout in milliseconds
   * @return the RPC API response as a map
   */
  inline const std::shared_ptr<PyMoneroJsonResponse> send_json_request(const PyMoneroJsonRequest &request, std::chrono::milliseconds timeout = std::chrono::seconds(15)) {
    PyMoneroJsonResponse response;

    int result = invoke_post("/json_rpc", request, response, timeout);
    if (result != 200) throw PyMoneroRpcError(result, "HTTP error: code " + std::to_string(result));

    return std::make_shared<PyMoneroJsonResponse>(response);
  }

  /**
   * Send a RPC request to the given path and with the given paramters.
   *
   * E.g. "/get_transactions" with params
   *
   * @param path is the url path of the request to invoke
   * @param params are request parameters sent in the body
   * @return the RPC API response as a map
   */
  inline const boost::property_tree::ptree send_path_request(const std::string& path, const std::shared_ptr<PyMoneroRequestParams>& params = nullptr) {
    PyMoneroPathRequest request(path, params);
    auto response = send_path_request(request);

    if (response->m_response == boost::none) throw std::runtime_error("Invalid Monero path response");
    return response->m_response.get();
  }

  /**
   * Send a RPC request to the given path and with the given paramters.
   *
   * @param request specifies the method to request with parameters
   * @param timeout request timeout in milliseconds
   * @return the request's deserialized response
   */
  inline const std::shared_ptr<PyMoneroPathResponse> send_path_request(const PyMoneroPathRequest &request, std::chrono::milliseconds timeout = std::chrono::seconds(15)) {
    PyMoneroPathResponse response;

    if (request.m_method == boost::none || request.m_method->empty()) throw std::runtime_error("No RPC method set in path request");
    int result = invoke_post(std::string("/") + request.m_method.get(), request, response, timeout);
    if (result != 200) throw PyMoneroRpcError(result, "HTTP error: code " + std::to_string(result));

    return std::make_shared<PyMoneroPathResponse>(response);
  }

  /**
   * Send a binary RPC request.
   *
   * @param request specifies the method to request with paramesters
   * @param timeout request timeout in milliseconds
   * @return the request's deserialized response
   */
  inline const std::shared_ptr<PyMoneroBinaryResponse> send_binary_request(const PyMoneroBinaryRequest &request, std::chrono::milliseconds timeout = std::chrono::seconds(15)) {
    if (request.m_method == boost::none || request.m_method->empty()) throw std::runtime_error("No RPC method set in binary request");
    if (!m_http_client) throw std::runtime_error("http client not set");

    std::string uri = std::string("/") + request.m_method.get();
    std::string body = request.to_binary_val();

    const epee::net_utils::http::http_response_info* response = invoke_post(uri, body, timeout);
    int result = response->m_response_code;
    if (result != 200) throw PyMoneroRpcError(result, "HTTP error: code " + std::to_string(result));

    auto res = std::make_shared<PyMoneroBinaryResponse>();
    res->m_binary = response->m_body;

    return res;
  }

  // exposed python methods

  /**
   * Send a request to the RPC API.
   *
   * @param method specifies the method to request
   * @param parameters are the request's input parameters
   * @return the RPC API response as a map
   */
  inline boost::optional<py::object> send_json_request(const std::string& method, const boost::optional<py::object>& parameters) {
    PyMoneroJsonRequest request(method, parameters);
    auto response = send_json_request(request);
    return response->get_result();
  }

  /**
   * Send a RPC request to the given path and with the given paramters.
   *
   * E.g. "/get_transactions" with params
   *
   * @param method is the url path of the request to invoke
   * @param parameters are request parameters sent in the body
   * @return the RPC API response as a map
   */
  inline boost::optional<py::object> send_path_request(const std::string& method, const boost::optional<py::object>& parameters) {
    PyMoneroPathRequest request(method, parameters);
    auto response = send_path_request(request);
    return response->get_response();
  }

  /**
   * Send a binary RPC request.
   *
   * @param method specifies the method to request
   * @param parameters are request parameters sent in the body
   * @return the request's deserialized response
   */
  inline boost::optional<std::string> send_binary_request(const std::string& method, const boost::optional<py::object>& parameters) {
    PyMoneroBinaryRequest request(method, parameters);
    auto response = send_binary_request(request);
    return response->m_binary;
  }

  rapidjson::Value to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const override;

protected:
  // istance variables
  mutable boost::recursive_mutex m_mutex;
  std::string m_server;
  boost::optional<epee::net_utils::http::login> m_credentials;
  std::unique_ptr<epee::net_utils::http::abstract_http_client> m_http_client;
  std::unordered_map<std::string, std::string> m_attributes;
  boost::optional<bool> m_is_online;
  boost::optional<bool> m_is_authenticated;

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

};
