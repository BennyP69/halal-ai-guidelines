#!/bin/bash
# Installs the halal-ai-guidelines skill for Claude Code (and optionally Codex) on this computer.
#   bash install.sh           -> Claude Code
#   bash install.sh --codex   -> Claude Code + Codex
# Safe to run again: it replaces the skill files and never adds the always-on rule twice.
set -euo pipefail
SRC="$(cd "$(dirname "$0")" && pwd)"
MARK="## Halal/haram check (halal-ai-guidelines)"
RULE="$MARK
I follow Salafi scholarship. Before any reply, content, or code that touches money, selling, chance, marketing honesty, music/images, food, or helping a business whose activity may be haram - even when nobody says \"haram\" - use the \`halal-ai-guidelines\` skill. Never state a ruling from memory. No verified source = say you are unsure. Otherwise stay silent about religion."

install_to() {  # $1 = skills dir, $2 = main instruction file
  local dest="$1/halal-ai-guidelines"
  mkdir -p "$1"
  if [ "$(cd "$SRC" && pwd -P)" != "$(cd "$dest" 2>/dev/null && pwd -P || true)" ]; then
    if [ -e "$dest" ] || [ -L "$dest" ]; then
      mv "$dest" "$dest.backup-$(date +%Y%m%d%H%M%S)"
    fi
    mkdir -p "$dest"
    cp "$SRC"/SKILL.md "$SRC"/sources.md "$SRC"/library.md "$SRC"/halal.py "$dest"/
  fi
  touch "$2"
  if grep -qF "Halal/haram check" "$2"; then
    echo "  always-on rule already in $2"
  else
    printf '\n%s\n' "$RULE" >> "$2"
    echo "  always-on rule added to $2"
  fi
  echo "  skill installed at $dest"
}

command -v python3 >/dev/null || { echo "Python 3 is required (https://www.python.org/downloads/)."; exit 1; }
python3 "$SRC/halal.py" --selftest >/dev/null
echo "Claude Code:"
install_to "$HOME/.claude/skills" "$HOME/.claude/CLAUDE.md"
if [ "${1:-}" = "--codex" ]; then
  echo "Codex:"
  install_to "$HOME/.codex/skills" "$HOME/.codex/AGENTS.md"
fi
command -v yt-dlp >/dev/null || echo "Note: yt-dlp not found, so YouTube search is skipped. Optional install: https://github.com/yt-dlp/yt-dlp"
echo "Done. Open a NEW Claude chat to use it."
