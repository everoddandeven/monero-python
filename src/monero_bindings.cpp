#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <string>
#include <regex>
#include <set>
#include <future>
#include <chrono>
#include <algorithm>
#include <memory>

#include "../external/monero-cpp/src/utils/monero_utils.h"
#include "../external/monero-cpp/src/daemon/monero_daemon_model.h"
#include "../external/monero-cpp/src/wallet/monero_wallet_model.h"
#include "../external/monero-cpp/src/wallet/monero_wallet_full.h"
#include "../external/monero-cpp/src/wallet/monero_wallet_keys.h"

namespace py = pybind11;

enum PyMoneroAddressType : uint8_t {
  PRIMARY_ADDRESS = 0,
  INTEGRATED_ADDRESS,
  SUBADDRESS
};

enum PyMoneroConnectionType : uint8_t {
  INVALID = 0,
  IPV4,
  IPV6,
  TOR,
  I2P
};

enum PyMoneroKeyImageSpentStatus : uint8_t {
  NOT_SPENT = 0,
  CONFIRMED,
  TX_POOL
};

enum PyMoneroConnectionPoolType : uint8_t {
  PRIORITIZED = 0,
  CURRENT,
  ALL,
  UNDEFINED
};

class PySerializableStruct : public serializable_struct {
public:
  using serializable_struct::serializable_struct;

  rapidjson::Value to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const override { throw std::runtime_error("not implemented"); };

};

class PyDeserializableStruct {
public:
  PyDeserializableStruct() { }

  virtual PyDeserializableStruct deserialize(const std::string str_json);
};

class PyEmptyRequest : public PySerializableStruct {
public:
  PyEmptyRequest() {}

  rapidjson::Value to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const override { rapidjson::Value root(rapidjson::kObjectType); return root; };

};

class PyMoneroJsonRequest : public PySerializableStruct {
public:
  PyMoneroJsonRequest(std::string method) {
    m_version = "2.0";
    m_id = "0";
    m_method = method;
    m_params = PyEmptyRequest();
  }

  PyMoneroJsonRequest(std::string method, PySerializableStruct& params) {
    m_version = "2.0";
    m_id = "0";
    m_method = method;
    m_params = params;
  }

  rapidjson::Value to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const override { 
    rapidjson::Value root(rapidjson::kObjectType); 
    rapidjson::Value value_str(rapidjson::kStringType);

    if (m_version != boost::none) monero_utils::add_json_member("version", m_version.get(), allocator, root, value_str);
    if (m_id != boost::none) monero_utils::add_json_member("id", m_id.get(), allocator, root, value_str);
    if (m_method != boost::none) monero_utils::add_json_member("method", m_method.get(), allocator, root, value_str);
    if (m_params != boost::none) root.AddMember("params", m_params.get().to_rapidjson_val(allocator), allocator);

    return root; 
  };

  boost::optional<std::string> m_version;
  boost::optional<std::string> m_id;
  boost::optional<std::string> m_method;
  boost::optional<PySerializableStruct> m_params;
};

class PyMoneroGetBlockParams : public PySerializableStruct {
public:
  boost::optional<uint64_t> m_height;
  boost::optional<std::string> m_hash;
  boost::optional<bool> m_fill_pow_hash;

  PyMoneroGetBlockParams(uint64_t height, bool fill_pow_hash = false) {
    m_height = height;
    m_fill_pow_hash = fill_pow_hash;
  }

  PyMoneroGetBlockParams(std::string hash, bool fill_pow_hash = false) {
    m_hash = hash;
    m_fill_pow_hash = fill_pow_hash;
  }

  rapidjson::Value to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const override { 
    rapidjson::Value root(rapidjson::kObjectType); 
    rapidjson::Value value_str(rapidjson::kStringType);
    rapidjson::Value value_num(rapidjson::kNumberType);
  
    if (m_hash != boost::none) monero_utils::add_json_member("hash", m_hash.get(), allocator, root, value_str);
    if (m_height != boost::none) monero_utils::add_json_member("height", m_height.get(), allocator, root, value_num);
    if (m_fill_pow_hash != boost::none) monero_utils::add_json_member("fill_pow_hash", m_fill_pow_hash.get(), allocator, root);

    return root; 
  }
};

class PyMoneroJsonResponse {
public:
  boost::optional<std::string> m_jsonrpc;
  boost::optional<std::string> m_id;
  boost::optional<boost::property_tree::ptree> m_result;

  static std::shared_ptr<PyMoneroJsonResponse> deserialize(const std::string& response_json) {
    // deserialize json to property node
    std::istringstream iss = response_json.empty() ? std::istringstream() : std::istringstream(response_json);
    boost::property_tree::ptree node;
    boost::property_tree::read_json(iss, node);

    auto response = std::make_shared<PyMoneroJsonResponse>();

    for (boost::property_tree::ptree::const_iterator it = node.begin(); it != node.end(); ++it) {
      std::string key = it->first;
      if (key == std::string("jsonrpc")) {
        response->m_jsonrpc = it->second.data();
      }
      else if (key == std::string("id")) {
        response->m_id = it->second.data();
      }
      else if (key == std::string("result")) {
        response->m_result = it->second;   
      }
      else MWARNING("WARNING MoneroJsonResponse::deserialize() unrecognized key: " << key);
    }

    return response;
  }
};

class PyMoneroConnectionPriorityComparator {
public:
  
  static int compare(int p1, int p2) {
    if (p1 == p2) return 0;
    if (p1 == 0) return -1;
    if (p2 == 0) return 1;
    return p2 - p1;
  }
};

class PyMoneroRpcConnection : public monero_rpc_connection {
public:
  boost::optional<std::string> m_zmq_uri;
  boost::optional<std::string> m_proxy;
  int m_priority;
  uint64_t m_timeout;
  boost::optional<long> m_response_time;

  static int compare(std::shared_ptr<PyMoneroRpcConnection> c1, std::shared_ptr<PyMoneroRpcConnection> c2, std::shared_ptr<PyMoneroRpcConnection> current_connection) {
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
      else if (!c1->is_online()) return -1;
      else return 1; // c1 is offline
    }
  }

  PyMoneroRpcConnection(const std::string& uri = "", const std::string& username = "", const std::string& password = "", const std::string& zmq_uri = "", int priority = 0, uint64_t timeout = 0) {
    m_uri = uri;
    m_username = username; 
    m_password = password;
    m_zmq_uri = zmq_uri;
    m_priority = priority;
    m_timeout = timeout;
  }

  PyMoneroRpcConnection(PyMoneroRpcConnection& rpc) {
    m_uri = rpc.m_uri;
    m_username = rpc.m_username;
    m_password = rpc.m_password;
    m_zmq_uri = rpc.m_zmq_uri;
    m_priority = rpc.m_priority;
    m_timeout = rpc.m_timeout;
  }

  PyMoneroRpcConnection(monero::monero_rpc_connection& rpc) {
    m_uri = rpc.m_uri;
    m_username = rpc.m_username;
    m_password = rpc.m_password;
    m_zmq_uri = "";
    m_priority = 0;
    m_timeout = 500;
  }

  bool is_onion() const {
    if (m_uri == boost::none) return false;

    if (m_uri && m_uri->size() >= 6 && m_uri->compare(m_uri->size() - 6, 6, ".onion") == 0) {
      return true;
    }

    return false;
  }

  bool is_i2p() const {
    if (m_uri == boost::none) return false;

    if (m_uri && m_uri->size() >= 8 && m_uri->compare(m_uri->size() - 8, 8, ".b32.i2p") == 0) {
      return true;
    }

    return false;
  }

  void set_credentials(const std::string& username, const std::string& password) {
    m_username = username;
    m_password = password;
  }

  void set_attribute(const std::string& key, const std::string& val) {
    m_attributes[key] = val;
  }

  std::string get_attribute(const std::string& key) {
    std::unordered_map<std::string, std::string>::const_iterator i = m_attributes.find(key);
    if (i == m_attributes.end())
      return std::string("");
    return i->second;
  }

  bool is_online() const {
    return m_is_online.value_or(false);
  }

  bool is_authenticated() const {
    return m_is_authenticated.value_or(false);
  }

  bool is_connected() const {
    if (!is_online()) return false;

    if (m_is_authenticated != boost::none) {
      return is_authenticated();
    }

    return true;
  }

  bool check_connection(int timeout_ms = 2000) {
    bool is_online_before = is_online();
    bool is_authenticated_before = is_authenticated();

    try {
      auto response = invoke_post("/get_version", "{}", std::chrono::milliseconds(timeout_ms));

      if (response->m_response_code != 200) {
        throw std::runtime_error("Request error");
      }

      m_is_online = true;
      m_is_authenticated = true;

      return is_online_before != is_online() || is_authenticated_before != is_authenticated();
    }
    catch (...) {
      m_is_online = false;
      m_is_authenticated = boost::none;
      return false;
    }
  }

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

    if (!m_http_client->invoke_post(uri, body, timeout, &response)) {
    throw std::runtime_error("Network error");
    }

    return response;
  }

  inline const std::shared_ptr<PyMoneroJsonResponse> send_json_request(const PyMoneroJsonRequest request, std::chrono::milliseconds timeout = std::chrono::seconds(15)) {
    PyMoneroJsonResponse response;

    int result = invoke_post("/json_rpc", request, response, timeout);

    if (result != 200) throw std::runtime_error("Network error");

    return std::make_shared<PyMoneroJsonResponse>(response);
  }

protected:
  mutable boost::recursive_mutex m_mutex;
  std::string m_server;
  boost::optional<epee::net_utils::http::login> m_credentials;
  std::unique_ptr<epee::net_utils::http::abstract_http_client> m_http_client;
  serializable_unordered_map<std::string, std::string> m_attributes;
  boost::optional<bool> m_is_online;
  boost::optional<bool> m_is_authenticated;
};

class PyMoneroConnectionManagerListener {
public:
  void on_connection_changed(std::shared_ptr<PyMoneroRpcConnection> connection) {
    throw std::runtime_error("not implemented");
  }
};

class PyMoneroConnectionManager {
public:
  void add_listener(std::shared_ptr<PyMoneroConnectionManagerListener> &listener) {
    boost::lock_guard<boost::recursive_mutex> lock(m_listeners_mutex);
    m_listeners.push_back(listener);
  }

  void remove_listener(std::shared_ptr<PyMoneroConnectionManagerListener> &listener) {
    boost::lock_guard<boost::recursive_mutex> lock(m_listeners_mutex);
    m_listeners.erase(std::remove_if(m_listeners.begin(), m_listeners.end(), [&listener](std::shared_ptr<PyMoneroConnectionManagerListener> iter){ return iter == listener; }), m_listeners.end());
  }

  void remove_listeners() {
    boost::lock_guard<boost::recursive_mutex> lock(m_listeners_mutex);
    m_listeners.clear();
  }

  std::vector<std::shared_ptr<PyMoneroConnectionManagerListener>> get_listeners() {
    return m_listeners;
  }

  std::shared_ptr<PyMoneroRpcConnection> get_connection_by_uri(const std::string &uri) {
    boost::lock_guard<boost::recursive_mutex> lock(m_connections_mutex);
    for(const auto &m_connection : m_connections) {
      if (m_connection->m_uri == uri) return m_connection;
    }

    return nullptr;
  }

  void add_connection(std::shared_ptr<PyMoneroRpcConnection> connection) {
    if (connection->m_uri == boost::none) throw std::runtime_error("Invalid connection uri");
    boost::lock_guard<boost::recursive_mutex> lock(m_connections_mutex);
    for(const auto &m_connection : m_connections) {
      if (m_connection->m_uri == connection->m_uri) throw std::runtime_error("Connection URI already exists with connection manager: " + connection->m_uri.get());
    }

    m_connections.push_back(connection);
  }

  void add_connection(const std::string &uri) {
    std::shared_ptr<PyMoneroRpcConnection> connection = std::make_shared<PyMoneroRpcConnection>();
    connection->m_uri = uri;
    add_connection(connection);
  }

  void remove_connection(const std::string &uri) {
    boost::lock_guard<boost::recursive_mutex> lock(m_connections_mutex);

    std::shared_ptr<PyMoneroRpcConnection> connection = get_connection_by_uri(uri);

    if (connection == nullptr) throw std::runtime_error("Connection not found");
    
    m_connections.erase(std::remove_if(m_connections.begin(), m_connections.end(), [&connection](std::shared_ptr<PyMoneroRpcConnection> iter){ return iter == connection; }), m_connections.end());

    if (connection == m_current_connection) {
      m_current_connection = nullptr;
      on_connection_changed(m_current_connection);
    }
  }

