"""Smoke + self-test tests for skills/linguistic-speech/scripts/ipa_validate.py.

Covers 0011-ipa-validate-self-test (audit mode + per-language orthographic_block declarations)
plus the existing validate() entry-point smoke (Yoruba minimal pair).
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
SCRIPT = REPO_ROOT / "skills" / "linguistic-speech" / "scripts" / "ipa_validate.py"


def _run(*args: str, timeout: int = 30) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        capture_output=True,
        text=True,
        timeout=timeout,
    )


def test_self_test_passes_all_inventories():
    """0011 acceptance: --self-test exits 0 and reports all_passed=true for all 14 inventories."""
    result = _run("--self-test")
    assert result.returncode == 0, f"exit={result.returncode}; stdout={result.stdout[:500]}; stderr={result.stderr}"
    payload = json.loads(result.stdout)
    assert payload["all_passed"] is True
    # Sanity: report covers all 14 cached languages.
    assert len(payload["languages"]) == 14
    isos = {lang["iso"] for lang in payload["languages"]}
    assert {"yor", "vie", "cmn", "hau", "ibo", "amh", "arb"} <= isos
    # No language has any issues.
    for lang in payload["languages"]:
        assert lang["issues"] == [], f"{lang['iso']}: {lang['issues']}"


def test_classify_codepoint_taxonomy():
    """Direct unit test of the classifier — no subprocess."""
    sys.path.insert(0, str(SCRIPT.parent))
    from ipa_validate import _classify_codepoint  # noqa: E402

    # IPA Extensions block + named exceptions
    assert _classify_codepoint("ɔ") == "ipa_extensions"
    assert _classify_codepoint("ŋ") == "ipa_extensions"  # named exception (Latin Extended-A)
    assert _classify_codepoint("ð") == "ipa_extensions"  # named exception
    assert _classify_codepoint("θ") == "ipa_extensions"  # named exception (Greek)
    assert _classify_codepoint("ː") == "ipa_extensions"  # suprasegmental
    assert _classify_codepoint("ˈ") == "ipa_extensions"  # primary stress

    # Combining + ASCII + orthographic blocks
    assert _classify_codepoint("̀") == "combining_mark"  # combining grave
    assert _classify_codepoint("a") == "basic_latin_lower"
    assert _classify_codepoint("'") == "apostrophe"
    assert _classify_codepoint("ọ") == "latin_extended_additional"  # U+1ECD
    assert _classify_codepoint("ā") == "latin_extended"  # U+0101


def test_yoruba_minimal_pair_validates():
    """Regression for the iter-2 Yoruba P1 fix: ọkọ̀ must validate as a real Yoruba IPA word."""
    result = _run("Yoruba", "ọkọ̀")
    assert result.returncode == 0, f"exit={result.returncode}; stderr={result.stderr}"
    parsed = json.loads(result.stdout)
    assert parsed["valid"] is True
    assert parsed["language"] == "yor"


def test_self_test_fails_when_inventory_corrupted(monkeypatch):
    """Inject an undeclared latin_extended_additional codepoint into Mandarin and confirm self-test catches it."""
    sys.path.insert(0, str(SCRIPT.parent))
    import ipa_validate  # noqa: E402

    original = set(ipa_validate._IPA_INVENTORY["cmn"]["phonemes"])
    try:
        # ụ U+1EE5 is latin_extended_additional; cmn declares only latin_extended.
        ipa_validate._IPA_INVENTORY["cmn"]["phonemes"] = original | {"ụ"}
        report = ipa_validate._run_self_test()
        assert report["all_passed"] is False
        cmn_entry = next(lang for lang in report["languages"] if lang["iso"] == "cmn")
        assert cmn_entry["issues"], "self-test should have flagged the injected codepoint"
        assert any("U+1EE5" in issue for issue in cmn_entry["issues"])
    finally:
        ipa_validate._IPA_INVENTORY["cmn"]["phonemes"] = original
