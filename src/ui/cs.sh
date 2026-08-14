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

    if [[ ${#CATEGORIES[@]} -eq 0 ]]; then
        clear
        printf '%s[WARNING]%s No categories available.\n' "$STATUS_WARNING" "$CLR_RESET"
        printf '\n'
        printf '%sPress ENTER to exit...%s\n' "$UI_MUTED" "$CLR_RESET"
        read -r
        exit 0
    fi
}

draw_header() {
    printf '%s' "$UI_BORDER"
    printf '╔══════════════════════════════════════════════════════╗\n'
    printf '║%s                 MFORCE ENHANCED%s                      ║\n' "$UI_TITLE" "$UI_BORDER"
    printf '╠══════════════════════════════════════════════════════╣\n'
    printf '║%s                 CATEGORY SELECT%s                      ║\n' "$UI_TEXT" "$UI_BORDER"
    printf '╚══════════════════════════════════════════════════════╝\n'
    printf '%s' "$CLR_RESET"
}

draw_menu() {
    local i

    printf '\n'

    for i in "${!CATEGORIES[@]}"; do
        if [[ "$i" -eq "$SELECTED" ]]; then
            printf '  %s❯ %s%s\n' "$MENU_SELECTED" "${CATEGORIES[$i]}" "$CLR_RESET"
        else
            printf '    %s%s%s\n' "$MENU_NORMAL" "${CATEGORIES[$i]}" "$CLR_RESET"
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
                    SELECTED=$((${#CATEGORIES[@]} - 1))
                fi
                ;;

            DOWN)
                ((SELECTED++))

                if (( SELECTED >= ${#CATEGORIES[@]} )); then
                    SELECTED=0
                fi
                ;;

            ENTER)
                SELECTED_ID="${CATEGORY_IDS[$SELECTED]}"
                SELECTED_NAME="${CATEGORIES[$SELECTED]}"

                stty echo icanon 2>/dev/null
                show_cursor

                exec "$ROOT_DIR/src/ui/fs.sh" \
                    "$SELECTED_ID" \
                    "$SELECTED_NAME"
                ;;

            QUIT)
                cleanup
                ;;
        esac
    done
}

trap cleanup INT TERM

main
