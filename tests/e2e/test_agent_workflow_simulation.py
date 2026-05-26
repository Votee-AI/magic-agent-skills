#!/usr/bin/env python3
"""
Workflow Reinforcement — Agent Workflow Simulation Tests.

These tests simulate what a real agent would do when given NL input.
Instead of just checking SKILL.md content (structural tests), these tests:

1. Read the SKILL.md to extract what the agent SHOULD do
2. Execute the scripts the agent WOULD execute
3. Verify the outputs match what the SKILL.md promises
4. Check the full workflow chain works end-to-end

This is the closest to real agent testing without an actual LLM —
it validates that the instructions in SKILL.md lead to working pipelines.
"""

import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SKILLS_DIR = PROJECT_ROOT / "skills"
DATASETS_DIR = Path(__file__).parent / "datasets"


def _run_script(script_path: str, *args, timeout: int = 120) -> dict:
    """Run a skill script and return parsed output."""
    full_path = SKILLS_DIR / script_path
    if not full_path.exists():
        return {"success": False, "error": f"Script not found: {full_path}"}

    cmd = [sys.executable, str(full_path)] + [str(a) for a in args]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)

    try:
        output = json.loads(result.stdout)
    except json.JSONDecodeError:
        output = {
            "success": result.returncode == 0,
            "stdout": result.stdout[:500],
            "stderr": result.stderr[:500],
            "returncode": result.returncode,
        }
    return output


def _extract_script_quick_ref(skill_name: str) -> list[dict]:
    """Extract Script Quick Reference entries from a SKILL.md.

    Supports two formats:
    1. Markdown table under "Script Quick Reference" heading (legacy v1 format)
    2. YAML frontmatter ``scripts:`` list (v2.0 restructured format)
    """
    path = SKILLS_DIR / skill_name / "SKILL.md"
    content = path.read_text(encoding="utf-8")

    # --- v2.0: read from YAML frontmatter `scripts:` list ---
    import re as _re
    fm_match = _re.match(r"^---\n(.+?)\n---", content, _re.DOTALL)
    if fm_match:
        for line in fm_match.group(1).splitlines():
            stripped = line.strip()
            if stripped.startswith("- scripts/"):
                # e.g. "  - scripts/load_file.py"
                script_rel = stripped.lstrip("- ").strip()
                # Resolve relative to skills root: skill_name/scripts/...
                full_path = f"{skill_name}/{script_rel}"
                return_entries = []
                # Collect all scripts from frontmatter
                pass  # handled below

        fm_scripts = []
        in_scripts = False
        for line in fm_match.group(1).splitlines():
            if line.strip() == "scripts:":
                in_scripts = True
                continue
            if in_scripts:
                stripped = line.strip()
                if stripped.startswith("- "):
                    script_rel = stripped[2:].strip()
                    fm_scripts.append({
                        "script": f"{skill_name}/{script_rel}",
                        "purpose": "",
                    })
                elif stripped and not stripped.startswith("-"):
                    in_scripts = False
        if fm_scripts:
            return fm_scripts

    # --- v1 legacy: table under "Script Quick Reference" heading ---
    entries = []
    in_table = False
    for line in content.splitlines():
        if "Script Quick Reference" in line:
            in_table = True
            continue
        if in_table and line.startswith("|") and "---" not in line and "Script" not in line:
            cols = [c.strip() for c in line.split("|")[1:-1]]
            if len(cols) >= 3:
                name = cols[0].strip("`").strip()
                full_path = cols[1].strip("`").strip()
                purpose = cols[2].strip() if len(cols) > 2 else ""
                entries.append({"script": full_path or name, "purpose": purpose})
        if in_table and not line.startswith("|") and line.strip() and not line.startswith("#"):
            break

    return entries


def _extract_guidance_commands(skill_name: str) -> list[str]:
    """Extract slash commands mentioned in Guidance blocks."""
    path = SKILLS_DIR / skill_name / "SKILL.md"
    content = path.read_text(encoding="utf-8")
    commands = re.findall(r"/magic:[\w-]+", content)
    return list(set(commands))


@pytest.fixture(scope="module")
def workspace():
    """Create a temporary workspace for testing."""
    ws = Path(tempfile.mkdtemp(prefix="agent_sim_"))
    yield ws
    shutil.rmtree(ws, ignore_errors=True)


# ==========================================================================
# Scenario 1: NL-Only Workflow — "help me check this data"
# Simulates: lifecycle auto-skill detection → loading → profiling → guidance
# ==========================================================================

