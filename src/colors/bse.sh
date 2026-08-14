#!/data/data/com.termux/files/usr/bin/bash

COLORS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
COLORS_FILE="$COLORS_DIR/clrs.json"

if [[ ! -f "$COLORS_FILE" ]]; then
    return 1 2>/dev/null || exit 1
fi

if ! command -v jq >/dev/null 2>&1; then
    return 1 2>/dev/null || exit 1
fi

CLR_RESET="$(jq -r '.reset' "$COLORS_FILE")"
CLR_BOLD="$(jq -r '.bold' "$COLORS_FILE")"
CLR_DIM="$(jq -r '.dim' "$COLORS_FILE")"

CLR_BLACK="$(jq -r '.black' "$COLORS_FILE")"
CLR_RED="$(jq -r '.red' "$COLORS_FILE")"
CLR_GREEN="$(jq -r '.green' "$COLORS_FILE")"
CLR_YELLOW="$(jq -r '.yellow' "$COLORS_FILE")"
CLR_BLUE="$(jq -r '.blue' "$COLORS_FILE")"
CLR_MAGENTA="$(jq -r '.magenta' "$COLORS_FILE")"
CLR_CYAN="$(jq -r '.cyan' "$COLORS_FILE")"
CLR_WHITE="$(jq -r '.white' "$COLORS_FILE")"
CLR_GRAY="$(jq -r '.gray' "$COLORS_FILE")"

CLR_BRIGHT_RED="$(jq -r '.bright_red' "$COLORS_FILE")"
CLR_BRIGHT_GREEN="$(jq -r '.bright_green' "$COLORS_FILE")"
CLR_BRIGHT_YELLOW="$(jq -r '.bright_yellow' "$COLORS_FILE")"
CLR_BRIGHT_BLUE="$(jq -r '.bright_blue' "$COLORS_FILE")"
CLR_BRIGHT_MAGENTA="$(jq -r '.bright_magenta' "$COLORS_FILE")"
CLR_BRIGHT_CYAN="$(jq -r '.bright_cyan' "$COLORS_FILE")"
CLR_BRIGHT_WHITE="$(jq -r '.bright_white' "$COLORS_FILE")"
