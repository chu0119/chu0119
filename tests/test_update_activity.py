import os
import sys

import defusedxml.ElementTree as ET
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

import update_activity  # noqa: E402
from update_activity import render_activity, replace_activity  # noqa: E402


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


def test_render_activity_svg_creates_dark_bilingual_panel():
    renderer = getattr(update_activity, "render_activity_svg", None)
    assert callable(renderer), "activity SVG renderer is missing"

    svg = renderer([
        "- 🚀 [**zhidun**](https://github.com/chu0119/zhidun) — pushed updates",
        "- ⭐ [**xingchuan-ti**](https://github.com/chu0119/xingchuan-ti) — starred this project",
    ])
    ET.fromstring(svg)
    assert "#07101C" in svg
    assert "RECENT ACTIVITY / 最近动态" in svg
    assert "zhidun" in svg
    assert "xingchuan-ti" in svg


def test_main_writes_activity_svg_alongside_hidden_markdown(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "README.md").write_text(
        "before\n<!-- BEGIN ACTIVITY -->\nold\n<!-- END ACTIVITY -->\nafter\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(update_activity, "api", lambda _url: [
        {"type": "PushEvent", "repo": {"name": "chu0119/zhidun"}},
    ])

    update_activity.main()

    activity = tmp_path / "assets" / "activity.svg"
    assert activity.exists()
    ET.parse(activity)