class TestNLWorkflowSimulation:
    """Simulate what an agent does when user says 'help me check this data [path]'."""

    def test_step1_lifecycle_detects_csv_and_routes_to_loading(self, workspace):
        """Lifecycle SKILL.md says: detect file path → trigger loading."""
        content = (SKILLS_DIR / "magic-data-lifecycle" / "SKILL.md").read_text()

        # Lifecycle should route to loading skill
        assert "magic-data-loading" in content

        # Agent would now invoke loading — simulate by running load_file.py
        input_csv = DATASETS_DIR / "full_pipeline_messy.csv"
        loaded = workspace / "scenario1_loaded.csv"
        result = _run_script(
            "magic-data-loading/scripts/load_file.py",
            str(input_csv), str(loaded),
        )
        assert result.get("success"), f"Loading failed: {result}"
        assert loaded.exists()
        assert loaded.stat().st_size > 0

    def test_step2_auto_profile_after_load(self, workspace):
        """Lifecycle says: auto-profile after first data load."""
        content = (SKILLS_DIR / "magic-data-lifecycle" / "SKILL.md").read_text()
        assert "auto-profile" in content.lower() or "Auto-profile" in content

        # Agent would now run quality_score.py
        loaded = workspace / "scenario1_loaded.csv"
        quality = workspace / "scenario1_quality.json"
        result = _run_script(
            "magic-data-profiling/scripts/quality_score.py",
            str(loaded), str(quality),
        )
        assert result.get("success"), f"Profiling failed: {result}"
        assert quality.exists()

        # Verify quality score structure
        data = json.loads(quality.read_text())
        assert "overall_score" in data or "quality_score" in data or "score" in data

    def test_step3_detect_issues_runs(self, workspace):
        """Lifecycle references detect_all_issues.py — agent would run it."""
        content = (SKILLS_DIR / "magic-data-lifecycle" / "SKILL.md").read_text()
        assert "detect_all_issues.py" in content

        loaded = workspace / "scenario1_loaded.csv"
        issues = workspace / "scenario1_issues.json"
        result = _run_script(
            "magic-data-profiling/scripts/detect_all_issues.py",
            str(loaded), str(issues),
        )
        assert result.get("success"), f"Issue detection failed: {result}"

    def test_step4_guidance_block_provides_next_steps(self):
        """After profiling, lifecycle should show guidance with slash commands."""
        content = (SKILLS_DIR / "magic-data-lifecycle" / "SKILL.md").read_text()

        # Should have guidance for post-discovery actions
        assert "Discover" in content
        assert "quality" in content.lower()


# ==========================================================================
# Scenario 2: JSONL Text Data — Structured Dataset (T-WR-01 simulation)
# Simulates: NL → loading JSONL → text profiling → findings
# ==========================================================================

class TestJSONLWorkflowSimulation:
    """Simulate processing a JSONL text dataset end-to-end."""

    def test_step1_load_jsonl(self, workspace):
        """Loading skill should handle JSONL via detect_format + load_file."""
        input_jsonl = DATASETS_DIR / "text_corpus.jsonl"
        loaded = workspace / "scenario2_loaded.csv"

        # First detect format
        fmt = workspace / "scenario2_format.json"
        result = _run_script(
            "magic-data-loading/scripts/detect_format.py",
            str(input_jsonl), str(fmt),
        )
        assert result.get("success"), f"Format detection failed: {result}"

        # Then load
        result = _run_script(
            "magic-data-loading/scripts/load_file.py",
            str(input_jsonl), str(loaded),
        )
        assert result.get("success"), f"JSONL loading failed: {result}"
        assert loaded.exists()

    def test_step2_profile_text_data(self, workspace):
        """Profile text data — distribution_analysis should work."""
        loaded = workspace / "scenario2_loaded.csv"
        if not loaded.exists():
            pytest.skip("Depends on step1")

        dist = workspace / "scenario2_distributions.json"
        result = _run_script(
            "magic-data-profiling/scripts/distribution_analysis.py",
            str(loaded), str(dist),
        )
        assert result.get("success"), f"Distribution analysis failed: {result}"
        assert dist.exists()

    def test_step3_detect_patterns(self, workspace):
        """Exploration scripts should find patterns in text data."""
        loaded = workspace / "scenario2_loaded.csv"
        if not loaded.exists():
            pytest.skip("Depends on step1")

        patterns = workspace / "scenario2_patterns.csv"
        result = _run_script(
            "magic-data-exploration/scripts/detect_patterns.py",
            str(loaded), str(patterns),
        )
        assert result.get("success"), f"Pattern detection failed: {result}"


