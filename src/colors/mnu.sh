#!/data/data/com.termux/files/usr/bin/bash

COLORS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [[ -z "${CLR_RESET:-}" ]]; then
    source "$COLORS_DIR/bse.sh"
fi

MENU_SELECTED="${CLR_BRIGHT_CYAN}"
MENU_NORMAL="${CLR_WHITE}"
MENU_MUTED="${CLR_GRAY}"
MENU_KEY="${CLR_BRIGHT_WHITE}"
