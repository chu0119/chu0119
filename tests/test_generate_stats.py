import os
import sys
from unittest.mock import patch

import defusedxml.ElementTree as ET

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

from generate_stats import fetch_stats, normalize_stats, svg_achievements  # noqa: E402

STATS = {"repos": 66, "stars": 72, "prs": 3, "issues": 5,
         "contributions": 1234, "top_langs": [("Python", 10)]}
STREAK = {"current": 2, "longest": 5, "total": 548}


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
    assert s.count("#27C93F") == 3
    assert "#10B981" not in s


def test_ascii_only_vector_icons():
    s = svg_achievements(STATS, STREAK)
    assert s.isascii()


def test_small_numbers_have_no_separator():
    s = svg_achievements({**STATS, "contributions": 999}, STREAK)
    assert ">999</text>" in s
    assert "1,234" not in s
