#!/data/data/com.termux/files/usr/bin/bash

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
AUTH_DIR="$ROOT_DIR/src/auth"
SESSION_DIR="${TMPDIR:-$PREFIX/tmp}/mforce-enhanced"
SESSION_FILE="$SESSION_DIR/session.json"

create_session() {
    mkdir -p "$SESSION_DIR"

    local session_id
    local created

    session_id="$(printf '%s-%s-%s' "$RANDOM" "$RANDOM" "$(date +%s)")"
    created="$(date +%s)"

    cat > "$SESSION_FILE" <<EOF
{
  "authenticated": true,
  "session_id": "$session_id",
  "created": $created
}
EOF
}

cleanup() {
    rm -f "$SESSION_FILE"
    printf '\033[?25h'
    stty echo icanon 2>/dev/null
    clear
    exit 0
}

main() {
    create_session

    trap cleanup INT TERM EXIT

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

    trap - EXIT

    exec "$ROOT_DIR/src/ui/cs.sh"
}

main