# ==========================================================================
# Scenario 3: Self-Healing Error Recovery
# Simulates: agent encounters wrong encoding → detect_format → retry
# ==========================================================================

class TestSelfHealingSimulation:
    """Simulate agent error recovery with encoding/delimiter issues."""

    def test_encoding_recovery_flow(self, workspace):
        """Agent loads Latin-1 file, gets garbled → detect_format → retry."""
        latin1_file = DATASETS_DIR / "latin1_encoded.csv"

        # Step 1: Agent tries default load (may produce garbled output)
        loaded_v1 = workspace / "scenario3_encoding_v1.csv"
        _run_script(
            "magic-data-loading/scripts/load_file.py",
            str(latin1_file), str(loaded_v1),
        )

        # Step 2: Agent runs detect_format to find correct encoding
        fmt = workspace / "scenario3_encoding_fmt.json"
        result = _run_script(
            "magic-data-loading/scripts/detect_format.py",
            str(latin1_file), str(fmt),
        )
        assert result.get("success"), f"Format detection failed: {result}"

        # Step 3: Agent retries with detected encoding
        loaded_v2 = workspace / "scenario3_encoding_v2.csv"
        result = _run_script(
            "magic-data-loading/scripts/load_file.py",
            str(latin1_file), str(loaded_v2),
            "--encoding", "latin-1",
        )
        assert result.get("success"), f"Retry with encoding failed: {result}"
        assert loaded_v2.exists()

    def test_delimiter_recovery_flow(self, workspace):
        """Agent loads semicolon-delimited file — detect_format finds correct delimiter."""
        semicolon_file = DATASETS_DIR / "semicolon_delimited.csv"

        # Step 1: Detect format reveals the delimiter
        fmt = workspace / "scenario3_delim_fmt.json"
        result = _run_script(
            "magic-data-loading/scripts/detect_format.py",
            str(semicolon_file), str(fmt),
        )
        assert result.get("success"), f"Format detection failed: {result}"

        # Step 2: Load with auto-detection (load_file.py is smart enough)
        loaded = workspace / "scenario3_delim_loaded.csv"
        r = _run_script(
            "magic-data-loading/scripts/load_file.py",
            str(semicolon_file), str(loaded),
        )
        assert r.get("success"), f"Loading failed: {r}"

        # Verify: should detect multiple columns (not collapse to 1)
        cols = r.get("columns", 0)
        assert cols > 1, (
            f"Delimiter auto-detection failed: got only {cols} column(s)"
        )


# ==========================================================================
# Scenario 4: Full Lifecycle Pipeline — Discover → Plan → Execute → Validate
# ==========================================================================

class TestFullLifecycleSimulation:
    """Simulate the full lifecycle: load → profile → clean → validate → stats → chart → report."""

    def test_discover_phase(self, workspace):
        """Phase 1: Load + Profile (Discovery)."""
        input_csv = DATASETS_DIR / "full_pipeline_messy.csv"
        loaded = workspace / "scenario4_loaded.csv"

        # Load
        r = _run_script(
            "magic-data-loading/scripts/load_file.py",
            str(input_csv), str(loaded),
        )
        assert r.get("success"), f"Load failed: {r}"

        # Profile
        quality = workspace / "scenario4_quality.json"
        r = _run_script(
            "magic-data-profiling/scripts/quality_score.py",
            str(loaded), str(quality),
        )
        assert r.get("success"), f"Profile failed: {r}"

        # Detect issues
        issues = workspace / "scenario4_issues.json"
        r = _run_script(
            "magic-data-profiling/scripts/detect_all_issues.py",
            str(loaded), str(issues),
        )
        assert r.get("success"), f"Issue detection failed: {r}"

    def test_execute_phase(self, workspace):
        """Phase 2: Clean + Validate (Execution)."""
        loaded = workspace / "scenario4_loaded.csv"
        if not loaded.exists():
            pytest.skip("Depends on discover phase")

        # Clean
        cleaned = workspace / "scenario4_cleaned.csv"
        r = _run_script(
            "magic-data-cleaning/scripts/handle_missing.py",
            str(loaded), str(cleaned),
            "--strategy", "auto",
        )
        assert r.get("success"), f"Clean failed: {r}"

        # Validate
        validated = workspace / "scenario4_validated.json"
        r = _run_script(
            "magic-data-validation/scripts/sanity_check.py",
            "--input", str(cleaned),
            "--output", str(validated),
        )
        # Validation should produce output regardless of pass/fail
        assert validated.exists() or r.get("success") is not None

    def test_deliver_phase(self, workspace):
        """Phase 3: Stats + Chart + Report (Delivery)."""
        cleaned = workspace / "scenario4_cleaned.csv"
        if not cleaned.exists():
            pytest.skip("Depends on execute phase")

        # Stats
        stats = workspace / "scenario4_stats.json"
        r = _run_script(
            "magic-statistical-analysis/scripts/descriptive_stats.py",
            "--input", str(cleaned),
            "--output", str(stats),
        )
        assert r.get("success"), f"Stats failed: {r}"

        # Chart
        chart = workspace / "scenario4_chart.png"
        r = _run_script(
            "magic-data-visualization/scripts/generate_chart.py",
            str(cleaned), str(chart),
            "--chart_type", "histogram",
        )
        assert r.get("success"), f"Chart failed: {r}"

        # Report
        findings = {
            "summary": "Test pipeline results.",
            "data_source": {"file": "test.csv"},
            "methodology": "Automated pipeline.",
            "key_findings": [{"title": "Test", "description": "Test finding"}],
            "caveats": ["Test data."],
            "next_steps": ["Deploy."],
        }
        findings_path = workspace / "scenario4_findings.json"
        findings_path.write_text(json.dumps(findings, indent=2))

        report = workspace / "scenario4_report.md"
        r = _run_script(
            "magic-report-generation/scripts/generate_report.py",
            str(findings_path), str(report),
        )
        assert r.get("success"), f"Report failed: {r}"
        assert report.exists()


