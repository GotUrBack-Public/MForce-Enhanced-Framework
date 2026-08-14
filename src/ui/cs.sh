#!/data/data/com.termux/files/usr/bin/bash

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
DATA_FILE="$ROOT_DIR/src/data/cats.json"
COLOR_DIR="$ROOT_DIR/src/colors"

source "$COLOR_DIR/bse.sh"
source "$COLOR_DIR/uic.sh"
source "$COLOR_DIR/sts.sh"
source "$COLOR_DIR/mnu.sh"

CATEGORIES=()
CATEGORY_IDS=()
SELECTED=0
MENU_ITEMS=()

load_categories() {
    if [[ ! -f "$DATA_FILE" ]]; then
        clear
        printf '%s[ERROR]%s Category database not found.\n' "$STATUS_ERROR" "$CLR_RESET"
        printf '\n'
        printf '%sMissing:%s\n' "$UI_MUTED" "$CLR_RESET"
        printf '  %s\n' "$DATA_FILE"
        printf '\n'
        printf '%sPress ENTER to exit...%s\n' "$UI_MUTED" "$CLR_RESET"
        read -r
        exit 1
    fi

    if ! command -v jq >/dev/null 2>&1; then
        clear
        printf '%s[ERROR]%s jq is not installed.\n' "$STATUS_ERROR" "$CLR_RESET"
        printf '\n'
        printf '%sInstall it with:%s\n' "$UI_MUTED" "$CLR_RESET"
        printf '  pkg install jq\n'
        printf '\n'
        printf '%sPress ENTER to exit...%s\n' "$UI_MUTED" "$CLR_RESET"
        read -r
        exit 1
    fi

    while IFS=$'\t' read -r id name; do
        CATEGORY_IDS+=("$id")
        CATEGORIES+=("$name")
    done < <(
        jq -r '
            .categories[]
            | select(.enabled == true)
            | [.id, .name]
            | @tsv
        ' "$DATA_FILE"
    )

    MENU_ITEMS=("${CATEGORIES[@]}" "Category Info" "About")
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

draw_header() {
    printf '%s' "$UI_BORDER"
    printf '╔══════════════════════════════════════════════════════╗\n'
    printf '║%s                 MFORCE ENHANCED%s                      ║\n' "$UI_TITLE" "$UI_BORDER"
    printf '╠══════════════════════════════════════════════════════╣\n'
    printf '║%s                  MAIN MENU%s                           ║\n' "$UI_TEXT" "$UI_BORDER"
    printf '╚══════════════════════════════════════════════════════╝\n'
    printf '%s' "$CLR_RESET"
}

draw_menu() {
    local i
    local total=${#MENU_ITEMS[@]}

    printf '\n'

    for i in "${!MENU_ITEMS[@]}"; do
        if [[ "$i" -eq "$SELECTED" ]]; then
            printf '  %s❯ %s%s\n' \
                "$MENU_SELECTED" \
                "${MENU_ITEMS[$i]}" \
                "$CLR_RESET"
        else
            printf '    %s%s%s\n' \
                "$MENU_NORMAL" \
                "${MENU_ITEMS[$i]}" \
                "$CLR_RESET"
        fi

        if [[ "$i" -eq $((${#CATEGORIES[@]} - 1)) ]]; then
            printf '\n'
        fi
    done

    printf '\n'
    printf '  %s↑ ↓%s Navigate   %sENTER%s Select   %sQ%s Exit\n' \
        "$MENU_KEY" "$CLR_RESET" \
        "$MENU_KEY" "$CLR_RESET" \
        "$MENU_KEY" "$CLR_RESET"
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
            echo "QUIT"
            ;;
    esac
}

open_category() {
    local index="$SELECTED"

    stty echo icanon 2>/dev/null
    show_cursor

    exec "$ROOT_DIR/src/ui/cp.sh" \
        "${CATEGORY_IDS[$index]}" \
        "${CATEGORIES[$index]}"
}

open_about() {
    stty echo icanon 2>/dev/null
    show_cursor

    exec "$ROOT_DIR/src/ui/ap.sh"
}

main() {
    load_categories

    hide_cursor
    stty -echo -icanon min 1 time 0 2>/dev/null

    while true; do
        clear
        draw_header
        draw_menu

        case "$(read_key)" in
            UP)
                ((SELECTED--))

                if (( SELECTED < 0 )); then
                    SELECTED=$((${#MENU_ITEMS[@]} - 1))
                fi
                ;;

            DOWN)
                ((SELECTED++))

                if (( SELECTED >= ${#MENU_ITEMS[@]} )); then
                    SELECTED=0
                fi
                ;;

            ENTER)
                if (( SELECTED < ${#CATEGORIES[@]} )); then
                    open_category
                elif (( SELECTED == ${#CATEGORIES[@]} )); then
                    if (( ${#CATEGORIES[@]} > 0 )); then
                        open_category
                    fi
                else
                    open_about
                fi
                ;;

            QUIT)
                cleanup
                ;;
        esac
    done
}

trap cleanup INT TERM

main
