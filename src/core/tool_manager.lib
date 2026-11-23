#!/usr/bin/env bash
# External tool registry and safe process adapter. Source after runtime.sh.
MF_TOOL_CATALOG="${MF_ROOT}/src/tools/catalog.json"
MF_TOOL_IDS=()
MF_TOOL_NAMES=()
MF_TOOL_COMMANDS=()
MF_TOOL_CATEGORIES=()
MF_TOOL_DESCRIPTIONS=()
MF_TOOL_ENABLED=()

mf_tools_validate() {
    local file="${1:-$MF_TOOL_CATALOG}"
    mf_require_json "$file" tools || return 1
    jq -e '
      .schema_version == 1 and
      (.tools | type == "array") and
      ([.tools[] | select(
        (.id | type == "string" and test("^[a-z][a-z0-9_-]{1,39}$")) and
        (.name | type == "string" and length > 0 and length <= 80) and
        (.command | type == "string" and test("^[A-Za-z0-9_.+-]+$")) and
        (.category | type == "string" and length > 0 and length <= 40) and
        (.description | type == "string" and length <= 240) and
        (.enabled | type == "boolean")
      )] | length) == (.tools | length) and
      ([.tools[].id] | length == (unique | length))
    ' "$file" >/dev/null 2>&1 || {
        printf 'ERROR: Invalid external tool catalog: %s\n' "$file" >&2
        return 1
    }
}

mf_tools_load() {
    local file="${1:-$MF_TOOL_CATALOG}" id name binary category description enabled
    mf_tools_validate "$file" || return 1
    MF_TOOL_IDS=() MF_TOOL_NAMES=() MF_TOOL_COMMANDS=()
    MF_TOOL_CATEGORIES=() MF_TOOL_DESCRIPTIONS=() MF_TOOL_ENABLED=()
    while IFS=$'\t' read -r id name binary category description enabled; do
        [[ -n "$id" ]] || continue
        MF_TOOL_IDS+=("$id")
        MF_TOOL_NAMES+=("$name")
        MF_TOOL_COMMANDS+=("$binary")
        MF_TOOL_CATEGORIES+=("$category")
        MF_TOOL_DESCRIPTIONS+=("$description")
        MF_TOOL_ENABLED+=("$enabled")
    done < <(jq -r '.tools[] | [.id,.name,.command,.category,.description,.enabled] | @tsv' "$file")
}

mf_tool_available() {
    local tool_id="$1" i
    for i in "${!MF_TOOL_IDS[@]}"; do
        if [[ "${MF_TOOL_IDS[$i]}" == "$tool_id" ]]; then
            [[ "${MF_TOOL_ENABLED[$i]}" == true ]] || return 1
            command -v -- "${MF_TOOL_COMMANDS[$i]}" >/dev/null 2>&1
            return $?
        fi
    done
    return 1
}

# Invoke only a registered, enabled executable. Arguments remain an argv array;
# no eval, command-string parsing, or implicit shell expansion is performed.
mf_tool_run() {
    local tool_id="$1" i binary
    shift
    for i in "${!MF_TOOL_IDS[@]}"; do
        [[ "${MF_TOOL_IDS[$i]}" == "$tool_id" ]] || continue
        [[ "${MF_TOOL_ENABLED[$i]}" == true ]] || {
            printf 'ERROR: Tool is disabled: %s\n' "$tool_id" >&2; return 1;
        }
        binary="${MF_TOOL_COMMANDS[$i]}"
        command -v -- "$binary" >/dev/null 2>&1 || {
            printf 'ERROR: Required program is not installed: %s\n' "$binary" >&2; return 127;
        }
        "$binary" "$@"
        return $?
    done
    printf 'ERROR: Tool is not registered: %s\n' "$tool_id" >&2
    return 1
}
