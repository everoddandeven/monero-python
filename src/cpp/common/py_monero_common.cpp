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
#include <boost/asio/thread_pool.hpp>
#include <boost/asio/post.hpp>
#include <boost/thread.hpp>
#include <queue>
#include <atomic>
#include "py_monero_common.h"
#include "utils/monero_utils.h"

// --------------------------- THREAD POLLER ---------------------------

thread_poller::~thread_poller() {
  set_is_polling(false);
}

void thread_poller::init_common(const std::string& name) {
  m_name = name;
  m_is_polling = false;
  m_poll_period_ms = 20000;
  m_poll_loop_running = false;
}

void thread_poller::set_is_polling(bool is_polling) {
  if (is_polling == m_is_polling) return;
  m_is_polling = is_polling;

  if (m_is_polling) {
    run_poll_loop();
  } else {
    if (m_poll_loop_running) {
      m_poll_cv.notify_one();
      // TODO: in emscripten, m_poll_cv.notify_one() returns without waiting, so sleep; bug in emscripten upstream llvm?
      std::this_thread::sleep_for(std::chrono::milliseconds(1));
      if (m_thread.joinable()) m_thread.join();
    }
  }
}

void thread_poller::run_poll_loop() {
  if (m_poll_loop_running.exchange(true)) return; // only run one loop at a time

  // start pool loop thread
  // TODO: use global threadpool, background sync wasm wallet in c++ thread
  m_thread = boost::thread([this]() {

    // poll while enabled
    while (m_is_polling) {
      try { poll(); }
      catch (const std::exception& e) { MERROR(m_name << " failed to background poll: " << e.what()); }
      catch (...) { MERROR(m_name << " failed to background poll"); }

      // only wait if polling still enabled
      if (m_is_polling) {
        boost::mutex::scoped_lock lock(m_polling_mutex);
        boost::posix_time::milliseconds wait_for_ms(m_poll_period_ms.load());
        m_poll_cv.timed_wait(lock, wait_for_ms, [&]() { return !m_is_polling; });
      }
    }

    m_poll_loop_running.exchange(false);
  });
}

// --------------------------- KEY VALUE ---------------------------

void key_value::from_property_tree(const boost::property_tree::ptree& node, const std::shared_ptr<key_value>& attributes) {
  attributes->m_key = boost::none;
  attributes->m_value = boost::none;

  for (boost::property_tree::ptree::const_iterator it = node.begin(); it != node.end(); ++it) {
    std::string key = it->first;
    if (key == std::string("key")) attributes->m_key = it->second.data();
    else if (key == std::string("value")) attributes->m_value = it->second.data();
  }
}

rapidjson::Value key_value::to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const {
  // create root
  rapidjson::Value root(rapidjson::kObjectType);

  // set string values
  rapidjson::Value value_str(rapidjson::kStringType);
  if (m_key != boost::none) monero_utils::add_json_member("key", m_key.get(), allocator, root, value_str);
  if (m_value != boost::none) monero_utils::add_json_member("value", m_value.get(), allocator, root, value_str);

  // return root
  return root;
}

// --------------------------- GEN UTILS ---------------------------

py::object PyGenUtils::convert_value(const std::string& val) {
  if (val == "true") return py::bool_(true);
  if (val == "false") return py::bool_(false);

  try {
    std::size_t pos;
    int i = std::stoi(val, &pos);
    if (pos == val.size()) return py::int_(i);
  } catch (...) {}

  try {
    std::size_t pos;
    double d = std::stod(val, &pos);
    if (pos == val.size()) return py::float_(d);
  } catch (...) {}

  return py::str(val);
}

