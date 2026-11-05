# 0004. Centralized Vault Configuration and Self-Identity

- **Status:** Accepted
- **Date:** 2026-08-20
- **Deciders:** lwaldron

## Context and Problem Statement

As LifeOS grows to include automated ingestion pipelines across email (`scan_emails.py`), calendar/meetings (`export-calendar-ics.py`, `meeting-ingest.py`), and progress reporting (`progress-report.py`, `github-activity-sync.py`), multiple subsystems need to know the identity of the vault owner.

Previously, owner-specific identifiers (e.g., `SELF_SLUG = "levi-waldron"`, email addresses, GitHub usernames) were either hardcoded inside individual Python scripts or inferred ad-hoc. This created maintenance friction, potential attribution errors, and prevented simple portability or vault initialization for other users.

## Decision

We will establish a single, central configuration file at the vault root: **`config.yaml`**.

### Configuration Schema:
```yaml
owner:
  name: "Levi Waldron"
  slug: "levi-waldron"
  email: "Levi.Waldron@sph.cuny.edu"
  email_alt:
    - "levi.waldron@sph.cuny.edu"
    - "levi.waldron@microbiome-vif.org"
    - "lwaldron.research@gmail.com"
  github: "lwaldron"

vault:
  name: "LifeOS"
  timezone: "Europe/Rome"
  lookback_days: 14
```

1. **Unified Schema:** Uses `email_alt` (matching the frontmatter property in `people/*.md`) for all alternate email aliases.
2. **Ingestion Contract:** All automated pipelines and Python scripts must load owner identity (`slug`, `name`, `email`, `email_alt`, `github`) and vault settings dynamically from `config.yaml`, providing graceful fallbacks if the file is absent.
3. **Primary Dossier Separation:** The owner's Markdown file (`people/[owner.slug].md`) remains the human-facing knowledge dossier, while `config.yaml` serves as the machine-readable runtime configuration.

## Alternatives Considered

- **Hardcoded constants in scripts:** Rejected due to scattering of identity data and high maintenance friction when aliases change.
- **Frontmatter flag in `people/` (`is_self: true`):** Rejected because discovering identity would require parsing and indexing all people files on every script invocation.
- **Environment variables only (`LIFEOS_OWNER_SLUG`):** Kept as a fallback mechanism, but rejected as primary storage since configuration should be version-controlled with the vault.

## Consequences

- **Easier Configuration:** Aliases, owner identity, and timezone are managed in one file and immediately reflected across all pipelines.
- **Portability:** Setting up a new vault or running `/init` only requires editing `config.yaml`.
- **Dependencies:** Scripts reading YAML use standard library or `pyyaml` with fallback parsing.
