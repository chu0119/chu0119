#!/usr/bin/env python3
"""Generate profile stats SVGs using GitHub API. No external service dependencies."""
import json
import math
import os
import urllib.request
import xml.etree.ElementTree as ET
from xml.sax.saxutils import escape

USER = "chu0119"
TOKEN = os.environ.get("GH_TOKEN", os.environ.get("GITHUB_TOKEN", ""))
OUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets")

BG = "#07101C"
PANEL = "#0C1D2C"
CYAN = "#59E7D1"
BLUE = "#66DDFF"
MAGENTA = "#E85B9C"
TEXT = "#EAF3F8"
MUTED = "#7691A5"


def svg_text(value):
    """Escape dynamic values before inserting them into SVG markup."""
    return escape(str(value), {'"': "&quot;", "'": "&apos;"})


def api(url):
    req = urllib.request.Request(url, headers={
        "Accept": "application/vnd.github+json",
        "User-Agent": "chu0119-profile-bot"
    })
    if TOKEN:
        req.add_header("Authorization", f"Bearer {TOKEN}")
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def gql(query, variables=None):
    body = json.dumps({"query": query, "variables": variables or {}}).encode()
    req = urllib.request.Request("https://api.github.com/graphql", data=body, headers={
        "Content-Type": "application/json",
        "User-Agent": "chu0119-profile-bot"
    })
    if TOKEN:
        req.add_header("Authorization", f"Bearer {TOKEN}")
    with urllib.request.urlopen(req, timeout=30) as r:
        payload = json.load(r)
    errors = payload.get("errors") or []
    if errors:
        # Error details can contain private resource names when a broad token is
        # used, so publish only the count in workflow logs.
        raise RuntimeError(f"GraphQL request failed with {len(errors)} error(s)")
    data = payload.get("data")
    if not isinstance(data, dict):
        raise RuntimeError("GraphQL request returned no data")
    return data


def normalize_stats(user):
    """Normalize the public profile data used by the SVG renderers."""
    public_repositories = user.get("publicRepositories") or {}
    source_repositories = user.get("sourceRepositories") or {}
    nodes = source_repositories.get("nodes") or []
    repos = [repo for repo in nodes if repo]

    lang_counts = {}
    for repo in repos:
        language = repo.get("primaryLanguage")
        if language and language.get("name"):
            name = language["name"]
            lang_counts[name] = lang_counts.get(name, 0) + 1

    return {
        "repos": public_repositories.get("totalCount", 0) or 0,
        "source_repos": source_repositories.get("totalCount", 0) or 0,
        "active_repos": sum(not repo.get("isArchived", False) for repo in repos),
        "stars": sum(repo.get("stargazerCount", 0) or 0 for repo in repos),
        "forks": sum(repo.get("forkCount", 0) or 0 for repo in repos),
        "languages": len(lang_counts),
        "top_langs": sorted(
            lang_counts.items(), key=lambda item: (-item[1], item[0])
        )[:8],
    }


def fetch_stats():
    """Fetch public repository stats and aggregate source repositories."""
    q = '''
    query($login: String!) {
      user(login: $login) {
        name
        publicRepositories: repositories(
          ownerAffiliations: OWNER,
          privacy: PUBLIC,
          first: 1
        ) {
          totalCount
        }
        sourceRepositories: repositories(
          ownerAffiliations: OWNER,
          privacy: PUBLIC,
          isFork: false,
          first: 100
        ) {
          totalCount
          nodes {
            stargazerCount
            forkCount
            isArchived
            primaryLanguage { name color }
          }
        }
      }
    }
    '''
    return normalize_stats(gql(q, {"login": USER})["user"])


