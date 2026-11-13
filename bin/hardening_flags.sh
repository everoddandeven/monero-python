# shellcheck shell=sh
# Sourced by the scripts that build the static libraries of the module (bin/build_monero_cpp.sh,
# debian/install-static-deps.sh). On Linux it adds the flags of the hardening to CFLAGS and CXXFLAGS, which
# cmake and configure take from the environment:
#
#   . bin/hardening_flags.sh
#
# Debian's gcc turns none of them on, Ubuntu's turns on some, so the same sources gave a different library on
# each release. A flag that the compiler does not know (-fstack-clash-protection on 32 bit arm, -fcf-protection
# outside of x86) is left out instead of failing the build. The module has the same flags in CMakeLists.txt.
# macOS is not touched, the clang of Apple has the stack protector on, and the Windows build has its own toolchain.
#
# -O2 is there because configure drops its default -O2 once CFLAGS is set, and _FORTIFY_SOURCE needs it. The
# CMAKE_BUILD_TYPE of monero-project adds its own -O3 after it.
if [ "$(uname -s)" = Linux ]; then
    hardening_flags="-O2 -D_FORTIFY_SOURCE=2"
    hardening_flag_candidates="-fstack-protector-strong -fstack-clash-protection"
    if [ "$(uname -m)" = x86_64 ]; then
        hardening_flag_candidates="$hardening_flag_candidates -fcf-protection=full"
    fi
    for hardening_flag in $hardening_flag_candidates; do
        # CC can be "ccache gcc"
        # shellcheck disable=SC2086
        if echo 'int main(void) { return 0; }' | ${CC:-cc} -Werror "$hardening_flag" -x c -c -o /dev/null - 2> /dev/null; then
            hardening_flags="$hardening_flags $hardening_flag"
        else
            echo "hardening: the compiler does not take $hardening_flag, building without it" >&2
        fi
    done
    CFLAGS="${CFLAGS:+$CFLAGS }$hardening_flags"
    CXXFLAGS="${CXXFLAGS:+$CXXFLAGS }$hardening_flags -D_GLIBCXX_ASSERTIONS"
    export CFLAGS CXXFLAGS
    echo "hardening: CFLAGS=$CFLAGS" >&2
    unset hardening_flags hardening_flag_candidates hardening_flag
fi
