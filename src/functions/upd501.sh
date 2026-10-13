#!/usr/bin/env bash
# Educational Purpose / Professional Usage / Official MForce updates.
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
exec bash "$ROOT_DIR/src/lib/upd501/upd501.sh" "$@"
