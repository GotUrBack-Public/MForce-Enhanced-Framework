#!/data/data/com.termux/files/usr/bin/bash
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$ROOT_DIR/src/core/runtime.sh" || exit 1
source "$ROOT_DIR/src/core/mariadb.sh" || exit 1
mf_db_start
trap 'mf_db_stop' EXIT
bash "$ROOT_DIR/src/ui/epos.sh" "$@"
