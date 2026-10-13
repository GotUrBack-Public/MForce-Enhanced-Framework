#!/data/data/com.termux/files/usr/bin/bash

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
source "$ROOT_DIR/src/core/runtime.sh" || exit 1
DATA_FILE="$ROOT_DIR/src/data/cats.json"
COLOR_DIR="$ROOT_DIR/src/colors"

source "$COLOR_DIR/bse.sh" || exit 1
source "$COLOR_DIR/uic.sh" || exit 1
source "$COLOR_DIR/sts.sh" || exit 1
source "$COLOR_DIR/mnu.sh" || exit 1

CATEGORIES=()
CATEGORY_IDS=()
SELECTED=0
LAST_CATEGORY=0
MENU_ITEMS=()

load_categories() {
    mf_require_json "$DATA_FILE" categories || exit 1
    if [[ ! -f "$DATA_FILE" ]]; then
        clear
        printf '%s[ERROR]%s Category database not found.\n' "$STATUS_ERROR" "$CLR_RESET"
        printf '\n'
        printf '%sMissing:%s\n' "$UI_MUTED" "$CLR_RESET"
        printf '  %s\n' "$DATA_FILE"
        printf '\n'
        printf '%sPress ENTER to exit...%s\n' "$UI_MUTED" "$CLR_RESET"
        read -r || exit 0
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
        read -r || exit 0
        exit 1
    fi

    local rows
    rows="$(
        jq -r '
            .categories[]
            | select(.enabled == true)
            | [.id, .name]
            | @tsv
        ' "$DATA_FILE"
    )" || exit 1

    while IFS=$'\t' read -r id name; do
        [[ -n "$id" ]] || continue
        CATEGORY_IDS+=("$id")
        CATEGORIES+=("$name")
    done <<< "$rows"

    MENU_ITEMS=("${CATEGORIES[@]}" "Category Info" "About")
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

read_key() { mf_read_key "QUIT"; }

open_category() {
    local index="${1:-$SELECTED}"
    [[ -n "${CATEGORY_IDS[$index]:-}" ]] || return 1

    stty echo icanon 2>/dev/null
    show_cursor

    exec bash "$ROOT_DIR/src/ui/cp.sh" \
        "${CATEGORY_IDS[$index]}" \
        "${CATEGORIES[$index]}"
}

open_about() {
    stty echo icanon 2>/dev/null
    show_cursor

    exec bash "$ROOT_DIR/src/ui/ap.sh"
}

main() {
    load_categories

    hide_cursor
    stty -echo -icanon min 1 time 0 2>/dev/null

    while true; do
        clear
        if (( SELECTED < ${#CATEGORIES[@]} )); then LAST_CATEGORY="$SELECTED"; fi
        draw_header
        draw_menu

        read_key
        case "$MF_KEY" in
            EOF) exit 0 ;;
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
                        open_category "$LAST_CATEGORY"
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


main
