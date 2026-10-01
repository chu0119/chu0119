#!/usr/bin/env python3
"""Fetch recent GitHub activity for chu0119 and rewrite the ACTIVITY block in README.md."""
import json
import os
import re
import urllib.request
import xml.etree.ElementTree as ET
from xml.sax.saxutils import escape

USER = "chu0119"
TOKEN = os.environ.get("GH_TOKEN", "")
BEGIN = "<!-- BEGIN ACTIVITY -->"
END = "<!-- END ACTIVITY -->"
ACTIVITY_PATH = os.path.join("assets", "activity.svg")

BG = "#07101C"
PANEL = "#0C1D2C"
CYAN = "#59E7D1"
MAGENTA = "#E85B9C"
TEXT = "#EAF3F8"
MUTED = "#7691A5"

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


def render_activity_svg(lines):
    """Render recent public activity as a GitHub-safe dark SVG panel."""
    rows = []
    pattern = re.compile(
        r"^- . \[\*\*(?P<repo>.+?)\*\*\]\(https://github\.com/[^)]+\) — "
        r"(?P<action>.+)$"
    )
    for index, line in enumerate(lines[:5], 1):
        match = pattern.match(line)
        if match:
            repo = match.group("repo")
            action = match.group("action")
        else:
            repo = line.removeprefix("- ").strip()
            action = "PUBLIC BUILD SIGNAL"
        y = 70 + (index - 1) * 42
        accent = CYAN if index % 2 else MAGENTA
        rows.append(f'''  <rect x="18" y="{y}" width="684" height="34" rx="8" fill="{PANEL}" stroke="{accent}" stroke-opacity="0.25"/>
  <text x="34" y="{y + 22}" font-family="Consolas,Menlo,monospace" font-size="9" font-weight="700" fill="{accent}">{index:02d}</text>
  <text x="70" y="{y + 22}" font-family="Segoe UI,Arial,sans-serif" font-size="12" font-weight="700" fill="{TEXT}">{escape(repo)}</text>
  <text x="686" y="{y + 22}" text-anchor="end" font-family="Consolas,Menlo,monospace" font-size="8.5" fill="{MUTED}">{escape(action.upper())}</text>''')

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="720" height="300" viewBox="0 0 720 300" role="img" aria-labelledby="title desc">
  <title id="title">Recent Activity</title>
  <desc id="desc">Recent public GitHub activity for xingchuan</desc>
  <defs>
    <linearGradient id="activity-edge" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%" stop-color="{CYAN}"/>
      <stop offset="100%" stop-color="{MAGENTA}"/>
    </linearGradient>
  </defs>
  <rect width="720" height="300" rx="16" fill="{BG}"/>
  <rect x="0.75" y="0.75" width="718.5" height="298.5" rx="15" fill="none" stroke="url(#activity-edge)" stroke-opacity="0.42"/>
  <rect x="18" y="18" width="4" height="20" rx="2" fill="{MAGENTA}"/>
  <text x="34" y="32" font-family="Consolas,Menlo,monospace" font-size="13" font-weight="700" letter-spacing="1.7" fill="{CYAN}">RECENT ACTIVITY / 最近动态</text>
  <text x="702" y="31" text-anchor="end" font-family="Consolas,Menlo,monospace" font-size="9" letter-spacing="1.1" fill="{MUTED}">PUBLIC EVENTS · LIVE FEED</text>
  <path d="M18 49H702" stroke="#17364A"/>
{chr(10).join(rows)}
  <text x="18" y="282" font-family="Consolas,Menlo,monospace" font-size="8" letter-spacing="1" fill="{MUTED}">GITHUB PUBLIC EVENT STREAM · UPDATED BY REPOSITORY WORKFLOW</text>
</svg>'''


def main():
    events = api(f"https://api.github.com/users/{USER}/events/public?per_page=30")
    lines = render_activity(events)
    with open("README.md", encoding="utf-8") as f:
        readme = f.read()
    updated = replace_activity(readme, lines)
    activity_svg = render_activity_svg(lines)
    ET.fromstring(activity_svg)
    os.makedirs(os.path.dirname(ACTIVITY_PATH), exist_ok=True)
    with open(ACTIVITY_PATH, "w", encoding="utf-8", newline="\n") as f:
        f.write(activity_svg)
    if updated != readme:
        with open("README.md", "w", encoding="utf-8") as f:
            f.write(updated)
        print("README activity block updated")
    else:
        print("No changes")


if __name__ == "__main__":
    main()
