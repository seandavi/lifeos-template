# Restructure team's weekly meeting cadence

*This file is the same prospective decision from [`decision-prospective.md`](decision-prospective.md), three months later, with the revisit block appended by `/decide-revisit`. The revisit log is what makes the system honest — without it, you remember your good calls and forget the bad ones.*

---
**Status:** Decided
**Opened:** 2026-05-12
**Closed:** 2026-05-18 (trial began)
**Decision:** Collapse the four standing team meetings (Mon standup, Wed planning, Thu sync, Fri retro) into two: a 30-min Tuesday "what's blocked" sync and a 45-min Thursday "what's next" planning. Standups go async in Slack. Retros move to bi-weekly.
**Confidence:** 6/10
**Review Date:** 2026-08-12
**Emotional State:** clear, slightly pressured by the survey results
---

## Prediction

- **30 days:** Trial in week 4. Async standup adoption is uneven — 3-4 people post daily, 2 post sometimes. The Tuesday sync is the most-attended meeting on the team's calendar. Bi-weekly retro feels right.
- **90 days:** Async standup either stabilized as the norm or quietly reverted (~50/50). Tuesday and Thursday meetings are the canonical team rituals. One adjacent team has copied the structure.
- **365 days:** Either this is "how Pat's team runs" or one specific failure mode (likely: async standup not catching real blockers) drove a partial revert. The Fri retro stays bi-weekly regardless.

*(other prospective sections elided for brevity — see prospective file)*

## Revisit log

### 2026-08-12 — Revisit (90-day, scheduled)

**Outcome:** Right on the main call, wrong on the async standup specifics.

**Prediction vs reality:**
- *30-day:* Predicted "uneven async adoption, 3-4 post daily, 2 sometimes." Reality: by week 3, only 2 of 6 were posting daily; the rest posted 1-2 times per week or skipped. Tuesday sync attendance was 100% — predicted correctly. **Calibration: I underestimated how much active norm-setting async culture needs.**
- *90-day:* Predicted "50/50 on async standup, bi-weekly retro feels right, one adjacent team copies." Reality: async standup was quietly modified at week 5 — [[sally-sanders]] proposed a Monday-only async post (instead of daily), team unanimously agreed. Tuesday + Thursday meetings are now the canonical rhythm. [[jane-doe]]'s team copied the structure 2026-07-01. Bi-weekly retro held; nobody asked for weekly back. **Net: outcome better than predicted on the meetings overall, worse on the async standup specifically.**
- *365-day:* Too early.

**Lesson:** Async standup ≠ "everyone posts whenever, no structure." Without a specific cadence and a specific channel norm, it decays toward silence. Next time, I'd start with Monday-only async (not daily) and explicitly say "if you don't post, we assume you're heads-down — no judgment, but you carry the comms cost if something breaks." That framing matches what we ended up at without the 5 weeks of drift.

The bigger meta-lesson: the team converged on a better answer than mine within 5 weeks of being given room to. That's a stronger argument for "trial it and let the team adjust" than my original framing of "I'll decide and we'll review at 4 weeks."

**Status update:** Tuesday 30-min sync, Thursday 45-min planning, Monday async standup, bi-weekly Friday retro. Stable since 2026-06-22. Next survey shows meeting-fatigue dropped from #1 to #6 complaint. [[bob-jones]]'s feared pushback never fully materialized — his actual concern was knowing what others were working on, which the Tuesday sync covers fine.

**Decision quality:** *Right decision, slightly wrong specifics.* The choice to collapse the four meetings was correct and the structural specifics (2 sync, 1 async, bi-weekly retro) held up. The execution of the async standup needed more scaffolding upfront. Filed as [[note-async-rituals-need-explicit-norms]] for future me.

---

### 2027-05-12 — Revisit (365-day, scheduled)

*(future entry — will be appended automatically when review date passes)*
