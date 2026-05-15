# Restructure team's weekly meeting cadence

---
**Status:** Open
**Opened:** 2026-05-12
**Closed:**
**Decision:** Collapse the four standing team meetings (Mon standup, Wed planning, Thu sync, Fri retro) into two: a 30-min Tuesday "what's blocked" sync and a 45-min Thursday "what's next" planning. Standups go async in Slack. Retros move to bi-weekly.
**Confidence:** 6/10
**Review Date:** 2026-08-12
**Emotional State:** clear, slightly pressured by the survey results
---

## Context

The Q1 engineering survey flagged "too many meetings" as the top friction item — 5 of 6 team members called it out. Current standing meetings consume ~3.5 hours/week of every IC's time. Two of them (Thu sync, Fri retro) have visibly low signal — most weeks they end early or devolve into status reads. [[sally-sanders]] and [[chris-brown]] have separately suggested cuts. [[bob-jones]] has not, and prefers structure.

## Decision

- **Keep:** Tuesday 30-min "what's blocked" sync (replaces Mon standup + Thu sync)
- **Keep:** Thursday 45-min "what's next" planning (replaces Wed planning)
- **Drop:** Daily standup → async Slack thread in `#platform-standup` by 10:30 local
- **Move:** Fri retro → bi-weekly (every other Friday), 45 min, with explicit agenda template
- **Trial period:** 4 weeks (2026-05-18 through 2026-06-12), then decide formally
- **Exit criterion:** If the next survey or 1:1 round shows the team feels less informed or more siloed, revert.

## Alternatives considered

| Alternative | Why rejected |
|-------------|--------------|
| Keep all four meetings, shorten each | The signal-to-noise problem isn't duration; it's redundancy. Two of the four cover the same ground. |
| Go fully async (no standing meetings) | Loses the small amount of real-time decision-making that happens in the Thu sync. Team is mid-migration; we need at least one synchronous check per week. |
| Cut only the Fri retro | Easy win, but doesn't address the actual top complaint (daily standup). |
| Punt to Q3 with the survey results | Survey is 4 months old. Continued delay reads as ignoring it. |

## Prediction

- **30 days:** Trial in week 4. Async standup adoption is uneven — 3-4 people post daily, 2 post sometimes. The Tuesday sync is the most-attended meeting on the team's calendar. Bi-weekly retro feels right.
- **90 days:** Async standup either stabilized as the norm or quietly reverted (~50/50). Tuesday and Thursday meetings are the canonical team rituals. One adjacent team has copied the structure.
- **365 days:** Either this is "how Pat's team runs" or one specific failure mode (likely: async standup not catching real blockers) drove a partial revert. The Fri retro stays bi-weekly regardless.

## Key factors

- Survey signal is unambiguous; deferring further damages trust.
- Team is mid-migration on [[platform-migration]] phase 2 — too much process change at once is risky.
- [[bob-jones]] is the highest-friction person on this change; his concerns need to be heard before, not after.
- [[mary-johnson]] is new (started 2026-05-04); needs visibility into how the team operates, which fewer meetings reduces.

## Worst case

The async standup fails — real blockers go unsurfaced for 2-3 days at a time, and we lose a minor incident's worth of trust before noticing. The team feels less connected; [[mary-johnson]] doesn't onboard as well as she would have with daily synchronous touchpoints. Recovery cost: revert to daily standup, ~1 week to restore the old rhythm. Acceptable.

## What would change my mind

- If 3+ team members in 1:1s next week say "actually I want to keep the daily standup" — abort before changing anything.
- If the next [[postmortem-may-incident]]-style event happens during the trial and traces to a missed standup signal — revert before the 4-week deadline.
- If [[mary-johnson]]'s onboarding visibly suffers in week 2-3 of the trial.

## Related

- [[meeting-restructure]] — the project tracking the proposal, trial, and survey follow-up
- [[note-async-standup-tradeoffs]] — atomic note on the pattern from previous teams
- [[bob-jones]] — most likely to push back; steel-man his view before the Wed proposal
- [[q3-roadmap]] — meeting cadence affects the roadmap planning rhythm

## Revisit log

<!-- /decide-revisit will append here on or after 2026-08-12 -->
