#include <string>
#include <regex>
#include <set>
#include <future>
#include <chrono>
#include <algorithm>
#include <memory>
#include <type_traits>

#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include "../../external/monero-cpp/src/utils/monero_utils.h"
#include "../../external/monero-cpp/src/daemon/monero_daemon_model.h"
#include "../../external/monero-cpp/src/wallet/monero_wallet_model.h"
#include "../../external/monero-cpp/src/wallet/monero_wallet_full.h"
#include "../../external/monero-cpp/src/wallet/monero_wallet_keys.h"

namespace py = pybind11;

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
  
  static int compare(int p1, int p2) {
    if (p1 == p2) return 0;
    if (p1 == 0) return -1;
    if (p2 == 0) return 1;
    return p2 - p1;
  }
};

class PyMoneroTxHeightComparator {
public:

  static int compare(const std::shared_ptr<monero::monero_tx> &tx1, const std::shared_ptr<monero::monero_tx> &tx2) {
    if (tx1->get_height() == boost::none && tx2->get_height() == boost::none) return 0; // both unconfirmed
    else if (tx1->get_height() == boost::none) return 1;   // tx1 is unconfirmed
    else if (tx2->get_height() == boost::none) return -1;  // tx2 is unconfirmed
    int diff = tx1->get_height().get() - tx2->get_height().get();
    if (diff != 0) return diff;
    auto txs1 = tx1->m_block.get()->m_txs;
    auto txs2 = tx2->m_block.get()->m_txs;
    auto it1 = find(txs1.begin(), txs1.end(), tx1);
    auto it2 = find(txs2.begin(), txs2.end(), tx2);
    if (it1 == txs1.end() && it2 == txs2.end()) return 0;
    else if (it1 == txs1.end()) return 1;
    else if (it2 == txs2.end()) return -1;

    return std::distance(txs1.begin(), it1) - std::distance(txs2.begin(), it2); // txs are in the same block so retain their original order
  }
};

class PyGenUtils {
public:
  PyGenUtils() {}

  // Converti valore stringa in tipo nativo se possibile
  static py::object convert_value(const std::string& val) {
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
  
  // ptree → py::object
  static py::object ptree_to_pyobject(const boost::property_tree::ptree& tree) {
    // Caso foglia: nessun figlio
    if (tree.empty()) {
      return convert_value(tree.get_value<std::string>());
    }

    // Verifica se è una lista (tutti i figli con la stessa chiave "")
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
  
  // py::object → ptree
  static boost::property_tree::ptree pyobject_to_ptree(const py::object& obj) {
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
  };
  
};

class PySerializableStruct : public serializable_struct {
public:
  using serializable_struct::serializable_struct;

  rapidjson::Value to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const override { throw std::runtime_error("PySerializableStruct::to_rapid_json_value(): not implemented"); };

};
