# /// script
# requires-python = ">=3.11"
# dependencies = ["pyyaml"]
# ///
"""Lint vault note frontmatter against reference/frontmatter-spec.yaml.

Report-only by default. `--fix` performs ONLY safe normalizations
(currently: none destructive — reserved). Exit code 1 if any ERROR found.

Usage:
    uv run scripts/vault_lint.py                 # lint whole vault
    uv run scripts/vault_lint.py people projects # lint specific folders
    uv run scripts/vault_lint.py --json          # machine-readable output
"""
from __future__ import annotations

import datetime as dt
import json
import sys
from pathlib import Path

import yaml

VAULT = Path(__file__).resolve().parent.parent
SPEC_PATH = VAULT / "reference" / "frontmatter-spec.yaml"


def load_spec() -> dict:
    return yaml.safe_load(SPEC_PATH.read_text())


def parse_frontmatter(text: str):
    """Return (frontmatter_dict_or_None, error_str_or_None)."""
    if not text.startswith("---"):
        return None, None
    end = text.find("\n---", 3)
    if end == -1:
        return None, "unterminated frontmatter block"
    block = text[3:end].lstrip("\n")
    try:
        data = yaml.safe_load(block)
    except yaml.YAMLError as e:
        return None, f"invalid YAML: {e}"
    if data is None:
        return {}, None
    if not isinstance(data, dict):
        return None, "frontmatter is not a mapping"
    return data, None


def note_type(fm: dict, path: Path, spec: dict) -> str | None:
    # Folder-first: the collection folder determines the schema. A note's own
    # `type:` field is a *sub-category* in some collections (projects use
    # type: research/infrastructure/...), so it must NOT override folder-based
    # classification. Fall back to frontmatter `type` only outside known folders.
    parent = path.parent.name
    folder_type = spec.get("folder_type", {}).get(parent)
    if folder_type:
        return folder_type
    if fm and isinstance(fm.get("type"), str):
        return fm["type"]
    return None


def lint_file(path: Path, spec: dict) -> list[dict]:
    findings: list[dict] = []
    rel = path.relative_to(VAULT)
    text = path.read_text()
    fm, err = parse_frontmatter(text)

    if err:
        findings.append({"file": str(rel), "level": "ERROR", "msg": err})
        return findings

    ntype = note_type(fm or {}, path, spec)
    if ntype is None:
        return findings  # not a typed collection; nothing to check
    rules = spec["types"].get(ntype)
    if rules is None:
        return findings

    if fm is None:
        # Only a problem if this type actually requires frontmatter fields.
        # Notes/decisions/research/talk-notes are fine without any.
        if rules.get("required"):
            findings.append({"file": str(rel), "level": "ERROR",
                             "msg": f"{ntype}: no frontmatter block (required: {rules['required']})"})
        return findings

    for key in rules.get("required", []):
        if key not in fm or fm[key] in (None, "", []):
            findings.append({"file": str(rel), "level": "ERROR",
                             "msg": f"{ntype}: missing required '{key}'"})
    for key in rules.get("recommended", []):
        if key not in fm or fm[key] in (None, "", []):
            findings.append({"file": str(rel), "level": "WARN",
                             "msg": f"{ntype}: missing recommended '{key}'"})
    for key in rules.get("list_fields", []):
        if key in fm and fm[key] not in (None, "") and not isinstance(fm[key], list):
            findings.append({"file": str(rel), "level": "ERROR",
                             "msg": f"{ntype}: '{key}' should be a list, got {type(fm[key]).__name__}"})
    for key, allowed in (rules.get("enums") or {}).items():
        if key in fm and fm[key] not in (None, "") and fm[key] not in allowed:
            findings.append({"file": str(rel), "level": "ERROR",
                             "msg": f"{ntype}: '{key}'={fm[key]!r} not in {allowed}"})

    stale = rules.get("stale_days")
    if stale and str(fm.get("status")) == "Active":
        upd = fm.get("updated")
        d = None
        if isinstance(upd, dt.date):
            d = upd
        elif isinstance(upd, str) and upd:
            try:
                d = dt.date.fromisoformat(upd[:10])
            except ValueError:
                pass
        if d is not None:
            age = (dt.date.today() - d).days
            if age > stale:
                findings.append({"file": str(rel), "level": "WARN",
                                 "msg": f"project: Active but 'updated' is {age}d old ({upd}) — reconcile vs now.md"})
    return findings


def main() -> int:
    args = [a for a in sys.argv[1:] if not a.startswith("-")]
    as_json = "--json" in sys.argv
    spec = load_spec()

    folders = args or list(spec["folder_type"])
    files: list[Path] = []
    for folder in folders:
        files.extend(sorted((VAULT / folder).glob("*.md")))

    all_findings: list[dict] = []
    for f in files:
        all_findings.extend(lint_file(f, spec))

    if as_json:
        print(json.dumps(all_findings, indent=2))
    else:
        errors = [f for f in all_findings if f["level"] == "ERROR"]
        warns = [f for f in all_findings if f["level"] == "WARN"]
        for f in all_findings:
            marker = "❌" if f["level"] == "ERROR" else "⚠️ "
            print(f"{marker} {f['file']}: {f['msg']}")
        print(f"\nLinted {len(files)} files — {len(errors)} errors, {len(warns)} warnings.")

    return 1 if any(f["level"] == "ERROR" for f in all_findings) else 0


if __name__ == "__main__":
    raise SystemExit(main())
