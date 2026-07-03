"""0015-lang-codes-coverage-expansion: ISO 639-3 validity test.

Every LangRecord in lang_codes.py must have an iso639_3 that exists in the
bundled SIL snapshot at skills/_linguistic_shared/data/iso_639_3_snapshot.tsv.
Plus: the 10 NLLB-200-overlap languages must resolve via name AND iso code.
Plus: the 4 macrolangs (orm, mlg, nep, mon) must be detected by is_macrolanguage.
"""

from __future__ import annotations

import csv
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
SHARED_DIR = REPO_ROOT / "skills" / "_linguistic_shared"
SNAPSHOT = SHARED_DIR / "data" / "iso_639_3_snapshot.tsv"
sys.path.insert(0, str(SHARED_DIR))

from lang_codes import _CACHE, is_macrolanguage, resolve_language, subtag_for  # noqa: E402

NEW_LANGUAGES_2026_04_23 = [
    ("Tigrinya", "tir"),
    ("Somali", "som"),
    ("Oromo", "orm"),
    ("Borana Oromo", "gax"),
    ("Afrikaans", "afr"),
    ("Malagasy", "mlg"),
    ("Plateau Malagasy", "plt"),
    ("Sinhala", "sin"),
    ("Nepali", "nep"),
    ("Nepali (individual)", "npi"),
    ("Kyrgyz", "kir"),
    ("Tajik", "tgk"),
    ("Mongolian", "mon"),
    ("Halh Mongolian", "khk"),
]


def _load_snapshot_iso() -> set[str]:
    """Parse the SIL TSV (skipping header comments) and return the set of valid ISO codes."""
    isos: set[str] = set()
    with SNAPSHOT.open(encoding="utf-8") as f:
        # Skip leading comment lines starting with '#'
        lines = [ln for ln in f if not ln.startswith("#")]
    reader = csv.DictReader(lines, delimiter="\t")
    for row in reader:
        if row.get("Id"):
            isos.add(row["Id"].strip())
    return isos


def test_snapshot_exists_and_is_well_formed():
    assert SNAPSHOT.exists(), f"SIL snapshot missing: {SNAPSHOT}"
    isos = _load_snapshot_iso()
    assert len(isos) > 7000, f"snapshot has only {len(isos)} ISO codes (expected ~7900)"


def test_every_record_iso_in_snapshot():
    isos = _load_snapshot_iso()
    bad = sorted({rec.iso639_3 for rec in _CACHE.values()} - isos)
    assert not bad, f"LangRecord iso639_3 codes not in SIL snapshot: {bad}"


@pytest.mark.parametrize("display,iso", NEW_LANGUAGES_2026_04_23)
def test_new_language_resolves_by_display(display: str, iso: str):
    rec = resolve_language(display)
    assert rec.iso639_3 == iso, f"resolve_language({display!r}).iso639_3={rec.iso639_3!r}, expected {iso!r}"


@pytest.mark.parametrize("display,iso", NEW_LANGUAGES_2026_04_23)
def test_new_language_resolves_by_iso(display: str, iso: str):
    rec = resolve_language(iso)
    assert rec.iso639_3 == iso


@pytest.mark.parametrize("name", ["Oromo", "Malagasy", "Nepali", "Mongolian"])
def test_new_macrolanguages_detected(name: str):
    assert is_macrolanguage(name) is True, f"{name} should be detected as a macrolanguage"


def test_subtag_records_have_macrolang_link():
    """Each subtag (gax, plt, npi, khk) must point to a real macrolang record."""
    expected = {"gax": "orm", "plt": "mlg", "npi": "nep", "khk": "mon"}
    iso_to_rec = {r.iso639_3: r for r in _CACHE.values()}
    for subtag, parent_iso in expected.items():
        assert subtag in iso_to_rec, f"subtag record missing: {subtag}"
        assert iso_to_rec[subtag].macrolang == parent_iso, (
            f"{subtag}: macrolang={iso_to_rec[subtag].macrolang!r}, expected {parent_iso!r}"
        )
        assert parent_iso in iso_to_rec, f"parent macrolang record missing: {parent_iso}"


@pytest.mark.parametrize(
    "macrolang,expected_iso",
    [
        ("Chinese", "cmn"),
        ("Arabic", "arb"),
        ("Quechua", "quz"),
        ("Oromo", "gax"),
        ("Malagasy", "plt"),
        ("Nepali", "npi"),
        ("Mongolian", "khk"),
    ],
)
def test_subtag_for_returns_default_high_resource_pick(macrolang: str, expected_iso: str):
    """subtag_for(macrolang) returns the curated default high-resource subtag."""
    rec = subtag_for(macrolang)
    assert rec is not None, f"subtag_for({macrolang!r}) returned None"
    assert rec.iso639_3 == expected_iso, (
        f"subtag_for({macrolang!r}).iso639_3={rec.iso639_3!r}, expected {expected_iso!r}"
    )


def test_subtag_for_returns_none_for_non_macrolang():
    """Individual languages (English, French) have no subtag default."""
    assert subtag_for("English") is None
    assert subtag_for("French") is None


def test_subtag_for_unknown_query_returns_none():
    """Unknown language name returns None gracefully (no KeyError)."""
    assert subtag_for("not-a-real-language-zzz") is None
