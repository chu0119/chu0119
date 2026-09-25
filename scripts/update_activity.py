#!/usr/bin/env python3
"""Fetch recent GitHub activity for chu0119 and rewrite the ACTIVITY block in README.md."""
import json
import os
import urllib.request

USER = "chu0119"
TOKEN = os.environ.get("GH_TOKEN", "")
BEGIN = "<!-- BEGIN ACTIVITY -->"
END = "<!-- END ACTIVITY -->"

EVENT_LABELS = {
    "PushEvent": ("🚀", "pushed updates"),
    "CreateEvent": ("✨", "created something new"),
    "WatchEvent": ("⭐", "starred this project"),
    "ForkEvent": ("🍴", "forked this project"),
    "ReleaseEvent": ("📦", "published a release"),
    "PullRequestEvent": ("🔀", "opened a pull request"),
}


def api(url):
    req = urllib.request.Request(url, headers={"Accept": "application/vnd.github+json"})
    if TOKEN:
        req.add_header("Authorization", f"Bearer {TOKEN}")
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def render_activity(events):
    """Turn public GitHub events into at most five unique activity links."""
    lines = []
    seen = set()
    for event in events:
        repo = event.get("repo", {}).get("name", "")
        if not repo or repo == f"{USER}/{USER}" or repo in seen:
            continue
        icon, action = EVENT_LABELS.get(
            event.get("type", ""), ("🧪", "worked on this project")
        )
        short = repo.split("/", 1)[1] if repo.startswith(f"{USER}/") else repo
        lines.append(f"- {icon} [**{short}**](https://github.com/{repo}) — {action}")
        seen.add(repo)
        if len(lines) == 5:
            break
    return lines or ["- 🔬 Building in public · 持续构建中"]


def replace_activity(readme, lines):
    """Replace exactly one activity region without touching other content."""
    if readme.count(BEGIN) != 1 or readme.count(END) != 1:
        raise ValueError("README must contain exactly one activity marker pair")
    start, tail = readme.split(BEGIN, 1)
    _, end = tail.split(END, 1)
    body = "\n".join(lines)
    return f"{start}{BEGIN}\n{body}\n{END}{end}"


def main():
    events = api(f"https://api.github.com/users/{USER}/events/public?per_page=30")
    lines = render_activity(events)
    with open("README.md", encoding="utf-8") as f:
        readme = f.read()
    updated = replace_activity(readme, lines)
    if updated != readme:
        with open("README.md", "w", encoding="utf-8") as f:
            f.write(updated)
        print("README activity block updated")
    else:
        print("No changes")


if __name__ == "__main__":
    main()
