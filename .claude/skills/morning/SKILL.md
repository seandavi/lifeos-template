---
name: morning
description: "Daily journaling, reflection, and planning. Use when the user says 'morning', 'let's plan the day', 'journal', or similar. Loads calendar + email scan, reviews yesterday, checks emotional state, runs inbox hygiene, creates today's journal, offers an honest reality check, sets 1-3 priorities that ladder up to annual goals, updates now.md."
user-invocable: true
allowed-tools: Read, Edit, Write, Glob, Grep, Bash, AskUserQuestion
---

# Morning Journaling, Reflection & Planning

This skill runs the 11-step morning routine. The point: load context, take an honest read on yesterday + current state, set 1-3 priorities that ladder up to annual goals, and prevent drift in `now.md`.

**Tone:** Direct, curious, non-judgmental. Coach in the locker room, not greeting card. Push back if priorities don't connect to goals or if something obvious is being avoided. Use AskUserQuestion to force clear thinking — not to gather data for forms.

---

## Step 1: Calendar export + email scan (parallel)

Run both in parallel. Don't serialize.

**Calendar:**
```bash
<VAULT_ROOT>/calendar/export-calendar.sh
```
Then read `<VAULT_ROOT>/calendar/this-week.md`.

**Email scan:**
```bash
<VAULT_ROOT>/scripts/email-scan.sh
```
Then read `<VAULT_ROOT>/calendar/email-scan.md`.

If either fails: continue without it. Don't block the routine; note the failure briefly.

**Calendar gotchas to know:** Calendar exports include all sync'd calendars (often spouse's, shared work calendars, etc.). Verify event ownership before treating something as the user's commitment — e.g., a "travel to Lisbon" entry may belong to a partner.

---

## Step 2: Load yesterday + current state

In parallel:
- `<VAULT_ROOT>/journal/YYYY/MM/YYYY-MM-DD.md` for yesterday (calculate date with `date -v-1d "+%Y/%m/%Y-%m-%d"`). If missing, look back up to 7 days.
- `<VAULT_ROOT>/journal/YYYY/goals.md` — annual goals
- `<VAULT_ROOT>/now.md` — current state (substitute for full `projects.md` scan unless something specific needs checking)

Don't summarize yet. Just load.

---

## Step 3: Diary check

Read the latest entry in `<VAULT_ROOT>/personal/diary.md` (most-recent-first format — read from the top until you hit the next `---` divider).

This calibrates the rest of the routine: emotional state, recent reflections, anything the user is sitting with. Don't reference this back to them unless they ask — it's context for how to engage, not material to surface.

---

## Step 4: Inbox hygiene

Read `<VAULT_ROOT>/inbox.md` top-to-bottom. Identify candidates for removal:
- Past deadlines that have passed
- "Waiting on" items where the thing arrived (cross-reference recent journals / `completed.md`)
- Travel/dates that already happened

Confirm removals via AskUserQuestion (multiSelect). Don't auto-delete.

Then check `email-scan.md` for new items that should be added. For each new item, follow `inbox.md`'s section structure (`Action needed` / `Waiting on others` / `Keep warm`).

---

## Step 5: Review yesterday

Present a tight summary — what was planned vs. what happened. Don't just list. Reflect:
- Name what was avoided
- Call out patterns (third day this dropped?)
- Flag if "completed" is bookkeeping vs. real movement

Then ask the user to walk through yesterday via AskUserQuestion:
> "Walk me through yesterday — what happened, how did it go, anything worth reflecting on?"

Push back if something sounds like narrative rather than reality. Surface emotional signals when they show up — don't checkbox them.

**Update yesterday's journal** if reflections add value:
- Fill in the Log section with what actually happened
- Add Evening reflections if missing
- Mark completed to-dos as done
- Keep the user's voice — don't polish

---

## Step 6: Create today's journal

Path: `<VAULT_ROOT>/journal/YYYY/MM/YYYY-MM-DD.md`

If today's entry doesn't exist, create it from `<VAULT_ROOT>/templates/daily-journal.md`. Use today's actual day-of-week + date in the title.

---

## Step 7: Reality check & pep talk

This is a real step, not ritual filler. The diary read in Step 3 sets the tone.

Optionally read 1-2 recent files from `<VAULT_ROOT>/notes/` if relevant context might exist (e.g., a recent insight that connects to today).

Offer a brief honest reflection — typically 3-4 sentences total:

- **What's going well** — with specific evidence, not vague affirmation
- **What the anxiety is actually about** — name it, don't dance around it
- **Reminder to have fun with the work** — the actual work, not abstract
- **Something genuinely encouraging** that fits today's actual state

**Coach in the locker room, not greeting card.** Direct, specific, not saccharine.

Occasionally (not daily) include a light contextual nudge about life outside work — family, exercise, something enjoyable. Make it specific and natural. "Remember work-life balance" is the *opposite* of helpful.

If the diary shows acute stress: keep this step light and concrete. If it shows clarity: don't over-soften. Match the state. **Skip this step entirely on days when the user is in flow** — forcing it then is the wrong move.

---

## Step 8: Franklin's morning question

> "What good shall I do this day?"

Let the user answer. Translate into 1-3 concrete priorities for the "Highest stakes" section of today's journal. Don't accept vague answers ("be productive", "make progress"). Push: "What specifically would make today a win?"

---

## Step 9: Challenge priorities

For each priority the user names, do two checks:

**1. Does this connect to an annual goal?** If yes, name the link explicitly in the journal entry: `Priority 1 (connects to: [goal X])`. If no — fine for tactical items (admin, replies, scheduling), but flag if multiple "key" priorities are off-goals.

**2. What's being avoided?** Look at the past 5-7 days of journal entries. If the same hard thing keeps not making the list, name it.

If today's plan has 4+ "key" priorities: push back.
> "That's a lot. What's the *one* thing that matters most if everything else slips?"

---

## Step 10: Carry forward

For each unfinished item from yesterday's journal:
- **Still relevant for today** → add to today's journal (`Promoted from yesterday`)
- **Still relevant, not today** → move to `inbox.md` (`Action needed` section)
- **No longer relevant** → drop. Note in yesterday's journal entry: "dropped: no longer relevant."

Don't let zombie items pile up. Making the user decide is the value of the carry-forward step.

---

## Step 11: Update now.md

Quick pass over `<VAULT_ROOT>/now.md` Active table. For each project, ask: does the Status column reflect current reality based on this morning's context (yesterday's journal, calendar, email scan)?

- Update stale status lines
- Move resolved items off the Active table
- Update the `*Updated: YYYY-MM-DD*` date stamp at the top

This takes 2 minutes. Skipping it is how `now.md` drifts to lying within 10 days.

---

## Throughout the day

When something log-worthy comes up in conversation:
- Read today's journal file
- Append a timestamped entry in the Log section: `- HH:MM — Entry text`
- Tell the user: "Added to log: [brief summary]"
- Don't ask permission — keep the conversation flowing

When ideas/insights surface, create atomic notes in `<VAULT_ROOT>/notes/` per CLAUDE.md — don't ask, just do it and say "Noted: [filename]".

---

## Related skills

This skill is morning-only. For other parts of the day, use the dedicated skill:

- **Evening close** → `/end-of-day`
- **Weekly review** → `/weekly-review`
- **Vault audit** → `/audit`
- **Decision capture** → `/decide`
- **Quarterly review** → `/quarterly-review`

Do not try to do those flows from within `/morning`.
