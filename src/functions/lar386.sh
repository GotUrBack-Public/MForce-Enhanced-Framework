#!/data/data/com.termux/files/usr/bin/bash

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
LIB_DIR="$ROOT_DIR/src/lib/frc386"

if [[ ! -f "$LIB_DIR/frc386.sh" ]]; then
    printf '\033[1;31m[ERROR]\033[0m Library not found.\n'
    printf '  %s\n' "$LIB_DIR/frc386.sh"
    exit 1
fi

exec "$LIB_DIR/frc386.sh"
