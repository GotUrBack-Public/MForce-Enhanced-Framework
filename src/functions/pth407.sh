#!/usr/bin/env bash
# MForce Exposure Path Auditor: delegated, bounded offensive audit.
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
exec bash "$ROOT_DIR/src/lib/pth407/pth407.sh" "$@"
