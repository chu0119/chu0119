# GitHub Profile Redesign Implementation Plan

> Review amendment (2026-09-25): the final implementation intentionally replaces user-wide pull request, issue, contribution, and streak totals with metrics derived solely from `privacy: PUBLIC` repository connections. It also rejects GraphQL partial responses before any asset write. The task-by-task text below records the original execution plan; the review amendment is authoritative where they differ.

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ship a bilingual, privacy-safe GitHub profile with a polished Cyber Security Lab visual system, six coherent featured projects, and reliable repository-owned dynamic assets.

**Architecture:** Keep the profile GitHub-native: `README.md` owns the narrative, repository SVGs own the high-fidelity visual system, and two small Python scripts refresh public statistics and public activity. Refactor dynamic-data handling into pure functions so privacy rules, fallback behavior, marker safety, and SVG validity are covered by deterministic tests before live data is generated.

**Tech Stack:** GitHub Markdown/HTML, SVG 1.1, Python 3.12 standard library, pytest, GitHub GraphQL/REST APIs, GitHub Actions.

**Spec:** `docs/superpowers/specs/2026-09-25-github-profile-redesign-design.md`

## Global Constraints

- Public identity is only `星川 / xingchuan`.
- Never publish a legal name, employer, school, phone number, personal address, private contact detail, private engagement, private repository name, or private repository metadata.
- Resume-derived content is limited to generalized security-engineering practice since 2023, demonstrated capability areas, and generalized national/provincial competition recognition.
- Visual palette is deep navy with cyan/teal signals and limited magenta accents.
- Chinese carries the main narrative; concise English provides context without sentence-by-sentence duplication.
- Dynamic visuals remain repository-owned and must not depend on third-party statistics-image services.
- The six featured repositories are `fscan-toolkit`, `zhidun`, `DarkForest-Hunter`, `log-audit`, `xingchuan-ti`, and `AegisIR`.
- API failures must leave the last committed valid assets and README activity block intact.

## Review Focus

1. A token with access to private repositories must still query and aggregate only public repositories; Task 1 adds a query-contract and aggregation test.
2. GitHub may return null nodes, missing languages, or zero repositories; Task 1 adds normalization and zero-data tests.
3. Dynamic text may contain XML metacharacters; Task 2 adds escaping and parse-validity tests for every generated SVG.
4. Activity markers may be missing or duplicated; Task 3 adds tests that reject unsafe replacement and preserve the original README.
5. Resume-only identity and contact information must not enter tracked files; Task 4 adds structural privacy tests without embedding private values in the repository.

---

### Task 1: Public-only GitHub data model

**Files:**
- Modify: `scripts/generate_stats.py`
- Modify: `tests/test_generate_stats.py`

**Interfaces:**
- Consumes: GitHub GraphQL response for `user.repositories`, `pullRequests`, `issues`, and `contributionsCollection`.
- Produces: `fetch_stats() -> dict[str, object]` containing `repos`, `stars`, `prs`, `issues`, `contributions`, and `top_langs`; `normalize_stats(user: dict) -> dict[str, object]`; `fetch_streak() -> dict[str, int]`.

- [ ] **Step 1: Add failing public-data and normalization tests**

Add imports and tests that pin the public-only contract and safe handling of incomplete data:

```python
from unittest.mock import patch

from generate_stats import fetch_stats, normalize_stats


def test_fetch_stats_queries_public_repositories_only():
    payload = {
        "user": {
            "publicRepositories": {"totalCount": 69},
            "sourceRepositories": {"nodes": []},
            "pullRequests": {"totalCount": 0},
            "issues": {"totalCount": 0},
            "contributionsCollection": {
                "contributionCalendar": {"totalContributions": 0}
            },
        }
    }
    with patch("generate_stats.gql", return_value=payload) as mocked:
        result = fetch_stats()
    query = mocked.call_args.args[0]
    assert "privacy: PUBLIC" in query
    assert result["repos"] == 69


def test_normalize_stats_ignores_null_nodes_and_missing_languages():
    user = {
        "publicRepositories": {"totalCount": 2},
        "sourceRepositories": {
            "nodes": [None, {"stargazerCount": 7, "primaryLanguage": None}]
        },
        "pullRequests": {"totalCount": 1},
        "issues": {"totalCount": 2},
        "contributionsCollection": {
            "contributionCalendar": {"totalContributions": 3}
        },
    }
    result = normalize_stats(user)
    assert result == {
        "repos": 2,
        "stars": 7,
        "prs": 1,
        "issues": 2,
        "contributions": 3,
        "top_langs": [],
    }
```

