---
type: dashboard
---

# 🏠 Command Center

> **Optional Obsidian dashboard layer.** Native **Bases** for note-collections + **Tasks** for checkboxes. Everything degrades to plain markdown — if you don't use Obsidian, or don't enable these, nothing breaks. Setup: [`docs/obsidian-setup.md`](../docs/obsidian-setup.md).

## 🎛️ Live files
- [[now]] · [[inbox]] · [[completed]] · [[projects]] · [[plan]]

## 📊 Dashboards
- [[tasks-dashboard]] — open items across inbox + journals (needs the Tasks plugin)

## 🚀 Active projects
*(native Bases view — edit properties in each project note; this table follows automatically)*

![[projects.base]]

## 👥 People directory
![[people.base]]

## 💰 Budget pipeline
![[funding.base]]

## ✍️ Output pipeline
*(heuristic — matches `projects/` notes whose deliverables/artifacts/name look output-ish)*

![[writing.base]]

## 🧭 About
- `.base` files in `dashboards/` are native Obsidian databases (Obsidian 1.9+). Coding agents can query them via the `obsidian` CLI (`obsidian base:query`).
- Validate note frontmatter against the schema: `uv run scripts/vault_lint.py`.
- Bases views are only as fresh as note frontmatter — keep project `status`/`updated` current (a periodic review skill helps).
