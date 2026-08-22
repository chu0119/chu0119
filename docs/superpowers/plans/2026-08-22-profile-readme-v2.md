# GitHub Profile README v2 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Expand and polish the chu0119 GitHub profile README per the approved spec `docs/superpowers/specs/2026-08-22-profile-readme-v2-design.md` — new animated banner, 6-project card arsenal, self-drawn achievements panel, focus & contact sections, bilingual copy.

**Architecture:** Reuse the existing zero-external-dependency pipeline: `scripts/generate_stats.py` (run daily by `.github/workflows/generate-stats.yml`) gains a `render_achievements()` step producing `assets/achievements.svg`; `assets/banner.svg` is hand-crafted SMIL-animated SVG; `README.md` is rewritten Markdown referencing these assets.

**Tech Stack:** Python 3.12 (stdlib only), SVG + SMIL animation, GitHub Actions, shields.io badges (already in use), pytest for the new generator tests.

**Working dir:** `D:\xiangmu\chu0119\profile-repo` (clone of `chu0119/chu0119`). All paths below are relative to it.

## Global Constraints

- Palette (verbatim): neon cyan `#00E5FF`, magenta `#FF2E97`, background `#0D1117` / tile `#161b22`, muted `#8B949E`, text `#C9D1D9`, green accent `#27C93F`.
- Animations only inside SVG files (SMIL `<animate>`); GitHub README forbids CSS animation.
- New sections add NO new external services (shields.io badges already in use are allowed).
- Copy: English primary with Chinese counterpart lines (双语).
- Contact email: `chu0119@foxmail.com`.
- Achievement panel uses self-drawn vector icons, NOT emoji (viewer-font risk noted in spec).
- Do NOT modify `scripts/update_activity.py`, `.github/workflows/update-activity.yml`, `.github/workflows/generate-stats.yml` (its `paths: ['scripts/generate_stats.py']` trigger already covers our change).
- Preserve exactly: `<!-- BEGIN ACTIVITY -->` / `<!-- END ACTIVITY -->` markers in README.
- Environment is Windows; use Bash tool syntax for shell steps; `python` and `gh` CLI are available and authenticated.

---

### Task 1: Achievements panel generator (`svg_achievements`) — TDD

**Files:**
- Modify: `scripts/generate_stats.py` (add `import math`; add functions after `svg_langs`, line ~213; wire into `main()`)
- Test: `tests/test_generate_stats.py` (create)

**Interfaces:**
- Consumes: existing `fetch_stats()` → dict with keys `repos, stars, prs, issues, contributions, top_langs`; existing `fetch_streak()` → dict with keys `current, longest, total` (both already called in `main()`).
- Produces: `svg_achievements(stats: dict, streak_data: dict) -> str` (SVG markup); writes `assets/achievements.svg`. Later tasks reference the file `assets/achievements.svg` only.

- [ ] **Step 1: Write the failing test**

Create `tests/test_generate_stats.py`:

```python
import os
import sys

import defusedxml.ElementTree as ET

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

from generate_stats import svg_achievements  # noqa: E402

STATS = {"repos": 66, "stars": 72, "prs": 3, "issues": 5,
         "contributions": 1234, "top_langs": [("Python", 10)]}
STREAK = {"current": 2, "longest": 5, "total": 548}


def test_output_is_valid_xml():
    ET.fromstring(svg_achievements(STATS, STREAK))


def test_renders_all_four_tiles():
    s = svg_achievements(STATS, STREAK)
    assert s.count('rx="8"') == 4


def test_embeds_real_values():
    s = svg_achievements(STATS, STREAK)
    assert ">72</text>" in s
    assert ">66</text>" in s
    assert "1,234" in s          # thousands separator kicks in >= 1000
    assert "LONGEST 5" in s
    assert "TOTAL STARS" in s
    assert "CONTRIBUTIONS" in s


def test_ascii_only_vector_icons():
    s = svg_achievements(STATS, STREAK)
    assert s.isascii()


def test_small_numbers_have_no_separator():
    s = svg_achievements({**STATS, "contributions": 999}, STREAK)
    assert ">999</text>" in s
    assert "1,234" not in s
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd /d/xiangmu/chu0119/profile-repo && python -m pytest --version >/dev/null 2>&1 || python -m pip install pytest defusedxml
python -m pytest tests/ -v
```

Expected: FAIL / collection error with `ImportError: cannot import name 'svg_achievements'`.

- [ ] **Step 3: Write minimal implementation**

