#!/data/data/com.termux/files/usr/bin/bash

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
source "$ROOT_DIR/src/core/runtime.sh" || exit 1
AUTH_DIR="$ROOT_DIR/src/auth"
CONFIG_FILE="$AUTH_DIR/ath.json"

generate_code() {
    local chars="ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
    local code=""
    local i length
    length="$(get_value '.code_length // 6')"

    for ((i=0; i<length; i++)); do
        code+="${chars:RANDOM%${#chars}:1}"
    done

    if (( length > 3 )); then
        printf '%s-%s\n' "${code:0:3}" "${code:3}"
    else
        printf '%s\n' "$code"
    fi
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
    mf_require_json "$CONFIG_FILE" auth || exit 1
}

is_enabled() {
    jq -r 'if has("enabled") then .enabled else true end' "$CONFIG_FILE"
}

get_value() {
    jq -r "$1" "$CONFIG_FILE"
}

main() {
    verify_config

    local enabled
    enabled="$(is_enabled)" || exit 1
    if [[ "$enabled" == "false" ]]; then
        exec bash "$AUTH_DIR/sns.sh"
    fi

    local max_attempts
    local delay
    local attempts=0
    local code
    local input code_normalized input_normalized case_sensitive
    case_sensitive="$(get_value '.case_sensitive // false')"

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

        IFS= read -r input || exit 0

        input="${input// /}"
        code_normalized="$code"
        if [[ "$case_sensitive" == false ]]; then
            input="${input^^}"
            code_normalized="${code^^}"
        fi
        input_normalized="${input//-/}"

        if [[ "$input_normalized" == "${code_normalized//-/}" ]]; then
            printf '\n'
            printf '  \033[1;32m✓ Verification successful\033[0m\n'
            sleep 1

            stty echo icanon 2>/dev/null
            printf '\033[?25h'

            exec bash "$AUTH_DIR/sns.sh"
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


main
