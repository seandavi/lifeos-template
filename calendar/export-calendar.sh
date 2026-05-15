#!/bin/bash
# Export the next week of calendar events to markdown.
# Reads from macOS Calendar (which syncs Outlook + Google + iCloud).
# Writes to calendar/this-week.md, which the morning skill reads.
#
# Requires: icalBuddy (brew install ical-buddy)
#
# Usage: ./export-calendar.sh [days_ahead]
#   default: 7 days

set -euo pipefail

DAYS=${1:-7}
OUTDIR="$(cd "$(dirname "$0")" && pwd)"
TODAY=$(date +%Y-%m-%d)

if ! command -v icalBuddy >/dev/null 2>&1; then
  echo "icalBuddy not found. Install with: brew install ical-buddy" >&2
  exit 1
fi

{
  echo "# Calendar: $TODAY + ${DAYS} days"
  echo ""
  echo "Last exported: $(date '+%Y-%m-%d %H:%M')"
  echo ""
  icalBuddy -sd -nc -nrd \
    -iep "title,datetime,location" \
    -df "%Y-%m-%d %A" -tf "%H:%M" \
    -b "- " \
    "eventsToday+${DAYS}" 2>/dev/null | sed $'s/\033\[[0-9;]*m//g'
} > "$OUTDIR/this-week.md"

echo "Exported to $OUTDIR/this-week.md"
