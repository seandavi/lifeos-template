---
name: obsidian-cli
description: "Playbook for operating this Obsidian vault via the `obsidian` CLI when it's installed — link resolution, graph hygiene (backlinks / orphans / unresolved), task reconciliation across files, frontmatter/tag/property queries, full-text search, version history. Use when doing substantial work over the vault's link graph, tasks, or frontmatter AND `obsidian` is on PATH. Describes the filesystem fallback for when it isn't. Also /obsidian-cli."
user-invocable: true
allowed-tools: Bash, Read, Edit, Grep, Glob
---

# Operating the vault via the `obsidian` CLI

The `obsidian` CLI talks to the **running Obsidian app** and exposes its *parsed*
model — the resolved link graph, tasks with status chars, frontmatter properties,
tags, bases — not just bytes on disk. That makes graph/task/property work a query
instead of a Grep-and-guess. This skill is the playbook for using it well.

**This integration is optional.** LifeOS does not require Obsidian. If you don't
use Obsidian (or don't have the CLI), every workflow in this vault still works —
this skill simply never activates. Nothing needs to be configured or disabled.

## 0. Preconditions — check before relying on it

```bash
command -v obsidian        # is the CLI installed?
obsidian vault info=name   # is the app running + a vault open? (errors/hangs if not)
```

- **If the CLI is absent or the app is closed → fall back to the filesystem**
  (Glob/Grep/Read), exactly as `CLAUDE.md`'s Wiki-Links fallback describes. Every
  query below has a filesystem equivalent; the CLI is faster and exact, not
  required. Don't block work waiting on it.
- Target a specific vault with `vault=<name>` if more than one is open.

## 1. The golden boundary

**Query and navigate with the CLI. Change prose with `Edit`.** The CLI's write
verbs (`append`, `prepend`, `create`, `property:set`) are coarse — good for
appending a log line or setting one frontmatter key, wrong for surgical
multi-line edits.

**Live-app verbs are opt-in only.** `eval`, `command`, `open`, `daily`, `tabs`,
`theme`, `dev:*`, `restart` mutate the user's *running* session (pop tabs open,
run JS in-app, change the UI). Use them **only when the user explicitly asks you
to drive the UI.** Never as a side effect of a lookup.

**Git is the version-control truth, not Obsidian Sync.** `history` / `diff` /
`sync:restore` are a handy second safety net, but recovery and commits go through
git (see `CLAUDE.md`'s Git Workflow section). Don't conflate them.

## 2. Link resolution & graph hygiene

```bash
obsidian read file="some-name"          # resolve [[some-name]] by name, read it
obsidian backlinks file="X" counts      # what links TO X (before editing/renaming X)
obsidian links file="X"                 # what X links to
obsidian unresolved verbose             # [[stubs]] not yet written — the "worth writing" marks
obsidian orphans                        # notes nothing links to
obsidian deadends                       # notes with no outgoing links
```

- **Before renaming/moving a note**, run `backlinks` first so you know what breaks.
  `obsidian rename` / `obsidian move` update the file; verify links after.
- `unresolved` is the backlog of intentional `[[future-note]]` stubs — a to-write
  list, not errors.
- `orphans` counts can be inflated by auto-generated or imported stubs; scan the
  list before treating the raw number as a problem.

## 3. Tasks — first-class across the whole vault

```bash
obsidian tasks todo verbose             # every open "- [ ]" with path:line
obsidian tasks done                     # completed
obsidian tasks path="inbox.md" todo     # scope to a file
obsidian task ref="inbox.md:42" done    # mark one done (or toggle / status="x")
```

Use for the **task-management protocol** in `CLAUDE.md`: reconcile the same item's
checkbox across `inbox.md`, the day's journal, and `now.md` instead of eyeballing.
Still complete tasks in the three-step order (inbox → `completed.md` → journal) —
the CLI toggles boxes, it doesn't do the `completed.md` write with strategic
context.

## 4. Frontmatter, tags, properties

```bash
obsidian tags counts sort=count                 # tag frequency across the vault
obsidian tag name="research" verbose            # files carrying a tag
obsidian properties file="people/jane-smith.md" # frontmatter of one file
obsidian property:read name="status" file="…"   # one property value
obsidian property:set name="status" value="active" type="text" file="…"  # clean write, no YAML hand-edit
```

Prefer `property:set` over hand-editing YAML frontmatter — it won't corrupt the
block. For anything below the frontmatter, use `Edit`.

## 5. Search, history, bases

```bash
obsidian search:context query="some-topic" path="notes"   # matches WITH line context
obsidian history file="X"      # local version list   ·   obsidian diff file="X" from=2 to=1
obsidian bases                 # Obsidian DB-view files, if the vault has any
obsidian base:query file="…" view="…" format=json         # query a base as structured data
```

If the vault has a base, `base:query` turns it into a JSON/CSV data source — the
vault's own lightweight database. If not, `bases` returns empty; that's fine.

## 6. Worked patterns

- **Vault audit** (feeds `/audit`): `unresolved`, `orphans`, `deadends`,
  `tasks todo total` → a health snapshot in four commands. Report the numbers;
  don't auto-delete orphans (many are intentional stubs).
- **Pre-edit context**: before revising a note, `backlinks file="X"` to see who
  depends on it and keep cross-references honest.
- **Link a new note in**: after writing `notes/foo.md`, `backlinks file="foo"`
  should be non-empty — if it's an orphan, add an inbound link from a relevant hub.

## Discovering more

`obsidian --help` lists the full command set; `obsidian help <command>` details one.
The catalog is large (plugins, snippets, workspace, dev tools) — this skill covers
the vault-knowledge subset that matters for day-to-day work.
