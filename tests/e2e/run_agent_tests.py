#!/usr/bin/env python3
"""
Agent Test Orchestrator — Helper for prompt-driven agent testing.

This script provides utilities for the main agent to:
1. Set up workspaces for each conversation script
2. Verify workspace artifacts between turns
3. Score sub-agent behavior from agent_log.md
4. Produce the agent_test_report.json

This is NOT a fully autonomous runner — the main agent drives the
conversation scripts using Task(resume=id). This script helps with
setup, verification, and scoring.

Usage (from the main agent):
    # Setup workspace for a script
    python run_agent_tests.py setup --script T1-01 --workspace /tmp/agent_test

    # Verify artifacts after a turn
    python run_agent_tests.py verify --workspace /tmp/agent_test/T1-01 \
        --expect loaded.csv format.json agent_log.md

    # Score a completed script
    python run_agent_tests.py score --workspace /tmp/agent_test/T1-01

    # Generate aggregate report
    python run_agent_tests.py report --workspace /tmp/agent_test
"""

import argparse
import json
import re
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

DATASETS_DIR = Path(__file__).parent / "datasets"
SCRIPTS_DIR = Path(__file__).parent.parent.parent / "skills"

# Conversation script metadata
SCRIPTS = {
    "T1-01": {
        "name": "Full Pipeline",
        "tier": 1,
        "turns": 7,
        "skills": [
            "magic-data-loading", "magic-data-profiling", "magic-data-cleaning",
            "magic-data-validation", "magic-statistical-analysis",
            "magic-data-visualization", "magic-report-generation",
        ],
        "setup_dataset": "full_pipeline_messy.csv",
        "setup_name": "input.csv",
    },
    "T1-02": {
        "name": "Data Transformation Pipeline",
        "tier": 1,
        "turns": 4,
        "skills": ["magic-data-loading", "magic-data-transformation"],
        "setup_dataset": "full_pipeline_messy.csv",
        "setup_name": "input.csv",
    },
    "T1-03": {
        "name": "Data Validation Pipeline",
        "tier": 1,
        "turns": 3,
        "skills": ["magic-data-loading", "magic-data-validation"],
        "setup_dataset": "full_pipeline_messy.csv",
        "setup_name": "input.csv",
    },
    "T1-04": {
        "name": "Statistical Analysis",
        "tier": 1,
        "turns": 3,
        "skills": ["magic-data-loading", "magic-data-cleaning", "magic-statistical-analysis"],
        "setup_dataset": "full_pipeline_messy.csv",
        "setup_name": "input.csv",
    },
    "T1-05": {
        "name": "Visualization + Reporting",
        "tier": 1,
        "turns": 3,
        "skills": ["magic-data-loading", "magic-data-visualization", "magic-report-generation"],
        "setup_dataset": "full_pipeline_messy.csv",
        "setup_name": "input.csv",
    },
    "T2-01": {
        "name": "The Data Looks Weird",
        "tier": 2,
        "turns": 3,
        "skills": ["magic-data-profiling", "magic-data-cleaning"],
        "setup_dataset": "full_pipeline_messy.csv",
        "setup_name": "input.csv",
    },
    "T2-02": {
        "name": "Can You Profile This?",
        "tier": 2,
        "turns": 2,
        "skills": ["magic-data-profiling"],
        "setup_dataset": "full_pipeline_messy.csv",
        "setup_name": "input.csv",
    },
    "T2-03": {
        "name": "I Think There Are Duplicates",
        "tier": 2,
        "turns": 2,
        "skills": ["magic-data-cleaning"],
        "setup_dataset": "full_pipeline_messy.csv",
        "setup_name": "input.csv",
    },
    "T3-01": {
        "name": "Wrong Encoding",
        "tier": 3,
        "turns": 3,
        "skills": ["magic-data-loading"],
        "setup_dataset": "latin1_encoded.csv",
        "setup_name": "tricky_data.csv",
    },
    "T3-02": {
        "name": "Wrong Delimiter",
        "tier": 3,
        "turns": 3,
        "skills": ["magic-data-loading"],
        "setup_dataset": "semicolon_delimited.csv",
        "setup_name": "data.csv",
    },
    "T3-03": {
        "name": "Non-Existent Column",
        "tier": 3,
        "turns": 2,
        "skills": ["magic-statistical-analysis"],
        "setup_dataset": "full_pipeline_messy.csv",
        "setup_name": "input.csv",
    },
    "T3-04": {
        "name": "Mixed Types in Numeric Column",
        "tier": 3,
        "turns": 3,
        "skills": ["magic-data-loading", "magic-data-cleaning"],
        "setup_dataset": "mixed_types.csv",
        "setup_name": "messy_data.csv",
    },
}


