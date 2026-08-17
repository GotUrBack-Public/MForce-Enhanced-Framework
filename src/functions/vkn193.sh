#!/data/data/com.termux/files/usr/bin/bash

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
LIB_DIR="$ROOT_DIR/src/lib/sys193"

exec "$LIB_DIR/sys193.sh"
