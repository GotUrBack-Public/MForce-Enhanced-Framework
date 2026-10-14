#!/usr/bin/env bash
# Exposure Path Auditor — Educational Purpose / Professional Usage.
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
source "$ROOT_DIR/src/core/runtime.sh" || exit 1
mf_module_resources "pth407" "${1:-}" || exit 1
if ! command -v python3 >/dev/null 2>&1; then
  printf '%s\n' 'Python 3 required (Termux: pkg install python).' >&2
  exit 1
fi
if (($#)); then exec python3 "$ROOT_DIR/src/offensive/http_audit.py" paths "$@"; fi
stty echo icanon 2>/dev/null || :
show_cursor
printf '%s\n' 'Exposure Path Auditor — authorized targets only'
read -r -p 'Authorized http(s) URL: ' target || exit 1
read -r -p 'Confirm authorization for this target? [yes/NO] ' confirm || exit 1
[[ "$confirm" == yes ]] || { printf '%s\n' 'Cancelled.'; exit 1; }
python3 "$ROOT_DIR/src/offensive/http_audit.py" paths "$target" --authorized
status=$?
if [[ -t 0 && -t 1 ]]; then
  read -r -p 'Press Enter to return...' _ || :
  exec bash "$ROOT_DIR/src/ui/fs.sh" offensive "Offensive Security"
fi
exit "$status"
