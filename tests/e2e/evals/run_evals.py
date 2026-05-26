#!/usr/bin/env python3
"""
Eval runner for evals.json (Anthropic assertion format).

Sends each eval prompt to an LLM with the relevant SKILL.md loaded,
then checks the response against structured assertions.

Usage:
    # Run all evals with Anthropic API
    python run_evals.py --all

    # Run with local LM Studio
    python run_evals.py --all --provider lmstudio

    # Run specific skill with delay between calls
    python run_evals.py --skill magic-data-synthesis --delay 5

    # Run with custom LM Studio model
    python run_evals.py --all --provider lmstudio --model qwen/qwen3.5-35b-a3b

    # Dry run
    python run_evals.py --all --dry-run

    # Check assertions against a pre-existing response file
    python run_evals.py --skill magic-data-synthesis --check-file response.txt

Providers:
    anthropic  — Anthropic API (requires ANTHROPIC_API_KEY)
    lmstudio   — Local LM Studio OpenAI-compatible API (http://localhost:1234)
    claude-cli — Claude Code CLI (claude --print)
    auto       — Try anthropic → lmstudio → claude-cli (default)
"""

import argparse
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

SKILLS_DIR = Path(__file__).parent.parent.parent.parent / "skills"
EVALS_DIR = Path(__file__).parent

DEFAULT_LMSTUDIO_URL = "http://localhost:1234/v1"
DEFAULT_LMSTUDIO_MODEL = "qwen/qwen3.5-35b-a3b"
DEFAULT_TIMEOUT = 120


def load_evals(skill_name: str) -> dict:
    evals_path = SKILLS_DIR / skill_name / "evals" / "evals.json"
    if not evals_path.exists():
        print(f"ERROR: {evals_path} not found")
        sys.exit(1)
    return json.load(open(evals_path))


def load_skill_md(skill_name: str) -> str:
    skill_path = SKILLS_DIR / skill_name / "SKILL.md"
    if not skill_path.exists():
        print(f"ERROR: {skill_path} not found")
        sys.exit(1)
    return skill_path.read_text()


def check_assertions(response: str, assertions: list) -> list:
    results = []
    response_lower = response.lower()

    for assertion in assertions:
        atype = assertion["type"]
        values = assertion["values"]

        if atype == "must_contain_one":
            found = any(v.lower() in response_lower for v in values)
            matched = [v for v in values if v.lower() in response_lower]
            results.append({
                "type": atype,
                "values": values,
                "passed": found,
                "detail": f"matched: {matched}" if found else "none matched",
            })

        elif atype == "must_not_contain":
            violations = [v for v in values if v.lower() in response_lower]
            passed = len(violations) == 0
            results.append({
                "type": atype,
                "values": values,
                "passed": passed,
                "detail": f"violations: {violations}" if not passed else "clean",
            })

        else:
            results.append({
                "type": atype,
                "values": values,
                "passed": False,
                "detail": f"unknown assertion type: {atype}",
            })

    return results


def build_prompt(prompt: str, skill_md: str) -> str:
    return f"""You are an AI data agent with the following skill loaded:

<skill>
{skill_md}
</skill>

Now handle this task:

{prompt}

Provide your plan and approach. Explain what tools, methods, and steps you would use."""


def call_anthropic(full_prompt: str, timeout: int) -> str:
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise RuntimeError("ANTHROPIC_API_KEY not set")
    import anthropic
    client = anthropic.Anthropic(api_key=api_key)
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2000,
        messages=[{"role": "user", "content": full_prompt}],
        timeout=timeout,
    )
    return response.content[0].text


