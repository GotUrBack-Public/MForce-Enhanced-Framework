#!/data/data/com.termux/files/usr/bin/bash

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
AUTH_DIR="$ROOT_DIR/src/auth"
CONFIG_FILE="$AUTH_DIR/ath.json"
SESSION_DIR="${TMPDIR:-$PREFIX/tmp}/mforce-enhanced"
SESSION_FILE="$SESSION_DIR/session.json"

generate_code() {
    local chars="ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
    local code=""
    local i

    for ((i=0; i<6; i++)); do
        code+="${chars:RANDOM%${#chars}:1}"
    done

    printf '%s-%s\n' "${code:0:3}" "${code:3:3}"
}

cleanup() {
    printf '\033[?25h'
    stty echo icanon 2>/dev/null
    clear
    exit 0
}

show_header() {
    clear

    printf '\033[1;36m'
    printf '╔══════════════════════════════════════════════════════╗\n'
    printf '║                 MFORCE ENHANCED                      ║\n'
    printf '╠══════════════════════════════════════════════════════╣\n'
    printf '║                STARTUP VERIFICATION                  ║\n'
    printf '╚══════════════════════════════════════════════════════╝\n'
    printf '\033[0m'
    printf '\n'
}

verify_config() {
    if [[ ! -f "$CONFIG_FILE" ]]; then
        printf '\033[1;31m[ERROR]\033[0m Authentication configuration not found.\n'
        printf '\n'
        printf 'Missing:\n'
        printf '  %s\n' "$CONFIG_FILE"
        printf '\n'
        printf 'Press ENTER to exit...\n'
        read -r
        exit 1
    fi

    if ! command -v jq >/dev/null 2>&1; then
        printf '\033[1;31m[ERROR]\033[0m jq is required.\n'
        printf '\n'
        printf 'Install it with:\n'
        printf '  pkg install jq\n'
        printf '\n'
        printf 'Press ENTER to exit...\n'
        read -r
        exit 1
    fi
}

is_enabled() {
    jq -r '.enabled // true' "$CONFIG_FILE"
}

get_value() {
    jq -r "$1" "$CONFIG_FILE"
}

main() {
    verify_config

    if [[ "$(is_enabled)" != "true" ]]; then
        exec "$AUTH_DIR/sns.sh"
    fi

    local max_attempts
    local delay
    local attempts=0
    local code
    local input

    max_attempts="$(get_value '.max_attempts // 3')"
    delay="$(get_value '.delay_on_failure // 2')"

    code="$(generate_code)"

    printf '\033[?25l'
    stty -echo icanon 2>/dev/null

    while (( attempts < max_attempts )); do
        show_header

        printf '  \033[1;37mVerification required\033[0m\n\n'
        printf '  Enter the code shown below:\n\n'

        printf '              \033[1;33m%s\033[0m\n\n' "$code"

        printf '  Attempts remaining: \033[1;36m%d\033[0m\n\n' \
            "$((max_attempts - attempts))"

        printf '  \033[90mCode:\033[0m '

        IFS= read -r input

        input="${input// /}"
        input="${input^^}"
        code_normalized="${code^^}"
        input_normalized="${input//-/}"

        if [[ "$input_normalized" == "${code_normalized//-/}" ]]; then
            printf '\n'
            printf '  \033[1;32m✓ Verification successful\033[0m\n'
            sleep 1

            stty echo icanon 2>/dev/null
            printf '\033[?25h'

            exec "$AUTH_DIR/sns.sh"
        fi

        ((attempts++))

        printf '\n'
        printf '  \033[1;31m✗ Invalid verification code.\033[0m\n'

        if (( attempts < max_attempts )); then
            sleep "$delay"
            code="$(generate_code)"
        fi
    done

    printf '\n'
    printf '  \033[1;31mVerification failed.\033[0m\n'
    printf '\n'
    printf '  Maximum attempts reached.\n'
    printf '\n'

    stty echo icanon 2>/dev/null
    printf '\033[?25h'

    sleep 2
    clear
    exit 1
}

trap cleanup INT TERM

main
