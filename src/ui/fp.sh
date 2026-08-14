#!/data/data/com.termux/files/usr/bin/bash

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
COLOR_DIR="$ROOT_DIR/src/colors"

source "$COLOR_DIR/bse.sh"
source "$COLOR_DIR/uic.sh"
source "$COLOR_DIR/sts.sh"
source "$COLOR_DIR/mnu.sh"

CATEGORY_ID="${1:-}"
CATEGORY_NAME="${2:-Category}"
FUNCTION_ID="${3:-}"
FUNCTION_ENTRY="${4:-}"
FUNCTION_NAME="${5:-Function}"

ENTRY_FILE="$ROOT_DIR/src/functions/$FUNCTION_ENTRY"
LIB_ID=""

resolve_library() {
    if [[ ! -f "$ROOT_DIR/src/data/funcs.json" ]]; then
        return
    fi

    if ! command -v jq >/dev/null 2>&1; then
        return
    fi

    LIB_ID="$(
        jq -r --arg id "$FUNCTION_ID" '
            .functions[]
            | select(.id == $id)
            | (.library // .id)
        ' "$ROOT_DIR/src/data/funcs.json" 2>/dev/null
    )"

    if [[ -z "$LIB_ID" || "$LIB_ID" == "null" ]]; then
        LIB_ID="$FUNCTION_ID"
    fi
}

get_metadata() {
    local file="$ROOT_DIR/src/lib/$LIB_ID/$LIB_ID.json"

    if [[ ! -f "$file" || ! $(command -v jq) ]]; then
        return
    fi

    META_VERSION="$(jq -r '.version // "unknown"' "$file" 2>/dev/null)"
    META_TYPE="$(jq -r '.type // "function"' "$file" 2>/dev/null)"
    META_CATEGORY="$(jq -r '.category // "'"$CATEGORY_ID"'"' "$file" 2>/dev/null)"
}

hide_cursor() {
    printf '\033[?25l'
}

show_cursor() {
    printf '\033[?25h'
}

cleanup() {
    show_cursor
    stty echo icanon 2>/dev/null
    clear
    exit 0
}

read_key() {
    local key

    IFS= read -rsn1 key

    case "$key" in
        $'\x1b')
            IFS= read -rsn2 key

            case "$key" in
                '[A') echo "UP" ;;
                '[B') echo "DOWN" ;;
                '[D') echo "LEFT" ;;
                '[C') echo "RIGHT" ;;
            esac
            ;;

        "")
            echo "ENTER"
            ;;

        q|Q)
            echo "BACK"
            ;;
    esac
}

draw_header() {
    printf '%s' "$UI_BORDER"
    printf '╔══════════════════════════════════════════════════════╗\n'
    printf '║%s                 MFORCE ENHANCED%s                      ║\n' "$UI_TITLE" "$UI_BORDER"
    printf '╠══════════════════════════════════════════════════════╣\n'
    printf '║%s                 FUNCTION PREVIEW%s                     ║\n' "$UI_TEXT" "$UI_BORDER"
    printf '╚══════════════════════════════════════════════════════╝\n'
    printf '%s' "$CLR_RESET"
}

draw_page() {
    clear
    draw_header

    printf '\n'
    printf '  %s%s%s\n' "$UI_TITLE" "$FUNCTION_NAME" "$CLR_RESET"
    printf '\n'

    printf '  %sCategory%s  : %s\n' "$UI_MUTED" "$CLR_RESET" "$CATEGORY_NAME"
    printf '  %sFunction%s  : %s\n' "$UI_MUTED" "$CLR_RESET" "$FUNCTION_ID"
    printf '  %sEntry%s     : %s\n' "$UI_MUTED" "$CLR_RESET" "$FUNCTION_ENTRY"

    if [[ -n "$LIB_ID" ]]; then
        printf '  %sLibrary%s   : %s\n' "$UI_MUTED" "$CLR_RESET" "$LIB_ID"
    fi

    if [[ -n "${META_VERSION:-}" ]]; then
        printf '  %sVersion%s   : %s\n' "$UI_MUTED" "$CLR_RESET" "$META_VERSION"
    fi

    if [[ -n "${META_TYPE:-}" ]]; then
        printf '  %sType%s      : %s\n' "$UI_MUTED" "$CLR_RESET" "$META_TYPE"
    fi

    printf '\n'

    if [[ -f "$ENTRY_FILE" ]]; then
        printf '  %s● Entry point available%s\n' "$STATUS_SUCCESS" "$CLR_RESET"
    else
        printf '  %s● Entry point missing%s\n' "$STATUS_ERROR" "$CLR_RESET"
    fi

    printf '\n'
    printf '  %sENTER%s Run function\n' "$MENU_KEY" "$CLR_RESET"
    printf '  %sQ%s Back\n' "$MENU_KEY" "$CLR_RESET"
}

run_function() {
    stty echo icanon 2>/dev/null
    show_cursor

    if [[ ! -f "$ENTRY_FILE" ]]; then
        clear

        printf '%s[ERROR]%s Function entry point not found.\n' \
            "$STATUS_ERROR" "$CLR_RESET"

        printf '\n'
        printf '  %s%s\n' "$UI_MUTED" "$ENTRY_FILE"
        printf '\n'
        printf '%sPress ENTER to return...%s\n' "$UI_MUTED" "$CLR_RESET"

        read -r

        stty -echo -icanon min 1 time 0 2>/dev/null
        hide_cursor
        return
    fi

    exec "$ENTRY_FILE"
}

main() {
    resolve_library
    get_metadata

    hide_cursor
    stty -echo -icanon min 1 time 0 2>/dev/null

    while true; do
        draw_page

        case "$(read_key)" in
            ENTER)
                run_function
                ;;

            BACK)
                stty echo icanon 2>/dev/null
                show_cursor

                exec "$ROOT_DIR/src/ui/fs.sh" \
                    "$CATEGORY_ID" \
                    "$CATEGORY_NAME"
                ;;
        esac
    done
}

trap cleanup INT TERM

main
