#!/usr/bin/env python3
"""
E2E Scenario Verification Script
===================================
Verifies that a simulation test workspace contains expected outputs.

Supports two modes:
  Synthetic:  python verify_scenario.py --scenario full_pipeline --workspace /path
  Real-data:  python verify_scenario.py --config my_config.json --workspace /path
"""
import argparse
import json
import sys
from pathlib import Path

import pandas as pd


# ── Reusable check functions ─────────────────────────────────────────

def check_file_exists(workspace, pattern, description):
    """Check if files matching pattern exist in workspace."""
    matches = list(Path(workspace).glob(pattern))
    if matches:
        return {"pass": True, "description": description, "files": [str(m) for m in matches]}
    return {"pass": False, "description": description, "error": f"No files matching '{pattern}'"}


def check_json_field(filepath, field, expected_type=None, description=""):
    """Check if a JSON file contains a specific field."""
    try:
        with open(filepath) as f:
            data = json.load(f)
        if field not in data:
            return {"pass": False, "description": description, "error": f"Missing field: {field}"}
        if expected_type and not isinstance(data[field], expected_type):
            return {"pass": False, "description": description,
                    "error": f"Field {field} is {type(data[field]).__name__}, expected {expected_type.__name__}"}
        return {"pass": True, "description": description, "value": str(data[field])[:100]}
    except Exception as e:
        return {"pass": False, "description": description, "error": str(e)}


def check_markdown_sections(filepath, required_sections, description=""):
    """Check if a Markdown file contains required sections."""
    try:
        content = Path(filepath).read_text()
        missing = []
        for section in required_sections:
            if section.lower() not in content.lower():
                missing.append(section)
        if missing:
            return {"pass": False, "description": description, "error": f"Missing sections: {missing}"}
        return {"pass": True, "description": description}
    except Exception as e:
        return {"pass": False, "description": description, "error": str(e)}


def check_csv_rows(workspace, pattern, min_rows, description):
    """Check that a CSV file has at least min_rows rows."""
    matches = list(Path(workspace).glob(pattern))
    if not matches:
        return {"pass": False, "description": description, "error": f"No files matching '{pattern}'"}
    try:
        df = pd.read_csv(matches[0])
        if len(df) >= min_rows:
            return {"pass": True, "description": description, "value": f"{len(df)} rows"}
        return {"pass": False, "description": description,
                "error": f"Expected >= {min_rows} rows, got {len(df)}"}
    except Exception as e:
        return {"pass": False, "description": description, "error": str(e)}


def check_csv_columns(workspace, pattern, expected_columns, description):
    """Check that a CSV file contains expected columns."""
    matches = list(Path(workspace).glob(pattern))
    if not matches:
        return {"pass": False, "description": description, "error": f"No files matching '{pattern}'"}
    try:
        df = pd.read_csv(matches[0], nrows=1)
        missing = [c for c in expected_columns if c not in df.columns]
        if missing:
            return {"pass": False, "description": description,
                    "error": f"Missing columns: {missing}. Found: {list(df.columns)}"}
        return {"pass": True, "description": description}
    except Exception as e:
        return {"pass": False, "description": description, "error": str(e)}


def check_csv_missing_pct(workspace, pattern, max_pct, description):
    """Check that missing data percentage is below threshold."""
    matches = list(Path(workspace).glob(pattern))
    if not matches:
        return {"pass": False, "description": description, "error": f"No files matching '{pattern}'"}
    try:
        df = pd.read_csv(matches[0])
        total = df.size
        missing = df.isnull().sum().sum()
        pct = (missing / total) * 100 if total > 0 else 0
        if pct <= max_pct:
            return {"pass": True, "description": description, "value": f"{pct:.1f}% missing"}
        return {"pass": False, "description": description,
                "error": f"Missing data {pct:.1f}% exceeds max {max_pct}%"}
    except Exception as e:
        return {"pass": False, "description": description, "error": str(e)}


# ── Synthetic scenario verifiers ─────────────────────────────────────

