#!/usr/bin/env bash
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
source "$ROOT_DIR/src/core/runtime.sh" || exit 1
source "$ROOT_DIR/src/ui/theme.lib" || exit 1

CATEGORIES=() CATEGORY_IDS=() CATEGORY_COUNTS=() MENU_ITEMS=()
SELECTED=0 LAST_CATEGORY=0

category_description() {
    case "$1" in
        net) printf 'Interfaces, local addresses and connectivity context' ;;
        sys) printf 'Kernel, architecture, platform and runtime details' ;;
        osint) printf 'Search tools (planned; currently unavailable)' ;;
        util) printf 'General-purpose utilities (planned)' ;;
        file) printf 'File operations (planned)' ;;
        cfg) printf 'Application options (planned)' ;;
        *) printf 'Explore the available modules' ;;
    esac
}

load_categories() {
    mf_require_json "$ROOT_DIR/src/data/cats.json" categories || exit 1
    mf_require_json "$ROOT_DIR/src/data/funcs.json" functions || exit 1
    local id name count
    while IFS=$'\t' read -r id name; do
        [[ -n "$id" ]] || continue
        CATEGORIES+=("$name") CATEGORY_IDS+=("$id")
        count="$(jq -r --arg id "$id" '[.functions[] | select(.category == $id and .enabled == true)] | length' "$ROOT_DIR/src/data/funcs.json")" || exit 1
        CATEGORY_COUNTS+=("$count")
    done < <(jq -r '.categories[] | select(.enabled == true) | [.id,.name] | @tsv' "$ROOT_DIR/src/data/cats.json")
    MENU_ITEMS=("${CATEGORIES[@]}" 'Category Info' 'About')
}

draw_page() {
    local i note selected_id count current
    ((SELECTED < ${#CATEGORIES[@]})) && LAST_CATEGORY=$SELECTED
    mf_ui_header 'MAIN MENU' "$(mf_ui_platform) / $MF_VERSION"
    mf_ui_text 'Choose a workspace. All operations run locally.' bright
    mf_ui_gap
    mf_ui_section 'WORKSPACES'
    for i in "${!CATEGORIES[@]}"; do
        count="${CATEGORY_COUNTS[$i]}"
        if ((count > 0)); then note="$count AVAILABLE MODULE(S)"; else note='NO ACTIVE MODULES'; fi
        mf_ui_row "$((i+1))" "${CATEGORIES[$i]}" "$([[ $i -eq $SELECTED ]] && printf '%s' "$note")" "$((i == SELECTED))"
    done
    mf_ui_gap
    mf_ui_section 'QUICK ACCESS'
    mf_ui_row "$(( ${#CATEGORIES[@]}+1 ))" 'Category Info' '' "$((SELECTED == ${#CATEGORIES[@]}))"
    mf_ui_row "$(( ${#CATEGORIES[@]}+2 ))" 'About MForce' '' "$((SELECTED == ${#CATEGORIES[@]}+1))"
    mf_ui_gap
    if (( ! MF_UI_COMPACT )) && ((SELECTED < ${#CATEGORIES[@]})); then
        selected_id="${CATEGORY_IDS[$SELECTED]}"
        mf_ui_text "FOCUS  /  ${CATEGORIES[$SELECTED]}" accent
        mf_ui_text "$(category_description "$selected_id")"
    elif (( ! MF_UI_COMPACT )); then
        mf_ui_text 'FOCUS  /  INFORMATION' accent
        if ((SELECTED == ${#CATEGORIES[@]})); then
            mf_ui_text 'Details for the last selected workspace'
        else
            mf_ui_text 'Version, source, platform and licensing'
        fi
    fi
    mf_ui_footer 'UP/DOWN or J/K  Navigate  |  ENTER  Open  |  ?  Help  |  Q  Exit' 'ARROWS  ENTER  ? HELP  Q EXIT'
}

launch() {
    local script="$1"; shift
    stty echo icanon 2>/dev/null || :
    show_cursor
    exec bash "$ROOT_DIR/src/ui/$script" "$@"
}

main() {
    load_categories
    hide_cursor
    stty -echo -icanon min 1 time 0 2>/dev/null || :
    while :; do
        draw_page
        mf_read_key QUIT
        case "$MF_KEY" in
            EOF|QUIT) cleanup ;;
            UP) ((SELECTED=(SELECTED+${#MENU_ITEMS[@]}-1)%${#MENU_ITEMS[@]})) ;;
            DOWN) ((SELECTED=(SELECTED+1)%${#MENU_ITEMS[@]})) ;;
            HOME) SELECTED=0 ;;
            END) SELECTED=$((${#MENU_ITEMS[@]}-1)) ;;
            HELP) mf_ui_help ;;
            DIGIT_*)
                number=${MF_KEY#DIGIT_}
                if ((number>=1 && number<=${#MENU_ITEMS[@]})); then SELECTED=$((number-1)); fi
                ;;
            ENTER)
                if ((SELECTED < ${#CATEGORIES[@]})); then
                    launch cp.sh "${CATEGORY_IDS[$SELECTED]}" "${CATEGORIES[$SELECTED]}"
                elif ((SELECTED == ${#CATEGORIES[@]})); then
                    if ((${#CATEGORIES[@]} > 0)); then
                        launch cp.sh "${CATEGORY_IDS[$LAST_CATEGORY]}" "${CATEGORIES[$LAST_CATEGORY]}"
                    fi
                else launch ap.sh; fi
                ;;
        esac
    done
}
main
