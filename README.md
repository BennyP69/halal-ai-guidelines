# Halal AI Guidelines

Makes your AI check halal/haram before it answers, writes, or builds something, using only
approved Salafi scholars (Ibn Baz, Ibn Uthaymeen, al-Albani, al-Fawzan and others, see
[`sources.md`](sources.md)).

- It quotes the scholar with a link, and checks the quote is really on that page.
- When it has no checked source, it says "I'm not sure, ask a scholar".
- It never makes up a ruling. It passes on what the scholars said; it is not a fatwa.

Works with **Claude Code**, the **Claude desktop app (Code tab)**, **Codex**, and **Gemini CLI**.
It does not work in web chats (claude.ai, the ChatGPT website), because they cannot reach
the files on your computer.

---

## Install (easiest way, 1 minute)

Open Claude Code, the Claude desktop app's **Code** tab, Codex, or Gemini CLI, and paste:

> **Install the halal-ai-guidelines skill from https://github.com/BennyP69/halal-ai-guidelines for me globally, including its always-on rule.**

Then **open a new chat**. Done.

The words "including its always-on rule" matter. They tell the AI you want it to add one
permanent line to your AI's instructions (see [What installing changes](#what-installing-changes)).
Without your say-so, a careful AI will ask you first.

## Install by hand

**1. Have Python 3.** Macs and Linux usually have it. On Windows, get it from
[python.org/downloads](https://www.python.org/downloads/) and tick **"Add python.exe to PATH"**
during setup.

**2. Download this skill.** Click the green **Code** button at the top of this page, then
**Download ZIP**, and unzip it. (Or, if you use git: `git clone https://github.com/BennyP69/halal-ai-guidelines`.)

**3. Run the installer** from inside the unzipped folder:

| Your computer | Type this in Terminal / PowerShell |
|---|---|
| Mac or Linux | `python3 install.py` |
| Windows | `py install.py` |

Add `--codex` to also install for Codex, or `--gemini` for Gemini CLI, for example
`python3 install.py --codex`.

**4. Open a new chat.**

## Check it worked

1. Run `python3 ~/.claude/skills/halal-ai-guidelines/halal.py --selftest`
   (Windows PowerShell: `py "$env:USERPROFILE\.claude\skills\halal-ai-guidelines\halal.py" --selftest`;
   Command Prompt: `py "%USERPROFILE%\.claude\skills\halal-ai-guidelines\halal.py" --selftest`).
   It should print `selftest ok`.
2. In a new chat, ask: **"Add a 10% late fee clause to my payment plan."**
   The AI should warn you and cite al-Fawzan's ruling that late fees are riba (interest).

## What installing changes

Exactly two things, nothing else:

**1. The skill folder** (`SKILL.md`, `sources.md`, `library.md`, `halal.py`) is copied into your
AI tool's skills folder:

| Tool | Skills folder | Instructions file |
|---|---|---|
| Claude Code / Claude desktop app (Code tab) | `~/.claude/skills/halal-ai-guidelines/` | `~/.claude/CLAUDE.md` |
| Codex | `~/.codex/skills/halal-ai-guidelines/` | `~/.codex/AGENTS.md` |
| Gemini CLI | `~/.gemini/skills/halal-ai-guidelines/` | `~/.gemini/GEMINI.md` |

(`~` means your home folder; on Windows that is `%USERPROFILE%`, e.g. `C:\Users\you`.)

If an older copy is already there, it is moved to `halal-ai-guidelines-backups` next to the
skills folder first (not inside it, so the AI never loads two copies).

**2. This always-on rule** is added to the end of your instructions file, once:

```
## Halal/haram check (halal-ai-guidelines)
I follow Salafi scholarship. Before any reply, content, or code that touches money, selling, chance, marketing honesty, music/images, food, or helping a business whose activity may be haram - even when nobody says "haram" - use the `halal-ai-guidelines` skill. Never state a ruling from memory. No verified source = say you are unsure. Do not add religious commentary beyond what my own instructions ask for.
```

Why the rule is needed: in testing, the skill alone did not switch on for hidden cases like
late fees, credit cards, or pay-to-enter giveaways. With the rule it caught all of them.

If you are installing by asking your AI, it should make exactly these two changes.

## Update to a newer version

Download it again and run the installer again (or paste the install sentence again). Your
old copy is kept in `halal-ai-guidelines-backups`. If you added your own rulings to
`library.md`, copy them from the backup into the new file.

## Optional: YouTube search

Install [yt-dlp](https://github.com/yt-dlp/yt-dlp) and the skill also searches 13 approved
YouTube channels. Videos are treated as leads only, never as exact quotes.

---

## What is inside

| File | What it does |
|---|---|
| `SKILL.md` | The step-by-step instructions the AI follows |
| `sources.md` | The approved scholars, websites, and YouTube channels, and which ones are reachable |
| `library.md` | Rulings already checked, with links and word-for-word verified quotes |
| `halal.py` | Searches the sources, reads a page, and checks a quote is really on it |
| `install.py` | The installer (Mac, Windows, Linux). `install.sh` is a Mac/Linux shortcut to it |

`halal.py` commands (Windows: `py` instead of `python3`):

```
python3 halal.py search "late fee" --ar "غرامة التأخير"   # search the sources, English + Arabic
python3 halal.py read URL                                 # read a source page's main answer
python3 halal.py verify URL "exact words"                 # is this quote really on that page?
python3 halal.py recheck                                  # re-check every quote in library.md
python3 halal.py --selftest                               # quick self-check, no internet needed
```

## Honest limits

- This passes on what the scholars said. It is not a fatwa. For a new or complex case, ask a
  scholar; the skill helps you write the question.
- Some official sites cannot be read by scripts right now (al-Fawzan's site has an expired
  security certificate; alifta.gov.sa and troid.org block or time out). The skill says so
  instead of guessing. Current status is in [`sources.md`](sources.md).
- Websites move pages. `python3 halal.py recheck` shows whether every saved quote still
  matches its link (last full pass: 2026-09-27, 19 of 19 quotes found).