py::object PyGenUtils::ptree_to_pyobject(const boost::property_tree::ptree& tree) {
  if (tree.empty()) {
    return convert_value(tree.get_value<std::string>());
  }

  bool is_array = true;
  for (const auto& child : tree) {
    if (child.first != "") {
      is_array = false;
      break;
    }
  }

  if (is_array) {
    py::list lst;
    for (const auto& child : tree) {
      lst.append(ptree_to_pyobject(child.second));
    }
    return lst;
  }
  else {
    py::dict d;
    if (!tree.get_value<std::string>().empty()) {
      d["__value__"] = convert_value(tree.get_value<std::string>());
    }
    for (const auto& child : tree) {
      d[py::str(child.first)] = ptree_to_pyobject(child.second);
    }

    return d;
  }
}

boost::property_tree::ptree PyGenUtils::parse_json_string(const std::string &json) {
  boost::property_tree::ptree pt;
  std::istringstream iss(json);
  boost::property_tree::read_json(iss, pt);
  return pt;
}

// --------------------------- SSL OPTIONS ---------------------------

rapidjson::Value ssl_options::to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const {
  // create root
  rapidjson::Value root(rapidjson::kObjectType);

  // set string values
  rapidjson::Value value_str(rapidjson::kStringType);
  if (m_ssl_private_key_path != boost::none) monero_utils::add_json_member("sslPrivateKeyPath", m_ssl_private_key_path.get(), allocator, root, value_str);
  if (m_ssl_certificate_path != boost::none) monero_utils::add_json_member("sslCertificatePath", m_ssl_certificate_path.get(), allocator, root, value_str);
  if (m_ssl_ca_file != boost::none) monero_utils::add_json_member("sslCaFile", m_ssl_ca_file.get(), allocator, root, value_str);
  if (m_ssl_private_key_path != boost::none) monero_utils::add_json_member("sslPrivateKeyPath", m_ssl_private_key_path.get(), allocator, root, value_str);
  if (!m_ssl_allowed_fingerprints.empty()) root.AddMember("sslAllowedFingerprints", monero_utils::to_rapidjson_val(allocator, m_ssl_allowed_fingerprints), allocator);

  // set bool values
  if (m_ssl_allow_any_cert != boost::none) monero_utils::add_json_member("sslAllowAnyCert", m_ssl_allow_any_cert.get(), allocator, root);

  return root;
}

// --------------------------- MONERO REQUEST PARAMS ---------------------------

rapidjson::Value monero_request_params::to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const {
  rapidjson::Value root(rapidjson::kObjectType);

  if (m_py_params != boost::none) {
    // convert python dict params to rapidjson::Value
    py::module json = py::module::import("json");
    std::string json_string = json.attr("dumps")(m_py_params.get()).cast<std::string>();

    rapidjson::Document doc;
    doc.Parse(json_string.c_str());
    root.Swap(doc);
  }

  return root;
}

// --------------------------- MONERO RPC REQUEST ---------------------------

monero_rpc_request::monero_rpc_request(const std::string& method, const boost::optional<py::object>& params, bool json_rpc): m_method(method), m_params(std::make_shared<monero_request_params>(params)) {
  if (json_rpc) {
    m_id = "0";
    m_version = "2.0";
  }
}

monero_rpc_request::monero_rpc_request(const std::string& method, const std::shared_ptr<monero::serializable_struct>& params, bool json_rpc): m_method(method), m_params(params) {
  if (params == nullptr) m_params = std::make_shared<monero_request_params>();
  if (json_rpc) {
    m_id = "0";
    m_version = "2.0";
  }
}

rapidjson::Value monero_rpc_request::to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const {
  if (!is_json_rpc()) {
    if (m_params == boost::none) throw std::runtime_error("No params provided");
    return m_params.get()->to_rapidjson_val(allocator);
  }

  // create root
  rapidjson::Value root(rapidjson::kObjectType);

  // set string values
  rapidjson::Value value_str(rapidjson::kStringType);

  if (m_version != boost::none) monero_utils::add_json_member("version", m_version.get(), allocator, root, value_str);
  if (m_id != boost::none) monero_utils::add_json_member("id", m_id.get(), allocator, root, value_str);
  if (m_method != boost::none) monero_utils::add_json_member("method", m_method.get(), allocator, root, value_str);
  if (m_params != boost::none) root.AddMember("params", m_params.get()->to_rapidjson_val(allocator), allocator);

  // return root
  return root;
}

