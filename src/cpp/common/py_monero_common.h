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

#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <boost/optional.hpp>

#include "net/http.h"
#include "daemon/monero_daemon_model.h"

namespace py = pybind11;

// ------------------------------ Utilities ---------------------------------

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

/**
 * Collection of generic utilities.
 */
class PyGenUtils {
public:
  static py::object convert_value(const std::string& val);
  static py::object ptree_to_pyobject(const boost::property_tree::ptree& tree);
  static boost::property_tree::ptree parse_json_string(const std::string &json);
};

class thread_poller {
public:
  ~thread_poller();

  bool is_polling() const { return m_is_polling; }
  void set_is_polling(bool is_polling);
  void set_period_in_ms(uint64_t period_ms) { m_poll_period_ms = period_ms; }
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

// ------------------------------ Errors ---------------------------------

class monero_error : public std::exception {
public:
  std::string message;

  monero_error() {}
  monero_error(const std::string& msg) : message(msg) {}

  const char* what() const noexcept override {
    return message.c_str();
  }
};

class monero_rpc_error : public monero_error {
public:
  int code;

  monero_rpc_error(int error_code, const std::string& msg) : code(error_code) { message = msg; }
  monero_rpc_error(const std::string& msg) : code(-1) { message = msg; }
};

// ------------------------------ Extended Data Model ---------------------------------

struct ssl_options : public monero::serializable_struct {
public:
  boost::optional<std::string> m_ssl_private_key_path;
  boost::optional<std::string> m_ssl_certificate_path;
  boost::optional<std::string> m_ssl_ca_file;
  std::vector<std::string> m_ssl_allowed_fingerprints;
  boost::optional<bool> m_ssl_allow_any_cert;

  rapidjson::Value to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const override;
};

enum monero_connection_type : uint8_t {
  INVALID = 0,
  IPV4,
  IPV6,
  TOR,
  I2P
};

// ------------------------------ RPC Request ---------------------------------

struct monero_request : public monero::serializable_struct {
public:
  boost::optional<std::string> m_method;

  monero_request() { }
};

struct monero_request_params : public monero::serializable_struct {
public:
  boost::optional<py::object> m_py_params;

  monero_request_params() { }
  monero_request_params(const boost::optional<py::object>& py_params): m_py_params(py_params) { }

  rapidjson::Value to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const override;
};

struct monero_path_request : public monero_request {
public:
  boost::optional<std::shared_ptr<monero_request_params>> m_params;

  monero_path_request() { }
  monero_path_request(const std::string& method, const boost::optional<py::object>& params = boost::none);
  monero_path_request(const std::string& method, const std::shared_ptr<monero_request_params>& params);

  rapidjson::Value to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const override;
};

struct monero_binary_request : public monero_path_request {
public:
  monero_binary_request() { }
  monero_binary_request(const std::string& method, const boost::optional<py::object>& params = boost::none);

  std::string to_binary_val() const;
};

struct monero_json_request_params : public monero_request_params {
public:
  monero_json_request_params() { }
  monero_json_request_params(const boost::optional<py::object>& py_params);
};

struct monero_json_request : public monero_request {
public:
  boost::optional<std::string> m_version;
  boost::optional<std::string> m_id;
  boost::optional<std::shared_ptr<monero_json_request_params>> m_params;

  monero_json_request(const std::string& method, const boost::optional<py::object>& params = boost::none);
  monero_json_request(const std::string& method, const std::shared_ptr<monero_json_request_params>& params);

  rapidjson::Value to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const override;
};

struct monero_get_blocks_by_height_request : public monero_binary_request {
public:
  std::vector<uint64_t> m_heights;

  monero_get_blocks_by_height_request(uint64_t num_blocks);
  monero_get_blocks_by_height_request(const std::vector<uint64_t>& heights): m_heights(heights) { m_method = "get_blocks_by_height.bin"; }

  rapidjson::Value to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const override;
};

// ------------------------------ RPC Response ---------------------------------

struct monero_json_response {
public:
  boost::optional<std::string> m_jsonrpc;
  boost::optional<std::string> m_id;
  boost::optional<boost::property_tree::ptree> m_result;

  static void raise_rpc_error(const boost::property_tree::ptree& error_node);
  static std::shared_ptr<monero_json_response> deserialize(const std::string& response_json);

  monero_json_response(const monero_json_response& response): m_jsonrpc("2.0"), m_id("0"), m_result(response.m_result) {}
  monero_json_response(const boost::optional<boost::property_tree::ptree> &result = boost::none): m_jsonrpc("2.0"), m_id("0"), m_result(result) {}

