#include <boost/asio/thread_pool.hpp>
#include <boost/asio/post.hpp>
#include <boost/thread.hpp>
#include <queue>
#include <atomic>
#include "py_monero_common.h"
#include "utils/monero_utils.h"

boost::property_tree::ptree json_to_property_node(const std::string& json) {
  // deserialize json to property node
  std::istringstream iss = json.empty() ? std::istringstream() : std::istringstream(json);
  boost::property_tree::ptree node;
  boost::property_tree::read_json(iss, node);
  return node;
}

PyThreadPoller::~PyThreadPoller() {
  set_is_polling(false);
}

void PyThreadPoller::init_common(const std::string& name) {
  m_name = name;
  m_is_polling = false;
  m_poll_period_ms = 20000;
  m_poll_loop_running = false;
}

void PyThreadPoller::set_is_polling(bool is_polling) {
  if (is_polling == m_is_polling) return;
  m_is_polling = is_polling;

  if (m_is_polling) {
    run_poll_loop();
  } else {
    if (m_poll_loop_running) {
      m_poll_cv.notify_one();
      // TODO: in emscripten, m_sync_cv.notify_one() returns without waiting, so sleep; bug in emscripten upstream llvm?
      std::this_thread::sleep_for(std::chrono::milliseconds(1));
      if (m_thread.joinable()) m_thread.join();
    }
  }
}

void PyThreadPoller::set_period_in_ms(uint64_t period_ms) {
  m_poll_period_ms = period_ms;
}

