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

#include "common/monero_rpc_connection.h"
#include "daemon/monero_daemon_model.h"

using namespace monero;
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

PYBIND11_MAKE_OPAQUE(std::vector<std::string>);
PYBIND11_MAKE_OPAQUE(std::vector<std::shared_ptr<monero_block>>);
PYBIND11_MAKE_OPAQUE(std::vector<std::shared_ptr<monero_block_header>>);
PYBIND11_MAKE_OPAQUE(std::vector<std::shared_ptr<monero_tx>>);
PYBIND11_MAKE_OPAQUE(std::vector<std::shared_ptr<monero_output>>);

/**
 * Collection of python generic utilities.
 */
class PyGenUtils {
public:
  static std::string serialize(const py::dict& d);
  static py::dict deserialize(const std::string& s);
  static py::object convert_value(const std::string& val);
  static py::object ptree_to_pyobject(const boost::property_tree::ptree& tree);
};

struct PyMoneroRequestParams : public monero_request_params {
public:
  boost::optional<py::object> m_py_params;

  PyMoneroRequestParams() { }
  PyMoneroRequestParams(const boost::optional<py::object>& py_params): m_py_params(py_params) { }

  rapidjson::Value to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const override;
};
