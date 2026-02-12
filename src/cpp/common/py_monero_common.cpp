#include "py_monero_common.h"
#include "utils/monero_utils.h"

int PyMoneroConnectionPriorityComparator::compare(int p1, int p2) {
  if (p1 == p2) return 0;
  if (p1 == 0) return -1;
  if (p2 == 0) return 1;
  return p2 - p1;
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
  // deserialize json to property node
  std::istringstream iss = response_json.empty() ? std::istringstream() : std::istringstream(response_json);
  boost::property_tree::ptree node;
  boost::property_tree::read_json(iss, node);

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
  // deserialize json to property node
  std::istringstream iss = response_json.empty() ? std::istringstream() : std::istringstream(response_json);
  boost::property_tree::ptree node;
  boost::property_tree::read_json(iss, node);
  auto response = std::make_shared<PyMoneroPathResponse>();
  response->m_response = node;
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
  rapidjson::Value root(rapidjson::kObjectType); 
  rapidjson::Value value_str(rapidjson::kStringType);

  if (m_version != boost::none) monero_utils::add_json_member("version", m_version.get(), allocator, root, value_str);
  if (m_id != boost::none) monero_utils::add_json_member("id", m_id.get(), allocator, root, value_str);
  if (m_method != boost::none) monero_utils::add_json_member("method", m_method.get(), allocator, root, value_str);
  if (m_params != boost::none) root.AddMember("params", m_params.get()->to_rapidjson_val(allocator), allocator);

  return root;
}

int PyMoneroRpcConnection::compare(std::shared_ptr<PyMoneroRpcConnection> c1, std::shared_ptr<PyMoneroRpcConnection> c2, std::shared_ptr<PyMoneroRpcConnection> current_connection) {
  // current connection is first
  if (c1 == current_connection) return -1;
  if (c2 == current_connection) return 1;
  
  // order by availability then priority then by name
  if (c1->is_online() == c2->is_online()) {
    if (c1->m_priority == c2->m_priority) {
      if (c1->m_uri == c2->m_uri) return 1;
      else return -1;
    }
    return PyMoneroConnectionPriorityComparator::compare(c1->m_priority, c2->m_priority) * -1; // order by priority in descending order
  } else {
    if (c1->is_online()) return -1;
    else if (c2->is_online()) return 1;
    // TODO manage never connected
    //else if (!c1->is_online()) return -1;
    //else return 1; // c1 is offline
    return -1;
  }
}

bool PyMoneroRpcConnection::is_onion() const {
  if (m_uri == boost::none) return false;
  if (m_uri && m_uri->size() >= 6 && m_uri->compare(m_uri->size() - 6, 6, ".onion") == 0) {
    return true;
  }
  return false;
}

bool PyMoneroRpcConnection::is_i2p() const {
  if (m_uri == boost::none) return false;
  if (m_uri && m_uri->size() >= 8 && m_uri->compare(m_uri->size() - 8, 8, ".b32.i2p") == 0) {
    return true;
  }
  return false;
}

void PyMoneroRpcConnection::set_credentials(const std::string& username, const std::string& password) {
  if (m_http_client != nullptr) {
    if (m_http_client->is_connected()) {
      m_http_client->disconnect();
    }
  }
  else {
    auto factory = new net::http::client_factory();
    m_http_client = factory->create();
  }

  if (username.empty()) {
    m_username = boost::none;
  }

  if (password.empty()) {
    m_password = boost::none;
  }

  if (!password.empty() || !username.empty()) {
    if (password.empty()) {
      throw PyMoneroError("username cannot be empty because password is not empty");
    }

    if (username.empty()) {
      throw PyMoneroError("password cannot be empty because username is not empty");
    }
  }

  if (m_username != username || m_password != password) {
    m_is_online = boost::none;
    m_is_authenticated = boost::none;
  }

  m_username = username;
  m_password = password;
}

