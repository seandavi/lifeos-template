---
name: orient
description: "A 5-minute guided tour of the LifeOS vault. Walks the user through the 5-layer architecture (Foundation, Knowledge, Connections, Execution, Feedback), names the files and skills in each layer, and shows what to do tomorrow morning to start the daily rhythm. Use when user says 'orient', '/orient', 'tour', 'how does this work', or '/init' just finished."
user-invocable: true
allowed-tools: Read, AskUserQuestion
---

# Orient — a guided tour of the system

You are showing the user around their newly-personalized LifeOS vault. Goal: in 5 minutes, give them a working mental model of the 5 layers, name the files and skills, and point them at the right next action.

**Tone:** Concise. Concrete. A real tour, not a sales pitch. End with "go run /morning tomorrow."

---

## Step 1: One-line orientation

Open with:

> The vault is organized into 5 layers. Each layer has files and skills. The whole thing is self-correcting if you let the feedback layer do its job.

---

## Step 2: Walk the 5 layers (one short paragraph each)

### Layer 1 — Foundation: who you are, where you're going
Files: `plan.md` (10-year vision), `values.md` (principles), `goals.md` (annual), `now.md` (current state), `CLAUDE.md` (operating manifest).

This is the *identity* layer. `plan.md` updates slowly. `goals.md` updates quarterly. `now.md` updates weekly. `CLAUDE.md` is read by Claude Code every time it operates in this vault.

### Layer 2 — Knowledge: what you know
Directories: `notes/` (atomic slipbox), `research/` (longer docs), `decisions/` (records), `people/` (relationships), `projects/` (per-project details), `wiki/` (structured domain wikis), `raw/` (source material for ingest).

Cross-references everywhere via `[[wiki-links]]`. The templates in `templates/` define the file shapes.

### Layer 3 — Connections: external state
Scripts: `calendar/export-calendar.sh` (calendar → markdown), `scripts/email-scan.sh` (email → digest), `scripts/meeting-ingest.py` (calendar → meeting notes).

These bring outside-world state into the vault so the skills can reason about it.

### Layer 4 — Execution: rituals that run on a cadence
Skills:
- `/morning` — daily AM (11-step routine)
- `/end-of-day` — daily PM (close the loop)
- `/weekly-review` — Fridays (update now.md, draft week-WW.md)
- `/meeting-prep` — nightly (briefs for tomorrow)
- `/decide` — on-demand (capture decisions prospectively)

### Layer 5 — Feedback: the layer that prevents rot
Skills:
- `/audit` — monthly (vault hygiene; flags decay)
- `/decide-revisit` — monthly (compare predictions to reality)
- `/quarterly-review` — quarterly (heavy strategic review; rewrite goals.md)

Most public Claude Code vaults skip this layer entirely. They look great at launch and rot within 2-3 months. The feedback layer is what makes the system self-correcting.

---

## Step 3: The forcing question

> "Of these 5 layers, which one feels least obvious to you?"

(Use AskUserQuestion.)

Spend 2-3 extra sentences on whichever layer they pick. Don't lecture — explain via a concrete example.

---

## Step 4: Hand off

> ```
> Three things to do next:
>
> 1. Tomorrow morning, type `/morning`. The first run will feel awkward;
>    by day 3 it'll feel essential.
>
> 2. This Friday, run `/weekly-review`. Even if the week was light, the
>    cadence is the point.
>
> 3. End of next month, run `/audit`. Catch the early drift before it
>    compounds.
>
> Everything else is on-demand.
> ```

Point them at the README for deeper reading.

---

## What to NOT do

- Don't pitch. The user already cloned the repo.
- Don't recite the README. This is a *tour*, not a re-read.
- Don't open a long Q&A. Two questions max. The vault rewards use, not study.
- Don't ask if they want to set anything up — `/init` already ran (or should have).
