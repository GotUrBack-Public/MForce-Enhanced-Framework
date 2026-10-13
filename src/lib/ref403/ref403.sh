#!/usr/bin/env bash
# MForce HTTP Reflection Inspector — no simulated output.
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
source "$ROOT_DIR/src/core/runtime.sh" || exit 1
mf_module_resources "ref403" "${1:-}" || exit 1
if ! command -v python3 >/dev/null 2>&1; then
  printf '%s\n' 'Python 3 is required (Termux: pkg install python; Linux: install python3).' >&2
  exit 1
fi
if (($#)); then exec python3 "$ROOT_DIR/src/offensive/reflection.py" "$@"; fi
stty echo icanon 2>/dev/null || :
show_cursor
printf '%s\n' 'HTTP Reflection Inspector — Educational Purpose / Professional Usage'
printf '%s\n' 'Only scan systems you own or are explicitly authorized to test.'
read -r -p 'Authorized URL with ?parameter=value: ' target || exit 1
read -r -p 'Confirm written authorization? [yes/NO] ' confirm || exit 1
[[ "$confirm" == "yes" ]] || { printf '%s\n' 'Cancelled.'; exit 1; }
python3 "$ROOT_DIR/src/offensive/reflection.py" "$target" --authorized
status=$?
if [[ -t 0 && -t 1 ]]; then
  read -r -p 'Press Enter to return...' _ || :
  exec bash "$ROOT_DIR/src/ui/fs.sh" offensive "Offensive Security"
fi
exit "$status"
