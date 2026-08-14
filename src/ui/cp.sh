#!/data/data/com.termux/files/usr/bin/bash

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
DATA_DIR="$ROOT_DIR/src/data"
COLOR_DIR="$ROOT_DIR/src/colors"

source "$COLOR_DIR/bse.sh"
source "$COLOR_DIR/uic.sh"
source "$COLOR_DIR/sts.sh"
source "$COLOR_DIR/mnu.sh"

CATEGORY_ID="${1:-}"
CATEGORY_NAME="${2:-Category}"

FUNCTION_COUNT=0
ENABLED_COUNT=0

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

load_category_data() {
    if [[ -z "$CATEGORY_ID" ]]; then
        return 1
    fi

    if [[ ! -f "$DATA_DIR/funcs.json" ]]; then
        return 1
    fi

    if ! command -v jq >/dev/null 2>&1; then
        return 1
    fi

    FUNCTION_COUNT="$(
        jq -r --arg category "$CATEGORY_ID" '
            [.functions[] | select(.category == $category)] | length
        ' "$DATA_DIR/funcs.json"
    )"

    ENABLED_COUNT="$(
        jq -r --arg category "$CATEGORY_ID" '
            [.functions[] | select(.category == $category and .enabled == true)] | length
        ' "$DATA_DIR/funcs.json"
    )"
}

draw_header() {
    printf '%s' "$UI_BORDER"
    printf '╔══════════════════════════════════════════════════════╗\n'
    printf '║%s                 MFORCE ENHANCED%s                      ║\n' "$UI_TITLE" "$UI_BORDER"
    printf '╠══════════════════════════════════════════════════════╣\n'
    printf '║%s                  CATEGORY INFO%s                       ║\n' "$UI_TEXT" "$UI_BORDER"
    printf '╚══════════════════════════════════════════════════════╝\n'
    printf '%s' "$CLR_RESET"
}

draw_page() {
    clear
    draw_header

    printf '\n'
    printf '  %s%s%s\n' "$UI_TITLE" "$CATEGORY_NAME" "$CLR_RESET"
    printf '\n'

    printf '  %sCategory ID%s : %s\n' "$UI_MUTED" "$CLR_RESET" "$CATEGORY_ID"
    printf '  %sFunctions%s   : %s\n' "$UI_MUTED" "$CLR_RESET" "$FUNCTION_COUNT"
    printf '  %sEnabled%s     : %s\n' "$UI_MUTED" "$CLR_RESET" "$ENABLED_COUNT"

    printf '\n'

    if (( ENABLED_COUNT > 0 )); then
        printf '  %s● Category available%s\n' \
            "$STATUS_SUCCESS" "$CLR_RESET"
    else
        printf '  %s● No enabled functions%s\n' \
            "$STATUS_WARNING" "$CLR_RESET"
    fi

    printf '\n'
    printf '  %sENTER%s Open functions\n' "$MENU_KEY" "$CLR_RESET"
    printf '  %sQ%s Back\n' "$MENU_KEY" "$CLR_RESET"
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

main() {
    load_category_data

    hide_cursor
    stty -echo -icanon min 1 time 0 2>/dev/null

    while true; do
        draw_page

        case "$(read_key)" in
            ENTER)
                stty echo icanon 2>/dev/null
                show_cursor

                exec "$ROOT_DIR/src/ui/fs.sh" \
                    "$CATEGORY_ID" \
                    "$CATEGORY_NAME"
                ;;

            BACK)
                stty echo icanon 2>/dev/null
                show_cursor

                exec "$ROOT_DIR/src/ui/cs.sh"
                ;;
        esac
    done
}

trap cleanup INT TERM

main
