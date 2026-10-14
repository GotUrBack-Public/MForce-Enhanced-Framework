#!/usr/bin/env bash
# Optional, local-only audit database. Explicit opt-in: MF_DB_ENABLE=1.
# No module output, request URL or raw scan results are stored.
mf_db_start() {
    unset MF_DB_READY
    [[ "${MF_DB_ENABLE:-0}" == 1 && "${MF_DB_DISABLE:-0}" != 1 ]] || return 0
    local retention="${MF_DB_RETENTION_DAYS:-7}" cmd base i
    if [[ ! "$retention" =~ ^[0-9]+$ ]] || ((10#$retention < 1 || 10#$retention > 365)); then
        printf 'MForce: invalid MF_DB_RETENTION_DAYS (expected 1..365); logging disabled\n' >&2
        return 0
    fi
    # Canonicalize before interpolation into a SQL INTERVAL.
    retention="$((10#$retention))"
    for cmd in mariadbd mariadb mariadb-install-db; do
        command -v "$cmd" >/dev/null 2>&1 || {
            printf 'MForce: MariaDB unavailable (%s); logging disabled\n' "$cmd" >&2
            return 0
        }
    done
    base="${XDG_STATE_HOME:-$HOME/.local/state}/mforce/mariadb"
    (umask 077; mkdir -p -- "$base/data" "$base/run") || return 0
    chmod 700 -- "$base" "$base/data" "$base/run" || return 0
    export MF_DB_SOCKET="$base/run/mysql.sock"
    if [[ ! -d "$base/data/mysql" ]]; then
        (umask 077; mariadb-install-db --no-defaults --datadir="$base/data" --auth-root-authentication-method=normal --skip-test-db >/dev/null 2>&1) || return 0
    fi
    if [[ -S "$MF_DB_SOCKET" ]]; then
        printf 'MForce: MariaDB socket already exists; logging disabled for safety\n' >&2
        return 0
    fi
    (umask 077; exec mariadbd --no-defaults --datadir="$base/data" --socket="$MF_DB_SOCKET" --pid-file="$base/run/server.pid" --skip-networking --port=0 --user="$(id -un)" >"$base/run/server.log" 2>&1) &
    MF_DB_PID=$!
    for ((i=0;i<40;i++)); do
        if mariadb --no-defaults --socket="$MF_DB_SOCKET" -uroot -N -e 'SELECT 1' >/dev/null 2>&1; then
            if mariadb --no-defaults --socket="$MF_DB_SOCKET" -uroot < "$MF_ROOT/sql/schema.sql" &&
               # Remove legacy captured output from earlier versions and expire
               # metadata using a bounded retention policy before enabling logs.
               mariadb --no-defaults --socket="$MF_DB_SOCKET" -uroot -e "
                   UPDATE mforce_logs.module_runs SET output = NULL WHERE output IS NOT NULL;
                   DELETE FROM mforce_logs.module_runs
                   WHERE started_at < UTC_TIMESTAMP() - INTERVAL $retention DAY;
               " >/dev/null 2>&1; then
                export MF_DB_READY=1
                return 0
            fi
            break
        fi
        kill -0 "$MF_DB_PID" 2>/dev/null || break
        sleep 0.25
    done
    mf_db_stop
    printf 'MForce: MariaDB could not start safely; logging disabled\n' >&2
    return 0
}
mf_db_stop() {
    [[ -n "${MF_DB_PID:-}" ]] || return 0
    kill "$MF_DB_PID" 2>/dev/null || :
    wait "$MF_DB_PID" 2>/dev/null || :
    unset MF_DB_PID MF_DB_READY
}
mf_db_record() {
    [[ "${MF_DB_READY:-0}" == 1 && -S "${MF_DB_SOCKET:-}" ]] || return 0
    local module="${1:-}" status="${2:-}"
    [[ "$module" =~ ^[a-zA-Z0-9_-]{1,128}$ && "$status" =~ ^[0-9]+$ ]] || return 0
    ((status >= 0 && status <= 255)) || return 0
    # Only a validated identifier and exit status. No file read, SQL quoting,
    # raw terminal output or sensitive network-response storage.
    printf "INSERT INTO mforce_logs.module_runs (module_id,exit_code,output) VALUES ('%s',%d,NULL);\n" "$module" "$status" |
        mariadb --no-defaults --socket="$MF_DB_SOCKET" -uroot >/dev/null 2>&1 || :
    return 0
}
