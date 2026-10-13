#!/data/data/com.termux/files/usr/bin/bash

# Shared runtime; sourced by entry points, never a separate application.
MF_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
for mf_lib in "$MF_ROOT"/classes{1..5}.lib; do
    source "$mf_lib" || return 1
done
unset mf_lib

mf_require_json() {
    local file="$1" kind="$2"
    if ! command -v jq >/dev/null 2>&1; then
        if mf_is_termux; then
            printf 'ERROR: jq is required. Install with: pkg install jq\n' >&2
        else
            printf 'ERROR: jq is required. Install it using your Linux package manager.\n' >&2
        fi
        return 1
    fi
    # Slurp first to reject empty files and multiple top-level documents.
    if ! jq -e -s 'length == 1' "$file" >/dev/null 2>&1 ||
       ! jq -e --arg kind "$kind" -f "$MF_ROOT/src/core/schema.jq" "$file" >/dev/null 2>&1; then
        printf 'ERROR: Invalid or missing %s configuration: %s\n' "$kind" "$file" >&2
        return 1
    fi
}

mf_restore_terminal() {
    if [[ -t 0 ]]; then
        if [[ -n "${MF_TTY_STATE:-}" ]]; then
            stty "$MF_TTY_STATE" 2>/dev/null || :
        else
            stty echo icanon 2>/dev/null || :
        fi
    fi
    [[ ! -t 1 ]] || mf_cursor_show
    return 0
}

hide_cursor() { mf_cursor_hide; }
show_cursor() { mf_cursor_show; }
cleanup() { exit 0; }


mf_read_key() {
    local key tail last
    MF_KEY=IGNORE
    IFS= read -rsn1 key || { MF_KEY=EOF; return 0; }
    case "$key" in
        $'\x1b')
            IFS= read -rsn2 -t 0.15 tail || return 0
            case "$tail" in
                '[A') MF_KEY=UP ;;
                '[B') MF_KEY=DOWN ;;
                '[C') MF_KEY=RIGHT ;;
                '[D') MF_KEY=LEFT ;;
                '[H'|'OH') MF_KEY=HOME ;;
                '[F'|'OF') MF_KEY=END ;;
                '[1'|'[7')
                    IFS= read -rsn1 -t 0.10 last || :
                    [[ "$last" == '~' ]] && MF_KEY=HOME
                    ;;
                '[4'|'[8')
                    IFS= read -rsn1 -t 0.10 last || :
                    [[ "$last" == '~' ]] && MF_KEY=END
                    ;;
            esac ;;
        '') MF_KEY=ENTER ;;
        q|Q) MF_KEY="${1:-BACK}" ;;
        j|J) MF_KEY=DOWN ;;
        k|K) MF_KEY=UP ;;
        '?') MF_KEY=HELP ;;
        [1-9]) MF_KEY="DIGIT_$key" ;;
    esac
    return 0
}

mf_require_category() {
    mf_require_json "$MF_ROOT/src/data/cats.json" categories || return 1
    jq -e --arg id "$1" '.categories | any(.id == $id and .enabled)' \
        "$MF_ROOT/src/data/cats.json" >/dev/null || {
        printf 'ERROR: Unknown or disabled category: %s\n' "$1" >&2
        return 1
    }
}

mf_module_resources() {
    local id="$1" option="${2:-}" line key value
    local dir="$MF_ROOT/src/lib/$id"
    mf_require_json "$dir/$id.json" metadata || return 1
    [[ -r "$dir/$id.conf" && -r "$dir/$id.help" ]] || {
        printf 'ERROR: Missing module resources: %s\n' "$id" >&2; return 1;
    }
    local enabled='' version='' mode=''
    while IFS= read -r line || [[ -n "$line" ]]; do
        [[ -z "$line" || "$line" == \#* ]] && continue
        key="${line%%=*}"; value="${line#*=}"
        case "$key" in
            enabled) [[ -z "$enabled" && "$value" =~ ^(true|false)$ ]] || return 1; enabled="$value" ;;
            version) [[ -z "$version" && "$value" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]] || return 1; version="$value" ;;
            mode) [[ -z "$mode" && "$value" == terminal ]] || return 1; mode="$value" ;;
            *) printf 'ERROR: Invalid module setting: %s\n' "$key" >&2; return 1 ;;
        esac
    done < "$dir/$id.conf"
    [[ -n "$enabled" && -n "$version" && -n "$mode" ]] || return 1
    jq -e --arg id "$id" --arg version "$version" \
        '.id == $id and .library == $id and .version == $version' "$dir/$id.json" >/dev/null || return 1
    if [[ "$option" == --help || "$option" == -h ]]; then
        cat "$dir/$id.help"
        exit 0
    fi
    if [[ "$enabled" != true ]] || ! jq -e '.enabled' "$dir/$id.json" >/dev/null; then
        printf 'ERROR: Module disabled: %s\n' "$id" >&2
        return 1
    fi
}

if [[ -t 0 && -z "${MF_TTY_STATE:-}" ]]; then
    MF_TTY_STATE="$(stty -g)"
    export MF_TTY_STATE
fi
trap mf_restore_terminal EXIT
trap 'exit 130' INT
trap 'exit 143' TERM
trap 'exit 129' HUP
mf_require_json "$MF_ROOT/cfg/zrk391.json" project || return 1
MF_VERSION="$(jq -r .version "$MF_ROOT/cfg/zrk391.json")"
