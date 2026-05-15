---
name: decide-revisit
description: "Scheduled revisit of decisions whose Review Date has passed. Reads <VAULT_ROOT>/decisions/, filters to open decisions with overdue or due-today review dates, walks through each one comparing prediction vs reality, appends a revisit entry, and updates status. Use when user says 'revisit decisions', '/decide-revisit', or monthly on the 15th."
user-invocable: true
allowed-tools: Read, Edit, Glob, Bash, AskUserQuestion
---

# Decision Revisit

The periodic decision revisit. Decisions made prospectively are useless unless reality is compared to prediction. Surface decisions whose Review Date has arrived and walk through each one.

**Tone:** Calibration-focused. Honest accounting of what was predicted vs what actually happened — not retroactive justification. Push back on rewriting history. Collison's principle: "you don't need to be excellent at deciding, you need to be good at re-deciding."

---

## Step 1: Find decisions due

```bash
date "+%Y-%m-%d"
```

```
Glob: <VAULT_ROOT>/decisions/*.md
```

For each: extract Status, Review Date, title.

Filter to: `Status: Open` AND `Review Date <= today`.

If nothing's due, say so and stop. Don't manufacture work.

---

## Step 2: Walk through each decision

For each due decision, present in order of importance:

```
## [[YYYY-MM-DD-slug]] — {{title}}

Decided on YYYY-MM-DD. Confidence at the time: N/10. Predicted:
- 30d: {{prediction}}
- 90d: {{prediction}}

What actually happened?
```

Then AskUserQuestion:

> "How did this play out vs what you predicted?"
> - Right call, outcome matched prediction
> - Right call, outcome better than predicted
> - Right call, outcome worse than predicted (but not the alternative's fault)
> - Wrong call — alternative would have been better
> - Partial — some predictions right, some wrong
> - Too early to tell — extend review date

If "too early": ask for new review date.

---

## Step 3: Probe one level deeper

Based on the answer, push for the lesson:

- **Right call:** "What signal told you this would work? Is that signal repeatable?"
- **Wrong call:** "What signal did you miss or underweight? How would you recognize it earlier next time?"
- **Partial:** "Which prediction was right and why? Which was wrong and why?"

Don't accept "I just got lucky/unlucky" — push for the model.

---

## Step 4: Append revisit entry

In `## Revisit log`:

```markdown
### YYYY-MM-DD — Revisit

**Outcome:** {{Right call / Wrong call / Partial / Too early}}

**Prediction vs reality:**
- Predicted: {{summarize}}
- Actual: {{summarize}}

**Lesson:** {{the articulated model — what to recognize next time}}

**Status update:** {{If closing: set Status to Closed/Resolved + Closed: date. If extending: new Review Date.}}
```

Use Edit, not Write — preserve the rest.

---

## Step 5: Update frontmatter

If closing:
- `Status: Resolved` (or `Status: Closed-Wrong` for explicitly wrong calls — visible signal for future audits)
- `Closed: YYYY-MM-DD`
- Update `Decision:` line if outcome reshaped what was decided

If extending:
- New `Review Date:`
- Optionally bump `Confidence:` if shifted

---

## Step 6: Cross-cutting pattern check

If 3+ decisions revisited in one session, scan for patterns:

- All decisions involving same person trending same direction?
- All decisions made in anxious state going wrong?
- Confidence > 8 reliably right or wrong?

Surface any pattern with evidence. This is where decision logs compound — across decisions, not within one.

---

## Step 7: Capture lessons as notes

If a lesson generalizes beyond the specific decision, prompt to write it as an atomic note in `notes/`. Use `templates/note.md`. Wiki-link back to the decision.

---

## End state

- All overdue decisions closed, extended, or have revisit entries
- Pattern observations surfaced if multiple revisited
- New atomic notes for generalizable lessons
- Honest read on decision quality this period

If nothing due, the skill exits in one sentence.
