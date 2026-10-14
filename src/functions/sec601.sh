#!/usr/bin/env bash
# MForce Local Secret Scanner: delegated, bounded defensive audit.
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
exec bash "$ROOT_DIR/src/lib/sec601/sec601.sh" "$@"
