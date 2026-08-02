# 0002. GitHub Activity Connector

- **Status:** Accepted
- **Date:** 2026-08-02
- **Deciders:** seandavi, lwaldron

## Context and Problem Statement

A large portion of the user's actual work occurs in code repositories, but none of this activity flows into the progress tracking system automatically. Manually logging commits and Pull Requests (PRs) is tedious and error-prone, leading to incomplete activity timelines and effort reports. We need a way to automatically ingest GitHub and git work into the project's activity timeline without requiring manual data entry, while correctly attributing the work to the appropriate projects.

## Decision

We will implement a GitHub Activity Connector as a standalone ingestion script (`scripts/github-activity-sync.py`) with the following key design decisions:

1. **Topic-Based Repository Mapping:** Repositories are mapped to lifeos projects primarily via GitHub topics (e.g., a repository with topic `u24ca289073` maps to the project with `grant_id: u24ca289073`). Explicit repository configuration with a `project` override acts as a fallback and takes precedence over topics.
2. **Configurable Author Filtering:** By default, only commits, PRs, and PR Reviews authored by the user are ingested. The script gracefully handles null user fields (from deleted accounts). This filtering is configurable per-repository to allow tracking team-wide activity for projects where the user acts as a PI.
3. **Zero-Duration Markers & Duration Escaping:** Commits and PRs are ingested as zero-effort markers (e.g., `0h`). Furthermore, bare duration strings in commit messages (e.g., "increase TTL to 24h") are sanitized to prevent false progress logging on automated runs.
4. **Deduplication Strategy:** The script uses detailed internal markers (including repository names and specific PR/Review IDs) to prevent duplication on successive runs. Potential cross-source duplicates (where the script overlaps with a manually entered log) are flagged with an HTML comment (`<!-- CONFIRM DUPLICATE? -->`) for manual reconciliation during the weekly review.
5. **Comprehensive Remote API Integration:** The connector uses the `gh` CLI to interact with the GitHub API. It enumerates all repository branches to guarantee that work on non-default branches is ingested, and utilizes a configurable `timezone` key (`zoneinfo`) to guarantee deterministic date resolution for the user's local timezone.
6. **Unattributable Activity Handling:** Any discovered repository that cannot be confidently mapped to a specific project is flagged and appended to an `unattributable.md` file for manual review, rather than being silently dropped or incorrectly inferred.
7. **Automation via Agent Skills:** The synchronization script is triggered automatically during the established weekly review cadence (via `.claude/skills/weekly-review/SKILL.md`) to respect API rate limits and avoid background daemon processes.

## Alternatives Considered

- **Local `.git` repository scanning:** Scanning local `.git` clones would save API calls and work offline, but it risks missing activity performed on other machines or the web UI, and relies on the user keeping local clones up-to-date. We opted for the GitHub API for consistency and completeness.
- **Manual Logging:** Maintaining the status quo of manually logging commits. This was rejected because it is tedious and unsustainable.
- **Background Daemon:** Running a background service to constantly poll GitHub. This was rejected in favor of triggering the sync during the existing weekly review ritual to keep the system simple and avoid background resource consumption.
- **Separate Python Package:** Extracting the sync script into a separate, installable Python package with its own test suite. This was rejected to avoid over-engineering the solution for now and to leave the scope of LifeOS flexible, relying on PR descriptions and documentation for future maintainability.
- **PyGitHub Dependency:** Using the `PyGitHub` library instead of `gh` CLI. This was rejected to adhere to a "zero-dependency philosophy," preferring the standard library and the already-required `gh` CLI over adding external python dependencies.

## Consequences

- **Easier:** The user's GitHub activity is now automatically aggregated and attributed to the correct projects, creating a comprehensive activity timeline with zero manual overhead.
- **Risks Introduced:** The system depends on the user maintaining consistent GitHub topics across their repositories. Irrelevant forks could be pulled in if they share the same topic, though this is mitigated by author filtering and the `unattributable.md` review process.
- **Dependencies:** The connector requires the `gh` CLI to be installed and authenticated on the system where the script runs.