  boost::optional<py::object> get_result() const;
};

struct monero_path_response {
public:
  boost::optional<boost::property_tree::ptree> m_response;

  monero_path_response() { }
  monero_path_response(const monero_path_response& response): m_response(response.m_response) {}
  monero_path_response(const boost::optional<boost::property_tree::ptree> &response): m_response(response) {}

  boost::optional<py::object> get_response() const;
  static std::shared_ptr<monero_path_response> deserialize(const std::string& response_json);
};

struct monero_binary_response {
public:
  boost::optional<std::string> m_binary;
  boost::optional<boost::property_tree::ptree> m_response;

  monero_binary_response() { }
  monero_binary_response(const std::string &binary): m_binary(binary) { }
  monero_binary_response(const monero_binary_response& response): m_binary(response.m_binary), m_response(response.m_response) { }
};

// ------------------------------ Custom RPC Connection ---------------------------------

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
   * Checks connection priority order.
   *
   * @param c1 first priority to compare.
   * @param c2 second priority to compare.
   */
  static bool compare(int p1, int p2);

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
  const boost::property_tree::ptree send_json_request(const std::string& path, const std::shared_ptr<monero_json_request_params>& params = nullptr);

  /**
   * Send a request to the RPC API.
   *
   * @param request specifies the method to request with parameters
   * @param timeout request timeout in milliseconds
   * @return the RPC API response as a map
   */
  const std::shared_ptr<monero_json_response> send_json_request(const monero_json_request &request, std::chrono::milliseconds timeout = std::chrono::seconds(15));

  /**
   * Send a RPC request to the given path and with the given paramters.
   *
   * E.g. "/get_transactions" with params
   *
   * @param path is the url path of the request to invoke
   * @param params are request parameters sent in the body
   * @return the RPC API response as a map
   */
  const boost::property_tree::ptree send_path_request(const std::string& path, const std::shared_ptr<monero_request_params>& params = nullptr);

  /**
   * Send a RPC request to the given path and with the given paramters.
   *
   * @param request specifies the method to request with parameters
   * @param timeout request timeout in milliseconds
   * @return the request's deserialized response
   */
  const std::shared_ptr<monero_path_response> send_path_request(const monero_path_request &request, std::chrono::milliseconds timeout = std::chrono::seconds(15));

  /**
   * Send a binary RPC request.
   *
   * @param request specifies the method to request with paramesters
   * @param timeout request timeout in milliseconds
   * @return the request's deserialized response
   */
  const std::shared_ptr<monero_binary_response> send_binary_request(const monero_binary_request &request, std::chrono::milliseconds timeout = std::chrono::seconds(15));

  // exposed python methods

  /**
   * Send a request to the RPC API.
   *
   * @param method specifies the method to request
   * @param parameters are the request's input parameters
   * @return the RPC API response as a map
   */
  boost::optional<py::object> send_json_request(const std::string& method, const boost::optional<py::object>& parameters);

  /**
   * Send a RPC request to the given path and with the given paramters.
   *
   * E.g. "/get_transactions" with params
   *
   * @param method is the url path of the request to invoke
   * @param parameters are request parameters sent in the body
   * @return the RPC API response as a map
   */
  boost::optional<py::object> send_path_request(const std::string& method, const boost::optional<py::object>& parameters);

  /**
   * Send a binary RPC request.
   *
   * @param method specifies the method to request
   * @param parameters are request parameters sent in the body
   * @return the request's deserialized response
   */
  boost::optional<py::bytes> send_binary_request(const std::string& method, const boost::optional<py::object>& parameters);

  rapidjson::Value to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const override;

protected:
  // instance variables
  mutable boost::recursive_mutex m_mutex;
  std::string m_server;
  boost::optional<epee::net_utils::http::login> m_credentials;
  std::unique_ptr<epee::net_utils::http::abstract_http_client> m_http_client;
  std::unordered_map<std::string, std::string> m_attributes;
  boost::optional<bool> m_is_online;
  boost::optional<bool> m_is_authenticated;

  const epee::net_utils::http::http_response_info* invoke_post(const boost::string_ref uri, const std::string& body, std::chrono::milliseconds timeout = std::chrono::seconds(15)) const;

  template<class t_request, class t_response>
  inline int invoke_post(const boost::string_ref uri, const t_request& request, t_response& res, std::chrono::milliseconds timeout = std::chrono::seconds(15)) const {
    std::string body = request.serialize();
    const epee::net_utils::http::http_response_info* response = invoke_post(uri, body, timeout);
    if (response->m_response_code == 200) {
      res = *t_response::deserialize(response->m_body);
    }
    return response->m_response_code;
  }

};
