"""Smoke + branch tests for skills/linguistic-bitext/scripts/alignment_score.py.

Covers 0012-alignment-niger-congo-branch (Niger-Congo widening) and the existing
polysynthetic / agglutinative / semitic / default branches.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
SCRIPT = REPO_ROOT / "skills" / "linguistic-bitext" / "scripts" / "alignment_score.py"
sys.path.insert(0, str(SCRIPT.parent))

from alignment_score import _is_niger_congo, recommend_length_ratio  # noqa: E402


@pytest.mark.parametrize(
    "iso,family,expected",
    [
        # Niger-Congo widening (0012)
        ("yor", "Niger-Congo > Atlantic-Congo", (0.3, 3.0)),
        ("swa", "Niger-Congo > Bantu", (0.3, 3.0)),
        ("twi", "Niger-Congo > Atlantic-Congo", (0.3, 3.0)),
        ("ibo", "Niger-Congo > Atlantic-Congo", (0.3, 3.0)),
        ("hau", "Afro-Asiatic > Chadic", (0.3, 3.0)),
        ("zul", "Niger-Congo > Bantu", (0.3, 3.0)),
        ("xho", "Niger-Congo > Bantu", (0.3, 3.0)),
        # Existing branches unchanged
        ("nav", "Na-Dene > Athabaskan", (0.2, 1.5)),  # polysynthetic
        ("iku", "Eskimo-Aleut", (0.2, 1.5)),  # polysynthetic
        ("tur", "Turkic", (0.4, 2.5)),  # agglutinative
        ("fin", "Uralic", (0.4, 2.5)),  # agglutinative
        ("arb", "Afro-Asiatic > Semitic", (0.4, 2.0)),  # semitic
        ("heb", "Afro-Asiatic > Semitic", (0.4, 2.0)),  # semitic
        # Default
        ("fra", "Indo-European > Romance", (0.5, 2.0)),
        ("deu", "Indo-European > Germanic", (0.5, 2.0)),
        ("spa", "Indo-European > Romance", (0.5, 2.0)),
    ],
)
def test_length_ratio_bounds_per_iso(iso, family, expected):
    bounds, _ = recommend_length_ratio(iso, family)
    assert bounds == expected, f"{iso} ({family}): got {bounds}, expected {expected}"


def test_niger_congo_typology_tag_widens_unknown_iso():
    """Unknown ISO + Niger-Congo family tag still hits the widened branch."""
    assert _is_niger_congo("xyz", "niger-congo > unknown") is True
    bounds, rationale = recommend_length_ratio("xyz", "niger-congo > unknown")
    assert bounds == (0.3, 3.0)
    assert "niger-congo" in rationale.lower() or "bantu" in rationale.lower() or "kwa" in rationale.lower()


def test_niger_congo_bantu_tag_widens():
    bounds, _ = recommend_length_ratio("xyz", "Bantu")
    assert bounds == (0.3, 3.0)


def test_default_branch_for_typologically_similar_pairs():
    """Romance/Germanic without Niger-Congo signal stays default."""
    bounds, _ = recommend_length_ratio("ita", "Indo-European > Romance")
    assert bounds == (0.5, 2.0)


def test_smoke_subprocess_yor_eng(tmp_path):
    """End-to-end smoke: script exits 0 + emits valid JSON for Yoruba bitext recommendations."""
    import subprocess

    result = subprocess.run(
        [sys.executable, str(SCRIPT), "english", "yoruba"],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode == 0, f"exit={result.returncode}; stderr={result.stderr}"
    parsed = json.loads(result.stdout)
    assert parsed["target_iso"] == "yor"
    # 0012: Niger-Congo widening must be reflected in the recommendation
    assert parsed["recommendations"]["length_ratio_filter"]["min"] == 0.3
    assert parsed["recommendations"]["length_ratio_filter"]["max"] == 3.0
