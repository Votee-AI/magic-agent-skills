"""Install-simulation regression: a linguistic skill must be self-contained on disk.

Both installers (`@votee-ai/magic-agent-skills` and `npx skills add` / skills.sh)
fetch the GitHub tree and recursively copy ONLY the named skill directory — they
do NOT ship the sibling `skills/_linguistic_shared/`. So after install, the
runtime `sys.path` shim must still resolve `_linguistic_shared` from inside the
copied skill (the committed in-skill bundle).

This test simulates that by copying ONE skill dir to a tmp location with NO
`skills/` parent and NO `_linguistic_shared` sibling, then running one of its
scripts as a subprocess. It FAILS (red) until the bundle is generated and the
import shim searches upward instead of hardcoding `parents[2]`.
"""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
SKILLS_DIR = REPO_ROOT / "skills"

# (skill dir name, script relative to the skill dir) — pick scripts that hit the
# shared `lang_codes` import and accept `--help`.
CASES = [
    ("magic-linguistic-tokenize", "scripts/fertility_audit.py"),
    ("magic-linguistic-scope", "scripts/language_lookup.py"),
    ("magic-linguistic-bitext", "scripts/alignment_score.py"),
    ("magic-linguistic-eval", "scripts/benchmark_advisor.py"),
    ("magic-linguistic-syntax", "scripts/ud_coverage.py"),
    ("magic-linguistic-transfer", "scripts/uriel_transfer_plan.py"),
]


@pytest.mark.parametrize("skill_name,script_rel", CASES, ids=[c[0] for c in CASES])
def test_skill_is_self_contained_after_isolated_install(
    skill_name: str, script_rel: str, tmp_path: Path
) -> None:
    src_skill = SKILLS_DIR / skill_name
    assert src_skill.is_dir(), f"missing source skill {skill_name}"

    # Copy ONLY the skill dir — no `skills/` parent, no `_linguistic_shared` sibling.
    dest_skill = tmp_path / skill_name
    shutil.copytree(src_skill, dest_skill)

    # Sanity: the sibling shared dir is genuinely absent in this isolated install.
    assert not (tmp_path / "_linguistic_shared").exists()
    assert not (dest_skill.parent / "_linguistic_shared").exists()

    script = dest_skill / script_rel
    assert script.exists(), f"missing script {script_rel} in copied skill"

    proc = subprocess.run(
        [sys.executable, str(script), "--help"],
        cwd=dest_skill,
        capture_output=True,
        text=True,
    )

    combined = proc.stdout + proc.stderr
    assert proc.returncode == 0, (
        f"{skill_name}/{script_rel} --help failed (rc={proc.returncode}):\n{combined}"
    )
    assert "ModuleNotFoundError" not in combined, (
        f"shared import did not resolve for {skill_name}:\n{combined}"
    )
    assert "lang_codes" not in proc.stderr, (
        f"unexpected lang_codes error for {skill_name}:\n{proc.stderr}"
    )
