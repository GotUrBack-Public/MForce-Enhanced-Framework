#!/usr/bin/env bash
# Local, socket-only MariaDB session; never listens on the network.
mf_db_start() {
    [[ "${MF_DB_DISABLE:-0}" != 1 ]] || return 0
    for cmd in mariadbd mariadb mariadb-install-db; do
        command -v "$cmd" >/dev/null 2>&1 || { printf 'MForce: MariaDB unavailable (%s); logging disabled\n' "$cmd" >&2; return 0; }
    done
    local base="${XDG_STATE_HOME:-$HOME/.local/state}/mforce/mariadb"
    mkdir -p "$base/data" "$base/run" || return 0
    chmod 700 "$base" "$base/data" "$base/run"
    export MF_DB_SOCKET="$base/run/mysql.sock"
    if [[ ! -d "$base/data/mysql" ]]; then
        mariadb-install-db --no-defaults --datadir="$base/data" --auth-root-authentication-method=normal --skip-test-db >/dev/null 2>&1 || return 0
    fi
    if [[ -S "$MF_DB_SOCKET" ]]; then
        printf 'MForce: MariaDB socket already exists; logging disabled for safety\n' >&2
        return 0
    fi
    mariadbd --no-defaults --datadir="$base/data" --socket="$MF_DB_SOCKET" --pid-file="$base/run/server.pid" --skip-networking --port=0 --user="$(id -un)" >"$base/run/server.log" 2>&1 &
    MF_DB_PID=$!
    local i
    for ((i=0;i<40;i++)); do
        if mariadb --no-defaults --socket="$MF_DB_SOCKET" -uroot -N -e 'SELECT 1' >/dev/null 2>&1; then
            if mariadb --no-defaults --socket="$MF_DB_SOCKET" -uroot < "$MF_ROOT/sql/schema.sql"; then
                export MF_DB_READY=1
                return 0
            fi
            break
        fi
        kill -0 "$MF_DB_PID" 2>/dev/null || break
        sleep 0.25
    done
    mf_db_stop
    printf 'MForce: MariaDB could not start; logging disabled\n' >&2
}
mf_db_stop() {
    [[ -n "${MF_DB_PID:-}" ]] || return 0
    kill "$MF_DB_PID" 2>/dev/null || :
    wait "$MF_DB_PID" 2>/dev/null || :
    unset MF_DB_PID MF_DB_READY
}
mf_db_record() {
    [[ "${MF_DB_READY:-0}" == 1 && -S "${MF_DB_SOCKET:-}" ]] || return 0
    local module="$1" status="$2" file="$3" hex idhex
    # Bound the captured output; no shell interpolation into SQL literals.
    hex="$(head -c 1048576 "$file" | od -An -tx1 -v | tr -d ' \n')" || return 0
    idhex="$(printf '%s' "$module" | od -An -tx1 -v | tr -d ' \n')"
    printf "INSERT INTO mforce_logs.module_runs (module_id,exit_code,output) VALUES (CONVERT(UNHEX('%s') USING utf8mb4),%d,CONVERT(UNHEX('%s') USING utf8mb4));\n" "$idhex" "$status" "$hex" |
        mariadb --no-defaults --socket="$MF_DB_SOCKET" -uroot >/dev/null 2>&1 || :
}