std::string monero_rpc_request::to_binary_val() const {
  std::string json_val = serialize();
  std::string binary_val;
  monero_utils::json_to_binary(json_val, binary_val);
  return binary_val;
}

// --------------------------- MONERO GET BLOCKS BY HEIGHT REQUEST ---------------------------

monero_get_blocks_by_height_request::monero_get_blocks_by_height_request(uint64_t num_blocks) {
  m_method = "get_blocks_by_height.bin";
  m_heights.reserve(num_blocks);
  for (uint64_t i = 0; i < num_blocks; i++) m_heights.push_back(i);
}

rapidjson::Value monero_get_blocks_by_height_request::to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const {
  rapidjson::Value root(rapidjson::kObjectType);
  if (!m_heights.empty()) root.AddMember("heights", monero_utils::to_rapidjson_val(allocator, m_heights), allocator);
  return root;
}

// --------------------------- MONERO RPC RESPONSE ---------------------------

void monero_rpc_response::raise_rpc_error(const boost::property_tree::ptree& error_node) {
  std::string err_message = "Unknown error";
  int err_code = -1;

  for (auto it = error_node.begin(); it != error_node.end(); ++it) {
    std::string key_err = it->first;
    if (key_err == std::string("message")) {
      err_message = it->second.data();
    } else if (key_err == std::string("code")) {
      err_code = it->second.get_value<int>();
    }
  }

  throw monero_rpc_error(err_code, err_message);
}

std::shared_ptr<monero_rpc_response> monero_rpc_response::deserialize(const std::string& response_json) {
  // parse json to property node
  boost::property_tree::ptree node;
  monero_utils::deserialize(response_json, node);
  auto response = std::make_shared<monero_rpc_response>();

  for (boost::property_tree::ptree::const_iterator it = node.begin(); it != node.end(); ++it) {
    std::string key = it->first;
    if (key == std::string("error")) {
      raise_rpc_error(it->second);
    }
    else if (key == std::string("jsonrpc")) {
      response->m_jsonrpc = it->second.data();
    }
    else if (key == std::string("result")) {
      response->m_result = it->second;
    }
  }

  if (response->m_jsonrpc == boost::none) {
    boost::property_tree::ptree node;
    monero_utils::deserialize(response_json, node);
    response->m_response = node;
  }

  return response;
}


// --------------------------- MONERO RPC CONNECTION ---------------------------

bool PyMoneroRpcConnection::before(const std::shared_ptr<PyMoneroRpcConnection>& c1, const std::shared_ptr<PyMoneroRpcConnection>& c2, const std::shared_ptr<PyMoneroRpcConnection>& current_connection) {
  // current connection is first
  if (c1 == current_connection) return true;
  if (c2 == current_connection) return false;

  // order by availability then priority then by name
  if (c1->m_is_online == c2->m_is_online) {
    if (c1->m_priority == c2->m_priority) {
      // order by priority in descending order
      return c1->m_uri.value_or("") < c2->m_uri.value_or("");
    }
    // order by priority in descending order
    return !compare(c1->m_priority, c2->m_priority);
  } else {
    if (c1->m_is_online != boost::none && c1->m_is_online.get()) return true;
    else if (c2->m_is_online != boost::none && c2->m_is_online.get()) return false;
    else if (c1->m_is_online == boost::none) return true;
    // c1 is offline
    return false;
  }
}

bool PyMoneroRpcConnection::compare(int p1, int p2) {
  if (p1 == p2) return false;
  // 0 alway first
  if (p1 == 0) return true;
  if (p2 == 0) return false;
  return p1 > p2;
}