def cmd_setup(args):
    """Set up workspace for a conversation script."""
    script_id = args.script.upper()
    if script_id not in SCRIPTS:
        print(json.dumps({"success": False, "error": f"Unknown script: {script_id}. Available: {list(SCRIPTS.keys())}"}))
        sys.exit(1)

    meta = SCRIPTS[script_id]
    ws = Path(args.workspace) / script_id
    ws.mkdir(parents=True, exist_ok=True)

    # Copy dataset
    src = DATASETS_DIR / meta["setup_dataset"]
    dst = ws / meta["setup_name"]
    if src.exists():
        shutil.copy2(src, dst)
    else:
        print(json.dumps({"success": False, "error": f"Dataset not found: {src}. Run generate_e2e_data.py first."}))
        sys.exit(1)

    print(json.dumps({
        "success": True,
        "script": script_id,
        "name": meta["name"],
        "tier": meta["tier"],
        "turns": meta["turns"],
        "skills": meta["skills"],
        "workspace": str(ws),
        "input_file": str(dst),
        "skills_path": str(SCRIPTS_DIR),
    }, indent=2))


def cmd_verify(args):
    """Verify expected files exist in workspace."""
    ws = Path(args.workspace)
    results = {}
    all_pass = True

    for filename in args.expect:
        path = ws / filename
        exists = path.exists()
        size = path.stat().st_size if exists else 0
        results[filename] = {
            "exists": exists,
            "size": size,
            "pass": exists and size > 0,
        }
        if not (exists and size > 0):
            all_pass = False

    print(json.dumps({
        "success": all_pass,
        "workspace": str(ws),
        "files": results,
    }, indent=2))

    if not all_pass:
        sys.exit(1)


def _split_log_into_steps(log_content: str) -> list:
    """Split agent_log.md into individual step blocks."""
    parts = re.split(r"(?=^## Turn \d+)", log_content, flags=re.MULTILINE)
    return [p.strip() for p in parts if p.strip() and re.match(r"## Turn", p.strip())]


def _step_has_discover(step_text: str) -> bool:
    """Check if a step shows discovery behavior (reading docs/scripts before executing)."""
    patterns = [
        r"SKILL\.md",                          # Explicit SKILL.md reference
        r"Read:.*skills/",                     # Read a skill directory/file
        r"Read:.*scripts/",                    # Read a script to understand interface
        r"Read:.*\.py",                        # Read a Python script
        r"understand\s+(their|the|its)\s+interface",  # Understanding interface
        r"to\s+(understand|check|review|examine)",     # Intent to learn before acting
        r"detect_format",                      # Discovery scripts
        r"detect_issues",
        r"detect_all_issues",
        r"infer_schema",
        r"chart_selector",
        r"validate_statistics",
        r"validate_chart",
        r"validate_report",
        r"content_validator",
        r"text_parser",
        r"prepare_for_exploration",
        r"Identified relevant skills",         # Skill identification
        # Auto-detection patterns
        r"auto[- ]detect",                     # Auto-detection
        r"chardet",                            # Encoding detection library
        r"--strategy\s+auto",                  # Auto strategy flag
        r"--auto-checkpoint",                  # Auto-checkpoint flag
        r"--explain",                          # Explain flag
        r"--flatten-depth",                    # Flatten-depth flag
        # Implicit discovery patterns
        r"Read:.*input.*→.*Decision",          # Reading input file followed by decision
        r"Read:.*\.(csv|json|xlsx).*columns?", # Reading data file and inspecting columns
        r"Detected.*format|encoding|delimiter|type",  # Detection of data characteristics
        r"Analyzed.*structure|columns|schema", # Analysis of data structure
    ]
    return any(re.search(p, step_text, re.IGNORECASE) for p in patterns)


