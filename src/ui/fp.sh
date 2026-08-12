#!/data/data/com.termux/files/usr/bin/bash

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

CATEGORY_ID="${1:-}"
CATEGORY_NAME="${2:-Category}"
FUNCTION_ID="${3:-}"
FUNCTION_ENTRY="${4:-}"
FUNCTION_NAME="${5:-Function}"

ENTRY_FILE="$ROOT_DIR/src/functions/$FUNCTION_ENTRY"

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

draw_page() {
    clear

    printf '\033[1;36m'
    printf '╔══════════════════════════════════════════════════════╗\n'
    printf '║                 MFORCE ENHANCED                      ║\n'
    printf '╠══════════════════════════════════════════════════════╣\n'
    printf '║                  FUNCTION PREVIEW                    ║\n'
    printf '╚══════════════════════════════════════════════════════╝\n'
    printf '\033[0m'

    printf '\n'
    printf '  \033[1;37m%s\033[0m\n' "$FUNCTION_NAME"
    printf '\n'

    printf '  Category : %s\n' "$CATEGORY_NAME"
    printf '  Function : %s\n' "$FUNCTION_ID"
    printf '  Entry    : %s\n' "$FUNCTION_ENTRY"

    printf '\n'
    printf '  \033[90mENTER  Run function\033[0m\n'
    printf '  \033[90mQ      Back\033[0m\n'
}

main() {
    hide_cursor
    stty -echo -icanon min 1 time 0 2>/dev/null

    while true; do
        draw_page

        case "$(read_key)" in
            ENTER)
                stty echo icanon 2>/dev/null
                show_cursor

                if [[ ! -f "$ENTRY_FILE" ]]; then
                    clear
                    printf '\033[1;31m[ERROR]\033[0m Function entry point not found.\n'
                    printf '\n'
                    printf 'Missing:\n'
                    printf '  %s\n' "$ENTRY_FILE"
                    printf '\n'
                    printf 'Press ENTER to return...\n'
                    read -r
                    stty -echo -icanon min 1 time 0 2>/dev/null
                    hide_cursor
                    continue
                fi

                exec "$ENTRY_FILE"
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

main
