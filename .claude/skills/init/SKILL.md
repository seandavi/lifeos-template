---
name: init
description: "First-run personalization for a freshly-cloned LifeOS vault. Asks for the user's name, vault root path, timezone, and tool preferences (email scanner, etc.), then substitutes <VAULT_ROOT> throughout all skill files + CLAUDE.md. Optionally walks the user through writing their first plan.md / values.md. Idempotent — safe to re-run. Use when user says 'init', '/init', 'set this up', or it's the first time the vault is being used."
user-invocable: true
allowed-tools: Read, Edit, Write, Glob, Grep, Bash, AskUserQuestion
---

# Init — first-run personalization

You are setting up a freshly-cloned LifeOS vault for a specific user. Goal: replace the `<VAULT_ROOT>` placeholder throughout all skill files + CLAUDE.md, gather a few key preferences, and (optionally) seed `plan.md` / `values.md` so the system is ready to use.

**Tone:** Welcoming but efficient. This is a 5-minute setup, not a 30-minute conversation. Don't oversell. Ask only what's needed, do the work, hand off to `/orient` or `/morning`.

---

## Step 0: Detect re-run

Check if `<VAULT_ROOT>` still appears anywhere in the vault:

```bash
grep -rln '<VAULT_ROOT>' . --include="*.md" --include="*.sh" 2>/dev/null | head -5
```

If no matches: greet briefly and ask "Looks like this vault is already initialized. Want me to re-run setup anyway (reset paths) or skip?"

---

## Step 1: Gather core parameters

Use AskUserQuestion. One question at a time, don't form-dump.

1. **Vault root path** (absolute) — where this vault lives.
   - Auto-detect with `pwd` from where init was run; offer that as the default.
   - Validate it's an absolute path that exists.

2. **User's name** — for personalization in CLAUDE.md and templates.
   - First name is enough; full name optional.

3. **Timezone** — for cron schedules later.
   - Auto-detect via `date "+%Z"`; offer that as default.

4. **Email scanner backend** — for the daily email digest.
   - Options: gemini CLI (default), claude CLI, ollama, llm (Simon Willison's), skip
   - This sets `EMAIL_LLM` in the email-scan script.

5. **Calendar source** — `icalBuddy` (macOS Calendar, captures Outlook+Google+iCloud) or "I'll wire my own."
   - Note that `icalBuddy` requires `brew install ical-buddy` on macOS.

Skip questions whose answers are obvious from context.

---

## Step 2: Substitute `<VAULT_ROOT>` throughout

Find all files containing the placeholder:
```bash
grep -rln '<VAULT_ROOT>' . --include="*.md" --include="*.sh" 2>/dev/null
```

For each file, use Edit with `replace_all: true`:
- old_string: `<VAULT_ROOT>`
- new_string: the actual path the user supplied

Report progress: "Updated N files."

---

## Step 3: Personalize CLAUDE.md

Read `<VAULT_ROOT>/CLAUDE.md`. Add or update:
- A "User profile" section near the top with: name, role (ask once if not obvious), timezone
- The user's preferred salutation / how they want to be addressed

Show the diff before writing.

---

## Step 4: Set EMAIL_LLM in email-scan.sh

If the user picked a non-default email scanner, edit `<VAULT_ROOT>/scripts/email-scan.sh`:
- Update the `LLM_CMD="${EMAIL_LLM:-gemini --yolo}"` default to match their choice
- Add a comment near the top noting the chosen backend

---

## Step 5: Seed plan.md and values.md (optional)

> "Want to populate plan.md and values.md now (10 min), or skip and come back later?"
> - Populate now
> - Skip — I'll do it before the first /quarterly-review

If populate now:
- Read `<VAULT_ROOT>/plan.md` (currently a template)
- Walk the user through the 4 sections: 10-year picture, optimizing for, not optimizing for, the bets
- Use AskUserQuestion for each section; one focused question, not a form
- Write their answers in their voice — don't polish

Same flow for `values.md` if they want.

Do NOT write `goals.md` here — annual goals deserve their own session via `/quarterly-review`.

---

## Step 6: Create today's journal

If `<VAULT_ROOT>/journal/$(date +%Y)/$(date +%m)/$(date +%Y-%m-%d).md` doesn't exist:
- Create the directory
- Copy from `templates/daily-journal.md`
- Fill in title with today's date

---

## Step 7: Initialize git (if not already)

```bash
cd <VAULT_ROOT>
git status 2>&1
```

If "not a git repository":
- Offer to `git init -b main`
- Offer to make an initial commit: "init: personalized LifeOS for {{user's name}}"

If already a git repo: skip.

---

## Step 8: Hand off

```
Setup complete. Suggested next step:
- Run /orient for a 5-minute tour of the components
- Or run /morning tomorrow to start the daily rhythm

The full set of skills is in CLAUDE.md.
```

If running on a Friday: also suggest `/weekly-review` after a week of using `/morning`.

---

## What to NOT do

- Don't draft goals.md (that's `/quarterly-review`).
- Don't push back on the user's chosen vault root path; they know their filesystem.
- Don't burn 30 minutes on personalization questions; 5-10 is the bar.
- Don't ask "are you sure?" for every step — show the diff once, confirm once, move on.

---

## End state

- All `<VAULT_ROOT>` placeholders replaced with actual path
- CLAUDE.md personalized
- email-scan.sh and other scripts configured to the user's tooling
- Optionally: plan.md / values.md seeded
- Today's journal exists
- Git initialized if needed
- User pointed at `/orient` or `/morning`
