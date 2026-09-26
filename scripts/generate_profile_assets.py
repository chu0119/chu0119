#!/usr/bin/env python3
"""Generate the static visual system used by the GitHub profile README."""
import argparse
import os
import xml.etree.ElementTree as ET
from pathlib import Path
from xml.sax.saxutils import escape


BG = "#07101C"
PANEL = "#0C1D2C"
PANEL_ALT = "#0A1724"
LINE = "#17364A"
CYAN = "#59E7D1"
BLUE = "#66DDFF"
MAGENTA = "#E85B9C"
TEXT = "#EAF3F8"
MUTED = "#7691A5"
GREEN = "#36D399"

ROOT = Path(__file__).parents[1]
DEFAULT_OUT = ROOT / "assets" / "visual"

FOCUS = (
    (
        "01",
        "攻防与漏洞研究",
        "OFFENSIVE SECURITY & VULNERABILITY RESEARCH",
        "面向授权场景的漏洞发现、验证与治理。",
    ),
    (
        "02",
        "检测、研判与响应",
        "DETECTION · THREAT INTELLIGENCE · INCIDENT RESPONSE",
        "从日志与流量中提取线索，形成可解释的安全结论。",
    ),
    (
        "03",
        "AI 安全自动化",
        "AI-POWERED SECURITY TOOLING",
        "用智能工作流缩短侦察、分析、处置与报告链路。",
    ),
)

PROJECTS = (
    (
        "fscan-toolkit",
        "HTML · SECURITY WORKFLOW UX",
        "把内网评估命令与结果整理成清晰、可复用的工作流。",
        "Command building and report parsing for practical assessment.",
    ),
    (
        "zhidun",
        "TYPESCRIPT · AI THREAT ANALYSIS",
        "将原始 Web 日志转化为可解释的威胁研判结果。",
        "AI-assisted web-log analysis from raw events to security verdicts.",
    ),
    (
        "DarkForest-Hunter",
        "PYTHON · EXPOSURE DEFENSE",
        "面向公开泄露风险的发现、只读验证与持续监控。",
        "Defensive exposure discovery and validation across AI platforms.",
    ),
    (
        "log-audit",
        "PYTHON · DETECTION ENGINEERING",
        "用规则、威胁情报和攻击链视角完成结构化日志研判。",
        "ATT&CK-aware detection, investigation, and reporting workflows.",
    ),
    (
        "xingchuan-ti",
        "TYPESCRIPT · THREAT INTELLIGENCE",
        "聚合多源情报，对 IP 与域名形成加权研判。",
        "Multi-source threat intelligence with fast, explainable verdicts.",
    ),
    (
        "AegisIR",
        "PYTHON · INCIDENT RESPONSE",
        "为失陷主机提供快速网络隔离与生效验证。",
        "Fast network isolation and verification for incident response.",
    ),
)

CAPABILITIES = (
    ("SECURITY ENGINEERING", "漏洞评估", "授权测试", "漏洞治理"),
    ("DETECTION & RESPONSE", "日志与流量分析", "威胁情报", "应急响应"),
    ("DEVELOPMENT", "Python", "TypeScript", "LLM Agent"),
    ("PLATFORMS", "Linux · Docker", "MySQL · Redis", "Security Toolchains"),
)


def text(value):
    return escape(str(value), {'"': "&quot;", "'": "&apos;"})


