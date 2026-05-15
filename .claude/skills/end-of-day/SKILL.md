---
name: end-of-day
description: "Closing ritual for the daily journal. Reads today's journal, lifts completed items to completed.md with strategic context, prompts for atomic notes / decisions captured during the day, asks Franklin's evening question, optionally prompts a diary entry, carries forward incomplete items to tomorrow. Use when user says 'end of day', '/end-of-day', 'wrapping up', 'evening', or similar."
user-invocable: true
allowed-tools: Read, Edit, Write, Glob, Bash, AskUserQuestion
---

# End-of-Day Close

The mirror of `/morning`. Close the daily loop in 10 minutes so nothing escapes capture and tomorrow starts clean.

**Tone:** Direct. No padding. 5-10 minute ritual, not therapy.

---

## Step 1: Load today

```bash
date "+%Y-%m-%d"
```

Read:
- `<VAULT_ROOT>/journal/YYYY/MM/YYYY-MM-DD.md` (today)
- `<VAULT_ROOT>/inbox.md`
- `<VAULT_ROOT>/completed.md` (top 20 lines for format reference)

If today's journal doesn't exist: "No journal for today — did you skip morning? Want me to backfill from completed work and inbox movement?"

---

## Step 2: Summarize the day from the log

Identify:
- What got done (log entries, items marked done in journal)
- What didn't happen from morning's "Highest stakes"
- Anything that surfaced as a new thread / project / decision

Present a tight summary (3-5 lines). No more.

---

## Step 3: Lift completed items to completed.md

For each completed item in today's journal:
1. Confirm with the user: "Closing these — confirm?"
2. For each confirmed item, prompt for **strategic context** (one line) if not obvious. From CLAUDE.md: entries must be substantial enough to inform annual evaluations.
3. Append to `completed.md` under today's date heading (`## YYYY-MM-DD`), creating the heading if needed.
4. Use Edit to keep completed.md sorted: most recent date at top.

Entry format:
```markdown
- [x] **{{What was done}}** — {{One-line outcome}} (Impact: {{strategic context}})
```

Three-step completion: inbox check → completed.md append → journal check.

---

## Step 4: Capture what surfaced

Two AskUserQuestion prompts:

> "Anything to capture as a note?"
> - Yes — describe it briefly, I'll write it to notes/
> - No

If yes: write atomic note to `<VAULT_ROOT>/notes/{slug}.md` using `templates/note.md`.

> "Anything to capture as a decision?"
> - Yes — I'll trigger /decide
> - No

If yes: invoke the `/decide` skill.

Don't force these — most days, neither happens. If today *was* substantive, push lightly.

---

## Step 5: Diary check

> "Anything for diary?"
> - Yes
> - No (default)

Don't push if no. If yes, prepend to `<VAULT_ROOT>/personal/diary.md` (most-recent-first format). Match the existing voice; don't sanitize.

---

## Step 6: Carry forward

Read today's journal "Highest stakes" / "Today's calendar". For each unfinished item:
- **Carry forward** to inbox.md
- **Leave in journal** as historical record (the right call to drop)

Ask the user for each: "Carry forward, drop, or move to inbox?"

For items moving to inbox: append to the `## Action needed` section at the top.

---

## Step 7: Append evening section

Edit today's journal to fill in the Evening section (Franklin's "What good have I done today?"). Let the user speak — don't paraphrase. If they give nothing, leave empty rather than invent.

---

## Step 8: Offer commit

```bash
cd <VAULT_ROOT> && git status --short
```

If there are uncommitted changes, offer:
> "Commit today's work? Suggested message: 'end of day: YYYY-MM-DD'"

Don't push unless asked.

---

## What to NOT do

- Don't summarize back what the user said.
- Don't add "Great work today!" cheerleading.
- Don't write to diary unless explicitly asked.
- Don't force note/decision capture — ask once each.
- Don't carry forward zombie items by default.

---

## End state

- Today's journal Evening section filled in
- completed.md updated with today's wins + strategic context
- New notes/decisions captured if surfaced
- Inbox carries tomorrow's unfinished items
- Optionally: a clean commit
- Ritual ends in 5-10 minutes
