#!/usr/bin/env python3
"""Generate profile stats SVGs using GitHub API. No external service dependencies."""
import json
import math
import os
import urllib.request
from datetime import datetime, timezone, timedelta

USER = "chu0119"
TOKEN = os.environ.get("GH_TOKEN", os.environ.get("GITHUB_TOKEN", ""))
OUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets")


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
        return json.load(r)["data"]


def fetch_stats():
    """Fetch user stats via GraphQL."""
    q = '''
    query($login: String!) {
      user(login: $login) {
        name
        repositories(ownerAffiliations: OWNER, isFork: false, first: 100) {
          totalCount
          nodes { stargazerCount primaryLanguage { name color } }
        }
        pullRequests(first: 1) { totalCount }
        issues(first: 1) { totalCount }
        contributionsCollection {
          contributionCalendar { totalContributions }
        }
      }
    }
    '''
    data = gql(q, {"login": USER})["user"]
    repos = data["repositories"]
    total_stars = sum(r["stargazerCount"] for r in repos["nodes"])
    lang_counts = {}
    for r in repos["nodes"]:
        pl = r.get("primaryLanguage")
        if pl:
            lang_counts[pl["name"]] = lang_counts.get(pl["name"], 0) + 1
    # sort by count desc
    top_langs = sorted(lang_counts.items(), key=lambda x: -x[1])[:8]
    return {
        "repos": repos["totalCount"],
        "stars": total_stars,
        "prs": data["pullRequests"]["totalCount"],
        "issues": data["issues"]["totalCount"],
        "contributions": data["contributionsCollection"]["contributionCalendar"]["totalContributions"],
        "top_langs": top_langs,
    }


def fetch_streak():
    """Calculate current and longest commit streak."""
    q = '''
    query($login: String!) {
      user(login: $login) {
        contributionsCollection {
          contributionCalendar {
            weeks {
              contributionDays { date contributionCount }
            }
          }
        }
      }
    }
    '''
    data = gql(q, {"login": USER})["user"]
    days = []
    for w in data["contributionsCollection"]["contributionCalendar"]["weeks"]:
        for d in w["contributionDays"]:
            days.append((d["date"], d["contributionCount"]))

    # Calculate streaks (from today backwards)
    current_streak = 0
    longest_streak = 0
    streak = 0
    streak_start = None
    current_start = None
    found_current = False

    for date_str, count in reversed(days):
        if count > 0:
            streak += 1
            if not found_current:
                current_streak = streak
                current_start = date_str
            if streak > longest_streak:
                longest_streak = streak
                streak_start = date_str
        else:
            if not found_current and current_streak > 0:
                found_current = True
            streak = 0

    return {
        "current": current_streak,
        "longest": longest_streak,
        "total": sum(c for _, c in days),
    }


