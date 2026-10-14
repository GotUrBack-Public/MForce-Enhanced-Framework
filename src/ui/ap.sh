#!/usr/bin/env bash
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
source "$ROOT_DIR/src/core/runtime.sh" || exit 1
source "$ROOT_DIR/src/ui/theme.lib" || exit 1
CONFIG_FILE="$ROOT_DIR/cfg/zrk391.json"
NAME='' VERSION='' LICENSE='' LANGUAGE='' REPOSITORY=''

load_config() {
    mf_require_json "$CONFIG_FILE" project || exit 1
    NAME="$(jq -r '.name // "MForce Enhanced Framework"' "$CONFIG_FILE")"
    VERSION="$(jq -r '.version // "unknown"' "$CONFIG_FILE")"
    LICENSE="$(jq -r '.license // "unknown"' "$CONFIG_FILE")"
    LANGUAGE="$(jq -r '.language // "unknown"' "$CONFIG_FILE")"
    REPOSITORY="$(jq -r '.repository // "unknown"' "$CONFIG_FILE")"
}

draw_page() {
    mf_ui_header 'ABOUT' 'PROJECT / INFORMATION'
    mf_ui_text "$NAME" bright
    mf_ui_gap
    mf_ui_section 'RELEASE DETAILS'
    mf_ui_field 'Version' "$VERSION"
    mf_ui_field 'License' "$LICENSE"
    mf_ui_field 'Language' "$LANGUAGE"
    mf_ui_field 'Platform' "$(mf_ui_platform)"
    mf_ui_field 'Repository' "$REPOSITORY"
    mf_ui_gap
    mf_ui_section 'PROJECT PHILOSOPHY'
    mf_ui_text 'Open-source terminal tools with a modular Bash core.'
    mf_ui_text 'Designed for Termux and Linux environments.'
    mf_ui_text 'Review source before running tools on your machine.'
    mf_ui_footer 'ENTER / Q  Back to main menu'
}

main() {
    load_config
    hide_cursor; stty -echo -icanon min 1 time 0 2>/dev/null || :
    while :; do
        draw_page
        mf_read_key BACK
        case "$MF_KEY" in
            EOF) exit 0 ;;
            ENTER|BACK)
                stty echo icanon 2>/dev/null || :; show_cursor
                exec bash "$ROOT_DIR/src/ui/cs.sh" ;;
            HELP) mf_ui_help ;;
        esac
    done
}
main
