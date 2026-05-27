#!/usr/bin/env python3
"""
Programmatic E2E Scenario Runner.

Executes skill scripts in sequence to simulate agent behavior.
Use this for automated testing without a real agent.

Usage:
    python scenario_runner.py --scenario full_pipeline \
        --input datasets/full_pipeline_messy.csv \
        --workspace /tmp/e2e_workspace
"""

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple


SKILLS_DIR = Path(__file__).parent.parent.parent.parent / "skills"


class ScenarioRunner:
    """Execute skill script sequences with checkpoint tracking."""

    def __init__(self, workspace: Path, skills_dir: Path = None):
        self.workspace = Path(workspace)
        self.workspace.mkdir(parents=True, exist_ok=True)
        self.skills_dir = skills_dir or SKILLS_DIR
        self.step = 0
        self.log: List[Dict[str, Any]] = []

    def run_script(self, script_path: str, *args) -> Tuple[Dict[str, Any], int]:
        """Run a skill script and return parsed JSON output + exit code."""
        full_path = self.skills_dir / script_path
        cmd = [sys.executable, str(full_path)] + [str(a) for a in args]

        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=300
        )

        try:
            output = json.loads(result.stdout)
        except json.JSONDecodeError:
            output = {
                "success": False,
                "error": f"Non-JSON output: {result.stdout[:500]}",
                "stderr": result.stderr[:500],
            }

        self.log.append({
            "step": self.step,
            "script": script_path,
            "exit_code": result.returncode,
            "success": output.get("success", False),
        })

        return output, result.returncode

    def checkpoint(self, source_path: str, label: str) -> Path:
        """Copy output to checkpoint file with convention naming."""
        self.step += 1
        src = Path(source_path)
        ckpt = self.workspace / f"ckpt_{self.step:02d}_{label}{src.suffix}"
        if src.exists():
            shutil.copy2(src, ckpt)
        else:
            print(f"  [WARN] Checkpoint source missing: {src}")
        return ckpt

    # ------------------------------------------------------------------
    # Full Pipeline Scenario
    # ------------------------------------------------------------------
    def run_full_pipeline(self, input_csv: Path) -> Dict[str, Any]:
        """load -> profile -> detect_issues -> clean -> validate -> stats -> chart -> report"""
        print("=== Full Pipeline Scenario ===\n")
        results = {}

        # Step 1: Load
        print("[1/7] Loading data...")
        loaded = self.workspace / "loaded.csv"
        r, _ = self.run_script(
            "magic-data-loading/scripts/load_file.py",
            str(input_csv), str(loaded),
        )
        assert r["success"], f"Load failed: {r.get('error')}"
        self.checkpoint(str(loaded), "loaded")
        results["load"] = r

        # Step 2: Profile (quality score)
        print("[2/7] Profiling data quality...")
        profile = self.workspace / "quality.json"
        r, _ = self.run_script(
            "magic-data-profiling/scripts/quality_score.py",
            str(loaded), str(profile),
        )
        assert r["success"], f"Profile failed: {r.get('error')}"
        self.checkpoint(str(profile), "profiled")
        results["profile"] = r

        # Step 3: Clean (handle missing with auto strategy)
        print("[3/7] Cleaning data...")
        cleaned = self.workspace / "cleaned.csv"
        r, _ = self.run_script(
            "magic-data-cleaning/scripts/handle_missing.py",
            str(loaded), str(cleaned),
            "--strategy", "auto",
        )
        assert r["success"], f"Clean failed: {r.get('error')}"
        self.checkpoint(str(cleaned), "cleaned")
        results["clean"] = r

        # Step 4: Validate (sanity check)
        print("[4/7] Validating cleaned data...")
        validated = self.workspace / "validated.json"
        r, _ = self.run_script(
            "magic-data-validation/scripts/sanity_check.py",
            "--input", str(cleaned),
            "--output", str(validated),
        )
        self.checkpoint(str(validated), "validated")
        results["validate"] = r

        # Step 5: Statistics
        print("[5/7] Computing statistics...")
        stats = self.workspace / "stats.json"
        r, _ = self.run_script(
            "magic-statistical-analysis/scripts/descriptive_stats.py",
            "--input", str(cleaned),
            "--output", str(stats),
        )
        assert r["success"], f"Stats failed: {r.get('error')}"
        self.checkpoint(str(stats), "stats")
        results["stats"] = r

        # Step 6: Chart
        print("[6/7] Generating visualization...")
        chart = self.workspace / "chart.png"
        r, _ = self.run_script(
            "magic-data-visualization/scripts/generate_chart.py",
            str(cleaned), str(chart),
            "--chart_type", "histogram",
        )
        assert r["success"], f"Chart failed: {r.get('error')}"
        self.checkpoint(str(chart), "chart")
        results["chart"] = r

        # Step 7: Report
        print("[7/7] Generating report...")
        # Build findings JSON for the report
        findings = {
            "summary": f"Analyzed dataset with {results['load'].get('rows_in', '?')} rows.",
            "data_source": {
                "file": str(input_csv),
                "rows": results["load"].get("rows_in"),
                "columns": results["load"].get("columns", 15),
            },
            "methodology": "Automated pipeline: load, profile, clean, validate, analyze, visualize.",
            "key_findings": [
                {"title": "Quality Score", "description": f"Overall quality: {results['profile'].get('overall_score', 'N/A')}"},
                {"title": "Cleaning Applied", "description": "Missing values handled with auto strategy."},
            ],
            "caveats": [
                "Analysis performed on synthetic test data.",
                "Correlation does not imply causation.",
            ],
            "next_steps": ["Validate with domain expert.", "Test on production data."],
            "visualizations": [{"path": str(chart), "caption": "Distribution histogram"}],
        }
        findings_path = self.workspace / "findings.json"
        findings_path.write_text(json.dumps(findings, indent=2))

        report = self.workspace / "report.md"
        r, _ = self.run_script(
            "magic-report-generation/scripts/generate_report.py",
            str(findings_path), str(report),
        )
        assert r["success"], f"Report failed: {r.get('error')}"
        self.checkpoint(str(report), "report")
        results["report"] = r

        print("\n=== Full Pipeline Complete ===")
        return results

    # ------------------------------------------------------------------
    # Self-Healing Scenario
    # ------------------------------------------------------------------
    def run_self_healing(self, datasets_dir: Path) -> Dict[str, Any]:
        """Test error recovery: encoding, mixed types, wrong delimiter."""
        print("=== Self-Healing Scenario ===\n")
        results = {}

        # Sub-test 1: Encoding recovery
        print("[1/3] Encoding recovery test...")
        latin1_file = datasets_dir / "latin1_encoded.csv"
        loaded_enc = self.workspace / "loaded_encoding.csv"

        # First attempt: default UTF-8 (should fail or produce garbled data)
        r1, _ = self.run_script(
            "magic-data-loading/scripts/load_file.py",
            str(latin1_file), str(loaded_enc),
        )

        # Detect format to find encoding
        fmt_out = self.workspace / "format_detect.json"
        r_fmt, _ = self.run_script(
            "magic-data-loading/scripts/detect_format.py",
            str(latin1_file), str(fmt_out),
        )

        # Retry with detected encoding
        detected_encoding = "latin-1"
        if r_fmt.get("success"):
            detected_encoding = r_fmt.get("encoding", "latin-1")

        loaded_enc2 = self.workspace / "loaded_encoding_fixed.csv"
        r2, _ = self.run_script(
            "magic-data-loading/scripts/load_file.py",
            str(latin1_file), str(loaded_enc2),
            "--encoding", detected_encoding,
        )
        self.checkpoint(str(loaded_enc2), "loaded_encoding")
        results["encoding"] = {
            "first_attempt": r1.get("success", False),
            "detection": r_fmt.get("success", False),
            "retry_success": r2.get("success", False),
        }

        # Sub-test 2: Mixed types recovery
        print("[2/3] Mixed types recovery test...")
        mixed_file = datasets_dir / "mixed_types.csv"
        loaded_mixed = self.workspace / "loaded_mixed.csv"
        r, _ = self.run_script(
            "magic-data-loading/scripts/load_file.py",
            str(mixed_file), str(loaded_mixed),
        )
        self.checkpoint(str(loaded_mixed), "loaded_mixed")

        # Try stats (may warn about mixed types)
        stats_mixed = self.workspace / "stats_mixed.json"
        r_stats, _ = self.run_script(
            "magic-statistical-analysis/scripts/descriptive_stats.py",
            "--input", str(loaded_mixed),
            "--output", str(stats_mixed),
        )
        results["mixed_types"] = {
            "load_success": r.get("success", False),
            "stats_success": r_stats.get("success", False),
        }

        # Sub-test 3: Delimiter recovery
        print("[3/3] Delimiter recovery test...")
        semicolon_file = datasets_dir / "semicolon_delimited.csv"
        loaded_delim = self.workspace / "loaded_delim.csv"

        # First attempt: default comma (will load as 1 column)
        r1, _ = self.run_script(
            "magic-data-loading/scripts/load_file.py",
            str(semicolon_file), str(loaded_delim),
        )

        # Detect format
        fmt_out2 = self.workspace / "format_detect_delim.json"
        r_fmt2, _ = self.run_script(
            "magic-data-loading/scripts/detect_format.py",
            str(semicolon_file), str(fmt_out2),
        )
        detected_delim = ";"
        if r_fmt2.get("success"):
            detected_delim = r_fmt2.get("delimiter", ";")

        # Retry with detected delimiter
        loaded_delim2 = self.workspace / "loaded_delim_fixed.csv"
        r2, _ = self.run_script(
            "magic-data-loading/scripts/load_file.py",
            str(semicolon_file), str(loaded_delim2),
            "--delimiter", detected_delim,
        )
        self.checkpoint(str(loaded_delim2), "loaded_delim")
        results["delimiter"] = {
            "first_attempt_cols": r1.get("columns", 1),
            "detection": r_fmt2.get("success", False),
            "retry_success": r2.get("success", False),
            "retry_cols": r2.get("columns", 0),
        }

        print("\n=== Self-Healing Complete ===")
        return results

    # ------------------------------------------------------------------
    # Text Analysis Scenario
    # ------------------------------------------------------------------
    def run_text_analysis(self, input_jsonl: Path) -> Dict[str, Any]:
        """load JSONL -> distribution_analysis -> detect_patterns -> chart -> report"""
        print("=== Text Analysis Scenario ===\n")
        results = {}

        # Step 1: Load JSONL
        print("[1/5] Loading JSONL data...")
        loaded = self.workspace / "loaded.csv"
        r, _ = self.run_script(
            "magic-data-loading/scripts/load_file.py",
            str(input_jsonl), str(loaded),
        )
        assert r["success"], f"Load failed: {r.get('error')}"
        self.checkpoint(str(loaded), "loaded")
        results["load"] = r

        # Step 2: Distribution analysis (text profiling)
        print("[2/5] Analyzing text distributions...")
        dist = self.workspace / "distributions.json"
        r, _ = self.run_script(
            "magic-data-profiling/scripts/distribution_analysis.py",
            str(loaded), str(dist),
        )
        assert r["success"], f"Distribution analysis failed: {r.get('error')}"
        self.checkpoint(str(dist), "distributions")
        results["distributions"] = r

        # Step 3: Detect patterns
        print("[3/5] Detecting patterns...")
        patterns = self.workspace / "patterns.csv"
        r, _ = self.run_script(
            "magic-data-exploration/scripts/detect_patterns.py",
            str(loaded), str(patterns),
        )
        assert r["success"], f"Pattern detection failed: {r.get('error')}"
        self.checkpoint(str(patterns), "patterns")
        results["patterns"] = r

        # Step 4: Chart
        print("[4/5] Generating visualization...")
        chart = self.workspace / "chart.png"
        r, _ = self.run_script(
            "magic-data-visualization/scripts/generate_chart.py",
            str(loaded), str(chart),
            "--chart_type", "histogram",
        )
        assert r["success"], f"Chart failed: {r.get('error')}"
        self.checkpoint(str(chart), "chart")
        results["chart"] = r

        # Step 5: Report
        print("[5/5] Generating report...")
        findings = {
            "summary": "Text corpus analysis of JSONL dataset.",
            "data_source": {"file": str(input_jsonl), "rows": results["load"].get("rows_in")},
            "methodology": "Text profiling with distribution and pattern analysis.",
            "key_findings": [
                {"title": "Text Distributions", "description": "Analyzed word count and vocabulary distributions."},
            ],
            "caveats": ["Text generated synthetically for testing."],
            "next_steps": ["Apply to real text corpus."],
        }
        findings_path = self.workspace / "findings.json"
        findings_path.write_text(json.dumps(findings, indent=2))

        report = self.workspace / "report.md"
        r, _ = self.run_script(
            "magic-report-generation/scripts/generate_report.py",
            str(findings_path), str(report),
        )
        assert r["success"], f"Report failed: {r.get('error')}"
        self.checkpoint(str(report), "report")
        results["report"] = r

        print("\n=== Text Analysis Complete ===")
        return results

    def save_log(self):
        """Save execution log to workspace."""
        log_path = self.workspace / "runner_log.json"
        log_path.write_text(json.dumps(self.log, indent=2))