def svg_stats(stats, streak_data):
    """Generate the main stats card SVG."""
    items = [
        ("📦 Repositories", str(stats["repos"])),
        ("⭐ Total Stars", str(stats["stars"])),
        ("🔀 Pull Requests", str(stats["prs"])),
        ("🐛 Issues", str(stats["issues"])),
        ("📊 Contributions", str(stats["contributions"])),
        ("🔥 Current Streak", f"{streak_data['current']} days"),
        ("🏆 Longest Streak", f"{streak_data['longest']} days"),
    ]

    card_h = 50 + len(items) * 42 + 20
    card_w = 480

    rows = ""
    for i, (label, value) in enumerate(items):
        y = 50 + i * 42
        fill = "#161b22" if i % 2 == 0 else "#0d1117"
        rows += f'''
  <rect x="0" y="{y}" width="{card_w}" height="42" fill="{fill}" rx="4"/>
  <text x="16" y="{y+27}" font-family="Segoe UI,Helvetica,Arial,sans-serif" font-size="14" fill="#8b949e">{label}</text>
  <text x="{card_w-16}" y="{y+27}" font-family="Segoe UI,Helvetica,Arial,sans-serif" font-size="14" fill="#c9d1d9" font-weight="600" text-anchor="end">{value}</text>'''

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{card_w}" height="{card_h}" viewBox="0 0 {card_w} {card_h}">
  <defs>
    <linearGradient id="headerGrad" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%" stop-color="#00E5FF"/>
      <stop offset="100%" stop-color="#FF2E97"/>
    </linearGradient>
  </defs>
  <rect width="{card_w}" height="{card_h}" fill="#0d1117" rx="12"/>
  <rect width="{card_w}" height="44" rx="12" fill="url(#headerGrad)" opacity="0.15"/>
  <text x="16" y="29" font-family="Segoe UI,Helvetica,Arial,sans-serif" font-size="16" font-weight="700" fill="#00E5FF">📊 GitHub Stats</text>
{rows}
</svg>'''
    return svg


def svg_langs(stats):
    """Generate the language breakdown SVG."""
    langs = stats["top_langs"]
    if not langs:
        return "<svg xmlns='http://www.w3.org/2000/svg' width='400' height='120'><text x='16' y='60' fill='#8b949e'>No languages found</text></svg>"

    total = sum(c for _, c in langs)
    colors = {
        "Python": "#3572A5", "TypeScript": "#3178C6", "JavaScript": "#F7DF1E",
        "PHP": "#4F5D95", "HTML": "#E34C26", "CSS": "#563D7C", "Shell": "#89E051",
        "PowerShell": "#012456", "C": "#555555", "C++": "#F34B7D", "Go": "#00ADD8",
        "Rust": "#DEA584", "Java": "#B07219", "Ruby": "#701516",
        "Elixir": "#6E4A7E", "Swift": "#F05138", "Kotlin": "#A97BFF",
    }
    default_colors = ["#FF2E97", "#00E5FF", "#8B5CF6", "#10B981", "#F59E0B", "#EF4444", "#6366F1", "#EC4899"]

    bar_segments = ""
    x_offset = 16
    bar_w = 400
    for i, (name, count) in enumerate(langs):
        w = max(4, count / total * bar_w)
        color = colors.get(name, default_colors[i % len(default_colors)])
        bar_segments += f'  <rect x="{x_offset}" y="50" width="{w}" height="8" fill="{color}" rx="2"/>\n'
        x_offset += w

    legend = ""
    legend_x = 16
    legend_y = 82
    for i, (name, count) in enumerate(langs[:5]):
        color = colors.get(name, default_colors[i % len(default_colors)])
        pct = f"{count / total * 100:.1f}%"
        legend += f'''  <circle cx="{legend_x}" cy="{legend_y}" r="4" fill="{color}"/>
  <text x="{legend_x+8}" y="{legend_y+4}" font-family="Segoe UI,Helvetica,Arial,sans-serif" font-size="11" fill="#c9d1d9">{name} {pct}</text>\n'''
        legend_x += len(name) * 7 + 50
        if legend_x > 350:
            legend_x = 16
            legend_y += 22

    card_h = legend_y + 20
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="440" height="{card_h}" viewBox="0 0 440 {card_h}">
  <defs>
    <linearGradient id="headerGrad2" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%" stop-color="#00E5FF"/>
      <stop offset="100%" stop-color="#FF2E97"/>
    </linearGradient>
  </defs>
  <rect width="440" height="{card_h}" fill="#0d1117" rx="12"/>
  <rect width="440" height="44" rx="12" fill="url(#headerGrad2)" opacity="0.15"/>
  <text x="16" y="29" font-family="Segoe UI,Helvetica,Arial,sans-serif" font-size="16" font-weight="700" fill="#00E5FF">💻 Top Languages</text>
{bar_segments}{legend}</svg>'''
    return svg


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
                f'fill="none" stroke="#00E5FF" stroke-width="1.5"/>\n'
                f'  <line x1="{cx-6}" y1="{cy-2}" x2="{cx+6}" y2="{cy-2}" '
                f'stroke="#00E5FF" stroke-width="1.5"/>\n')
    if kind == "streak":
        pts = (f"{cx+2},{cy-8} {cx-4},{cy+1} {cx-0.5},{cy+1} "
               f"{cx-2},{cy+8} {cx+4},{cy-1} {cx+0.5},{cy-1}")
        return f'  <polygon points="{pts}" fill="#FF2E97"/>\n'
    # contrib: mini ascending bar chart
    bars = ""
    for i, h in enumerate((6, 10, 14)):
        bx = cx - 7 + i * 6
        bars += f'  <rect x="{bx}" y="{cy+7-h}" width="4" height="{h}" fill="#27C93F" rx="1"/>\n'
    return bars