PyMoneroRpcConnection::PyMoneroRpcConnection(const std::string& uri, const std::string& username, const std::string& password, const std::string& proxy_uri, const std::string& zmq_uri, int priority, uint64_t timeout) {
  if (!uri.empty()) m_uri = uri;
  else m_uri = boost::none;
  if (!proxy_uri.empty()) m_proxy_uri = proxy_uri;
  else m_proxy_uri = boost::none;
  if (!zmq_uri.empty()) m_zmq_uri = zmq_uri;
  else m_zmq_uri = boost::none;
  m_priority = priority;
  m_timeout = timeout;
  set_credentials(username, password);
}

PyMoneroRpcConnection::PyMoneroRpcConnection(const monero::monero_rpc_connection& rpc) {
  m_uri = rpc.m_uri;
  m_proxy_uri = rpc.m_proxy_uri;
  m_priority = 0;
  m_timeout = 20000;
  // TODO move this definitions to monero-cpp
  //m_zmq_uri = rpc.m_zmq_uri;
  //m_priority = rpc.m_priority;
  //m_timeout = rpc.m_timeout;
  //m_is_online = rpc.m_is_online;
  //m_is_authenticated = rpc.m_is_authenticated;
  //m_response_time = rpc.m_response_time;
  set_credentials(rpc.m_username.value_or(""), rpc.m_password.value_or(""));
}

rapidjson::Value PyMoneroRpcConnection::to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const {
  // create root
  rapidjson::Value root = monero_rpc_connection::to_rapidjson_val(allocator);

  // set string values
  rapidjson::Value value_str(rapidjson::kStringType);
  if (m_zmq_uri != boost::none) monero_utils::add_json_member("zmqUri", m_zmq_uri.get(), allocator, root, value_str);

  // set num values
  rapidjson::Value value_num(rapidjson::kNumberType);
  monero_utils::add_json_member("priority", m_priority, allocator, root, value_num);
  monero_utils::add_json_member("timeout", m_timeout, allocator, root, value_num);
  if (m_response_time != boost::none) monero_utils::add_json_member("responseTime", m_response_time.get(), allocator, root, value_num);

  // set bool values
  if (m_is_online != boost::none) monero_utils::add_json_member("isOnline", m_is_online.get(), allocator, root);
  if (m_is_authenticated != boost::none) monero_utils::add_json_member("isAuthenticated", m_is_authenticated.get(), allocator, root);

  return root;
}

bool PyMoneroRpcConnection::is_onion() const {
  // check onion uri
  return m_uri != boost::none && m_uri->size() >= 6 && m_uri->compare(m_uri->size() - 6, 6, ".onion") == 0;
}

bool PyMoneroRpcConnection::is_i2p() const {
  // check i2p uri
  return m_uri != boost::none && m_uri->size() >= 8 && m_uri->compare(m_uri->size() - 8, 8, ".b32.i2p") == 0;
}

void PyMoneroRpcConnection::set_credentials(const std::string& username, const std::string& password) {
  // reset http client
  if (m_http_client != nullptr) {
    if (m_http_client->is_connected()) {
      m_http_client->disconnect();
    }
  } else {
    auto factory = new net::http::client_factory();
    m_http_client = factory->create();
  }

  bool username_empty = username.empty();
  bool password_empty = password.empty();

  // check username and password consistency
  if (!username_empty || !password_empty) {
    if (password_empty) {
      throw monero_error("password cannot be empty because username is not empty");
    }

    if (username_empty) {
      throw monero_error("username cannot be empty because password is not empty");
    }
  }

  // check username and password changes
  bool username_equals = (m_username == boost::none && username_empty) || (m_username != boost::none && *m_username == username);
  bool password_equals = (m_password == boost::none && password_empty) || (m_password != boost::none && *m_password == password);

  // connection reset values
  if (!username_equals || !password_equals) {
    m_is_online = boost::none;
    m_is_authenticated = boost::none;
  }

  // setup username and password
  if (!username_empty && !password_empty) {
    m_username = username;
    m_password = password;
  } else {
    m_username = boost::none;
    m_password = boost::none;
  }
}

void PyMoneroRpcConnection::set_attribute(const std::string& key, const std::string& val) {
  m_attributes[key] = val;
}

