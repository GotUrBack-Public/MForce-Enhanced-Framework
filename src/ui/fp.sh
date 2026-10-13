#!/usr/bin/env bash
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
source "$ROOT_DIR/src/core/runtime.sh" || exit 1
source "$ROOT_DIR/src/ui/theme.lib" || exit 1
source "$ROOT_DIR/src/core/mariadb.sh" || exit 1
CATEGORY_ID="${1:-}" CATEGORY_NAME="${2:-Category}"
FUNCTION_ID="${3:-}" FUNCTION_ENTRY="${4:-}" FUNCTION_NAME="${5:-Function}"
ENTRY_FILE="$ROOT_DIR/src/functions/$FUNCTION_ENTRY"
LIB_ID='' META_VERSION='' META_TYPE='' META_CATEGORY=''

load_module() {
    mf_require_json "$ROOT_DIR/src/data/funcs.json" functions || exit 1
    mf_require_category "$CATEGORY_ID" || exit 1
    jq -e --arg id "$FUNCTION_ID" --arg entry "$FUNCTION_ENTRY" --arg category "$CATEGORY_ID" \
        '.functions | any(.id == $id and .entry == $entry and .category == $category and .enabled == true)' \
        "$ROOT_DIR/src/data/funcs.json" >/dev/null || exit 1
    LIB_ID="$(jq -r --arg id "$FUNCTION_ID" '.functions[] | select(.id == $id) | (.library // .id)' "$ROOT_DIR/src/data/funcs.json")" || exit 1
    [[ -n "$LIB_ID" && "$LIB_ID" != null ]] || LIB_ID="$FUNCTION_ID"
    local meta="$ROOT_DIR/src/lib/$LIB_ID/$LIB_ID.json"
    if [[ -f "$meta" ]]; then
        mf_require_json "$meta" metadata || exit 1
        META_VERSION="$(jq -r '.version // "unknown"' "$meta")"
        META_TYPE="$(jq -r '.type // "function"' "$meta")"
    fi
}

draw_page() {
    mf_ui_header 'FUNCTION PREVIEW' "$CATEGORY_NAME / $FUNCTION_NAME"
    mf_ui_text "$FUNCTION_NAME" bright
    mf_ui_gap
    mf_ui_section 'MODULE DETAILS'
    mf_ui_field 'Category' "$CATEGORY_NAME"
    mf_ui_field 'Module ID' "$FUNCTION_ID"
    mf_ui_field 'Entry point' "$FUNCTION_ENTRY"
    mf_ui_field 'Library' "$LIB_ID"
    [[ -z "$META_VERSION" ]] || mf_ui_field 'Version' "$META_VERSION"
    [[ -z "$META_TYPE" ]] || mf_ui_field 'Type' "$META_TYPE"
    mf_ui_gap
    mf_ui_section 'EXECUTION STATUS'
    if [[ -f "$ENTRY_FILE" ]]; then
        mf_ui_status 'Entry point ready. Runs locally on this device.'
    else
        mf_ui_status 'Module entry point is missing.' warning
    fi
    mf_ui_gap
    mf_ui_text 'Inspect module source before using unfamiliar commands.'
    mf_ui_footer 'ENTER  Run module  |  Q  Back to module list'
}

run_module() {
    stty echo icanon 2>/dev/null || :; show_cursor
    if [[ ! -f "$ENTRY_FILE" ]]; then
        mf_ui_header 'EXECUTION ERROR' 'ENTRY POINT MISSING'
        mf_ui_status 'Module entry point not found.' warning
        mf_ui_text "$ENTRY_FILE"
        mf_ui_footer 'ENTER  Return to preview'
        IFS= read -r || exit 0
        hide_cursor; stty -echo -icanon min 1 time 0 2>/dev/null || :
        return
    fi
    if [[ "${MF_DB_READY:-0}" == 1 ]]; then
        local output_file status
        output_file="$(mktemp)" || { bash "$ENTRY_FILE"; return; }
        bash "$ENTRY_FILE" 2>&1 | tee "$output_file"
        status=${PIPESTATUS[0]}
        mf_db_record "$FUNCTION_ID" "$status" "$output_file"
        rm -f "$output_file"
        exit "$status"
    fi
    exec bash "$ENTRY_FILE"
}

main() {
    load_module
    hide_cursor; stty -echo -icanon min 1 time 0 2>/dev/null || :
    while :; do
        draw_page
        mf_read_key BACK
        case "$MF_KEY" in
            EOF) exit 0 ;;
            ENTER) run_module ;;
            BACK)
                stty echo icanon 2>/dev/null || :; show_cursor
                exec bash "$ROOT_DIR/src/ui/fs.sh" "$CATEGORY_ID" "$CATEGORY_NAME"
                ;;
            HELP) mf_ui_help ;;
        esac
    done
}
main
