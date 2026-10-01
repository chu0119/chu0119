import subprocess
import sys
from pathlib import Path

import defusedxml.ElementTree as ET


ROOT = Path(__file__).parents[1]
GENERATOR = ROOT / "scripts" / "generate_profile_assets.py"

PROJECTS = (
    "fscan-toolkit",
    "zhidun",
    "DarkForest-Hunter",
    "log-audit",
    "xingchuan-ti",
    "AegisIR",
)


def test_generator_builds_complete_dark_visual_system(tmp_path):
    assert GENERATOR.exists(), "profile visual generator is missing"

    subprocess.run(
        [sys.executable, str(GENERATOR), "--output-dir", str(tmp_path)],
        check=True,
        cwd=ROOT,
    )

    expected = [
        tmp_path / "focus.svg",
        tmp_path / "projects-header.svg",
        tmp_path / "profile.svg",
        tmp_path / "footer.svg",
        *(tmp_path / "projects" / f"{name}.svg" for name in PROJECTS),
    ]
    for asset in expected:
        assert asset.exists(), f"missing generated asset: {asset.name}"
        svg = asset.read_text(encoding="utf-8")
        ET.fromstring(svg)
        assert "#07101C" in svg
        assert "#59E7D1" in svg


def test_project_cards_contain_bilingual_copy_and_no_private_contact(tmp_path):
    subprocess.run(
        [sys.executable, str(GENERATOR), "--output-dir", str(tmp_path)],
        check=True,
        cwd=ROOT,
    )

    for project in PROJECTS:
        svg = (tmp_path / "projects" / f"{project}.svg").read_text(
            encoding="utf-8"
        )
        assert project in svg
        assert "PROJECT //" in svg
        assert "mailto:" not in svg.lower()


def test_readme_uses_visual_panels_for_primary_content():
    readme = (ROOT / "README.md").read_text(encoding="utf-8")

    for asset in (
        "assets/visual/focus.svg",
        "assets/visual/projects-header.svg",
        "assets/visual/profile.svg",
        "assets/visual/footer.svg",
        "assets/activity.svg",
    ):
        assert asset in readme

    for project in PROJECTS:
        assert f'assets/visual/projects/{project}.svg' in readme
        assert f'https://github.com/chu0119/{project}' in readme

    assert "<table>" not in readme
    assert readme.count("<details>") == 1
    assert readme.count("assets/visual/") >= 9


def test_activity_workflow_publishes_visual_asset():
    workflow = (ROOT / ".github" / "workflows" / "update-activity.yml").read_text(
        encoding="utf-8"
    )
    assert "assets/activity.svg" in workflow
