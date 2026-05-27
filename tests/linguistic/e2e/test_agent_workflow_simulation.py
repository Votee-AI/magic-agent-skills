"""E2E smoke test — simulate the orchestrator handling a Yoruba query.

Phase 0 version: structural-only. Confirms that:
- The orchestrator SKILL.md mentions Yoruba (or another concrete low-resource language).
- The phase-indicator helper produces a valid format.
- The findings_presenter can render an empty report without errors.
- The interaction_utils can record a decision.

Phase 1+ will replace this with a real LLM-based simulation that calls the
orchestrator and asserts on routed-skill outputs.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
SHARED = REPO_ROOT / "skills" / "_linguistic_shared"
sys.path.insert(0, str(SHARED))

import findings_presenter  # noqa: E402
import interaction_utils  # noqa: E402


def test_orchestrator_mentions_concrete_low_resource_language() -> None:
    p = REPO_ROOT / "skills" / "linguistic-orchestrator" / "SKILL.md"
    text = p.read_text(encoding="utf-8")
    # At least one of these should appear in the orchestrator (used as triage example).
    candidates = ["Yoruba", "Khmer", "Quechua", "Cantonese", "Twi", "Kinyarwanda"]
    hits = [c for c in candidates if c in text]
    assert hits, (
        f"Orchestrator SKILL.md should reference ≥ 1 concrete low-resource language; none of {candidates} found"
    )


def test_phase_indicator_format() -> None:
    s = interaction_utils.phase_indicator(
        phase="Scope",
        language="Yoruba",
        iso="yor",
        resource_class=2,
        skills_routed=["linguistic-scope", "linguistic-ethics"],
    )
    expected_pattern = (
        r"^\[Phase: Scope \| Language: Yoruba \(yor\) \| Resource Class: 2 \| "
        r"Skills routed: linguistic-scope, linguistic-ethics\]$"
    )
    assert re.match(expected_pattern, s), f"phase_indicator output unexpected: {s}"


def test_findings_presenter_empty_report() -> None:
    out = findings_presenter.render_findings_report([])
    assert "# Findings" in out
    assert "## HIGH (0)" in out
    assert "## MEDIUM (0)" in out
    assert "## LOW (0)" in out


def test_findings_presenter_single_finding_routes_correctly() -> None:
    f = findings_presenter.Finding(
        issue_type="bleu_on_mrl",
        severity="HIGH",
        summary="BLEU used as primary metric for Yoruba (morphologically rich)",
        evidence="eval_report.json shows BLEU=0.12 as headline",
        recommended_action="Switch to chrF++ or COMET-22; report BLEU only as secondary",
    )
    assert f.owner_skill == "linguistic-eval"
    rendered = findings_presenter.render_finding(f)
    assert "linguistic-eval" in rendered
    assert "HIGH" in rendered


def test_interaction_utils_records_decision() -> None:
    d = interaction_utils.record_decision(
        workspace_state_path="/tmp/dummy.md",
        title="Choose tokenizer for Yoruba",
        options_considered=["Extend mBART vocab via OFA", "Train new SentencePiece"],
        chosen="Extend mBART vocab via OFA",
        rationale="Class-2 resource; full retrain budget too high",
    )
    md = interaction_utils.render_decision_md(d)
    assert "### Decision: Choose tokenizer for Yoruba" in md
    assert "OFA" in md
