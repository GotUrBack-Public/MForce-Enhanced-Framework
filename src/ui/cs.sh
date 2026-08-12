#!/data/data/com.termux/files/usr/bin/bash

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
DATA_FILE="$ROOT_DIR/src/data/cats.json"

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
        printf '\033[1;31m[ERROR]\033[0m Category database not found.\n'
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
        printf '\033[1;33m[WARNING]\033[0m No categories available.\n'
        printf '\n'
        printf 'Press ENTER to exit...\n'
        read -r
        exit 0
    fi
}

draw_header() {
    printf '\033[1;36m'
    printf '╔══════════════════════════════════════════════════════╗\n'
    printf '║                 MFORCE ENHANCED                      ║\n'
    printf '╠══════════════════════════════════════════════════════╣\n'
    printf '║                 CATEGORY SELECT                      ║\n'
    printf '╚══════════════════════════════════════════════════════╝\n'
    printf '\033[0m'
}

draw_menu() {
    local i

    printf '\n'

    for i in "${!CATEGORIES[@]}"; do
        if [[ "$i" -eq "$SELECTED" ]]; then
            printf '  \033[1;36m❯ %s\033[0m\n' "${CATEGORIES[$i]}"
        else
            printf '    \033[90m%s\033[0m\n' "${CATEGORIES[$i]}"
        fi
    done

    printf '\n'
    printf '  \033[90m↑ ↓\033[0m Navigate   '
    printf '\033[90mENTER\033[0m Select   '
    printf '\033[90mQ\033[0m Exit\n'
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

main
