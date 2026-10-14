#!/usr/bin/env bash
# Local Secret Scanner — Educational Purpose / Professional Usage.
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
source "$ROOT_DIR/src/core/runtime.sh" || exit 1
mf_module_resources "sec601" "${1:-}" || exit 1
if ! command -v python3 >/dev/null 2>&1; then
  printf '%s\n' 'Python 3 required (Termux: pkg install python).' >&2
  exit 1
fi
if (($#)); then exec python3 "$ROOT_DIR/src/defensive/secrets_audit.py" "$@"; fi
stty echo icanon 2>/dev/null || :
show_cursor
printf '%s\n' 'Local Secret Scanner — offline only'
read -r -p 'Local file or directory: ' target || exit 1
python3 "$ROOT_DIR/src/defensive/secrets_audit.py" "$target"
status=$?
if [[ -t 0 && -t 1 ]]; then
  read -r -p 'Press Enter to return...' _ || :
  exec bash "$ROOT_DIR/src/ui/fs.sh" defensive "Defensive Security"
fi
exit "$status"
