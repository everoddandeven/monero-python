#!/usr/bin/env bash
# Checks the hardening and the exports of the module on macOS. Run it on macOS, which has nm and otool.
#
#   check_macho_hardening.sh path/to/monero.cpython-314-darwin.so
#
# Apple clang turns the stack protector on (-fstack-protector-strong), so what is checked is that the module imports the guard and the handler of
# the canary, and that many functions call the handler. The count is the number of calls to ___stack_chk_fail in the code, a call for each function
# that has a canary. The module of the build of CI has 3018 of them on arm64 (macos-15) and 2864 on x86_64 (macos-15-intel), and the minimum is
# about half of that: a module built with no stack protector, or whose libraries were, has a handful.
#
# The exports are _PyInit_monero and nothing else, which the linker is asked for with -exported_symbol in CMakeLists.txt.
set -euo pipefail
export LC_ALL=C

library="${1:?usage: check_macho_hardening.sh monero.cpython-314-darwin.so}"
MIN_CANARY_CALLS=1400

failed=0
fail() {
  echo "FAIL: $*"
  failed=1
}

for tool in nm otool awk; do
  command -v "$tool" > /dev/null || { echo "$tool is needed"; exit 2; }
done

echo "$library"
undefined=$(nm -u "$library")
for symbol in ___stack_chk_fail ___stack_chk_guard; do
  # nm of Apple prints the name alone for -u, and some print the type before it
  grep -Eq "(^|[[:space:]])${symbol}\$" <<< "$undefined" || fail "$symbol is not imported, so there are no stack canaries"
done

# a call is a line of the code that names the handler. The stub of the dynamic linker is named in each of them
calls=$(otool -tV "$library" | awk '/___stack_chk_fail/ { n++ } END { print n + 0 }')
echo "calls to ___stack_chk_fail: $calls (minimum $MIN_CANARY_CALLS)"
[ "$calls" -ge "$MIN_CANARY_CALLS" ] || fail "only $calls calls to ___stack_chk_fail, so most of the code has no stack protector"

# the names of the external symbols that the module defines, with the type before them when nm prints it
exports=$(nm -gU "$library" | awk 'NF { print $NF }' | sort -u)
echo "exports: $(wc -l <<< "$exports" | tr -d ' ')"
grep -qx '_PyInit_monero' <<< "$exports" || fail "_PyInit_monero is not exported"
unexpected=$(grep -Evx '_PyInit_monero|__mh_[a-z_]+_header' <<< "$exports" || true)
if [ -n "$unexpected" ]; then
  fail "the module exports $(wc -l <<< "$unexpected" | tr -d ' ') symbols besides _PyInit_monero, such as:"
  head -n 20 <<< "$unexpected"
fi

if [ "$failed" -ne 0 ]; then
  exit 1
fi
echo "hardening of $library: ok"
