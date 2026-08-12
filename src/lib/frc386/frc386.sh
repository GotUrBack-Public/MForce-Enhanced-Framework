#!/data/data/com.termux/files/usr/bin/bash

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
LIB_DIR="$ROOT_DIR/src/lib/frc386"

CONFIG_FILE="$LIB_DIR/frc386.conf"
HELP_FILE="$LIB_DIR/frc386.help"
DATA_FILE="$LIB_DIR/data.json"

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

read -r

exec "$ROOT_DIR/src/ui/fs.sh" "net" "Network"