In `scripts/generate_stats.py`:

Add to imports (line 3 area):

```python
import math
```

Add after `svg_langs()` (before `def main():`):

```python
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
        bars += f'  <rect x="{bx}" y="{cy+7-h}" width="4" height="{h}" fill="#10B981" rx="1"/>\n'
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
```

In `main()`, after the langs card block (after `print(f"  wrote {p}")` for `langs.svg`), insert:

```python
    # Write achievements panel
    p = os.path.join(OUT_DIR, "achievements.svg")
    with open(p, "w", encoding="utf-8") as f:
        f.write(svg_achievements(stats, streak_data))
    print(f"  wrote {p}")
```

- [ ] **Step 4: Run test to verify it passes**

```bash
cd /d/xiangmu/chu0119/profile-repo && python -m pytest tests/ -v
```

Expected: 5 passed.

- [ ] **Step 5: Generate real asset locally**

```bash
cd /d/xiangmu/chu0119/profile-repo && GH_TOKEN=$(gh auth token) python scripts/generate_stats.py
```

Expected output ends with `wrote ...\assets\achievements.svg` and `Done!`. Confirm `assets/achievements.svg` exists and starts with `<svg`.

- [ ] **Step 6: Commit**

```bash
cd /d/xiangmu/chu0119/profile-repo && git add scripts/generate_stats.py tests/test_generate_stats.py assets/
git commit -m "feat: add self-drawn achievements panel SVG generator"
```

(Note: `stats.svg`/`langs.svg` may also refresh — include them; they are generated artifacts.)

---

### Task 2: Animated banner v2

**Files:**
- Modify: `assets/banner.svg` (full rewrite)

**Interfaces:**
- Consumes: nothing.
- Produces: `assets/banner.svg` (same filename, referenced by README Task 3). Canvas grows 120→150 px tall; width unchanged at 720.

Animation design: 9-second looping terminal session, lines appear cumulatively then the whole block resets. Uses the same SMIL technique as v1 (proven to work on GitHub).

- [ ] **Step 1: Rewrite `assets/banner.svg` with this exact content**

```xml
<svg xmlns="http://www.w3.org/2000/svg" width="720" height="150" viewBox="0 0 720 150" role="img" aria-label="terminal banner">
  <defs>
    <filter id="glow" x="-50%" y="-50%" width="200%" height="200%">
      <feGaussianBlur stdDeviation="3" result="blur"/>
      <feMerge>
        <feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>
    <linearGradient id="neon" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%" stop-color="#00E5FF"/>
      <stop offset="100%" stop-color="#FF2E97"/>
    </linearGradient>
  </defs>

  <!-- terminal window -->
  <rect x="2" y="2" width="716" height="146" rx="10" fill="#0D1117" stroke="url(#neon)" stroke-width="2" filter="url(#glow)"/>

  <!-- title bar -->
  <line x1="2" y1="28" x2="718" y2="28" stroke="url(#neon)" stroke-width="1" opacity="0.6"/>
  <circle cx="20" cy="15" r="5" fill="#FF5F56"/>
  <circle cx="38" cy="15" r="5" fill="#FFBD2E"/>
  <circle cx="56" cy="15" r="5" fill="#27C93F"/>
  <text x="360" y="19" text-anchor="middle" font-family="monospace" font-size="11" fill="#8B949E">visitor@chu0119: ~/profile — zsh</text>

  <!-- looping session: whoami -> nmap -> exploit -> result, 9s cycle -->
  <g font-family="Consolas,Menlo,monospace" font-size="15">
    <text x="20" y="56">
      <tspan fill="#FF2E97">➜</tspan>  <tspan fill="#00E5FF">~/</tspan> <tspan fill="#C9D1D9">whoami</tspan>
      <animate attributeName="opacity" values="0;1;1;0;0" keyTimes="0;0.06;0.85;0.92;1" dur="9s" repeatCount="indefinite"/>
    </text>
    <text x="20" y="78">
      <tspan fill="#FF2E97">➜</tspan>  <tspan fill="#00E5FF">~/</tspan> <tspan fill="#C9D1D9">nmap -sV --top-ports 1000 10.0.0.0/24</tspan>
      <animate attributeName="opacity" values="0;0;1;1;0;0" keyTimes="0;0.24;0.32;0.85;0.92;1" dur="9s" repeatCount="indefinite"/>
    </text>
    <text x="20" y="100">
      <tspan fill="#FF2E97">➜</tspan>  <tspan fill="#00E5FF">~/</tspan> <tspan fill="#C9D1D9">./exploit --mode stealth_</tspan>
      <animate attributeName="opacity" values="0;0;1;1;0;0" keyTimes="0;0.46;0.54;0.85;0.92;1" dur="9s" repeatCount="indefinite"/>
    </text>
    <text x="20" y="130" font-size="17" font-weight="bold" fill="url(#neon)" filter="url(#glow)">
      <tspan fill="#27C93F">[+]</tspan> <tspan>access granted · security research in progress</tspan>
      <animate attributeName="opacity" values="0;0;1;1;0;0" keyTimes="0;0.64;0.72;0.85;0.92;1" dur="9s" repeatCount="indefinite"/>
    </text>
  </g>
</svg>
```

