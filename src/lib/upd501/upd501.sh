#!/usr/bin/env bash
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
source "$ROOT_DIR/src/core/runtime.sh" || exit 1
mf_module_resources upd501 "${1:-}" || exit 1
if ! command -v python3 >/dev/null 2>&1; then
  printf '%s\n' 'Python 3 required: Termux pkg install python / Linux install python3' >&2
  exit 1
fi
stty echo icanon 2>/dev/null || :
show_cursor
python3 "$ROOT_DIR/src/update/updater.py" "$@"
status=$?
if [[ -t 0 && -t 1 && $# -eq 0 ]]; then
  read -r -p 'Press Enter to return to menu...' _ || :
  exec bash "$ROOT_DIR/src/ui/fs.sh" upd "Updates"
fi
exit "$status"
