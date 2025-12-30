#pragma once

#include <pybind11/pybind11.h>
#include <boost/optional.hpp>

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

}} // namespace pybind11::detail
