#!/usr/bin/env bash
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
source "$ROOT_DIR/src/core/runtime.sh" || exit 1
source "$ROOT_DIR/src/ui/theme.lib" || exit 1
CATEGORY_ID="${1:-}" CATEGORY_NAME="${2:-Category}"
FUNCTION_COUNT=0 ENABLED_COUNT=0

load_category_data() {
    mf_require_json "$ROOT_DIR/src/data/funcs.json" functions || exit 1
    mf_require_category "$CATEGORY_ID" || exit 1
    FUNCTION_COUNT="$(jq -r --arg id "$CATEGORY_ID" '[.functions[] | select(.category == $id)] | length' "$ROOT_DIR/src/data/funcs.json")" || exit 1
    ENABLED_COUNT="$(jq -r --arg id "$CATEGORY_ID" '[.functions[] | select(.category == $id and .enabled == true)] | length' "$ROOT_DIR/src/data/funcs.json")" || exit 1
}

draw_page() {
    mf_ui_header 'CATEGORY INFO' "$CATEGORY_NAME / $(mf_ui_platform)"
    mf_ui_section 'WORKSPACE OVERVIEW'
    mf_ui_text "$CATEGORY_NAME" bright
    mf_ui_gap
    mf_ui_field 'Category ID' "$CATEGORY_ID"
    mf_ui_field 'Registered' "$FUNCTION_COUNT"
    mf_ui_field 'Available' "$ENABLED_COUNT"
    mf_ui_gap
    if (( ENABLED_COUNT > 0 )); then
        mf_ui_status 'This workspace is ready to explore.'
    else
        mf_ui_status 'No active modules in this workspace yet.' warning
    fi
    mf_ui_gap
    mf_ui_section 'NEXT ACTION'
    if ((ENABLED_COUNT > 0)); then
        mf_ui_text 'Press ENTER to browse the available tools.'
    else
        mf_ui_text 'Press ENTER to view the empty module list.'
    fi
    mf_ui_footer 'ENTER  Modules  |  Q  Back'
}

return_to() {
    stty echo icanon 2>/dev/null || :; show_cursor
    exec bash "$ROOT_DIR/src/ui/$1" "${@:2}"
}
main() {
    load_category_data
    hide_cursor; stty -echo -icanon min 1 time 0 2>/dev/null || :
    while :; do
        draw_page
        mf_read_key BACK
        case "$MF_KEY" in
            EOF) exit 0 ;;
            ENTER) return_to fs.sh "$CATEGORY_ID" "$CATEGORY_NAME" ;;
            BACK) return_to cs.sh ;;
            HELP) mf_ui_help ;;
        esac
    done
}
main
