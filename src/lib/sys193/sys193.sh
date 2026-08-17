#!/data/data/com.termux/files/usr/bin/bash

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"

get_value() {
    local value="$1"

    if [[ -n "$value" ]]; then
        printf '%s\n' "$value"
    else
        printf 'Unavailable\n'
    fi
}

clear

printf '\033[1;36m'
printf '╔══════════════════════════════════════════════════════╗\n'
printf '║                 MFORCE ENHANCED                      ║\n'
printf '╠══════════════════════════════════════════════════════╣\n'
printf '║                 SYSTEM INFORMATION                   ║\n'
printf '╚══════════════════════════════════════════════════════╝\n'
printf '\033[0m'

printf '\n'
printf '\033[1;37mPlatform\033[0m\n\n'

if [[ -n "${PREFIX:-}" ]]; then
    printf 'Environment    : Termux\n'
else
    printf 'Environment    : %s\n' "$(uname -s 2>/dev/null)"
fi

printf 'Architecture   : '
get_value "$(uname -m 2>/dev/null)"

printf 'Kernel         : '
get_value "$(uname -sr 2>/dev/null)"

printf '\n'
printf '\033[1;37mAndroid\033[0m\n\n'

printf 'Android        : '
get_value "$(getprop ro.build.version.release 2>/dev/null)"

printf 'SDK            : '
get_value "$(getprop ro.build.version.sdk 2>/dev/null)"

printf 'Device         : '
get_value "$(getprop ro.product.model 2>/dev/null)"

printf '\n'
printf '\033[1;37mRuntime\033[0m\n\n'

printf 'Shell          : '
get_value "${SHELL:-}"

printf 'Termux Prefix  : '
get_value "${PREFIX:-}"

printf 'CPU Cores      : '
if command -v nproc >/dev/null 2>&1; then
    nproc
else
    printf 'Unavailable\n'
fi

printf 'Hostname       : '
get_value "$(hostname 2>/dev/null)"

printf '\n'
printf '\033[90mPress ENTER to return...\033[0m\n'

read -r

exec "$ROOT_DIR/src/ui/fs.sh" "sys" "System"
