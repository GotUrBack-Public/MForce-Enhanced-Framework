#!/usr/bin/env bash
# Educational Purpose / Professional Usage / authorized targets only.
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
exec bash "$ROOT_DIR/src/lib/tls213/tls213.sh" "$@"
