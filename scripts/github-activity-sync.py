#!/usr/bin/env python3
import os
import sys
import json
import shutil
import subprocess
import glob
from datetime import datetime, timezone
try:
    from zoneinfo import ZoneInfo
except ImportError:
    ZoneInfo = None
import re

def sanitize_text(text):
    # Remove lifeOS tags
    text = re.sub(r'\[\[.*?\]\]', '', text)
    # Remove duration tags (e.g. (1h), (30m), (1h30m))
    text = re.sub(r'\(\d+[hm](?:\d+[hm])?\)', '', text)
    # Escape bare duration tokens that progress-report.py recognizes (e.g., 24h -> 24 h)
    text = re.sub(r'\b(\d+(?:\.\d+)?)([hm])\b', r'\1 \2', text)
    # Remove private tags
    text = text.replace('%private', '')
    return text.strip()

def run_gh_api(endpoint, method="GET", body=None, paginate=False):
    cmd = ["gh", "api", endpoint, "-X", method]
    if paginate:
        cmd.append("--paginate")
        if endpoint.startswith("search/"):
            cmd.extend(["-q", ".items[]"])
        else:
            cmd.extend(["-q", ".[]"])
    if body:
        cmd.extend(["-f", f"query={json.dumps(body)}"])
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        if not result.stdout.strip():
            if paginate and endpoint.startswith("search/"): return {"items": []}
            return [] if paginate else {}
        
        if paginate:
            items = []
            for line in result.stdout.strip().split('\n'):
                if line.strip():
                    items.append(json.loads(line))
            if endpoint.startswith("search/"):
                return {"items": items}
            return items
        else:
            return json.loads(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"Error calling GitHub API {endpoint}: {e.stderr}", file=sys.stderr)
        return None
    except json.JSONDecodeError:
        print(f"Failed to parse JSON from {endpoint}", file=sys.stderr)
        return None

def parse_frontmatter(content):
    frontmatter = {}
    if content.startswith('---'):
        parts = content.split('---', 2)
        if len(parts) >= 3:
            for line in parts[1].strip().split('\n'):
                line = line.split('#')[0]
                if ':' in line:
                    k, v = line.split(':', 1)
                    k = k.strip()
                    v = v.strip().strip('"\'')
                    frontmatter[k] = v
    return frontmatter

def get_projects(vault_root):
    projects_by_topic = {}
    for path in glob.glob(os.path.join(vault_root, 'projects', '*.md')):
        name = os.path.splitext(os.path.basename(path))[0]
        try:
            with open(path, 'r', encoding='utf-8') as f:
                fm = parse_frontmatter(f.read())
                if 'grant_id' in fm:
                    projects_by_topic.setdefault(fm['grant_id'], []).append(name)
        except Exception:
            pass
    return projects_by_topic

def get_date_path(vault_root, date_str):
    # date_str is YYYY-MM-DD
    parts = date_str.split('-')
    if len(parts) != 3:
        return None
    year, month, day = parts
    dir_path = os.path.join(vault_root, 'journal', year, month)
    os.makedirs(dir_path, exist_ok=True)
    return os.path.join(dir_path, f"{date_str}.md")

def file_contains(filepath, text):
    if not os.path.exists(filepath):
        return False
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
        return text in content

def check_duplicate_effort(filepath, project_name):
    if not os.path.exists(filepath):
        return False
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    in_log = False
    for line in content.splitlines():
        if line.startswith("## Log"):
            in_log = True
            continue
        elif in_log and line.startswith("## "):
            in_log = False
            
        if in_log and not re.match(r'^-\s*\[.\]', line):
            if f"[[{project_name}]]" in line and "(0h)" not in line:
                return True
    return False

