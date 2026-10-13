#!/data/data/com.termux/files/usr/bin/bash

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
source "$ROOT_DIR/src/core/runtime.sh" || exit 1
CONFIG_FILE="$ROOT_DIR/cfg/zrk391.json"
COLOR_DIR="$ROOT_DIR/src/colors"

source "$COLOR_DIR/bse.sh" || exit 1
source "$COLOR_DIR/uic.sh" || exit 1
source "$COLOR_DIR/sts.sh" || exit 1
source "$COLOR_DIR/mnu.sh" || exit 1

VERSION="unknown"
NAME="MForce Enhanced Framework"
LICENSE="unknown"
LANGUAGE="unknown"
PLATFORM="unknown"
REPOSITORY="unknown"

load_config() {
    mf_require_json "$CONFIG_FILE" project || exit 1
    if [[ ! -f "$CONFIG_FILE" ]]; then
        return
    fi

    if ! command -v jq >/dev/null 2>&1; then
        return
    fi

    NAME="$(jq -r '.name // "MForce Enhanced Framework"' "$CONFIG_FILE")"
    VERSION="$(jq -r '.version // "unknown"' "$CONFIG_FILE")"
    LICENSE="$(jq -r '.license // "unknown"' "$CONFIG_FILE")"
    LANGUAGE="$(jq -r '.language // "unknown"' "$CONFIG_FILE")"
    PLATFORM="$(jq -r '.platform // "unknown"' "$CONFIG_FILE")"
    REPOSITORY="$(jq -r '.repository // "unknown"' "$CONFIG_FILE")"
}

draw_header() {
    printf '%s' "$UI_BORDER"
    printf '╔══════════════════════════════════════════════════════╗\n'
    printf '║%s                 MFORCE ENHANCED%s                      ║\n' "$UI_TITLE" "$UI_BORDER"
    printf '╠══════════════════════════════════════════════════════╣\n'
    printf '║%s                    ABOUT%s                             ║\n' "$UI_TEXT" "$UI_BORDER"
    printf '╚══════════════════════════════════════════════════════╝\n'
    printf '%s' "$CLR_RESET"
}

draw_page() {
    clear
    draw_header

    printf '\n'
    printf '  %s%s%s\n' "$UI_TITLE" "$NAME" "$CLR_RESET"
    printf '\n'

    printf '  %sVersion%s     : %s\n' "$UI_MUTED" "$CLR_RESET" "$VERSION"
    printf '  %sLicense%s     : %s\n' "$UI_MUTED" "$CLR_RESET" "$LICENSE"
    printf '  %sLanguage%s    : %s\n' "$UI_MUTED" "$CLR_RESET" "$LANGUAGE"
    printf '  %sPlatform%s    : %s\n' "$UI_MUTED" "$CLR_RESET" "$PLATFORM"
    printf '  %sRepository%s  : %s\n' "$UI_MUTED" "$CLR_RESET" "$REPOSITORY"

    printf '\n'
    printf '  %sA modular terminal framework built for Termux.%s\n' \
        "$UI_TEXT" "$CLR_RESET"

    printf '\n'
    printf '  %sENTER%s Back\n' "$MENU_KEY" "$CLR_RESET"
}

read_key() { mf_read_key "BACK"; }

main() {
    load_config

    hide_cursor
    stty -echo -icanon min 1 time 0 2>/dev/null

    while true; do
        draw_page

        read_key
        case "$MF_KEY" in
            EOF) exit 0 ;;
            ENTER|BACK)
                stty echo icanon 2>/dev/null
                show_cursor

                exec bash "$ROOT_DIR/src/ui/cs.sh"
                ;;
        esac
    done
}


main
