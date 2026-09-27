#!/usr/bin/env python3
"""Install the halal-ai-guidelines skill on this computer (Mac, Windows, Linux).

  python3 install.py              Claude Code / Claude desktop app (Code tab)
  python3 install.py --codex      also Codex
  python3 install.py --gemini     also Gemini CLI
  (On Windows type `python` or `py` instead of `python3`.)

Safe to run again: it replaces the skill files (the old copy is kept as a backup outside the
skills folder) and never adds the always-on rule twice. The older wording of the rule is
updated in place.
"""
import filecmp
import shutil
import subprocess
import sys
import time
from pathlib import Path

SRC = Path(__file__).resolve().parent
FILES = ["SKILL.md", "sources.md", "library.md", "halal.py"]
MARK = "## Halal/haram check (halal-ai-guidelines)"
START = ("I follow Salafi scholarship. Before any reply, content, or code that touches money, selling, "
         "chance, marketing honesty, music/images, food, or helping a business whose activity may be "
         'haram - even when nobody says "haram" - use the `halal-ai-guidelines` skill. Never state a '
         "ruling from memory. No verified source = say you are unsure. ")
OLD_RULE = START + "Otherwise stay silent about religion."
RULE = START + "Do not add religious commentary beyond what my own instructions ask for."
TOOLS = {"claude": (".claude", "CLAUDE.md"), "codex": (".codex", "AGENTS.md"),
         "gemini": (".gemini", "GEMINI.md")}


def install(tool):
    home = Path.home() / TOOLS[tool][0]
    dest, rules = home / "skills" / "halal-ai-guidelines", home / TOOLS[tool][1]
    # Same files already there (or installing from the skills folder itself): nothing to back up.
    if not all((dest / f).is_file() and filecmp.cmp(SRC / f, dest / f, shallow=False) for f in FILES):
        if dest.exists() or dest.is_symlink():
            # Backups live OUTSIDE the skills folder: a copy inside it would load as a second skill.
            stamp, n = time.strftime("%Y%m%d-%H%M%S"), 1
            backup = home / "halal-ai-guidelines-backups" / stamp
            while backup.exists():  # never move INTO an existing backup
                backup, n = backup.with_name(f"{stamp}-{n}"), n + 1
            backup.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(dest), str(backup))
            print(f"  old copy moved to {backup} (copy any rulings you added to library.md back in)")
        dest.mkdir(parents=True)
        for f in FILES:
            shutil.copy2(SRC / f, dest / f)
    print(f"  skill installed at {dest}")

    text = rules.read_text(encoding="utf-8") if rules.exists() else ""
    if OLD_RULE in text:
        rules.write_text(text.replace(OLD_RULE, RULE), encoding="utf-8")
        print(f"  always-on rule updated to the new wording in {rules}")
    elif "Halal/haram check" in text:
        print(f"  always-on rule already in {rules}")
    else:
        rules.parent.mkdir(parents=True, exist_ok=True)
        with rules.open("a", encoding="utf-8") as fh:
            fh.write(f"\n{MARK}\n{RULE}\n")
        print(f"  always-on rule added to {rules}")


if __name__ == "__main__":
    if sys.version_info < (3, 8):
        sys.exit("Python 3.8 or newer is required: https://www.python.org/downloads/")
    subprocess.run([sys.executable, str(SRC / "halal.py"), "--selftest"], check=True,
                   stdout=subprocess.DEVNULL)
    tools = ["claude"] + [t for t in ("codex", "gemini") if f"--{t}" in sys.argv]
    for t in tools:
        print(f"{t.capitalize()}:")
        install(t)
    if not shutil.which("yt-dlp"):
        print("Note: yt-dlp not found, so YouTube search is skipped. Optional: https://github.com/yt-dlp/yt-dlp")
    print("Done. Open a NEW chat to use it.")
