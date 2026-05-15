---
name: decide
description: "Capture a decision prospectively in Patrick Collison / Farnam Street format. Writes to <VAULT_ROOT>/decisions/YYYY-MM-DD-slug.md with context, alternatives, prediction, confidence, key factors, emotional state, and a revisit date. Forces articulation before action. Use when user says 'decide', '/decide', 'capture this decision', 'I'm going to X', or surfaces a substantive choice (hire, grant, role, structural commitment)."
user-invocable: true
allowed-tools: Read, Write, Glob, AskUserQuestion
---

# Capture a Decision

You are capturing a decision in standard format so it can be revisited later. This is the **forcing** ritual — most decisions happen in journal entries and get lost. Your job: extract the decision into a structured record with predictions and a revisit date.

**Tone:** Critical partner. Push back on stated confidence vs evidence. Force articulation of the worst case. Ask "what would change your mind?" If the decision is reversible and low-stakes, suggest skipping the formal record and just journaling it.

---

## Step 1: Disambiguate

If invoked with a specific decision in mind, confirm. If not: "What decision are we capturing?"

Then ask:
1. **Is this actually a decision worth recording?** A decision worth recording:
   - Has a stake (money, time, reputation, structural commitment)
   - Has at least one real alternative
   - Will look different in retrospect than it does now

   If it fails all three, suggest journaling instead.

2. **Is it reversible?** Reversible decisions need lighter capture (1-page). Irreversible decisions need heavier capture (worst-case alternative, premortem).

---

## Step 2: Pull structured fields

Use AskUserQuestion liberally — one or two fields at a time. Don't dump a form.

Required:
- **Slug** (kebab-case, e.g., `accept-new-role-x`)
- **Context** — 2-3 sentences: situation, stake
- **Decision** — what's being chosen
- **Alternatives** — 2-3 things considered and *why rejected*
- **Prediction** — what you expect in 30/90/365 days
- **Confidence** — 1-10. If > 7, ask "what evidence justifies that?"
- **Key factors** — constraints, preferences, deadlines
- **Worst case** — if this goes wrong, what does that look like?
- **What would change your mind** — concrete signal for re-decision
- **Revisit date** — when to check against reality

Optional but recommended:
- **Emotional state** — anxious / clear / pressured / aligned (logging surfaces patterns)
- **Related decisions** — wiki-links to other decisions/projects/people
- **People involved** — wiki-links to `people/[name].md`

---

## Step 3: Set the revisit date intelligently

Don't default to 30 days. Calibrate:

| Decision type | Default revisit |
|---------------|-----------------|
| Hire / firing | 90 days |
| Grant submission | 30 days post-decision date |
| Role change / commitment | 90 days |
| Tool / infra / repo choice | 60 days |
| Strategic positioning | 30 days |
| Quick reversible call | 14 days |

Ask to override if instinct differs.

---

## Step 4: Push back

Before writing, do ONE round of critical-partner challenge:

- If confidence ≥ 8: "What's the strongest argument against this?"
- If alternatives are weak (e.g., "I could not do it" as the only alt): "What's the strongest *positive* alternative — what else could you spend this time/money/attention on?"
- If emotional state is anxious/pressured: "Are you deciding from the right state? Want to wait 24 hours?"
- If revisit date > 6 months: "That's a long time to wait. What earlier signal would justify revisiting?"

Only push where the answer matters. Don't make it performative.

---

## Step 5: Write the file

Path: `<VAULT_ROOT>/decisions/YYYY-MM-DD-{slug}.md`

Use `<VAULT_ROOT>/templates/decision.md` as the structure.

---

## Step 6: Cross-link

After writing:
- Mention in today's journal log: `- HH:MM — Captured decision: [[YYYY-MM-DD-slug]]`
- If decision involves a project, add a link in that project's file
- If decision involves people, add backlinks in their person files

Confirm each cross-link before writing.

---

## End state

- A new file in `decisions/`
- A backlink in today's journal
- Optional cross-links to related files
- Clear revisit date and "what would change my mind" criteria
