#!/bin/bash
# Scan the last 48h of email and write actionable items to calendar/email-scan.md.
#
# How it works:
#   1. AppleScript pulls last 48h from macOS Mail.app INBOX (handles all configured
#      accounts — Gmail, Outlook/Exchange, iCloud, etc. in one shot).
#   2. The raw output is piped to an LLM CLI (gemini by default) for filtering and
#      summarization. The 48h window with overlap-between-runs is intentional:
#      morning routines fire at variable times, so 24h can miss items.
#
# Requirements:
#   - macOS Mail.app configured with your email account(s)
#   - An LLM CLI installed (default: gemini; alternatives: claude, ollama, llm)
#
# Configuration:
#   Set EMAIL_LLM env var to switch backends. Default is `gemini --yolo`.
#
# Usage: ./email-scan.sh
#
# Output: <VAULT_ROOT>/calendar/email-scan.md

set -euo pipefail

OUTFILE="${LIFEOS_HOME:-$HOME/Documents/lifeos}/calendar/email-scan.md"
LLM_CMD="${EMAIL_LLM:-gemini --yolo}"

# Detect Mail.app
if ! osascript -e 'application "Mail"' 2>/dev/null; then
  echo "macOS Mail.app not available. This script is macOS-specific." >&2
  exit 1
fi

PROMPT='Run AppleScript to pull last 48h from INBOX (use: tell application "Mail" / set _msgs to messages of inbox whose date received is greater than ((current date) - (48 * 60 * 60))). Extract sender, subject, and a content snippet for each. Filter to only action items / deadlines / responses needed. Skip newsletters, calendar invitations/notifications, and automated mail. Write a bullet summary (sender, subject, one-line action) to '"$OUTFILE"'.'

$LLM_CMD -p "$PROMPT"

echo "Wrote email scan to $OUTFILE"
