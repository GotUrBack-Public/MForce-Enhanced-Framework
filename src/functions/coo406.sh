#!/usr/bin/env bash
# MForce Cookie Flag Auditor: delegated, bounded offensive audit.
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
exec bash "$ROOT_DIR/src/lib/coo406/coo406.sh" "$@"