def svg_achievements(stats, streak_data):
    """Terminal-style 'ACHIEVEMENTS UNLOCKED' panel."""
    def fmt(n):
        return f"{n:,}" if n >= 1000 else str(n)

    tiles = [
        ("stars", str(stats["stars"]), "TOTAL STARS"),
        ("repos", str(stats["repos"]), "REPOSITORIES"),
        ("streak", f"{streak_data['current']} DAYS", f"LONGEST {streak_data['longest']}"),
        ("contrib", fmt(stats["contributions"]), "CONTRIBUTIONS"),
    ]

    W, H = 720, 164
    TILE_Y, TILE_W, TILE_H, GAP = 58, 163, 90, 12
    tiles_svg = ""
    for i, (kind, value, label) in enumerate(tiles):
        tx = 16 + i * (TILE_W + GAP)
        stroke = "#00E5FF" if i % 2 == 0 else "#FF2E97"
        cx = tx + TILE_W // 2
        tiles_svg += f'''  <rect x="{tx}" y="{TILE_Y}" width="{TILE_W}" height="{TILE_H}" rx="8" fill="#161b22" stroke="{stroke}" stroke-opacity="0.55"/>
{_achievement_icon(kind, cx, TILE_Y + 24)}  <text x="{cx}" y="{TILE_Y + 56}" text-anchor="middle" font-family="Segoe UI,Helvetica,Arial,sans-serif" font-size="21" font-weight="700" fill="#c9d1d9">{value}</text>
  <text x="{cx}" y="{TILE_Y + 76}" text-anchor="middle" font-family="Consolas,Menlo,monospace" font-size="9" letter-spacing="1.5" fill="#8b949e">{label}</text>
'''

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
  <defs>
    <linearGradient id="agrad" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%" stop-color="#00E5FF"/>
      <stop offset="100%" stop-color="#FF2E97"/>
    </linearGradient>
  </defs>
  <rect width="{W}" height="{H}" fill="#0d1117" rx="12"/>
  <rect width="{W}" height="44" rx="12" fill="url(#agrad)" opacity="0.15"/>
  <text x="16" y="29" font-family="Consolas,Menlo,monospace" font-size="15" font-weight="700" letter-spacing="2" fill="#FF2E97">ACHIEVEMENTS UNLOCKED</text>
{tiles_svg}</svg>'''


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    print(f"Fetching data for {USER}...")
    stats = fetch_stats()
    streak_data = fetch_streak()
    print(f"  repos={stats['repos']} stars={stats['stars']} prs={stats['prs']} issues={stats['issues']}")
    print(f"  contributions={stats['contributions']} streak_current={streak_data['current']} streak_longest={streak_data['longest']}")

    # Write stats card
    p = os.path.join(OUT_DIR, "stats.svg")
    with open(p, "w", encoding="utf-8") as f:
        f.write(svg_stats(stats, streak_data))
    print(f"  wrote {p}")

    # Write langs card
    p = os.path.join(OUT_DIR, "langs.svg")
    with open(p, "w", encoding="utf-8") as f:
        f.write(svg_langs(stats))
    print(f"  wrote {p}")

    # Write achievements panel
    p = os.path.join(OUT_DIR, "achievements.svg")
    with open(p, "w", encoding="utf-8") as f:
        f.write(svg_achievements(stats, streak_data))
    print(f"  wrote {p}")

    # Write streak badge (reuse streak_data in stats card, no separate file needed)
    # But save streak_data as JSON for reference
    p = os.path.join(OUT_DIR, "streak.json")
    with open(p, "w") as f:
        json.dump(streak_data, f, indent=2)

    print("Done!")


if __name__ == "__main__":
    main()
