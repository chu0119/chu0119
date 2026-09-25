import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

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
