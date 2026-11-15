#!/usr/bin/env bash
# Installs a group of the packages that bin/msys2_pins.txt pins, in the MSYS2 of the Windows build (build-windows.yml): it downloads
# each one, checks it against its sha256 and installs the group with a single pacman -U, since the packages of a group depend on each other.
#
#   bin/install_msys2_pins.sh <group>
set -euo pipefail

group=${1:?usage: $0 <group>}
pins="$(dirname "${BASH_SOURCE[0]}")/msys2_pins.txt"
repo=${MSYS2_REPO:-https://repo.msys2.org/mingw/mingw64}

work=$(mktemp -d)
trap 'rm -rf "$work"' EXIT

files=()
while read -r pin_group sha256 file; do
  [ "$pin_group" = "$group" ] || continue
  wget -nv -P "$work" "$repo/$file"
  echo "$sha256  $work/$file" | sha256sum -c
  files+=("$work/$file")
done < <(grep -v '^#' "$pins")

if [ ${#files[@]} -eq 0 ]; then
  echo "No package of the group $group in $pins" >&2
  exit 1
fi

pacman -U --noconfirm "${files[@]}"
