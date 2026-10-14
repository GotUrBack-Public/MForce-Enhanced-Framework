#!/usr/bin/env bash
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
source "$ROOT_DIR/src/core/runtime.sh" || exit 1
source "$ROOT_DIR/src/ui/theme.lib" || exit 1
SESSION_DIR='' SESSION_FILE='' UI_PID=''

create_session() {
    local base="${TMPDIR:-${PREFIX:+$PREFIX/tmp}}"
    base="${base:-/tmp}"
    SESSION_DIR="$(umask 077; mktemp -d "$base/mforce-enhanced.XXXXXXXXXX")" || return 1
    SESSION_FILE="$SESSION_DIR/session.json"
    (umask 077; jq -n --arg id "${SESSION_DIR##*/}" --argjson created "$(date +%s)" \
        '{authenticated: true, session_id: $id, created: $created}' > "$SESSION_FILE") || return 1
}
session_cleanup() {
    local status=$?
    trap - EXIT
    if [[ -n "$UI_PID" ]]; then
        kill -TERM "$UI_PID" 2>/dev/null || :
        wait "$UI_PID" 2>/dev/null || :
    fi
    if [[ -n "$SESSION_DIR" ]]; then
        rm -f -- "$SESSION_FILE"
        rmdir -- "$SESSION_DIR" 2>/dev/null || :
    fi
    mf_restore_terminal
    return "$status"
}
main() {
    trap session_cleanup EXIT
    create_session || exit 1
    hide_cursor; stty -echo -icanon 2>/dev/null || :
    mf_ui_header 'SESSION READY' "$(mf_ui_platform) / LOCAL SESSION"
    mf_ui_status 'Local workspace initialized'
    mf_ui_status 'Session directory created with restricted permissions'
    mf_ui_gap
    mf_ui_text 'Entering the main workspace...' accent
    [[ -t 0 && -t 1 && "${MF_UI_REDUCED_MOTION:-0}" != 1 ]] && sleep 0.2
    stty echo icanon 2>/dev/null || :; show_cursor
    # Keep supervisor alive across UI exec transitions to clean up on all exits.
    bash "$ROOT_DIR/src/ui/cs.sh" <&0 &
    UI_PID=$!
    local status=0
    wait "$UI_PID" || status=$?
    UI_PID=''
    return "$status"
}
main