def call_lmstudio(full_prompt: str, model: str, base_url: str, timeout: int) -> str:
    import urllib.request
    import urllib.error

    payload = json.dumps({
        "model": model,
        "messages": [{"role": "user", "content": full_prompt}],
        "max_tokens": 2000,
        "temperature": 0.7,
    }).encode("utf-8")

    req = urllib.request.Request(
        f"{base_url}/chat/completions",
        data=payload,
        headers={"Content-Type": "application/json"},
    )

    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            content = data["choices"][0]["message"]["content"]
            if not content or content.strip() == "":
                reasoning = data["choices"][0]["message"].get("reasoning_content", "")
                if reasoning:
                    content = reasoning
            return content
    except urllib.error.URLError as e:
        raise RuntimeError(f"LM Studio request failed: {e}")
    except (KeyError, IndexError) as e:
        raise RuntimeError(f"LM Studio response parse error: {e}")


def call_claude_cli(full_prompt: str, timeout: int) -> str:
    result = subprocess.run(
        ["claude", "--print", "-p", full_prompt],
        capture_output=True, text=True, timeout=timeout,
    )
    if result.returncode == 0 and result.stdout.strip():
        return result.stdout.strip()
    raise RuntimeError(f"Claude CLI failed: {result.stderr[:200]}")


def call_llm(prompt: str, skill_md: str, provider: str, model: str,
             base_url: str, timeout: int) -> str:
    full_prompt = build_prompt(prompt, skill_md)
    errors = []

    providers_to_try = []
    if provider == "auto":
        providers_to_try = ["anthropic", "lmstudio", "claude-cli"]
    else:
        providers_to_try = [provider]

    for p in providers_to_try:
        try:
            if p == "anthropic":
                return call_anthropic(full_prompt, timeout)
            elif p == "lmstudio":
                return call_lmstudio(full_prompt, model, base_url, timeout)
            elif p == "claude-cli":
                return call_claude_cli(full_prompt, timeout)
        except Exception as e:
            errors.append(f"{p}: {e}")
            continue

    print(f"ERROR: All providers failed:")
    for err in errors:
        print(f"  {err}")
    sys.exit(1)


def run_eval(skill_name: str, eval_data: dict, skill_md: str,
             provider: str, model: str, base_url: str, timeout: int,
             dry_run: bool = False, check_file: str = None):
    name = eval_data["name"]
    prompt = eval_data["prompt"]
    assertions = eval_data["assertions"]
    difficulty = eval_data.get("difficulty", "")

    print(f"\n{'='*60}")
    print(f"Eval: {name} ({difficulty})" if difficulty else f"Eval: {name}")
    print(f"Prompt: {prompt[:100]}...")
    print(f"Assertions: {len(assertions)}")

    if dry_run:
        print("  [DRY RUN] Would check:")
        for a in assertions:
            print(f"    {a['type']}: {a['values']}")
        return {"name": name, "status": "dry_run"}

    if check_file:
        response = Path(check_file).read_text()
        print(f"  Using pre-existing response from {check_file}")
    else:
        provider_label = provider if provider != "auto" else "auto-detect"
        print(f"  Calling LLM ({provider_label})...")
        try:
            response = call_llm(prompt, skill_md, provider, model, base_url, timeout)
            print(f"  Response length: {len(response)} chars")
        except SystemExit:
            return {"name": name, "status": "ERROR", "passed": 0, "total": len(assertions)}

    results = check_assertions(response, assertions)

    passed_count = sum(1 for r in results if r["passed"])
    total = len(results)
    all_passed = passed_count == total

    status = "PASS" if all_passed else "FAIL"
    print(f"  Result: {status} ({passed_count}/{total} assertions)")

    for r in results:
        icon = "✓" if r["passed"] else "✗"
        print(f"    {icon} {r['type']}: {r['values'][:3]}... → {r['detail']}")

    return {
        "name": name,
        "status": status,
        "passed": passed_count,
        "total": total,
        "assertions": results,
        "response_preview": response[:200] if not dry_run else None,
    }