void PyMoneroRpcConnection::set_attribute(const std::string& key, const std::string& val) {
  m_attributes[key] = val;
}

std::string PyMoneroRpcConnection::get_attribute(const std::string& key) {
  std::unordered_map<std::string, std::string>::const_iterator i = m_attributes.find(key);
  if (i == m_attributes.end())
    return std::string("");
  return i->second;
}

bool PyMoneroRpcConnection::is_online() const {
  return m_is_online.value_or(false);
}

bool PyMoneroRpcConnection::is_authenticated() const {
  return m_is_authenticated.value_or(false);
}

bool PyMoneroRpcConnection::is_connected() const {
  if (!is_online()) return false;
  if (m_is_authenticated != boost::none) {
    return is_authenticated();
  }
  return true;
}

bool PyMoneroRpcConnection::check_connection(int timeout_ms) {
  boost::optional<bool> is_online_before = m_is_online;
  boost::optional<bool> is_authenticated_before = m_is_authenticated;
  boost::lock_guard<boost::recursive_mutex> lock(m_mutex);
  try {
    if (!m_http_client) throw std::runtime_error("http client not set");
    if (m_http_client->is_connected()) {
      m_http_client->disconnect();
    }

    if (m_proxy_uri != boost::none) {
      if(!m_http_client->set_proxy(m_proxy_uri.get())) {
        throw std::runtime_error("Could not set proxy");
      }
    }

    if(m_username != boost::none && !m_username->empty() && m_password != boost::none && !m_password->empty()) {
      auto credentials = std::make_shared<epee::net_utils::http::login>();

      credentials->username = *m_username;
      credentials->password = *m_password;
  
      m_credentials = *credentials;
    }
    
    if (!m_http_client->set_server(m_uri.get(), m_credentials)) {
      throw std::runtime_error("Could not set rpc connection: " + m_uri.get());
    }

    m_http_client->connect(std::chrono::milliseconds(timeout_ms));
    auto start = std::chrono::high_resolution_clock::now();
    PyMoneroJsonRequest request("get_version");
    auto response = send_json_request(request);
    auto end = std::chrono::high_resolution_clock::now();
    auto duration = std::chrono::duration_cast<std::chrono::milliseconds>(end - start);
    if (response->m_result == boost::none) {
      throw PyMoneroRpcError(-1, "Invalid JSON RPC response");
    }

    m_is_online = true;
    m_is_authenticated = true;
    m_response_time = duration.count();

    return is_online_before != m_is_online || is_authenticated_before != m_is_authenticated;
  }
  catch (const PyMoneroRpcError& ex) {
    m_is_online = false;
    m_is_authenticated = boost::none;
    m_response_time = boost::none;

    if (ex.code == 401) {
      m_is_online = true;
      m_is_authenticated = false;
    }
    else if (ex.code == 404) {
      m_is_online = true;
      m_is_authenticated = true;
    }

    return false;
  }
  catch (const std::exception& ex) {
    m_is_online = false;
    m_is_authenticated = boost::none;
    m_response_time = boost::none;
    return false;
  }
}

void PyMoneroConnectionManager::add_listener(const std::shared_ptr<monero_connection_manager_listener> &listener) {
  boost::lock_guard<boost::recursive_mutex> lock(m_listeners_mutex);
  m_listeners.push_back(listener);
}

void PyMoneroConnectionManager::remove_listener(const std::shared_ptr<monero_connection_manager_listener> &listener) {
  boost::lock_guard<boost::recursive_mutex> lock(m_listeners_mutex);
  m_listeners.erase(std::remove_if(m_listeners.begin(), m_listeners.end(), [&listener](std::shared_ptr<monero_connection_manager_listener> iter){ return iter == listener; }), m_listeners.end());
}

void PyMoneroConnectionManager::remove_listeners() {
  boost::lock_guard<boost::recursive_mutex> lock(m_listeners_mutex);
  m_listeners.clear();
}

