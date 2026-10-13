#!/data/data/com.termux/files/usr/bin/bash

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
source "$ROOT_DIR/src/core/runtime.sh" || exit 1
LIB_DIR="$ROOT_DIR/src/lib/sys193"

exec bash "$LIB_DIR/sys193.sh" "$@"
