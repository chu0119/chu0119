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
