# 0005. Vault-Relative Paths and Non-Destructive Initialization

- **Status:** Accepted
- **Date:** 2026-08-26
- **Deciders:** lwaldron

## Context and Problem Statement

[ADR 0004 (Centralized Vault Configuration and Self-Identity)](0004-vault-configuration-and-identity.md) established `config.yaml` to manage owner identity and self-attribution across ingestion pipelines. However, path handling across the rest of the vault still suffered from two structural issues:

1. **Placeholder Tokens & Destructive Init:** Upstream `lifeos-template` used `<VAULT_ROOT>` string placeholders across all skills and documentation. On initial vault setup, `/init` performed a global find-and-replace across every `.md` and `.sh` file. This produced:
   - A massive dirty git diff on day one.
   - Persistent merge conflicts whenever pulling upstream updates to skills or scripts.
2. **Scattered External Integration Paths:** Paths to cloud-synced reference materials (OneDrive documents, spreadsheets, Dropbox archive folders) were hardcoded inside standalone Python scripts rather than managed in configuration.

## Decision

We establish **vault-relative paths** as the universal standard for all skills and agent instructions, extend **`config.yaml`** with an `external:` block for external integration paths, and refactor `/init` into a non-destructive setup workflow.

### 1. Vault-Relative Paths in Skills & Documentation
Modern AI coding assistants (Claude Code, Antigravity) execute tools relative to the active workspace root by default. All skill files (`.claude/skills/*`), documentation (`CLAUDE.md`, `README.md`), and prompts must reference relative paths (`inbox.md`, `calendar/this-week.md`, `scripts/run_hooks.py`, `notes/`) without leading slashes or `<VAULT_ROOT>` placeholders.

### 2. Dynamic Vault Resolution in Helper Scripts
All Python and shell scripts resolve the vault root dynamically relative to their location:
- **Python:** `VAULT_ROOT = Path(__file__).resolve().parent.parent`
- **Shell:** `VAULT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"`
- Environment variable `$LIFEOS_HOME` remains available as an optional override.

### 3. Extending `config.yaml` with `external:`
Building on ADR 0004, `config.yaml` is extended with an `external:` mapping for external cloud storage dependencies:

```yaml
external:
  onedrive_handbook: "~/Library/CloudStorage/OneDrive-CUNY/.../EPID-BIOS Faculty handbook.docx"
  onedrive_course_planning: "~/Library/CloudStorage/OneDrive-CUNY/.../EPIBIOS course planning spreadsheet.xlsx"
  archives_context: "~/Health Dropbox/Levi Waldron/SPH archives/AI helper context folder"
```

Scripts that sync external materials read these keys dynamically and expand user home (`~`) paths.

### 4. Non-Destructive `/init` Routine
The `/init` skill writes/updates `config.yaml` and seeds core strategy documents (`plan.md`, `values.md`). It never performs text replacement on skill files or core system templates.

## Alternatives Considered

- **Global String Substitution on Init:** Rejected. Rewriting skill files creates unnecessary churn and breaks clean git tracking against upstream.
- **Environment Variables for External Paths:** Rejected. Cloud paths should be declared in a version-controlled config file rather than requiring complex shell profile setups across varied execution environments.

## Consequences

- **Zero Dirty Diff on Clone:** Freshly initialized vaults remain cleanly aligned with upstream `lifeos-template`.
- **Seamless Upstream Pulls:** Downstream vaults can pull improvements to skills, templates, and scripts with zero merge conflicts on path strings.
- **Centralized Integration Points:** All local and cloud paths are managed in `config.yaml`.
