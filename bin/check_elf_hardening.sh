#!/usr/bin/env bash
# Checks the hardening of the module on Linux: the segments and the dynamic section, the exports, and how much of the code the compiler protected.
#
#   check_elf_hardening.sh path/to/monero.cpython-312-x86_64-linux-gnu.so
#
# The module is stripped (by pybind11 and by dh_strip), so there are no function names to count by kind: what is counted are the calls to
# __stack_chk_fail, one for each function that has a canary, and, on x86_64, the endbr64 instructions of the branch protection. The disassembly
# is read for x86_64 and aarch64 only, the objdump of an arm64 runner does not read the 32 bit arm module that is built there.
#
# What the debs had, to put the minimums where a build with none of the flags falls under them:
#   before the flags, with every symbol exported and no code removed (0.9.4):
#     trixie amd64 : 13306 calls to __stack_chk_fail, 47087 endbr64, 5 _chk functions imported, no full RELRO
#     noble amd64  : 27284 calls to __stack_chk_fail, 82737 endbr64, 15 _chk functions imported, no full RELRO, an executable stack (GNU_STACK RWE)
#   with the flags of bin/hardening_flags.sh and CMakeLists.txt (run 43531387312, bookworm amd64): 6472 calls to __stack_chk_fail, 66916 endbr64,
#   12 _chk functions imported, 890 exports. There are fewer calls than before because --gc-sections now drops the code that nothing reaches.
# The minimums are about half of the build with the flags. The one of aarch64 was not measured.
#
# The exports are PyInit_monero, the names that the linker adds, and the C++ symbols of Boost and the standard library: the headers of Boost mark
# many of their classes visible (BOOST_SYMBOL_VISIBLE), and namespace std is visible, so the module's own objects export them whatever
# -fvisibility=hidden says, as the Windows module exports the ones of Boost.Serialization. The symbols of the static libraries are hidden.
set -euo pipefail
export LC_ALL=C

library="${1:?usage: check_elf_hardening.sh monero.cpython-312-x86_64-linux-gnu.so}"

MIN_FORTIFY_IMPORTS=8
MIN_CANARY_CALLS_X86_64=3000
MIN_CANARY_CALLS_AARCH64=1000
MIN_LANDING_PADS_X86_64=20000

failed=0
fail() {
  echo "FAIL: $*"
  failed=1
}

for tool in readelf awk; do
  command -v "$tool" > /dev/null || { echo "$tool is needed"; exit 2; }
done

# the output of a tool is kept in a variable and read with here-strings: grep -q that stops at the first match makes the tool before it in a pipe
# fail with SIGPIPE, which pipefail turns into a failure
header=$(readelf -h "$library")
machine=$(awk -F: '/Machine:/ { gsub(/^[ \t]+/, "", $2); print $2 }' <<< "$header")
echo "$library: $machine"
grep -Eq 'Type:[[:space:]]+DYN' <<< "$header" || fail "the module is not a shared object"

program_headers=$(readelf -lW "$library")
grep -q 'GNU_RELRO' <<< "$program_headers" || fail "RELRO segment is missing"
awk '$1 == "GNU_STACK" { found = 1; if ($7 ~ /E/) executable = 1 } END { exit !(found && !executable) }' <<< "$program_headers" || fail "GNU_STACK is executable or missing"
dynamic_section=$(readelf -dW "$library")
grep -Eq '\(BIND_NOW\)|\(FLAGS_1\).*NOW' <<< "$dynamic_section" || fail "full RELRO (BIND_NOW) is missing"
# a path of the build machine in the module, or a path to look for libraries in
if grep -Eq '\((RPATH|RUNPATH)\)' <<< "$dynamic_section"; then
  fail "the module has an RPATH or RUNPATH: $(grep -E '\((RPATH|RUNPATH)\)' <<< "$dynamic_section")"
fi

dynamic_symbols=$(readelf --dyn-syms --wide "$library")
grep -Eq 'UND[[:space:]]+__stack_chk_fail(@|$)' <<< "$dynamic_symbols" || fail "__stack_chk_fail is not imported, so there are no stack canaries"
fortify_imports=$(awk '$7 == "UND" && $8 ~ /^__[A-Za-z0-9_]+_chk(@|$)/ { n++ } END { print n + 0 }' <<< "$dynamic_symbols")
echo "FORTIFY functions imported: $fortify_imports (minimum $MIN_FORTIFY_IMPORTS)"
[ "$fortify_imports" -ge "$MIN_FORTIFY_IMPORTS" ] || fail "only $fortify_imports _chk functions are imported, FORTIFY_SOURCE is not on in most of the code"

# a python module exports PyInit_monero and nothing else. The linker adds a few names of its own to some shared objects
exports=$(awk 'NF >= 8 && $1 ~ /^[0-9]+:$/ && $7 != "UND" { sub(/@.*/, "", $8); print $8 }' <<< "$dynamic_symbols" | sort -u)
# the mangled names of Boost and of the standard library: the symbol itself, its guard variable, vtable, typeinfo and thunks, and the local statics of a function
visible_cpp='^_Z(GV|TV|TI|TS|TT|GR)?Z?(Th[0-9n]+_|Tv[0-9n]+_[0-9n]+_)?(N[KVr]*)?(5boost|St|9__gnu_cxx)'
unexpected=$(grep -Evx 'PyInit_monero|_init|_fini|_edata|_end|__bss_start' <<< "$exports" | grep -Ev "$visible_cpp" || true)
echo "exports: $(wc -l <<< "$exports")"
grep -qx 'PyInit_monero' <<< "$exports" || fail "PyInit_monero is not exported"
if [ -n "$unexpected" ]; then
  fail "the module exports $(wc -l <<< "$unexpected") symbols besides PyInit_monero and the C++ of Boost and std, such as:"
  head -n 30 <<< "$unexpected"
fi

case "$machine" in
  "Advanced Micro Devices X86-64") canary_pattern='call.*__stack_chk_fail' min_canary=$MIN_CANARY_CALLS_X86_64 ;;
  AArch64) canary_pattern='bl[[:space:]].*__stack_chk_fail' min_canary=$MIN_CANARY_CALLS_AARCH64 ;;
  *) canary_pattern='' ;;
esac
if [ -n "$canary_pattern" ] && command -v objdump > /dev/null; then
  disassembly=$(objdump -d --no-show-raw-insn "$library")
  calls=$(grep -Ec "$canary_pattern" <<< "$disassembly" || true)
  echo "calls to __stack_chk_fail: $calls (minimum $min_canary)"
  [ "$calls" -ge "$min_canary" ] || fail "only $calls calls to __stack_chk_fail, so most of the code has no stack protector"
  if [ "$machine" = "Advanced Micro Devices X86-64" ]; then
    pads=$(grep -c endbr64 <<< "$disassembly" || true)
    echo "endbr64: $pads (minimum $MIN_LANDING_PADS_X86_64)"
    [ "$pads" -ge "$MIN_LANDING_PADS_X86_64" ] || fail "only $pads endbr64 instructions, so most of the code has no branch protection"
  fi
else
  echo "the code of $machine is not disassembled here, the counts are skipped"
fi

if [ "$failed" -ne 0 ]; then
  exit 1
fi
echo "hardening of $library: ok"
