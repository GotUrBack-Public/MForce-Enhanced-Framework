#!/usr/bin/env bash
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
source "$ROOT_DIR/src/core/runtime.sh" || exit 1
source "$ROOT_DIR/src/ui/theme.lib" || exit 1
CATEGORY_ID="${1:-}" CATEGORY_NAME="${2:-Category}"
FUNCTIONS=() FUNCTION_IDS=() FUNCTION_ENTRIES=()
SELECTED=0

load_functions() {
    mf_require_json "$ROOT_DIR/src/data/funcs.json" functions || exit 1
    mf_require_category "$CATEGORY_ID" || exit 1
    local id entry name
    while IFS=$'\t' read -r id entry name; do
        [[ -n "$id" ]] || continue
        FUNCTION_IDS+=("$id") FUNCTION_ENTRIES+=("$entry") FUNCTIONS+=("$name")
    done < <(jq -r --arg id "$CATEGORY_ID" '.functions[] | select(.category == $id and .enabled == true) | [.id,.entry,.name] | @tsv' "$ROOT_DIR/src/data/funcs.json")
}

draw_page() {
    local i
    mf_ui_header 'FUNCTION SELECT' "$CATEGORY_NAME / MODULES"
    mf_ui_text 'Inspect an entry before running it.' bright
    mf_ui_gap
    mf_ui_section 'AVAILABLE TOOLS'
    if ((${#FUNCTIONS[@]} == 0)); then
        mf_ui_status 'No functions available. Check back after future releases.' warning
    else
        for i in "${!FUNCTIONS[@]}"; do
            mf_ui_row "$((i+1))" "${FUNCTIONS[$i]}" "$([[ $i -eq $SELECTED ]] && printf 'ID / %s' "${FUNCTION_IDS[$i]}")" "$((SELECTED == i))"
        done
        if (( ! MF_UI_COMPACT )); then
            mf_ui_gap
            mf_ui_section 'SELECTED MODULE'
            mf_ui_field 'Name' "${FUNCTIONS[$SELECTED]}"
            mf_ui_field 'ID' "${FUNCTION_IDS[$SELECTED]}"
            mf_ui_field 'Entry' "${FUNCTION_ENTRIES[$SELECTED]}"
        fi
    fi
    mf_ui_footer 'UP/DOWN or J/K  Navigate  |  ENTER  Preview  |  Q  Back' 'ARROWS  ENTER  Q BACK'
}

back_to_menu() { stty echo icanon 2>/dev/null || :; show_cursor; exec bash "$ROOT_DIR/src/ui/cs.sh"; }
open_preview() {
    stty echo icanon 2>/dev/null || :; show_cursor
    exec bash "$ROOT_DIR/src/ui/fp.sh" "$CATEGORY_ID" "$CATEGORY_NAME" \
        "${FUNCTION_IDS[$SELECTED]}" "${FUNCTION_ENTRIES[$SELECTED]}" "${FUNCTIONS[$SELECTED]}"
}
main() {
    load_functions
    hide_cursor; stty -echo -icanon min 1 time 0 2>/dev/null || :
    while :; do
        draw_page
        mf_read_key QUIT
        case "$MF_KEY" in
            EOF) exit 0 ;;
            QUIT) back_to_menu ;;
            UP) if ((${#FUNCTIONS[@]})); then SELECTED=$(( (SELECTED+${#FUNCTIONS[@]}-1)%${#FUNCTIONS[@]} )); fi ;;
            DOWN) if ((${#FUNCTIONS[@]})); then SELECTED=$(((SELECTED+1)%${#FUNCTIONS[@]})); fi ;;
            HOME) SELECTED=0 ;;
            END) if ((${#FUNCTIONS[@]})); then SELECTED=$((${#FUNCTIONS[@]}-1)); fi ;;
            HELP) mf_ui_help ;;
            DIGIT_*) number=${MF_KEY#DIGIT_}; if ((number>=1 && number<=${#FUNCTIONS[@]})); then SELECTED=$((number-1)); fi ;;
            ENTER) if ((${#FUNCTIONS[@]})); then open_preview; fi ;;
        esac
    done
}
main
