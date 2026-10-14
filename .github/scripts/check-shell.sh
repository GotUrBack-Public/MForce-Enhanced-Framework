#!/usr/bin/env bash
# Validate every shell script. Only suppress known cross-file false positives.
set -euo pipefail
command -v shellcheck >/dev/null || { printf 'shellcheck is required\n' >&2; exit 127; }

# ShellCheck analyzes each file independently. The color palette and runtime
# exports are consumed after being sourced from other scripts (SC2034).
# runtime.sh sources dynamically assembled classes*.lib files (SC1090).
# These exceptions are scoped to the exact existing files, not the whole repo.
while IFS= read -r -d '' file; do
  case "$file" in
    ./src/colors/*.sh|./src/auth/sns.sh|./src/ui/fp.sh|./src/ui/ap.sh|./src/ui/cs.sh)
      shellcheck --severity=warning --exclude=SC2034 "$file"
      ;;
    ./src/core/runtime.sh)
      shellcheck --severity=warning --exclude=SC2034,SC1090 "$file"
      ;;
    *)
      shellcheck --severity=warning "$file"
      ;;
  esac
done < <(find . -type f \( -name '*.sh' -o -name '*.bash' \) -not -path './.git/*' -print0)
