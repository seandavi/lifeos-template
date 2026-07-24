#!/usr/bin/env bash
# Opt-in setup for the LifeOS Obsidian dashboard layer.
#
# Installs the Tasks community plugin and enables the native Bases core plugin
# for THIS vault. Everything it does is reversible and vault-local (.obsidian/).
# Safe to re-run (idempotent). Nothing in LifeOS requires this — skip it entirely
# if you don't use Obsidian.
#
# Usage:  bash scripts/setup-obsidian.sh
set -euo pipefail

VAULT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OBS="$VAULT_ROOT/.obsidian"
PLUGIN_ID="obsidian-tasks-plugin"
PLUGIN_DIR="$OBS/plugins/$PLUGIN_ID"

echo "Vault: $VAULT_ROOT"
mkdir -p "$PLUGIN_DIR"

echo "==> Fetching latest Tasks plugin release..."
API="https://api.github.com/repos/obsidian-tasks-group/obsidian-tasks/releases/latest"
for asset in main.js manifest.json styles.css; do
  url="$(curl -fsSL "$API" | grep -oE "https://[^\"]*/download/[^\"]*/$asset" | head -1)"
  if [ -z "$url" ]; then
    echo "ERROR: could not resolve download URL for $asset" >&2; exit 1
  fi
  curl -fsSL "$url" -o "$PLUGIN_DIR/$asset"
  echo "    got $asset"
done

echo "==> Enabling Tasks in community-plugins.json ..."
python3 - "$OBS" "$PLUGIN_ID" <<'PY'
import json, sys, pathlib
obs, pid = pathlib.Path(sys.argv[1]), sys.argv[2]
f = obs / "community-plugins.json"
data = json.loads(f.read_text()) if f.exists() and f.read_text().strip() else []
if pid not in data:
    data.append(pid)
f.write_text(json.dumps(data, indent=2) + "\n")
print("    community-plugins.json:", data)
PY

echo "==> Ensuring the native Bases core plugin is enabled ..."
python3 - "$OBS" <<'PY'
import json, sys, pathlib
obs = pathlib.Path(sys.argv[1])
f = obs / "core-plugins.json"
data = json.loads(f.read_text()) if f.exists() and f.read_text().strip() else {}
if isinstance(data, list):        # very old Obsidian used a list form
    if "bases" not in data: data.append("bases")
else:
    data["bases"] = True
f.write_text(json.dumps(data, indent=2) + "\n")
print("    bases enabled")
PY

cat <<'EOF'

Done. Two manual steps remain (Obsidian can't be scripted for these):
  1. In Obsidian: Settings -> Community plugins -> "Turn on community plugins"
     (accept the dialog). This is off by default in a fresh vault.
  2. Reload Obsidian (Cmd/Ctrl-R, or quit & reopen) so it scans the new plugin.
     Then Settings -> Community plugins -> enable "Tasks".

Open dashboards/Home.md to see the Bases dashboards.
Optional: `uv run scripts/vault_lint.py` validates note frontmatter.
EOF