  void set_connection(std::shared_ptr<PyMoneroRpcConnection> connection) {
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

  void set_connection(const std::string& uri) {
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

  std::shared_ptr<PyMoneroRpcConnection> get_connection() { return m_current_connection; }

  bool has_connection(const std::string& uri) {
    auto connection = get_connection_by_uri(uri);

    if (connection != nullptr) return true;
    return false;
  }

  std::vector<std::shared_ptr<PyMoneroRpcConnection>> get_connections() { return m_connections; }

  bool is_connected() {
    if (m_current_connection == nullptr) return false;
    return m_current_connection->is_connected();
  }

  void check_connection() {
    bool connection_changed = false;
    std::shared_ptr<PyMoneroRpcConnection> connection = get_connection();
    if (connection != nullptr) {
      if (connection->check_connection(m_timeout)) connection_changed = true;
      std::vector<std::shared_ptr<PyMoneroRpcConnection>> cons;
      cons.push_back(connection);
      process_responses(cons);
    }
    if (m_autoswitch && !is_connected()) {
      std::shared_ptr<PyMoneroRpcConnection> best_connection = get_best_available_connection(connection);
      if (best_connection != nullptr) {
        set_connection(best_connection);
        return;
      }
    }
    if (connection_changed) on_connection_changed(connection);
  }

  void set_autoswitch(bool autoswitch) {
    m_autoswitch = autoswitch;
  }

  void stop_polling() {
    throw std::runtime_error("not implemented");
  }

  void start_polling(uint64_t period_ms = 20000) {
    throw std::runtime_error("not implemented");
  }

  void start_polling(uint64_t period_ms, bool autoswitch, uint64_t timeout_ms, PyMoneroConnectionPoolType poll_type, std::vector<std::shared_ptr<PyMoneroRpcConnection>> excluded_connections) {
    throw std::runtime_error("not implemented");
  }

  void start_polling(uint64_t period_ms, bool autoswitch, uint64_t timeout_ms, PyMoneroConnectionPoolType poll_type) {
    std::vector<std::shared_ptr<PyMoneroRpcConnection>> excluded_connections;
    start_polling(period_ms, autoswitch, timeout_ms, poll_type, excluded_connections);
  }

  void start_polling(uint64_t period_ms, bool autoswitch, uint64_t timeout_ms) {
    std::vector<std::shared_ptr<PyMoneroRpcConnection>> excluded_connections;
    start_polling(period_ms, autoswitch, timeout_ms, PyMoneroConnectionPoolType::UNDEFINED, excluded_connections);
  }

  void start_polling(uint64_t period_ms, bool autoswitch) {
    throw std::runtime_error("not implemented");
  }

  void start_polling(uint64_t period_ms, PyMoneroConnectionPoolType poll_type) {
    throw std::runtime_error("not implemented");
  }

  bool get_autoswitch() { return m_autoswitch; }

  void set_timeout(uint64_t timeout_ms) { m_timeout = timeout_ms; }

  uint64_t get_timeout() { return m_timeout; }

  std::vector<std::shared_ptr<PyMoneroRpcConnection>> get_peer_connections() { throw std::runtime_error("not implemented"); }

  void disconnect() { set_connection(std::shared_ptr<PyMoneroRpcConnection>(nullptr)); }

  void clear() {
    boost::lock_guard<boost::recursive_mutex> lock(m_connections_mutex);

    m_connections.clear();

    if (m_current_connection != nullptr) {
      m_current_connection = nullptr;
      on_connection_changed(m_current_connection);
    }
  }

  void reset() {
    remove_listeners();
    // stop_pooling();
    clear();
    m_timeout = DEFAULT_TIMEOUT;
    m_autoswitch = DEFAULT_AUTO_SWITCH;
  }

  std::shared_ptr<PyMoneroRpcConnection> get_best_available_connection(const std::set<std::shared_ptr<PyMoneroRpcConnection>>& excludedConnections = {}) {
    int m_timeout = 2000;

    for (const auto& prioritizedConnections : get_connections_in_ascending_priority()) {
      try {
        std::vector<std::future<std::shared_ptr<PyMoneroRpcConnection>>> futures;

        for (const auto& connection : prioritizedConnections) {
          if (excludedConnections.count(connection)) continue;

          futures.push_back(std::async(std::launch::async, [connection, m_timeout]() {
            connection->check_connection(m_timeout);
            return connection;
          }));
        }

        for (auto& fut : futures) {
          try {
            auto conn = fut.get();
            if (conn->is_connected()) return conn;
          } catch (...) {
            
          }
        }

      } catch (const std::exception& e) {
        throw std::runtime_error(std::string("Connection check error: ") + e.what());
      }
    }

    return std::shared_ptr<PyMoneroRpcConnection>(nullptr);
  }

  std::shared_ptr<PyMoneroRpcConnection> get_best_available_connection(std::shared_ptr<PyMoneroRpcConnection>& excluded_connection) {
    const std::set<std::shared_ptr<PyMoneroRpcConnection>>& excluded_connections = { excluded_connection };
  
    return get_best_available_connection(excluded_connections);
  }

  void check_connections() {
    check_connections(get_connections());
  }

private:
  // static variables
  static const uint64_t DEFAULT_TIMEOUT = 5000;
  static const uint64_t DEFAULT_POLL_PERIOD = 20000;
  static const bool DEFAULT_AUTO_SWITCH = true;
  static const int MIN_BETTER_RESPONSES = 3;
  mutable boost::recursive_mutex m_listeners_mutex;
  mutable boost::recursive_mutex m_connections_mutex;
  std::vector<std::shared_ptr<PyMoneroConnectionManagerListener>> m_listeners;
  std::vector<std::shared_ptr<PyMoneroRpcConnection>> m_connections;
  std::shared_ptr<PyMoneroRpcConnection> m_current_connection;
  bool m_autoswitch = true;
  uint64_t m_timeout;
  std::map<std::shared_ptr<PyMoneroRpcConnection>, std::vector<boost::optional<long>>> m_response_times;

  void on_connection_changed(std::shared_ptr<PyMoneroRpcConnection> connection) {
    boost::lock_guard<boost::recursive_mutex> lock(m_listeners_mutex);

    for (const auto &listener : m_listeners) {
      listener->on_connection_changed(connection);
    }
  }

  std::vector<std::vector<std::shared_ptr<PyMoneroRpcConnection>>> get_connections_in_ascending_priority() {
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

  bool check_connections(const std::vector<std::shared_ptr<PyMoneroRpcConnection>>& connections, const std::set<std::shared_ptr<PyMoneroRpcConnection>>& excluded_connections = {}) {
    boost::lock_guard<boost::recursive_mutex> lock(m_connections_mutex);
    try {
      int timeout_ms = 2000; // puoi impostarlo da membro o parametro
      std::vector<std::future<std::shared_ptr<PyMoneroRpcConnection>>> futures;
  
      for (const auto& connection : connections) {
        if (excluded_connections.count(connection)) continue;
  
        futures.push_back(std::async(std::launch::async, [this, connection, timeout_ms]() {
          bool changed = connection->check_connection(timeout_ms);
          if (changed && connection == get_connection()) {
            on_connection_changed(connection);
          }
          return connection;
        }));
      }
  
      bool has_connection = false;
  
      for (auto& fut : futures) {
        try {
          auto connection = fut.get();
          if (connection->is_connected() && !has_connection) {
            has_connection = true;
            if (!is_connected() && m_autoswitch) {
              set_connection(connection);
            }
          }
        } catch (...) { }
      }
  
      process_responses(connections);
      return has_connection;
  
    } catch (const std::exception& e) {
      throw std::runtime_error(std::string("check_connections failed: ") + e.what());
    }
  }
  
  std::shared_ptr<PyMoneroRpcConnection> process_responses(const std::vector<std::shared_ptr<PyMoneroRpcConnection>>& responses) {
    // Aggiungi nuove connessioni a response_times
    for (const auto& conn : responses) {
      if (m_response_times.find(conn) == m_response_times.end()) {
        m_response_times[conn] = {};
      }
    }
  
    // Inserisci tempi di risposta o null
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

  std::shared_ptr<PyMoneroRpcConnection> get_best_connection_from_prioritized_responses(const std::vector<std::shared_ptr<PyMoneroRpcConnection>>& responses) {
    std::shared_ptr<PyMoneroRpcConnection> best_response = std::shared_ptr<PyMoneroRpcConnection>(nullptr);

    for (const auto& conn : responses) {
      if (conn->is_connected()) {
        if (!best_response || conn->m_response_time < best_response->m_response_time) {
          best_response = conn;
        }
      }
    }

    if (!best_response) return std::shared_ptr<PyMoneroRpcConnection>(nullptr);

    // Se la connessione attuale non esiste o è disconnessa, usa la nuova
    auto best_connection = get_connection();
    if (!best_connection || !best_connection->is_connected()) {
      return best_response;
    }

    // Confronta priorità: se sono diverse, usa la nuova
    if (PyMoneroConnectionPriorityComparator::compare(best_response->m_priority, best_connection->m_priority) != 0) {
      return best_response;
    }

    // Se non abbiamo dati per la connessione attuale, mantienila
    if (m_response_times.find(best_connection) == m_response_times.end()) {
      return best_connection;
    }

    // Controlla se un'altra connessione ha prestazioni consistentemente migliori
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
        if (!curr_time.has_value() || !best_time.has_value() || curr_time.value() > best_time.value()) {
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

  std::shared_ptr<PyMoneroRpcConnection> update_best_connection_in_priority() {
    if (!m_autoswitch) return std::shared_ptr<PyMoneroRpcConnection>(nullptr);
  
    for (const auto& prioritized_connections : get_connections_in_ascending_priority()) {
      auto best_conn = get_best_connection_from_prioritized_responses(prioritized_connections);
      if (best_conn != nullptr) {
        set_connection(best_conn);
        return best_conn;
      }
    }
  
    return std::shared_ptr<PyMoneroRpcConnection>(nullptr);
  }

};

class PyMoneroDecodedAddress {
public:
  PyMoneroDecodedAddress(std::string& address, PyMoneroAddressType address_type, monero::monero_network_type network_type) {
    m_address = address;
    m_address_type = address_type;
    m_network_type = network_type;
  }

  std::string m_address;
  PyMoneroAddressType m_address_type;
  monero::monero_network_type m_network_type;
};

class PyMoneroAccountTag {
public:
  PyMoneroAccountTag(std::string& tag, std::string& label) {
    m_tag = tag;
    m_label = label;
  }

  PyMoneroAccountTag(std::string& tag, std::string& label, std::vector<uint32_t> account_indices) {
    m_tag = tag;
    m_label = label;
    m_account_indices = account_indices;
  }

  std::string m_tag;
  std::string m_label;
  std::vector<uint32_t> m_account_indices;
};

class PyMoneroAltChain {
public:
  std::vector<std::string> m_block_hashes;
  boost::optional<uint64_t> m_difficulty;
  boost::optional<uint64_t> m_height;
  boost::optional<uint64_t> m_length;
  boost::optional<std::string> m_main_chain_parent_block_hash;

  static void from_property_tree(const boost::property_tree::ptree& node, const std::shared_ptr<PyMoneroAltChain>& alt_chain) {
    for (boost::property_tree::ptree::const_iterator it = node.begin(); it != node.end(); ++it) {
      std::string key = it->first;
      if (key == std::string("difficulty")) alt_chain->m_difficulty = it->second.get_value<uint64_t>();
      else if (key == std::string("block_hashes")) {
        for (const auto& child : it->second) alt_chain->m_block_hashes.push_back(child.second.data());
      }
      else if (key == std::string("height")) alt_chain->m_height = it->second.get_value<uint64_t>();
      else if (key == std::string("length")) alt_chain->m_length = it->second.get_value<uint64_t>();
      else if (key == std::string("main_chain_parent_block_hash")) alt_chain->m_main_chain_parent_block_hash = it->second.data();

    }
  }
};

class PyMoneroBan {
public:
  boost::optional<std::string> m_host;
  boost::optional<int> m_ip;
  boost::optional<bool> m_is_banned;
  boost::optional<uint64_t> m_seconds;
};

class PyMoneroPruneResult {
public:
  boost::optional<bool> m_is_pruned;
  boost::optional<int> m_pruning_seed;
};

class PyMoneroMiningStatus {
public:
  boost::optional<bool> m_is_active;
  boost::optional<bool> m_is_background;
  boost::optional<std::string> m_address;
  boost::optional<uint64_t> m_speed;
  boost::optional<int> m_num_threads;
};

class PyMoneroMinerTxSum {
public:
  boost::optional<uint64_t> m_emission_sum;
  boost::optional<uint64_t> m_fee_sum;
};

class PyMoneroBlockTemplate {
public:
  boost::optional<std::string> m_block_template_blob;
  boost::optional<std::string> m_block_hashing_blob;
  boost::optional<uint64_t> m_difficulty;
  boost::optional<uint64_t> m_expected_reward;
  boost::optional<uint64_t> m_height;
  boost::optional<std::string> m_prev_hash;
  boost::optional<uint64_t> m_reserved_offset;
  boost::optional<uint64_t> m_seed_height;
  boost::optional<std::string> m_seed_hash;
  boost::optional<std::string> m_next_seed_hash;
};

class PyMoneroConnectionSpan {
public:
  boost::optional<std::string> m_connection_id;
  boost::optional<uint64_t> m_num_blocks;
  boost::optional<std::string> m_remote_address;
  boost::optional<uint64_t> m_rate;
  boost::optional<uint64_t> m_speed;
  boost::optional<uint64_t> m_size;
  boost::optional<uint64_t> m_start_height;
};

class PyMoneroPeer {
public:
  boost::optional<std::string> m_id;
  boost::optional<std::string> m_address;
  boost::optional<std::string> m_host;
  boost::optional<int> m_port;
  boost::optional<bool> m_is_online;
  boost::optional<uint64_t> m_last_seen_timestamp;
  boost::optional<int> m_pruning_seed;
  boost::optional<int> m_rpc_port;
  boost::optional<uint64_t> m_rpc_credits_per_hash;
  boost::optional<std::string> m_hash;
  boost::optional<uint64_t> m_avg_download;
  boost::optional<uint64_t> m_avg_upload;
  boost::optional<uint64_t> m_current_download;
  boost::optional<uint64_t> m_current_upload;
  boost::optional<uint64_t> m_height;
  boost::optional<bool> m_is_incoming;
  boost::optional<uint64_t> m_live_time;
  boost::optional<bool> m_is_local_ip;
  boost::optional<bool> m_is_local_host;
  boost::optional<int> m_num_receives;
  boost::optional<int> m_num_sends;
  boost::optional<uint64_t> m_receive_idle_time;
  boost::optional<uint64_t> m_send_idle_time;
  boost::optional<std::string> m_state;
  boost::optional<int> m_num_support_flags;
  boost::optional<PyMoneroConnectionType> m_connection_type;
};

class PyMoneroSubmitTxResult {
public:
  boost::optional<bool> m_is_good;
  boost::optional<bool> m_is_relayed;
  boost::optional<bool> m_is_double_spend;
  boost::optional<bool> m_is_fee_too_low;
  boost::optional<bool> m_is_mixin_too_low;
  boost::optional<bool> m_has_invalid_input;
  boost::optional<bool> m_has_invalid_output;
  boost::optional<bool> m_has_too_few_outputs;
  boost::optional<bool> m_is_overspend;
  boost::optional<bool> m_is_too_big;
  boost::optional<bool> m_sanity_check_failed;
  boost::optional<std::string> m_reason;
  boost::optional<uint64_t> m_credits;
  boost::optional<std::string> m_top_block_hash;
  boost::optional<bool> m_is_tx_extra_too_big;
  boost::optional<bool> m_is_nonzero_unlock_time;
};

class PyMoneroTxBacklogEntry {
  // TODO
};

class PyMoneroOutputDistributionEntry {
public:
  boost::optional<uint64_t> m_amount;
  boost::optional<int> m_base;
  std::vector<int> m_distribution;
  boost::optional<uint64_t> m_start_height;
};

class PyMoneroOutputHistogramEntry {
public:
  boost::optional<uint64_t> m_amount;
  boost::optional<uint64_t> m_num_instances;
  boost::optional<uint64_t> m_unlocked_instances;
  boost::optional<uint64_t> m_recent_instances;
};

class PyMoneroTxPoolStats {
public:
  boost::optional<int> m_num_txs;
  boost::optional<int> m_num_not_relayed;
  boost::optional<int> m_num_failing;
  boost::optional<int> m_num_double_spends;
  boost::optional<int> m_num10m;
  boost::optional<uint64_t> m_fee_total;
  boost::optional<uint64_t> m_bytes_max;
  boost::optional<uint64_t> m_bytes_med;
  boost::optional<uint64_t> m_bytes_min;
  boost::optional<uint64_t> m_bytes_total;
  //private Map<Long, Integer> histo;
  boost::optional<uint64_t> m_histo98pc;
  boost::optional<uint64_t> m_oldest_timestamp;
};

class PyMoneroDaemonUpdateCheckResult {
public:
  boost::optional<bool> m_is_update_available;
  boost::optional<std::string> m_version;
  boost::optional<std::string> m_hash;
  boost::optional<std::string> m_auto_uri;
  boost::optional<std::string> m_user_uri;
};

class PyMoneroDaemonUpdateDownloadResult : public PyMoneroDaemonUpdateCheckResult {
public:
  boost::optional<std::string> m_download_path;
};

class PyMoneroFeeEstimate {
public:
  boost::optional<uint64_t> m_fee;
  std::vector<uint64_t> m_fees;
  boost::optional<uint64_t> m_quantization_mask;
};

class PyMoneroDaemonInfo {
public:
  boost::optional<std::string> m_version;
  boost::optional<uint64_t> m_num_alt_blocks;
  boost::optional<uint64_t> m_block_size_limit;
  boost::optional<uint64_t> m_block_size_median;
  boost::optional<uint64_t> m_block_weight_limit;
  boost::optional<uint64_t> m_block_weight_median;
  boost::optional<std::string> m_bootstrap_daemon_address;
  boost::optional<uint64_t> m_difficulty;
  boost::optional<uint64_t> m_cumulative_difficulty;
  boost::optional<uint64_t> m_free_space;
  boost::optional<int> m_num_offline_peers;
  boost::optional<int> m_num_online_peers;
  boost::optional<uint64_t> m_height;
  boost::optional<uint64_t> m_height_without_bootstrap;
  boost::optional<monero::monero_network_type> m_network_type;
  boost::optional<bool> m_is_offline;
  boost::optional<int> m_num_incoming_connections;
  boost::optional<int> m_num_outgoing_connections;
  boost::optional<int> m_num_rpc_connections;
  boost::optional<uint64_t> m_start_timestamp;
  boost::optional<uint64_t> m_adjusted_timestamp;
  boost::optional<uint64_t> m_target;
  boost::optional<uint64_t> m_target_height;
  boost::optional<std::string> m_top_block_hash;
  boost::optional<int> m_num_txs;
  boost::optional<int> m_num_txs_pool;
  boost::optional<bool> m_was_bootstrap_ever_used;
  boost::optional<uint64_t> m_database_size;
  boost::optional<bool> m_update_available;
  boost::optional<uint64_t> m_credits;
  boost::optional<bool> m_is_busy_syncing;
  boost::optional<bool> m_is_synchronized;
  boost::optional<bool> m_is_restricted;
};

class PyMoneroDaemonSyncInfo {
public:
  boost::optional<uint64_t> m_height;
  std::vector<PyMoneroPeer> m_peers;
  std::vector<PyMoneroConnectionSpan> m_spans;
  boost::optional<uint64_t> m_target_height;
  boost::optional<int> m_next_needed_pruning_seed;
  boost::optional<std::string> m_overview;
  boost::optional<uint64_t> m_credits;
  boost::optional<std::string> m_top_block_hash;
};

class PyMoneroHardForkInfo {
public:
  boost::optional<uint64_t> m_earliest_height;
  boost::optional<bool> m_is_enabled;
  boost::optional<int> m_state;
  boost::optional<int> m_threshold;
  boost::optional<int> m_version;
  boost::optional<int> m_num_votes;
  boost::optional<int> m_window;
  boost::optional<int> m_voting;
  boost::optional<uint64_t> m_credits;
  boost::optional<std::string> m_top_block_hash;
};

class PyMoneroDaemonListener {
public:
  virtual void on_new_block(const monero::monero_block_header &header) {
    m_last_header = header;
  }

  boost::optional<monero::monero_block_header> m_last_header;
};

class PyMoneroDaemon {

public:
  virtual void add_listener(std::shared_ptr<PyMoneroDaemonListener> listener) { throw std::runtime_error("not implemented"); }
  virtual void remove_listener(std::shared_ptr<PyMoneroDaemonListener> listener) { throw std::runtime_error("not implemented"); }
  virtual std::vector<std::shared_ptr<PyMoneroDaemonListener>> get_listeners() { throw std::runtime_error("not implemented"); }
  virtual monero::monero_version get_version() { throw std::runtime_error("not implemented"); }
  virtual bool is_trusted() { throw std::runtime_error("not implemented"); }
  virtual uint64_t get_height() { throw std::runtime_error("not implemented"); }
  virtual std::string get_block_hash(uint64_t height) { throw std::runtime_error("not implemented"); }
  virtual PyMoneroBlockTemplate& get_block_template(std::string& wallet_address) { throw std::runtime_error("not implemented"); }
  virtual PyMoneroBlockTemplate& get_block_template(std::string& wallet_address, int reserve_size) { throw std::runtime_error("not implemented"); }
  virtual monero::monero_block_header get_last_block_header() { throw std::runtime_error("not implemented"); }
  virtual monero::monero_block_header get_block_header_by_hash(const std::string& hash) { throw std::runtime_error("not implemented"); }
  virtual monero::monero_block_header get_block_header_by_height(uint64_t height) { throw std::runtime_error("not implemented"); }
  virtual std::vector<monero::monero_block_header> get_block_headers_by_range(uint64_t start_height, uint64_t end_height) { throw std::runtime_error("not implemented"); }
  virtual std::shared_ptr<monero::monero_block> get_block_by_hash(const std::string& hash) { throw std::runtime_error("not implemented"); }
  virtual std::vector<std::shared_ptr<monero::monero_block>> get_blocks_by_hash(const std::vector<std::string>& block_hashes, uint64_t start_height, bool prune) { throw std::runtime_error("not implemented"); }
  virtual monero::monero_block get_block_by_height(uint64_t height) { throw std::runtime_error("not implemented"); }
  virtual std::vector<monero::monero_block> get_blocks_by_height(std::vector<uint64_t> heights) { throw std::runtime_error("not implemented"); }
  virtual std::vector<monero::monero_block> get_blocks_by_range(uint64_t start_height, uint64_t end_height) { throw std::runtime_error("not implemented"); }
  virtual std::vector<monero::monero_block> get_blocks_by_range_chunked(uint64_t start_height, uint64_t end_height) { throw std::runtime_error("not implemented"); }
  virtual std::vector<monero::monero_block> get_blocks_by_range_chunked(uint64_t start_height, uint64_t end_height, uint64_t max_chunk_size) { throw std::runtime_error("not implemented"); }
  virtual std::vector<std::string> get_block_hashes(std::vector<std::string> block_hashes, uint64_t start_height) { throw std::runtime_error("not implemented"); }
  virtual monero::monero_tx get_tx(const std::string& tx_hash, bool prune = false) { throw std::runtime_error("not implemented"); }
  virtual std::vector<monero::monero_tx> get_txs(const std::vector<std::string>& tx_hashes, bool prune = false) { throw std::runtime_error("not implemented"); }
  virtual std::string get_tx_hex(const std::string& tx_hash, bool prune = false) { throw std::runtime_error("not implemented"); }
  virtual std::vector<std::string> get_tx_hexes(const std::vector<std::string>& tx_hashes, bool prune = false) { throw std::runtime_error("not implemented"); }
  virtual PyMoneroMinerTxSum& get_miner_tx_sum(uint64_t height, uint64_t num_blocks) { throw std::runtime_error("not implemented"); }
  virtual PyMoneroFeeEstimate& get_fee_estimate(uint64_t grace_blocks = 0) { throw std::runtime_error("not implemented"); }
  virtual PyMoneroSubmitTxResult& submit_tx_hex(std::string& tx_hex, bool do_not_relay = false) { throw std::runtime_error("not implemented"); }
  virtual void relay_tx_by_hash(std::string& tx_hash) { throw std::runtime_error("not implemented"); }
  virtual void relay_txs_by_hash(std::vector<std::string>& tx_hashes) { throw std::runtime_error("not implemented"); }
  virtual std::vector<monero::monero_tx> get_tx_pool() { throw std::runtime_error("not implemented"); }
  virtual std::vector<std::string> get_tx_pool_hashes() { throw std::runtime_error("not implemented"); }
  virtual std::vector<PyMoneroTxBacklogEntry> get_tx_pool_backlog() { throw std::runtime_error("not implemented"); }
  virtual std::vector<PyMoneroTxPoolStats> get_tx_pool_stats() { throw std::runtime_error("not implemented"); }
  virtual void flush_tx_pool() { throw std::runtime_error("not implemented"); }
  virtual void flush_tx_pool(std::vector<std::string> hashes) { throw std::runtime_error("not implemented"); }
  virtual PyMoneroKeyImageSpentStatus get_key_image_spent_status(std::string& key_image) { throw std::runtime_error("not implemented"); }
  virtual std::vector<PyMoneroKeyImageSpentStatus> get_key_image_spent_statuses(std::vector<std::string>& key_images) { throw std::runtime_error("not implemented"); }
  virtual std::vector<monero::monero_output> get_outputs(std::vector<monero::monero_output>& outputs) { throw std::runtime_error("not implemented"); }
  virtual std::vector<PyMoneroOutputHistogramEntry> get_output_histogram(std::vector<uint64_t> amounts, int min_count, int max_count, bool is_unlocked, int recent_cutoff) { throw std::runtime_error("not implemented"); }
  virtual std::vector<PyMoneroOutputDistributionEntry> get_output_distribution(std::vector<uint64_t> amounts) { throw std::runtime_error("not implemented"); }
  virtual std::vector<PyMoneroOutputDistributionEntry> get_output_distribution(std::vector<uint64_t> amounts, bool is_cumulative, uint64_t start_height, uint64_t end_height) { throw std::runtime_error("not implemented"); }
  virtual PyMoneroDaemonInfo& get_info() { throw std::runtime_error("not implemented"); }
  virtual PyMoneroDaemonSyncInfo& get_sync_info() { throw std::runtime_error("not implemented"); }
  virtual PyMoneroHardForkInfo& get_hard_fork_info() { throw std::runtime_error("not implemented"); }
  virtual std::vector<std::shared_ptr<PyMoneroAltChain>> get_alt_chains() { throw std::runtime_error("not implemented"); }
  virtual std::vector<std::string> get_alt_block_hashes() { throw std::runtime_error("not implemented"); }
  virtual int get_download_limit() { throw std::runtime_error("not implemented"); }
  virtual int set_download_limit(int limit) { throw std::runtime_error("not implemented"); }
  virtual int reset_download_limit() { throw std::runtime_error("not implemented"); }
  virtual int get_upload_limit() { throw std::runtime_error("not implemented"); }
  virtual int set_upload_limit(int limit) { throw std::runtime_error("not implemented"); }
  virtual int reset_upload_limit() { throw std::runtime_error("not implemented"); }
  virtual std::vector<PyMoneroPeer> get_peers() { throw std::runtime_error("not implemented"); }
  virtual std::vector<PyMoneroPeer> get_known_peers() { throw std::runtime_error("not implemented"); }
  virtual void set_outgoing_peer_limit(int limit) { throw std::runtime_error("not implemented"); }
  virtual void set_incoming_peer_limit(int limit) { throw std::runtime_error("not implemented"); }
  virtual std::vector<PyMoneroBan> get_peer_bans() { throw std::runtime_error("not implemented"); }
  virtual void set_peer_bans(std::vector<PyMoneroBan> bans) { throw std::runtime_error("not implemented"); }
  virtual void set_peer_ban(const PyMoneroBan& ban) { throw std::runtime_error("not implemented"); }
  virtual void start_mining(std::string address, uint64_t num_threads, bool is_background, bool ignore_battery) { throw std::runtime_error("not implemented"); }
  virtual void stop_mining() { throw std::runtime_error("not implemented"); }
  virtual PyMoneroMiningStatus& get_mining_status() { throw std::runtime_error("not implemented"); }
  virtual void submit_block(const std::string& block_blob) { throw std::runtime_error("not implemented"); }
  virtual void submit_blocks(const std::vector<std::string>& block_blobs) { throw std::runtime_error("not implemented"); }
  virtual PyMoneroPruneResult& prune_blockchain(bool check) { throw std::runtime_error("not implemented"); }
  virtual PyMoneroDaemonUpdateCheckResult& check_for_update() { throw std::runtime_error("not implemented"); }
  virtual PyMoneroDaemonUpdateDownloadResult& download_update() { throw std::runtime_error("not implemented"); }
  virtual PyMoneroDaemonUpdateDownloadResult& download_update(const std::string& path) { throw std::runtime_error("not implemented"); }
  virtual void stop() { throw std::runtime_error("not implemented"); }
  virtual monero::monero_block_header wait_for_next_block_header() { throw std::runtime_error("not implemented"); }

protected:
  std::vector<std::shared_ptr<PyMoneroDaemonListener>> m_listeners;
};

class PyMoneroDaemonRpc : public PyMoneroDaemon {
public:
  PyMoneroDaemonRpc() {
    m_rpc = std::make_shared<PyMoneroRpcConnection>();
  }

  PyMoneroDaemonRpc(std::shared_ptr<PyMoneroRpcConnection> rpc) {
    m_rpc = rpc;
  }

  PyMoneroDaemonRpc(const std::string& uri, const std::string& username = "", const std::string& password = "") {
    m_rpc = std::make_shared<PyMoneroRpcConnection>();
    m_rpc->m_uri = uri;
    m_rpc->set_credentials(username, password);
  }

  std::shared_ptr<PyMoneroRpcConnection> get_rpc_connection() const {
    return m_rpc;
  }

  std::shared_ptr<monero::monero_block> get_block_by_hash(const std::string& hash) override {
    auto result = std::make_shared<monero::monero_block>();

    PyMoneroGetBlockParams params(hash);

    PyMoneroJsonRequest request("/get_block", params);

    auto response = m_rpc->send_json_request(request);
    if (response->m_result == boost::none) throw std::runtime_error("Invalid Monero JSONRPC response");
    auto res = response->m_result.get();

    for (boost::property_tree::ptree::const_iterator it = res.begin(); it != res.end(); ++it) {
      std::string key = it->first;
      
      if (key == std::string("blob")) {
        result->m_hex = it->second.data();
      }
      else if (key == std::string("tx_hashes")) {
        for(const auto &hex : it->second) result->m_tx_hashes.push_back(hex.second.data());
      }
      else if (key == std::string("txs")) {
        for (const auto &tx_node : it->second) {
          auto tx = std::make_shared<monero::monero_tx>();
          monero::monero_tx::from_property_tree(tx_node.second, tx);
          result->m_txs.push_back(tx);
        }
      }
      else if (key == std::string("miner_tx")) {
        auto tx = std::make_shared<monero::monero_tx>();
        monero::monero_tx::from_property_tree(it->second, tx);
        result->m_miner_tx = tx;
      }
    }

    return result;
  }

  std::vector<std::shared_ptr<PyMoneroAltChain>> get_alt_chains() override { 
    std::vector<std::shared_ptr<PyMoneroAltChain>> result;
    
    PyMoneroJsonRequest request("/get_alternative_chains");

    std::shared_ptr<PyMoneroJsonResponse> response = m_rpc->send_json_request(request);

    if (response->m_result == boost::none) throw std::runtime_error("Invalid Monero JSONRPC response");
    auto res = response->m_result.get();

    for (boost::property_tree::ptree::const_iterator it = res.begin(); it != res.end(); ++it) {
      std::string key = it->first;
      
      if (key == std::string("chains")) {
        boost::property_tree::ptree chains = it->second;
        for (boost::property_tree::ptree::const_iterator it2 = chains.begin(); it2 != chains.end(); ++it2) {
          std::shared_ptr<PyMoneroAltChain> alt_chain = std::make_shared<PyMoneroAltChain>();
          PyMoneroAltChain::from_property_tree(it2->second, alt_chain);
          result.push_back(alt_chain);
        }
      }
    }

    return result;
  }


protected:
  std::shared_ptr<PyMoneroRpcConnection> m_rpc;
};

class PyMoneroDaemonPooler {
public:
  PyMoneroDaemonPooler(std::shared_ptr<PyMoneroDaemon> daemon) {
    m_daemon = daemon;
  }

  void setIsPooling(bool is_pooling) {
    if (is_pooling) start_pooling();
    else stop_pooling();
  }

protected:
  std::shared_ptr<PyMoneroDaemon> m_daemon;
  boost::optional<monero::monero_block_header> m_last_header;
  void start_pooling() {}
  void stop_pooling() {}
  void pool() {}
};

class PyMoneroWallet : public monero_wallet {
public:
  using monero_wallet::monero_wallet;

  std::string get_seed() const override {
    PYBIND11_OVERRIDE_PURE(
      std::string,
      monero_wallet,
      get_seed,
    );
  }
};

class PyMoneroWalletRpc : public monero_wallet {
public:

  PyMoneroWalletRpc() {
    m_rpc_connection = std::make_shared<PyMoneroRpcConnection>();
  }

  PyMoneroWalletRpc(std::shared_ptr<PyMoneroRpcConnection> rpc_connection) {
    m_rpc_connection = rpc_connection;
  }

  boost::optional<monero::monero_rpc_connection> get_daemon_connection() const override {
    if (m_rpc_connection == nullptr) return boost::none;
    return boost::optional<monero::monero_rpc_connection>(*m_rpc_connection);
  }


protected:
  std::shared_ptr<PyMoneroRpcConnection> m_rpc_connection;
};

class PyMoneroTransfer : public monero_transfer {
public:
  using monero_transfer::monero_transfer;

  boost::optional<bool> is_incoming() const override {
    PYBIND11_OVERRIDE_PURE(
      boost::optional<bool>,
      monero_transfer,
      is_incoming
    );
  }
};

class PyMoneroUtils {
public:
  static const uint64_t NUM_MNEMONIC_WORDS = 25;
  static const uint64_t XMR_AU_MULTIPLIER = 1000000000000ULL;

  PyMoneroUtils() {};
  static std::string get_version() { return std::string("0.1.0"); };
  static int get_ring_size() { return monero_utils::RING_SIZE; };
  static void set_log_level(int level) { monero_utils::set_log_level(level); };
  static void configure_logging(const std::string& path, bool console) { monero_utils::configure_logging(path, console); };
  static monero_integrated_address get_integrated_address(monero_network_type network_type, const std::string& standard_address, const std::string& payment_id = "") { return monero_utils::get_integrated_address(network_type, standard_address, payment_id); };
  static bool is_valid_address(const std::string& address, monero_network_type network_type) { return monero_utils::is_valid_address(address, network_type); };
  static bool is_valid_public_view_key(const std::string& public_view_key) { return is_hex_64(public_view_key); };
  static bool is_valid_public_spend_key(const std::string& public_spend_key) { return is_hex_64(public_spend_key); };
  static bool is_valid_private_view_key(const std::string& private_view_key) { return monero_utils::is_valid_private_view_key(private_view_key); };
  static bool is_valid_private_spend_key(const std::string& private_spend_key) { return monero_utils::is_valid_private_spend_key(private_spend_key); };
  static bool is_valid_payment_id(const std::string& payment_id) { return payment_id.size() == 16 || payment_id.size() == 64; };
  static bool is_valid_mnemonic(const std::string& mnemonic) {
    try {
      validate_mnemonic(mnemonic);
      return true;
    }
    catch (...) {
      return false;
    }
  };
  static void validate_address(const std::string& address, monero_network_type network_type) { monero_utils::validate_address(address, network_type); };
  static void validate_public_view_key(const std::string& public_view_key) { if(!is_hex_64(public_view_key)) throw std::runtime_error("Invalid public view key"); };
  static void validate_public_spend_key(const std::string& public_spend_key) { if(!is_hex_64(public_spend_key)) throw std::runtime_error("Invalid public view key"); };
  static void validate_private_view_key(const std::string& private_view_key) { monero_utils::validate_private_view_key(private_view_key); };
  static void validate_private_spend_key(const std::string& private_spend_key) { monero_utils::validate_private_spend_key(private_spend_key); };
  static void validate_payment_id(const std::string& payment_id) { if (!is_valid_payment_id(payment_id)) throw std::runtime_error("Invalid payment id"); };
  static void validate_mnemonic(const std::string& mnemonic) {
    if (mnemonic.empty()) throw std::runtime_error("Mnemonic phrase is empty");
    if (mnemonic.size() != NUM_MNEMONIC_WORDS) throw std::runtime_error("Mnemonic phrase words must be 25");
  };
  static std::string json_to_binary(const std::string &json) {
    std::string bin;
    monero_utils::json_to_binary(json, bin);
    return bin;
  };
  static std::string dict_to_binary(const py::dict &dictionary) {
    py::object JSON = py::module_::import("json");
    py::object JSON_DUMPS = JSON.attr("dumps");
  
    py::object result_py = JSON_DUMPS(dictionary);
    std::string json = result_py.cast<std::string>();

    return json_to_binary(json);
  };
  static py::dict binary_to_dict(const std::string& bin) {
    py::object JSON = py::module_::import("json");
    py::object JSON_LOADS = JSON.attr("loads");

    std::string json = binary_to_json(bin);
  
    py::object result_py = JSON_LOADS(json);
    py::dict result = result_py.cast<py::dict>();

    return result;
  };
  static std::string binary_to_json(const std::string &bin) {
    std::string json; 
    monero_utils::binary_to_json(bin, json);
    return json;
  };
  static void binary_blocks_to_json(const std::string &bin, std::string &json) { monero_utils::binary_blocks_to_json(bin, json); };
  static bool is_valid_language(const std::string& language) { return monero_utils::is_valid_language(language); };
  static std::vector<std::shared_ptr<monero_block>> get_blocks_from_txs(std::vector<std::shared_ptr<monero_tx_wallet>> txs) { return monero_utils::get_blocks_from_txs(txs); };
  static std::vector<std::shared_ptr<monero_block>> get_blocks_from_transfers(std::vector<std::shared_ptr<monero_transfer>> transfers) { return monero_utils::get_blocks_from_transfers(transfers); };
  static std::vector<std::shared_ptr<monero_block>> get_blocks_from_outputs(std::vector<std::shared_ptr<monero_output_wallet>> outputs) { return monero_utils::get_blocks_from_outputs(outputs); };
  static std::string get_payment_uri(const monero_tx_config& config) {
    // validate config
    std::vector<std::shared_ptr<monero_destination>> destinations = config.get_normalized_destinations();
    if (destinations.size() != 1) throw std::runtime_error("Cannot make URI from supplied parameters: must provide exactly one destination to send funds");
    if (destinations.at(0)->m_address == boost::none) throw std::runtime_error("Cannot make URI from supplied parameters: must provide destination address");
    if (destinations.at(0)->m_amount == boost::none) throw std::runtime_error("Cannot make URI from supplied parameters: must provide destination amount");
  
    // prepare wallet2 params
    std::string address = destinations.at(0)->m_address.get();
    std::string payment_id = config.m_payment_id == boost::none ? "" : config.m_payment_id.get();
    uint64_t amount = destinations.at(0)->m_amount.get();
    std::string note = config.m_note == boost::none ? "" : config.m_note.get();
    std::string m_recipient_name = config.m_recipient_name == boost::none ? "" : config.m_recipient_name.get();
  
    // make uri
    std::string uri = make_uri(address, payment_id, amount, note, m_recipient_name);
    if (uri.empty()) throw std::runtime_error("Cannot make URI from supplied parameters");
    return uri;
  };
  static uint64_t xmr_to_atomic_units(double amount_xmr) {
    if (amount_xmr < 0) throw std::invalid_argument("amount_xmr cannot be negative");
    return static_cast<uint64_t>(std::round(amount_xmr * XMR_AU_MULTIPLIER));
  };
  static double atomic_units_to_xmr(uint64_t amount_atomic_units) {
    return static_cast<double>(amount_atomic_units) / static_cast<double>(XMR_AU_MULTIPLIER);
  };

private:
  static bool is_hex_64(const std::string& value) { 
    if (value.size() != 64) return false;
    const std::regex hexRegex("^-?[0-9a-fA-F]+$");
    return std::regex_match(value, hexRegex);
  }

  static std::string make_uri(const std::string &address, const std::string &payment_id, uint64_t amount, const std::string &tx_description, const std::string &recipient_name) {
    cryptonote::address_parse_info info;

    if(!get_account_address_from_str(info, cryptonote::MAINNET, address))
    {
      if(!get_account_address_from_str(info, cryptonote::TESTNET, address))
      {
        if(!get_account_address_from_str(info, cryptonote::STAGENET, address))
        {
          throw std::runtime_error(std::string("wrong address: ") + address);
        }            
      }
    }
    
    // we want only one payment id
    if (info.has_payment_id && !payment_id.empty())
    {
      throw std::runtime_error("A single payment id is allowed");
    }
    
    if (!payment_id.empty())
    {
      throw std::runtime_error("Standalone payment id deprecated, use integrated address instead");
    }
    
    std::string uri = "monero:" + address;
    unsigned int n_fields = 0;
    
    if (!payment_id.empty())
    {
      uri += (n_fields++ ? "&" : "?") + std::string("tx_payment_id=") + payment_id;
    }
    
    if (amount > 0)
    {
      // URI encoded amount is in decimal units, not atomic units
      uri += (n_fields++ ? "&" : "?") + std::string("tx_amount=") + cryptonote::print_money(amount);
    }
    
    if (!recipient_name.empty())
    {
      uri += (n_fields++ ? "&" : "?") + std::string("recipient_name=") + epee::net_utils::conver_to_url_format(recipient_name);
    }
    
    if (!tx_description.empty())
    {
      uri += (n_fields++ ? "&" : "?") + std::string("tx_description=") + epee::net_utils::conver_to_url_format(tx_description);
    }
    
    return uri;
    }  

};

#define MONERO_CATCH_AND_RETHROW(expr)           \
  try {                                        \
    return expr;                             \
  } catch (const std::exception& e) {          \
    throw py::value_error(e.what());      \
  }
  
PYBIND11_MODULE(monero, m) {
  m.doc() = "";

  // monero_error
  py::register_exception<std::runtime_error>(m, "MoneroError");

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
  py::enum_<PyMoneroConnectionPoolType>(m, "MoneroConnectionPoolType")
    .value("PRIORITIZED", PyMoneroConnectionPoolType::PRIORITIZED)
    .value("CURRENT", PyMoneroConnectionPoolType::CURRENT)
    .value("ALL", PyMoneroConnectionPoolType::ALL)
    .value("UNDEFINED", PyMoneroConnectionPoolType::UNDEFINED);

  // enum address_type
  py::enum_<PyMoneroAddressType>(m, "MoneroAddressType")
    .value("PRIMARY_ADDRESS", PyMoneroAddressType::PRIMARY_ADDRESS)
    .value("INTEGRATED_ADDRESS", PyMoneroAddressType::INTEGRATED_ADDRESS)
    .value("SUBADDRESS", PyMoneroAddressType::SUBADDRESS);

  py::class_<monero::serializable_struct, PySerializableStruct, std::shared_ptr<monero::serializable_struct>>(m, "SerializableStruct")
    .def(py::init<>())
    .def("serialize", [](monero::serializable_struct& self) {
      MONERO_CATCH_AND_RETHROW(self.serialize());
    });

  py::class_<PyEmptyRequest, PySerializableStruct, std::shared_ptr<PyEmptyRequest>>(m, "MoneroEmptyRequest")
    .def(py::init<>());

  py::class_<PyMoneroJsonRequest, PySerializableStruct, std::shared_ptr<PyMoneroJsonRequest>>(m, "MoneroJsonRequest")
    .def(py::init<std::string&>(), py::arg("method"))
    .def(py::init<std::string&, PySerializableStruct&>(), py::arg("method"), py::arg("params"))
    .def_property("version", 
      [](const PyMoneroJsonRequest& self) { return self.m_version.value_or(""); },
      [](PyMoneroJsonRequest& self, std::string& val) { self.m_version = val; })
    .def_property("id", 
      [](const PyMoneroJsonRequest& self) { return self.m_id.value_or(""); },
      [](PyMoneroJsonRequest& self, std::string& val) { self.m_id = val; })
    .def_property("method", 
      [](const PyMoneroJsonRequest& self) { return self.m_method.value_or(""); },
      [](PyMoneroJsonRequest& self, std::string& val) { self.m_method = val; })
    .def_property("params", 
      [](const PyMoneroJsonRequest& self) { return self.m_params.value_or(PyEmptyRequest()); },
      [](PyMoneroJsonRequest& self, PySerializableStruct& val) { self.m_params = val; }); 

  py::class_<PyMoneroJsonResponse, std::shared_ptr<PyMoneroJsonResponse>>(m, "MoneroJsonResponse")
    .def(py::init<>())
    .def_static("deserialize", [](const std::string& response_json) {
      MONERO_CATCH_AND_RETHROW(PyMoneroJsonResponse::deserialize(response_json));
    }, py::arg("response_json"))
    .def_property("jsonrpc", 
      [](const PyMoneroJsonResponse& self) { return self.m_jsonrpc.value_or(""); },
      [](PyMoneroJsonResponse& self, std::string& val) { self.m_jsonrpc = val; })
    .def_property("id", 
      [](const PyMoneroJsonResponse& self) { return self.m_id.value_or(""); },
      [](PyMoneroJsonResponse& self, std::string& val) { self.m_id = val; });

  py::class_<PyMoneroFeeEstimate, std::shared_ptr<PyMoneroFeeEstimate>>(m, "MoneroFeeEstimate")
    .def(py::init<>())
    .def_property("fee", 
      [](const PyMoneroFeeEstimate& self) { return self.m_fee.value_or(0); },
      [](PyMoneroFeeEstimate& self, uint64_t val) { self.m_fee = val; })
    .def_readwrite("fees", &PyMoneroFeeEstimate::m_fees)
    .def_property("quantization_mask", 
      [](const PyMoneroFeeEstimate& self) { return self.m_quantization_mask.value_or(0); },
      [](PyMoneroFeeEstimate& self, uint64_t val) { self.m_quantization_mask = val; });

  py::class_<PyMoneroTxBacklogEntry, std::shared_ptr<PyMoneroTxBacklogEntry>>(m, "MoneroTxBacklogEntry")
    .def(py::init<>());

  // monero_version
  py::class_<monero::monero_version, monero::serializable_struct, std::shared_ptr<monero::monero_version>>(m, "MoneroVersion")
    .def(py::init<>())
    .def_property("number", 
      [](const monero::monero_version& self) { return self.m_number.value_or(0); },
      [](monero::monero_version& self, uint32_t val) { self.m_number = val; })
    .def_property("is_release", 
      [](const monero::monero_version& self) { return self.m_is_release.value_or(false); },
      [](monero::monero_version& self, bool val) { self.m_is_release = val; });

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
    .def_property("uri", 
      [](const PyMoneroRpcConnection& self) { return self.m_uri.value_or(""); },
      [](PyMoneroRpcConnection& self, std::string val) { self.m_uri = val; })
    .def_property("username", 
      [](const PyMoneroRpcConnection& self) { return self.m_username.value_or(""); },
      [](PyMoneroRpcConnection& self, std::string val) { self.m_username = val; })
    .def_property("password", 
      [](const PyMoneroRpcConnection& self) { return self.m_password.value_or(""); },
      [](PyMoneroRpcConnection& self, std::string val) { self.m_password = val; })
    .def_property("proxy", 
      [](const PyMoneroRpcConnection& self) { return self.m_proxy.value_or(""); },
      [](PyMoneroRpcConnection& self, std::string val) { self.m_proxy = val; })
    .def_property("zmq_uri", 
      [](const PyMoneroRpcConnection& self) { return self.m_zmq_uri.value_or(""); },
      [](PyMoneroRpcConnection& self, std::string val) { self.m_zmq_uri = val; })
    .def_property("priority", 
      [](const PyMoneroRpcConnection& self) { return self.m_priority; },
      [](PyMoneroRpcConnection& self, int val) { self.m_priority = val; })
    .def_property("timeout", 
      [](const PyMoneroRpcConnection& self) { return self.m_timeout; },
      [](PyMoneroRpcConnection& self, uint64_t val) { self.m_timeout = val; })
    .def_property("response_time", 
      [](const PyMoneroRpcConnection& self) { return self.m_response_time.value_or(0); },
      [](PyMoneroRpcConnection& self, long val) { self.m_response_time = val; })
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
    .def("check_connection", [](PyMoneroRpcConnection& self) {
      MONERO_CATCH_AND_RETHROW(self.check_connection());
    })
    .def("send_json_request", [](PyMoneroRpcConnection& self, const PyMoneroJsonRequest& request) {
      MONERO_CATCH_AND_RETHROW(self.send_json_request(request));
    }, py::arg("request"));

  // monero_connection_manager_listener
  py::class_<PyMoneroConnectionManagerListener, std::shared_ptr<PyMoneroConnectionManagerListener>>(m, "MoneroConnectionManagerListener")
    .def(py::init<>())
    .def("on_connection_changed", [](PyMoneroConnectionManagerListener& self, std::shared_ptr<PyMoneroRpcConnection> &connection) {
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
    .def("start_polling", [](PyMoneroConnectionManager& self, uint64_t period_ms) {
      MONERO_CATCH_AND_RETHROW(self.start_polling(period_ms));
    }, py::arg("period_ms") = 20000)
    .def("start_polling", [](PyMoneroConnectionManager& self, uint64_t period_ms, bool autoswitch, uint64_t timeout_ms, PyMoneroConnectionPoolType poll_type, std::vector<std::shared_ptr<PyMoneroRpcConnection>> excluded_connections) {
      MONERO_CATCH_AND_RETHROW(self.start_polling(period_ms, autoswitch, timeout_ms, poll_type, excluded_connections));
    }, py::arg("period_ms"), py::arg("autoswitch"), py::arg("timeout_ms"), py::arg("poll_type"), py::arg("excluded_connections"))
    .def("start_polling", [](PyMoneroConnectionManager& self, uint64_t period_ms, bool autoswitch, uint64_t timeout_ms, PyMoneroConnectionPoolType poll_type) {
      MONERO_CATCH_AND_RETHROW(self.start_polling(period_ms, autoswitch, timeout_ms, poll_type));
    }, py::arg("period_ms"), py::arg("autoswitch"), py::arg("timeout_ms"), py::arg("poll_type"))
    .def("start_polling", [](PyMoneroConnectionManager& self, uint64_t period_ms, bool autoswitch, uint64_t timeout_ms) {
      MONERO_CATCH_AND_RETHROW(self.start_polling(period_ms, autoswitch, timeout_ms));
    }, py::arg("period_ms"), py::arg("autoswitch"), py::arg("timeout_ms"))
    .def("start_polling", [](PyMoneroConnectionManager& self, uint64_t period_ms, bool autoswitch) {
      MONERO_CATCH_AND_RETHROW(self.start_polling(period_ms, autoswitch));
    }, py::arg("period_ms"), py::arg("autoswitch"))
    .def("start_polling", [](PyMoneroConnectionManager& self, uint64_t period_ms, PyMoneroConnectionPoolType poll_type) {
      MONERO_CATCH_AND_RETHROW(self.start_polling(period_ms, poll_type));
    }, py::arg("period_ms"), py::arg("poll_type"))
    .def("stop_polling", [](PyMoneroConnectionManager& self) {
      MONERO_CATCH_AND_RETHROW(self.stop_polling());
    })
    .def("set_autoswitch", [](PyMoneroConnectionManager& self, bool autoswitch) {
      MONERO_CATCH_AND_RETHROW(self.set_autoswitch(autoswitch));
    }, py::arg("autoswitch"))
    .def("get_autoswitch", [](PyMoneroConnectionManager& self) {
      MONERO_CATCH_AND_RETHROW(self.get_autoswitch());
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
  py::class_<monero::monero_block_header, monero::serializable_struct, std::shared_ptr<monero::monero_block_header>>(m, "MoneroBlockHeader")
    .def(py::init<>())
    .def_property("hash", 
      [](const monero::monero_block_header& self) { return self.m_hash.value_or(""); },
      [](monero::monero_block_header& self, std::string val) { self.m_hash = val; })
    .def_property("height", 
      [](const monero::monero_block_header& self) { return self.m_height.value_or(0); },
      [](monero::monero_block_header& self, uint64_t val) { self.m_height = val; })
    .def_property("timestamp", 
      [](const monero::monero_block_header& self) { return self.m_timestamp.value_or(0); },
      [](monero::monero_block_header& self, uint64_t val) { self.m_timestamp = val; })
    .def_property("size", 
      [](const monero::monero_block_header& self) { return self.m_size.value_or(0); },
      [](monero::monero_block_header& self, uint64_t val) { self.m_size = val; })
    .def_property("weight", 
      [](const monero::monero_block_header& self) { return self.m_weight.value_or(0); },
      [](monero::monero_block_header& self, uint64_t val) { self.m_weight = val; })
    .def_property("long_term_weight", 
      [](const monero::monero_block_header& self) { return self.m_long_term_weight.value_or(0); },
      [](monero::monero_block_header& self, uint64_t val) { self.m_long_term_weight = val; })
    .def_property("depth", 
      [](const monero::monero_block_header& self) { return self.m_depth.value_or(0); },
      [](monero::monero_block_header& self, uint64_t val) { self.m_depth = val; })
    .def_property("difficulty", 
      [](const monero::monero_block_header& self) { return self.m_difficulty.value_or(0); },
      [](monero::monero_block_header& self, uint64_t val) { self.m_difficulty = val; })
    .def_property("cumulative_difficulty", 
      [](const monero::monero_block_header& self) { return self.m_cumulative_difficulty.value_or(0); },
      [](monero::monero_block_header& self, uint64_t val) { self.m_cumulative_difficulty = val; })
    .def_property("major_version", 
      [](const monero::monero_block_header& self) { return self.m_major_version.value_or(0); },
      [](monero::monero_block_header& self, uint32_t val) { self.m_major_version = val; })
    .def_property("minor_version", 
      [](const monero::monero_block_header& self) { return self.m_minor_version.value_or(0); },
      [](monero::monero_block_header& self, uint32_t val) { self.m_minor_version = val; })
    .def_property("nonce", 
      [](const monero::monero_block_header& self) { return self.m_nonce.value_or(0); },
      [](monero::monero_block_header& self, uint32_t val) { self.m_nonce = val; })
    .def_property("miner_tx_hash", 
      [](const monero::monero_block_header& self) { return self.m_miner_tx_hash.value_or(""); },
      [](monero::monero_block_header& self, std::string& val) { self.m_miner_tx_hash = val; })
    .def_property("num_txs", 
      [](const monero::monero_block_header& self) { return self.m_num_txs.value_or(0); },
      [](monero::monero_block_header& self, uint32_t val) { self.m_num_txs = val; })
    .def_property("orphan_status", 
      [](const monero::monero_block_header& self) { return self.m_orphan_status.value_or(false); },
      [](monero::monero_block_header& self, bool val) { self.m_orphan_status = val; })
    .def_property("prev_hash", 
      [](const monero::monero_block_header& self) { return self.m_prev_hash.value_or(""); },
      [](monero::monero_block_header& self, std::string& val) { self.m_prev_hash = val; })
    .def_property("reward", 
      [](const monero::monero_block_header& self) { return self.m_reward.value_or(0); },
      [](monero::monero_block_header& self, uint64_t val) { self.m_reward = val; })
    .def_property("pow_hash", 
      [](const monero::monero_block_header& self) { return self.m_pow_hash.value_or(""); },
      [](monero::monero_block_header& self, std::string& val) { self.m_pow_hash = val; });

  // monero_block
  py::class_<monero::monero_block, monero::monero_block_header, std::shared_ptr<monero::monero_block>>(m, "MoneroBlock")
    .def(py::init<>())
    .def_property("hex", 
      [](const monero::monero_block& self) { return self.m_hex.value_or(""); },
      [](monero::monero_block& self, std::string val) { self.m_hex = val; })
    .def_property("miner_tx", 
      [](const monero::monero_block& self) { return self.m_miner_tx.value_or(nullptr); },
      [](monero::monero_block& self, std::shared_ptr<monero::monero_tx> val) { self.m_miner_tx = val; })
    .def_readwrite("txs", &monero::monero_block::m_txs)
    .def_readwrite("tx_hashes", &monero::monero_block::m_tx_hashes);

  // monero_block_template
  py::class_<PyMoneroBlockTemplate, std::shared_ptr<PyMoneroBlockTemplate>>(m, "MoneroBlockTemplate")
    .def(py::init<>())
    .def_property("block_template_blob", 
      [](const PyMoneroBlockTemplate& self) { return self.m_block_template_blob.value_or(""); },
      [](PyMoneroBlockTemplate& self, std::string& val) { self.m_block_template_blob = val; })
    .def_property("block_hashing_blob", 
      [](const PyMoneroBlockTemplate& self) { return self.m_block_hashing_blob.value_or(""); },
      [](PyMoneroBlockTemplate& self, std::string& val) { self.m_block_hashing_blob = val; })
    .def_property("difficulty", 
      [](const PyMoneroBlockTemplate& self) { return self.m_difficulty.value_or(0); },
      [](PyMoneroBlockTemplate& self, uint64_t val) { self.m_difficulty = val; })
    .def_property("expected_reward", 
      [](const PyMoneroBlockTemplate& self) { return self.m_expected_reward.value_or(0); },
      [](PyMoneroBlockTemplate& self, uint64_t val) { self.m_expected_reward = val; })
    .def_property("height", 
      [](const PyMoneroBlockTemplate& self) { return self.m_height.value_or(0); },
      [](PyMoneroBlockTemplate& self, uint64_t val) { self.m_height = val; })
    .def_property("prev_hash", 
      [](const PyMoneroBlockTemplate& self) { return self.m_prev_hash.value_or(""); },
      [](PyMoneroBlockTemplate& self, std::string& val) { self.m_prev_hash = val; })
    .def_property("reserved_offset", 
      [](const PyMoneroBlockTemplate& self) { return self.m_reserved_offset.value_or(0); },
      [](PyMoneroBlockTemplate& self, uint64_t val) { self.m_reserved_offset = val; })
    .def_property("seed_height", 
      [](const PyMoneroBlockTemplate& self) { return self.m_seed_height.value_or(0); },
      [](PyMoneroBlockTemplate& self, uint64_t val) { self.m_seed_height = val; })
    .def_property("seed_hash", 
      [](const PyMoneroBlockTemplate& self) { return self.m_seed_hash.value_or(""); },
      [](PyMoneroBlockTemplate& self, std::string& val) { self.m_seed_hash = val; })
    .def_property("next_seed_hash", 
      [](const PyMoneroBlockTemplate& self) { return self.m_next_seed_hash.value_or(""); },
      [](PyMoneroBlockTemplate& self, std::string& val) { self.m_next_seed_hash = val; });

  // monero_connection_span
  py::class_<PyMoneroConnectionSpan, std::shared_ptr<PyMoneroConnectionSpan>>(m, "MoneroConnectionSpan")
    .def(py::init<>())
    .def_property("connection_id", 
      [](const PyMoneroConnectionSpan& self) { return self.m_connection_id.value_or(""); },
      [](PyMoneroConnectionSpan& self, std::string& val) { self.m_connection_id = val; })
    .def_property("num_blocks", 
      [](const PyMoneroConnectionSpan& self) { return self.m_num_blocks.value_or(0); },
      [](PyMoneroConnectionSpan& self, uint64_t val) { self.m_num_blocks = val; })
    .def_property("remote_address", 
      [](const PyMoneroConnectionSpan& self) { return self.m_remote_address.value_or(""); },
      [](PyMoneroConnectionSpan& self, std::string& val) { self.m_remote_address = val; })
    .def_property("rate", 
      [](const PyMoneroConnectionSpan& self) { return self.m_rate.value_or(0); },
      [](PyMoneroConnectionSpan& self, uint64_t val) { self.m_rate = val; })
    .def_property("speed", 
      [](const PyMoneroConnectionSpan& self) { return self.m_speed.value_or(0); },
      [](PyMoneroConnectionSpan& self, uint64_t val) { self.m_speed = val; })
    .def_property("size", 
      [](const PyMoneroConnectionSpan& self) { return self.m_size.value_or(0); },
      [](PyMoneroConnectionSpan& self, uint64_t val) { self.m_size = val; })
    .def_property("start_height", 
      [](const PyMoneroConnectionSpan& self) { return self.m_start_height.value_or(0); },
      [](PyMoneroConnectionSpan& self, uint64_t val) { self.m_start_height = val; });

  // monero_peer
  py::class_<PyMoneroPeer, std::shared_ptr<PyMoneroPeer>>(m, "MoneroPeer")
    .def(py::init<>())
    .def_property("id", 
      [](const PyMoneroPeer& self) { return self.m_id.value_or(""); },
      [](PyMoneroPeer& self, std::string& val) { self.m_id = val; })
    .def_property("address", 
      [](const PyMoneroPeer& self) { return self.m_address.value_or(""); },
      [](PyMoneroPeer& self, std::string& val) { self.m_address = val; })
    .def_property("host", 
      [](const PyMoneroPeer& self) { return self.m_host.value_or(""); },
      [](PyMoneroPeer& self, std::string& val) { self.m_host = val; })
    .def_property("port", 
      [](const PyMoneroPeer& self) { return self.m_port.value_or(0); },
      [](PyMoneroPeer& self, int val) { self.m_port = val; })
    .def_property("is_online", 
      [](const PyMoneroPeer& self) { return self.m_is_online.value_or(false); },
      [](PyMoneroPeer& self, bool val) { self.m_is_online = val; })
    .def_property("last_seen_timestamp", 
      [](const PyMoneroPeer& self) { return self.m_last_seen_timestamp.value_or(0); },
      [](PyMoneroPeer& self, uint64_t val) { self.m_last_seen_timestamp = val; })
    .def_property("pruning_seed", 
      [](const PyMoneroPeer& self) { return self.m_pruning_seed.value_or(0); },
      [](PyMoneroPeer& self, int val) { self.m_pruning_seed = val; })
    .def_property("rpc_port", 
      [](const PyMoneroPeer& self) { return self.m_rpc_port.value_or(0); },
      [](PyMoneroPeer& self, int val) { self.m_rpc_port = val; })
    .def_property("rpc_credits_per_hash", 
      [](const PyMoneroPeer& self) { return self.m_rpc_credits_per_hash.value_or(0); },
      [](PyMoneroPeer& self, uint64_t val) { self.m_rpc_credits_per_hash = val; })
    .def_property("hash", 
      [](const PyMoneroPeer& self) { return self.m_hash.value_or(""); },
      [](PyMoneroPeer& self, std::string& val) { self.m_hash = val; })
    .def_property("avg_download", 
      [](const PyMoneroPeer& self) { return self.m_avg_download.value_or(0); },
      [](PyMoneroPeer& self, uint64_t val) { self.m_avg_download = val; })
    .def_property("avg_upload", 
      [](const PyMoneroPeer& self) { return self.m_avg_upload.value_or(0); },
      [](PyMoneroPeer& self, uint64_t val) { self.m_avg_upload = val; })
    .def_property("current_download", 
      [](const PyMoneroPeer& self) { return self.m_current_download.value_or(0); },
      [](PyMoneroPeer& self, uint64_t val) { self.m_current_download = val; })
    .def_property("current_upload", 
      [](const PyMoneroPeer& self) { return self.m_current_upload.value_or(0); },
      [](PyMoneroPeer& self, uint64_t val) { self.m_current_upload = val; })
    .def_property("height", 
      [](const PyMoneroPeer& self) { return self.m_height.value_or(0); },
      [](PyMoneroPeer& self, uint64_t val) { self.m_height = val; })
    .def_property("is_incoming", 
      [](const PyMoneroPeer& self) { return self.m_is_incoming.value_or(false); },
      [](PyMoneroPeer& self, bool val) { self.m_is_incoming = val; })
    .def_property("live_time", 
      [](const PyMoneroPeer& self) { return self.m_live_time.value_or(0); },
      [](PyMoneroPeer& self, uint64_t val) { self.m_live_time = val; })
    .def_property("is_local_ip", 
      [](const PyMoneroPeer& self) { return self.m_is_local_ip.value_or(false); },
      [](PyMoneroPeer& self, bool val) { self.m_is_local_ip = val; })
    .def_property("is_local_host", 
      [](const PyMoneroPeer& self) { return self.m_is_local_host.value_or(false); },
      [](PyMoneroPeer& self, bool val) { self.m_is_local_host = val; })
    .def_property("num_receives", 
      [](const PyMoneroPeer& self) { return self.m_num_receives.value_or(0); },
      [](PyMoneroPeer& self, int val) { self.m_num_receives = val; })
    .def_property("num_sends", 
      [](const PyMoneroPeer& self) { return self.m_num_sends.value_or(0); },
      [](PyMoneroPeer& self, int val) { self.m_num_sends = val; })
    .def_property("receive_idle_time", 
      [](const PyMoneroPeer& self) { return self.m_receive_idle_time.value_or(0); },
      [](PyMoneroPeer& self, uint64_t val) { self.m_receive_idle_time = val; })
    .def_property("send_idle_time", 
      [](const PyMoneroPeer& self) { return self.m_send_idle_time.value_or(0); },
      [](PyMoneroPeer& self, uint64_t val) { self.m_send_idle_time = val; })
    .def_property("state", 
      [](const PyMoneroPeer& self) { return self.m_state.value_or(""); },
      [](PyMoneroPeer& self, std::string& val) { self.m_state = val; })
    .def_property("num_support_flags", 
      [](const PyMoneroPeer& self) { return self.m_num_support_flags.value_or(0); },
      [](PyMoneroPeer& self, int val) { self.m_num_support_flags = val; })
    .def_property("connection_type", 
      [](const PyMoneroPeer& self) { return self.m_connection_type.value_or(PyMoneroConnectionType::INVALID); },
      [](PyMoneroPeer& self, PyMoneroConnectionType val) { self.m_connection_type = val; });

  // monero_alt_chain
  py::class_<PyMoneroAltChain, std::shared_ptr<PyMoneroAltChain>>(m, "MoneroAltChain")
    .def(py::init<>())
    .def_property("block_hashes", 
      [](const PyMoneroAltChain& self) { return self.m_block_hashes; },
      [](PyMoneroAltChain& self, std::vector<std::string>& val) { self.m_block_hashes = val; })
    .def_property("difficulty", 
      [](const PyMoneroAltChain& self) { return self.m_difficulty.value_or(0); },
      [](PyMoneroAltChain& self, uint64_t val) { self.m_difficulty = val; })
    .def_property("height", 
      [](const PyMoneroAltChain& self) { return self.m_height.value_or(0); },
      [](PyMoneroAltChain& self, uint64_t val) { self.m_height = val; })
    .def_property("length", 
      [](const PyMoneroAltChain& self) { return self.m_length.value_or(0); },
      [](PyMoneroAltChain& self, uint64_t val) { self.m_length = val; })
    .def_property("main_chain_parent_block_hash", 
      [](const PyMoneroAltChain& self) { return self.m_main_chain_parent_block_hash.value_or(""); },
      [](PyMoneroAltChain& self, std::string& val) { self.m_main_chain_parent_block_hash = val; });

  // monero_ban
  py::class_<PyMoneroBan, std::shared_ptr<PyMoneroBan>>(m, "MoneroBan")
    .def(py::init<>())
    .def_property("host", 
      [](const PyMoneroBan& self) { return self.m_host.value_or(""); },
      [](PyMoneroBan& self, std::string& val) { self.m_host = val; })
    .def_property("ip", 
      [](const PyMoneroBan& self) { return self.m_ip.value_or(0); },
      [](PyMoneroBan& self, int val) { self.m_ip = val; })
    .def_property("is_banned", 
      [](const PyMoneroBan& self) { return self.m_is_banned.value_or(false); },
      [](PyMoneroBan& self, bool val) { self.m_is_banned = val; })
    .def_property("seconds", 
      [](const PyMoneroBan& self) { return self.m_seconds.value_or(0); },
      [](PyMoneroBan& self, uint64_t val) { self.m_seconds = val; });
  
  // monero_output_distribution_entry
  py::class_<PyMoneroOutputDistributionEntry, std::shared_ptr<PyMoneroOutputDistributionEntry>>(m, "MoneroOutputDistributionEntry")
    .def(py::init<>())
    .def_property("amount", 
      [](const PyMoneroOutputDistributionEntry& self) { return self.m_amount.value_or(0); },
      [](PyMoneroOutputDistributionEntry& self, uint64_t val) { self.m_amount = val; })
    .def_property("base", 
      [](const PyMoneroOutputDistributionEntry& self) { return self.m_base.value_or(0); },
      [](PyMoneroOutputDistributionEntry& self, int val) { self.m_base = val; })
    .def_readwrite("distribution", &PyMoneroOutputDistributionEntry::m_distribution)
    .def_property("start_height", 
      [](const PyMoneroOutputDistributionEntry& self) { return self.m_start_height.value_or(0); },
      [](PyMoneroOutputDistributionEntry& self, uint64_t val) { self.m_start_height = val; });
  
  // monero_output_histogram_entry
  py::class_<PyMoneroOutputHistogramEntry, std::shared_ptr<PyMoneroOutputHistogramEntry>>(m, "MoneroOutputHistogramEntry")
    .def(py::init<>())
    .def_property("amount", 
      [](const PyMoneroOutputHistogramEntry& self) { return self.m_amount.value_or(0); },
      [](PyMoneroOutputHistogramEntry& self, uint64_t val) { self.m_amount = val; })
    .def_property("num_instances", 
      [](const PyMoneroOutputHistogramEntry& self) { return self.m_num_instances.value_or(0); },
      [](PyMoneroOutputHistogramEntry& self, uint64_t val) { self.m_num_instances = val; })
    .def_property("unlocked_instances", 
      [](const PyMoneroOutputHistogramEntry& self) { return self.m_unlocked_instances.value_or(0); },
      [](PyMoneroOutputHistogramEntry& self, uint64_t val) { self.m_unlocked_instances = val; })
    .def_property("recent_instances", 
      [](const PyMoneroOutputHistogramEntry& self) { return self.m_recent_instances.value_or(0); },
      [](PyMoneroOutputHistogramEntry& self, uint64_t val) { self.m_recent_instances = val; });
  
  // monero_hard_fork_info
  py::class_<PyMoneroHardForkInfo, std::shared_ptr<PyMoneroHardForkInfo>>(m, "MoneroHardForkInfo")
    .def(py::init<>())
    .def_property("earliest_height", 
      [](const PyMoneroHardForkInfo& self) { return self.m_earliest_height.value_or(0); },
      [](PyMoneroHardForkInfo& self, uint64_t val) { self.m_earliest_height = val; })
    .def_property("is_enabled", 
      [](const PyMoneroHardForkInfo& self) { return self.m_is_enabled.value_or(false); },
      [](PyMoneroHardForkInfo& self, bool val) { self.m_is_enabled = val; })
    .def_property("state", 
      [](const PyMoneroHardForkInfo& self) { return self.m_state.value_or(0); },
      [](PyMoneroHardForkInfo& self, int val) { self.m_state = val; })
    .def_property("threshold", 
      [](const PyMoneroHardForkInfo& self) { return self.m_threshold.value_or(0); },
      [](PyMoneroHardForkInfo& self, int val) { self.m_threshold = val; })
    .def_property("version", 
      [](const PyMoneroHardForkInfo& self) { return self.m_version.value_or(0); },
      [](PyMoneroHardForkInfo& self, int val) { self.m_version = val; })
    .def_property("num_votes", 
      [](const PyMoneroHardForkInfo& self) { return self.m_num_votes.value_or(0); },
      [](PyMoneroHardForkInfo& self, int val) { self.m_num_votes = val; })
    .def_property("window", 
      [](const PyMoneroHardForkInfo& self) { return self.m_window.value_or(0); },
      [](PyMoneroHardForkInfo& self, int val) { self.m_window = val; })
    .def_property("voting", 
      [](const PyMoneroHardForkInfo& self) { return self.m_voting.value_or(0); },
      [](PyMoneroHardForkInfo& self, int val) { self.m_voting = val; })
    .def_property("credits", 
      [](const PyMoneroHardForkInfo& self) { return self.m_credits.value_or(0); },
      [](PyMoneroHardForkInfo& self, uint64_t val) { self.m_credits = val; })
    .def_property("top_block_hash", 
      [](const PyMoneroHardForkInfo& self) { return self.m_top_block_hash.value_or(""); },
      [](PyMoneroHardForkInfo& self, std::string& val) { self.m_top_block_hash = val; });

  // monero_prune_result
  py::class_<PyMoneroPruneResult, std::shared_ptr<PyMoneroPruneResult>>(m, "MoneroPruneResult")
    .def(py::init<>())
    .def_property("is_pruned", 
      [](const PyMoneroPruneResult& self) { return self.m_is_pruned.value_or(false); },
      [](PyMoneroPruneResult& self, bool val) { self.m_is_pruned = val; })
    .def_property("pruning_seed", 
      [](const PyMoneroPruneResult& self) { return self.m_pruning_seed.value_or(0); },
      [](PyMoneroPruneResult& self, int val) { self.m_pruning_seed = val; });
  
  // monero_daemon_sync_info
  py::class_<PyMoneroDaemonSyncInfo, std::shared_ptr<PyMoneroDaemonSyncInfo>>(m, "MoneroDaemonSyncInfo")
  .def(py::init<>())
  .def_property("height", 
    [](const PyMoneroDaemonSyncInfo& self) { return self.m_height.value_or(0); },
    [](PyMoneroDaemonSyncInfo& self, uint64_t val) { self.m_height = val; })
  .def_readwrite("peers", &PyMoneroDaemonSyncInfo::m_peers)
  .def_readwrite("spans", &PyMoneroDaemonSyncInfo::m_spans)
  .def_property("target_height", 
    [](const PyMoneroDaemonSyncInfo& self) { return self.m_target_height.value_or(0); },
    [](PyMoneroDaemonSyncInfo& self, uint64_t val) { self.m_target_height = val; })
  .def_property("next_needed_pruning_seed", 
    [](const PyMoneroDaemonSyncInfo& self) { return self.m_next_needed_pruning_seed.value_or(0); },
    [](PyMoneroDaemonSyncInfo& self, int val) { self.m_next_needed_pruning_seed = val; })
  .def_property("overview", 
    [](const PyMoneroDaemonSyncInfo& self) { return self.m_overview.value_or(""); },
    [](PyMoneroDaemonSyncInfo& self, std::string& val) { self.m_overview = val; })
  .def_property("credits", 
    [](const PyMoneroDaemonSyncInfo& self) { return self.m_credits.value_or(0); },
    [](PyMoneroDaemonSyncInfo& self, uint64_t val) { self.m_credits = val; })
  .def_property("top_block_hash", 
    [](const PyMoneroDaemonSyncInfo& self) { return self.m_top_block_hash.value_or(""); },
    [](PyMoneroDaemonSyncInfo& self, std::string& val) { self.m_top_block_hash = val; });
  
  // monero_daemon_info
  py::class_<PyMoneroDaemonInfo, std::shared_ptr<PyMoneroDaemonInfo>>(m, "MoneroDaemonInfo")
  .def(py::init<>())
  .def_property("version", 
    [](const PyMoneroDaemonInfo& self) { return self.m_version.value_or(""); },
    [](PyMoneroDaemonInfo& self, std::string& val) { self.m_version = val; })
  .def_property("num_alt_blocks", 
    [](const PyMoneroDaemonInfo& self) { return self.m_num_alt_blocks.value_or(0); },
    [](PyMoneroDaemonInfo& self, uint64_t val) { self.m_num_alt_blocks = val; })
  .def_property("block_size_limit", 
    [](const PyMoneroDaemonInfo& self) { return self.m_block_size_limit.value_or(0); },
    [](PyMoneroDaemonInfo& self, uint64_t val) { self.m_block_size_limit = val; })
  .def_property("block_size_median", 
    [](const PyMoneroDaemonInfo& self) { return self.m_block_size_median.value_or(0); },
    [](PyMoneroDaemonInfo& self, uint64_t val) { self.m_block_size_median = val; })
  .def_property("block_weight_limit", 
    [](const PyMoneroDaemonInfo& self) { return self.m_block_weight_limit.value_or(0); },
    [](PyMoneroDaemonInfo& self, uint64_t val) { self.m_block_weight_limit = val; })
  .def_property("block_weight_median", 
    [](const PyMoneroDaemonInfo& self) { return self.m_block_weight_median.value_or(0); },
    [](PyMoneroDaemonInfo& self, uint64_t val) { self.m_block_weight_median = val; })
  .def_property("bootstrap_daemon_address", 
    [](const PyMoneroDaemonInfo& self) { return self.m_bootstrap_daemon_address.value_or(""); },
    [](PyMoneroDaemonInfo& self, std::string& val) { self.m_bootstrap_daemon_address = val; })
  .def_property("difficulty", 
    [](const PyMoneroDaemonInfo& self) { return self.m_difficulty.value_or(0); },
    [](PyMoneroDaemonInfo& self, uint64_t val) { self.m_difficulty = val; })
  .def_property("cumulative_difficulty", 
    [](const PyMoneroDaemonInfo& self) { return self.m_cumulative_difficulty.value_or(0); },
    [](PyMoneroDaemonInfo& self, uint64_t val) { self.m_cumulative_difficulty = val; })
  .def_property("free_space", 
    [](const PyMoneroDaemonInfo& self) { return self.m_free_space.value_or(0); },
    [](PyMoneroDaemonInfo& self, uint64_t val) { self.m_free_space = val; })
  .def_property("num_offline_peers", 
    [](const PyMoneroDaemonInfo& self) { return self.m_num_offline_peers.value_or(0); },
    [](PyMoneroDaemonInfo& self, int val) { self.m_num_offline_peers = val; })
  .def_property("num_online_peers", 
    [](const PyMoneroDaemonInfo& self) { return self.m_num_online_peers.value_or(0); },
    [](PyMoneroDaemonInfo& self, int val) { self.m_num_online_peers = val; })
  .def_property("height", 
    [](const PyMoneroDaemonInfo& self) { return self.m_height.value_or(0); },
    [](PyMoneroDaemonInfo& self, uint64_t val) { self.m_height = val; })
  .def_property("height_without_bootstrap", 
    [](const PyMoneroDaemonInfo& self) { return self.m_height_without_bootstrap.value_or(0); },
    [](PyMoneroDaemonInfo& self, uint64_t val) { self.m_height_without_bootstrap = val; })
  .def_property("network_type", 
    [](const PyMoneroDaemonInfo& self) { return self.m_network_type.value_or(monero::monero_network_type::MAINNET); },
    [](PyMoneroDaemonInfo& self, monero::monero_network_type val) { self.m_network_type = val; })
  .def_property("is_offline", 
    [](const PyMoneroDaemonInfo& self) { return self.m_is_offline.value_or(false); },
    [](PyMoneroDaemonInfo& self, bool val) { self.m_is_offline = val; })
  .def_property("num_incoming_connections", 
    [](const PyMoneroDaemonInfo& self) { return self.m_num_incoming_connections.value_or(0); },
    [](PyMoneroDaemonInfo& self, int val) { self.m_num_incoming_connections = val; })
  .def_property("num_outgoing_connections", 
    [](const PyMoneroDaemonInfo& self) { return self.m_num_outgoing_connections.value_or(0); },
    [](PyMoneroDaemonInfo& self, int val) { self.m_num_outgoing_connections = val; })
  .def_property("num_rpc_connections", 
    [](const PyMoneroDaemonInfo& self) { return self.m_num_rpc_connections.value_or(0); },
    [](PyMoneroDaemonInfo& self, int val) { self.m_num_rpc_connections = val; })
  .def_property("start_timestamp", 
    [](const PyMoneroDaemonInfo& self) { return self.m_start_timestamp.value_or(0); },
    [](PyMoneroDaemonInfo& self, uint64_t val) { self.m_start_timestamp = val; })
  .def_property("adjusted_timestamp", 
    [](const PyMoneroDaemonInfo& self) { return self.m_adjusted_timestamp.value_or(0); },
    [](PyMoneroDaemonInfo& self, uint64_t val) { self.m_adjusted_timestamp = val; })
  .def_property("target", 
    [](const PyMoneroDaemonInfo& self) { return self.m_target.value_or(0); },
    [](PyMoneroDaemonInfo& self, uint64_t val) { self.m_target = val; })
  .def_property("target_height", 
    [](const PyMoneroDaemonInfo& self) { return self.m_target_height.value_or(0); },
    [](PyMoneroDaemonInfo& self, uint64_t val) { self.m_target_height = val; })
  .def_property("top_block_hash", 
    [](const PyMoneroDaemonInfo& self) { return self.m_top_block_hash.value_or(""); },
    [](PyMoneroDaemonInfo& self, std::string& val) { self.m_top_block_hash = val; })
  .def_property("num_txs", 
    [](const PyMoneroDaemonInfo& self) { return self.m_num_txs.value_or(0); },
    [](PyMoneroDaemonInfo& self, int val) { self.m_num_txs = val; })
  .def_property("num_txs_pool", 
    [](const PyMoneroDaemonInfo& self) { return self.m_num_txs_pool.value_or(0); },
    [](PyMoneroDaemonInfo& self, int val) { self.m_num_txs_pool = val; })
  .def_property("was_bootstrap_ever_used", 
    [](const PyMoneroDaemonInfo& self) { return self.m_was_bootstrap_ever_used.value_or(false); },
    [](PyMoneroDaemonInfo& self, bool val) { self.m_was_bootstrap_ever_used = val; })
  .def_property("database_size", 
    [](const PyMoneroDaemonInfo& self) { return self.m_database_size.value_or(0); },
    [](PyMoneroDaemonInfo& self, uint64_t val) { self.m_database_size = val; })
  .def_property("update_available", 
    [](const PyMoneroDaemonInfo& self) { return self.m_update_available.value_or(false); },
    [](PyMoneroDaemonInfo& self, bool val) { self.m_update_available = val; })
  .def_property("credits", 
    [](const PyMoneroDaemonInfo& self) { return self.m_credits.value_or(0); },
    [](PyMoneroDaemonInfo& self, uint64_t val) { self.m_credits = val; })
  .def_property("is_busy_syncing", 
    [](const PyMoneroDaemonInfo& self) { return self.m_is_busy_syncing.value_or(false); },
    [](PyMoneroDaemonInfo& self, bool val) { self.m_is_busy_syncing = val; })
  .def_property("is_synchronized", 
    [](const PyMoneroDaemonInfo& self) { return self.m_is_synchronized.value_or(false); },
    [](PyMoneroDaemonInfo& self, bool val) { self.m_is_synchronized = val; })
  .def_property("is_restricted", 
    [](const PyMoneroDaemonInfo& self) { return self.m_is_restricted.value_or(false); },
    [](PyMoneroDaemonInfo& self, bool val) { self.m_is_restricted = val; });

  // monero_daemon_update_check_result
  py::class_<PyMoneroDaemonUpdateCheckResult, std::shared_ptr<PyMoneroDaemonUpdateCheckResult>>(m, "MoneroDaemonUpdateCheckResult")
  .def(py::init<>())
  .def_property("is_update_available", 
    [](const PyMoneroDaemonUpdateCheckResult& self) { return self.m_is_update_available.value_or(false); },
    [](PyMoneroDaemonUpdateCheckResult& self, bool val) { self.m_is_update_available = val; })
  .def_property("version", 
    [](const PyMoneroDaemonUpdateCheckResult& self) { return self.m_version.value_or(""); },
    [](PyMoneroDaemonUpdateCheckResult& self, std::string& val) { self.m_version = val; })
  .def_property("hash", 
    [](const PyMoneroDaemonUpdateCheckResult& self) { return self.m_hash.value_or(""); },
    [](PyMoneroDaemonUpdateCheckResult& self, std::string& val) { self.m_hash = val; })
  .def_property("auto_uri", 
    [](const PyMoneroDaemonUpdateCheckResult& self) { return self.m_auto_uri.value_or(""); },
    [](PyMoneroDaemonUpdateCheckResult& self, std::string& val) { self.m_auto_uri = val; })
  .def_property("user_uri", 
    [](const PyMoneroDaemonUpdateCheckResult& self) { return self.m_user_uri.value_or(""); },
    [](PyMoneroDaemonUpdateCheckResult& self, std::string& val) { self.m_user_uri = val; });

  // monero_daemon_update_check_result
  py::class_<PyMoneroDaemonUpdateDownloadResult, PyMoneroDaemonUpdateCheckResult, std::shared_ptr<PyMoneroDaemonUpdateDownloadResult>>(m, "MoneroDaemonUpdateDownloadResult")
  .def(py::init<>())
  .def_property("download_path", 
    [](const PyMoneroDaemonUpdateDownloadResult& self) { return self.m_download_path.value_or(""); },
    [](PyMoneroDaemonUpdateDownloadResult& self, std::string& val) { self.m_download_path = val; });
  
  // monero_submit_tx_result
  py::class_<PyMoneroSubmitTxResult, std::shared_ptr<PyMoneroSubmitTxResult>>(m, "MoneroSubmitTxResult")
    .def(py::init<>())
    .def_property("is_good", 
      [](const PyMoneroSubmitTxResult& self) { return self.m_is_good.value_or(false); },
      [](PyMoneroSubmitTxResult& self, bool val) { self.m_is_good = val; })
    .def_property("is_relayed", 
      [](const PyMoneroSubmitTxResult& self) { return self.m_is_relayed.value_or(false); },
      [](PyMoneroSubmitTxResult& self, bool val) { self.m_is_relayed = val; })
    .def_property("is_double_spend", 
      [](const PyMoneroSubmitTxResult& self) { return self.m_is_double_spend.value_or(false); },
      [](PyMoneroSubmitTxResult& self, bool val) { self.m_is_double_spend = val; })
    .def_property("is_fee_too_low", 
      [](const PyMoneroSubmitTxResult& self) { return self.m_is_fee_too_low.value_or(false); },
      [](PyMoneroSubmitTxResult& self, bool val) { self.m_is_fee_too_low = val; })
    .def_property("is_mixin_too_low", 
      [](const PyMoneroSubmitTxResult& self) { return self.m_is_mixin_too_low.value_or(false); },
      [](PyMoneroSubmitTxResult& self, bool val) { self.m_is_mixin_too_low = val; })
    .def_property("has_invalid_input", 
      [](const PyMoneroSubmitTxResult& self) { return self.m_has_invalid_input.value_or(false); },
      [](PyMoneroSubmitTxResult& self, bool val) { self.m_has_invalid_input = val; })
    .def_property("has_invalid_output", 
      [](const PyMoneroSubmitTxResult& self) { return self.m_has_invalid_output.value_or(false); },
      [](PyMoneroSubmitTxResult& self, bool val) { self.m_has_invalid_output = val; })
    .def_property("has_too_few_outputs", 
      [](const PyMoneroSubmitTxResult& self) { return self.m_has_too_few_outputs.value_or(false); },
      [](PyMoneroSubmitTxResult& self, bool val) { self.m_has_too_few_outputs = val; })
    .def_property("is_overspend", 
      [](const PyMoneroSubmitTxResult& self) { return self.m_is_overspend.value_or(false); },
      [](PyMoneroSubmitTxResult& self, bool val) { self.m_is_overspend = val; })
    .def_property("is_too_big", 
      [](const PyMoneroSubmitTxResult& self) { return self.m_is_too_big.value_or(false); },
      [](PyMoneroSubmitTxResult& self, bool val) { self.m_is_too_big = val; })
    .def_property("sanity_check_failed", 
      [](const PyMoneroSubmitTxResult& self) { return self.m_sanity_check_failed.value_or(false); },
      [](PyMoneroSubmitTxResult& self, bool val) { self.m_sanity_check_failed = val; })
    .def_property("reason", 
      [](const PyMoneroSubmitTxResult& self) { return self.m_reason.value_or(""); },
      [](PyMoneroSubmitTxResult& self, std::string& val) { self.m_reason = val; })
    .def_property("credits", 
      [](const PyMoneroSubmitTxResult& self) { return self.m_credits.value_or(0); },
      [](PyMoneroSubmitTxResult& self, uint64_t val) { self.m_credits = val; })
    .def_property("top_block_hash", 
      [](const PyMoneroSubmitTxResult& self) { return self.m_top_block_hash.value_or(""); },
      [](PyMoneroSubmitTxResult& self, std::string& val) { self.m_top_block_hash = val; })
    .def_property("is_tx_extra_too_big", 
      [](const PyMoneroSubmitTxResult& self) { return self.m_is_tx_extra_too_big.value_or(false); },
      [](PyMoneroSubmitTxResult& self, bool val) { self.m_is_tx_extra_too_big = val; })
    .def_property("is_nonzero_unlock_time", 
      [](const PyMoneroSubmitTxResult& self) { return self.m_is_nonzero_unlock_time.value_or(false); },
      [](PyMoneroSubmitTxResult& self, bool val) { self.m_is_nonzero_unlock_time = val; });

  // monero_tx_pool_stats
  py::class_<PyMoneroTxPoolStats, std::shared_ptr<PyMoneroTxPoolStats>>(m, "MoneroTxPoolStats")
    .def(py::init<>())
    .def_property("num_txs", 
      [](const PyMoneroTxPoolStats& self) { return self.m_num_txs.value_or(0); },
      [](PyMoneroTxPoolStats& self, int val) { self.m_num_txs = val; })
    .def_property("num_not_relayed", 
      [](const PyMoneroTxPoolStats& self) { return self.m_num_not_relayed.value_or(0); },
      [](PyMoneroTxPoolStats& self, int val) { self.m_num_not_relayed = val; })
    .def_property("num_failing", 
      [](const PyMoneroTxPoolStats& self) { return self.m_num_failing.value_or(0); },
      [](PyMoneroTxPoolStats& self, int val) { self.m_num_failing = val; })
    .def_property("num_double_spends", 
      [](const PyMoneroTxPoolStats& self) { return self.m_num_double_spends.value_or(0); },
      [](PyMoneroTxPoolStats& self, int val) { self.m_num_double_spends = val; })
    .def_property("num10m", 
      [](const PyMoneroTxPoolStats& self) { return self.m_num10m.value_or(0); },
      [](PyMoneroTxPoolStats& self, int val) { self.m_num10m = val; })
    .def_property("fee_total", 
      [](const PyMoneroTxPoolStats& self) { return self.m_fee_total.value_or(0); },
      [](PyMoneroTxPoolStats& self, uint64_t val) { self.m_fee_total = val; })
    .def_property("bytes_max", 
      [](const PyMoneroTxPoolStats& self) { return self.m_bytes_max.value_or(0); },
      [](PyMoneroTxPoolStats& self, uint64_t val) { self.m_bytes_max = val; })
    .def_property("bytes_med", 
      [](const PyMoneroTxPoolStats& self) { return self.m_bytes_med.value_or(0); },
      [](PyMoneroTxPoolStats& self, uint64_t val) { self.m_bytes_med = val; })
    .def_property("bytes_min", 
      [](const PyMoneroTxPoolStats& self) { return self.m_bytes_min.value_or(0); },
      [](PyMoneroTxPoolStats& self, uint64_t val) { self.m_bytes_min = val; })
    .def_property("bytes_total", 
      [](const PyMoneroTxPoolStats& self) { return self.m_bytes_total.value_or(0); },
      [](PyMoneroTxPoolStats& self, uint64_t val) { self.m_bytes_total = val; })
    .def_property("histo98pc", 
      [](const PyMoneroTxPoolStats& self) { return self.m_histo98pc.value_or(0); },
      [](PyMoneroTxPoolStats& self, uint64_t val) { self.m_histo98pc = val; })
    .def_property("oldest_timestamp", 
      [](const PyMoneroTxPoolStats& self) { return self.m_oldest_timestamp.value_or(0); },
      [](PyMoneroTxPoolStats& self, uint64_t val) { self.m_oldest_timestamp = val; });
  
  // monero_mining_status
  py::class_<PyMoneroMiningStatus, std::shared_ptr<PyMoneroMiningStatus>>(m, "MoneroMiningStatus")
    .def(py::init<>())
    .def_property("is_active", 
      [](const PyMoneroMiningStatus& self) { return self.m_is_active.value_or(false); },
      [](PyMoneroMiningStatus& self, bool val) { self.m_is_active = val; })
    .def_property("is_background", 
      [](const PyMoneroMiningStatus& self) { return self.m_is_background.value_or(false); },
      [](PyMoneroMiningStatus& self, bool val) { self.m_is_background = val; })
    .def_property("address", 
      [](const PyMoneroMiningStatus& self) { return self.m_address.value_or(""); },
      [](PyMoneroMiningStatus& self, std::string& val) { self.m_address = val; })
    .def_property("speed", 
      [](const PyMoneroMiningStatus& self) { return self.m_speed.value_or(0); },
      [](PyMoneroMiningStatus& self, uint64_t val) { self.m_speed = val; })    
    .def_property("num_threads", 
      [](const PyMoneroMiningStatus& self) { return self.m_num_threads.value_or(0); },
      [](PyMoneroMiningStatus& self, int val) { self.m_num_threads = val; });

  // monero_miner_tx_sum
  py::class_<PyMoneroMinerTxSum, std::shared_ptr<PyMoneroMinerTxSum>>(m, "MoneroMinerTxSum")
    .def(py::init<>())
    .def_property("emission_sum", 
      [](const PyMoneroMinerTxSum& self) { return self.m_emission_sum.value_or(0); },
      [](PyMoneroMinerTxSum& self, uint64_t val) { self.m_emission_sum = val; })
    .def_property("fee_sum", 
      [](const PyMoneroMinerTxSum& self) { return self.m_fee_sum.value_or(0); },
      [](PyMoneroMinerTxSum& self, uint64_t val) { self.m_fee_sum = val; });
  
  // monero_tx
  py::class_<monero::monero_tx, monero::serializable_struct, std::shared_ptr<monero::monero_tx>>(m, "MoneroTx")
    .def(py::init<>())
    .def_property("block", 
      [](const monero::monero_tx& self) { return self.m_block.value_or(nullptr); },
      [](monero::monero_tx& self, std::shared_ptr<monero::monero_block> val) { self.m_block = val; })
    .def_property("hash", 
      [](const monero::monero_tx& self) { return self.m_hash.value_or(""); },
      [](monero::monero_tx& self, std::string val) { self.m_hash = val; })
    .def_property("version", 
      [](const monero::monero_tx& self) { return self.m_version.value_or(0); },
      [](monero::monero_tx& self, uint32_t val) { self.m_version = val; })
    .def_property("is_miner_tx", 
      [](const monero::monero_tx& self) { return self.m_is_miner_tx.value_or(false); },
      [](monero::monero_tx& self, bool val) { self.m_is_miner_tx = val; })
    .def_property("payment_id", 
      [](const monero::monero_tx& self) { return self.m_payment_id.value_or(""); },
      [](monero::monero_tx& self, std::string val) { self.m_payment_id = val; })
    .def_property("fee", 
      [](const monero::monero_tx& self) { return self.m_fee.value_or(0); },
      [](monero::monero_tx& self, uint64_t val) { self.m_fee = val; })
    .def_property("ring_size", 
      [](const monero::monero_tx& self) { return self.m_ring_size.value_or(0); },
      [](monero::monero_tx& self, uint32_t val) { self.m_ring_size = val; })
    .def_property("relay", 
      [](const monero::monero_tx& self) { return self.m_relay.value_or(false); },
      [](monero::monero_tx& self, bool val) { self.m_relay = val; })
    .def_property("is_relayed", 
      [](const monero::monero_tx& self) { return self.m_is_relayed.value_or(false); },
      [](monero::monero_tx& self, bool val) { self.m_is_relayed = val; })
    .def_property("is_confirmed", 
      [](const monero::monero_tx& self) { return self.m_is_confirmed.value_or(false); },
      [](monero::monero_tx& self, bool val) { self.m_is_confirmed = val; })
    .def_property("in_tx_pool", 
      [](const monero::monero_tx& self) { return self.m_in_tx_pool.value_or(false); },
      [](monero::monero_tx& self, bool val) { self.m_in_tx_pool = val; })
    .def_property("num_confirmations", 
      [](const monero::monero_tx& self) { return self.m_num_confirmations.value_or(0); },
      [](monero::monero_tx& self, uint64_t val) { self.m_num_confirmations = val; })
    .def_property("unlock_time", 
      [](const monero::monero_tx& self) { return self.m_unlock_time.value_or(0); },
      [](monero::monero_tx& self, uint64_t val) { self.m_unlock_time = val; })
    .def_property("last_relayed_timestamp", 
      [](const monero::monero_tx& self) { return self.m_last_relayed_timestamp.value_or(0); },
      [](monero::monero_tx& self, uint64_t val) { self.m_last_relayed_timestamp = val; })
    .def_property("received_timestamp", 
      [](const monero::monero_tx& self) { return self.m_received_timestamp.value_or(0); },
      [](monero::monero_tx& self, uint64_t val) { self.m_received_timestamp = val; })
    .def_property("is_double_spend_seen", 
      [](const monero::monero_tx& self) { return self.m_is_double_spend_seen.value_or(false); },
      [](monero::monero_tx& self, bool val) { self.m_is_double_spend_seen = val; })
    .def_property("key", 
      [](const monero::monero_tx& self) { return self.m_key.value_or(""); },
      [](monero::monero_tx& self, std::string val) { self.m_key = val; })
    .def_property("full_hex", 
      [](const monero::monero_tx& self) { return self.m_full_hex.value_or(""); },
      [](monero::monero_tx& self, std::string val) { self.m_full_hex = val; })
    .def_property("pruned_hex", 
      [](const monero::monero_tx& self) { return self.m_pruned_hex.value_or(""); },
      [](monero::monero_tx& self, std::string val) { self.m_pruned_hex = val; })
    .def_property("prunable_hex", 
      [](const monero::monero_tx& self) { return self.m_prunable_hex.value_or(""); },
      [](monero::monero_tx& self, std::string val) { self.m_prunable_hex = val; })
    .def_property("prunable_hash", 
      [](const monero::monero_tx& self) { return self.m_prunable_hash.value_or(""); },
      [](monero::monero_tx& self, std::string val) { self.m_prunable_hash = val; })
    .def_property("size", 
      [](const monero::monero_tx& self) { return self.m_size.value_or(0); },
      [](monero::monero_tx& self, uint64_t val) { self.m_size = val; })
    .def_property("weight", 
      [](const monero::monero_tx& self) { return self.m_weight.value_or(0); },
      [](monero::monero_tx& self, uint64_t val) { self.m_weight = val; })
    .def_readwrite("inputs", &monero::monero_tx::m_inputs)
    .def_readwrite("outputs", &monero::monero_tx::m_outputs)
    .def_readwrite("output_indices", &monero::monero_tx::m_output_indices)
    .def_property("metadata", 
      [](const monero::monero_tx& self) { return self.m_metadata.value_or(""); },
      [](monero::monero_tx& self, std::string val) { self.m_metadata = val; })
    .def_property("common_tx_sets", 
      [](const monero::monero_tx& self) { return self.m_common_tx_sets.value_or(""); },
      [](monero::monero_tx& self, std::string val) { self.m_common_tx_sets = val; })
    .def_readwrite("extra", &monero::monero_tx::m_extra)
    .def_property("rct_signatures", 
      [](const monero::monero_tx& self) { return self.m_rct_signatures.value_or(""); },
      [](monero::monero_tx& self, std::string val) { self.m_rct_signatures = val; })
    .def_property("rct_sig_prunable", 
      [](const monero::monero_tx& self) { return self.m_rct_sig_prunable.value_or(""); },
      [](monero::monero_tx& self, std::string val) { self.m_rct_sig_prunable = val; })
    .def_property("is_kept_by_block", 
      [](const monero::monero_tx& self) { return self.m_is_kept_by_block.value_or(false); },
      [](monero::monero_tx& self, bool val) { self.m_is_kept_by_block = val; })
    .def_property("is_failed", 
      [](const monero::monero_tx& self) { return self.m_is_failed.value_or(false); },
      [](monero::monero_tx& self, bool val) { self.m_is_failed = val; })
    .def_property("last_failed_height", 
      [](const monero::monero_tx& self) { return self.m_last_failed_height.value_or(0); },
      [](monero::monero_tx& self, uint64_t val) { self.m_last_failed_height = val; })
    .def_property("last_failed_hash", 
      [](const monero::monero_tx& self) { return self.m_last_failed_hash.value_or(""); },
      [](monero::monero_tx& self, std::string val) { self.m_last_failed_hash = val; })
    .def_property("max_used_block_height", 
      [](const monero::monero_tx& self) { return self.m_max_used_block_height.value_or(0); },
      [](monero::monero_tx& self, uint64_t val) { self.m_max_used_block_height = val; })
    .def_property("max_used_block_hash", 
      [](const monero::monero_tx& self) { return self.m_max_used_block_hash.value_or(""); },
      [](monero::monero_tx& self, std::string val) { self.m_max_used_block_hash = val; })
    .def_readwrite("signatures", &monero::monero_tx::m_signatures);

  // monero_key_image
  py::class_<monero::monero_key_image, monero::serializable_struct, std::shared_ptr<monero::monero_key_image>>(m, "MoneroKeyImage")
    .def(py::init<>())
    .def_static("deserialize_key_images", [](const std::string& key_images_json) {
      MONERO_CATCH_AND_RETHROW(monero::monero_key_image::deserialize_key_images(key_images_json));
    }, py::arg("key_images_json"))
    .def_property("hex", 
      [](const monero::monero_key_image& self) { return self.m_hex.value_or(""); },
      [](monero::monero_key_image& self, std::string val) { self.m_hex = val; })
    .def_property("signature", 
      [](const monero::monero_key_image& self) { return self.m_signature.value_or(""); },
      [](monero::monero_key_image& self, std::string val) { self.m_signature = val; });

  // monero_output
  py::class_<monero::monero_output, monero::serializable_struct, std::shared_ptr<monero::monero_output>>(m, "MoneroOutput")
    .def(py::init<>())
    .def_readwrite("tx", &monero::monero_output::m_tx)
    .def_property("key_image", 
      [](const monero::monero_output& self) { return self.m_key_image.value_or(nullptr); },
      [](monero::monero_output& self, std::shared_ptr<monero_key_image> val) { self.m_key_image = val; })
    .def_property("amount", 
      [](const monero::monero_output& self) { return self.m_amount.value_or(0); },
      [](monero::monero_output& self, uint64_t val) { self.m_amount = val; })
    .def_property("index", 
      [](const monero::monero_output& self) { return self.m_index.value_or(0); },
      [](monero::monero_output& self, uint64_t val) { self.m_index = val; })
    .def_property("stealth_public_key", 
      [](const monero::monero_output& self) { return self.m_stealth_public_key.value_or(""); },
      [](monero::monero_output& self, std::string val) { self.m_stealth_public_key = val; })
    .def_readwrite("ring_output_indices", &monero::monero_output::m_ring_output_indices);

  // monero_wallet_config
  py::class_<monero::monero_wallet_config, monero::serializable_struct, std::shared_ptr<monero::monero_wallet_config>>(m, "MoneroWalletConfig")
    .def(py::init<>())
    .def(py::init<const monero_wallet_config& config>(), py::arg("config"))
    .def_static("deserialize", [](const std::string& config_json) {
      MONERO_CATCH_AND_RETHROW(monero::monero_wallet_config::deserialize(config_json));
    }, py::arg("config_json"))
    .def_property("path", 
      [](const monero::monero_wallet_config& self) { 
        std::optional<std::string> res;
        if (self.m_path != boost::none) res = self.m_path.get();
        return res; 
      },
      [](monero::monero_wallet_config& self, const std::optional<std::string>& val) { 
        if (val.has_value()) self.m_path = val.value();
        else self.m_path = boost::none;
      }
    )
    .def_property("password", 
      [](const monero::monero_wallet_config& self) { 
        std::optional<std::string> res;
        if (self.m_password != boost::none) res = self.m_password.get();
        return res;
      },
      [](monero::monero_wallet_config& self, const std::optional<std::string>& val) { 
        if (val.has_value()) self.m_password = val.value();
        else self.m_password = boost::none;
      }
    )
    .def_property("network_type", 
      [](const monero::monero_wallet_config& self) {
        std::optional<monero::monero_network_type> res;
        if (self.m_network_type != boost::none) res = self.m_network_type.get();
        return res;
      },
      [](monero::monero_wallet_config& self, std::optional<monero::monero_network_type> nettype) { 
        if (nettype.has_value()) self.m_network_type = nettype.value();
        else self.m_network_type = boost::none;
      }
    )
    .def_property("server", 
      [](const monero::monero_wallet_config& self) {
        std::optional<monero::monero_rpc_connection> res;
        if (self.m_server != boost::none) res = self.m_server.get();        
        return res;
      },
      [](monero::monero_wallet_config& self, std::optional<monero::monero_rpc_connection>& server) {
        if (server.has_value()) self.m_server = server.value(); 
        else self.m_server = boost::none;
      }
    )
    .def_property("seed", 
      [](const monero::monero_wallet_config& self) {
        std::optional<std::string> res;
        if (self.m_seed != boost::none) res = self.m_seed.get();
        return res; 
      },
      [](monero::monero_wallet_config& self, const std::optional<std::string>& val) { 
        if (val.has_value()) self.m_seed = val.value();
        else self.m_seed = boost::none; 
      }
    )
    .def_property("seed_offset", 
      [](const monero::monero_wallet_config& self) {
        std::optional<std::string> res;
        if (self.m_seed_offset != boost::none) res = self.m_seed_offset.get();
        return res; 
      },
      [](monero::monero_wallet_config& self, const std::optional<std::string>& val) { 
        if (val.has_value()) self.m_seed_offset = val.value();
        else self.m_seed_offset = boost::none; 
      })
    .def_property("primary_address", 
      [](const monero::monero_wallet_config& self) {
        std::optional<std::string> res;
        if (self.m_primary_address != boost::none) res = self.m_primary_address.get();
        return res; 
      },
      [](monero::monero_wallet_config& self, const std::optional<std::string>& val) { 
        if (val.has_value()) self.m_primary_address = val.value();
        else self.m_primary_address = boost::none; 
      }
    )
    .def_property("private_view_key", 
      [](const monero::monero_wallet_config& self) {
        std::optional<std::string> res;
        if (self.m_private_view_key != boost::none) res = self.m_private_view_key.get();
        return res; 
      },
      [](monero::monero_wallet_config& self, const std::optional<std::string>& val) { 
        if (val.has_value()) self.m_private_view_key = val.value();
        else self.m_private_view_key = boost::none; 
      }
    )
    .def_property("private_spend_key", 
      [](const monero::monero_wallet_config& self) {
        std::optional<std::string> res;
        if (self.m_private_spend_key != boost::none) res = self.m_private_spend_key.get();
        return res; 
      },
      [](monero::monero_wallet_config& self, const std::optional<std::string>& val) { 
        if (val.has_value()) self.m_private_spend_key = val.value();
        else self.m_private_spend_key = boost::none; 
      }
    )
    .def_property("save_current", 
      [](const monero::monero_wallet_config& self) {
        std::optional<bool> res;
        if (self.m_save_current != boost::none) res = self.m_save_current.get();
        return res; 
      },
      [](monero::monero_wallet_config& self, const std::optional<bool>& val) { 
        if (val.has_value()) self.m_save_current = val.value();
        else self.m_save_current = boost::none; 
      }
    )
    .def_property("language", 
      [](const monero::monero_wallet_config& self) {
        std::optional<std::string> res;
        if (self.m_language != boost::none) res = self.m_language.get();
        return res; 
      },
      [](monero::monero_wallet_config& self, const std::optional<std::string>& val) { 
        if (val.has_value()) self.m_language = val.value();
        else self.m_language = boost::none; 
      }
    )
    .def_property("restore_height", 
      [](const monero::monero_wallet_config& self) {
        std::optional<uint64_t> res;
        if (self.m_restore_height != boost::none) res = self.m_restore_height.get();
        return res; 
      },
      [](monero::monero_wallet_config& self, const std::optional<uint64_t>& val) { 
        if (val.has_value()) self.m_restore_height = val.value();
        else self.m_restore_height = boost::none; 
      }
    )
    .def_property("account_lookahead", 
      [](const monero::monero_wallet_config& self) {
        std::optional<uint64_t> res;
        if (self.m_account_lookahead != boost::none) res = self.m_account_lookahead.get();
        return res; 
      },
      [](monero::monero_wallet_config& self, const std::optional<uint64_t>& val) { 
        if (val.has_value()) self.m_account_lookahead = val.value();
        else self.m_account_lookahead = boost::none; 
      }
    )
    .def_property("subaddress_lookahead", 
      [](const monero::monero_wallet_config& self) {
        std::optional<uint64_t> res;
        if (self.m_subaddress_lookahead != boost::none) res = self.m_subaddress_lookahead.get();
        return res; 
      },
      [](monero::monero_wallet_config& self, const std::optional<uint64_t>& val) { 
        if (val.has_value()) self.m_subaddress_lookahead = val.value();
        else self.m_subaddress_lookahead = boost::none; 
      }
    )
    .def_property("is_multisig", 
      [](const monero::monero_wallet_config& self) {
        std::optional<bool> res;
        if (self.m_is_multisig != boost::none) res = self.m_is_multisig.get();
        return res; 
      },
      [](monero::monero_wallet_config& self, const std::optional<bool>& val) { 
        if (val.has_value()) self.m_is_multisig = val.value();
        else self.m_is_multisig = boost::none; 
      }
    )
    .def("copy", [](monero::monero_wallet_config& self) {
      MONERO_CATCH_AND_RETHROW(self.copy());
    });

  // monero_subaddress
  py::class_<monero::monero_subaddress, monero::serializable_struct, std::shared_ptr<monero::monero_subaddress>>(m, "MoneroSubaddress")
    .def(py::init<>())
    .def_property("account_index", 
      [](const monero::monero_subaddress& self) { return self.m_account_index.value_or(NULL); },
      [](monero::monero_subaddress& self, uint32_t val) { self.m_account_index = val; })
    .def_property("index", 
      [](const monero::monero_subaddress& self) { return self.m_index.value_or(NULL); },
      [](monero::monero_subaddress& self, uint32_t val) { self.m_index = val; })
    .def_property("address", 
      [](const monero::monero_subaddress& self) { return self.m_address.value_or(""); },
      [](monero::monero_subaddress& self, std::string val) { self.m_address = val; })
    .def_property("label", 
      [](const monero::monero_subaddress& self) { return self.m_label.value_or(""); },
      [](monero::monero_subaddress& self, std::string val) { self.m_label = val; })
    .def_property("balance", 
      [](const monero::monero_subaddress& self) { return self.m_balance.value_or(0); },
      [](monero::monero_subaddress& self, uint64_t val) { self.m_balance = val; })
    .def_property("unlocked_balance", 
      [](const monero::monero_subaddress& self) { return self.m_unlocked_balance.value_or(0); },
      [](monero::monero_subaddress& self, uint64_t val) { self.m_unlocked_balance = val; })
    .def_property("num_unspent_outputs", 
      [](const monero::monero_subaddress& self) { return self.m_num_unspent_outputs.value_or(0); },
      [](monero::monero_subaddress& self, uint64_t val) { self.m_num_unspent_outputs = val; })
    .def_property("is_used", 
      [](const monero::monero_subaddress& self) { return self.m_is_used.value_or(NULL); },
      [](monero::monero_subaddress& self, bool val) { self.m_is_used = val; })
    .def_property("num_blocks_to_unlock", 
      [](const monero::monero_subaddress& self) { return self.m_num_blocks_to_unlock.value_or(0); },
      [](monero::monero_subaddress& self, uint64_t val) { self.m_num_blocks_to_unlock = val; });

  // monero_sync_result
  py::class_<monero::monero_sync_result, monero::serializable_struct, std::shared_ptr<monero::monero_sync_result>>(m, "MoneroSyncResult")
    .def(py::init<>())
    .def_readwrite("num_blocks_fetched", &monero::monero_sync_result::m_num_blocks_fetched)
    .def_readwrite("received_money", &monero::monero_sync_result::m_received_money);

  // monero_account
  py::class_<monero::monero_account, monero::serializable_struct, std::shared_ptr<monero::monero_account>>(m, "MoneroAccount")
    .def(py::init<>())
    .def_property("index", 
      [](const monero::monero_account& self) { return self.m_index.value_or(NULL); },
      [](monero::monero_account& self, uint32_t val) { self.m_index = val; })
    .def_property("primary_address", 
      [](const monero::monero_account& self) { return self.m_primary_address.value_or(""); },
      [](monero::monero_account& self, std::string val) { self.m_primary_address = val; })
    .def_property("balance", 
      [](const monero::monero_account& self) { return self.m_balance.value_or(0); },
      [](monero::monero_account& self, uint64_t val) { self.m_balance = val; })
    .def_property("unlocked_balance", 
      [](const monero::monero_account& self) { return self.m_unlocked_balance.value_or(0); },
      [](monero::monero_account& self, uint64_t val) { self.m_unlocked_balance = val; })
    .def_property("tag", 
      [](const monero::monero_account& self) { return self.m_tag.value_or(""); },
      [](monero::monero_account& self, std::string val) { self.m_tag = val; })
    .def_readwrite("subaddresses", &monero::monero_account::m_subaddresses);

  // monero_account_tag
  py::class_<PyMoneroAccountTag, std::shared_ptr<PyMoneroAccountTag>>(m, "MoneroAccountTag")
    .def(py::init<std::string&, std::string&>(), py::arg("tag"), py::arg("label"))
    .def(py::init<std::string&, std::string&, std::vector<uint32_t>>(), py::arg("tag"), py::arg("label"), py::arg("account_indices"))
    .def_readwrite("tag", &PyMoneroAccountTag::m_tag)
    .def_readwrite("label", &PyMoneroAccountTag::m_label)
    .def_readwrite("account_indices", &PyMoneroAccountTag::m_account_indices);

  // monero_destination
  py::class_<monero::monero_destination, std::shared_ptr<monero::monero_destination>>(m, "MoneroDestination")
    .def(py::init<>())
    .def_property("address", 
      [](const monero::monero_destination& self) { return self.m_address.value_or(""); },
      [](monero::monero_destination& self, std::string val) { self.m_address = val; })
    .def_property("amount", 
      [](const monero::monero_destination& self) { return self.m_amount.value_or(0); },
      [](monero::monero_destination& self, uint64_t val) { self.m_amount = val; });

  // monero_transfer
  py::class_<monero::monero_transfer, PyMoneroTransfer, std::shared_ptr<monero::monero_transfer>>(m, "MoneroTransfer")
    .def(py::init<>())
    .def_readwrite("tx", &monero::monero_transfer::m_tx)
    .def_property("account_index", 
      [](const monero::monero_transfer& self) { return self.m_account_index.value_or(NULL); },
      [](monero::monero_transfer& self, uint32_t val) { self.m_account_index = val; })
    .def_property("amount", 
      [](const monero::monero_transfer& self) { return self.m_amount.value_or(0); },
      [](monero::monero_transfer& self, uint64_t val) { self.m_amount = val; })
    .def("is_incoming", [](monero::monero_transfer& self) {
      MONERO_CATCH_AND_RETHROW(self.is_incoming().value_or(NULL));
    })
    .def("is_outgoing", [](monero::monero_transfer& self) {
      MONERO_CATCH_AND_RETHROW(self.is_outgoing().value_or(NULL));
    });
  
  // monero_incoming_transfer
  py::class_<monero::monero_incoming_transfer, monero::monero_transfer, std::shared_ptr<monero::monero_incoming_transfer>>(m, "MoneroIncomingTransfer")
    .def(py::init<>())
    .def_property("address", 
      [](const monero::monero_incoming_transfer& self) { return self.m_address.value_or(""); },
      [](monero::monero_incoming_transfer& self, std::string val) { self.m_address = val; })
    .def_property("subaddress_index", 
      [](const monero::monero_incoming_transfer& self) { return self.m_subaddress_index.value_or(NULL); },
      [](monero::monero_incoming_transfer& self, uint32_t val) { self.m_subaddress_index = val; })
    .def_property("num_suggested_confirmations", 
      [](const monero::monero_incoming_transfer& self) { return self.m_num_suggested_confirmations.value_or(NULL); },
      [](monero::monero_incoming_transfer& self, uint64_t val) { self.m_num_suggested_confirmations = val; });

  // monero_outgoing_transfer
  py::class_<monero::monero_outgoing_transfer, monero::monero_transfer, std::shared_ptr<monero::monero_outgoing_transfer>>(m, "MoneroOutgoingTransfer")
    .def(py::init<>())
    .def_readwrite("subaddress_indices", &monero::monero_outgoing_transfer::m_subaddress_indices)
    .def_readwrite("addresses", &monero::monero_outgoing_transfer::m_addresses)
    .def_readwrite("destinations", &monero::monero_outgoing_transfer::m_destinations);

  // monero_transfer_query
  py::class_<monero::monero_transfer_query, monero::monero_transfer, std::shared_ptr<monero_transfer_query>>(m, "MoneroTransferQuery")
    .def(py::init<>())
    .def_static("deserialize_from_block", [](const std::string& transfer_query_json) {
      MONERO_CATCH_AND_RETHROW(monero::monero_transfer_query::deserialize_from_block(transfer_query_json));
    }, py::arg("transfer_query_json"))
    .def_property("incoming", 
      [](const monero::monero_transfer_query& self) { return self.m_is_incoming.value_or(false); },
      [](monero::monero_transfer_query& self, bool val) { self.m_is_incoming = val; })
    .def_property("address", 
      [](const monero::monero_transfer_query& self) { return self.m_address.value_or(""); },
      [](monero::monero_transfer_query& self, std::string& val) { self.m_address = val; })
    .def_readwrite("addresses", &monero::monero_transfer_query::m_addresses)
    .def_property("subaddress_index",
      [](const monero::monero_transfer_query& self) { return self.m_subaddress_index.value_or(NULL); },
      [](monero::monero_transfer_query& self, uint32_t val) { self.m_subaddress_index = val; })
    .def_readwrite("subaddress_indices", &monero::monero_transfer_query::m_subaddress_indices)
    .def_readwrite("destinations", &monero::monero_transfer_query::m_destinations)
    .def_property("has_destinations", 
      [](const monero::monero_transfer_query& self) { return self.m_has_destinations.value_or(false); },
      [](monero::monero_transfer_query& self, bool val) { self.m_has_destinations = val; })
    .def_property("tx_query", 
      [](const monero::monero_transfer_query& self) { return self.m_tx_query.value_or(nullptr); },
      [](monero::monero_transfer_query& self, std::shared_ptr<monero_tx_query> val) { self.m_tx_query = val; })
    .def("meets_criteria", [](monero::monero_transfer_query& self, monero_transfer_query* transfer, bool query_parent) {
      MONERO_CATCH_AND_RETHROW(self.meets_criteria(transfer, query_parent));
    }, py::arg("transfer"), py::arg("query_parent") = true);

  // monero_output_wallet
  py::class_<monero::monero_output_wallet, monero::monero_output, std::shared_ptr<monero::monero_output_wallet>>(m, "MoneroOutputWallet")
    .def(py::init<>())
    .def_property("account_index", 
      [](const monero::monero_output_wallet& self) { return self.m_account_index.value_or(0); },
      [](monero::monero_output_wallet& self, uint32_t val) { self.m_account_index = val; })
    .def_property("subaddress_index", 
      [](const monero::monero_output_wallet& self) { return self.m_subaddress_index.value_or(0); },
      [](monero::monero_output_wallet& self, uint32_t val) { self.m_subaddress_index = val; })
    .def_property("is_spent", 
      [](const monero::monero_output_wallet& self) { return self.m_is_spent.value_or(false); },
      [](monero::monero_output_wallet& self, bool val) { self.m_is_spent = val; })
    .def_property("is_frozen", 
      [](const monero::monero_output_wallet& self) { return self.m_is_frozen.value_or(false); },
      [](monero::monero_output_wallet& self, bool val) { self.m_is_frozen = val; });

  // monero_output_query
  py::class_<monero::monero_output_query, monero::monero_output_wallet, std::shared_ptr<monero::monero_output_query>>(m, "MoneroOutputQuery")
    .def(py::init<>())
    .def_static("deserialize_from_block", [](const std::string& output_query_json) {
      MONERO_CATCH_AND_RETHROW(monero::monero_output_query::deserialize_from_block(output_query_json));
    }, py::arg("output_query_json"))
    .def_readwrite("subaddress_indices", &monero::monero_output_query::m_subaddress_indices)
    .def_property("min_amount", 
      [](const monero::monero_output_query& self) { return self.m_min_amount.value_or(0); },
      [](monero::monero_output_query& self, uint64_t val) { self.m_min_amount = val; })
    .def_property("max_amount", 
      [](const monero::monero_output_query& self) { return self.m_max_amount.value_or(0); },
      [](monero::monero_output_query& self, uint64_t val) { self.m_max_amount = val; })
    .def_property("min_amount", 
      [](const monero::monero_output_query& self) { return self.m_min_amount.value_or(0); },
      [](monero::monero_output_query& self, uint64_t val) { self.m_min_amount = val; })
    .def_property("tx_query", 
      [](const monero::monero_output_query& self) { return self.m_tx_query.value_or(nullptr); },
      [](monero::monero_output_query& self, std::shared_ptr<monero::monero_tx_query> val) { self.m_tx_query = val; })
    .def("meets_criteria", [](monero::monero_output_query& self, monero_output_wallet* output, bool query_parent) {
      MONERO_CATCH_AND_RETHROW(self.meets_criteria(output, query_parent));
    }, py::arg("output"), py::arg("query_parent") = true);

  // monero_tx_wallet
  py::class_<monero::monero_tx_wallet, monero::monero_tx, std::shared_ptr<monero::monero_tx_wallet>>(m, "MoneroTxWallet")
    .def(py::init<>())
    .def_property("tx_set", 
      [](const monero::monero_tx_wallet& self) { return self.m_tx_set.value_or(nullptr); },
      [](monero::monero_tx_wallet& self, std::shared_ptr<monero_tx_set> val) { self.m_tx_set = val; })
    .def_property("is_incoming", 
      [](const monero::monero_tx_wallet& self) { return self.m_is_incoming.value_or(false); },
      [](monero::monero_tx_wallet& self, bool val) { self.m_is_incoming = val; })
    .def_property("is_outgoing", 
      [](const monero::monero_tx_wallet& self) { return self.m_is_outgoing.value_or(false); },
      [](monero::monero_tx_wallet& self, bool val) { self.m_is_outgoing = val; })
    .def_readwrite("incoming_transfers", &monero::monero_tx_wallet::m_incoming_transfers)
    .def_readwrite("outgoing_transfer", &monero::monero_tx_wallet::m_outgoing_transfer)
    .def_property("outgoing_transfer", 
      [](const monero::monero_tx_wallet& self) { return self.m_outgoing_transfer.value_or(nullptr); },
      [](monero::monero_tx_wallet& self, std::shared_ptr<monero_outgoing_transfer> val) { self.m_outgoing_transfer = val; })
    .def_property("note", 
      [](const monero::monero_tx_wallet& self) { return self.m_note.value_or(""); },
      [](monero::monero_tx_wallet& self, std::string& val) { self.m_note = val; })
    .def_property("is_locked", 
      [](const monero::monero_tx_wallet& self) { return self.m_is_locked.value_or(false); },
      [](monero::monero_tx_wallet& self, bool val) { self.m_is_locked = val; })
    .def_property("input_sum", 
      [](const monero::monero_tx_wallet& self) { return self.m_input_sum.value_or(0); },
      [](monero::monero_tx_wallet& self, uint64_t val) { self.m_input_sum = val; })
    .def_property("output_sum", 
      [](const monero::monero_tx_wallet& self) { return self.m_output_sum.value_or(0); },
      [](monero::monero_tx_wallet& self, uint64_t val) { self.m_output_sum = val; })
    .def_property("change_address", 
      [](const monero::monero_tx_wallet& self) { return self.m_change_address.value_or(""); },
      [](monero::monero_tx_wallet& self, std::string& val) { self.m_change_address = val; })
    .def_property("change_amount", 
      [](const monero::monero_tx_wallet& self) { return self.m_change_amount.value_or(0); },
      [](monero::monero_tx_wallet& self, uint64_t val) { self.m_change_amount = val; })
    .def_property("num_dummy_outputs", 
      [](const monero::monero_tx_wallet& self) { return self.m_num_dummy_outputs.value_or(0); },
      [](monero::monero_tx_wallet& self, uint32_t val) { self.m_num_dummy_outputs = val; })
    .def_property("extra_hex", 
      [](const monero::monero_tx_wallet& self) { return self.m_extra_hex.value_or(""); },
      [](monero::monero_tx_wallet& self, std::string& val) { self.m_extra_hex = val; })
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
    }, py::arg("query"));

  // monero_tx_query
  py::class_<monero::monero_tx_query, monero::monero_tx_wallet, std::shared_ptr<monero::monero_tx_query>>(m, "MoneroTxQuery")
    .def(py::init<>())
    .def_static("deserialize_from_block", [](const std::string& tx_query_json) {
      MONERO_CATCH_AND_RETHROW(monero::monero_tx_query::deserialize_from_block(tx_query_json));
    }, py::arg("tx_query_json"))
    .def_property("is_outgoing", 
      [](const monero::monero_tx_query& self) { return self.m_is_outgoing.value_or(false); },
      [](monero::monero_tx_query& self, bool val) { self.m_is_outgoing = val; })
    .def_property("is_incoming", 
      [](const monero::monero_tx_query& self) { return self.m_is_incoming.value_or(false); },
      [](monero::monero_tx_query& self, bool val) { self.m_is_incoming = val; })
    .def_readwrite("hashes", &monero::monero_tx_query::m_hashes)
    .def_property("has_payment_id", 
      [](const monero::monero_tx_query& self) { return self.m_has_payment_id.value_or(false); },
      [](monero::monero_tx_query& self, bool val) { self.m_has_payment_id = val; })
    .def_readwrite("payment_ids", &monero::monero_tx_query::m_payment_ids)
    .def_property("height", 
      [](const monero::monero_tx_query& self) { return self.m_height.value_or(0); },
      [](monero::monero_tx_query& self, uint64_t val) { self.m_height = val; })
    .def_property("min_height", 
      [](const monero::monero_tx_query& self) { return self.m_min_height.value_or(0); },
      [](monero::monero_tx_query& self, uint64_t val) { self.m_min_height = val; })
    .def_property("max_height", 
      [](const monero::monero_tx_query& self) { return self.m_max_height.value_or(0); },
      [](monero::monero_tx_query& self, uint64_t val) { self.m_max_height = val; })
    .def_property("min_height", 
      [](const monero::monero_tx_query& self) { return self.m_min_height.value_or(0); },
      [](monero::monero_tx_query& self, uint64_t val) { self.m_min_height = val; })
    .def_property("max_height", 
      [](const monero::monero_tx_query& self) { return self.m_max_height.value_or(0); },
      [](monero::monero_tx_query& self, uint64_t val) { self.m_max_height = val; })
    .def_property("include_outputs", 
      [](const monero::monero_tx_query& self) { return self.m_include_outputs.value_or(0); },
      [](monero::monero_tx_query& self, uint64_t val) { self.m_include_outputs = val; })
    .def_property("transfer_query", 
      [](const monero::monero_tx_query& self) { return self.m_transfer_query.value_or(nullptr); },
      [](monero::monero_tx_query& self, std::shared_ptr<monero_transfer_query> val) { self.m_transfer_query = val; })
    .def_property("input_query", 
      [](const monero::monero_tx_query& self) { return self.m_input_query.value_or(nullptr); },
      [](monero::monero_tx_query& self, std::shared_ptr<monero_output_query> val) { self.m_input_query = val; })
    .def_property("output_query", 
      [](const monero::monero_tx_query& self) { return self.m_output_query.value_or(nullptr); },
      [](monero::monero_tx_query& self, std::shared_ptr<monero_output_query> val) { self.m_output_query = val; })
    .def("meets_criteria", [](monero::monero_tx_query& self, monero_tx_wallet* tx, bool query_children) {
      MONERO_CATCH_AND_RETHROW(self.meets_criteria(tx, query_children));
    }, py::arg("tx"), py::arg("query_children") = false);

  // monero_tx_set
  py::class_<monero::monero_tx_set, monero::serializable_struct, std::shared_ptr<monero::monero_tx_set>>(m, "MoneroTxSet")
    .def(py::init<>())
    .def_static("deserialize", [](const std::string& tx_set_json) {
      MONERO_CATCH_AND_RETHROW(monero::monero_tx_set::deserialize(tx_set_json));
    }, py::arg("tx_set_json"))
    .def_readwrite("txs", &monero::monero_tx_set::m_txs)
    .def_property("signed_tx_hex", 
      [](const monero::monero_tx_set& self) { return self.m_signed_tx_hex.value_or(""); },
      [](monero::monero_tx_set& self, std::string val) { self.m_signed_tx_hex = val; })
    .def_property("unsigned_tx_hex", 
      [](const monero::monero_tx_set& self) { return self.m_unsigned_tx_hex.value_or(""); },
      [](monero::monero_tx_set& self, std::string val) { self.m_unsigned_tx_hex = val; })
    .def_property("multisig_tx_hex", 
      [](const monero::monero_tx_set& self) { return self.m_multisig_tx_hex.value_or(""); },
      [](monero::monero_tx_set& self, std::string val) { self.m_multisig_tx_hex = val; });

  // monero_integrated_address
  py::class_<monero::monero_integrated_address,  monero::serializable_struct, std::shared_ptr<monero::monero_integrated_address>>(m, "MoneroIntegratedAddress")
    .def(py::init<>())
    .def_readwrite("standard_address", &monero::monero_integrated_address::m_standard_address)
    .def_readwrite("payment_id", &monero::monero_integrated_address::m_payment_id)
    .def_readwrite("integrated_address", &monero::monero_integrated_address::m_integrated_address);

  // monero_decoded_address
  py::class_<PyMoneroDecodedAddress, std::shared_ptr<PyMoneroDecodedAddress>>(m, "MoneroDecodedAddress")
    .def(py::init<std::string&, PyMoneroAddressType, monero::monero_network_type>(), py::arg("address"), py::arg("address_type"), py::arg("network_type"))
    .def_readwrite("address", &PyMoneroDecodedAddress::m_address)
    .def_readwrite("address_type", &PyMoneroDecodedAddress::m_address_type)
    .def_readwrite("network_type", &PyMoneroDecodedAddress::m_network_type);

  // enum monero_tx_priority
  py::enum_<monero::monero_tx_priority>(m, "MoneroTxPriority")
    .value("DEFAULT", monero::monero_tx_priority::DEFAULT)
    .value("UNIMPORTANT", monero::monero_tx_priority::UNIMPORTANT)
    .value("NORMAL", monero::monero_tx_priority::NORMAL)
    .value("ELEVATED", monero::monero_tx_priority::ELEVATED);

  // monero_tx_config
  py::class_<monero::monero_tx_config, monero::serializable_struct, std::shared_ptr<monero::monero_tx_config>>(m, "MoneroTxConfig")
    .def(py::init<>())
    .def(py::init<monero::monero_tx_config&>(), py::arg("config"))
    .def_static("deserialize", [](const std::string& config_json) {
      MONERO_CATCH_AND_RETHROW(monero::monero_tx_config::deserialize(config_json));
    }, py::arg("config_json"))
    .def("copy", [](monero::monero_tx_config& self) {
      MONERO_CATCH_AND_RETHROW(self.copy());
    })
    .def("get_normalized_destinations", [](monero::monero_tx_config& self) {
      MONERO_CATCH_AND_RETHROW(self.get_normalized_destinations());
    })
    .def_property("address", 
      [](const monero::monero_tx_config& self) { return self.m_address.value_or(""); },
      [](monero::monero_tx_config& self, std::string val) { self.m_address = val; })
    .def_property("amount", 
      [](const monero::monero_tx_config& self) { return self.m_amount.value_or(0); },
      [](monero::monero_tx_config& self, uint64_t val) { self.m_amount = val; })
    .def_readwrite("destinations", &monero::monero_tx_config::m_destinations)
    .def_readwrite("subtract_fee_from", &monero::monero_tx_config::m_subtract_fee_from)
    .def_property("payment_id", 
      [](const monero::monero_tx_config& self) { return self.m_payment_id.value_or(""); },
      [](monero::monero_tx_config& self, std::string val) { self.m_payment_id = val; })
    .def_property("priority", 
      [](const monero::monero_tx_config& self) { return self.m_priority.value_or(monero_tx_priority::NORMAL); },
      [](monero::monero_tx_config& self, monero::monero_tx_priority val) { self.m_priority = val; })
    .def_property("ring_size", 
      [](const monero::monero_tx_config& self) { return self.m_ring_size.value_or(0); },
      [](monero::monero_tx_config& self, uint32_t val) { self.m_ring_size = val; })
    .def_property("fee", 
      [](const monero::monero_tx_config& self) { return self.m_fee.value_or(0); },
      [](monero::monero_tx_config& self, uint64_t val) { self.m_fee = val; })
    .def_property("account_index", 
      [](const monero::monero_tx_config& self) { return self.m_account_index.value_or(0); },
      [](monero::monero_tx_config& self, uint32_t val) { self.m_account_index = val; })
    .def_readwrite("subaddress_indices", &monero::monero_tx_config::m_subaddress_indices)
    .def_property("can_split", 
      [](const monero::monero_tx_config& self) { return self.m_can_split.value_or(false); },
      [](monero::monero_tx_config& self, bool val) { self.m_can_split = val; })
    .def_property("relay", 
      [](const monero::monero_tx_config& self) { return self.m_relay.value_or(false); },
      [](monero::monero_tx_config& self, bool val) { self.m_relay = val; })
    .def_property("note", 
      [](const monero::monero_tx_config& self) { return self.m_note.value_or(""); },
      [](monero::monero_tx_config& self, std::string val) { self.m_note = val; })
    .def_property("recipient_name", 
      [](const monero::monero_tx_config& self) { return self.m_recipient_name.value_or(""); },
      [](monero::monero_tx_config& self, std::string val) { self.m_recipient_name = val; })
    .def_property("below_amount", 
      [](const monero::monero_tx_config& self) { return self.m_below_amount.value_or(0); },
      [](monero::monero_tx_config& self, uint64_t val) { self.m_below_amount = val; })
    .def_property("sweep_each_subaddress", 
      [](const monero::monero_tx_config& self) { return self.m_sweep_each_subaddress.value_or(false); },
      [](monero::monero_tx_config& self, bool val) { self.m_sweep_each_subaddress = val; })
    .def_property("key_image", 
      [](const monero::monero_tx_config& self) { return self.m_key_image.value_or(""); },
      [](monero::monero_tx_config& self, std::string val) { self.m_key_image = val; });

  // monero_key_image_import_result
  py::class_<monero::monero_key_image_import_result, monero::serializable_struct, std::shared_ptr<monero::monero_key_image_import_result>>(m, "MoneroKeyImageImportResult")
    .def(py::init<>())
    .def_property("height", 
      [](const monero::monero_key_image_import_result& self) { return self.m_height.value_or(NULL); },
      [](monero::monero_key_image_import_result& self, uint64_t val) { self.m_height = val; })
    .def_property("spent_amount", 
      [](const monero::monero_key_image_import_result& self) { return self.m_spent_amount.value_or(NULL); },
      [](monero::monero_key_image_import_result& self, uint64_t val) { self.m_spent_amount = val; })
    .def_property("unspent_amount", 
      [](const monero::monero_key_image_import_result& self) { return self.m_unspent_amount.value_or(NULL); },
      [](monero::monero_key_image_import_result& self, uint64_t val) { self.m_unspent_amount = val; });

  // enum monero_message_signature_type
  py::enum_<monero::monero_message_signature_type>(m, "MoneroMessageSignatureType")
    .value("SIGN_WITH_SPEND_KEY", monero::monero_message_signature_type::SIGN_WITH_SPEND_KEY)
    .value("SIGN_WITH_VIEW_KEY", monero::monero_message_signature_type::SIGN_WITH_VIEW_KEY);

  // monero_message_signature_result
  py::class_<monero::monero_message_signature_result,  monero::serializable_struct, std::shared_ptr<monero::monero_message_signature_result>>(m, "MoneroMessageSignatureResult")
    .def(py::init<>())
    .def_readwrite("is_good", &monero::monero_message_signature_result::m_is_good)
    .def_readwrite("version", &monero::monero_message_signature_result::m_version)
    .def_readwrite("is_old", &monero::monero_message_signature_result::m_is_old)
    .def_readwrite("signature_type", &monero::monero_message_signature_result::m_signature_type);

  // monero_check
  py::class_<monero::monero_check,  monero::serializable_struct, std::shared_ptr<monero::monero_check>>(m, "MoneroCheck")
    .def(py::init<>())
    .def_readwrite("is_good", &monero::monero_check::m_is_good);
  
  // monero_check_tx
  py::class_<monero::monero_check_tx, monero::monero_check, std::shared_ptr<monero::monero_check_tx>>(m, "MoneroCheckTx")
    .def(py::init<>())
    .def_property("in_tx_pool", 
      [](const monero::monero_check_tx& self) { return self.m_in_tx_pool.value_or(false); },
      [](monero::monero_check_tx& self, bool val) { self.m_in_tx_pool = val; })
    .def_property("num_confirmations", 
      [](const monero::monero_check_tx& self) { return self.m_num_confirmations.value_or(false); },
      [](monero::monero_check_tx& self, uint64_t val) { self.m_num_confirmations = val; })
    .def_property("received_amount", 
      [](const monero::monero_check_tx& self) { return self.m_received_amount.value_or(0); },
      [](monero::monero_check_tx& self, uint64_t val) { self.m_received_amount = val; });
  
  // monero_check_reserve
  py::class_<monero::monero_check_reserve, monero::monero_check, std::shared_ptr<monero::monero_check_reserve>>(m, "MoneroCheckReserve")
    .def(py::init<>())
    .def_property("total_amount", 
      [](const monero::monero_check_reserve& self) { return self.m_total_amount.value_or(false); },
      [](monero::monero_check_reserve& self, uint64_t val) { self.m_total_amount = val; })
    .def_property("unconfirmed_spent_amount", 
      [](const monero::monero_check_reserve& self) { return self.m_unconfirmed_spent_amount.value_or(false); },
      [](monero::monero_check_reserve& self, uint64_t val) { self.m_unconfirmed_spent_amount = val; });
  
  // monero_multisig_info
  py::class_<monero::monero_multisig_info, std::shared_ptr<monero_multisig_info>>(m, "MoneroMultisigInfo")
    .def(py::init<>())
    .def_readwrite("is_multisig", &monero::monero_multisig_info::m_is_multisig)
    .def_readwrite("is_ready", &monero::monero_multisig_info::m_is_ready)
    .def_readwrite("threshold", &monero::monero_multisig_info::m_threshold)
    .def_readwrite("num_participants", &monero::monero_multisig_info::m_num_participants);
  
  // monero_multisig_init_result
  py::class_<monero::monero_multisig_init_result, std::shared_ptr<monero_multisig_init_result>>(m, "MoneroMultisigInitResult")
    .def(py::init<>())
    .def_property("address", 
      [](const monero::monero_multisig_init_result& self) { return self.m_address.value_or(""); },
      [](monero::monero_multisig_init_result& self, std::string val) { self.m_address = val; })
    .def_property("multisig_hex", 
      [](const monero::monero_multisig_init_result& self) { return self.m_multisig_hex.value_or(""); },
      [](monero::monero_multisig_init_result& self, std::string val) { self.m_multisig_hex = val; });
    
  // monero_multisig_sign_result
  py::class_<monero::monero_multisig_sign_result, std::shared_ptr<monero::monero_multisig_sign_result>>(m, "MoneroMultisigSignResult")
    .def(py::init<>())
    .def_property("signed_multisig_tx_hex", 
      [](const monero::monero_multisig_sign_result& self) { return self.m_signed_multisig_tx_hex.value_or(""); },
      [](monero::monero_multisig_sign_result& self, std::string val) { self.m_signed_multisig_tx_hex = val; })
    .def_readwrite("tx_hashes", &monero::monero_multisig_sign_result::m_tx_hashes);

  // monero_address_book_entry
  py::class_<monero::monero_address_book_entry, std::shared_ptr<monero::monero_address_book_entry>>(m, "MoneroAddressBookEntry")
    .def(py::init<>())
    .def_property("index", 
      [](const monero::monero_address_book_entry& self) { return self.m_index.value_or(NULL); },
      [](monero::monero_address_book_entry& self, uint64_t val) { self.m_index = val; })
    .def_property("address", 
      [](const monero::monero_address_book_entry& self) { return self.m_address.value_or(""); },
      [](monero::monero_address_book_entry& self, std::string val) { self.m_address = val; })
    .def_property("description", 
      [](const monero::monero_address_book_entry& self) { return self.m_description.value_or(""); },
      [](monero::monero_address_book_entry& self, std::string val) { self.m_description = val; })
    .def_property("payment_id", 
      [](const monero::monero_address_book_entry& self) { return self.m_payment_id.value_or(""); },
      [](monero::monero_address_book_entry& self, std::string val) { self.m_payment_id = val; });
  
  // monero_wallet_listener
  py::class_<monero::monero_wallet_listener, std::shared_ptr<monero::monero_wallet_listener>>(m, "MoneroWalletListener")
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
  py::class_<PyMoneroDaemonListener, std::shared_ptr<PyMoneroDaemonListener>>(m, "MoneroDaemonListener")
    .def_property("last_header", 
      [](const PyMoneroDaemonListener& self) { 
        return self.m_last_header.get_ptr();
       },
      [](PyMoneroDaemonListener& self, const monero::monero_block_header val) { self.m_last_header = val; })
    .def("on_new_block", [](PyMoneroDaemonListener& self, const monero::monero_block_header& header) {
      MONERO_CATCH_AND_RETHROW(self.on_new_block(header));
    }, py::arg("header"));

  // monero_daemon
  py::class_<PyMoneroDaemon, std::shared_ptr<PyMoneroDaemon>>(m, "MoneroDaemon")
    .def("add_listener", [](PyMoneroDaemon& self, std::shared_ptr<PyMoneroDaemonListener> listener) {
      MONERO_CATCH_AND_RETHROW(self.add_listener(listener));
    }, py::arg("listener"))
    .def("remove_listener", [](PyMoneroDaemon& self, std::shared_ptr<PyMoneroDaemonListener> listener) {
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
    .def("set_peer_bans", [](PyMoneroDaemon& self, std::vector<PyMoneroBan> bans) {
      MONERO_CATCH_AND_RETHROW(self.set_peer_bans(bans));
    }, py::arg("bans"))
    .def("set_peer_ban", [](PyMoneroDaemon& self, PyMoneroBan& ban) {
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

  // monero_daemon_rpc
  py::class_<PyMoneroDaemonRpc, PyMoneroDaemon, std::shared_ptr<PyMoneroDaemonRpc>>(m, "MoneroDaemonRpc")
    .def(py::init<>())
    .def(py::init<std::shared_ptr<PyMoneroRpcConnection>>(), py::arg("rpc"))
    .def(py::init<std::string&, std::string&, std::string&>(), py::arg("uri"), py::arg("username") = "", py::arg("password") = "")
    .def("get_rpc_connection", [](const PyMoneroDaemonRpc& self) {
      MONERO_CATCH_AND_RETHROW(self.get_rpc_connection());
    });

  // monero_wallet
  py::class_<monero::monero_wallet, PyMoneroWallet, std::shared_ptr<monero::monero_wallet>>(m, "MoneroWallet")
    .def(py::init<>())
    .def("is_view_only", [](monero::monero_wallet& self) {
      MONERO_CATCH_AND_RETHROW(self.is_view_only());
    })
    .def("set_daemon_connection", [](monero::monero_wallet& self, const monero::monero_rpc_connection& connection) {
      MONERO_CATCH_AND_RETHROW(self.set_daemon_connection(connection));
    }, py::arg("connection"))
     .def("set_daemon_connection", [](monero::monero_wallet& self, std::string uri, std::string username, std::string password) {
      MONERO_CATCH_AND_RETHROW(self.set_daemon_connection(uri, username, password));
    }, py::arg("uri") = "", py::arg("username") = "", py::arg("password") = "")       
    .def("set_daemon_proxy", [](monero::monero_wallet& self, const std::string& uri) {
      MONERO_CATCH_AND_RETHROW(self.set_daemon_proxy(uri));
    }, py::arg("uri") = "")
    .def("get_daemon_connection", [](monero::monero_wallet& self) {
      MONERO_CATCH_AND_RETHROW(self.get_daemon_connection().value_or(monero::monero_rpc_connection()));
    })
    .def("is_connected_to_daemon", [](monero::monero_wallet& self) {
      MONERO_CATCH_AND_RETHROW(self.is_connected_to_daemon());
    })
    .def("is_daemon_trusted", [](monero::monero_wallet& self) {
      MONERO_CATCH_AND_RETHROW(self.is_daemon_trusted());
    })
    .def("is_synced", [](monero::monero_wallet& self) {
      MONERO_CATCH_AND_RETHROW(self.is_synced());
    })
    .def("get_version", [](monero::monero_wallet& self) {
      MONERO_CATCH_AND_RETHROW(self.get_version());
    })
    .def("get_path", [](monero::monero_wallet& self) {
      MONERO_CATCH_AND_RETHROW(self.get_path());
    })
    .def("get_network_type", [](monero::monero_wallet& self) {
      MONERO_CATCH_AND_RETHROW(self.get_network_type());
    })
    .def("get_seed", [](monero::monero_wallet& self) {
      MONERO_CATCH_AND_RETHROW(self.get_seed());
    })
    .def("get_seed_language", [](monero::monero_wallet& self) {
      MONERO_CATCH_AND_RETHROW(self.get_seed_language());
    })
    .def("get_public_view_key", [](monero::monero_wallet& self) {
      MONERO_CATCH_AND_RETHROW(self.get_public_view_key());
    })
    .def("get_private_view_key", [](monero::monero_wallet& self) {
      MONERO_CATCH_AND_RETHROW(self.get_private_view_key());
    })
    .def("get_public_spend_key", [](monero::monero_wallet& self) {
      MONERO_CATCH_AND_RETHROW(self.get_public_spend_key());
    })
    .def("get_private_spend_key", [](monero::monero_wallet& self) {
      MONERO_CATCH_AND_RETHROW(self.get_private_spend_key());
    })
    .def("get_primary_address", [](monero::monero_wallet& self) {
      MONERO_CATCH_AND_RETHROW(self.get_primary_address());
    })
    .def("get_address", [](monero::monero_wallet& self, uint32_t account_idx, uint32_t subaddress_idx) {
      MONERO_CATCH_AND_RETHROW(self.get_address(account_idx, subaddress_idx));
    }, py::arg("account_idx"), py::arg("subaddress_idx"))
    .def("get_address_index", [](monero::monero_wallet& self, const std::string& address) {
      MONERO_CATCH_AND_RETHROW(self.get_address_index(address));
    }, py::arg("address"))
    .def("get_integrated_address", [](monero::monero_wallet& self, const std::string& standard_address, const std::string& payment_id) {
      MONERO_CATCH_AND_RETHROW(self.get_integrated_address(standard_address, payment_id));
    }, py::arg("standard_address") = "", py::arg("payment_id") = "")
    .def("decode_integrated_address", [](monero::monero_wallet& self, const std::string& integrated_address) {
      MONERO_CATCH_AND_RETHROW(self.decode_integrated_address(integrated_address));
    }, py::arg("integrated_address"))
    .def("get_height", [](monero::monero_wallet& self) {
      MONERO_CATCH_AND_RETHROW(self.get_height());
    })
    .def("get_restore_height", [](monero::monero_wallet& self) {
      MONERO_CATCH_AND_RETHROW(self.get_restore_height());
    })
    .def("set_restore_height", [](monero::monero_wallet& self, uint64_t restore_height) {
      MONERO_CATCH_AND_RETHROW(self.set_restore_height(restore_height));
    }, py::arg("restore_height"))
    .def("get_daemon_height", [](monero::monero_wallet& self) {
      MONERO_CATCH_AND_RETHROW(self.get_daemon_height());
    })
    .def("get_daemon_max_peer_height", [](monero::monero_wallet& self) {
      MONERO_CATCH_AND_RETHROW(self.get_daemon_max_peer_height());
    })
    .def("get_height_by_date", [](monero::monero_wallet& self, uint16_t year, uint8_t month, uint8_t day) {
      MONERO_CATCH_AND_RETHROW(self.get_height_by_date(year, month, day));
    }, py::arg("year"), py::arg("month"), py::arg("day"))
    .def("add_listener", [](monero::monero_wallet& self, monero::monero_wallet_listener& listener) {
      MONERO_CATCH_AND_RETHROW(self.add_listener(listener));
    }, py::arg("listener"))
    .def("remove_listener", [](monero::monero_wallet& self, monero::monero_wallet_listener& listener) {
      MONERO_CATCH_AND_RETHROW(self.remove_listener(listener));
    }, py::arg("listener"))
    .def("get_listeners", [](monero::monero_wallet& self) {
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
    .def("sync", [](monero::monero_wallet& self) {
      MONERO_CATCH_AND_RETHROW(self.sync());
    })
    .def("sync", [](monero::monero_wallet& self, monero::monero_wallet_listener& listener) {
      MONERO_CATCH_AND_RETHROW(self.sync(listener));
    }, py::arg("listener"))
    .def("sync", [](monero::monero_wallet& self, uint64_t start_height) {
      MONERO_CATCH_AND_RETHROW(self.sync(start_height));
    }, py::arg("start_height"))
    .def("sync", [](monero::monero_wallet& self, uint64_t start_height, monero::monero_wallet_listener& listener) {
      MONERO_CATCH_AND_RETHROW(self.sync(start_height, listener));
    }, py::arg("start_height"), py::arg("listener"))
    .def("start_syncing", [](monero::monero_wallet& self, uint64_t sync_period_in_ms) {
      MONERO_CATCH_AND_RETHROW(self.start_syncing(sync_period_in_ms));
    }, py::arg("sync_period_in_ms") = 10000)
    .def("stop_syncing", [](monero::monero_wallet& self) {
      MONERO_CATCH_AND_RETHROW(self.stop_syncing());
    })
    .def("scan_txs", [](monero::monero_wallet& self, const std::vector<std::string>& tx_hashes) {
      MONERO_CATCH_AND_RETHROW(self.scan_txs(tx_hashes));
    }, py::arg("tx_hashes"))
    .def("rescan_spent", [](monero::monero_wallet& self) {
      MONERO_CATCH_AND_RETHROW(self.rescan_spent());
    })
    .def("rescan_blockchain", [](monero::monero_wallet& self) {
      MONERO_CATCH_AND_RETHROW(self.rescan_blockchain());
    })
    .def("get_balance", [](monero::monero_wallet& self) {
      MONERO_CATCH_AND_RETHROW(self.get_balance());
    })
    .def("get_balance", [](monero::monero_wallet& self, uint32_t account_idx) {
      MONERO_CATCH_AND_RETHROW(self.get_balance(account_idx));
    }, py::arg("account_idx"))
    .def("get_balance", [](monero::monero_wallet& self, uint32_t account_idx, uint32_t subaddress_idx) {
      MONERO_CATCH_AND_RETHROW(self.get_balance(account_idx, subaddress_idx));
    }, py::arg("account_idx"), py::arg("subaddress_idx"))
    .def("get_unlocked_balance", [](monero::monero_wallet& self) {
      MONERO_CATCH_AND_RETHROW(self.get_unlocked_balance());
    })
    .def("get_unlocked_balance", [](monero::monero_wallet& self, uint32_t account_idx) {
      MONERO_CATCH_AND_RETHROW(self.get_unlocked_balance(account_idx));
    }, py::arg("account_idx"))
    .def("get_unlocked_balance", [](monero::monero_wallet& self, uint32_t account_idx, uint32_t subaddress_idx) {
      MONERO_CATCH_AND_RETHROW(self.get_unlocked_balance(account_idx, subaddress_idx));
    }, py::arg("account_idx"), py::arg("subaddress_idx"))
    .def("get_accounts", [](monero::monero_wallet& self) {
      MONERO_CATCH_AND_RETHROW(self.get_accounts());
    })
    .def("get_accounts", [](monero::monero_wallet& self, bool include_subaddresses) {
      MONERO_CATCH_AND_RETHROW(self.get_accounts(include_subaddresses));
    }, py::arg("include_subaddresses"))
    .def("get_accounts", [](monero::monero_wallet& self, const std::string& tag) {
      MONERO_CATCH_AND_RETHROW(self.get_accounts(tag));
    }, py::arg("tag"))
    .def("get_accounts", [](monero::monero_wallet& self, bool include_subaddresses, const std::string& tag) {
      MONERO_CATCH_AND_RETHROW(self.get_accounts(include_subaddresses, tag));
    }, py::arg("include_subaddresses"), py::arg("tag"))
    .def("get_account", [](monero::monero_wallet& self, uint32_t account_idx) {
      MONERO_CATCH_AND_RETHROW(self.get_account(account_idx));
    }, py::arg("account_idx"))
    .def("get_account", [](monero::monero_wallet& self, uint32_t account_idx, bool include_subaddresses) {
      MONERO_CATCH_AND_RETHROW(self.get_account(account_idx, include_subaddresses));
    }, py::arg("account_idx"), py::arg("include_subaddresses"))
    .def("create_account", [](monero::monero_wallet& self, const std::string& label) {
      MONERO_CATCH_AND_RETHROW(self.create_account(label));
    }, py::arg("label") = "")
    .def("get_subaddresses", [](monero::monero_wallet& self, uint32_t account_idx) {
      MONERO_CATCH_AND_RETHROW(self.get_subaddresses(account_idx));
    }, py::arg("account_idx"))
    .def("get_subaddresses", [](monero::monero_wallet& self, uint32_t account_idx, const std::vector<uint32_t>& subaddress_indices) {
      MONERO_CATCH_AND_RETHROW(self.get_subaddresses(account_idx, subaddress_indices));
    }, py::arg("account_idx"), py::arg("subaddress_indices"))
    .def("create_subaddress", [](monero::monero_wallet& self, uint32_t account_idx, const std::string& label) {
      MONERO_CATCH_AND_RETHROW(self.create_subaddress(account_idx, label));
    }, py::arg("account_idx"), py::arg("label") = "")
    .def("set_subaddress_label", [](monero::monero_wallet& self, uint32_t account_idx, uint32_t subaddress_idx, const std::string& label) {
      MONERO_CATCH_AND_RETHROW(self.set_subaddress_label(account_idx, subaddress_idx, label));
    }, py::arg("account_idx"), py::arg("subaddress_idx"), py::arg("label") = "")
    .def("get_txs", [](monero::monero_wallet& self) {
      MONERO_CATCH_AND_RETHROW(self.get_txs());
    })
    .def("get_txs", [](monero::monero_wallet& self, const monero::monero_tx_query& query) {
      MONERO_CATCH_AND_RETHROW(self.get_txs(query));
    }, py::arg("query"))
    .def("get_transfers", [](monero::monero_wallet& self, const monero::monero_transfer_query& query) {
      MONERO_CATCH_AND_RETHROW(self.get_transfers(query));
    }, py::arg("query"))
    .def("get_outputs", [](monero::monero_wallet& self, const monero::monero_output_query& query) {
      MONERO_CATCH_AND_RETHROW(self.get_outputs(query));
    }, py::arg("query"))
    .def("export_outputs", [](monero::monero_wallet& self, bool all) {
      MONERO_CATCH_AND_RETHROW(self.export_outputs(all));
    }, py::arg("all") = false)
    .def("import_outputs", [](monero::monero_wallet& self, const std::string& outputs_hex) {
      MONERO_CATCH_AND_RETHROW(self.import_outputs(outputs_hex));
    }, py::arg("outputs_hex"))
    .def("export_key_images", [](monero::monero_wallet& self, bool all) {
      MONERO_CATCH_AND_RETHROW(self.export_key_images(all));
    }, py::arg("all") = false)
    .def("import_key_images", [](monero::monero_wallet& self, const std::vector<std::shared_ptr<monero_key_image>>& key_images) {
      MONERO_CATCH_AND_RETHROW(self.import_key_images(key_images));
    }, py::arg("key_images"))
    .def("freeze_output", [](monero::monero_wallet& self, const std::string& key_image) {
      MONERO_CATCH_AND_RETHROW(self.freeze_output(key_image));
    }, py::arg("key_image"))
    .def("thaw_output", [](monero::monero_wallet& self, const std::string& key_image) {
      MONERO_CATCH_AND_RETHROW(self.thaw_output(key_image));
    }, py::arg("key_image"))
    .def("is_output_frozen", [](monero::monero_wallet& self, const std::string& key_image) {
      MONERO_CATCH_AND_RETHROW(self.is_output_frozen(key_image));
    }, py::arg("key_image"))
    .def("get_default_fee_priority", [](monero::monero_wallet& self) {
      MONERO_CATCH_AND_RETHROW(self.get_default_fee_priority());
    })
    .def("create_tx", [](monero::monero_wallet& self, const monero::monero_tx_config& config) {
      MONERO_CATCH_AND_RETHROW(self.create_tx(config));
    }, py::arg("config"))
    .def("create_txs", [](monero::monero_wallet& self, const monero::monero_tx_config& config) {
      MONERO_CATCH_AND_RETHROW(self.create_txs(config));
    }, py::arg("config"))
    .def("sweep_unlocked", [](monero::monero_wallet& self, const monero::monero_tx_config& config) {
      MONERO_CATCH_AND_RETHROW(self.sweep_unlocked(config));
    }, py::arg("config"))
    .def("sweep_output", [](monero::monero_wallet& self, const monero::monero_tx_config& config) {
      MONERO_CATCH_AND_RETHROW(self.sweep_output(config));
    }, py::arg("config"))
    .def("sweep_dust", [](monero::monero_wallet& self, bool relay) {
      MONERO_CATCH_AND_RETHROW(self.sweep_dust(relay));
    }, py::arg("relay") = false)
    .def("relay_tx", [](monero::monero_wallet& self, const std::string& tx_metadata) {
      MONERO_CATCH_AND_RETHROW(self.relay_tx(tx_metadata));
    }, py::arg("tx_metadata"))
    .def("relay_tx", [](monero::monero_wallet& self, const monero::monero_tx_wallet& tx) {
      MONERO_CATCH_AND_RETHROW(self.relay_tx(tx));
    }, py::arg("tx"))
    .def("relay_txs", [](monero::monero_wallet& self, const std::vector<std::shared_ptr<monero_tx_wallet>>& txs) {
      MONERO_CATCH_AND_RETHROW(self.relay_txs(txs));
    }, py::arg("txs"))
    .def("relay_txs", [](monero::monero_wallet& self, const std::vector<std::string>& tx_metadatas) {
      MONERO_CATCH_AND_RETHROW(self.relay_txs(tx_metadatas));
    }, py::arg("tx_metadatas"))
    .def("describe_tx_set", [](monero::monero_wallet& self, const monero::monero_tx_set& tx_set) {
      MONERO_CATCH_AND_RETHROW(self.describe_tx_set(tx_set));
    }, py::arg("tx_set"))
    .def("sign_txs", [](monero::monero_wallet& self, const std::string& unsigned_tx_hex) {
      MONERO_CATCH_AND_RETHROW(self.sign_txs(unsigned_tx_hex));
    }, py::arg("unsigned_tx_hex"))
    .def("submit_txs", [](monero::monero_wallet& self, const std::string& signed_tx_hex) {
      MONERO_CATCH_AND_RETHROW(self.submit_txs(signed_tx_hex));
    }, py::arg("signed_tx_hex"))
    .def("sign_message", [](monero::monero_wallet& self, const std::string& msg, monero_message_signature_type signature_type, uint32_t account_idx, uint32_t subaddress_idx) {
      MONERO_CATCH_AND_RETHROW(self.sign_message(msg, signature_type, account_idx, subaddress_idx));
    }, py::arg("msg"), py::arg("signature_type"), py::arg("account_idx") = 0, py::arg("subaddress_idx") = 0)
    .def("verify_message", [](monero::monero_wallet& self, const std::string& msg, const std::string& address, const std::string& signature) {
      MONERO_CATCH_AND_RETHROW(self.verify_message(msg, address, signature));
    }, py::arg("msg"), py::arg("address"), py::arg("signature"))
    .def("get_tx_key", [](monero::monero_wallet& self, const std::string& tx_hash) {
      MONERO_CATCH_AND_RETHROW(self.get_tx_key(tx_hash));
    }, py::arg("tx_hash"))
    .def("check_tx_key", [](monero::monero_wallet& self, const std::string& tx_hash, const std::string& tx_key, const std::string& address) {
      MONERO_CATCH_AND_RETHROW(self.check_tx_key(tx_hash, tx_key, address));
    }, py::arg("tx_hash"), py::arg("tx_key"), py::arg("address"))
    .def("get_tx_proof", [](monero::monero_wallet& self, const std::string& tx_hash, const std::string& address, const std::string& message) {
      MONERO_CATCH_AND_RETHROW(self.get_tx_proof(tx_hash, address, message));
    }, py::arg("tx_hash"), py::arg("address"), py::arg("message"))
    .def("check_tx_proof", [](monero::monero_wallet& self, const std::string& tx_hash, const std::string& address, const std::string& message, const std::string& signature) {
      MONERO_CATCH_AND_RETHROW(self.check_tx_proof(tx_hash, address, message, signature));
    }, py::arg("tx_hash"), py::arg("address"), py::arg("message"), py::arg("signature"))
    .def("get_spend_proof", [](monero::monero_wallet& self, const std::string& tx_hash, const std::string& message) {
      MONERO_CATCH_AND_RETHROW(self.get_spend_proof(tx_hash, message));
    }, py::arg("tx_hash"), py::arg("message"))
    .def("check_spend_proof", [](monero::monero_wallet& self, const std::string& tx_hash, const std::string& message, const std::string& signature) {
      MONERO_CATCH_AND_RETHROW(self.check_spend_proof(tx_hash, message, signature));
    }, py::arg("tx_hash"), py::arg("message"), py::arg("signature"))
    .def("get_reserve_proof_wallet", [](monero::monero_wallet& self, const std::string& message) {
      MONERO_CATCH_AND_RETHROW(self.get_reserve_proof_wallet(message));
    }, py::arg("message"))
    .def("get_reserve_proof_account", [](monero::monero_wallet& self, uint32_t account_idx, uint64_t amount, const std::string& message) {
      MONERO_CATCH_AND_RETHROW(self.get_reserve_proof_account(account_idx, amount, message));
    }, py::arg("account_idx"), py::arg("amount"), py::arg("message"))
    .def("check_reserve_proof", [](monero::monero_wallet& self, const std::string& address, const std::string& message, const std::string& signature) {
      MONERO_CATCH_AND_RETHROW(self.check_reserve_proof(address, message, signature));
    }, py::arg("address"), py::arg("message"), py::arg("signature"))
    .def("get_tx_note", [](monero::monero_wallet& self, const std::string& tx_hash) {
      MONERO_CATCH_AND_RETHROW(self.get_tx_note(tx_hash));
    }, py::arg("tx_hash"))
    .def("get_tx_notes", [](monero::monero_wallet& self, const std::vector<std::string>& tx_hashes) {
      MONERO_CATCH_AND_RETHROW(self.get_tx_notes(tx_hashes));
    }, py::arg("tx_hashes"))
    .def("set_tx_note", [](monero::monero_wallet& self, const std::string& tx_hash, const std::string& note) {
      MONERO_CATCH_AND_RETHROW(self.set_tx_note(tx_hash, note));
    }, py::arg("tx_hash"), py::arg("note"))
    .def("set_tx_notes", [](monero::monero_wallet& self, const std::vector<std::string>& tx_hashes, const std::vector<std::string>& notes) {
      MONERO_CATCH_AND_RETHROW(self.set_tx_notes(tx_hashes, notes));
    }, py::arg("tx_hashes"), py::arg("notes"))
    .def("get_address_book_entries", [](monero::monero_wallet& self, const std::vector<uint64_t>& indices) {
      MONERO_CATCH_AND_RETHROW(self.get_address_book_entries(indices));
    }, py::arg("indices"))
    .def("add_address_book_entry", [](monero::monero_wallet& self, const std::string& address, const std::string& description) {
      MONERO_CATCH_AND_RETHROW(self.add_address_book_entry(address, description));
    }, py::arg("address"), py::arg("description"))
    .def("edit_address_book_entry", [](monero::monero_wallet& self, uint64_t index, bool set_address, const std::string& address, bool set_description, const std::string& description) {
      MONERO_CATCH_AND_RETHROW(self.edit_address_book_entry(index, set_address, address, set_description, description));
    }, py::arg("index"), py::arg("set_address"), py::arg("address"), py::arg("set_description"), py::arg("description"))
    .def("delete_address_book_entry", [](monero::monero_wallet& self, uint64_t index) {
      MONERO_CATCH_AND_RETHROW(self.delete_address_book_entry(index));
    }, py::arg("index"))
    .def("get_payment_uri", [](monero::monero_wallet& self, const monero::monero_tx_config& config) {
      MONERO_CATCH_AND_RETHROW(self.get_payment_uri(config));
    }, py::arg("config"))
    .def("parse_payment_uri", [](monero::monero_wallet& self, const std::string& uri) {
      MONERO_CATCH_AND_RETHROW(self.parse_payment_uri(uri));
    }, py::arg("uri"))        
    .def("get_attribute", [](monero::monero_wallet& self, const std::string& key, std::string& val) {
      MONERO_CATCH_AND_RETHROW(self.get_attribute(key, val));
    }, py::arg("key"), py::arg("val"))
    .def("set_attribute", [](monero::monero_wallet& self, const std::string& key, const std::string& val) {
      MONERO_CATCH_AND_RETHROW(self.set_attribute(key, val));
    }, py::arg("key"), py::arg("val"))
    .def("stop_mining", [](monero::monero_wallet& self) {
      MONERO_CATCH_AND_RETHROW(self.stop_mining());
    }) 
    .def("wait_for_next_block", [](monero::monero_wallet& self) {
      MONERO_CATCH_AND_RETHROW(self.wait_for_next_block());
    }) 
    .def("is_multisig_import_needed", [](monero::monero_wallet& self) {
      MONERO_CATCH_AND_RETHROW(self.is_multisig_import_needed());
    })  
    .def("is_multisig", [](monero::monero_wallet& self) {
      MONERO_CATCH_AND_RETHROW(self.is_multisig());
    })  
    .def("get_multisig_info", [](monero::monero_wallet& self) {
      MONERO_CATCH_AND_RETHROW(self.get_multisig_info());
    })   
    .def("prepare_multisig", [](monero::monero_wallet& self) {
      MONERO_CATCH_AND_RETHROW(self.prepare_multisig());
    })        
    .def("make_multisig", [](monero::monero_wallet& self, const std::vector<std::string>& mutisig_hexes, int threshold, const std::string& password) {
      MONERO_CATCH_AND_RETHROW(self.make_multisig(mutisig_hexes, threshold, password));
    }, py::arg("mutisig_hexes"), py::arg("threshold"), py::arg("password"))
    .def("exchange_multisig_keys", [](monero::monero_wallet& self, const std::vector<std::string>& mutisig_hexes, const std::string& password) {
      MONERO_CATCH_AND_RETHROW(self.exchange_multisig_keys(mutisig_hexes, password));
    }, py::arg("mutisig_hexes"), py::arg("password"))
    .def("export_multisig_hex", [](monero::monero_wallet& self) {
      MONERO_CATCH_AND_RETHROW(self.export_multisig_hex());
    })
    .def("import_multisig_hex", [](monero::monero_wallet& self, const std::vector<std::string>& multisig_hexes) {
      MONERO_CATCH_AND_RETHROW(self.import_multisig_hex(multisig_hexes));
    }, py::arg("multisig_hexes"))
    .def("sign_multisig_tx_hex", [](monero::monero_wallet& self, const std::string& multisig_tx_hex) {
      MONERO_CATCH_AND_RETHROW(self.sign_multisig_tx_hex(multisig_tx_hex));
    }, py::arg("multisig_tx_hex"))
    .def("submit_multisig_tx_hex", [](monero::monero_wallet& self, const std::string& signed_multisig_tx_hex) {
      MONERO_CATCH_AND_RETHROW(self.submit_multisig_tx_hex(signed_multisig_tx_hex));
    }, py::arg("signed_multisig_tx_hex"))
    .def("change_password", [](monero::monero_wallet& self, const std::string& old_password, const std::string& new_password) {
      MONERO_CATCH_AND_RETHROW(self.change_password(old_password, new_password));
    }, py::arg("old_password"), py::arg("new_password"))
    .def("move_to", [](monero::monero_wallet& self, const std::string& path, const std::string& password) {
      MONERO_CATCH_AND_RETHROW(self.move_to(path, password));
    }, py::arg("path"), py::arg("password"))
    .def("save", [](monero::monero_wallet& self) {
      MONERO_CATCH_AND_RETHROW(self.save());
    })
    .def("close", [](monero::monero_wallet& self, bool save) {
      MONERO_CATCH_AND_RETHROW(self.close(save));
    }, py::arg("save") = false);

  // monero_wallet_keys
  py::class_<monero::monero_wallet_keys, monero::monero_wallet, std::shared_ptr<monero::monero_wallet_keys>>(m, "MoneroWalletKeys")
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
  py::class_<monero::monero_wallet_full, monero::monero_wallet, std::shared_ptr<monero::monero_wallet_full>>(m, "MoneroWalletFull")
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

  py::class_<PyMoneroWalletRpc, monero::monero_wallet, std::shared_ptr<PyMoneroWalletRpc>>(m, "MoneroWalletRpc")
    .def(py::init<std::shared_ptr<PyMoneroRpcConnection>>(), py::arg("rpc_connection"));

  // monero_utils
  py::class_<PyMoneroUtils>(m, "MoneroUtils")
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