void PyThreadPoller::run_poll_loop() {
  if (m_poll_loop_running.exchange(true)) return; // only run one loop at a time

  // start pool loop thread
  // TODO: use global threadpool, background sync wasm wallet in c++ thread
  m_thread = boost::thread([this]() {

    // poll while enabled
    while (m_is_polling) {
      try { poll(); }
      catch (const std::exception& e) { std::cout << m_name << " failed to background poll: " << e.what() << std::endl; }
      catch (...) { std::cout << m_name << " failed to background poll" << std::endl; }

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

boost::property_tree::ptree PyGenUtils::pyobject_to_ptree(const py::object& obj) {
  boost::property_tree::ptree tree;

  if (py::isinstance<py::dict>(obj)) {
    py::dict d = obj.cast<py::dict>();
    for (auto item : d) {
      std::string key = py::str(item.first);
      py::object val = py::reinterpret_borrow<py::object>(item.second);

      if (key == "__value__") {
        tree.put_value(py::str(val));
        continue;
      }

      boost::property_tree::ptree child = pyobject_to_ptree(val);
      tree.add_child(key, child);
    }
  }
  else if (py::isinstance<py::list>(obj) || py::isinstance<py::tuple>(obj)) {
    py::sequence seq = obj.cast<py::sequence>();
    for (py::handle item : seq) {
      py::object val = py::reinterpret_borrow<py::object>(item);
      tree.push_back(std::make_pair("", pyobject_to_ptree(val)));
    }
  }
  else if (py::isinstance<py::bool_>(obj)) {
    tree.put_value(obj.cast<bool>() ? "true" : "false");
  }
  else if (py::isinstance<py::int_>(obj)) {
    tree.put_value(std::to_string(obj.cast<int>()));
  }
  else if (py::isinstance<py::float_>(obj)) {
    tree.put_value(std::to_string(obj.cast<double>()));
  }
  else {
    tree.put_value(obj.cast<std::string>());
  }

  return tree;
}

boost::property_tree::ptree PyGenUtils::parse_json_string(const std::string &json) {
  boost::property_tree::ptree pt;
  std::istringstream iss(json);
  boost::property_tree::read_json(iss, pt);
  return pt;
}

PyMoneroPathRequest::PyMoneroPathRequest(const std::string& method, const boost::optional<py::object>& params) {
  m_method = method;
  if (params != boost::none) m_params = std::make_shared<PyMoneroRequestParams>(params);
  else m_params = std::make_shared<PyMoneroRequestEmptyParams>();
}

PyMoneroPathRequest::PyMoneroPathRequest(const std::string& method, const std::shared_ptr<PyMoneroRequestParams>& params):
  m_params(params) {
  m_method = method;
  if (params == nullptr) m_params = std::make_shared<PyMoneroRequestEmptyParams>();
}

PyMoneroBinaryRequest::PyMoneroBinaryRequest(const std::string& method, const boost::optional<py::object>& params) {
  m_method = method;
  if (params != boost::none) m_params = std::make_shared<PyMoneroRequestParams>(params);
  m_params = std::make_shared<PyMoneroRequestEmptyParams>();
}

PyMoneroBinaryRequest::PyMoneroBinaryRequest(const std::string& method, const std::shared_ptr<PyMoneroRequestParams>& params) {
  m_method = method;
  m_params = params;
}

PyMoneroJsonRequestParams::PyMoneroJsonRequestParams(const boost::optional<py::object>& py_params) {
  m_py_params = py_params;
}

PyMoneroJsonRequest::PyMoneroJsonRequest():
  m_version("2.0"),
  m_id("0") {
  m_params = std::make_shared<PyMoneroJsonRequestEmptyParams>();
}

PyMoneroJsonRequest::PyMoneroJsonRequest(const PyMoneroJsonRequest& request):
  m_version(request.m_version),
  m_id(request.m_id),
  m_params(request.m_params)
{
  m_method = request.m_method;
}

PyMoneroJsonRequest::PyMoneroJsonRequest(const std::string& method, const boost::optional<py::object>& params):
  m_version("2.0"),
  m_id("0") {
  m_method = method;
  if (params != boost::none) {
    m_params = std::make_shared<PyMoneroJsonRequestParams>(params);
  }
  else m_params = std::make_shared<PyMoneroJsonRequestEmptyParams>();
}

PyMoneroJsonRequest::PyMoneroJsonRequest(const std::string& method, const std::shared_ptr<PyMoneroJsonRequestParams>& params):
  m_version("2.0"),
  m_id("0"),
  m_params(params) {
  m_method = method;
  if (params == nullptr) m_params = boost::none;
}

PyMoneroGetBlocksByHeightRequest::PyMoneroGetBlocksByHeightRequest(uint64_t num_blocks) {
  m_method = "get_blocks_by_height.bin";
  m_heights.reserve(num_blocks);
  for (uint64_t i = 0; i < num_blocks; i++) m_heights.push_back(i);
}

rapidjson::Value PyMoneroGetBlocksByHeightRequest::to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const {
  rapidjson::Value root(rapidjson::kObjectType);
  if (!m_heights.empty()) root.AddMember("heights", monero_utils::to_rapidjson_val(allocator, m_heights), allocator);
  return root;
}

std::string PyMoneroBinaryRequest::to_binary_val() const {
  auto json_val = serialize();
  std::string binary_val;
  monero_utils::json_to_binary(json_val, binary_val);
  return binary_val;
}

std::string PyMoneroRequestParams::serialize() const {
  if (m_py_params == boost::none) return PySerializableStruct::serialize();
  auto node = PyGenUtils::pyobject_to_ptree(m_py_params.get());
  return monero_utils::serialize(node);
}

boost::optional<py::object> PyMoneroJsonResponse::get_result() const {
  boost::optional<py::object> res;
  if (m_result != boost::none) res = PyGenUtils::ptree_to_pyobject(m_result.get());
  return res;
}

std::shared_ptr<PyMoneroJsonResponse> PyMoneroJsonResponse::deserialize(const std::string& response_json) {
  // parse json to property node
  boost::property_tree::ptree node = json_to_property_node(response_json);
  auto response = std::make_shared<PyMoneroJsonResponse>();

  for (boost::property_tree::ptree::const_iterator it = node.begin(); it != node.end(); ++it) {
    std::string key = it->first;
    if (key == std::string("error")) {
      std::string err_message = "Unknown error";
      int err_code = -1;
      for (auto it_err = it->second.begin(); it_err != it->second.end(); ++it_err) {
        std::string key_err = it_err->first;
        if (key_err == std::string("message")) {
          err_message = it_err->second.data();
        }
        else if (key_err == std::string("code")) {
          err_code = it_err->second.get_value<int>();
        }
      }

      throw PyMoneroRpcError(err_code, err_message);
    }
    else if (key == std::string("jsonrpc")) {
      response->m_jsonrpc = it->second.data();
    }
    else if (key == std::string("id")) {
      response->m_id = it->second.data();
    }
    else if (key == std::string("result")) {
      response->m_result = it->second;
    }
    else std::cout << std::string("WARNING MoneroJsonResponse::deserialize() unrecognized key: ") << key << std::endl;
  }

  return response;
}

boost::optional<py::object> PyMoneroPathResponse::get_response() const {
  boost::optional<py::object> res;
  if (m_response != boost::none) res = PyGenUtils::ptree_to_pyobject(m_response.get());
  return res;
}

std::shared_ptr<PyMoneroPathResponse> PyMoneroPathResponse::deserialize(const std::string& response_json) {
  // parse json to property node
  auto response = std::make_shared<PyMoneroPathResponse>();
  response->m_response = json_to_property_node(response_json);
  return response;
}

std::shared_ptr<PyMoneroBinaryResponse> PyMoneroBinaryResponse::deserialize(const std::string& response_binary) {
  auto response = std::make_shared<PyMoneroBinaryResponse>();
  response->m_binary = response_binary;
  return response;
}

boost::optional<py::object> PyMoneroBinaryResponse::get_response() const {
  boost::optional<py::object> res;
  if (m_response != boost::none) res = PyGenUtils::ptree_to_pyobject(m_response.get());
  return res;
}

rapidjson::Value PyMoneroPathRequest::to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const {
  if (m_params != boost::none) return m_params.get()->to_rapidjson_val(allocator);
  throw std::runtime_error("No params provided");
}

rapidjson::Value PyMoneroJsonRequest::to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const {
  // create root
  rapidjson::Value root(rapidjson::kObjectType);

  // set string values
  rapidjson::Value value_str(rapidjson::kStringType);

  if (m_version != boost::none) monero_utils::add_json_member("version", m_version.get(), allocator, root, value_str);
  if (m_id != boost::none) monero_utils::add_json_member("id", m_id.get(), allocator, root, value_str);
  if (m_method != boost::none) monero_utils::add_json_member("method", m_method.get(), allocator, root, value_str);
  if (m_params != boost::none) root.AddMember("params", m_params.get()->to_rapidjson_val(allocator), allocator);

  return root;
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

bool PyMoneroConnectionPriorityComparator::compare(int p1, int p2) {
  if (p1 == p2) return false;
  // 0 alway first
  if (p1 == 0) return true;
  if (p2 == 0) return false;
  return p1 > p2;
}

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
    return !PyMoneroConnectionPriorityComparator::compare(c1->m_priority, c2->m_priority);
  } else {
    if (c1->m_is_online != boost::none && c1->m_is_online.get()) return true;
    else if (c2->m_is_online != boost::none && c2->m_is_online.get()) return false;
    else if (c1->m_is_online == boost::none) return true;
    // c1 is offline
    return false;
  }
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
      throw PyMoneroError("password cannot be empty because username is not empty");
    }

    if (username_empty) {
      throw PyMoneroError("username cannot be empty because password is not empty");
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
    PyMoneroGetBlocksByHeightRequest request(100);
    send_binary_request(request);
    m_is_online = true;
    m_is_authenticated = true;
  }
  catch (const PyMoneroRpcError& ex) {
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

void PyMoneroConnectionManager::add_listener(const std::shared_ptr<monero_connection_manager_listener> &listener) {
  boost::lock_guard<boost::recursive_mutex> lock(m_listeners_mutex);
  m_listeners.push_back(listener);
}

PyMoneroConnectionManager::~PyMoneroConnectionManager() {
  MTRACE("~PyMoneroConnectionManager()");
  reset();
}

void PyMoneroConnectionManager::remove_listener(const std::shared_ptr<monero_connection_manager_listener> &listener) {
  boost::lock_guard<boost::recursive_mutex> lock(m_listeners_mutex);
  // find and remove listener
  m_listeners.erase(std::remove_if(m_listeners.begin(), m_listeners.end(), [&listener](std::shared_ptr<monero_connection_manager_listener> iter){ return iter == listener; }), m_listeners.end());
}

void PyMoneroConnectionManager::remove_listeners() {
  // remove all listeners
  boost::lock_guard<boost::recursive_mutex> lock(m_listeners_mutex);
  m_listeners.clear();
}

std::vector<std::shared_ptr<monero_connection_manager_listener>> PyMoneroConnectionManager::get_listeners() const {
  return m_listeners;
}

std::vector<std::shared_ptr<PyMoneroRpcConnection>> PyMoneroConnectionManager::get_connections() const {
  boost::lock_guard<boost::recursive_mutex> lock(m_connections_mutex);
  // sort connections by priority
  std::vector<std::shared_ptr<PyMoneroRpcConnection>> sorted_connections(m_connections);
  std::sort(sorted_connections.begin(), sorted_connections.end(), [this](const std::shared_ptr<PyMoneroRpcConnection>& c1, const std::shared_ptr<PyMoneroRpcConnection>& c2) {
    return PyMoneroRpcConnection::before(c1, c2, m_current_connection);
  });
  return sorted_connections;
}

std::shared_ptr<PyMoneroRpcConnection> PyMoneroConnectionManager::get_connection_by_uri(const std::string &uri) {
  boost::lock_guard<boost::recursive_mutex> lock(m_connections_mutex);
  for(const auto &m_connection : m_connections) {
    if (m_connection->m_uri == uri) return m_connection;
  }

  // connection not found
  return nullptr;
}

void PyMoneroConnectionManager::add_connection(const std::shared_ptr<PyMoneroRpcConnection>& connection) {
  if (connection->m_uri == boost::none) throw std::runtime_error("Invalid connection uri");
  boost::lock_guard<boost::recursive_mutex> lock(m_connections_mutex);
  // check for duplicates
  for(const auto &m_connection : m_connections) {
    if (m_connection->m_uri == connection->m_uri) throw std::runtime_error("Connection URI already exists with connection manager: " + connection->m_uri.get());
  }

  // add connection
  m_connections.push_back(connection);
}

void PyMoneroConnectionManager::add_connection(const std::string &uri) {
  // add new connection by uri
  std::shared_ptr<PyMoneroRpcConnection> connection = std::make_shared<PyMoneroRpcConnection>();
  connection->m_uri = uri;
  add_connection(connection);
}

void PyMoneroConnectionManager::remove_connection(const std::string &uri) {
  boost::lock_guard<boost::recursive_mutex> lock(m_connections_mutex);

  std::shared_ptr<PyMoneroRpcConnection> connection = get_connection_by_uri(uri);
  if (connection == nullptr) throw std::runtime_error("Connection not found");

  // remove connection
  m_connections.erase(std::remove_if(m_connections.begin(), m_connections.end(), [&connection](std::shared_ptr<PyMoneroRpcConnection> iter){ return iter == connection; }), m_connections.end());

  if (connection == m_current_connection) {
    // remove also from current connection
    m_current_connection = nullptr;
    on_connection_changed(m_current_connection);
  }
}

void PyMoneroConnectionManager::set_connection(const std::shared_ptr<PyMoneroRpcConnection>& connection) {
  if (connection == m_current_connection) return;

  // check if setting null connection
  if (connection == nullptr) {
    m_current_connection = nullptr;
    on_connection_changed(nullptr);
    return;
  }

  // must provide uri
  if (connection->m_uri == boost::none || connection->m_uri->empty()) throw std::runtime_error("Connection is missing URI");

  // add or replace connection
  boost::lock_guard<boost::recursive_mutex> lock(m_connections_mutex);

  // remove previuous connection
  auto prev_connection = get_connection_by_uri(connection->m_uri.get());
  if (prev_connection != nullptr) m_connections.erase(std::remove_if(m_connections.begin(), m_connections.end(), [&prev_connection](std::shared_ptr<PyMoneroRpcConnection> iter){ return iter == prev_connection; }), m_connections.end());

  // set connection and notify changes
  add_connection(connection);
  m_current_connection = connection;
  on_connection_changed(connection);
}

void PyMoneroConnectionManager::set_connection(const std::string& uri) {
  if (uri.empty()) {
    // remove current connection
    set_connection(std::shared_ptr<PyMoneroRpcConnection>(nullptr));
    return;
  }

  // check if connection already exists
  auto found = get_connection_by_uri(uri);

  if (found != nullptr) {
    // set already found connection
    set_connection(found);
  }
  else {
    // create new connection
    auto connection = std::make_shared<PyMoneroRpcConnection>();
    connection->m_uri = uri;
    set_connection(connection);
  }
}

bool PyMoneroConnectionManager::has_connection(const std::string& uri) {
  auto connection = get_connection_by_uri(uri);
  return connection != nullptr;
}

boost::optional<bool> PyMoneroConnectionManager::is_connected() const {
  if (m_current_connection == nullptr) return false;
  return m_current_connection->is_connected();
}

void PyMoneroConnectionManager::check_connection() {
  bool connection_changed = false;
  std::shared_ptr<PyMoneroRpcConnection> connection = get_connection();
  if (connection != nullptr) {
    // check current connection
    if (connection->check_connection(m_timeout.load())) connection_changed = true;
    std::vector<std::shared_ptr<PyMoneroRpcConnection>> cons;
    cons.push_back(connection);
    process_responses(cons);
  }

  if (m_auto_switch && !is_connected().value_or(false)) {
    // switch to best available connection
    std::shared_ptr<PyMoneroRpcConnection> best_connection = get_best_available_connection(connection);
    if (best_connection != nullptr) {
      set_connection(best_connection);
      return;
    }
  }

  // notify changes
  if (connection_changed) on_connection_changed(connection);
}

void PyMoneroConnectionManager::set_auto_switch(bool auto_switch) {
  m_auto_switch = auto_switch;
}

void PyMoneroConnectionManager::stop_polling() {
  set_is_polling(false);
}

void PyMoneroConnectionManager::start_polling(const boost::optional<uint64_t>& period_ms, const boost::optional<bool>& auto_switch, const boost::optional<uint64_t>& timeout_ms, const boost::optional<PyMoneroConnectionPollType>& poll_type, const boost::optional<std::vector<std::shared_ptr<PyMoneroRpcConnection>>> &excluded_connections) {
  // stop polling
  stop_polling();

  // apply defaults
  uint64_t poll_period_ms = period_ms == boost::none ? DEFAULT_POLL_PERIOD : period_ms.get();
  set_period_in_ms(poll_period_ms);
  if (auto_switch != boost::none) set_auto_switch(auto_switch.get());
  if (timeout_ms != boost::none) set_timeout(timeout_ms.get());
  m_excluded_connections.clear();

  // set poll type
  m_poll_type = poll_type == boost::none ? PyMoneroConnectionPollType::PRIORITIZED : poll_type.get();
  if (excluded_connections != boost::none) {
    m_excluded_connections.insert(excluded_connections.get().begin(), excluded_connections.get().end());
  }

  // start polling
  set_is_polling(true);
}

std::shared_ptr<PyMoneroRpcConnection> PyMoneroConnectionManager::get_best_available_connection(const std::set<std::shared_ptr<PyMoneroRpcConnection>>& excluded_connections) {
  // try connections within each ascending priority
  auto cons = get_connections_in_ascending_priority();

  for (const auto& prioritized_connections : cons) {
    try {
      // check connections in parallel
      boost::asio::thread_pool pool(4);

      boost::mutex mtx;
      boost::condition_variable cv;
      std::queue<std::shared_ptr<PyMoneroRpcConnection>> completed;
      std::atomic<int> remaining{0};

      for (const auto& connection : prioritized_connections) {
        if (!connection) throw std::runtime_error("connection is nullptr");
        if (excluded_connections.count(connection)) continue;

        remaining++;

        boost::asio::post(pool, [&, connection]() {
          connection->check_connection(m_timeout.load());

          {
            boost::lock_guard<boost::mutex> lock(mtx);
            completed.push(connection);
          }
          cv.notify_one();
        });
      }

      // get connection by completion order
      while (remaining > 0) {
        boost::unique_lock<boost::mutex> lock(mtx);

        cv.wait(lock, [&]() { return !completed.empty(); });

        auto connection = completed.front();
        completed.pop();
        remaining--;

        lock.unlock();

        // use first available connection
        if (connection->is_connected().value_or(false)) {
          pool.join();
          return connection;
        }
      }

      pool.join();

    } catch (const std::exception& e) {
      throw PyMoneroError(std::string("Connection check error: ") + e.what());
    }
  }

  return nullptr;
}

std::shared_ptr<PyMoneroRpcConnection> PyMoneroConnectionManager::get_best_available_connection(const std::shared_ptr<PyMoneroRpcConnection>& excluded_connection) {
  const std::set<std::shared_ptr<PyMoneroRpcConnection>>& excluded_connections = { excluded_connection };
  return get_best_available_connection(excluded_connections);
}

void PyMoneroConnectionManager::check_connections() {
  check_connections(get_connections());
}

void PyMoneroConnectionManager::disconnect() {
  set_connection(std::shared_ptr<PyMoneroRpcConnection>(nullptr));
}

void PyMoneroConnectionManager::clear() {
  // clear connections
  m_connections.clear();
  m_excluded_connections.clear();

  if (m_current_connection != nullptr) {
    // clear current connection
    m_current_connection = nullptr;
    on_connection_changed(m_current_connection);
  }
}

void PyMoneroConnectionManager::reset() {
  remove_listeners();
  stop_polling();
  clear();
  m_timeout = DEFAULT_TIMEOUT;
  m_auto_switch = DEFAULT_AUTO_SWITCH;
}

void PyMoneroConnectionManager::on_connection_changed(const std::shared_ptr<PyMoneroRpcConnection>& connection) {
  boost::lock_guard<boost::recursive_mutex> lock(m_listeners_mutex);
  // notify connection change to listeners
  for (const auto &listener : m_listeners) {
    listener->on_connection_changed(connection);
  }
}

std::vector<std::vector<std::shared_ptr<PyMoneroRpcConnection>>> PyMoneroConnectionManager::get_connections_in_ascending_priority() {
  boost::lock_guard<boost::recursive_mutex> lock(m_connections_mutex);

  // build connection priorities map
  std::map<int, std::vector<std::shared_ptr<PyMoneroRpcConnection>>> connection_priorities;
  for (const auto& connection : m_connections) {
    int priority = connection->m_priority;
    connection_priorities[priority].push_back(connection);
  }

  // build prioritized connections vector
  std::vector<std::vector<std::shared_ptr<PyMoneroRpcConnection>>> prioritized_connections;
  for (auto& [priority, group] : connection_priorities) {
    prioritized_connections.push_back(group);
  }

  if (!prioritized_connections.empty() && connection_priorities.count(0)) {
    auto it = std::find_if(prioritized_connections.begin(), prioritized_connections.end(), [](const auto& group) {
      return !group.empty() && group[0]->m_priority == 0;
    });

    if (it != prioritized_connections.end()) {
      // move priority 0 to end
      auto zero_priority_group = *it;
      prioritized_connections.erase(it);
      prioritized_connections.push_back(zero_priority_group);
    }
  }

  return prioritized_connections;
}

void PyMoneroConnectionManager::poll() {
  // do polling
  switch (m_poll_type) {
    case PyMoneroConnectionPollType::CURRENT:
      check_connection();
      break;
    case PyMoneroConnectionPollType::ALL:
      check_connections();
      break;
    case PyMoneroConnectionPollType::UNDEFINED:
    case PyMoneroConnectionPollType::PRIORITIZED:
      check_prioritized_connections();
      break;
  }
}

bool PyMoneroConnectionManager::check_connections(const std::vector<std::shared_ptr<PyMoneroRpcConnection>>& connections, const std::set<std::shared_ptr<PyMoneroRpcConnection>>& excluded_connections) {
  boost::lock_guard<boost::recursive_mutex> connections_lock(m_connections_mutex);
  try {
    // start checking connections in parallel
    boost::asio::thread_pool pool(4);
    boost::mutex result_mutex;
    boost::condition_variable result_cv;
    std::vector<std::shared_ptr<PyMoneroRpcConnection>> completed;

    // submit tasks
    int num_tasks = 0;
    for (const auto& connection : connections) {
      if (excluded_connections.count(connection)) continue;

      num_tasks++;

      boost::asio::post(pool, [this, connection, &result_mutex, &result_cv, &completed]() {
        bool change = connection->check_connection(m_timeout.load());

        if (change && connection == get_connection()) {
          on_connection_changed(connection);
        }

        {
          boost::lock_guard<boost::mutex> lock(result_mutex);
          completed.push_back(connection);
        }

        result_cv.notify_one();
      });
    }

    bool has_connection = false;
    size_t received = 0;

    // wait for responses
    while (received < num_tasks) {
      boost::unique_lock<boost::mutex> lock(result_mutex);
      result_cv.wait(lock, [&]() { return completed.size() > received; });

      auto connection = completed[received++];
      lock.unlock();

      if (connection->is_connected().value_or(false) && !has_connection) {
        has_connection = true;
        if (!is_connected().value_or(false) && m_auto_switch) set_connection(connection);
      }
    }

    pool.join();

    // process responses
    process_responses(connections);

    return has_connection;
  }
  catch (const std::exception& e) {
    throw PyMoneroError(std::string("check_connections failed: ") + e.what());
  }
}

void PyMoneroConnectionManager::check_prioritized_connections() {
  // check connections in ascending priority
  for (const auto &prioritized_connections : get_connections_in_ascending_priority()) {
    check_connections(prioritized_connections, m_excluded_connections);
  }
}

std::shared_ptr<PyMoneroRpcConnection> PyMoneroConnectionManager::process_responses(const std::vector<std::shared_ptr<PyMoneroRpcConnection>>& responses) {
  // add new connections
  for (const auto& conn : responses) {
    if (m_response_times.find(conn) == m_response_times.end()) {
      m_response_times[conn] = {};
    }
  }

  // insert response times or null
  for (auto& [conn, times] : m_response_times) {
    if (std::find(responses.begin(), responses.end(), conn) != responses.end()) {
      times.insert(times.begin(), conn->m_response_time);
    } else {
      times.insert(times.begin(), boost::none);
    }

    if (times.size() > MIN_BETTER_RESPONSES) {
      // remove old response times
      times.pop_back();
    }
  }

  // update best connection based on responses and priority
  return update_best_connection_in_priority();
}

std::shared_ptr<PyMoneroRpcConnection> PyMoneroConnectionManager::get_best_connection_from_prioritized_responses(const std::vector<std::shared_ptr<PyMoneroRpcConnection>>& responses) {
  // get best response
  std::shared_ptr<PyMoneroRpcConnection> best_response = nullptr;
  for (const auto& conn : responses) {
    if (conn->is_connected().value_or(false)) {
      if (!best_response || conn->m_response_time < best_response->m_response_time) {
        best_response = conn;
      }
    }
  }

  // no update if no responses
  if (!best_response) return nullptr;

  // use best response if disconnected
  auto best_connection = get_connection();
  if (!best_connection || !best_connection->is_connected().value_or(false)) {
    return best_response;
  }

  // use best response if different priority (assumes being called in descending priority)
  if (best_response->m_priority != best_connection->m_priority) {
    return best_response;
  }

  // keep best connection if not enough data
  if (m_response_times.find(best_connection) == m_response_times.end()) {
    return best_connection;
  }

  // check if a connection is consistently better
  for (const auto& conn : responses) {
    if (conn == best_connection) continue;

    auto it_best = m_response_times.find(best_connection);
    auto it_curr = m_response_times.find(conn);

    if (it_curr == m_response_times.end() || it_curr->second.size() < MIN_BETTER_RESPONSES) continue;

    bool better = true;
    for (int i = 0; i < MIN_BETTER_RESPONSES; i++) {
      auto curr_time = it_curr->second[i];
      auto best_time = it_best->second[i];
      if (curr_time == boost::none || best_time == boost::none || curr_time.get() > best_time.get()) {
        better = false;
        break;
      }
    }

    if (better) best_connection = conn;
  }

  return best_connection;
}

std::shared_ptr<PyMoneroRpcConnection> PyMoneroConnectionManager::update_best_connection_in_priority() {
  if (!m_auto_switch) return nullptr;

  for (const auto& prioritized_connections : get_connections_in_ascending_priority()) {
    // get best connection and update current
    auto best_conn = get_best_connection_from_prioritized_responses(prioritized_connections);
    if (best_conn != nullptr) {
      set_connection(best_conn);
      return best_conn;
    }
  }

  // no connection updated
  return nullptr;
}
