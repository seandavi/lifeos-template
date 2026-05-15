#!/usr/bin/env python3
"""
Ingest macOS Calendar events into ~/meetings/YYYY/MM/ markdown files with
wiki-linked attendees.

Reads from macOS Calendar via icalBuddy (which sees all sync'd calendars:
Outlook, Google, iCloud). Skips events with more than 20 attendees as a
proxy for "all-hands / large meeting."

Requires: icalBuddy (brew install ical-buddy)

Usage:
  LIFEOS_HOME=~/Documents/your-vault python scripts/meeting-ingest.py
"""
from __future__ import annotations

import datetime
import os
import re
import subprocess
from pathlib import Path

# Configuration ---------------------------------------------------------------
VAULT_ROOT = Path(os.environ.get("LIFEOS_HOME", Path.home() / "Documents" / "lifeos"))
MEETINGS_DIR = VAULT_ROOT / "meetings"
ICAL_BUDDY_CMD = [
    "icalBuddy",
    "-nc",
    "-nrd",
    "-po", "title,datetime,attendees,location,notes",
    "-ea",
]
DAYS_AHEAD = 7
MAX_ATTENDEES = 20  # skip past this to avoid all-hands events polluting the vault


def parse_attendees(attendees_str: str) -> list[str]:
    """Parse the attendees field from icalBuddy output and return wiki-linked names."""
    if not attendees_str or "attendees:" not in attendees_str:
        return []

    match = re.search(r"attendees: (.*)", attendees_str)
    if not match:
        return []

    attendee_list = [a.strip() for a in match.group(1).split(",")]
    if len(attendee_list) > MAX_ATTENDEES:
        return [f"[[Large Meeting: >{MAX_ATTENDEES} participants]]"]

    wiki_linked = []
    for attendee in attendee_list:
        clean_name = re.sub(r"\(.*?\)", "", attendee).strip()
        slug = re.sub(r"[^a-z0-9]", "-", clean_name.lower())
        wiki_linked.append(f"[[{slug}]]")
    return wiki_linked


def get_events(start_date: str, end_date: str) -> list[str]:
    cmd = ICAL_BUDDY_CMD + [f"eventsFrom:{start_date}", f"to:{end_date}"]
    result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
    return result.stdout.strip().split("•") if result.stdout.strip() else []


def sync_meetings() -> None:
    start_date = datetime.datetime.now().strftime("%Y-%m-%d")
    end_date = (datetime.datetime.now() + datetime.timedelta(days=DAYS_AHEAD)).strftime(
        "%Y-%m-%d"
    )

    events = get_events(start_date, end_date)

    for event_text in events:
        lines = [l.strip() for l in event_text.split("\n") if l.strip()]
        if not lines:
            continue

        title = lines[0]
        # Future work: extract date/time/attendees into structured file path
        # and write only new events (deduplicate via title+start as key).
        print(f"Found: {title}")


if __name__ == "__main__":
    if not MEETINGS_DIR.exists():
        MEETINGS_DIR.mkdir(parents=True, exist_ok=True)
    sync_meetings()