- [ ] **Step 2: Run the focused tests and confirm they fail**

Run: `python -m pytest tests/test_generate_stats.py -q`

Expected: failure because `normalize_stats` does not exist and the query has no `privacy: PUBLIC` aliases.

- [ ] **Step 3: Implement the public-only query and normalization boundary**

Refactor the GraphQL query to separate total public repository count from non-fork source repositories used for earned stars and language distribution:

```python
def normalize_stats(user):
    public_repositories = user.get("publicRepositories") or {}
    source_repositories = user.get("sourceRepositories") or {}
    pull_requests = user.get("pullRequests") or {}
    issues = user.get("issues") or {}
    contributions = user.get("contributionsCollection") or {}
    calendar = contributions.get("contributionCalendar") or {}
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
        "stars": sum(repo.get("stargazerCount", 0) or 0 for repo in repos),
        "prs": pull_requests.get("totalCount", 0) or 0,
        "issues": issues.get("totalCount", 0) or 0,
        "contributions": calendar.get("totalContributions", 0) or 0,
        "top_langs": sorted(lang_counts.items(), key=lambda item: (-item[1], item[0]))[:8],
    }
```

Use these two GraphQL connections:

```graphql
publicRepositories: repositories(
  ownerAffiliations: OWNER,
  privacy: PUBLIC,
  first: 1
) { totalCount }
sourceRepositories: repositories(
  ownerAffiliations: OWNER,
  privacy: PUBLIC,
  isFork: false,
  first: 100
) { nodes { stargazerCount primaryLanguage { name color } } }
```

Return `normalize_stats(gql(query, {"login": USER})["user"])` from `fetch_stats()`.

- [ ] **Step 4: Run the complete stats test module**

Run: `python -m pytest tests/test_generate_stats.py -q`

Expected: all tests pass, including existing vector-icon and thousands-separator coverage.

- [ ] **Step 5: Commit the public-data boundary**

```bash
git add scripts/generate_stats.py tests/test_generate_stats.py
git commit -m "fix: restrict profile metrics to public repositories"
```

---

### Task 2: Cyber Security Lab SVG system

**Files:**
- Modify: `assets/banner.svg`
- Modify: `scripts/generate_stats.py`
- Modify: `tests/test_generate_stats.py`
- Regenerate: `assets/achievements.svg`
- Regenerate: `assets/stats.svg`
- Regenerate: `assets/langs.svg`
- Regenerate: `assets/streak.json`

**Interfaces:**
- Consumes: the normalized stats and streak dictionaries from Task 1.
- Produces: `svg_achievements(stats, streak_data) -> str`, `svg_stats(stats, streak_data) -> str`, `svg_langs(stats) -> str`, and four parse-valid repository assets.

- [ ] **Step 1: Add failing visual-contract tests**

Extend `tests/test_generate_stats.py`:

```python
from generate_stats import svg_langs, svg_stats


def test_all_generated_svgs_are_valid_xml():
    for renderer in (
        lambda: svg_achievements(STATS, STREAK),
        lambda: svg_stats(STATS, STREAK),
        lambda: svg_langs(STATS),
    ):
        ET.fromstring(renderer())


def test_cyber_lab_palette_and_bilingual_labels():
    combined = "".join((
        svg_achievements(STATS, STREAK),
        svg_stats(STATS, STREAK),
        svg_langs(STATS),
    ))
    assert "#07101C" in combined
    assert "#59E7D1" in combined
    assert "#E85B9C" in combined
    assert "公开仓库" in combined
    assert "PUBLIC REPOS" in combined


def test_dynamic_language_names_are_xml_escaped():
    svg = svg_langs({**STATS, "top_langs": [("R&D <Lab>", 1)]})
    ET.fromstring(svg)
    assert "R&amp;D &lt;Lab&gt;" in svg


def test_empty_language_data_still_renders_valid_cyber_lab_panel():
    svg = svg_langs({**STATS, "top_langs": []})
    ET.fromstring(svg)
    assert "暂无语言数据" in svg
    assert "NO PUBLIC LANGUAGE DATA" in svg
```