def shell(width, height, title, subtitle, body, accent=CYAN):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">
  <title id="title">{text(title)}</title>
  <desc id="desc">{text(subtitle)}</desc>
  <defs>
    <linearGradient id="edge" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%" stop-color="{CYAN}"/>
      <stop offset="65%" stop-color="{BLUE}"/>
      <stop offset="100%" stop-color="{MAGENTA}"/>
    </linearGradient>
    <pattern id="grid" width="32" height="32" patternUnits="userSpaceOnUse">
      <path d="M32 0H0V32" fill="none" stroke="#10283A" stroke-width="0.6" opacity="0.42"/>
    </pattern>
  </defs>
  <rect width="{width}" height="{height}" rx="16" fill="{BG}"/>
  <rect x="0.75" y="0.75" width="{width - 1.5}" height="{height - 1.5}" rx="15" fill="none" stroke="url(#edge)" stroke-opacity="0.42"/>
  <rect width="{width}" height="{height}" rx="16" fill="url(#grid)"/>
  <rect x="18" y="18" width="4" height="20" rx="2" fill="{accent}"/>
  <text x="34" y="32" font-family="Consolas,Menlo,monospace" font-size="13" font-weight="700" letter-spacing="1.7" fill="{CYAN}">{text(title)}</text>
  <text x="{width - 18}" y="31" text-anchor="end" font-family="Consolas,Menlo,monospace" font-size="9" letter-spacing="1.2" fill="{MUTED}">{text(subtitle)}</text>
  <path d="M18 49H{width - 18}" stroke="{LINE}"/>
{body}
</svg>'''


def render_focus():
    rows = []
    for index, (number, zh, en, description) in enumerate(FOCUS):
        y = 65 + index * 83
        accent = CYAN if index != 1 else MAGENTA
        rows.append(f'''  <rect x="18" y="{y}" width="684" height="70" rx="10" fill="{PANEL_ALT}" stroke="{accent}" stroke-opacity="0.32"/>
  <text x="38" y="{y + 31}" font-family="Consolas,Menlo,monospace" font-size="22" font-weight="700" fill="{accent}">{number}</text>
  <path d="M70 {y + 15}V{y + 55}" stroke="{LINE}"/>
  <text x="88" y="{y + 26}" font-family="Segoe UI,Microsoft YaHei,Arial,sans-serif" font-size="16" font-weight="700" fill="{TEXT}">{text(zh)}</text>
  <text x="88" y="{y + 48}" font-family="Consolas,Menlo,monospace" font-size="8.5" letter-spacing="0.75" fill="{MUTED}">{text(en)}</text>
  <text x="680" y="{y + 39}" text-anchor="end" font-family="Segoe UI,Microsoft YaHei,Arial,sans-serif" font-size="12" fill="{TEXT}">{text(description)}</text>''')
    return shell(
        720,
        322,
        "RESEARCH FOCUS / 研究方向",
        "03 ACTIVE DOMAINS",
        "\n".join(rows),
    )


def render_projects_header():
    body = f'''  <text x="18" y="69" font-family="Segoe UI,Microsoft YaHei,Arial,sans-serif" font-size="13" fill="{TEXT}">从真实安全工作流出发，把分析过程沉淀为可复用工具。</text>
  <text x="702" y="69" text-anchor="end" font-family="Consolas,Menlo,monospace" font-size="9" fill="{MUTED}">CLICK A CARD TO OPEN REPOSITORY</text>'''
    return shell(720, 88, "SELECTED WORK / 代表项目", "06 FIELD SYSTEMS", body, MAGENTA)


def render_project_card(index, project):
    name, label, zh, en = project
    accent = CYAN if index % 2 else MAGENTA
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="720" height="126" viewBox="0 0 720 126" role="img" aria-labelledby="title desc">
  <title id="title">{text(name)}</title>
  <desc id="desc">{text(en)}</desc>
  <defs>
    <linearGradient id="card-edge" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%" stop-color="{accent}"/>
      <stop offset="100%" stop-color="{CYAN}" stop-opacity="0.18"/>
    </linearGradient>
  </defs>
  <rect width="720" height="126" rx="14" fill="{BG}"/>
  <rect x="0.75" y="0.75" width="718.5" height="124.5" rx="13" fill="none" stroke="url(#card-edge)" stroke-opacity="0.72"/>
  <rect x="18" y="18" width="52" height="90" rx="9" fill="{PANEL}" stroke="{accent}" stroke-opacity="0.35"/>
  <text x="44" y="57" text-anchor="middle" font-family="Consolas,Menlo,monospace" font-size="8" letter-spacing="0.6" fill="{MUTED}">PROJECT //</text>
  <text x="44" y="84" text-anchor="middle" font-family="Consolas,Menlo,monospace" font-size="22" font-weight="700" fill="{accent}">{index:02d}</text>
  <text x="90" y="39" font-family="Segoe UI,Arial,sans-serif" font-size="21" font-weight="700" fill="{TEXT}">{text(name)}</text>
  <text x="694" y="37" text-anchor="end" font-family="Consolas,Menlo,monospace" font-size="8.5" letter-spacing="0.9" fill="{accent}">{text(label)}</text>
  <path d="M90 51H694" stroke="{LINE}"/>
  <text x="90" y="76" font-family="Segoe UI,Microsoft YaHei,Arial,sans-serif" font-size="13" fill="{TEXT}">{text(zh)}</text>
  <text x="90" y="99" font-family="Segoe UI,Arial,sans-serif" font-size="10.5" fill="{MUTED}">{text(en)}</text>
  <path d="M681 109h13v-13" fill="none" stroke="{accent}" stroke-width="1.5"/>
</svg>'''


