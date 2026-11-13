#!/usr/bin/env bash
# Checks the hardening and the exports of the module on Windows. Run it in MSYS2 MINGW64 (it needs objdump and c++filt of binutils, and awk).
#
#   check_pe_hardening.sh path/to/monero.cp313-win_amd64.pyd
#
# 1. The flags of the image: ASLR with a high entropy address space (DYNAMIC_BASE, HIGH_ENTROPY_VA) and DEP (NX_COMPAT). mingw-w64 sets them.
# 2. The exports: PyInit_monero, and nothing that isn't Boost.Serialization or Boost.Archive. Those are the 1099 symbols that the headers of
#    Boost mark with BOOST_SYMBOL_EXPORT and that --exclude-libs doesn't remove. The wheel of 0.9.10 has 1100 exports, and no other.
#
# There is no count of the stack canaries as on Linux: the module is stripped by pybind11, and the calls to __stack_chk_fail have no name left.
# CMakeLists.txt turns the flag on, and the build of the module fails to link if the runtime does not have it.
set -euo pipefail
export LC_ALL=C

library="${1:?usage: check_pe_hardening.sh monero.cp313-win_amd64.pyd}"

failed=0
fail() {
  echo "FAIL: $*"
  failed=1
}

for tool in objdump c++filt awk sort; do
  command -v "$tool" > /dev/null || { echo "$tool is needed"; exit 2; }
done

# the output of a tool is kept in a variable and read with here-strings: grep -q that stops at the first match makes the tool before it in a pipe
# fail with SIGPIPE, which pipefail turns into a failure
headers=$(objdump -p "$library")
echo "$library"
for flag in DYNAMIC_BASE HIGH_ENTROPY_VA NX_COMPAT; do
  grep -q "$flag" <<< "$headers" || fail "the image has no $flag in its DllCharacteristics"
done

exports=$(sed -n '/Ordinal\/Name Pointer/,$p' <<< "$headers" | awk '/^[ \t]*\[ *[0-9]+\]/ { print $NF }' | sort -u)
echo "exports: $(wc -l <<< "$exports")"
grep -qx 'PyInit_monero' <<< "$exports" || fail "PyInit_monero is not exported"
foreign=$(grep -vx 'PyInit_monero' <<< "$exports" | c++filt | grep -Ev '^((vtable|typeinfo|typeinfo name|guard variable|VTT|construction vtable) for )?((non-virtual |virtual )?thunk to )?boost::(serialization|archive)::' || true)
if [ -n "$foreign" ]; then
  fail "the module exports $(wc -l <<< "$foreign") symbols that are not PyInit_monero or of Boost.Serialization and Boost.Archive, such as:"
  head -n 20 <<< "$foreign"
fi

if [ "$failed" -ne 0 ]; then
  exit 1
fi
echo "hardening of $library: ok"
