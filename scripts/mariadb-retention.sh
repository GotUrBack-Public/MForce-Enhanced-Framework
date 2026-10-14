#!/usr/bin/env bash
# Optional, explicit local MariaDB retention. Never touches remote hosts.
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage: bash scripts/mariadb-retention.sh --days N [--execute] [--socket PATH]

Show how many locally stored MForce module logs are older than N days.
Dry-run is the default; --execute explicitly deletes those rows.
N must be an integer between 1 and 36500.

The MForce MariaDB server must be running locally. The socket defaults to
${MF_DB_SOCKET:-${XDG_STATE_HOME:-$HOME/.local/state}/mforce/mariadb/run/mysql.sock}.
This command never connects over TCP and does not change the bot runtime.
USAGE
}

days='' execute=0
socket="${MF_DB_SOCKET:-${XDG_STATE_HOME:-$HOME/.local/state}/mforce/mariadb/run/mysql.sock}"
while (($#)); do
  case "$1" in
    --days)
      (($# >= 2)) || { printf 'Missing value for --days\n' >&2; exit 2; }
      days="$2"; shift 2 ;;
    --socket)
      (($# >= 2)) || { printf 'Missing value for --socket\n' >&2; exit 2; }
      socket="$2"; shift 2 ;;
    --execute) execute=1; shift ;;
    --help|-h) usage; exit 0 ;;
    *) printf 'Unknown argument: %s\n' "$1" >&2; usage >&2; exit 2 ;;
  esac
done

if [[ ! "$days" =~ ^[0-9]+$ ]] || (("${#days}" > 5)) || ((10#$days < 1 || 10#$days > 36500)); then
  printf 'Specify --days as an integer from 1 to 36500\n' >&2
  exit 2
fi
days="$((10#$days))"
[[ -S "$socket" ]] || { printf 'Local MariaDB socket unavailable: %s\n' "$socket" >&2; exit 1; }
command -v mariadb >/dev/null || { printf 'mariadb CLI is required\n' >&2; exit 127; }

sql_count="SELECT COUNT(*) FROM mforce_logs.module_runs WHERE started_at < NOW() - INTERVAL $days DAY;"
count="$(mariadb --no-defaults --protocol=socket --socket="$socket" -uroot --batch --skip-column-names -e "$sql_count")" || {
  printf 'Could not query local MForce MariaDB. Check socket permissions.\n' >&2
  exit 1
}
[[ "$count" =~ ^[0-9]+$ ]] || { printf 'Unexpected MariaDB response\n' >&2; exit 1; }

if ((execute)); then
  mariadb --no-defaults --protocol=socket --socket="$socket" -uroot -e \
    "DELETE FROM mforce_logs.module_runs WHERE started_at < NOW() - INTERVAL $days DAY;" || {
    printf 'Could not delete local MForce logs\n' >&2
    exit 1
  }
  printf 'Retention executed: deleted rows older than %s days (previously matched: %s).\n' "$days" "$count"
else
  printf 'DRY RUN: %s rows older than %s days would be deleted. Add --execute to confirm.\n' "$count" "$days"
fi
