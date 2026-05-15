---
name: meeting-prep
description: "Generate meeting prep briefs for upcoming calendar events. For each meeting, pulls people/[name].md, recent journal mentions, open inbox items touching the person, open decisions, and last commitments. Outputs a per-meeting brief: 3 things to know, 3 questions to ask, 1 risk, last commitments. Use when user says 'meeting prep', '/meeting-prep', 'prep for tomorrow', or nightly at 9pm as a scheduled routine."
user-invocable: true
allowed-tools: Read, Write, Glob, Grep, Bash, AskUserQuestion
---

# Meeting Prep

Prepare briefs for upcoming meetings. The vault holds people records, journal mentions, and open threads — your job is to turn that context into a 60-second brief per meeting.

**Tone:** Operational. Like a chief of staff handing over notes before a meeting. Specific. No hedging.

---

## Step 1: Determine which meetings to prep

If invoked without args, default to **tomorrow** (or "today's remaining" if invoked after morning).

If invoked with `/meeting-prep [person]`, prep that person's meeting if on the calendar; otherwise prep a generic 1:1 brief on them.

Run the calendar export first:
```bash
<VAULT_ROOT>/calendar/export-calendar.sh 2>/dev/null
```
Then read `<VAULT_ROOT>/calendar/this-week.md` for the target day's events.

Skip:
- All-day events (typically travel/holidays)
- Events from non-owned calendars (verify ownership; the user's calendar export may include shared / spouse / team calendars)
- Events with only the user attending (focus blocks)

---

## Step 2: For each real meeting, gather context

In parallel:

1. **Resolve attendees** — from event title/description, extract names. For each, check `<VAULT_ROOT>/people/[name].md` exists via Glob with kebab-case patterns.

2. **Read each person file.** Pull: role, domains, tags, recent interactions, open threads.

3. **Find recent journal mentions** (last 30 days):
   ```bash
   grep -rl "person-name" <VAULT_ROOT>/journal/$(date +%Y)/ | head -10
   ```
   Read the mentions. Pull 1-2 most relevant log lines.

4. **Open inbox items touching them:**
   ```bash
   grep -n "person\|topic" <VAULT_ROOT>/inbox.md
   ```

5. **Open decisions involving them:**
   ```
   Glob: <VAULT_ROOT>/decisions/*.md
   ```
   Read frontmatter; flag any where this person is named.

6. **Last email signal** — read `<VAULT_ROOT>/calendar/email-scan.md` for recent mentions.

7. **Project context** — if the meeting title or person record mentions a project, read the relevant section of `projects.md` and `now.md`.

---

## Step 3: Write the brief per meeting

Output one brief per meeting:

```markdown
## HH:MM — {{Meeting title}}
**Who:** {{names, with [[wiki-links]]}}
**Format:** {{Zoom / In-person / Phone}}
**Duration:** {{minutes}}

### Why this matters
{{1-2 sentences on stakes / why on the calendar}}

### 3 things to know
1. {{Most recent / relevant context — cite source: "from YYYY-MM-DD journal" or "from people/X.md"}}
2. {{Status of any in-flight work involving this person}}
3. {{Any open decision or commitment}}

### 3 questions to ask / decisions to land
1. {{Question that moves the relationship or work forward}}
2.
3.

### 1 risk
{{What could go wrong — institutional dynamic, misalignment, sensitivity}}

### Last commitments
- From you to them: {{...}}
- From them to you: {{...}}

### After the meeting
- [ ] {{What to do / capture / decide}}
```

If the person file doesn't exist, note "no person record — create after meeting?" and prep based on event title context.

---

## Step 4: Surface patterns across the day

After all briefs, add:

```markdown
## Day overview

**Total meetings:** N
**Total meeting time:** X hrs
**Themes:** {{e.g., "Recruitment thread (3 meetings)", "Hiring (2 meetings)"}}
**Open afternoon for:** {{the gaps + what's pending in inbox that could fit}}
**Energy call:** {{If 5+ meetings, flag fatigue risk}}
```

---

## Step 5: Save the brief

Write to `<VAULT_ROOT>/calendar/prep/YYYY-MM-DD.md`.

Create the `calendar/prep/` directory if it doesn't exist.

If today's journal exists and doesn't have a meeting brief link, append:
```markdown
**Tomorrow's prep:** [[YYYY-MM-DD-prep]]
```

---

## Step 6: Flag anything needing attention now

If during prep you find:
- A person file woefully out of date
- An open inbox item that should be replied to before the meeting
- A decision overdue for revisit involving this person
- A meeting where you have zero context

Surface via AskUserQuestion before finishing.

---

## What to NOT do

- Don't fabricate context. If the vault doesn't have it, say "no prior context."
- Don't pad briefs to fixed length. 2-line brief for a coffee chat is fine.
- Don't reread the entire person file in output — extract what matters for *this* meeting.
- Don't generate "small talk topics."
- Don't auto-update person files — post-meeting work, not prep.

---

## End state

- A file at `calendar/prep/YYYY-MM-DD.md` with briefs per meeting
- A backlink from today's journal entry
- Any urgent pre-meeting items surfaced