- [ ] **Step 2: Run tests and confirm the new visual contract fails**

Run: `python -m pytest tests/test_generate_stats.py -q`

Expected: failures for the new palette, bilingual labels, and unescaped dynamic language name.

- [ ] **Step 3: Add safe SVG text and shared design tokens**

In `scripts/generate_stats.py`, add:

```python
from xml.sax.saxutils import escape

BG = "#07101C"
PANEL = "#0C1D2C"
CYAN = "#59E7D1"
BLUE = "#66DDFF"
MAGENTA = "#E85B9C"
TEXT = "#EAF3F8"
MUTED = "#7691A5"


def svg_text(value):
    return escape(str(value), {'"': "&quot;", "'": "&apos;"})
```

Call `svg_text` for every dynamic label and value inserted into SVG markup.

- [ ] **Step 4: Redesign the generated panels**

Implement the approved visual hierarchy:

- `achievements.svg`: 720×176 “OPEN SOURCE SIGNAL / 开源数据” panel with public repos, earned stars, yearly contributions, and current streak;
- `stats.svg`: 720×150 slim engineering-signal panel with PRs, issues, longest streak, and six featured projects;
- `langs.svg`: 720×140 language-distribution panel with a wide segmented bar and up to five legend items;
- ASCII/vector icons only, with bilingual accessible text and a `<title>` element in each SVG.

Keep every panel responsive through `viewBox="0 0 720 ..."` and `width="720"` rather than embedding raster assets.

- [ ] **Step 5: Replace the banner with the approved identity treatment**

Rewrite `assets/banner.svg` as a 960×300 scalable panel containing:

- `XINGCHUAN // SECURITY ENGINEERING` metadata;
- `Build systems that turn signals into action.`;
- `把安全信号转化为可执行的检测、响应与工程化工具。`;
- the three focus labels `OFFENSIVE`, `DEFENSIVE`, and `ENGINEERING`;
- subtle grid, scan-line, and signal-wave vector details;
- no exploit command, target IP, “access granted,” or other game-like copy.

- [ ] **Step 6: Run tests and generate live assets without partial writes**

Change `main()` to render all output strings first, parse them with `xml.etree.ElementTree.fromstring`, then write files only after every render validates. Run:

```bash
python -m pytest tests/test_generate_stats.py -q
```

Then generate against the authenticated account in PowerShell without printing the token:

```powershell
$env:GH_TOKEN = gh auth token
python scripts/generate_stats.py
Remove-Item Env:GH_TOKEN
```

Expected: tests pass; all four generated files update; an API/render failure occurs before any asset is replaced.

- [ ] **Step 7: Commit the visual system**

```bash
git add assets/banner.svg assets/achievements.svg assets/stats.svg assets/langs.svg assets/streak.json scripts/generate_stats.py tests/test_generate_stats.py
git commit -m "feat: add cyber security lab visual system"
```

---

### Task 3: Safe recent-activity updates

**Files:**
- Modify: `scripts/update_activity.py`
- Create: `tests/test_update_activity.py`

**Interfaces:**
- Consumes: public GitHub event dictionaries and a README string containing one activity marker pair.
- Produces: `render_activity(events: list[dict]) -> list[str]` and `replace_activity(readme: str, lines: list[str]) -> str`.

- [ ] **Step 1: Add failing tests for filtering and marker safety**

Create `tests/test_update_activity.py`:

```python
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

from update_activity import render_activity, replace_activity


def test_render_activity_excludes_profile_repo_and_deduplicates():
    events = [
        {"type": "PushEvent", "repo": {"name": "chu0119/chu0119"}},
        {"type": "PushEvent", "repo": {"name": "chu0119/zhidun"}},
        {"type": "PushEvent", "repo": {"name": "chu0119/zhidun"}},
    ]
    assert render_activity(events) == [
        "- 🚀 [**zhidun**](https://github.com/chu0119/zhidun) — pushed updates"
    ]


@pytest.mark.parametrize("readme", [
    "no markers",
    "<!-- BEGIN ACTIVITY -->\nonly begin",
    "<!-- BEGIN ACTIVITY -->a<!-- END ACTIVITY --><!-- END ACTIVITY -->",
])
def test_replace_activity_rejects_invalid_marker_counts(readme):
    with pytest.raises(ValueError, match="exactly one activity marker pair"):
        replace_activity(readme, ["- item"])


def test_replace_activity_changes_only_marked_region():
    source = "before\n<!-- BEGIN ACTIVITY -->\nold\n<!-- END ACTIVITY -->\nafter\n"
    result = replace_activity(source, ["- new"])
    assert result == "before\n<!-- BEGIN ACTIVITY -->\n- new\n<!-- END ACTIVITY -->\nafter\n"
```

