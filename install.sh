#!/bin/bash
# Mac/Linux shortcut. The real installer is install.py (it also works on Windows).
#   bash install.sh           -> Claude Code
#   bash install.sh --codex   -> Claude Code + Codex
set -euo pipefail
command -v python3 >/dev/null || { echo "Python 3 is required (https://www.python.org/downloads/)."; exit 1; }
exec python3 "$(cd "$(dirname "$0")" && pwd)/install.py" "$@"