def svg_stats(stats):
    """Render a compact engineering-signal panel."""
    metrics = [
        ("ORIGINAL REPOS", stats.get("source_repos", 0)),
        ("ACTIVE REPOS", stats.get("active_repos", 0)),
        ("LANGUAGES", stats.get("languages", 0)),
        ("FEATURED PROJECTS", 6),
    ]
    metric_svg = []
    for index, (label, value) in enumerate(metrics):
        x = 18 + index * 174
        accent = CYAN if index % 2 == 0 else MAGENTA
        metric_svg.append(f'''
  <rect x="{x}" y="66" width="162" height="66" rx="10" fill="{PANEL}" stroke="{accent}" stroke-opacity="0.28"/>
  <text x="{x + 14}" y="91" font-family="Consolas,Menlo,monospace" font-size="9" letter-spacing="1.2" fill="{MUTED}">{svg_text(label)}</text>
  <text x="{x + 14}" y="118" font-family="Segoe UI,Arial,sans-serif" font-size="20" font-weight="700" fill="{TEXT}">{svg_text(value)}</text>''')

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="720" height="150" viewBox="0 0 720 150" role="img" aria-labelledby="title desc">
  <title id="title">Engineering Signal</title>
  <desc id="desc">Public GitHub collaboration metrics for xingchuan</desc>
  <defs>
    <linearGradient id="signalHeader" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%" stop-color="{CYAN}"/>
      <stop offset="65%" stop-color="{BLUE}"/>
      <stop offset="100%" stop-color="{MAGENTA}"/>
    </linearGradient>
  </defs>
  <rect width="720" height="150" rx="16" fill="{BG}"/>
  <path d="M18 48 H702" stroke="#17364A"/>
  <rect x="18" y="18" width="4" height="18" rx="2" fill="url(#signalHeader)"/>
  <text x="34" y="31" font-family="Consolas,Menlo,monospace" font-size="13" font-weight="700" letter-spacing="1.6" fill="{CYAN}">ENGINEERING SIGNAL / 工程数据</text>
  <text x="702" y="31" text-anchor="end" font-family="Segoe UI,Arial,sans-serif" font-size="10" fill="{MUTED}">公开仓库由 GitHub API 每日更新</text>
{''.join(metric_svg)}
</svg>'''


def svg_langs(stats):
    """Render public source-repository language distribution."""
    langs = stats.get("top_langs") or []
    colors = {
        "Python": "#3572A5", "TypeScript": "#3178C6", "JavaScript": "#F7DF1E",
        "PHP": "#4F5D95", "HTML": "#E34C26", "CSS": "#563D7C", "Shell": "#89E051",
        "PowerShell": "#012456", "C": "#555555", "C++": "#F34B7D", "Go": "#00ADD8",
        "Rust": "#DEA584", "Java": "#B07219", "Ruby": "#701516",
        "Elixir": "#6E4A7E", "Swift": "#F05138", "Kotlin": "#A97BFF",
    }
    default_colors = [MAGENTA, CYAN, "#8B5CF6", "#27C93F", "#F59E0B"]

    if not langs:
        body = f'''
  <rect x="18" y="62" width="684" height="58" rx="10" fill="{PANEL}" stroke="#17364A"/>
  <text x="360" y="87" text-anchor="middle" font-family="Segoe UI,Arial,sans-serif" font-size="13" fill="{TEXT}">暂无语言数据</text>
  <text x="360" y="106" text-anchor="middle" font-family="Consolas,Menlo,monospace" font-size="9" letter-spacing="1.4" fill="{MUTED}">NO PUBLIC LANGUAGE DATA</text>'''
    else:
        total = sum(count for _, count in langs) or 1
        x_offset = 18.0
        bar_width = 684.0
        segments = []
        for index, (name, count) in enumerate(langs):
            width = count / total * bar_width
            color = colors.get(name, default_colors[index % len(default_colors)])
            segments.append(
                f'  <rect x="{x_offset:.2f}" y="58" width="{width:.2f}" '
                f'height="10" fill="{color}" rx="3"/>'
            )
            x_offset += width

        legend = []
        for index, (name, count) in enumerate(langs[:5]):
            x = 18 + index * 137
            color = colors.get(name, default_colors[index % len(default_colors)])
            percentage = count / total * 100
            legend.append(f'''
  <circle cx="{x + 4}" cy="97" r="4" fill="{color}"/>
  <text x="{x + 14}" y="95" font-family="Segoe UI,Arial,sans-serif" font-size="10" font-weight="600" fill="{TEXT}">{svg_text(name)}</text>
  <text x="{x + 14}" y="111" font-family="Consolas,Menlo,monospace" font-size="9" fill="{MUTED}">{percentage:.1f}%</text>''')
        body = "\n".join(segments + legend)

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="720" height="140" viewBox="0 0 720 140" role="img" aria-labelledby="title desc">
  <title id="title">Languages and Tooling</title>
  <desc id="desc">Primary languages across public source repositories</desc>
  <rect width="720" height="140" rx="16" fill="{BG}"/>
  <rect x="18" y="18" width="4" height="18" rx="2" fill="{MAGENTA}"/>
  <text x="34" y="31" font-family="Consolas,Menlo,monospace" font-size="13" font-weight="700" letter-spacing="1.6" fill="{CYAN}">LANGUAGES / 主要语言</text>
  <text x="702" y="31" text-anchor="end" font-family="Segoe UI,Arial,sans-serif" font-size="10" fill="{MUTED}">PUBLIC SOURCE REPOSITORIES</text>
  <path d="M18 46 H702" stroke="#17364A"/>
{body}
</svg>'''


def _star_points(cx, cy, r_out=7.0, r_in=2.9):
    pts = []
    for i in range(10):
        ang = math.radians(-90 + i * 36)
        r = r_out if i % 2 == 0 else r_in
        pts.append(f"{cx + r * math.cos(ang):.1f},{cy + r * math.sin(ang):.1f}")
    return " ".join(pts)


