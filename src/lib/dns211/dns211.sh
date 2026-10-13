#!/usr/bin/env bash
# Passive authorized OSINT / no rate-limit bypass or mass scanning.
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
source "$ROOT_DIR/src/core/runtime.sh" || exit 1
mf_module_resources "dns211" "${1:-}" || exit 1
if ! command -v python3 >/dev/null 2>&1; then
  printf "%s\n" "Python 3 is required (Termux: pkg install python; Linux: apt install python3)." >&2
  exit 1
fi
if (($#)); then exec python3 "$ROOT_DIR/src/osint/inspect.py" dns "$@"; fi
stty echo icanon 2>/dev/null || :
show_cursor
python3 "$ROOT_DIR/src/osint/inspect.py" dns
status=$?
if [[ -t 0 && -t 1 ]]; then exec bash "$ROOT_DIR/src/ui/fs.sh" net "Network"; fi
exit "$status"