- [ ] **Step 2: Run the new module and confirm it fails**

Run: `python -m pytest tests/test_update_activity.py -q`

Expected: import failure because the pure functions do not exist.

- [ ] **Step 3: Extract pure activity functions and safe replacement**

Implement:

```python
EVENT_LABELS = {
    "PushEvent": ("🚀", "pushed updates"),
    "CreateEvent": ("✨", "created something new"),
    "WatchEvent": ("⭐", "starred this project"),
    "ForkEvent": ("🍴", "forked this project"),
    "ReleaseEvent": ("📦", "published a release"),
    "PullRequestEvent": ("🔀", "opened a pull request"),
}


def render_activity(events):
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
    if readme.count(BEGIN) != 1 or readme.count(END) != 1:
        raise ValueError("README must contain exactly one activity marker pair")
    start, tail = readme.split(BEGIN, 1)
    _, end = tail.split(END, 1)
    body = "\n".join(lines)
    return f"{start}{BEGIN}\n{body}\n{END}{end}"
```

Keep file writes in `main()` only after `replace_activity` returns a complete string.

- [ ] **Step 4: Run the activity and complete test suites**

Run:

```bash
python -m pytest tests/test_update_activity.py -q
python -m pytest tests -q
```

Expected: all activity tests and all repository tests pass.

- [ ] **Step 5: Commit safe activity handling**

```bash
git add scripts/update_activity.py tests/test_update_activity.py
git commit -m "test: harden profile activity updates"
```

---

### Task 4: Bilingual profile narrative and privacy guard

**Files:**
- Modify: `README.md`
- Create: `tests/test_profile_content.py`

**Interfaces:**
- Consumes: repository-owned SVG assets and live GitHub repository URLs.
- Produces: one responsive bilingual profile README with one valid activity marker pair and no private contact/identity fields.

- [ ] **Step 1: Add failing structure and privacy tests**

Create `tests/test_profile_content.py`:

```python
import re
from pathlib import Path

README = Path(__file__).parents[1] / "README.md"
TEXT = README.read_text(encoding="utf-8")

FEATURED = (
    "fscan-toolkit", "zhidun", "DarkForest-Hunter",
    "log-audit", "xingchuan-ti", "AegisIR",
)


def test_required_identity_and_sections_are_present():
    for phrase in (
        "星川 / xingchuan",
        "Security Researcher & Tool Builder",
        "研究方向 · Focus",
        "代表项目 · Selected Work",
        "能力矩阵 · Capabilities",
        "经历与认可 · Experience & Recognition",
        "开源数据 · Open Source Signal",
    ):
        assert phrase in TEXT


def test_exact_featured_portfolio_is_present():
    for repo in FEATURED:
        assert f"https://github.com/chu0119/{repo}" in TEXT


def test_readme_contains_no_direct_private_contact_or_institution_fields():
    assert "mailto:" not in TEXT.lower()
    assert not re.search(r"(?<!\d)1[3-9]\d{9}(?!\d)", TEXT)
    for label in ("手机号", "手机：", "学校：", "工作单位", "有限公司"):
        assert label not in TEXT


def test_activity_markers_are_unique():
    assert TEXT.count("<!-- BEGIN ACTIVITY -->") == 1
    assert TEXT.count("<!-- END ACTIVITY -->") == 1
```

- [ ] **Step 2: Run the profile tests and confirm the old README fails**

Run: `python -m pytest tests/test_profile_content.py -q`

Expected: failures for the new identity heading, sections, changed project set, and removed email contact.

- [ ] **Step 3: Rewrite the hero, focus, and selected-work sections**

Use this exact opening and focus copy:

```markdown
<p align="center">
  <img src="assets/banner.svg" alt="星川 xingchuan — Security Engineering" width="960" />
</p>

<h1 align="center">星川 / xingchuan</h1>
<p align="center"><strong>Security Researcher & Tool Builder</strong></p>
<p align="center">
  把安全信号转化为可执行的检测、响应与工程化工具。<br>
  <sub>Turning security signals into practical detection, response, and engineering systems.</sub>
</p>

## 研究方向 · Focus

<table>
<tr>
<td width="33%"><strong>01 // 攻防与漏洞研究</strong><br><sub>Offensive Security & Vulnerability Research</sub><br><br>面向授权场景的漏洞发现、验证与治理。</td>
<td width="33%"><strong>02 // 检测、研判与响应</strong><br><sub>Detection, Threat Intelligence & IR</sub><br><br>从日志与流量中提取线索，形成可解释的安全结论。</td>
<td width="33%"><strong>03 // AI 安全自动化</strong><br><sub>AI-powered Security Tooling</sub><br><br>用智能工作流缩短侦察、分析、处置与报告链路。</td>
</tr>
</table>
```

Follow it with a two-column HTML table using this exact outcome-focused project copy:

| Repository | Chinese outcome copy | English context |
| --- | --- | --- |
| `fscan-toolkit` | 把内网评估命令与结果整理成清晰、可复用的工作流。 | Usable command building and report parsing for practical assessment. |
| `zhidun` | 将原始 Web 日志转化为可解释的威胁研判结果。 | AI-assisted web-log analysis from raw events to security verdicts. |
| `DarkForest-Hunter` | 面向公开泄露风险的发现、只读验证与持续监控。 | Defensive exposure discovery and validation across AI platforms. |
| `log-audit` | 用规则、威胁情报和攻击链视角完成结构化日志研判。 | ATT&CK-aware detection, investigation, and reporting workflows. |
| `xingchuan-ti` | 聚合多源情报，对 IP 与域名形成加权研判。 | Multi-source threat intelligence with fast, explainable verdicts. |
| `AegisIR` | 为失陷主机提供快速网络隔离与生效验证。 | Fast network isolation and verification for incident response. |

For every card, link the heading to `https://github.com/chu0119/<repository>` and show its demonstrated language as plain text. Do not use Shields.io or another external statistics image service; earned stars are already represented by repository-owned generated SVGs. Do not add any other repositories to the featured table.

- [ ] **Step 4: Add capability, experience, and open-source sections**

Add these exact sections after the featured table:

```markdown
## 能力矩阵 · Capabilities

| Security Engineering | Detection & Response | Development | Platforms |
| --- | --- | --- | --- |
| 漏洞评估、授权测试、漏洞治理 | 日志分析、流量分析、威胁情报、应急响应 | Python、TypeScript、自动化与 LLM Agent | Linux、Docker、MySQL、Redis |

## 经历与认可 · Experience & Recognition

- **2023 — Now · Security Engineering Practice** — 安全运营、漏洞治理、日志分析与自动化工具开发。
- **National & Provincial Recognition** — 企业信息安全、信息安全管理评估与 AI 信息素养相关赛事经历。
- **Build for real workflows** — 持续把侦察、检测、响应和报告沉淀为可复用工具链。

## 开源数据 · Open Source Signal

<p align="center"><img src="assets/achievements.svg" alt="开源仓库、Star、贡献与连续活跃数据" width="720" /></p>
<p align="center"><img src="assets/stats.svg" alt="工程协作与项目数据" width="720" /></p>
<p align="center"><img src="assets/langs.svg" alt="主要编程语言分布" width="720" /></p>

## 最近动态 · Recent Activity

<!-- BEGIN ACTIVITY -->
- 🔬 Building in public · 持续构建中
<!-- END ACTIVITY -->
```

- [ ] **Step 5: Replace direct contact with GitHub-native collaboration**

End with:

```markdown
## 协作 · Collaboration

欢迎围绕安全工具、威胁检测、应急响应与 AI 安全自动化交流协作。
Open to collaboration on practical security tooling, detection engineering, incident response, and AI-assisted security workflows.

[查看全部公开项目](https://github.com/chu0119?tab=repositories) · [Follow @chu0119](https://github.com/chu0119)

> All security research and tooling is intended for authorized testing, defensive research, and education.
```