def verify_full_pipeline(workspace):
    """Verify full pipeline scenario outputs."""
    checks = []
    ws = Path(workspace)

    # Checkpoint files
    checks.append(check_file_exists(ws, "ckpt_01_*", "Checkpoint 01 (loaded data) exists"))
    checks.append(check_file_exists(ws, "ckpt_02_*", "Checkpoint 02 (profiled) exists"))
    checks.append(check_file_exists(ws, "ckpt_03_*", "Checkpoint 03 (cleaned) exists"))
    checks.append(check_file_exists(ws, "ckpt_04_*", "Checkpoint 04 (validated) exists"))
    checks.append(check_file_exists(ws, "ckpt_05_*", "Checkpoint 05 (stats) exists"))
    checks.append(check_file_exists(ws, "ckpt_06_*", "Checkpoint 06 (chart) exists"))
    checks.append(check_file_exists(ws, "ckpt_07_*", "Checkpoint 07 (report) exists"))

    # Chart files
    checks.append(check_file_exists(ws, "*.png", "Chart PNG file exists"))

    # Report sections
    report_files = list(ws.glob("ckpt_07_*.md")) + list(ws.glob("*report*.md"))
    if report_files:
        checks.append(check_markdown_sections(
            report_files[0],
            ["Summary", "Data Provenance", "Methodology", "Findings", "Caveats", "Next Steps"],
            "Report contains all 6 mandatory sections"
        ))
    else:
        checks.append({"pass": False, "description": "Report file exists", "error": "No report found"})

    return checks


def verify_self_healing(workspace):
    """Verify self-healing scenario outputs."""
    checks = []
    ws = Path(workspace)

    # Final successful load should exist
    checks.append(check_file_exists(ws, "*.csv", "Successfully loaded data exists"))

    # Check for evidence of retry (multiple load attempts)
    checks.append(check_file_exists(ws, "ckpt_*", "At least one checkpoint exists"))

    # Check for encoding-fixed file
    checks.append(check_file_exists(ws, "*encoding*", "Encoding recovery evidence"))

    # Check for delimiter-fixed file
    checks.append(check_file_exists(ws, "*delim*", "Delimiter recovery evidence"))

    return checks


def verify_text_analysis(workspace):
    """Verify text analysis scenario outputs."""
    checks = []
    ws = Path(workspace)

    checks.append(check_file_exists(ws, "ckpt_01_*", "Loaded data exists"))
    checks.append(check_file_exists(ws, "*.png", "Visualization exists"))
    checks.append(check_file_exists(ws, "*report*.md", "Report exists"))

    # Check for text-specific outputs
    json_files = list(ws.glob("*.json"))
    for jf in json_files:
        try:
            with open(jf) as f:
                data = json.load(f)
            if "distributions" in data and "text" in data["distributions"]:
                checks.append({"pass": True, "description": "Text distribution analysis found"})
                break
        except (json.JSONDecodeError, KeyError):
            continue
    else:
        checks.append({"pass": False, "description": "Text distribution analysis found",
                        "error": "No text distribution data in any JSON output"})

    return checks


# ── Config-based verifier (real-data mode) ───────────────────────────