def main():
    parser = argparse.ArgumentParser(description="Run evals.json against an LLM")
    parser.add_argument("--skill", help="Skill name (e.g., magic-data-synthesis)")
    parser.add_argument("--all", action="store_true", help="Run all skills")
    parser.add_argument("--eval", help="Specific eval name to run")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be tested")
    parser.add_argument("--check-file", help="Check assertions against existing response file")
    parser.add_argument("--cross-skill", action="store_true", help="Run cross-skill E2E evals")
    parser.add_argument("--provider", default="auto",
                        choices=["auto", "anthropic", "lmstudio", "claude-cli"],
                        help="LLM provider (default: auto)")
    parser.add_argument("--model", default=DEFAULT_LMSTUDIO_MODEL,
                        help=f"Model for LM Studio (default: {DEFAULT_LMSTUDIO_MODEL})")
    parser.add_argument("--base-url", default=DEFAULT_LMSTUDIO_URL,
                        help=f"LM Studio base URL (default: {DEFAULT_LMSTUDIO_URL})")
    parser.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT,
                        help=f"Timeout per request in seconds (default: {DEFAULT_TIMEOUT})")
    parser.add_argument("--delay", type=float, default=0,
                        help="Delay in seconds between eval calls (rate limiting)")
    parser.add_argument("--skip-tested", nargs="*", default=[],
                        help="Skill names to skip (already tested)")
    args = parser.parse_args()

    if not args.skill and not args.all and not args.cross_skill:
        parser.print_help()
        sys.exit(1)

    skills = []
    if args.all:
        skills = [d.name for d in SKILLS_DIR.iterdir()
                  if d.is_dir() and (d / "evals" / "evals.json").exists()]
    elif args.skill:
        skills = [args.skill]

    if args.skip_tested:
        skills = [s for s in skills if s not in args.skip_tested]

    all_results = []
    eval_count = 0

    for skill_name in sorted(skills):
        print(f"\n{'#'*60}")
        print(f"# Skill: {skill_name}")
        print(f"{'#'*60}")

        evals_data = load_evals(skill_name)
        skill_md = load_skill_md(skill_name)

        for eval_item in evals_data["evals"]:
            if args.eval and eval_item["name"] != args.eval:
                continue

            if args.delay > 0 and eval_count > 0:
                print(f"  [rate limit] waiting {args.delay}s...")
                time.sleep(args.delay)

            result = run_eval(
                skill_name, eval_item, skill_md,
                args.provider, args.model, args.base_url, args.timeout,
                args.dry_run, args.check_file,
            )
            result["skill"] = skill_name
            all_results.append(result)
            eval_count += 1

    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")

    total_pass = sum(1 for r in all_results if r["status"] == "PASS")
    total_fail = sum(1 for r in all_results if r["status"] == "FAIL")
    total_error = sum(1 for r in all_results if r["status"] == "ERROR")
    total_dry = sum(1 for r in all_results if r["status"] == "dry_run")

    if total_dry:
        print(f"Dry run: {total_dry} evals would be tested")
    else:
        total_run = total_pass + total_fail + total_error
        print(f"Passed: {total_pass}/{total_run} ({total_pass/total_run*100:.0f}%)" if total_run else "No evals run")
        if total_fail:
            print(f"\nFailed evals ({total_fail}):")
            for r in all_results:
                if r["status"] == "FAIL":
                    print(f"  {r['skill']}/{r['name']}: {r['passed']}/{r['total']}")
        if total_error:
            print(f"\nErrors ({total_error}):")
            for r in all_results:
                if r["status"] == "ERROR":
                    print(f"  {r['skill']}/{r['name']}")

    # Save results JSON
    results_path = EVALS_DIR / "last_run_results.json"
    with open(results_path, "w") as f:
        json.dump({
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "provider": args.provider,
            "model": args.model if args.provider == "lmstudio" else "claude-sonnet-4-6",
            "total": len(all_results),
            "passed": total_pass,
            "failed": total_fail,
            "errors": total_error,
            "results": all_results,
        }, f, indent=2)
    print(f"\nResults saved to: {results_path}")


if __name__ == "__main__":
    main()
