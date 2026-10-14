#!/usr/bin/env bash
# Offline installer for an extracted MForce package (no git clone required).
set -euo pipefail

package_root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
install_root="${MFORCE_INSTALL_DIR:-$HOME/.local/share/mforce-enhanced-framework}"
bin_dir="${MFORCE_BIN_DIR:-$HOME/.local/bin}"

if [[ ! -f "$package_root/xrm742.sh" || ! -f "$package_root/src/data/funcs.json" ]]; then
  printf 'Error: package is incomplete. Extract the full archive first.\n' >&2
  exit 1
fi
if [[ -e "$install_root" || -L "$install_root" ]]; then
  printf 'Error: %s already exists; no files were overwritten.\n' "$install_root" >&2
  exit 1
fi
if [[ -e "$bin_dir/mforce" || -L "$bin_dir/mforce" ]]; then
  printf 'Error: %s/mforce already exists; no files were overwritten.\n' "$bin_dir" >&2
  exit 1
fi
if [[ "$install_root" == "$package_root" ]]; then
  printf 'Error: destination must differ from package source.\n' >&2
  exit 1
fi
if ! command -v bash >/dev/null 2>&1; then
  printf 'Error: bash is required.\n' >&2
  exit 1
fi

mkdir -p "$(dirname -- "$install_root")" "$bin_dir"
mkdir -- "$install_root"
# The package is already extracted; copy all files, including dotfiles.
if ! cp -a -- "$package_root"/. "$install_root"/; then
  rm -rf -- "$install_root"
  printf 'Error: package copy failed.\n' >&2
  exit 1
fi

cat > "$bin_dir/mforce" <<'WRAPPER'
#!/usr/bin/env bash
set -euo pipefail
framework_dir="${MFORCE_INSTALL_DIR:-$HOME/.local/share/mforce-enhanced-framework}"
exec bash "$framework_dir/xrm742.sh" "$@"
WRAPPER
chmod 755 "$bin_dir/mforce"

printf 'MForce package installed: %s\n' "$install_root"
printf 'Launcher: %s/mforce\n' "$bin_dir"
printf 'Runtime requirements: bash, jq, python3 and supported Linux/Termux utilities.\n'
printf 'Run: %s/mforce\n' "$bin_dir"
