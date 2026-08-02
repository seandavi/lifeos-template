#!/usr/bin/env python3
import os
import sys
import re
import argparse
import glob
from collections import defaultdict

def parse_frontmatter(content):
    frontmatter = {}
    if content.startswith('---'):
        parts = content.split('---', 2)
        if len(parts) >= 3:
            for line in parts[1].strip().split('\n'):
                # Ignore comments in frontmatter
                line = line.split('#')[0]
                if ':' in line:
                    k, v = line.split(':', 1)
                    k = k.strip()
                    v = v.strip().strip('"\'')
                    frontmatter[k] = v
    return frontmatter

def get_projects(vault_root):
    projects = {}
    for path in glob.glob(os.path.join(vault_root, 'projects', '*.md')):
        name = os.path.splitext(os.path.basename(path))[0]
        try:
            with open(path, 'r', encoding='utf-8') as f:
                fm = parse_frontmatter(f.read())
                projects[name] = fm
        except Exception as e:
            print(f"Warning: skipping project file {path}: {e}", file=sys.stderr)
    return projects

def parse_duration(line):
    total_hours = 0
    match_h = re.search(r'\b(\d+(?:\.\d+)?)h\b', line)
    if match_h:
        total_hours += float(match_h.group(1))
    
    match_m = re.search(r'\b(\d+)m\b', line)
    if match_m:
        total_hours += float(match_m.group(1)) / 60.0
        
    return total_hours

def parse_split(line, num_projects):
    if num_projects == 0:
        return []
    
    match = re.search(r'\(([\d/]+)\)', line)
    if match:
        parts = match.group(1).split('/')
        if len(parts) == num_projects:
            weights = [float(p) for p in parts]
            total = sum(weights)
            if total > 0:
                return [w/total for w in weights]
    
    # Default even split
    return [1.0 / num_projects for _ in range(num_projects)]

def get_journal_files(vault_root, start_date, end_date):
    files = []
    journal_dir = os.path.join(vault_root, 'journal')
    if not os.path.exists(journal_dir):
        return files
    for root, _, filenames in os.walk(journal_dir):
        for fn in filenames:
            if re.match(r'\d{4}-\d{2}-\d{2}\.md', fn):
                date_str = fn[:10]
                if start_date <= date_str <= end_date:
                    files.append((date_str, os.path.join(root, fn)))
    return files

def get_people(vault_root):
    people = set()
    for path in glob.glob(os.path.join(vault_root, 'people', '*.md')):
        name = os.path.splitext(os.path.basename(path))[0]
        people.add(name)
    return people

def process_file_lines(lines, date_str, projects_db, people_set, effort_by_proj, effort_by_person, effort_by_grant, milestones, start_date, end_date, is_journal=False):
    current_date = date_str
    # In journal files, only the "## Log" section holds effort entries; Morning/Evening
    # checkboxes may carry project links but are plans, not work performed.
    in_log_section = not is_journal

    for line in lines:
        line = line.strip()
        heading_match = re.match(r'^##\s+(.*)', line)
        if heading_match:
            if is_journal:
                in_log_section = heading_match.group(1).strip().lower().startswith('log')
            else:
                # Track dates in completed.md
                date_match = re.match(r'^(\d{4}-\d{2}-\d{2})', heading_match.group(1))
                if date_match:
                    current_date = date_match.group(1)
            continue

        if not in_log_section:
            continue

        if '%private' in line:
            continue

        if not line.startswith('-'):
            continue

        # Skip checkbox to-dos ("- [ ]" / "- [x]") — tasks, not logged work
        if re.match(r'^-\s*\[.\]', line):
            continue

        # completed.md entries carry their date inline: "- 2026-04-27 — ..."
        line_date = current_date
        inline_date = re.match(r'^-\s*(\d{4}-\d{2}-\d{2})', line)
        if inline_date:
            line_date = inline_date.group(1)

        if line_date and not (start_date <= line_date <= end_date):
            continue

        # Find all [[links]]
        links = re.findall(r'\[\[(.*?)\]\]', line)
        if not links:
            continue
            
        projs = [l for l in links if l in projects_db]
        people = [l for l in links if l in people_set]
        
        duration = parse_duration(line)
        
        if duration == 0 and projs:
            # Milestone — strip the list marker so report output isn't "- date: - text",
            # and the inline date (completed.md) since the report prints its own
            text = re.sub(r'^-\s*', '', line)
            text = re.sub(r'^\d{4}-\d{2}-\d{2}\s*[—:-]*\s*', '', text)
            for proj in projs:
                grant = projects_db[proj].get('grant_id', 'No Grant')
                if not grant: grant = 'No Grant'
                milestones.append({
                    'date': line_date,
                    'project': proj,
                    'grant': grant,
                    'text': text,
                    'people': people
                })
        elif duration > 0 and projs:
            # Effort
            splits = parse_split(line, len(projs))
            for proj, split_weight in zip(projs, splits):
                allocated_time = duration * split_weight
                effort_by_proj[proj] += allocated_time
                grant = projects_db[proj].get('grant_id', 'No Grant')
                if not grant: grant = 'No Grant'
                effort_by_grant[grant] += allocated_time
                
                if people:
                    # "Effort by person" means time involving that person: a 1h meeting
                    # with two people is 1h for each. Splitting only applies to
                    # projects/grants, where hours must sum to the block.
                    for person in people:
                        effort_by_person[person][proj] += allocated_time

