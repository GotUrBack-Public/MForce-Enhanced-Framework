#!/data/data/com.termux/files/usr/bin/bash

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
DATA_FILE="$ROOT_DIR/src/data/funcs.json"

CATEGORY_ID="${1:-}"
CATEGORY_NAME="${2:-Category}"

VERSION="v0.01.0"

FUNCTIONS=()
FUNCTION_IDS=()
FUNCTION_ENTRIES=()
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

trap cleanup INT TERM

load_functions() {

    if [[ -z "$CATEGORY_ID" ]]; then
        clear
        printf '\033[1;31m[ERROR]\033[0m No category selected.\n'
        exit 1
    fi

    if [[ ! -f "$DATA_FILE" ]]; then
        clear
        printf '\033[1;31m[ERROR]\033[0m Function database not found.\n'
        printf '\n'
        printf 'Missing:\n'
        printf '  %s\n' "$DATA_FILE"
        printf '\n'
        printf 'Press ENTER to exit...\n'
        read -r
        exit 1
    fi

    if ! command -v jq >/dev/null 2>&1; then
        clear
        printf '\033[1;31m[ERROR]\033[0m jq is not installed.\n'
        printf '\n'
        printf 'Install it with:\n'
        printf '  pkg install jq\n'
        printf '\n'
        printf 'Press ENTER to exit...\n'
        read -r
        exit 1
    fi

    while IFS=$'\t' read -r id entry name; do
        FUNCTION_IDS+=("$id")
        FUNCTION_ENTRIES+=("$entry")
        FUNCTIONS+=("$name")
    done < <(
        jq -r --arg category "$CATEGORY_ID" '
            .functions[]
            | select(.category == $category and .enabled == true)
            | [.id, .entry, .name]
            | @tsv
        ' "$DATA_FILE"
    )
}

draw_header() {
    printf '\033[1;36m'
    printf '╔══════════════════════════════════════════════════════╗\n'
    printf '║                 MFORCE ENHANCED                      ║\n'
    printf '╠══════════════════════════════════════════════════════╣\n'
    printf '║ %-52s ║\n' "CATEGORY: $CATEGORY_NAME"
    printf '╚══════════════════════════════════════════════════════╝\n'
    printf '\033[0m'
}

draw_menu() {
    local i

    printf '\n'

    if [[ ${#FUNCTIONS[@]} -eq 0 ]]; then
        printf '  \033[1;33mNo functions available.\033[0m\n'
    else
        for i in "${!FUNCTIONS[@]}"; do
            if [[ "$i" -eq "$SELECTED" ]]; then
                printf '  \033[1;36m❯ %s\033[0m\n' "${FUNCTIONS[$i]}"
            else
                printf '    \033[90m%s\033[0m\n' "${FUNCTIONS[$i]}"
            fi
        done
    fi

    printf '\n'
    printf '  \033[90m↑ ↓\033[0m Navigate   '
    printf '\033[90mENTER\033[0m Select   '
    printf '\033[90mQ\033[0m Back\n'
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

    load_functions

    hide_cursor
    stty -echo -icanon min 1 time 0 2>/dev/null

    while true; do

        clear

        draw_header
        draw_menu

        case "$(read_key)" in

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

                    clear

                    printf '\033[1;36mFunction selected\033[0m\n\n'
                    printf '  Name:  %s\n' "$FUNCTION_NAME"
                    printf '  ID:    %s\n' "$FUNCTION_ID"
                    printf '  Entry: %s\n\n' "$FUNCTION_ENTRY"

                    printf '\033[90mPress ENTER to return...\033[0m\n'

                    while true; do
                        IFS= read -rsn1 key
                        [[ -z "$key" ]] && break
                    done
                fi
                ;;

            QUIT)
                cleanup
                ;;

        esac
    done
}

main