(The trailing `_` on the exploit line doubles as the blinking-prompt feel without fragile cursor positioning.)

- [ ] **Step 2: Validate XML**

```bash
cd /d/xiangmu/chu0119/profile-repo && python -c "import xml.etree.ElementTree as ET; ET.parse('assets/banner.svg'); print('banner.svg OK')"
```

Expected: `banner.svg OK`.

- [ ] **Step 3: Visual spot-check**

Open `assets/banner.svg` in the default browser (animation should cycle: three commands type in sequence, green `[+]` result appears, all fade, restart).

```bash
start "" "D:\xiangmu\chu0119\profile-repo\assets\banner.svg" 2>/dev/null || cmd.exe /c start "" "D:\xiangmu\chu0119\profile-repo\assets\banner.svg"
```

If browser check is impractical in-session, rely on Step 2 plus identical-to-v1 SMIL technique; flag in the final report that the user should eyeball the live page.

- [ ] **Step 4: Commit**

```bash
cd /d/xiangmu/chu0119/profile-repo && git add assets/banner.svg
git commit -m "feat: banner v2 — multi-command looping terminal animation"
```

---

### Task 3: README v2 rewrite (bilingual)

**Files:**
- Modify: `README.md` (full rewrite)

**Interfaces:**
- Consumes: `assets/banner.svg`, `assets/stats.svg`, `assets/langs.svg`, `assets/achievements.svg` (from Tasks 1–2); preserves `<!-- BEGIN ACTIVITY -->`/`<!-- END ACTIVITY -->` block consumed by `scripts/update_activity.py`.
- Produces: final profile README.

- [ ] **Step 1: Replace `README.md` with this exact content**

````markdown
<p align="center">
  <img src="assets/banner.svg" alt="terminal banner" width="720"/>
</p>

```text
$ cat identity.txt
```

> **Security Researcher & Tool Builder** — focused on offensive security,
> threat intelligence, and AI-powered automation.
> Building tools that make recon faster and reporting painless.
>
> **安全研究员 & 工具建造者** —— 专注攻防渗透、威胁情报与 AI 自动化，
> 让信息收集更快、报告输出更省心。

```text
$ cat focus.txt
```

> 🎯 **Bug Hunting** — EDUSRC & enterprise SRC · 教育 SRC 与企业 SRC 漏洞挖掘中
>
> 🛠 **Tool Building** — recon & automation tooling · 持续打磨侦察与自动化工具链
>
> 🤖 **AI × Security** — LLM-driven security workflows · 探索大模型驱动的安全工作流

```text
$ ls ~/arsenal --sort=stars
```

## 🔫 Featured Arsenal · 精选武器库

<table>
<tr>
<td width="50%">

