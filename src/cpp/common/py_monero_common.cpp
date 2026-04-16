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
      // TODO: in emscripten, m_poll_cv.notify_one() returns without waiting, so sleep; bug in emscripten upstream llvm?
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