std::vector<std::shared_ptr<monero_connection_manager_listener>> PyMoneroConnectionManager::get_listeners() const {
  return m_listeners;
}

std::shared_ptr<PyMoneroRpcConnection> PyMoneroConnectionManager::get_connection_by_uri(const std::string &uri) {
  boost::lock_guard<boost::recursive_mutex> lock(m_connections_mutex);
  for(const auto &m_connection : m_connections) {
    if (m_connection->m_uri == uri) return m_connection;
  }

  return nullptr;
}

void PyMoneroConnectionManager::add_connection(std::shared_ptr<PyMoneroRpcConnection> connection) {
  if (connection->m_uri == boost::none) throw std::runtime_error("Invalid connection uri");
  boost::lock_guard<boost::recursive_mutex> lock(m_connections_mutex);
  for(const auto &m_connection : m_connections) {
    if (m_connection->m_uri == connection->m_uri) throw std::runtime_error("Connection URI already exists with connection manager: " + connection->m_uri.get());
  }

  m_connections.push_back(connection);
}

void PyMoneroConnectionManager::add_connection(const std::string &uri) {
  std::shared_ptr<PyMoneroRpcConnection> connection = std::make_shared<PyMoneroRpcConnection>();
  connection->m_uri = uri;
  add_connection(connection);
}

void PyMoneroConnectionManager::remove_connection(const std::string &uri) {
  boost::lock_guard<boost::recursive_mutex> lock(m_connections_mutex);

  std::shared_ptr<PyMoneroRpcConnection> connection = get_connection_by_uri(uri);

  if (connection == nullptr) throw std::runtime_error("Connection not found");
  
  m_connections.erase(std::remove_if(m_connections.begin(), m_connections.end(), [&connection](std::shared_ptr<PyMoneroRpcConnection> iter){ return iter == connection; }), m_connections.end());

  if (connection == m_current_connection) {
    m_current_connection = nullptr;
    on_connection_changed(m_current_connection);
  }
}

void PyMoneroConnectionManager::set_connection(std::shared_ptr<PyMoneroRpcConnection> connection) {
  if (connection == m_current_connection) return;

  if (connection == nullptr) {
    m_current_connection = nullptr;
    on_connection_changed(nullptr);
    return;
  }

  if (connection->m_uri == boost::none || connection->m_uri->empty()) throw std::runtime_error("Connection is missing URI");

  boost::lock_guard<boost::recursive_mutex> lock(m_connections_mutex);

  auto prev_connection = get_connection_by_uri(connection->m_uri.get());
  if (prev_connection != nullptr) m_connections.erase(std::remove_if(m_connections.begin(), m_connections.end(), [&prev_connection](std::shared_ptr<PyMoneroRpcConnection> iter){ return iter == prev_connection; }), m_connections.end());
  add_connection(connection);
  m_current_connection = connection;
  on_connection_changed(connection);
}

void PyMoneroConnectionManager::set_connection(const std::string& uri) {
  if (uri.empty()) {
    set_connection(std::shared_ptr<PyMoneroRpcConnection>(nullptr));
    return;
  }

  auto found = get_connection_by_uri(uri);

  if (found != nullptr) {
    set_connection(found);
  }
  else {
    auto connection = std::make_shared<PyMoneroRpcConnection>();
    connection->m_uri = uri;
    set_connection(connection);
  }
}

bool PyMoneroConnectionManager::has_connection(const std::string& uri) {
  auto connection = get_connection_by_uri(uri);

  if (connection != nullptr) return true;
  return false;
}

bool PyMoneroConnectionManager::is_connected() const {
  if (m_current_connection == nullptr) return false;
  return m_current_connection->is_connected();
}