def verify_from_config(workspace, config_path):
    """Verify scenario outputs based on user-defined config."""
    with open(config_path) as f:
        config = json.load(f)

    checks = []
    ws = Path(workspace)

    # Check output files from config
    for file_check in config.get("verification", {}).get("output_files", []):
        pattern = file_check.get("pattern", "")
        desc = file_check.get("description", "Config-defined file check")
        checks.append(check_file_exists(ws, pattern, desc))

    # Check quality gates
    gates = config.get("verification", {}).get("quality_gates", {})

    if "min_rows_after_cleaning" in gates and gates["min_rows_after_cleaning"] > 0:
        min_rows = gates["min_rows_after_cleaning"]
        # Look for cleaned CSV checkpoint
        checks.append(check_csv_rows(
            ws, "ckpt_*_cleaned*.csv",
            min_rows,
            f"Cleaned data has >= {min_rows} rows"
        ))
        # Fallback: any CSV
        if not list(ws.glob("ckpt_*_cleaned*.csv")):
            checks.append(check_csv_rows(
                ws, "*.csv",
                min_rows,
                f"Output CSV has >= {min_rows} rows"
            ))

    if "max_missing_pct_after_cleaning" in gates:
        max_pct = gates["max_missing_pct_after_cleaning"]
        if max_pct < 100:
            cleaned_csvs = list(ws.glob("ckpt_*_cleaned*.csv")) or list(ws.glob("*.csv"))
            if cleaned_csvs:
                checks.append(check_csv_missing_pct(
                    ws, cleaned_csvs[0].name,
                    max_pct,
                    f"Missing data <= {max_pct}% after cleaning"
                ))

    # Check expected columns survived
    loading_exp = config.get("expectations", {}).get("magic-data-loading", {})
    expected_cols = loading_exp.get("expected_columns", [])
    if expected_cols:
        csv_files = list(ws.glob("ckpt_*_cleaned*.csv")) or list(ws.glob("*.csv"))
        if csv_files:
            checks.append(check_csv_columns(
                ws, csv_files[0].name,
                expected_cols,
                "Expected columns present in output"
            ))

    return checks


# ── Scenario registry ────────────────────────────────────────────────

SCENARIOS = {
    "full_pipeline": verify_full_pipeline,
    "self_healing": verify_self_healing,
    "text_analysis": verify_text_analysis,
}


# ── Main ─────────────────────────────────────────────────────────────

def run_checks(checks, label, workspace):
    """Print results and return JSON summary."""
    passed = sum(1 for c in checks if c["pass"])
    failed = sum(1 for c in checks if not c["pass"])

    print(f"\n{'='*60}")
    print(f"Scenario: {label}")
    print(f"Workspace: {workspace}")
    print(f"{'='*60}\n")

    for c in checks:
        status = "PASS" if c["pass"] else "FAIL"
        print(f"  [{status}] {c['description']}")
        if not c["pass"]:
            print(f"         Error: {c.get('error', 'Unknown')}")

    print(f"\n{'='*60}")
    print(f"Results: {passed} passed, {failed} failed, {len(checks)} total")
    print(f"{'='*60}\n")

    result = {
        "scenario": label,
        "passed": passed,
        "failed": failed,
        "total": len(checks),
        "all_passed": failed == 0,
        "checks": checks,
    }
    print(json.dumps(result, indent=2))
    return result


def main():
    parser = argparse.ArgumentParser(description="Verify E2E simulation test outputs")
    parser.add_argument("--scenario", choices=list(SCENARIOS.keys()),
                        help="Scenario to verify (synthetic mode)")
    parser.add_argument("--config", help="Config file path (real-data mode)")
    parser.add_argument("--workspace", required=True, help="Path to workspace directory")
    parser.add_argument("--checks", default=None, help="Optional path to custom checks JSON")
    args = parser.parse_args()

    if not args.scenario and not args.config:
        parser.error("Must provide either --scenario or --config")

    if not Path(args.workspace).exists():
        print(json.dumps({"error": f"Workspace not found: {args.workspace}"}, indent=2))
        sys.exit(1)

    # Run appropriate verification mode
    if args.config:
        config_path = Path(args.config)
        if not config_path.exists():
            print(json.dumps({"error": f"Config not found: {args.config}"}, indent=2))
            sys.exit(1)
        with open(config_path) as f:
            config = json.load(f)
        label = config.get("scenario_name", "real_data")
        checks = verify_from_config(args.workspace, args.config)
    else:
        label = args.scenario
        checks = SCENARIOS[args.scenario](args.workspace)

    # If custom checks provided, add those too
    if args.checks and Path(args.checks).exists():
        with open(args.checks) as f:
            custom = json.load(f)
        for check in custom.get("checks", []):
            pattern = check.get("pattern", "")
            desc = check.get("description", "Custom check")
            checks.append(check_file_exists(args.workspace, pattern, desc))

    result = run_checks(checks, label, args.workspace)
    sys.exit(0 if result["all_passed"] else 1)


if __name__ == "__main__":
    main()
