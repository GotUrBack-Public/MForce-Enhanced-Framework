#!/data/data/com.termux/files/usr/bin/bash

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
source "$ROOT_DIR/src/core/runtime.sh" || exit 1
mf_module_resources "frc386" "${1:-}" || exit 1
LIB_DIR="$ROOT_DIR/src/lib/frc386"

jq -e '.id == "frc386" and .resources.config == "frc386.conf" and
    .resources.help == "frc386.help" and .resources.metadata == "frc386.json" and
    .runtime.shell == "bash" and .runtime.platform == "termux"' "$LIB_DIR/data.json" >/dev/null || exit 1

clear

printf '\033[1;36m'
printf '╔══════════════════════════════════════════════════════╗\n'
printf '║                 MFORCE ENHANCED                      ║\n'
printf '╠══════════════════════════════════════════════════════╣\n'
printf '║              NETWORK INFORMATION                     ║\n'
printf '╚══════════════════════════════════════════════════════╝\n'
printf '\033[0m'

printf '\n'

if command -v ip >/dev/null 2>&1; then
    printf '\033[1;37mNetwork Interfaces\033[0m\n\n'
    ip -brief address 2>/dev/null
else
    printf '\033[1;33m[WARNING]\033[0m ip command is not available.\n'
fi

printf '\n'

if command -v hostname >/dev/null 2>&1; then
    printf '\033[1;37mHostname\033[0m\n\n'
    hostname
fi

printf '\n'
printf '\033[90mPress ENTER to return...\033[0m\n'

read -r || exit 0

exec bash "$ROOT_DIR/src/ui/fs.sh" "net" "Network"
