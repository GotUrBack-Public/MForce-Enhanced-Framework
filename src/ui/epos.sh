#!/usr/bin/env bash
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
source "$ROOT_DIR/src/core/runtime.sh" || exit 1
source "$ROOT_DIR/src/ui/theme.lib" || exit 1

main() {
    hide_cursor
    mf_ui_header 'INITIALIZING' "$(mf_ui_platform) / $MF_VERSION"
    mf_ui_text 'MForce Enhanced Framework' bright
    mf_ui_gap
    mf_ui_section 'RUNTIME CHECKS'
    mf_ui_status 'Project configuration validated'
    mf_ui_status 'Shared runtime libraries loaded'
    mf_ui_status "Platform detected: $(mf_ui_platform)"
    mf_ui_gap
    mf_ui_text 'Starting local session...' accent
    # Motion is modest and never slows redirected output or automated tests.
    [[ -t 0 && -t 1 && "${MF_UI_REDUCED_MOTION:-0}" != 1 ]] && sleep 0.35
    stty echo icanon 2>/dev/null || :; show_cursor
    exec bash "$ROOT_DIR/src/auth/lgn.sh"
}
main
