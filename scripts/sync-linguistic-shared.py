#!/usr/bin/env python3
"""Sync the canonical `skills/_linguistic_shared/` into each linguistic skill.

Single source of truth: `skills/_linguistic_shared/`. Every `magic-linguistic-*`
skill whose `.py` files reference `_linguistic_shared` gets a committed in-skill
copy at `skills/<skill>/_linguistic_shared/`, so the skill is self-contained on
disk and survives an isolated install (our CLI and `npx skills add`/skills.sh
both recursively copy ONLY the named skill dir — never the sibling shared dir).

Deterministic and idempotent: re-running with no source change produces no diff.
`__pycache__/` and `*.pyc` are never copied. Run with no args:

    python scripts/sync-linguistic-shared.py
"""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SKILLS_DIR = REPO_ROOT / "skills"
SOURCE = SKILLS_DIR / "_linguistic_shared"
BUNDLE_NAME = "_linguistic_shared"
MARKER = "_linguistic_shared"

# Never vendor these into the per-skill bundles.
_IGNORE = shutil.ignore_patterns("__pycache__", "*.pyc", "*.pyo")


def _skills_referencing_shared() -> list[Path]:
    """Discover (don't hardcode) the linguistic skills that import the shared lib."""
    found: list[Path] = []
    for skill_dir in sorted(SKILLS_DIR.glob("magic-linguistic-*")):
        if not skill_dir.is_dir():
            continue
        for py in skill_dir.rglob("*.py"):
            # Skip a previously-synced bundle so detection keys off real script refs.
            if BUNDLE_NAME in py.relative_to(skill_dir).parts[:-1]:
                continue
            try:
                text = py.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError):
                continue
            if MARKER in text:
                found.append(skill_dir)
                break
    return found


def _sync_one(skill_dir: Path) -> Path:
    dest = skill_dir / BUNDLE_NAME
    if dest.exists():
        shutil.rmtree(dest)
    shutil.copytree(SOURCE, dest, ignore=_IGNORE)
    return dest


def _remove_orphaned_bundles(targets: list[Path]) -> list[Path]:
    """Remove any committed in-skill bundle whose parent skill no longer references _linguistic_shared."""
    target_set = set(targets)
    removed: list[Path] = []
    for skill_dir in sorted(SKILLS_DIR.glob("magic-linguistic-*")):
        if not skill_dir.is_dir():
            continue
        bundle = skill_dir / BUNDLE_NAME
        if bundle.exists() and skill_dir not in target_set:
            shutil.rmtree(bundle)
            removed.append(bundle)
    return removed


def main() -> int:
    if not SOURCE.is_dir():
        print(f"ERROR: source of truth not found: {SOURCE}", file=sys.stderr)
        return 1

    targets = _skills_referencing_shared()

    # Remove orphaned bundles FIRST (skills that no longer reference shared).
    orphans = _remove_orphaned_bundles(targets)
    for orphan in orphans:
        rel = orphan.relative_to(REPO_ROOT)
        print(f"removed orphan -> {rel}")

    if not targets:
        print("WARN: no linguistic skills reference _linguistic_shared", file=sys.stderr)
        return 0

    for skill_dir in targets:
        dest = _sync_one(skill_dir)
        rel = dest.relative_to(REPO_ROOT)
        print(f"synced -> {rel}")

    print(f"OK: {len(targets)} in-skill _linguistic_shared bundle(s) in sync")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
