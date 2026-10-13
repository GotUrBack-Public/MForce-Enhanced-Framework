#!/data/data/com.termux/files/usr/bin/bash

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$ROOT_DIR/src/core/runtime.sh" || exit 1

exec bash "$ROOT_DIR/src/ui/epos.sh" "$@"