def render_profile():
    cards = []
    for index, (label, *items) in enumerate(CAPABILITIES):
        x = 18 + index * 174
        cards.append(f'''  <rect x="{x}" y="66" width="162" height="148" rx="10" fill="{PANEL_ALT}" stroke="{CYAN if index % 2 == 0 else MAGENTA}" stroke-opacity="0.28"/>
  <text x="{x + 13}" y="91" font-family="Consolas,Menlo,monospace" font-size="8.5" font-weight="700" letter-spacing="0.7" fill="{CYAN}">{text(label)}</text>
  <path d="M{x + 13} 102H{x + 149}" stroke="{LINE}"/>
  <text x="{x + 13}" y="127" font-family="Segoe UI,Microsoft YaHei,Arial,sans-serif" font-size="12" fill="{TEXT}">• {text(items[0])}</text>
  <text x="{x + 13}" y="158" font-family="Segoe UI,Microsoft YaHei,Arial,sans-serif" font-size="12" fill="{TEXT}">• {text(items[1])}</text>
  <text x="{x + 13}" y="189" font-family="Segoe UI,Microsoft YaHei,Arial,sans-serif" font-size="12" fill="{TEXT}">• {text(items[2])}</text>''')

    experience = (
        ("2023 — NOW", "SECURITY ENGINEERING PRACTICE", "安全运营 · 漏洞治理 · 日志分析 · 自动化工具开发"),
        ("RECOGNITION", "NATIONAL & PROVINCIAL", "企业信息安全 · 信息安全管理评估 · AI 信息素养相关赛事"),
        ("PRINCIPLE", "BUILD FOR REAL WORKFLOWS", "把侦察、检测、响应与报告持续沉淀为可复用工具链"),
    )
    rows = []
    for index, (label, headline, detail) in enumerate(experience):
        y = 276 + index * 58
        rows.append(f'''  <rect x="18" y="{y}" width="684" height="46" rx="8" fill="{PANEL_ALT}" stroke="{LINE}"/>
  <text x="34" y="{y + 28}" font-family="Consolas,Menlo,monospace" font-size="9" letter-spacing="0.8" fill="{MAGENTA if index == 1 else CYAN}">{text(label)}</text>
  <text x="190" y="{y + 21}" font-family="Segoe UI,Arial,sans-serif" font-size="11" font-weight="700" fill="{TEXT}">{text(headline)}</text>
  <text x="190" y="{y + 37}" font-family="Segoe UI,Microsoft YaHei,Arial,sans-serif" font-size="9.5" fill="{MUTED}">{text(detail)}</text>''')

    body = "\n".join(cards) + f'''
  <rect x="18" y="238" width="4" height="18" rx="2" fill="{MAGENTA}"/>
  <text x="34" y="252" font-family="Consolas,Menlo,monospace" font-size="12" font-weight="700" letter-spacing="1.5" fill="{CYAN}">EXPERIENCE &amp; RECOGNITION / 经历与认可</text>
''' + "\n".join(rows) + f'''
  <text x="18" y="472" font-family="Consolas,Menlo,monospace" font-size="8.5" letter-spacing="1" fill="{MUTED}">SECURITY RESEARCHER · TOOL BUILDER · PRACTICAL AUTOMATION</text>
  <circle cx="696" cy="469" r="3" fill="{GREEN}"/>
  <text x="687" y="472" text-anchor="end" font-family="Consolas,Menlo,monospace" font-size="8" fill="{MUTED}">SYSTEMS ONLINE</text>'''
    return shell(720, 488, "CAPABILITY MATRIX / 能力矩阵", "BUILD · DETECT · RESPOND", body)


def render_footer():
    body = f'''  <text x="18" y="75" font-family="Segoe UI,Microsoft YaHei,Arial,sans-serif" font-size="13" fill="{TEXT}">欢迎围绕安全工具、威胁检测、应急响应与 AI 安全自动化交流协作。</text>
  <text x="18" y="98" font-family="Segoe UI,Arial,sans-serif" font-size="10" fill="{MUTED}">Open to collaboration on practical security tooling, detection engineering, incident response, and AI-assisted workflows.</text>
  <circle cx="687" cy="82" r="5" fill="{GREEN}"/>
  <circle cx="687" cy="82" r="10" fill="none" stroke="{GREEN}" stroke-opacity="0.3"/>
  <text x="672" y="86" text-anchor="end" font-family="Consolas,Menlo,monospace" font-size="9" letter-spacing="1" fill="{GREEN}">GITHUB // OPEN</text>'''
    return shell(720, 122, "OPEN TO COLLABORATION / 协作", "AUTHORIZED · DEFENSIVE · PRACTICAL", body, MAGENTA)


def build_assets():
    assets = {
        "focus.svg": render_focus(),
        "projects-header.svg": render_projects_header(),
        "profile.svg": render_profile(),
        "footer.svg": render_footer(),
    }
    for index, project in enumerate(PROJECTS, 1):
        assets[f"projects/{project[0]}.svg"] = render_project_card(index, project)
    return assets


def write_assets(output_dir):
    output_dir = Path(output_dir)
    for relative, content in build_assets().items():
        ET.fromstring(content)
        path = output_dir / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8", newline="\n")
        print(f"wrote {path}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", default=os.fspath(DEFAULT_OUT))
    args = parser.parse_args()
    write_assets(args.output_dir)


if __name__ == "__main__":
    main()
