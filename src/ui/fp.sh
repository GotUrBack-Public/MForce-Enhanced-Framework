#!/data/data/com.termux/files/usr/bin/bash

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
source "$ROOT_DIR/src/core/runtime.sh" || exit 1
COLOR_DIR="$ROOT_DIR/src/colors"

source "$COLOR_DIR/bse.sh" || exit 1
source "$COLOR_DIR/uic.sh" || exit 1
source "$COLOR_DIR/sts.sh" || exit 1
source "$COLOR_DIR/mnu.sh" || exit 1

CATEGORY_ID="${1:-}"
CATEGORY_NAME="${2:-Category}"
FUNCTION_ID="${3:-}"
FUNCTION_ENTRY="${4:-}"
FUNCTION_NAME="${5:-Function}"

ENTRY_FILE="$ROOT_DIR/src/functions/$FUNCTION_ENTRY"
LIB_ID=""

resolve_library() {
    mf_require_json "$ROOT_DIR/src/data/funcs.json" functions || exit 1
    mf_require_category "$CATEGORY_ID" || exit 1
    jq -e --arg id "$FUNCTION_ID" --arg entry "$FUNCTION_ENTRY" --arg category "$CATEGORY_ID" \
        '.functions | any(.id == $id and .entry == $entry and .category == $category and .enabled)' \
        "$ROOT_DIR/src/data/funcs.json" >/dev/null || exit 1
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

    mf_require_json "$file" metadata || exit 1

    META_VERSION="$(jq -r '.version // "unknown"' "$file" 2>/dev/null)"
    META_TYPE="$(jq -r '.type // "function"' "$file" 2>/dev/null)"
    META_CATEGORY="$(jq -r --arg category "$CATEGORY_ID" '.category // $category' "$file" 2>/dev/null)"
}

read_key() { mf_read_key "BACK"; }

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

        read -r || exit 0

        stty -echo -icanon min 1 time 0 2>/dev/null
        hide_cursor
        return
    fi

    exec bash "$ENTRY_FILE"
}

main() {
    resolve_library
    get_metadata

    hide_cursor
    stty -echo -icanon min 1 time 0 2>/dev/null

    while true; do
        draw_page

        read_key
        case "$MF_KEY" in
            EOF) exit 0 ;;
            ENTER)
                run_function
                ;;

            BACK)
                stty echo icanon 2>/dev/null
                show_cursor

                exec bash "$ROOT_DIR/src/ui/fs.sh" \
                    "$CATEGORY_ID" \
                    "$CATEGORY_NAME"
                ;;
        esac
    done
}


main