def cmd_score(args):
    """Score a completed conversation script from agent_log.md."""
    ws = Path(args.workspace)
    log_path = ws / "agent_log.md"

    scores = {
        "discover": {"pass": 0, "fail": 0, "na": 0},
        "plan": {"pass": 0, "fail": 0, "na": 0},
        "execute": {"pass": 0, "fail": 0, "na": 0},
        "validate": {"pass": 0, "fail": 0, "na": 0},
        "checkpoint": {"pass": 0, "fail": 0, "na": 0},
    }

    if not log_path.exists():
        print(json.dumps({
            "success": False,
            "error": "agent_log.md not found",
            "scores": scores,
        }, indent=2))
        sys.exit(1)

    log_content = log_path.read_text()

    # Split into individual steps
    steps = _split_log_into_steps(log_content)
    step_count = len(steps)

    # --- Discover: check each step for discovery behavior ---
    for step in steps:
        if _step_has_discover(step):
            scores["discover"]["pass"] += 1
        else:
            # Steps that are pure checkpointing or follow-up don't need discovery
            if re.search(r"checkpoint|Task complete|N/A|parallel execution", step, re.IGNORECASE):
                scores["discover"]["na"] += 1
            else:
                scores["discover"]["fail"] += 1

    # --- Plan: check for decision/reasoning entries per step ---
    for step in steps:
        # Accept explicit "Decision:" or implicit reasoning patterns
        has_explicit_decision = bool(re.search(r"Decision:", step))
        has_implicit_reasoning = bool(re.search(r"(will|need to|should|decided to|chose|selected|plan to|going to)", step, re.IGNORECASE))

        if has_explicit_decision or (has_implicit_reasoning and re.search(r"(Command:|Result:)", step)):
            scores["plan"]["pass"] += 1
        else:
            scores["plan"]["fail"] += 1

    # --- Execute: check for command/result entries per step ---
    for step in steps:
        has_cmd = bool(re.search(r"Command:", step))
        has_result = bool(re.search(r"Result:", step))
        if has_cmd or has_result:
            scores["execute"]["pass"] += 1
        else:
            # Some steps are pure reads or checkpoints, not executions
            scores["execute"]["na"] += 1

    # --- Validate: check for validation file existence ---
    validation_files = list(ws.glob("*valid*")) + list(ws.glob("*sanity*")) + list(ws.glob("*schema_validation*"))
    scores["validate"]["pass"] = len(validation_files)
    if not validation_files:
        scores["validate"]["na"] = 1  # Validation may not apply to all scripts

    # --- Checkpoint: check for ckpt files ---
    ckpt_files = list(ws.glob("ckpt_*"))
    scores["checkpoint"]["pass"] = len(ckpt_files)
    if not ckpt_files:
        # Check if checkpointing was requested/mentioned in the log
        checkpoint_requested = bool(re.search(r"checkpoint|ckpt_", log_content, re.IGNORECASE))
        if checkpoint_requested:
            scores["checkpoint"]["fail"] = 1  # Requested but not created
        else:
            scores["checkpoint"]["na"] = 1    # Not requested, so N/A

    # --- Self-healing scoring (check for error recovery patterns) ---
    self_healing = None
    error_patterns = [
        r"error", r"fail(?:ed|ure)?", r"wrong", r"incorrect",
        r"garbled", r"can't decode", r"codec", r"UnicodeDecodeError",
        r"not found", r"missing column", r"KeyError",
    ]
    recovery_patterns = [
        r"retry", r"re-?load", r"recover", r"fix(?:ed)?",
        r"detect_format", r"detect_issues", r"correct encoding",
        r"correct delimiter", r"re-?run", r"attempt\s*\d",
    ]
    error_mentions = any(re.search(p, log_content, re.IGNORECASE) for p in error_patterns)
    recovery_mentions = any(re.search(p, log_content, re.IGNORECASE) for p in recovery_patterns)

    if error_mentions:
        self_healing = {
            "error_detection": "pass",
            "diagnosis": "pass" if recovery_mentions else "fail",
            "recovery": "unknown",  # Needs manual check of final output files
        }

    # --- Compute summary ---
    total_pass = sum(scores[p]["pass"] for p in scores)
    total_checks = total_pass + sum(scores[p]["fail"] for p in scores)
    pass_rate = total_pass / total_checks if total_checks > 0 else 0.0

    print(json.dumps({
        "success": True,
        "workspace": str(ws),
        "steps_logged": step_count,
        "phase_scores": scores,
        "pass_rate": round(pass_rate, 3),
        "self_healing": self_healing,
    }, indent=2))


