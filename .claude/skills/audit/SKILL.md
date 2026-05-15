---
name: audit
description: "Vault hygiene meta-skill. Scans <VAULT_ROOT>/ for decay: stale goals.md, dormant now.md, projects with no recent activity, broken wiki-links, orphan notes, decisions without revisit dates, stale people records, zombie inbox items. Outputs a vault health score, top fixes, and offers low-risk auto-fixes with confirmation. Use when user says 'audit', '/audit', 'lint the vault', or monthly on the 1st."
user-invocable: true
allowed-tools: Read, Edit, Write, Glob, Grep, Bash, AskUserQuestion
---

# Vault Audit

A forensic health check on the vault at `<VAULT_ROOT>`. Detect decay before it bites. Specific, evidence-based, ranked. Do not preach.

**Tone:** Forensic, not nagging. "Your system is decaying in these specific ways." Cite files, dates, counts. Push back if real signal gets dismissed as noise.

---

## Step 1: Run checks in parallel

Use Bash + Read + Glob to collect signals at once.

### Staleness checks:
```bash
stat -f "%Sm %N" -t "%Y-%m-%d" <VAULT_ROOT>/plan.md
stat -f "%Sm %N" -t "%Y-%m-%d" <VAULT_ROOT>/journal/$(date +%Y)/goals.md
stat -f "%Sm %N" -t "%Y-%m-%d" <VAULT_ROOT>/now.md
stat -f "%Sm %N" -t "%Y-%m-%d" <VAULT_ROOT>/values.md
```

Thresholds:
- `plan.md` > 365 days → flag
- `goals.md` > 60 days → flag (warning at 30)
- `now.md` > 14 days → flag (warning at 10)
- `values.md` > 730 days → soft flag

### Project activity:
For each project in `now.md` Active table, find last journal mention:
```bash
grep -rl "project-name" <VAULT_ROOT>/journal/$(date +%Y)/ | head
```
No mention in 14+ days → drift candidate.

### Open decisions:
```
Glob: <VAULT_ROOT>/decisions/*.md
```
For each: read frontmatter. Flag:
- `Status: Open` with no `Review Date` → missing revisit
- `Status: Open` with `Review Date` < today → overdue
- Modified < 7 days ago with no status update → in-progress, skip

### Inbox staleness:
Read `inbox.md`. Flag candidates:
- Date references that have passed
- "Waiting on" items where the person has appeared as "delivered" in completed.md
- OVERDUE markers

### Wiki-link health:
```bash
grep -rohE '\[\[([^]]+)\]\]' <VAULT_ROOT>/{notes,research,decisions,journal,people}/ 2>/dev/null | sort -u
```
For each unique `[[X]]`, check whether `X.md` exists in `notes/`, `research/`, `decisions/`, `people/`, `wiki/*/entities/`, `wiki/*/concepts/`, `wiki/*/sources/`, `journal/`, `reference/`.

Report broken links — but treat as low-severity unless count is large (per CLAUDE.md: unresolved `[[name]]` is "something worth writing later, not an error").

### Orphan notes:
```
Glob: <VAULT_ROOT>/notes/*.md
```
For each `foo.md`, search for `[[foo]]` in the rest of the vault. Zero hits → orphan candidate. Only flag if > 90 days old AND zero inbound links.

### People record activity:
```
Glob: <VAULT_ROOT>/people/*.md
```
No interaction in 6+ months → ask if move to `people/archive/`. Don't move automatically.

### Completed.md strategic context:
Read top 30 entries. Flag entries lacking parenthetical "Impact: ..." — useless for annual review.

### Wiki health (if `wiki/` exists):
For each wiki domain, check `log.md` last entry. If > 30 days → stalled.

---

## Step 2: Score (0-100)

| Check | Weight | Pass criteria |
|-------|--------|---------------|
| plan.md fresh | 5 | ≤ 365 days |
| goals.md fresh | 15 | ≤ 60 days |
| now.md fresh | 10 | ≤ 14 days |
| All active projects mentioned this month | 15 | 100% |
| Decisions have revisit dates | 10 | ≥ 80% |
| Inbox stale items | 10 | ≤ 5 candidates |
| Wiki-link health | 5 | broken < 5% |
| Orphan notes | 5 | < 10 old orphans |
| People records active | 5 | < 10 stale |
| completed.md has strategic context | 10 | ≥ 80% recent entries |
| Wiki domains active (if exists) | 10 | log within 30 days |

Report the score and breakdown.

---

## Step 3: Top 5 fixes this week

Rank findings by **leverage** (impact) × **ease** (speed to fix). Prefer:
- 1 stale `goals.md` (high leverage) over 50 broken wiki-links (tedious)
- 3 zombie projects in `now.md` over 12 orphan notes

```
## Top 5 fixes this week

1. **[High]** goals.md is N days stale — block 60 min this weekend
2. **[High]** Three projects on Active not mentioned in 14+ days — demote or commit
3. **[Medium]** N inbox items past deadline — confirm closeout
4. **[Medium]** N decisions without revisit dates — add via /decide-revisit
5. **[Low]** N broken wiki-links — batch fix when convenient
```

---

## Step 4: Offer low-risk auto-fixes

Only for mechanical fixes. Always confirm in batches.

Safe:
- Add `Tags:` field to people records missing it
- Append `Last reviewed: YYYY-MM-DD` to decision files reviewed today
- Move people records with no 6-month activity to `people/archive/`

**Never auto-fix:**
- goals.md content
- now.md content beyond date stamp
- decision status fields
- inbox.md items

---

## Step 5: Write `research/vault-audits/YYYY-MM-DD-audit.md`

```markdown
# Vault Audit — YYYY-MM-DD

**Score:** XX/100 (prior: YY/100, delta: ±Z)

## Breakdown
{{rubric table}}

## Top 5 fixes
{{ranked list}}

## Auto-fixes applied
{{what got fixed with confirmation; empty if none}}

## Trend signals
{{anything flagged in multiple consecutive audits — structural issue, not one-off}}
```

Create `research/vault-audits/` if needed.

---

## Step 6: Force ONE follow-up

Pick the single most consequential finding. Examples:
- "goals.md stale 47 days and flagged in last audit. Schedule rewrite on which date?"
- "now.md untouched since /weekly-review on YYYY-MM-DD. Is this experiment failing?"
- "Five decisions have no revisit date. Backfill now or wait for next /decide-revisit?"

---

## What to NOT do

- Don't try to fix everything in one session.
- Don't soften findings due to diary stress.
- Don't moralize ("you should...") — describe what is.
- Don't repeat last audit's findings verbatim — surface as *trends*.

---

## End state

- Score + breakdown
- Ranked top-5 fixes
- (Optionally) safe auto-fixes applied
- Audit file in `research/vault-audits/`
- One forcing-decision asked + answered
