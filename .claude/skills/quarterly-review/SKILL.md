---
name: quarterly-review
description: "Heavy strategic review, run quarterly. Reads plan.md (10-year), goals.md (annual), last 90 days of journals + completed.md + decisions + weekly reviews, surfaces themes and patterns, forces a goals.md rewrite if conditions have changed, sets next quarter's 3 priorities, optionally updates plan.md. Use when user says 'quarterly review', '/quarterly-review', or scheduled for the 1st of Jan/Apr/Jul/Oct."
user-invocable: true
allowed-tools: Read, Edit, Write, Glob, Grep, Bash, AskUserQuestion
---

# Quarterly Review

The heavy ritual — 60-90 minutes, not a quick check. This is the skill that catches a stale `goals.md` *before* it gets a month stale. The point is **re-decision**: not "did the plan work" but "is this still the right plan."

**Tone:** Critical strategic partner. Question premises, not just execution. The default failure mode is rubber-stamping last quarter's plan with a fresh date. Force genuine re-evaluation. If the quarter's biggest events didn't show up in goals.md, that's the system's failure to update — not the user's.

---

## Step 1: Load full context

```bash
date "+%Y-%m-%d"
date "+%Y"
date -v-90d "+%Y-%m-%d"
```

In parallel:
- `<VAULT_ROOT>/plan.md`
- `<VAULT_ROOT>/journal/YYYY/goals.md`
- `<VAULT_ROOT>/values.md`
- `<VAULT_ROOT>/now.md`
- `<VAULT_ROOT>/completed.md` (last 90 days)
- `<VAULT_ROOT>/projects.md`

Weekly reviews from the last quarter:
```
Glob: <VAULT_ROOT>/journal/YYYY/MM/week-*.md
```

Decisions in the last quarter:
```
Glob: <VAULT_ROOT>/decisions/*.md
```
Filter by Opened date or modification date in last 90 days.

Diary entries from the last quarter — for emotional arc.

---

## Step 2: Establish the quarter's narrative

Synthesize 200-300 words from the evidence:

```
# Q{{N}} YYYY Narrative — DRAFT

## The quarter in 3 sentences
{{One sentence: what dominated. One: what shifted. One: where it ended.}}

## Major events
- {{decisions opened/closed}}
- {{external shocks}}
- {{relationships started/changed}}
- {{real wins (not bookkeeping)}}

## Emotional / energy arc
{{From diary — pattern of state across the quarter}}

## What went unaddressed
{{Goals with zero action; "On My Mind" items that persisted}}
```

Show this and ask: "Does this match your read of the quarter? What's missing or wrong?"

---

## Step 3: Walk through annual goals item by item

For each goal in `goals.md`:

1. Read the goal as written.
2. Find evidence of progress — `completed.md` entries, journal mentions, decision activity.
3. Rate: On track / Behind / Stalled / Conditions changed.
4. Push back on "on track" with thin evidence.
5. If conditions changed: "What's the new shape?"

Document each in working notes.

---

## Step 4: The premise check

Force the meta-question:

> "What's true about you now that wasn't true at the start of the year?"
> - Role / position changed
> - Geographic situation changed
> - Health / energy state changed
> - Strategic priorities reframed
> - Network / relationships shifted
> - All of the above

Sit with this. Don't rush. Establish first what's actually changed.

---

## Step 5: Force rewrite or formal legacy

> "Goals.md as written is stale. What's the call?"
> - Rewrite goals.md now (60+ min — will draft, you edit)
> - Formally accept current goals as legacy, write new ones at end of quarter
> - Surgical edits — fix specific items, keep structure

If "rewrite now":
- Use `<VAULT_ROOT>/templates/goals.md` as the structure
- Draft based on narrative + premise check
- Use AskUserQuestion liberally — one goal at a time
- Reference plan.md to ensure goals ladder up

If "legacy":
- Add header to `goals.md`: `**Status:** Legacy as of YYYY-MM-DD. New goals being drafted Q{{N+1}}.`
- Create `goals.md.legacy-YYYY-Q{{N}}` archive copy

---

## Step 6: Set Q{{N+1}} priorities (3, max)

Force selection of 3 priorities. Not 5, not 7. Three.

Each priority should be:
- **Specific enough to know if it happened** (not "make progress on X")
- **Tied to an annual goal** (or named as adding to goals.md)
- **Have a deliverable or signal** by quarter end

Write to `<VAULT_ROOT>/journal/YYYY/Q{{N+1}}-priorities.md` or append to goals.md.

---

## Step 7: Plan.md health check

Re-read `plan.md`. Ask: "Is anything in the 10-year vision wrong now?"

Most quarters: no — plan.md should move slowly. Every few quarters something does shift. If so:
- Capture the shift as a note (`notes/`)
- Sketch the edit
- Sit on it for a week before actually editing plan.md (long-horizon stuff deserves a cooling period)

---

## Step 8: Decisions review

For decisions made this quarter:
- How many right calls / wrong calls / partial / still-open?
- Patterns?
- Note lessons from `/decide-revisit`

Summarize. Don't re-do `/decide-revisit`.

---

## Step 9: Write the quarterly review file

Path: `<VAULT_ROOT>/journal/YYYY/Q{{N}}-review.md`

```markdown
# Q{{N}} YYYY Review — Completed YYYY-MM-DD

## Narrative
{{From Step 2}}

## Goals progress
{{Per-goal rating + evidence}}

## What changed
{{From Step 4 — premise check}}

## Goals.md disposition
{{Rewritten / Legacy / Surgical edits}}

## Q{{N+1}} priorities
1.
2.
3.

## Decisions
{{Tally + lessons}}

## Plan.md disposition
{{Health-checked: no change / edit pending / shifted}}

## Open question for next quarter
{{ONE pointed question}}
```

---

## Step 10: Update now.md (and memory if used)

The quarterly review changes the strategic frame. Update:
- `<VAULT_ROOT>/now.md` to reflect new priorities
- (If Claude Code memory is in use) project memory file with new key context

Confirm before writing.

---

## What to NOT do

- Don't rubber-stamp last quarter's plan with new dates.
- Don't soften findings because the quarter was hard.
- Don't write more than 3 priorities for the next quarter.
- Don't update plan.md in the same session as the review.
- Don't draft goals.md without showing each goal for ratification.

---

## End state

- A Q{{N}}-review.md file
- goals.md rewritten / archived as legacy / surgically edited (with explicit choice)
- 3 priorities for Q{{N+1}}
- now.md updated to reflect new frame
- One open question carried forward
