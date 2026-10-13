#!/data/data/com.termux/files/usr/bin/bash

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
source "$ROOT_DIR/src/core/runtime.sh" || exit 1

VERSION="$MF_VERSION"

main() {
    hide_cursor

    clear

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
    printf '  \033[1;37mInitializing framework...\033[0m\n'
    printf '\n'

    sleep 0.5

    printf '  \033[1;32m[✓]\033[0m Framework loaded\n'
    printf '  \033[1;32m[✓]\033[0m Version: %s\n' "$VERSION"
    printf '  \033[1;32m[✓]\033[0m Runtime: Termux\n'

    sleep 0.8

    stty echo icanon 2>/dev/null
    show_cursor

    exec bash "$ROOT_DIR/src/auth/lgn.sh"
}


main
