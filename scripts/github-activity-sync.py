#!/usr/bin/env python3
import os
import sys
import json
import shutil
import subprocess
import glob
from datetime import datetime, timezone
import re

def run_gh_api(endpoint, method="GET", body=None):
    cmd = ["gh", "api", endpoint, "-X", method]
    if body:
        cmd.extend(["-f", f"query={json.dumps(body)}"])
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
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
                    projects_by_topic[fm['grant_id']] = name
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

def append_to_journal(vault_root, date_str, line):
    filepath = get_date_path(vault_root, date_str)
    if not filepath:
        return
    
    if not os.path.exists(filepath):
        # Create with frontmatter if it doesn't exist
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f"---\ntitle: {date_str}\n---\n\n# {date_str}\n\n")
            
    with open(filepath, 'a', encoding='utf-8') as f:
        if os.path.getsize(filepath) > 0:
            # Ensure it ends with a newline before appending
            with open(filepath, 'r', encoding='utf-8') as rf:
                if not rf.read().endswith("\n"):
                    f.write("\n")
        f.write(f"{line}\n")

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

    projects_by_topic = get_projects(vault_root)
    
    since_date = (datetime.now(timezone.utc).astimezone().replace(microsecond=0) 
                  .replace(hour=0, minute=0, second=0) 
                  .isoformat())
    # simple formatting for GitHub API
    since_str = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0).isoformat()
    if sys.version_info >= (3, 11):
         import datetime as dt
         since_date = (dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=args.days)).isoformat()
    else:
        # Fallback
        import datetime as dt
        since_date = (dt.datetime.utcnow() - dt.timedelta(days=args.days)).isoformat() + "Z"


    repos_to_scan = {}
    unattributable = []

    # 1. Discover by topic
    for topic in topics:
        search_results = run_gh_api(f"search/repositories?q=topic:{topic}")
        if search_results and "items" in search_results:
            for repo in search_results["items"]:
                full_name = repo["full_name"]
                if repo.get("fork") and not explicit_repos.get(full_name, {}).get("allow_fork"):
                    continue
                repos_to_scan[full_name] = {"topic": topic, "config": explicit_repos.get(full_name, {})}

    # 2. Add explicit repos
    for full_name, repo_config in explicit_repos.items():
        if full_name not in repos_to_scan:
            repos_to_scan[full_name] = {"topic": repo_config.get("topic"), "config": repo_config}
        elif "topic" in repo_config:
            repos_to_scan[full_name]["topic"] = repo_config["topic"]

    for full_name, repo_data in repos_to_scan.items():
        topic = repo_data["topic"]
        project_name = projects_by_topic.get(topic)
        
        if not project_name:
            # Try to infer from explicit repo if topic is missing
            if topic:
                 unattributable.append(f"- Repo: {full_name} (Topic: {topic}) - No matching grant_id in projects/*.md")
            else:
                 unattributable.append(f"- Repo: {full_name} (Explicitly configured) - No topic assigned to map to project")
            continue

        include_all = repo_data["config"].get("include_all_authors", False)

        # Fetch Commits
        commits = run_gh_api(f"repos/{full_name}/commits?since={since_date}")
        if commits:
            for commit in commits:
                if not include_all:
                    author_login = commit.get("author", {}).get("login") if commit.get("author") else None
                    if author_login not in authors:
                        continue
                
                sha = commit["sha"][:7]
                msg = commit["commit"]["message"].split('\n')[0]
                date_str = commit["commit"]["author"]["date"][:10]
                
                # Check duplication
                filepath = get_date_path(vault_root, date_str)
                if not file_contains(filepath, sha):
                    line = f"- [[{project_name}]] Commit {sha}: {msg} (0h)"
                    append_to_journal(vault_root, date_str, line)

        # Fetch PRs Created
        pulls = run_gh_api(f"repos/{full_name}/pulls?state=all&sort=created&direction=desc")
        if pulls:
            for pr in pulls:
                created_at = pr["created_at"]
                if created_at < since_date:
                    continue # PRs are sorted desc, so we can break/continue
                    
                if not include_all:
                    if pr.get("user", {}).get("login") not in authors:
                        continue
                        
                number = pr["number"]
                title = pr["title"]
                date_str = created_at[:10]
                
                filepath = get_date_path(vault_root, date_str)
                marker = f"{full_name} PR #{number}"
                if not file_contains(filepath, marker):
                    line = f"- [[{project_name}]] Created PR #{number} in {full_name}: {title} (0h)"
                    append_to_journal(vault_root, date_str, line)
                    
        # Fetch PR Reviews (this requires iterating PRs which is expensive, but for recent it's okay)
        # We can use search issues for this author's reviews
        if not include_all and authors:
            for author in authors:
                search_reviews = run_gh_api(f"search/issues?q=repo:{full_name}+is:pr+reviewed-by:{author}+updated:>={since_date[:10]}")
                if search_reviews and "items" in search_reviews:
                    for pr in search_reviews["items"]:
                        number = pr["number"]
                        title = pr["title"]
                        # Just append to today since review date is hard to pin down without GraphQL or many REST calls
                        today_str = datetime.now(timezone.utc).isoformat()[:10]
                        filepath = get_date_path(vault_root, today_str)
                        marker = f"Reviewed {full_name} PR #{number}"
                        if not file_contains(filepath, marker):
                            line = f"- [[{project_name}]] Reviewed PR #{number} in {full_name}: {title} (0h)"
                            append_to_journal(vault_root, today_str, line)

    if unattributable:
        unattributable_path = os.path.join(vault_root, 'unattributable.md')
        with open(unattributable_path, 'w', encoding='utf-8') as f:
            f.write("# Unattributable GitHub Repositories\n\n")
            f.write("The following repositories were discovered but could not be mapped to a LifeOS project. Ensure your projects have a `grant_id` frontmatter that matches the repository's GitHub topic.\n\n")
            for item in unattributable:
                f.write(f"{item}\n")
                print(item, file=sys.stderr)
        
if __name__ == "__main__":
    main()