[🔧 **fscan-toolkit**](https://github.com/chu0119/fscan-toolkit)&nbsp;
[![stars](https://img.shields.io/github/stars/chu0119/fscan-toolkit?style=flat-square&color=00E5FF&label=%E2%AD%90)](https://github.com/chu0119/fscan-toolkit)&nbsp;
![HTML](https://img.shields.io/badge/HTML-E34C26?style=flat-square&logo=html5&logoColor=white)

*GUI suite for fscan — command builder + report parser, zero-dependency.*

fscan 图形化套件：命令生成器 + 报告解析器。

</td>
<td width="50%">

[🛡 **zhidun**](https://github.com/chu0119/zhidun)&nbsp;
[![stars](https://img.shields.io/github/stars/chu0119/zhidun?style=flat-square&color=00E5FF&label=%E2%AD%90)](https://github.com/chu0119/zhidun)&nbsp;
![TypeScript](https://img.shields.io/badge/TypeScript-3178C6?style=flat-square&logo=typescript&logoColor=white)

*AI-driven web log security analyzer — cyberpunk-themed threat hunting.*

星川智盾：AI 驱动的网站日志安全分析系统。

</td>
</tr>
<tr>
<td width="50%">

[🌲 **DarkForest-Hunter**](https://github.com/chu0119/DarkForest-Hunter)&nbsp;
[![stars](https://img.shields.io/github/stars/chu0119/DarkForest-Hunter?style=flat-square&color=00E5FF&label=%E2%AD%90)](https://github.com/chu0119/DarkForest-Hunter)&nbsp;
![Python](https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white)

*DeepSeek API-key security scanner — 14 sources, 238 queries.*

黑暗森林猎人：DeepSeek API 密钥泄露扫描器。

</td>
<td width="50%">

[🛰 **xingchuan-ti**](https://github.com/chu0119/xingchuan-ti)&nbsp;
[![stars](https://img.shields.io/github/stars/chu0119/xingchuan-ti?style=flat-square&color=00E5FF&label=%E2%AD%90)](https://github.com/chu0119/xingchuan-ti)&nbsp;
![TypeScript](https://img.shields.io/badge/TypeScript-3178C6?style=flat-square&logo=typescript&logoColor=white)

*Threat-intel assistant — select IP/domain, multi-source weighted verdict.*

星川威胁情报助手：划词识别，多源加权研判。

</td>
</tr>
<tr>
<td width="50%">

[📡 **tg-monitor-v2**](https://github.com/chu0119/tg-monitor-v2)&nbsp;
[![stars](https://img.shields.io/github/stars/chu0119/tg-monitor-v2?style=flat-square&color=00E5FF&label=%E2%AD%90)](https://github.com/chu0119/tg-monitor-v2)&nbsp;
![Python](https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white)

*Telegram group monitoring — keyword alerts, analytics & dashboard.*

听风追影：TG 群组实时监控告警与可视化大屏。

</td>
<td width="50%">

[🎯 **edusrc-hunter**](https://github.com/chu0119/edusrc-hunter)&nbsp;
[![stars](https://img.shields.io/github/stars/chu0119/edusrc-hunter?style=flat-square&color=00E5FF&label=%E2%AD%90)](https://github.com/chu0119/edusrc-hunter)&nbsp;
![Shell](https://img.shields.io/badge/Shell-89E051?style=flat-square&logo=gnu-bash&logoColor=black)

*EDUSRC hunting skill — Burp-MCP driven recon → scan → report.*

教育 SRC 漏洞挖掘技能：Burp MCP 全流程驱动。

</td>
</tr>
</table>

```text
$ sudo ./load_modules.sh
```

## 🛠 Tech Stack

**Languages**
![Python](https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white)
![TypeScript](https://img.shields.io/badge/TypeScript-3178C6?style=flat-square&logo=typescript&logoColor=white)
![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?style=flat-square&logo=javascript&logoColor=black)
![PHP](https://img.shields.io/badge/PHP-777BB4?style=flat-square&logo=php&logoColor=white)
![PowerShell](https://img.shields.io/badge/PowerShell-5391FE?style=flat-square&logo=powershell&logoColor=white)

**Security**
![Burp Suite](https://img.shields.io/badge/Burp_Suite-FF6633?style=flat-square&logo=burpsuite&logoColor=white)
![fscan](https://img.shields.io/badge/fscan-inner--network--scan-00E5FF?style=flat-square)
![Nmap](https://img.shields.io/badge/Nmap-204E77?style=flat-square&logo=nmap&logoColor=white)
![SRC](https://img.shields.io/badge/EDUSRC-vuln--hunting-FF2E97?style=flat-square)

**AI & Automation**
![LLM Agent](https://img.shields.io/badge/LLM_Agents-auto--pwn-8B5CF6?style=flat-square)
![MCP](https://img.shields.io/badge/MCP-toolchain-10B981?style=flat-square)
![Claude](https://img.shields.io/badge/Claude_Code-paired-191919?style=flat-square&logo=anthropic)

```text
$ ./monitor --live
```

## 📊 Stats & Achievements

> Stats & achievements auto-generated daily by GitHub Actions — zero external service dependency

<p align="center">
  <img src="assets/achievements.svg" alt="achievements"/>
</p>
<p align="center">
  <img src="assets/stats.svg" alt="stats"/>
</p>
<p align="center">
  <img src="assets/langs.svg" alt="langs"/>
</p>

## 📡 Recent Activity · 最近动态

<!-- BEGIN ACTIVITY -->
- ⭐ **1Panel-dev/CordysCRM** — starred it
- ⭐ **nginx/nginx** — starred it
- ⭐ **mickael-kerjean/filestash** — starred it
- ⭐ **xingchuan-ti** — starred it
- 📝 **cloudreve/cloudreve** — issues in it
<!-- END ACTIVITY -->

```text
$ ping me
```

## 📮 Contact · 联系我

<p align="left">
  <a href="mailto:chu0119@foxmail.com"><img src="https://img.shields.io/badge/Email-chu0119%40foxmail.com-00E5FF?style=flat-square&logo=minutemailer&logoColor=white" alt="email"/></a>&nbsp;&nbsp;
  <a href="https://github.com/chu0119"><img src="https://img.shields.io/badge/GitHub-chu0119-181717?style=flat-square&logo=github" alt="github"/></a>
</p>

```text
$ exit
```

<p align="center">
  <img src="https://komarev.com/ghpvc/?username=chu0119&style=for-the-badge&color=00E5FF" alt="visitors"/>
</p>
````

- [ ] **Step 2: Markdown render smoke-check**

```bash
cd /d/xiangmu/chu0119/profile-repo && gh api markdown -f text="$(cat README.md)" > /tmp/render.html && grep -c "assets/achievements.svg\|assets/banner.svg\|mailto:chu0119@foxmail.com" /tmp/render.html && grep -c "<table" /tmp/render.html
```

Expected: first count ≥ 3 (banner + achievements + mailto links present), second ≥ 1 (arsenal table rendered). If `$(cat ...)` chokes on CRLF, run `dos2unix README.md` equivalent via `sed -i 's/\r$//' README.md` first — but prefer NOT to mutate line endings; instead fall back to:

```bash
gh api markdown -F text=@README.md > /tmp/render.html
```

(-F reads raw file contents directly.)

- [ ] **Step 3: Verify activity markers intact**

```bash
cd /d/xiangmu/chu0119/profile-repo && grep -c "BEGIN ACTIVITY\|END ACTIVITY" README.md
```

Expected: `2`.

- [ ] **Step 4: Commit**

```bash
cd /d/xiangmu/chu0119/profile-repo && git add README.md
git commit -m "feat: profile v2 — bilingual sections, 6-project arsenal cards, contact block"
```

---

### Task 4: Push, trigger pipeline, verify live

**Files:** none created; remote verification only.

**Interfaces:**
- Consumes: all three prior commits on local `main`.
- Produces: deployed profile; `generate-stats.yml` re-runs (trigger: push touched `scripts/generate_stats.py`) committing fresh `assets/*.svg` including `achievements.svg`.

- [ ] **Step 1: Push**

```bash
cd /d/xiangmu/chu0119/profile-repo && git push origin main
```

- [ ] **Step 2: Watch the stats workflow**

```bash
gh run list --repo chu0119/chu0119 --workflow generate-stats.yml --limit 1
sleep 20 && gh run list --repo chu0119/chu0119 --workflow generate-stats.yml --limit 1
```

Poll until status `completed` with conclusion `success` (use `gh run watch <id> --exit-status` if preferred). Expected: success; the bot makes an extra commit `chore: update profile stats`.

- [ ] **Step 3: Verify live assets**

```bash
curl -sI https://raw.githubusercontent.com/chu0119/chu0119/main/assets/achievements.svg | head -1
curl -sI https://raw.githubusercontent.com/chu0119/chu0119/main/assets/banner.svg | head -1
```

Expected: `HTTP/2 200` twice.

- [ ] **Step 4: Final visual verification**

Fetch `https://github.com/chu0119` and confirm: banner animates (SMIL present in served HTML via camo-proxied SVG), arsenal table shows 6 clickable project cards, achievements panel image loads, contact email badge renders, bilingual copy intact. Report any rendering issue back to the user with a link.

---

## Self-Review Notes

- Spec coverage: layout items 1–10 map to Task 2 (banner), Task 3 (identity/focus/arsenal/tech-stack/stats+achievements/activity/contact/counter), Task 1 (achievements generator). Risks section honored (vector icons, snapshot-data caveat already stated in spec).
- No placeholders: all code, copy, and commands are verbatim above.
- Type consistency: `svg_achievements(stats, streak_data)` signature consistent between test (Task 1 Step 1), implementation (Task 1 Step 3), and `main()` wiring; asset filename `assets/achievements.svg` consistent across Tasks 1/3/4.