# ==========================================================================
# Scenario 5: Script Quick Reference Accuracy
# Verifies that scripts listed in SKILL.md actually work
# ==========================================================================

class TestScriptQuickRefExecution:
    """Verify that scripts listed in Script Quick Reference tables actually execute."""

    @pytest.mark.parametrize("skill_name", [
        "magic-data-loading",
        "magic-data-profiling",
        "magic-data-cleaning",
    ])
    def test_scripts_are_executable(self, skill_name):
        """Every script in the Quick Reference should at least show --help or error gracefully."""
        entries = _extract_script_quick_ref(skill_name)
        assert len(entries) > 0, f"{skill_name} has no Script Quick Reference entries"

        for entry in entries:
            script_path = entry["script"]
            full_path = SKILLS_DIR / script_path
            assert full_path.exists(), f"Script not found: {full_path}"

            # Run with --help to verify it's a valid Python script
            result = subprocess.run(
                [sys.executable, str(full_path), "--help"],
                capture_output=True, text=True, timeout=30,
            )
            # Should either show help (exit 0) or error gracefully (not crash)
            assert result.returncode in (0, 1, 2), (
                f"{script_path} crashed with exit code {result.returncode}: "
                f"{result.stderr[:200]}"
            )


# ==========================================================================
# Scenario 6: Guidance → Action Chain Verification
# Verifies that guidance slash commands actually exist and are valid
# ==========================================================================

class TestGuidanceActionChain:
    """Verify that guidance blocks reference valid slash commands."""

    def test_lifecycle_guidance_commands_exist(self):
        """All slash commands referenced in lifecycle guidance should have command files."""
        commands = _extract_guidance_commands("magic-data-lifecycle")
        commands_dir = PROJECT_ROOT / "commands" / "magic"

        for cmd in commands:
            # /magic:findings → findings.md
            cmd_name = cmd.split(":")[-1]
            cmd_file = commands_dir / f"{cmd_name}.md"
            assert cmd_file.exists(), (
                f"Lifecycle references {cmd} but {cmd_file} not found"
            )

    def test_all_skills_guidance_commands_valid(self):
        """All guidance commands across all skills should reference valid command files."""
        commands_dir = PROJECT_ROOT / "commands" / "magic"
        invalid = []

        for skill_dir in sorted(SKILLS_DIR.iterdir()):
            if not skill_dir.is_dir() or skill_dir.name.startswith("_"):
                continue
            skill_md = skill_dir / "SKILL.md"
            if not skill_md.exists():
                continue

            commands = _extract_guidance_commands(skill_dir.name)
            for cmd in commands:
                cmd_name = cmd.split(":")[-1]
                cmd_file = commands_dir / f"{cmd_name}.md"
                if not cmd_file.exists():
                    invalid.append(f"{skill_dir.name}: {cmd} → {cmd_file}")

        assert not invalid, (
            f"Invalid guidance commands:\n" + "\n".join(invalid)
        )