std::string PyMoneroRpcConnection::get_attribute(const std::string& key) const {
  std::unordered_map<std::string, std::string>::const_iterator i = m_attributes.find(key);
  if (i == m_attributes.end()) {
    // attribute not found
    return std::string("");
  }
  return i->second;
}

boost::optional<bool> PyMoneroRpcConnection::is_connected() const {
  if (m_is_online == boost::none) return boost::none;
  return m_is_online.get() && (m_is_authenticated == boost::none || m_is_authenticated.get());
}

void PyMoneroRpcConnection::reset() {
  boost::lock_guard<boost::recursive_mutex> lock(m_mutex);
  if (!m_http_client) throw std::runtime_error("http client not set");

  // disconnect http client
  if (m_http_client->is_connected()) {
    m_http_client->disconnect();
  }

  // set empty proxy
  if(!m_http_client->set_proxy(m_proxy_uri.value_or(""))) {
    throw std::runtime_error("Could not set proxy");
  }

  // reset instance variables
  m_is_online = boost::none;
  m_is_authenticated = boost::none;
  m_response_time = boost::none;
}

bool PyMoneroRpcConnection::check_connection(const boost::optional<int>& timeout_ms) {
  boost::optional<bool> is_online_before = m_is_online;
  boost::optional<bool> is_authenticated_before = m_is_authenticated;
  boost::lock_guard<boost::recursive_mutex> lock(m_mutex);
  auto start = std::chrono::high_resolution_clock::now();
  try {
    reset();

    // setup connection credentials
    if(m_username != boost::none && !m_username->empty() && m_password != boost::none && !m_password->empty()) {
      auto credentials = std::make_shared<epee::net_utils::http::login>();
      credentials->username = *m_username;
      credentials->password = *m_password;
      m_credentials = *credentials;
    }
    else m_credentials = boost::none;

    if (!m_http_client->set_server(m_uri.value_or(""), m_credentials)) {
      throw std::runtime_error("Could not set rpc connection: " + m_uri.get());
    }

    m_http_client->connect(std::chrono::milliseconds(timeout_ms == boost::none ? m_timeout : *timeout_ms));

    // assume daemon connection
    monero_get_blocks_by_height_request request(100);
    send_binary_request(request);
    m_is_online = true;
    m_is_authenticated = true;
  }
  catch (const monero_rpc_error& ex) {
    m_is_online = false;
    m_is_authenticated = boost::none;
    m_response_time = boost::none;

    if (ex.code == 401) {
      // TODO monero-project epee http client doesn't propagate 401 error code
      m_is_online = true;
      m_is_authenticated = false;
    }
    else if (ex.code == 404) {
      // fallback to latency check
      m_is_online = true;
      m_is_authenticated = true;
    }
  }
  catch (const std::exception& ex) {
    if(ex.what() == std::string("Network error") && m_http_client->is_connected()) {
      // TODO implement custom epee http client with 401 error handler?
      m_is_online = true;
      m_is_authenticated = false;
    } else {
      m_is_online = false;
      m_is_authenticated = boost::none;
      m_response_time = boost::none;
    }
  }

  if (*m_is_online) {
    // set response time
    auto end = std::chrono::high_resolution_clock::now();
    auto duration = std::chrono::duration_cast<std::chrono::milliseconds>(end - start);
    m_response_time = duration.count();
  }

  return is_online_before != m_is_online || is_authenticated_before != m_is_authenticated;
}

const boost::property_tree::ptree PyMoneroRpcConnection::send_json_request(const std::string& path, const std::shared_ptr<monero::serializable_struct>& params) {
  monero_rpc_request request(path, params);
  // send JSON-RPC request
  auto response = send_json_request(request);
  // assert JSON-RPC response is defined
  if (response.m_result == boost::none) throw std::runtime_error("Invalid Monero JSONRPC response");
  return response.m_result.get();
}

