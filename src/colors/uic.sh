#!/data/data/com.termux/files/usr/bin/bash

COLORS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [[ -z "${CLR_RESET:-}" ]]; then
    source "$COLORS_DIR/bse.sh"
fi

UI_TITLE="${CLR_BRIGHT_CYAN}"
UI_BORDER="${CLR_CYAN}"
UI_TEXT="${CLR_WHITE}"
UI_MUTED="${CLR_GRAY}"
UI_SELECTED="${CLR_BRIGHT_CYAN}"
UI_SUCCESS="${CLR_BRIGHT_GREEN}"
UI_WARNING="${CLR_BRIGHT_YELLOW}"
UI_ERROR="${CLR_BRIGHT_RED}"
UI_INFO="${CLR_BRIGHT_BLUE}"