def _achievement_icon(kind, cx, cy):
    """Self-drawn vector icons — no emoji, viewer-font independent."""
    if kind == "stars":
        return f'  <polygon points="{_star_points(cx, cy)}" fill="#FFC94D"/>\n'
    if kind == "repos":
        return (f'  <rect x="{cx-6}" y="{cy-6}" width="12" height="12" rx="2" '
                f'fill="none" stroke="{CYAN}" stroke-width="1.5"/>\n'
                f'  <line x1="{cx-6}" y1="{cy-2}" x2="{cx+6}" y2="{cy-2}" '
                f'stroke="{CYAN}" stroke-width="1.5"/>\n')
    if kind == "forks":
        return (f'  <path d="M{cx-5} {cy-6} V{cy+1} Q{cx-5} {cy+6} {cx} {cy+6} '
                f'H{cx+5} V{cy-1}" fill="none" stroke="{MAGENTA}" stroke-width="1.5"/>\n'
                f'  <circle cx="{cx-5}" cy="{cy-7}" r="2.5" fill="{MAGENTA}"/>\n'
                f'  <circle cx="{cx+5}" cy="{cy-3}" r="2.5" fill="{MAGENTA}"/>\n')
    # languages: mini ascending bar chart
    bars = ""
    for i, h in enumerate((6, 10, 14)):
        bx = cx - 7 + i * 6
        bars += f'  <rect x="{bx}" y="{cy+7-h}" width="4" height="{h}" fill="#27C93F" rx="1"/>\n'
    return bars


def svg_achievements(stats):
    """Render the primary open-source signal panel using vector icons."""
    tiles = [
        ("repos", str(stats.get("repos", 0)), "PUBLIC REPOS"),
        ("stars", str(stats.get("stars", 0)), "TOTAL STARS"),
        ("forks", str(stats.get("forks", 0)), "TOTAL FORKS"),
        ("languages", str(stats.get("languages", 0)), "LANGUAGES"),
    ]

    W, H = 720, 176
    TILE_Y, TILE_W, TILE_H, GAP = 66, 163, 92, 12
    tiles_svg = ""
    for i, (kind, value, label) in enumerate(tiles):
        tx = 16 + i * (TILE_W + GAP)
        stroke = CYAN if i % 2 == 0 else MAGENTA
        cx = tx + TILE_W // 2
        tiles_svg += f'''  <rect x="{tx}" y="{TILE_Y}" width="{TILE_W}" height="{TILE_H}" rx="8" fill="#161b22" stroke="{stroke}" stroke-opacity="0.55"/>
{_achievement_icon(kind, cx, TILE_Y + 24)}  <text x="{cx}" y="{TILE_Y + 59}" text-anchor="middle" font-family="Segoe UI,Arial,sans-serif" font-size="21" font-weight="700" fill="{TEXT}">{svg_text(value)}</text>
  <text x="{cx}" y="{TILE_Y + 80}" text-anchor="middle" font-family="Consolas,Menlo,monospace" font-size="9" letter-spacing="1.5" fill="{MUTED}">{svg_text(label)}</text>
'''

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-labelledby="title desc">
  <title id="title">Open Source Signal</title>
  <desc id="desc">Public repositories, earned stars, forks, and primary languages</desc>
  <defs>
    <linearGradient id="agrad" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%" stop-color="{CYAN}"/>
      <stop offset="100%" stop-color="{MAGENTA}"/>
    </linearGradient>
  </defs>
  <rect width="{W}" height="{H}" fill="{BG}" rx="16"/>
  <rect x="18" y="18" width="4" height="20" rx="2" fill="url(#agrad)"/>
  <text x="34" y="32" font-family="Consolas,Menlo,monospace" font-size="14" font-weight="700" letter-spacing="2" fill="{CYAN}">OPEN SOURCE SIGNAL</text>
  <text x="702" y="32" text-anchor="end" font-family="Consolas,Menlo,monospace" font-size="9" letter-spacing="1.2" fill="{MUTED}">LIVE / GITHUB API</text>
  <path d="M18 50 H702" stroke="#17364A"/>
{tiles_svg}</svg>'''


def main():
    print(f"Fetching data for {USER}...")
    stats = fetch_stats()
    print(
        f"  public_repos={stats['repos']} source_repos={stats['source_repos']} "
        f"active_repos={stats['active_repos']} stars={stats['stars']} "
        f"forks={stats['forks']} languages={stats['languages']}"
    )

    outputs = {
        "stats.svg": svg_stats(stats),
        "langs.svg": svg_langs(stats),
        "achievements.svg": svg_achievements(stats),
    }
    for filename, content in outputs.items():
        try:
            ET.fromstring(content)
        except ET.ParseError as exc:
            raise ValueError(f"Generated invalid SVG: {filename}") from exc

    os.makedirs(OUT_DIR, exist_ok=True)
    for filename, content in outputs.items():
        path = os.path.join(OUT_DIR, filename)
        with open(path, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(content)
        print(f"  wrote {path}")

    print("Done!")


if __name__ == "__main__":
    main()