const monero_rpc_response PyMoneroRpcConnection::send_json_request(const monero_rpc_request &request, std::chrono::milliseconds timeout) {
  monero_rpc_response response;
  // invoke JSON-RPC method
  int result = invoke_post("/json_rpc", request, response, timeout);
  // check status code
  if (result != 200) throw monero_rpc_error(result, "HTTP error: code " + std::to_string(result));
  // return JSON-RPC response
  return response;
}

const boost::property_tree::ptree PyMoneroRpcConnection::send_path_request(const std::string& path, const std::shared_ptr<monero::serializable_struct>& params) {
  monero_rpc_request request(path, params, false);
  // send RPC request
  auto response = send_path_request(request);
  // assert RPC response is defined
  if (response.m_response == boost::none) throw std::runtime_error("Invalid Monero RPC response");
  return response.m_response.get();
}

const monero_rpc_response PyMoneroRpcConnection::send_path_request(const monero_rpc_request &request, std::chrono::milliseconds timeout) {
  // validate parameters
  if (request.m_method == boost::none || request.m_method->empty()) throw std::runtime_error("No RPC method set in path request");
  monero_rpc_response response;

  // invoke RPC method
  int result = invoke_post(std::string("/") + request.m_method.get(), request, response, timeout);

  // check status code
  if (result != 200) throw monero_rpc_error(result, "HTTP error: code " + std::to_string(result));

  // return RPC response
  return response;
}

const monero_rpc_response PyMoneroRpcConnection::send_binary_request(const monero_rpc_request &request, std::chrono::milliseconds timeout) {
  // validate parameters
  if (request.m_method == boost::none || request.m_method->empty()) throw std::runtime_error("No RPC method set in binary request");

  // invoke Binary RPC method
  std::string uri = std::string("/") + request.m_method.get();
  std::string body = request.to_binary_val();
  const epee::net_utils::http::http_response_info* info = invoke_post(uri, body, timeout);

  // check response code
  if (info->m_response_code != 200) throw monero_rpc_error(info->m_response_code, "HTTP error: code " + std::to_string(info->m_response_code));

  // return binary response
  monero_rpc_response response;
  response.m_binary = info->m_body;
  return response;
}

boost::optional<py::object> PyMoneroRpcConnection::send_json_request(const std::string& method, const boost::optional<py::object>& parameters) {
  // send JSON-RPC request with py::object parameters
  monero_rpc_request request(method, parameters);
  auto response = send_json_request(request);
  boost::optional<py::object> res;
  if (response.m_result != boost::none) res = PyGenUtils::ptree_to_pyobject(*response.m_result);
  return res;
}

boost::optional<py::object> PyMoneroRpcConnection::send_path_request(const std::string& method, const boost::optional<py::object>& parameters) {
  // send RPC request with py::object parameters
  monero_rpc_request request(method, parameters);
  auto response = send_path_request(request);
  boost::optional<py::object> res;
  if (response.m_response != boost::none) res = PyGenUtils::ptree_to_pyobject(*response.m_response);
  return res;
}

boost::optional<py::bytes> PyMoneroRpcConnection::send_binary_request(const std::string& method, const boost::optional<py::object>& parameters) {
  // send Binary RPC request with py::object parameters
  monero_rpc_request request(method, parameters, false);
  auto response = send_binary_request(request);
  if (response.m_binary == boost::none || response.m_binary->empty()) {
    // return empty response
    return boost::none;
  }

  // convert binary string to py::bytes
  return py::bytes(response.m_binary.get());
}

const epee::net_utils::http::http_response_info* PyMoneroRpcConnection::invoke_post(const boost::string_ref uri, const std::string& body, std::chrono::milliseconds timeout) const {
  // assert internal http client is initialized
  if (!m_http_client) throw std::runtime_error("http client not initialized.");

  boost::lock_guard<boost::recursive_mutex> lock(m_mutex);
  const epee::net_utils::http::http_response_info* pri = NULL;

  // invoke http json
  if (!m_http_client->invoke_post(uri, body, timeout, std::addressof(pri))) throw std::runtime_error("Network error");
  if (!pri) throw std::runtime_error("Could not get response info");
  // return response info
  return pri;
}
