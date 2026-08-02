---
name: progress-report
description: "Generates a structured progress report across projects, people, and time. Parses the journal and completed.md for effort and milestones, grouping by grant, project, and person. Use when the user asks for a 'progress report', 'effort accounting', or asks 'what did I accomplish on project X'."
user-invocable: true
allowed-tools: Read, Bash
---

# Progress Report

Generates a structured progress report based on the journal logs and completed archive.

**Tone:** Professional and precise. Present the data clearly without fluff.

---

## Step 1: Clarify the scope

Determine the scope of the report from the user's request. If not specified, AskUserQuestion:
- Date range (e.g., "Q1 2026", "last year", "since 2026-01-01")
- (Optional) specific project or grant

---

## Step 2: Run the parser

Execute the parsing script with the appropriate arguments.
You may need to translate the user's date range into specific dates or pass it directly.

~~~bash
cd <VAULT_ROOT> && uv run scripts/progress-report.py --start "YYYY-MM-DD" --end "YYYY-MM-DD"
~~~

*Note: If `uv` is not available, fall back to `python3 scripts/progress-report.py`.*

---

## Step 3: Present the report

Output the generated Markdown report directly to the user. Do not summarize or alter the script's output, as it is designed to be copy-pasteable.
