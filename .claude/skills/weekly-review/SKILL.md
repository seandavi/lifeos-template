---
name: weekly-review
description: "Weekly review of the life-OS vault. Reads the past 7 days of journal entries, inbox.md, now.md, goals.md, completed.md, decisions/, calendar, and GitHub state; surfaces what got done, what's stuck, what's drifting; updates now.md; flags inbox staleness and goals.md decay; drafts week-WW.md; forces one decision via AskUserQuestion. Use when the user says 'weekly review', '/weekly-review', 'friday cleanup', or it's a Friday/Sunday afternoon and a review hasn't happened this week."
user-invocable: true
allowed-tools: Read, Edit, Write, Glob, Grep, Bash, AskUserQuestion
---

# Weekly Review

You are running the Friday weekly review for the life-OS vault at `<VAULT_ROOT>`. The cadence layer is the bottleneck of most systems — your job is to make it real.

**Tone:** Critical partner. Direct, evidence-based, no participation trophies. Push back when items got marked done but were actually bookkeeping, or when "stuck" items are quietly zombie items. Use AskUserQuestion to force decisions, not just gather info.

---

## Step 1: Determine the week + load context

Run these in parallel:

1. **Date math via Bash:**
   ```bash
   date "+%Y-%m-%d %A"
   date "+%V"
   date -v-7d "+%Y-%m-%d"
   ```
   If today isn't Friday/Saturday/Sunday, ask the user which week boundary they want.

2. **Load these files in parallel:**
   - `<VAULT_ROOT>/inbox.md`
   - `<VAULT_ROOT>/now.md`
   - `<VAULT_ROOT>/journal/YYYY/goals.md`
   - `<VAULT_ROOT>/completed.md` (read top 50 lines)
   - `<VAULT_ROOT>/calendar/this-week.md`
   - `<VAULT_ROOT>/personal/diary.md` (top entry only)
   - `<VAULT_ROOT>/projects.md`

3. **Find this week's journal entries:**
   ```
   Glob: <VAULT_ROOT>/journal/YYYY/MM/YYYY-MM-DD.md for each of the past 7 dates
   ```

4. **Scan open decisions:**
   ```
   Glob: <VAULT_ROOT>/decisions/*.md
   ```
   Read any with `Status: Open` or `Status: Active`. Check `Review Date` fields.

5. **Pull GitHub state** (if `gh` is authenticated):
   ```bash
   gh issue list --state open --assignee @me --limit 30
   gh pr list --state open --author @me --limit 20
   ```

Get all loaded before synthesizing.

---

## Step 2: Synthesize four lenses

Build internal notes on:

### What got done
- `completed.md` entries with this week's dates
- Journal log entries (timestamped lines)
- Closed GitHub issues/PRs
- **Filter out bookkeeping** — closing items already done weeks ago. Real wins moved this week.

### What's stuck or drifting
- Projects in `now.md` Active table with no journal mention in 7+ days
- Inbox items with no movement (past deadlines, "OVERDUE" markers)
- `goals.md` last-modified date — flag if > 30 days
- `now.md` last-updated date — flag if > 10 days (self-reports as lying after 10)
- On-hold items — still waiting? Or quietly died?

### What got dropped
- Items in daily "Highest stakes" that didn't show up in the log
- Why (often: meeting ran long, different priority took over)
- Pattern recognition: same item dropping multiple days is a *system signal*

### Emotional / context arc
- Diary entry top — what mental state?
- Tone of journal logs (terse / expansive / frustrated)
- Use to calibrate how hard to push back; never use as an excuse to soften critical observations

---

## Step 3: Update now.md

Edit `<VAULT_ROOT>/now.md`:

1. Refresh the date stamp: `*Updated: YYYY-MM-DD*`
2. **This Week's Focus** → next week's hinges
3. **Active table:** for each project, update Status to reflect ground truth. Add new active projects. Move stalled items to On Hold *only with confirmation*.
4. **On Hold table:** mark resolved/active/still-on-hold; confirm before removing.
5. **On My Mind:** remove resolved items, add new drift signals.

Show the diff before writing.

---

## Step 4: Inbox triage

**Do not auto-delete.** List stale candidates in batches:

- Past deadline (explicit dates that have passed)
- Resolved waiting (cross-reference completed.md and journal logs)
- No movement (items in inbox.md but never in any recent journal)

Present 5-10 candidates at a time via AskUserQuestion multiSelect: "Which of these are done/stale and can be removed?" Then edit.

For confirmed-completed items, follow three-step completion (remove from inbox.md → append to completed.md with strategic context → check off in journal).

---

## Step 5: Decisions revisit

For each open decision:
- If `Review Date <= today`, surface it. Ask: "Current read?"
- If implicitly resolved (journal says "decided on X"), prompt to update the decision doc.

Do not modify decision docs without confirmation.

---

## Step 6: Goals.md decay check

If `goals.md` is > 30 days stale OR flagged for rewrite in `now.md` On My Mind:

- Do not rewrite now. That's a quarterly ritual.
- Surface as concrete blocker: "`goals.md` is N days stale. Block 60 min this weekend, or formally accept the current goals as legacy and rebuild in Q3?"

---

## Step 7: Draft week-WW.md

Write to `<VAULT_ROOT>/journal/YYYY/MM/week-WW.md` (ISO week number from Step 1). Use `<VAULT_ROOT>/templates/week-review.md` as the structure.

Show before writing.

---

## Step 8: Force ONE decision via AskUserQuestion

Pick the *single* most consequential drift signal. Examples:

> "`goals.md` is 42 days stale and you've flagged it twice. What's the move?"
> - Block Saturday 9-10am for rewrite
> - Accept current goals as legacy, rebuild in Q3
> - Push to next quarterly review with a committed date

---

## Step 9: Confirm writes + commit

Before writing `now.md` updates or `week-WW.md`, present a brief diff summary. Once confirmed, write.

Offer to commit:
```bash
cd <VAULT_ROOT> && git add -A && git commit -m "weekly review: week WW"
```
Don't push without explicit ask.

---

## What to NOT do

- Don't rewrite `goals.md` (quarterly ritual).
- Don't auto-delete inbox items.
- Don't write to `personal/diary.md`.
- Don't replace `now.md` wholesale — diff and confirm.
- Don't promise "next week will be different."
- Don't soften critical observations because the diary shows stress.

---

## End state

- Updated `now.md` reflecting current ground truth
- New `week-WW.md` capturing the week
- Inbox triaged (with confirmation)
- One forcing-decision asked + answered
- Optionally: a commit