def main():
    parser = argparse.ArgumentParser(description="Generate structured progress report")
    parser.add_argument('--start', required=True, help="Start date (YYYY-MM-DD)")
    parser.add_argument('--end', required=True, help="End date (YYYY-MM-DD)")
    parser.add_argument('--vault', default=".", help="Vault root directory")
    args = parser.parse_args()

    vault_root = args.vault
    projects_db = get_projects(vault_root)
    people_set = get_people(vault_root)
    
    effort_by_proj = defaultdict(float)
    effort_by_person = defaultdict(lambda: defaultdict(float))
    effort_by_grant = defaultdict(float)
    milestones = []

    # Process journal files
    journal_files = get_journal_files(vault_root, args.start, args.end)
    for date_str, path in journal_files:
        try:
            with open(path, 'r', encoding='utf-8') as f:
                process_file_lines(f.readlines(), date_str, projects_db, people_set, effort_by_proj, effort_by_person, effort_by_grant, milestones, args.start, args.end, is_journal=True)
        except Exception as e:
            print(f"Error reading {path}: {e}", file=sys.stderr)
            
    # Process completed.md
    completed_path = os.path.join(vault_root, 'completed.md')
    if os.path.exists(completed_path):
        try:
            with open(completed_path, 'r', encoding='utf-8') as f:
                process_file_lines(f.readlines(), None, projects_db, people_set, effort_by_proj, effort_by_person, effort_by_grant, milestones, args.start, args.end)
        except Exception as e:
            print(f"Error reading {completed_path}: {e}", file=sys.stderr)

    total_effort = sum(effort_by_proj.values())

    # Output generation
    print(f"# Progress Report ({args.start} to {args.end})\n")
    
    print("## Effort by Grant")
    if effort_by_grant:
        for grant, hours in sorted(effort_by_grant.items(), key=lambda x: x[1], reverse=True):
            pct = (hours / total_effort * 100) if total_effort > 0 else 0
            print(f"- **{grant}**: {hours:.1f}h ({pct:.0f}%)")
    else:
        print("No effort recorded.\n")
        
    print("\n## Effort by Project")
    if effort_by_proj:
        for proj, hours in sorted(effort_by_proj.items(), key=lambda x: x[1], reverse=True):
            pct = (hours / total_effort * 100) if total_effort > 0 else 0
            print(f"- **[[{proj}]]**: {hours:.1f}h ({pct:.0f}%)")
    else:
        print("No effort recorded.\n")
        
    print("\n## Effort by Person")
    if effort_by_person:
        for person, projs in effort_by_person.items():
            print(f"\n### [[{person}]]")
            person_total = sum(projs.values())
            for proj, hours in sorted(projs.items(), key=lambda x: x[1], reverse=True):
                print(f"- **[[{proj}]]**: {hours:.1f}h")
            print(f"**Total**: {person_total:.1f}h")
    else:
        print("No personnel effort recorded.\n")

    print("\n## Milestones & Accomplishments")
    if milestones:
        # Group by Grant
        milestones_by_grant = defaultdict(list)
        for m in milestones:
            milestones_by_grant[m['grant']].append(m)
            
        for grant, ms in sorted(milestones_by_grant.items()):
            print(f"\n### {grant}")
            for m in ms:
                print(f"- {m['date']}: {m['text']}")
    else:
        print("No milestones recorded.")

if __name__ == "__main__":
    main()
