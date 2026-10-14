#!/usr/bin/env bash
# MForce HTTP Method Auditor: delegated, bounded offensive audit.
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
exec bash "$ROOT_DIR/src/lib/met405/met405.sh" "$@"
