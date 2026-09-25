import io
import json
import os
import sys
from unittest.mock import patch

import defusedxml.ElementTree as ET
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

from generate_stats import (  # noqa: E402
    fetch_stats,
    gql,
    main,
    normalize_stats,
    svg_achievements,
    svg_langs,
    svg_stats,
)

STATS = {
    "repos": 66,
    "source_repos": 52,
    "active_repos": 49,
    "stars": 72,
    "forks": 18,
    "languages": 7,
    "top_langs": [("Python", 10)],
}


def test_fetch_stats_uses_only_explicitly_public_repository_connections():
    payload = {
        "user": {
            "publicRepositories": {"totalCount": 69},
            "sourceRepositories": {"totalCount": 0, "nodes": []},
        }
    }
    with patch("generate_stats.gql", return_value=payload) as mocked:
        result = fetch_stats()
    query = mocked.call_args.args[0]
    assert query.count("privacy: PUBLIC") == 2
    assert "pullRequests" not in query
    assert "issues" not in query
    assert "contributionsCollection" not in query
    assert result["repos"] == 69


def test_normalize_stats_ignores_null_nodes_and_missing_languages():
    user = {
        "publicRepositories": {"totalCount": 2},
        "sourceRepositories": {
            "totalCount": 2,
            "nodes": [
                None,
                {
                    "stargazerCount": 7,
                    "forkCount": 3,
                    "isArchived": False,
                    "primaryLanguage": None,
                },
            ],
        },
    }
    result = normalize_stats(user)
    assert result == {
        "repos": 2,
        "source_repos": 2,
        "active_repos": 1,
        "stars": 7,
        "forks": 3,
        "languages": 0,
        "top_langs": [],
    }


def test_gql_rejects_partial_responses_with_errors():
    response = io.BytesIO(json.dumps({
        "data": {"user": {"sourceRepositories": {"nodes": [None]}}},
        "errors": [{"message": "repository data could not be resolved"}],
    }).encode())
    with patch("generate_stats.urllib.request.urlopen", return_value=response):
        with pytest.raises(RuntimeError, match="GraphQL request failed"):
            gql("query { viewer { login } }")


def test_main_preserves_existing_assets_on_partial_graphql_error(tmp_path):
    filenames = ("stats.svg", "langs.svg", "achievements.svg")
    for filename in filenames:
        (tmp_path / filename).write_text(f"existing:{filename}", encoding="utf-8")

    response = io.BytesIO(json.dumps({
        "data": {"user": {"sourceRepositories": {"nodes": [None]}}},
        "errors": [{"message": "partial response"}],
    }).encode())
    with patch("generate_stats.OUT_DIR", str(tmp_path)), patch(
        "generate_stats.urllib.request.urlopen", return_value=response
    ):
        with pytest.raises(RuntimeError, match="GraphQL request failed"):
            main()

    for filename in filenames:
        assert (tmp_path / filename).read_text(encoding="utf-8") == f"existing:{filename}"


def test_output_is_valid_xml():
    ET.fromstring(svg_achievements(STATS))


def test_renders_all_four_tiles():
    s = svg_achievements(STATS)
    assert s.count('rx="8"') == 4


def test_embeds_real_values():
    s = svg_achievements(STATS)
    assert ">72</text>" in s
    assert ">66</text>" in s
    assert ">18</text>" in s
    assert ">7</text>" in s
    assert "TOTAL STARS" in s
    assert "TOTAL FORKS" in s
    assert "LANGUAGES" in s
    assert "#10B981" not in s


def test_ascii_only_vector_icons():
    s = svg_achievements(STATS)
    assert s.isascii()


def test_all_generated_svgs_are_valid_xml():
    for renderer in (
        lambda: svg_achievements(STATS),
        lambda: svg_stats(STATS),
        lambda: svg_langs(STATS),
    ):
        ET.fromstring(renderer())


def test_cyber_lab_palette_and_bilingual_labels():
    combined = "".join((
        svg_achievements(STATS),
        svg_stats(STATS),
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
