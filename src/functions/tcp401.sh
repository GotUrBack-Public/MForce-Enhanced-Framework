#!/usr/bin/env bash
# Educational Purpose / Professional Usage / Authorized Targets Only.
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
exec bash "$ROOT_DIR/src/lib/tcp401/tcp401.sh" "$@"