def cmd_report(args):
    """Generate aggregate test report from scored workspaces."""
    ws = Path(args.workspace)
    report = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "summary": {
            "total_scripts": 0,
            "passed": 0,
            "failed": 0,
            "pass_rate": 0.0,
            "tier_breakdown": {},
            "skill_breakdown": {},
        },
        "scripts": [],
    }

    for script_id, meta in SCRIPTS.items():
        script_ws = ws / script_id
        if not script_ws.exists():
            continue

        report["summary"]["total_scripts"] += 1

        # Check if score file exists (main agent should run score first)
        log_path = script_ws / "agent_log.md"
        has_log = log_path.exists()

        # Basic pass/fail: check if key output files exist
        has_outputs = any(script_ws.glob("*.csv")) or any(script_ws.glob("*.json"))

        passed = has_log and has_outputs
        if passed:
            report["summary"]["passed"] += 1
        else:
            report["summary"]["failed"] += 1

        tier = f"tier_{meta['tier']}"
        if tier not in report["summary"]["tier_breakdown"]:
            report["summary"]["tier_breakdown"][tier] = {"total": 0, "passed": 0}
        report["summary"]["tier_breakdown"][tier]["total"] += 1
        if passed:
            report["summary"]["tier_breakdown"][tier]["passed"] += 1

        for skill in meta["skills"]:
            if skill not in report["summary"]["skill_breakdown"]:
                report["summary"]["skill_breakdown"][skill] = {"tested": 0, "passed": 0}
            report["summary"]["skill_breakdown"][skill]["tested"] += 1
            if passed:
                report["summary"]["skill_breakdown"][skill]["passed"] += 1

        report["scripts"].append({
            "name": f"{script_id}: {meta['name']}",
            "tier": meta["tier"],
            "skills_tested": meta["skills"],
            "turns": meta["turns"],
            "has_action_log": has_log,
            "has_outputs": has_outputs,
            "overall": "pass" if passed else "fail",
            "workspace_path": str(script_ws),
            "action_log_path": str(log_path) if has_log else None,
        })

    total = report["summary"]["total_scripts"]
    if total > 0:
        report["summary"]["pass_rate"] = report["summary"]["passed"] / total

        for tier_data in report["summary"]["tier_breakdown"].values():
            if tier_data["total"] > 0:
                tier_data["pass_rate"] = tier_data["passed"] / tier_data["total"]

    # Check overall pass against thresholds
    tiers = report["summary"]["tier_breakdown"]
    t1 = tiers.get("tier_1", {})
    t2 = tiers.get("tier_2", {})
    t3 = tiers.get("tier_3", {})

    t1_pass = t1.get("pass_rate", 0) == 1.0 if t1.get("total", 0) > 0 else True
    t2_pass = t2.get("pass_rate", 0) >= 0.8 if t2.get("total", 0) > 0 else True
    t3_pass = t3.get("pass_rate", 0) >= 0.6 if t3.get("total", 0) > 0 else True

    report["summary"]["overall_pass"] = t1_pass and t2_pass and t3_pass

    # Write report
    report_path = ws / "agent_test_report.json"
    report_path.write_text(json.dumps(report, indent=2))

    print(json.dumps(report, indent=2))


def main():
    parser = argparse.ArgumentParser(description="Agent Test Orchestrator")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # setup
    p_setup = subparsers.add_parser("setup", help="Set up workspace for a script")
    p_setup.add_argument("--script", required=True, help="Script ID (e.g., T1-01)")
    p_setup.add_argument("--workspace", required=True, help="Base workspace directory")

    # verify
    p_verify = subparsers.add_parser("verify", help="Verify expected files exist")
    p_verify.add_argument("--workspace", required=True, help="Script workspace directory")
    p_verify.add_argument("--expect", nargs="+", required=True, help="Expected filenames")

    # score
    p_score = subparsers.add_parser("score", help="Score agent_log.md")
    p_score.add_argument("--workspace", required=True, help="Script workspace directory")

    # report
    p_report = subparsers.add_parser("report", help="Generate aggregate report")
    p_report.add_argument("--workspace", required=True, help="Base workspace directory")

    args = parser.parse_args()

    if args.command == "setup":
        cmd_setup(args)
    elif args.command == "verify":
        cmd_verify(args)
    elif args.command == "score":
        cmd_score(args)
    elif args.command == "report":
        cmd_report(args)


if __name__ == "__main__":
    main()