void PyMoneroConnectionManager::check_connection() {
  bool connection_changed = false;
  std::shared_ptr<PyMoneroRpcConnection> connection = get_connection();
  if (connection != nullptr) {
    if (connection->check_connection(m_timeout)) connection_changed = true;
    std::vector<std::shared_ptr<PyMoneroRpcConnection>> cons;
    cons.push_back(connection);
    process_responses(cons);
  }
  if (m_auto_switch && !is_connected()) {
    std::shared_ptr<PyMoneroRpcConnection> best_connection = get_best_available_connection(connection);
    if (best_connection != nullptr) {
      set_connection(best_connection);
      return;
    }
  }
  if (connection_changed) on_connection_changed(connection);
}

void PyMoneroConnectionManager::set_auto_switch(bool auto_switch) {
  m_auto_switch = auto_switch;
}

void PyMoneroConnectionManager::stop_polling() {
  if (m_is_polling) {
    m_is_polling = false;
    if (m_thread.joinable()) m_thread.join();
  }
}

void PyMoneroConnectionManager::start_polling(boost::optional<uint64_t> period_ms, boost::optional<bool> auto_switch, boost::optional<uint64_t> timeout_ms, boost::optional<PyMoneroConnectionPollType> poll_type, boost::optional<std::vector<std::shared_ptr<PyMoneroRpcConnection>>> &excluded_connections) {
  // apply defaults
  if (period_ms == boost::none) period_ms = DEFAULT_POLL_PERIOD;
  if (auto_switch != boost::none) set_auto_switch(auto_switch.get());
  if (timeout_ms != boost::none) set_timeout(timeout_ms.get());
  if (poll_type == boost::none) poll_type = PyMoneroConnectionPollType::PRIORITIZED;

  // stop polling
  stop_polling();

  // start polling
  switch (poll_type.get()) {
    case PyMoneroConnectionPollType::CURRENT:
      start_polling_connection(period_ms.get());
      break;
    case PyMoneroConnectionPollType::ALL:
      start_polling_connections(period_ms.get());
      break;
    case PyMoneroConnectionPollType::UNDEFINED:
    case PyMoneroConnectionPollType::PRIORITIZED:
      start_polling_prioritized_connections(period_ms.get(), excluded_connections);
      break;
  }
}

std::shared_ptr<PyMoneroRpcConnection> PyMoneroConnectionManager::get_best_available_connection(const std::set<std::shared_ptr<PyMoneroRpcConnection>>& excluded_connections) {
  auto cons = get_connections_in_ascending_priority();
  for (const auto& prioritizedConnections : cons) {
    try {
      std::vector<std::thread*> futures;
      for (const auto& connection : prioritizedConnections) {
        if (!connection) throw std::runtime_error("connection is nullptr");
        if (excluded_connections.count(connection)) continue;
        std::thread thread = std::thread([this, connection]() {
          connection->check_connection(m_timeout);
        });
        thread.detach();
        futures.push_back(&thread);
      }

      for (auto& fut : futures) {
        if (fut->joinable()) fut->join();
      }

      std::shared_ptr<PyMoneroRpcConnection> best_connection = nullptr;

      for (const auto& conn : prioritizedConnections) {
        try {
          if (!conn) throw std::runtime_error("connection is nullptr");
          if (conn->is_connected()) {
            if (best_connection == nullptr || best_connection->m_response_time == boost::none || best_connection->m_response_time < conn->m_response_time) best_connection = conn;
          }
        } catch (...) {
          std::cout << "MoneroRpcConnection::get_best_available_connection(): error" << std::endl;
        }
      }

      if (best_connection != nullptr) return best_connection;
    } catch (const std::exception& e) {
      throw std::runtime_error(std::string("Connection check error: ") + e.what());
    }
  }

  return std::shared_ptr<PyMoneroRpcConnection>(nullptr);
}

