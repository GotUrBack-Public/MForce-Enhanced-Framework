#!/usr/bin/env bash
# Install MForce Enhanced Framework into the user's home directory.
set -euo pipefail

repo_url="https://github.com/GotUrBack-Public/MForce-Enhanced-Framework.git"
install_root="${MFORCE_INSTALL_DIR:-$HOME/.local/share/mforce-enhanced-framework}"
bin_dir="${MFORCE_BIN_DIR:-$HOME/.local/bin}"

if ! command -v git >/dev/null 2>&1; then
  printf 'Error: git is required.\n' >&2
  exit 1
fi
if ! command -v bash >/dev/null 2>&1; then
  printf 'Error: bash is required.\n' >&2
  exit 1
fi
if [[ -e "$install_root" ]]; then
  printf 'Error: %s already exists. Existing installations are not overwritten.\n' "$install_root" >&2
  exit 1
fi
mkdir -p "$(dirname "$install_root")" "$bin_dir"
git clone --depth 1 "$repo_url" "$install_root"

# A wrapper is necessary because the framework resolves assets relative to its root.
cat > "$bin_dir/mforce" <<'WRAPPER'
#!/usr/bin/env bash
set -euo pipefail
framework_dir="${MFORCE_INSTALL_DIR:-$HOME/.local/share/mforce-enhanced-framework}"
exec bash "$framework_dir/xrm742.sh" "$@"
WRAPPER
chmod 755 "$bin_dir/mforce"

printf 'Installed MForce into %s\n' "$install_root"
printf 'Launcher: %s/mforce\n' "$bin_dir"
printf 'Ensure %s is on your PATH.\n' "$bin_dir"
printf 'Runtime dependencies: bash, jq, python3/python, coreutils, ncurses, iproute2 (see README).\n'
