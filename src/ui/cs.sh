#!/data/data/com.termux/files/usr/bin/bash

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

VERSION="v0.01.0"
TITLE="MForce Enhanced Framework"

CATEGORIES=(
    "Network"
    "System"
    "OSINT"
    "Utilities"
    "Files"
    "Settings"
)

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
                '[A')
                    echo "UP"
                    ;;
                '[B')
                    echo "DOWN"
                    ;;
                '[D')
                    echo "LEFT"
                    ;;
                '[C')
                    echo "RIGHT"
                    ;;
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
                clear

                printf '\033[1;36m'
                printf 'Selected category:\n'
                printf '\033[0m\n'

                printf '  %s\n\n' "${CATEGORIES[$SELECTED]}"
                printf '\033[90mPress ENTER to continue...\033[0m\n'

                while true; do
                    IFS= read -rsn1 key

                    [[ -z "$key" ]] && break
                done
                ;;

            QUIT)
                cleanup
                ;;

        esac
    done
}

main


