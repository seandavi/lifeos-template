# 0001. Structured Progress Tracking

- **Status:** Accepted
- **Date:** 2026-08-02
- **Deciders:** seandavi, lwaldron

## Context and Problem Statement

LifeOS captures work in journal entries and `completed.md`, but there was no structured way to query progress across projects, people, and time. As a result, reconstructing activities for grant progress reports (RPPRs), effort accounting, and annual performance reviews was manual and error-prone. We needed a low-friction way to track effort in hours, divide time across multiple projects, and record zero-effort milestones without introducing heavy forms or external time-tracking dependencies.

## Decision

We will use the **daily journal as the single source of truth** for progress tracking, utilizing a capture convention and query-time parsing rather than maintaining a parallel database.

1. **Log Line Conventions**: 
   - Users optionally add a project wiki-link and a duration to a log line: `- 14:30 Worked on SOW draft [[u24ca289073]] 2.5h`.
   - **Milestones**: A line with a project link but no duration counts as a 0-effort milestone (e.g. publishing a paper).
   - **Splits**: Effort can be split across multiple projects evenly (`3h split`) or weighted (`3h (2/1)`).
   - **Privacy**: Lines containing `%private` are excluded from exported reports.
2. **Project Frontmatter**: Added `grant_id` to the frontmatter of `templates/project.md` so that effort can be grouped at the grant level rather than just the project level.
3. **Query-Time Parsing**: A new `scripts/progress-report.py` parses `journal/` and `completed.md` for project links, durations, and splits. The `/progress-report` skill invokes this script to generate a copy-pasteable Markdown report.
4. **Opt-in Storage**: A new `# Preferences` section in `CLAUDE.md` tracks whether effort tracking is enabled (`Track effort by project`), allowing the `/end-of-day` skill to prompt for missing durations only if desired.

## Alternatives Considered

- **Parallel Activity Database**: We considered storing atomic activity records in a dedicated database or append-only log file. This was rejected because it violates LifeOS's ethos of using plain markdown text, and would create a dual source of truth alongside the journal.
- **Third-Party Time Trackers / Git Integrations**: Integrating with external tools or analyzing git logs. This was rejected for the v1 implementation to prioritize capturing what is already written manually in the daily journal. External connectors may be added in the future.

## Consequences

- **Easier Reporting**: Effort percentages and milestones can now be easily aggregated for grants and performance reviews.
- **Low Friction**: Users can keep writing their daily journal normally, with only minor tagging required.
- **Complexity in Parsing**: Because the journal remains free-text, the progress tracking relies on relatively complex regular expressions to identify links, durations, and splits, which may require ongoing maintenance as users find new ways to format their logs.
