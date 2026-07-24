# Obsidian dashboard layer (optional)

LifeOS is plain markdown first — it works with any editor and any coding agent. This optional layer adds **dashboards, indexes, and task views** for people who use [Obsidian](https://obsidian.md). If you don't use Obsidian, ignore this entirely; nothing else depends on it.

## What you get

- **`dashboards/*.base`** — native Obsidian **Bases** (tables/cards over your notes): active projects, a people directory, a budget pipeline, and an output pipeline. Edit a note's frontmatter and the dashboards follow automatically.
- **`dashboards/Home.md`** — a command-center note that embeds the above.
- **`dashboards/tasks-dashboard.md`** — open `- [ ]` items across `inbox` + `journal`, via the **Tasks** community plugin.
- **`reference/frontmatter-spec.yaml` + `scripts/vault_lint.py`** — a tiny, dependency-light validator that checks note frontmatter against a spec you control (report-only; run with `uv run scripts/vault_lint.py`).

Everything **fails gracefully**: without Bases, `.base` files simply don't render; without Tasks, the query blocks show as harmless code. Your notes stay readable either way.

## Requirements

- **Obsidian 1.9+** (Bases is a built-in core plugin from 1.9 on).
- Optional: [`uv`](https://docs.astral.sh/uv/) to run the frontmatter linter.
- Optional: the [`obsidian` CLI](https://github.com/) so a coding agent can query your Bases headlessly (`obsidian base:query path="dashboards/projects.base" view="Active"`).

## One-time setup

**Scripted (recommended):**

```bash
bash scripts/setup-obsidian.sh
```

This installs the Tasks plugin and enables Bases for the vault. Then, in Obsidian:

1. **Settings → Community plugins → "Turn on community plugins"** (off by default in a fresh vault; accept the dialog).
2. **Reload Obsidian** (Cmd/Ctrl-R or restart) so it scans the new plugin, then enable **Tasks**.

**Manual:** enable Bases under Settings → Core plugins, install "Tasks" from Settings → Community plugins → Browse, and open `dashboards/Home.md`.

## People notes need frontmatter

The people dashboard (`dashboards/people.base`) indexes YAML frontmatter, so `templates/person.md` puts `role` / `organization` / `tags` / `domains` in the frontmatter block. If you have older person notes with those fields as `**bold-key**` lines in the body, move them into frontmatter (or they simply won't appear in the dashboard — no error, just absent).

## Keeping it honest

Bases views are only as fresh as your frontmatter. Two habits keep them from lying:

- Run `uv run scripts/vault_lint.py` periodically — it flags missing required fields, bad enum values, and **Active projects whose `updated` date has gone stale**.
- Reconcile flagged projects against `now.md` during your weekly/quarterly review.