std::shared_ptr<PyMoneroRpcConnection> PyMoneroConnectionManager::get_best_available_connection(std::shared_ptr<PyMoneroRpcConnection>& excluded_connection) {
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
  boost::lock_guard<boost::recursive_mutex> lock(m_connections_mutex);

  m_connections.clear();

  if (m_current_connection != nullptr) {
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

void PyMoneroConnectionManager::on_connection_changed(std::shared_ptr<PyMoneroRpcConnection> connection) {
  boost::lock_guard<boost::recursive_mutex> lock(m_listeners_mutex);

  for (const auto &listener : m_listeners) {
    listener->on_connection_changed(connection);
  }
}

std::vector<std::vector<std::shared_ptr<PyMoneroRpcConnection>>> PyMoneroConnectionManager::get_connections_in_ascending_priority() {
  boost::lock_guard<boost::recursive_mutex> lock(m_connections_mutex);

  std::map<int, std::vector<std::shared_ptr<PyMoneroRpcConnection>>> connection_priorities;

  for (const auto& connection : m_connections) {
    int priority = connection->m_priority;
    connection_priorities[priority].push_back(connection);
  }

  std::vector<std::vector<std::shared_ptr<PyMoneroRpcConnection>>> prioritized_connections;

  for (auto& [priority, group] : connection_priorities) {
    prioritized_connections.push_back(group);
  }

  if (!prioritized_connections.empty() && connection_priorities.count(0)) {
    auto it = std::find_if(prioritized_connections.begin(), prioritized_connections.end(),
                            [](const auto& group) {
                              return !group.empty() && group[0]->m_priority == 0;
                            });

    if (it != prioritized_connections.end()) {
      auto zero_priority_group = *it;
      prioritized_connections.erase(it);
      prioritized_connections.push_back(zero_priority_group);
    }
  }

  return prioritized_connections;
}

void PyMoneroConnectionManager::start_polling_connection(uint64_t period_ms) {
  m_is_polling = true;

  m_thread = std::thread([this, period_ms]() {
    while (m_is_polling) {
      try {
        check_connection();
      } catch (const std::exception& e) {
        std::cout << "ERROR " << e.what() << std::endl;
      }

      std::this_thread::sleep_for(std::chrono::milliseconds(period_ms));
    }
  });
  m_thread.detach();
}

void PyMoneroConnectionManager::start_polling_connections(uint64_t period_ms) {
  m_is_polling = true;

  m_thread = std::thread([this, period_ms]() {
    while (m_is_polling) {
      try {
        check_connections();
      } catch (const std::exception& e) {
        std::cout << "ERROR " << e.what() << std::endl;
      }

      std::this_thread::sleep_for(std::chrono::milliseconds(period_ms));
    }
  });
  m_thread.detach();
}

void PyMoneroConnectionManager::start_polling_prioritized_connections(uint64_t period_ms, boost::optional<std::vector<std::shared_ptr<PyMoneroRpcConnection>>> excluded_connections) {
  m_is_polling = true;
  m_thread = std::thread([this, period_ms, &excluded_connections]() {
    while (m_is_polling) {
      try {
        check_prioritized_connections(excluded_connections);
      } catch (const std::exception& e) {
        std::cout << "ERROR " << e.what() << std::endl;
      }

      std::this_thread::sleep_for(std::chrono::milliseconds(period_ms));
    }
  });
  m_thread.detach();
}

bool PyMoneroConnectionManager::check_connections(const std::vector<std::shared_ptr<PyMoneroRpcConnection>>& connections, const std::set<std::shared_ptr<PyMoneroRpcConnection>>& excluded_connections) {
  boost::lock_guard<boost::recursive_mutex> lock(m_connections_mutex);
  try {
    auto timeout_ms = m_timeout;

    bool has_connection = false;

    for (const auto& connection : connections) {
      if (excluded_connections.count(connection)) continue;

      bool changed = connection->check_connection(timeout_ms);
      if (changed && connection == get_connection()) {
        on_connection_changed(connection);
      }
      if (connection->is_connected() && !has_connection) {
        has_connection = true;
        if (!is_connected() && m_auto_switch) {
          set_connection(connection);
        }
      }
    }

    process_responses(connections);
    return has_connection;
  } 
  catch (const std::exception& e) {
    throw std::runtime_error(std::string("check_connections failed: ") + e.what());
  }
}

void PyMoneroConnectionManager::check_prioritized_connections(boost::optional<std::vector<std::shared_ptr<PyMoneroRpcConnection>>> excluded_connections) {
  for (const auto &prioritized_connections : get_connections_in_ascending_priority()) {
    if (excluded_connections != boost::none) {
      std::set<std::shared_ptr<PyMoneroRpcConnection>> ex(excluded_connections.get().begin(), excluded_connections.get().end());
      check_connections(prioritized_connections, ex);
    }
    else { check_connections(prioritized_connections, {}); }
  }
}

std::shared_ptr<PyMoneroRpcConnection> PyMoneroConnectionManager::process_responses(const std::vector<std::shared_ptr<PyMoneroRpcConnection>>& responses) {
  for (const auto& conn : responses) {
    if (m_response_times.find(conn) == m_response_times.end()) {
      m_response_times[conn] = {};
    }
  }

  for (auto& [conn, times] : m_response_times) {
    if (std::find(responses.begin(), responses.end(), conn) != responses.end()) {
      times.insert(times.begin(), conn->m_response_time);
    } else {
      times.insert(times.begin(), boost::none);
    }

    if (times.size() > MIN_BETTER_RESPONSES) {
      times.pop_back();
    }
  }

  return update_best_connection_in_priority();
}

std::shared_ptr<PyMoneroRpcConnection> PyMoneroConnectionManager::get_best_connection_from_prioritized_responses(const std::vector<std::shared_ptr<PyMoneroRpcConnection>>& responses) {
  std::shared_ptr<PyMoneroRpcConnection> best_response = std::shared_ptr<PyMoneroRpcConnection>(nullptr);

  for (const auto& conn : responses) {
    if (conn->is_connected()) {
      if (!best_response || conn->m_response_time < best_response->m_response_time) {
        best_response = conn;
      }
    }
  }

  if (!best_response) return std::shared_ptr<PyMoneroRpcConnection>(nullptr);

  auto best_connection = get_connection();
  if (!best_connection || !best_connection->is_connected()) {
    return best_response;
  }

  if (PyMoneroConnectionPriorityComparator::compare(best_response->m_priority, best_connection->m_priority) != 0) {
    return best_response;
  }

  if (m_response_times.find(best_connection) == m_response_times.end()) {
    return best_connection;
  }

  for (const auto& conn : responses) {
    if (conn == best_connection) continue;

    auto it_best = m_response_times.find(best_connection);
    auto it_curr = m_response_times.find(conn);
    if (it_curr == m_response_times.end()) continue;
    if (it_curr->second.size() < MIN_BETTER_RESPONSES || it_best->second.size() < MIN_BETTER_RESPONSES) continue;

    bool consistently_better = true;
    for (int i = 0; i < MIN_BETTER_RESPONSES; ++i) {
      auto curr_time = it_curr->second[i];
      auto best_time = it_best->second[i];
      if (curr_time == boost::none || best_time == boost::none || curr_time.get() > best_time.get()) {
        consistently_better = false;
        break;
      }
    }

    if (consistently_better) {
      best_connection = conn;
    }
  }

  return best_connection;
}

std::shared_ptr<PyMoneroRpcConnection> PyMoneroConnectionManager::update_best_connection_in_priority() {
  if (!m_auto_switch) return std::shared_ptr<PyMoneroRpcConnection>(nullptr);

  for (const auto& prioritized_connections : get_connections_in_ascending_priority()) {
    auto best_conn = get_best_connection_from_prioritized_responses(prioritized_connections);
    if (best_conn != nullptr) {
      set_connection(best_conn);
      return best_conn;
    }
  }

  return std::shared_ptr<PyMoneroRpcConnection>(nullptr);
}
