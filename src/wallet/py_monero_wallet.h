#include "daemon/py_monero_daemon.h"

enum PyMoneroAddressType : uint8_t {
  PRIMARY_ADDRESS = 0,
  INTEGRATED_ADDRESS,
  SUBADDRESS
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
  PyMoneroAccountTag() { }

  PyMoneroAccountTag(std::string& tag, std::string& label) {
    m_tag = tag;
    m_label = label;
  }

  PyMoneroAccountTag(std::string& tag, std::string& label, std::vector<uint32_t> account_indices) {
    m_tag = tag;
    m_label = label;
    m_account_indices = account_indices;
  }

  boost::optional<std::string> m_tag;
  boost::optional<std::string> m_label;
  std::vector<uint32_t> m_account_indices;
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

  PyMoneroWalletRpc(const std::string& uri = "", const std::string& username = "", const std::string& password = "")
  {
    m_rpc_connection = std::make_shared<PyMoneroRpcConnection>(uri, username, password);
    m_rpc_connection->check_connection();
  }

  boost::optional<monero::monero_rpc_connection> get_daemon_connection() const override {
    if (m_rpc_connection == nullptr) return boost::none;
    return boost::optional<monero::monero_rpc_connection>(*m_rpc_connection);
  }

  void open_wallet(const std::shared_ptr<monero::monero_wallet_config> config) {
    throw std::runtime_error("PyMoneroWalletRpc::open_wallet(): not implemented");
  }

  void open_wallet(const std::string& name, const std::string& password) {
    auto config = std::make_shared<monero::monero_wallet_config>();
    config->m_path = name;
    config->m_password = password;
    return open_wallet(config);
  }

protected:
  std::shared_ptr<PyMoneroRpcConnection> m_rpc_connection;
};
  