def main():
    parser = argparse.ArgumentParser(description="Run E2E scenarios programmatically")
    parser.add_argument("--scenario", required=True,
                        choices=["full_pipeline", "self_healing", "text_analysis"],
                        help="Scenario to execute")
    parser.add_argument("--input", required=True, help="Input file or dataset directory")
    parser.add_argument("--workspace", required=True, help="Workspace directory for outputs")
    parser.add_argument("--skills-dir", default=None, help="Path to skills/ directory")

    args = parser.parse_args()

    workspace = Path(args.workspace)
    skills_dir = Path(args.skills_dir) if args.skills_dir else SKILLS_DIR
    runner = ScenarioRunner(workspace, skills_dir)

    try:
        if args.scenario == "full_pipeline":
            results = runner.run_full_pipeline(Path(args.input))
        elif args.scenario == "self_healing":
            input_path = Path(args.input)
            # self_healing expects a datasets directory, not a single file
            datasets_dir = input_path if input_path.is_dir() else input_path.parent
            results = runner.run_self_healing(datasets_dir)
        elif args.scenario == "text_analysis":
            results = runner.run_text_analysis(Path(args.input))
        else:
            print(f"Unknown scenario: {args.scenario}")
            sys.exit(1)

        runner.save_log()
        print(f"\nOutputs in: {workspace}")
        print(json.dumps({"success": True, "scenario": args.scenario}, indent=2))

    except (AssertionError, Exception) as e:
        runner.save_log()
        print(json.dumps({"success": False, "error": str(e)}, indent=2))
        sys.exit(1)


if __name__ == "__main__":
    main()
