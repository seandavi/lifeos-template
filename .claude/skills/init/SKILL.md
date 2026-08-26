---
name: init
description: "First-run personalization for a freshly-cloned LifeOS vault. Configures config.yaml with the user's name, email, timezone, and tool preferences, and optionally walks the user through writing their first plan.md / values.md. Idempotent — safe to re-run. Use when user says 'init', '/init', 'set this up', or it's the first time the vault is being used."
user-invocable: true
allowed-tools: Read, Edit, Write, Glob, Grep, Bash, AskUserQuestion
---

# Init — first-run personalization

You are setting up a freshly-cloned LifeOS vault for a specific user. Goal: configure `config.yaml` with user details, preferences, and external integration paths, and (optionally) seed `plan.md` / `values.md` so the system is ready to use.

**Tone:** Welcoming but efficient. This is a 5-minute setup, not a 30-minute conversation. Don't oversell. Ask only what's needed, do the work, hand off to `/orient` or `/morning`.

---

## Step 1: Gather core parameters

Use AskUserQuestion. One question at a time, don't form-dump.

1. **User's name & email** — for personalization in `config.yaml`, CLAUDE.md, and templates.
   - First name is enough; full name optional.
2. **Timezone** — for cron schedules and daily routines (auto-detect via `date "+%Z"`; offer as default).
3. **Email scanner backend** — for the daily email digest (gemini CLI, claude CLI, ollama, llm, or skip).
4. **Calendar source** — `icalBuddy` (macOS Calendar, captures Outlook+Google+iCloud) or custom script.
   - Note: `icalBuddy` requires `brew install ical-buddy` on macOS.
5. **Progress Tracking** — Ask: "Track effort by project? (yes/no)"

Skip questions whose answers are obvious from context.

---

## Step 2: Detect optional integrations

Some LifeOS features are **capability-gated**: they activate only when a
supporting tool is present, and disappear entirely when it isn't. No
configuration is stored, no settings go dead — detection happens again at the
moment of use.

Check what's available and report one line per integration — no questions:

```bash
command -v obsidian >/dev/null && echo "obsidian CLI: available" || echo "obsidian CLI: not found"
```

- **`obsidian` CLI** — turns the vault from a folder of files into a queryable
  knowledge graph (resolved wiki-links, vault-wide tasks, frontmatter
  properties). When present, the `/obsidian-cli` skill and the CLI-first paths
  in `/audit` activate automatically. When absent, everything falls back to
  Glob/Grep — no feature is lost, only speed and precision.

Report what was detected and move on.

---

## Step 3: Write configuration to `config.yaml`

Write or update `config.yaml` at the vault root:

```yaml
# LifeOS Central Vault Configuration

owner:
  name: "{{User Name}}"
  slug: "{{user-slug}}"
  email: "{{user.email@example.com}}"
  github: "{{github_username}}"

vault:
  name: "LifeOS"
  timezone: "{{Timezone}}"
  lookback_days: 14

# User tool & workflow preferences
tools:
  email_llm: "{{email_backend}}" # e.g. gemini --yolo, claude, etc.
  calendar_backend: "{{calendar_source}}" # e.g. icalBuddy
  track_effort_by_project: {{true|false}}

# Optional external integrations
external: {}
```

---

## Step 4: Personalize CLAUDE.md

Read `CLAUDE.md`. Add or update:
- A "User profile" section near the top with: name, role (ask once if not obvious), timezone
- The user's preferred salutation / how they want to be addressed
- The "Track effort by project" preference setting under guidelines (set to yes or no based on Step 1 choice)

---

## Step 5: (Optional) Seed plan.md and values.md

Ask: "Want to draft your core values and 10-year plan now, or start with daily journaling and do strategy later?"

If now:
- Walk through `values.md` (3-5 core principles)
- Walk through `plan.md` (10-year horizon, 3-year milestones)
- Keep it brief — drafting, not agonizing

If later:
- Leave the template placeholders in place
- Remind the user they can invoke `/quarterly-review` when ready for strategy

---

## Step 6: Hand off

Finish with:
> "Setup complete. Run `/orient` for a 5-minute tour of how the layers connect, or `/morning` to start today's plan."
