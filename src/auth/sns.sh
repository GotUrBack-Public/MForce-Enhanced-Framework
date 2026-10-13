#!/data/data/com.termux/files/usr/bin/bash

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
source "$ROOT_DIR/src/core/runtime.sh" || exit 1
AUTH_DIR="$ROOT_DIR/src/auth"
SESSION_DIR=""
SESSION_FILE=""
UI_PID=""

create_session() {
    local base="${TMPDIR:-${PREFIX:+$PREFIX/tmp}}"
    base="${base:-/tmp}"
    SESSION_DIR="$(umask 077; mktemp -d "$base/mforce-enhanced.XXXXXXXXXX")" || return 1
    SESSION_FILE="$SESSION_DIR/session.json"
    # Local run metadata, not an authentication credential.
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

    printf '\033[?25l'
    stty -echo icanon 2>/dev/null

    clear

    printf '\033[1;36m'
    printf '╔══════════════════════════════════════════════════════╗\n'
    printf '║                 MFORCE ENHANCED                      ║\n'
    printf '╠══════════════════════════════════════════════════════╣\n'
    printf '║                  SESSION READY                       ║\n'
    printf '╚══════════════════════════════════════════════════════╝\n'
    printf '\033[0m'

    printf '\n'
    printf '  \033[1;32m✓\033[0m Verification complete\n'
    printf '  \033[1;32m✓\033[0m Local session created\n'

    sleep 1

    stty echo icanon 2>/dev/null
    printf '\033[?25h'

    # Keep this supervisor alive across the UI chain of exec calls.
    bash "$ROOT_DIR/src/ui/cs.sh" <&0 &
    UI_PID=$!
    local status=0
    wait "$UI_PID" || status=$?
    UI_PID=""
    return "$status"
}

main
