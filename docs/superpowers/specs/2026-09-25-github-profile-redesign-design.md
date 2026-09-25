# GitHub Profile Redesign — Design Specification

**Date:** 2026-09-25
**Profile:** `github.com/chu0119`
**Public identity:** 星川 / xingchuan

## 1. Goal

Redesign the profile README into a polished bilingual security-engineering portfolio that works for three audiences at once:

1. recruiters and technical interviewers;
2. security-community peers and open-source collaborators;
3. potential project and enterprise partners.

The primary impression must be “professional security researcher and tool builder.” The page may feel futuristic and cyberpunk, but visual effects must remain restrained enough to preserve credibility and readability.

## 2. Privacy Boundary

The public profile uses only **星川 / xingchuan**.

The README must not disclose:

- legal name;
- employer or school names;
- phone number, personal address, or private contact details;
- non-public engagements or operational details;
- content from private repositories.

Resume-derived information may be used only in generalized form:

- security-engineering practice since 2023;
- experience across security operations, vulnerability management, log analysis, incident response, and security automation;
- national- and provincial-level competition recognition, without identifying institutions or unnecessary personal details.

The implementation will include a privacy scan for known sensitive strings before publication.

## 3. Visual Direction

The selected direction is **Cyber Security Lab**:

- deep navy background;
- cyan/teal signal color;
- limited magenta highlights;
- subtle grids, signal lines, and terminal-inspired metadata;
- clean sans-serif headlines with restrained monospace accents;
- high contrast, accessible text, and mobile-safe layouts.

Cyberpunk elements are decorative accents, not the main content. The design must avoid excessive neon, dense badge walls, game-like terminology, or aggressive offensive-security imagery.

The page is bilingual. Chinese carries the main narrative, followed by concise English context. It does not repeat every sentence word-for-word.

## 4. Information Architecture

### 4.1 Hero identity

- `XINGCHUAN // SECURITY ENGINEERING`
- `Security Researcher & Tool Builder`
- a bilingual value proposition centered on turning security signals into practical detection, response, and engineering systems;
- concise open-source collaboration status.

### 4.2 Focus areas

Three capability pillars:

1. 攻防与漏洞研究 / Offensive Security & Vulnerability Research
2. 检测、研判与响应 / Detection, Threat Intelligence & Incident Response
3. AI 安全自动化 / AI-powered Security Tooling

### 4.3 Selected work

Show six original public projects. Organize them by security outcome, not only by star count:

| Project | Role in the portfolio |
| --- | --- |
| `fscan-toolkit` | practical assessment workflow and usable security UX |
| `zhidun` | AI-assisted web-log threat analysis |
| `DarkForest-Hunter` | defensive exposure discovery and validation |
| `log-audit` | structured detection, investigation, and reporting |
| `xingchuan-ti` | multi-source threat-intelligence analysis |
| `AegisIR` | incident-response isolation and verification |

Each card includes a short Chinese outcome statement, one English explanation, the primary language, and live star data where practical.

### 4.4 Capability matrix

Keep the matrix focused on demonstrated capabilities:

- Python and TypeScript;
- vulnerability assessment and security testing;
- log and network-traffic analysis;
- threat intelligence and detection engineering;
- incident response and vulnerability management;
- Linux, Docker, MySQL, and Redis;
- LLM agents and security workflow automation.

### 4.5 Experience and recognition

Use a compact timeline:

- `2023 — Now`: practical security engineering;
- security operations, vulnerability governance, analysis, and automation;
- national- and provincial-level competition recognition;
- an emphasis on building for real workflows.

No employer, school, or private operational details are included.

### 4.6 Open-source signal

Retain auto-generated public metrics and recent activity, but keep them secondary to project outcomes. The profile should show repository-backed metrics such as public repositories, earned stars, forks, languages, and recent public activity without feeling like a scoreboard. User-wide contribution, pull-request, issue, and streak totals are excluded because a broad workflow token could mix private activity into those values.

### 4.7 Footer

- link to the GitHub profile and repositories;
- invitation to collaborate through GitHub;
- short responsible-security statement;
- no public personal email or other direct private contact information.

## 5. Technical Design

The implementation stays inside the existing profile repository and uses GitHub-native Markdown/HTML plus repository-owned SVG assets.

### Components

- `README.md`: content hierarchy, project cards, capability matrix, activity block, and footer;
- `assets/banner.svg`: bilingual identity and value proposition;
- `assets/achievements.svg`: restrained open-source signal summary;
- `assets/stats.svg`: metrics derived only from explicitly public repository connections;
- `assets/langs.svg`: language distribution presented as supporting context;
- `scripts/generate_stats.py`: GitHub API data collection and SVG generation;
- `scripts/update_activity.py`: public activity block updates;
- GitHub Actions workflows: scheduled refreshes without external image services.

### Data flow

1. A scheduled GitHub Action reads public GitHub data with the repository token.
2. The generator calculates public metrics and writes repository-owned SVGs.
3. The activity script updates only the marked activity region in `README.md`.
4. The workflow commits changes only when generated content differs.
5. The README references local repository assets, so the last successful output remains visible if a later refresh fails.

### Failure behavior

- API, network, or rate-limit failures must fail the workflow without replacing valid assets with empty output.
- Missing or null fields receive safe fallbacks.
- Generated SVG text is XML-escaped.
- Activity updates are limited to explicit marker comments.
- No token, email address, resume field, or private repository metadata is written into generated output or logs.

## 6. Validation

Before publication:

1. run existing unit tests and extend them for changed generator behavior;
2. parse every generated SVG as XML;
3. validate local links and selected repository URLs;
4. verify activity markers remain intact;
5. inspect the rendered README at desktop and narrow/mobile widths;
6. check contrast and text legibility in the dark visual system;
7. scan tracked files for known private identifiers and resume-only personal data;
8. run the generators with representative API data and confirm stable fallback behavior.

## 7. Acceptance Criteria

The redesign is complete when:

- the profile clearly presents 星川 / xingchuan as a security researcher and tool builder;
- the page is bilingual, concise, and understandable to all three target audiences;
- the six selected repositories demonstrate a coherent security-engineering portfolio;
- the visual system is futuristic and distinctive without reducing professionalism;
- no private identity, institution, employer, phone, or private-repository information appears;
- scheduled metrics and activity updates continue to work without third-party image dependencies;
- tests, link checks, SVG validation, responsive inspection, and privacy checks pass.

## 8. Out of Scope

- creating a separate portfolio website;
- publishing resume files or direct contact details;
- changing repository visibility;
- rewriting the selected projects themselves;
- adding third-party analytics, trackers, or hosted statistics services.
