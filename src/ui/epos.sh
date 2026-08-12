#!/data/data/com.termux/files/usr/bin/bash

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

VERSION="v0.01.0"
TITLE="MForce Enhanced Framework"

clear

printf '\033[?25l'
trap 'printf "\033[?25h"; exit' EXIT INT TERM

printf '\033[1;36m'
printf '╔══════════════════════════════════════════════════════╗\n'
printf '║                                                      ║\n'
printf '║             MFORCE ENHANCED FRAMEWORK               ║\n'
printf '║                                                      ║\n'
printf '║                    %s                         ║\n' "$VERSION"
printf '║                                                      ║\n'
printf '╚══════════════════════════════════════════════════════╝\n'
printf '\033[0m'

printf '\n'
printf '\033[1;37mInitializing framework...\033[0m\n'
printf '\n'

sleep 1

printf '\033[1;32m[✓]\033[0m Framework loaded\n'
printf '\033[1;32m[✓]\033[0m Version: %s\n' "$VERSION"
printf '\033[1;32m[✓]\033[0m Root: %s\n' "$ROOT_DIR"

sleep 1

clear

printf '\033[1;36m'
printf '╔══════════════════════════════════════════════════════╗\n'
printf '║                 MFORCE ENHANCED                      ║\n'
printf '╚══════════════════════════════════════════════════════╝\n'
printf '\033[0m'

printf '\n'
printf '  Welcome to MForce Enhanced Framework\n'
printf '\n'
printf '  Version  : %s\n' "$VERSION"
printf '  Platform : Termux\n'
printf '\n'
printf '\033[90m  Press ENTER to continue...\033[0m\n'

while true; do
    IFS= read -rsn1 key

    if [[ -z "$key" ]]; then
        break
    fi
done

printf '\033[?25h'

exec "$ROOT_DIR/src/ui/cs.sh"
