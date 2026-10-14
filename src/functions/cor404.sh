#!/usr/bin/env bash
# MForce CORS Policy Auditor: delegated, bounded offensive audit.
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
exec bash "$ROOT_DIR/src/lib/cor404/cor404.sh" "$@"