def append_to_journal(vault_root, date_str, line):
    filepath = get_date_path(vault_root, date_str)
    if not filepath:
        return
    
    if not os.path.exists(filepath):
        template_path = os.path.join(vault_root, 'templates', 'daily-journal.md')
        if os.path.exists(template_path):
            with open(template_path, 'r', encoding='utf-8') as tf:
                content = tf.read().replace('{{DAY, MONTH D, YYYY}}', date_str)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
        else:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(f"---\ntitle: {date_str}\n---\n\n# {date_str}\n\n## Log\n\n")
            
    with open(filepath, 'r+', encoding='utf-8') as f:
        content = f.read()
        
        if "## Log" not in content:
            if not content.endswith('\n'):
                f.write("\n")
            f.write("\n## Log\n\n")
            content = content + ("\n" if not content.endswith('\n') else "") + "\n## Log\n\n"
        
        lines = content.splitlines()
        log_idx = -1
        next_heading_idx = len(lines)
        for i, l in enumerate(lines):
            if l.startswith("## Log"):
                log_idx = i
            elif log_idx != -1 and l.startswith("## "):
                next_heading_idx = i
                break
                
        insert_idx = next_heading_idx
        while insert_idx > log_idx + 1:
            prev_line = lines[insert_idx - 1].strip()
            if not prev_line or prev_line == '---':
                insert_idx -= 1
            else:
                break
                
        lines.insert(insert_idx, line)
        
        f.seek(0)
        f.truncate()
        f.write("\n".join(lines) + "\n")

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Sync GitHub activity to journal")
    parser.add_argument('--vault', default=".", help="Vault root directory")
    parser.add_argument('--days', type=int, default=7, help="Number of days to look back")
    args = parser.parse_args()

    vault_root = args.vault
    config_path = os.path.join(vault_root, 'github-config.json')

    # Capability Gate
    if not shutil.which("gh"):
        print("gh CLI not found. Skipping GitHub sync.", file=sys.stderr)
        sys.exit(0)
    
    if not os.path.exists(config_path):
        print("github-config.json not found. Skipping GitHub sync.", file=sys.stderr)
        sys.exit(0)

    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
    except json.JSONDecodeError:
        print("Failed to parse github-config.json.", file=sys.stderr)
        sys.exit(1)

    authors = config.get("authors", [])
    topics = config.get("topics", [])
    explicit_repos = config.get("repos", {})

    vault_tz_str = config.get("timezone", "UTC")
    vault_tz = timezone.utc
    if vault_tz_str != "UTC" and ZoneInfo is not None:
        try:
            vault_tz = ZoneInfo(vault_tz_str)
        except Exception as e:
            print(f"Warning: Invalid timezone '{vault_tz_str}', falling back to UTC. ({e})", file=sys.stderr)

    projects_by_topic = get_projects(vault_root)
    
    since_date = (datetime.now(vault_tz).replace(microsecond=0) 
                  .replace(hour=0, minute=0, second=0) 
                  .isoformat())
    # simple formatting for GitHub API
    since_str = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0).isoformat()
    if sys.version_info >= (3, 11):
         import datetime as dt
         since_date = (dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=args.days)).isoformat().replace("+00:00", "Z")
    else:
        # Fallback
        import datetime as dt
        since_date = (dt.datetime.utcnow() - dt.timedelta(days=args.days)).isoformat() + "Z"

    api_failed = False

    # Normalize authors
    normalized_authors = set(authors)
    try:
        user_info = run_gh_api("user")
        if user_info:
            if user_info.get("login"): normalized_authors.add(user_info["login"])
            if user_info.get("name"): normalized_authors.add(user_info["name"])
            if user_info.get("email"): normalized_authors.add(user_info["email"])
        elif user_info is None:
            api_failed = True
    except Exception:
        pass
    authors = list(normalized_authors)

    repos_to_scan = {}
    unattributable = []

    # 1. Discover by topic
    for topic in topics:
        search_results = run_gh_api(f"search/repositories?q=topic:{topic}", paginate=True)
        if search_results is None:
            api_failed = True
        elif "items" in search_results:
            for repo in search_results["items"]:
                full_name = repo["full_name"]
                if repo.get("fork") and not explicit_repos.get(full_name, {}).get("allow_fork"):
                    continue
                if full_name not in repos_to_scan:
                    repos_to_scan[full_name] = {"topics": set(), "config": explicit_repos.get(full_name, {})}
                repos_to_scan[full_name]["topics"].add(topic)

    # 2. Add explicit repos
    for full_name, repo_config in explicit_repos.items():
        if not repo_config.get("allow_fork"):
            repo_info = run_gh_api(f"repos/{full_name}")
            if repo_info is None:
                api_failed = True
            elif repo_info.get("fork"):
                continue
                
        if full_name not in repos_to_scan:
            repos_to_scan[full_name] = {"topics": set(), "config": repo_config}
        if "topic" in repo_config:
            repos_to_scan[full_name]["topics"].add(repo_config["topic"])

    for full_name, repo_data in repos_to_scan.items():
        repo_topics = repo_data["topics"]
        
        project_names = set()
        for t in repo_topics:
            if t in projects_by_topic:
                project_names.update(projects_by_topic[t])
                
        if not project_names:
            if repo_topics:
                 unattributable.append(f"- Repo: {full_name} (Topics: {', '.join(repo_topics)}) - No matching grant_id in projects/*.md")
            else:
                 unattributable.append(f"- Repo: {full_name} (Explicitly configured) - No topic assigned to map to project")
            continue
            
        explicit_project = repo_data["config"].get("project")
        explicit_topic = repo_data["config"].get("topic")
        explicit_projects = projects_by_topic.get(explicit_topic, []) if explicit_topic else []
        
        if explicit_project:
             if os.path.exists(os.path.join(vault_root, "projects", f"{explicit_project}.md")):
                  project_name = explicit_project
             else:
                  unattributable.append(f"- Repo: {full_name} (Explicit config) - Project '{explicit_project}' does not exist.")
                  continue
        elif len(project_names) > 1 and len(explicit_projects) != 1:
             unattributable.append(f"- Repo: {full_name} (Topics: {', '.join(repo_topics)}) - Matches multiple projects ({', '.join(project_names)}). Configure an explicit 'project' override.")
             continue
        elif len(explicit_projects) == 1:
             project_name = explicit_projects[0]
        else:
             project_name = list(project_names)[0]

        include_all = repo_data["config"].get("include_all_authors", False)

        # Fetch Commits
        commits = run_gh_api(f"repos/{full_name}/commits?since={since_date}", paginate=True)
        if commits is None:
            api_failed = True
        elif commits:
            for commit in commits:
                if not include_all:
                    author_login = commit.get("author", {}).get("login") if commit.get("author") else None
                    author_name = commit.get("commit", {}).get("author", {}).get("name")
                    author_email = commit.get("commit", {}).get("author", {}).get("email")
                    if not (author_login in authors or author_name in authors or author_email in authors):
                        continue
                
                sha = commit["sha"][:7]
                msg = sanitize_text(commit["commit"]["message"].split('\n')[0])
                
                # Convert to local timezone
                utc_str = commit["commit"]["author"]["date"].replace("Z", "+00:00")
                date_str = datetime.fromisoformat(utc_str).astimezone(vault_tz).isoformat()[:10]
                
                # Check duplication
                filepath = get_date_path(vault_root, date_str)
                if not file_contains(filepath, sha):
                    confirm_str = " <!-- CONFIRM DUPLICATE? -->" if check_duplicate_effort(filepath, project_name) else ""
                    line = f"- [[{project_name}]] Commit {sha}: {msg} (0h){confirm_str}"
                    append_to_journal(vault_root, date_str, line)

        # Fetch PRs Created
        pulls_search = run_gh_api(f"search/issues?q=repo:{full_name}+is:pr+created:>={since_date[:10]}", paginate=True)
        if pulls_search is None:
            api_failed = True
        elif "items" in pulls_search:
            for pr in pulls_search["items"]:
                created_at = pr["created_at"]
                if created_at < since_date:
                    continue
                    
                if not include_all:
                    if pr.get("user", {}).get("login") not in authors:
                        continue
                        
                number = pr["number"]
                title = sanitize_text(pr["title"])
                utc_str = created_at.replace("Z", "+00:00")
                date_str = datetime.fromisoformat(utc_str).astimezone(vault_tz).isoformat()[:10]
                
                filepath = get_date_path(vault_root, date_str)
                marker = f"Created {full_name} PR #{number}"
                if not file_contains(filepath, marker):
                    confirm_str = " <!-- CONFIRM DUPLICATE? -->" if check_duplicate_effort(filepath, project_name) else ""
                    line = f"- [[{project_name}]] Created {full_name} PR #{number}: {title} (0h){confirm_str}"
                    append_to_journal(vault_root, date_str, line)
                    
        # Fetch PR Reviews
        if authors or include_all:
            updated_prs = run_gh_api(f"search/issues?q=repo:{full_name}+is:pr+updated:>={since_date[:10]}", paginate=True)
            if updated_prs is None:
                api_failed = True
            elif "items" in updated_prs:
                for pr in updated_prs["items"]:
                    number = pr["number"]
                    reviews = run_gh_api(f"repos/{full_name}/pulls/{number}/reviews", paginate=True)
                    if reviews is None:
                        api_failed = True
                    elif reviews:
                        for review in reviews:
                            if review.get("submitted_at") and review["submitted_at"] >= since_date:
                                reviewer_login = review.get("user", {}).get("login")
                                reviewer_name = review.get("user", {}).get("name")
                                reviewer_email = review.get("user", {}).get("email")
                                if not include_all and not (reviewer_login in authors or reviewer_name in authors or reviewer_email in authors):
                                    continue
                                    
                                utc_str = review["submitted_at"].replace("Z", "+00:00")
                                review_date = datetime.fromisoformat(utc_str).astimezone(vault_tz).isoformat()[:10]
                                filepath = get_date_path(vault_root, review_date)
                                marker = f"<!-- REVIEW_ID:{review['id']} -->"
                                if not file_contains(filepath, marker):
                                    confirm_str = " <!-- CONFIRM DUPLICATE? -->" if check_duplicate_effort(filepath, project_name) else ""
                                    title = sanitize_text(pr['title'])
                                    line = f"- [[{project_name}]] Reviewed {full_name} PR #{number}: {title} (0h){confirm_str}{marker}"
                                    append_to_journal(vault_root, review_date, line)

    unattributable_path = os.path.join(vault_root, 'unattributable.md')
    if unattributable:
        with open(unattributable_path, 'w', encoding='utf-8') as f:
            f.write("# Unattributable GitHub Repositories\n\n")
            f.write("The following repositories were discovered but could not be mapped to a LifeOS project. Ensure your projects have a `grant_id` frontmatter that matches the repository's GitHub topic.\n\n")
            for item in unattributable:
                f.write(f"{item}\n")
                print(item, file=sys.stderr)
    elif not api_failed and os.path.exists(unattributable_path):
        os.remove(unattributable_path)

    if api_failed:
        sys.exit(1)
        
if __name__ == "__main__":
    main()
