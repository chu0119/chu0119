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
    assert "mail" + "to:" not in TEXT.lower()
    assert not re.search(r"(?<!\d)1[3-9]\d{9}(?!\d)", TEXT)
    labels = (
        "手机" + "号",
        "手机" + "：",
        "学校" + "：",
        "工作" + "单位",
        "有限" + "公司",
    )
    for label in labels:
        assert label not in TEXT


def test_activity_markers_are_unique():
    assert TEXT.count("<!-- BEGIN ACTIVITY -->") == 1
    assert TEXT.count("<!-- END ACTIVITY -->") == 1
