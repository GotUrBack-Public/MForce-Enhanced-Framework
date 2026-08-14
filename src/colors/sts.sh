#!/data/data/com.termux/files/usr/bin/bash

COLORS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [[ -z "${CLR_RESET:-}" ]]; then
    source "$COLORS_DIR/bse.sh"
fi

STATUS_SUCCESS="${CLR_BRIGHT_GREEN}"
STATUS_WARNING="${CLR_BRIGHT_YELLOW}"
STATUS_ERROR="${CLR_BRIGHT_RED}"
STATUS_INFO="${CLR_BRIGHT_BLUE}"
STATUS_MUTED="${CLR_GRAY}"
