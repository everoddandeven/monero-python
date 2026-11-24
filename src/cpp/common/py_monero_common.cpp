/**
 * Copyright (c) Libmonero
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
#include "py_monero_common.h"
#include "utils/gen_utils.h"
#include <algorithm>

// --------------------------- GEN UTILS ---------------------------

std::string PyGenUtils::serialize(const py::dict& d) {
  py::object fn = py::module_::import("json").attr("dumps");
  return fn(d).cast<std::string>();
}

py::dict PyGenUtils::deserialize(const std::string& s) {
  py::object fn = py::module_::import("json").attr("loads");
  return fn(s).cast<py::dict>();
}

// the message of an error response, as monero-cpp reads it from a property tree: the text of the value, or a message that names the
// request when it has no text
static std::string get_rpc_error_message(const py::handle& message, const std::string& method, const std::string& uri) {
  std::string text;
  if (py::isinstance<py::str>(message)) text = message.cast<std::string>();
  else if (py::isinstance<py::bool_>(message)) text = message.cast<bool>() ? "true" : "false";
  else if (py::isinstance<py::int_>(message) || py::isinstance<py::float_>(message)) text = py::str(message).cast<std::string>();
  else if (message.is_none()) text = "null";
  if (text.empty()) text = "Received error response from RPC request with method '" + method + "' to " + uri;
  return text;
}

// the code of an error response, as monero-cpp reads it from a property tree: an integer, or -1
static int get_rpc_error_code(const py::handle& code) {
  if (py::isinstance<py::bool_>(code)) return -1;
  if (py::isinstance<py::int_>(code)) {
    try {
      return code.cast<int>();
    } catch (...) {
      return -1;
    }
  }
  if (py::isinstance<py::str>(code)) {
    std::string text = code.cast<std::string>();
    try {
      std::size_t pos;
      int value = std::stoi(text, &pos);
      if (pos == text.size()) return value;
    } catch (...) {}
  }
  return -1;
}

py::object PyGenUtils::parse_rpc_response(const std::string& body, const std::string& method, const std::string& uri, bool json_rpc) {

  // parse the body
  py::object response;
  try {
    response = py::module_::import("json").attr("loads")(py::bytes(body));
  } catch (py::error_already_set& e) {
    if (!e.matches(PyExc_ValueError)) throw;
    throw monero_error("Invalid JSON");
  }

  // a response that is not an object has no result
  if (!py::isinstance<py::dict>(response)) return json_rpc ? py::none() : response;
  py::dict response_dict = response;

  // raise an error response
  if (response_dict.contains("error")) {
    std::string message = "Unknown error";
    int code = -1;
    py::object error = response_dict["error"];
    if (py::isinstance<py::dict>(error)) {
      py::dict error_dict = error;
      if (error_dict.contains("message")) message = get_rpc_error_message(error_dict["message"], method, uri);
      if (error_dict.contains("code")) code = get_rpc_error_code(error_dict["code"]);
    }
    throw monero_rpc_error(code, message);
  }

  // return the result of a JSON-RPC response, or the whole response of a path request unless it is a JSON-RPC one, as monero-cpp does
  if (json_rpc) return response_dict.contains("result") ? py::object(response_dict["result"]) : py::none();
  return response_dict.contains("jsonrpc") ? py::none() : response;
}

// replaces the non-empty strings of the keys with ***, at any depth, like the password of the server of a wallet config
static void redact(rapidjson::Value& val, const std::vector<std::string>& keys) {
  if (val.IsArray()) {
    for (auto& item : val.GetArray()) redact(item, keys);
    return;
  }
  if (!val.IsObject()) return;
  for (auto& member : val.GetObject()) {
    bool secret = std::find(keys.begin(), keys.end(), member.name.GetString()) != keys.end();
    if (secret && member.value.IsString() && member.value.GetStringLength() > 0) member.value.SetString("***");
    else redact(member.value, keys);
  }
}

std::string PyGenUtils::serialize_redacted(const serializable_struct& s, const std::vector<std::string>& keys) {
  rapidjson::Document doc;
  doc.SetObject();
  rapidjson::Value val = s.to_rapidjson_val(doc.GetAllocator());
  val.Swap(doc);
  redact(doc, keys);
  return gen_utils::serialize(doc);
}

py::str PyGenUtils::repr(const py::object& self, const std::string& json) {
  return py::str("{}({})").format(py::type::of(self).attr("__name__"), json);
}

// --------------------------- MONERO REQUEST PARAMS ---------------------------

PyMoneroRequestParams::PyMoneroRequestParams(const boost::optional<py::object>& py_params) {
  if (py_params == boost::none || py_params->is_none()) return;
  m_json = py::module_::import("json").attr("dumps")(py_params.get()).cast<std::string>();
}

rapidjson::Value PyMoneroRequestParams::to_rapidjson_val(rapidjson::Document::AllocatorType& allocator) const {
  rapidjson::Value root(rapidjson::kObjectType);
  if (m_json == boost::none) return root;

  // parse the params that the constructor serialized
  rapidjson::Document doc;
  doc.Parse(m_json->c_str());
  root.CopyFrom(doc, allocator);

  return root;
}
