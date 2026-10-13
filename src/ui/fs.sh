#!/data/data/com.termux/files/usr/bin/bash

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
source "$ROOT_DIR/src/core/runtime.sh" || exit 1
DATA_FILE="$ROOT_DIR/src/data/funcs.json"
COLOR_DIR="$ROOT_DIR/src/colors"

source "$COLOR_DIR/bse.sh" || exit 1
source "$COLOR_DIR/uic.sh" || exit 1
source "$COLOR_DIR/sts.sh" || exit 1
source "$COLOR_DIR/mnu.sh" || exit 1

CATEGORY_ID="${1:-}"
CATEGORY_NAME="${2:-Category}"

FUNCTIONS=()
FUNCTION_IDS=()
FUNCTION_ENTRIES=()
SELECTED=0

load_functions() {
    mf_require_json "$DATA_FILE" functions || exit 1
    mf_require_category "$CATEGORY_ID" || exit 1
    if [[ -z "$CATEGORY_ID" ]]; then
        clear
        printf '%s[ERROR]%s No category selected.\n' "$STATUS_ERROR" "$CLR_RESET"
        printf '\n'
        printf '%sPress ENTER to exit...%s\n' "$UI_MUTED" "$CLR_RESET"
        read -r || exit 0
        exit 1
    fi

    if [[ ! -f "$DATA_FILE" ]]; then
        clear
        printf '%s[ERROR]%s Function database not found.\n' "$STATUS_ERROR" "$CLR_RESET"
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
        jq -r --arg category "$CATEGORY_ID" '
            .functions[]
            | select(.category == $category and .enabled == true)
            | [.id, .entry, .name]
            | @tsv
        ' "$DATA_FILE"
    )" || exit 1

    while IFS=$'\t' read -r id entry name; do
        [[ -n "$id" ]] || continue
        FUNCTION_IDS+=("$id")
        FUNCTION_ENTRIES+=("$entry")
        FUNCTIONS+=("$name")
    done <<< "$rows"
}

draw_header() {
    printf '%s' "$UI_BORDER"
    printf '╔══════════════════════════════════════════════════════╗\n'
    printf '║%s                 MFORCE ENHANCED%s                      ║\n' "$UI_TITLE" "$UI_BORDER"
    printf '╠══════════════════════════════════════════════════════╣\n'
    printf '║%s %-52s%s║\n' "$UI_TEXT" "CATEGORY: $CATEGORY_NAME" "$UI_BORDER"
    printf '╠══════════════════════════════════════════════════════╣\n'
    printf '║%s                 FUNCTION SELECT%s                     ║\n' "$UI_TEXT" "$UI_BORDER"
    printf '╚══════════════════════════════════════════════════════╝\n'
    printf '%s' "$CLR_RESET"
}

draw_menu() {
    local i

    printf '\n'

    if [[ ${#FUNCTIONS[@]} -eq 0 ]]; then
        printf '  %sNo functions available.%s\n' "$STATUS_WARNING" "$CLR_RESET"
    else
        for i in "${!FUNCTIONS[@]}"; do
            if [[ "$i" -eq "$SELECTED" ]]; then
                printf '  %s❯ %s%s\n' "$MENU_SELECTED" "${FUNCTIONS[$i]}" "$CLR_RESET"
            else
                printf '    %s%s%s\n' "$MENU_NORMAL" "${FUNCTIONS[$i]}" "$CLR_RESET"
            fi
        done
    fi

    printf '\n'
    printf '  %s↑ ↓%s Navigate   %sENTER%s Select   %sQ%s Back\n' \
        "$MENU_KEY" "$CLR_RESET" \
        "$MENU_KEY" "$CLR_RESET" \
        "$MENU_KEY" "$CLR_RESET"
}

read_key() { mf_read_key "QUIT"; }

main() {
    load_functions

    hide_cursor
    stty -echo -icanon min 1 time 0 2>/dev/null

    while true; do
        clear

        draw_header
        draw_menu

        read_key
        case "$MF_KEY" in
            EOF) exit 0 ;;
            UP)
                if (( ${#FUNCTIONS[@]} > 0 )); then
                    ((SELECTED--))

                    if (( SELECTED < 0 )); then
                        SELECTED=$((${#FUNCTIONS[@]} - 1))
                    fi
                fi
                ;;

            DOWN)
                if (( ${#FUNCTIONS[@]} > 0 )); then
                    ((SELECTED++))

                    if (( SELECTED >= ${#FUNCTIONS[@]} )); then
                        SELECTED=0
                    fi
                fi
                ;;

            ENTER)
                if (( ${#FUNCTIONS[@]} > 0 )); then
                    FUNCTION_ID="${FUNCTION_IDS[$SELECTED]}"
                    FUNCTION_ENTRY="${FUNCTION_ENTRIES[$SELECTED]}"
                    FUNCTION_NAME="${FUNCTIONS[$SELECTED]}"

                    stty echo icanon 2>/dev/null
                    show_cursor

                    exec bash "$ROOT_DIR/src/ui/fp.sh" \
                        "$CATEGORY_ID" \
                        "$CATEGORY_NAME" \
                        "$FUNCTION_ID" \
                        "$FUNCTION_ENTRY" \
                        "$FUNCTION_NAME"
                fi
                ;;

            QUIT)
                stty echo icanon 2>/dev/null
                show_cursor

                exec bash "$ROOT_DIR/src/ui/cs.sh"
                ;;
        esac
    done
}


main