Remove the email badge, external visitor counter, exploit-themed copy, and broad undemonstrated badge wall.

- [ ] **Step 6: Run content and full tests**

Run:

```bash
python -m pytest tests/test_profile_content.py -q
python -m pytest tests -q
```

Expected: all tests pass; the README has one activity region and contains no direct private contact or institution fields.

- [ ] **Step 7: Commit the profile narrative**

```bash
git add README.md tests/test_profile_content.py
git commit -m "feat: redesign bilingual security profile"
```

---

### Task 5: Automation, rendering, and publication verification

**Files:**
- Modify: `.github/workflows/generate-stats.yml`
- Modify: `.github/workflows/update-activity.yml`
- Modify: `.gitignore`
- Verify: all tracked profile files

**Interfaces:**
- Consumes: the scripts, tests, README, and assets produced by Tasks 1–4.
- Produces: scheduled workflows that validate before committing, a clean repository, and the published profile on `main`.

- [ ] **Step 1: Add validation before automated commits**

In `generate-stats.yml`, add a test step before generation:

```yaml
      - name: Validate profile generators
        run: python -m pytest tests/test_generate_stats.py -q
```

In `update-activity.yml`, add:

```yaml
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'

      - name: Validate activity updater
        run: python -m pytest tests/test_update_activity.py tests/test_profile_content.py -q
```

Add a dependency installation step to both workflows:

```yaml
      - name: Install test dependency
        run: python -m pip install --disable-pip-version-check pytest defusedxml
```

Keep `contents: write`, scheduled execution, manual dispatch, and “commit only when changed” behavior.

- [ ] **Step 2: Prevent brainstorming artifacts from entering the profile repository**

Ensure `.gitignore` contains:

```gitignore
.superpowers/
__pycache__/
.pytest_cache/
```

- [ ] **Step 3: Run the full offline validation set**

Run:

```bash
python -m pytest tests -q
python -m compileall -q scripts tests
git diff --check
```

Expected: all tests pass, all Python compiles, and Git reports no whitespace errors.

- [ ] **Step 4: Validate assets and public links**

Parse every SVG:

```powershell
python -c "from pathlib import Path; import xml.etree.ElementTree as ET; [ET.parse(path) for path in Path('assets').glob('*.svg')]; print('SVG validation passed')"
```

Then validate the six selected repositories:

```powershell
$featuredRepos = @('fscan-toolkit','zhidun','DarkForest-Hunter','log-audit','xingchuan-ti','AegisIR')
foreach ($repoName in $featuredRepos) {
    $isPrivate = gh api "repos/chu0119/$repoName" --jq '.private'
    if ($LASTEXITCODE -ne 0 -or $isPrivate -ne 'false') {
        throw "Repository is unavailable or private: $repoName"
    }
}
```

Expected: every SVG parses and all six API calls return repository metadata with `private: false`.

- [ ] **Step 5: Perform the privacy and tracked-file audit**

Run:

```bash
git grep -n -Ei "mailto:|手机号|手机：|学校：|工作单位|有限公司|1[3-9][0-9]{9}" -- README.md assets scripts tests .github
git status --short
```

Expected: the privacy scan returns no matches; status contains only intentional profile changes.

- [ ] **Step 6: Inspect desktop and narrow-width rendering**

Open the rendered README locally or in a GitHub branch preview and verify:

- banner text is legible at 960 px and approximately 390 px viewport widths;
- two-column project tables collapse without clipped text;
- all SVGs preserve their aspect ratios;
- Chinese glyph fallbacks render correctly;
- cyan and magenta accents remain secondary to the content hierarchy.

Capture one desktop and one narrow-width screenshot for review; do not commit the screenshots.

- [ ] **Step 7: Commit automation hardening**

```bash
git add .github/workflows/generate-stats.yml .github/workflows/update-activity.yml .gitignore
git commit -m "ci: validate profile updates before publishing"
```

- [ ] **Step 8: Review the complete branch and publish**

Run:

```bash
git log --oneline --decorate -6
git diff origin/main...HEAD --stat
git status --short
git push origin main
```

Expected: a clean worktree; the design, implementation, and validation commits are pushed to `main`; the public profile renders the redesigned README.
