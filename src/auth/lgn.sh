#!/usr/bin/env bash
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
source "$ROOT_DIR/src/core/runtime.sh" || exit 1
source "$ROOT_DIR/src/ui/theme.lib" || exit 1
AUTH_DIR="$ROOT_DIR/src/auth"
CONFIG_FILE="$AUTH_DIR/ath.json"

generate_code() {
    local chars='ABCDEFGHJKLMNPQRSTUVWXYZ23456789' code='' i length
    length="$(get_value '.code_length // 6')"
    for ((i=0;i<length;i++)); do code+="${chars:RANDOM%${#chars}:1}"; done
    if ((length>3)); then printf '%s-%s\n' "${code:0:3}" "${code:3}"
    else printf '%s\n' "$code"; fi
}
get_value() { jq -r "$1" "$CONFIG_FILE"; }
show_header() {
    mf_ui_header 'STARTUP VERIFICATION' "$(mf_ui_platform) / LOCAL SESSION"
}
main() {
    mf_require_json "$CONFIG_FILE" auth || exit 1
    local enabled max_attempts delay attempts=0 code input code_normalized input_normalized case_sensitive
    enabled="$(get_value 'if has("enabled") then .enabled else true end')" || exit 1
    if [[ "$enabled" == false ]]; then exec bash "$AUTH_DIR/sns.sh"; fi
    case_sensitive="$(get_value '.case_sensitive // false')"
    max_attempts="$(get_value '.max_attempts // 3')"
    delay="$(get_value '.delay_on_failure // 2')"
    code="$(generate_code)"
    hide_cursor
    stty -echo icanon 2>/dev/null || :
    while ((attempts < max_attempts)); do
        show_header
        mf_ui_text 'Confirm the displayed code to continue.' bright
        mf_ui_text 'This is an interaction check, not authentication.'
        mf_ui_gap
        mf_ui_section 'CONFIRMATION CODE'
        printf '\n  %s  %s%s%s\n\n' "$MF_UI_ACCENT" "$MF_UI_BOLD" "$code" "$MF_UI_RESET"
        mf_ui_field 'Remaining' "$((max_attempts-attempts)) attempt(s)"
        mf_ui_footer 'TYPE CODE + ENTER  Continue  |  CTRL+C  Cancel'
        printf '  %sCODE%s  ' "$MF_UI_ACCENT" "$MF_UI_RESET"
        IFS= read -r input || exit 0
        input="${input// /}"
        code_normalized="$code"
        if [[ "$case_sensitive" == false ]]; then
            input="${input^^}"; code_normalized="${code^^}"
        fi
        input_normalized="${input//-/}"
        if [[ "$input_normalized" == "${code_normalized//-/}" ]]; then
            mf_ui_gap
            mf_ui_status 'Confirmation accepted. Opening workspace.'
            stty echo icanon 2>/dev/null || :; show_cursor
            exec bash "$AUTH_DIR/sns.sh"
        fi
        ((attempts++))
        mf_ui_gap
        mf_ui_status 'Invalid verification code.' warning
        if ((attempts<max_attempts)); then
            [[ -t 0 && "${MF_UI_REDUCED_MOTION:-0}" != 1 ]] && sleep "$delay"
            code="$(generate_code)"
        fi
    done
    mf_ui_gap
    mf_ui_status 'Maximum attempts reached. Session not started.' warning
    exit 1
}
main
