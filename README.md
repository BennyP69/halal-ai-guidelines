# Halal AI Guidelines

Makes your AI check halal/haram before it answers, writes, or builds something, using only
approved Salafi scholars (Ibn Baz, Ibn Uthaymeen, al-Albani, al-Fawzan and others, see
`sources.md`). It quotes the scholar with a link, checks the quote is really on the page,
and says "I'm not sure, ask a scholar" when it has no verified source. It never makes up a
ruling. It passes on what the scholars said; it is not a fatwa.

## How to install

Drop this zip (or folder) into Claude Code, the Claude desktop app's Code tab, Codex, or
Gemini CLI, and say:

> **Install this for me globally, including its always-on rule.**

Saying "including its always-on rule" matters: it tells the AI you want it to add a
permanent line to your global instructions. Without your say-so, a careful AI will
(correctly) ask first. Then open a new chat.

Installing means exactly two changes, nothing else:

**1. Copy the skill folder** (`SKILL.md`, `sources.md`, `library.md`, `halal.py`) into the
tool's skills folder. If a `halal-ai-guidelines` folder already exists there, rename it to
`halal-ai-guidelines.backup-<date>` first so no added rulings are lost.

| Tool | Skills folder | Global instructions file |
|---|---|---|
| Claude Code / Claude desktop app (Code tab) | `~/.claude/skills/halal-ai-guidelines/` | `~/.claude/CLAUDE.md` |
| Codex | `~/.codex/skills/halal-ai-guidelines/` | `~/.codex/AGENTS.md` |
| Gemini CLI | `~/.gemini/skills/halal-ai-guidelines/` | `~/.gemini/GEMINI.md` |

(`~` is your home folder; on Windows `%USERPROFILE%`.)

**2. Add this always-on rule** to the end of the global instructions file (only if a
"Halal/haram check" section is not already there):

```
## Halal/haram check (halal-ai-guidelines)
I follow Salafi scholarship. Before any reply, content, or code that touches money, selling, chance, marketing honesty, music/images, food, or helping a business whose activity may be haram - even when nobody says "haram" - use the `halal-ai-guidelines` skill. Never state a ruling from memory. No verified source = say you are unsure. Otherwise stay silent about religion.
```

Why the rule is needed: in testing (2026-09-19) the skill alone did not switch on for hidden
cases like late fees, credit cards, or pay-to-enter giveaways. With the rule it caught all of them.

**Check it worked:** `python3 <skills folder>/halal.py --selftest` prints `selftest ok`
(needs Python 3). Then in a new chat ask: "Add a 10% late fee clause to my payment plan."
It should warn you and cite al-Fawzan's ruling that late fees are riba.

Optional: `yt-dlp` adds YouTube search. Web chats (claude.ai, ChatGPT website) cannot
install this, because they cannot reach your computer's files.

Mac/Linux shortcut that does both steps: `bash install.sh` (add `--codex` for Codex too).

---

## What is inside

| File | What it does |
|---|---|
| `SKILL.md` | The instructions the AI follows |
| `sources.md` | The approved scholars, websites, and YouTube channels |
| `library.md` | Rulings already checked, with links and verified quotes |
| `halal.py` | Searches the sources, reads them, and checks quotes |
| `install.sh` | Manual installer for Mac/Linux: `bash install.sh` (add `--codex` for Codex) |
