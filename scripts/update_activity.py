#!/usr/bin/env python3
"""Fetch recent GitHub activity for chu0119 and rewrite the ACTIVITY block in README.md."""
import json
import os
import re
import urllib.request

USER = "chu0119"
TOKEN = os.environ.get("GH_TOKEN", "")
BEGIN = "<!-- BEGIN ACTIVITY -->"
END = "<!-- END ACTIVITY -->"


def api(url):
    req = urllib.request.Request(url, headers={"Accept": "application/vnd.github+json"})
    if TOKEN:
        req.add_header("Authorization", f"Bearer {TOKEN}")
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def main():
    events = api(f"https://api.github.com/users/{USER}/events/public?per_page=30")
    lines = []
    seen = set()
    for ev in events:
        repo = ev.get("repo", {}).get("name", "")
        if not repo or repo in seen or repo.startswith(f"{USER}/{USER}"):
            continue
        if repo.startswith(f"{USER}/"):
            short = repo.split("/", 1)[1]
        else:
            short = repo
        kind = ev.get("type", "")
        icon = {
            "PushEvent": "🚀",
            "CreateEvent": "✨",
            "WatchEvent": "⭐",
            "ForkEvent": "🍴",
            "ReleaseEvent": "📦",
            "PullRequestEvent": "🔀",
        }.get(kind, "📝")
        action = {
            "PushEvent": "pushed to",
            "CreateEvent": "created",
            "WatchEvent": "starred",
            "ForkEvent": "forked",
            "ReleaseEvent": "released",
            "PullRequestEvent": "opened PR in",
        }.get(kind, f"{kind.replace('Event','').lower()} in")
        lines.append(f"- {icon} **{short}** — {action} it")
        seen.add(repo)
        if len(lines) >= 5:
            break

    if not lines:
        lines = ["- 🗡️ Deep in the lab — check back soon"]

    block = BEGIN + "\n" + "\n".join(lines) + "\n" + END
    with open("README.md", encoding="utf-8") as f:
        readme = f.read()
    updated = re.sub(re.escape(BEGIN) + r".*?" + re.escape(END), block, readme, flags=re.S)
    if updated != readme:
        with open("README.md", "w", encoding="utf-8") as f:
            f.write(updated)
        print("README activity block updated")
    else:
        print("No changes")


if __name__ == "__main__":
    main()
