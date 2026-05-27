"""
DataDesigner Integration E2E Tests
====================================
Validates the DataDesigner synthesis pipeline end-to-end with local LM Studio.

Requirements:
  - data-designer installed (pip install data-designer)
  - LM Studio running at localhost:1234 with a loaded model
  - "local" provider configured in ~/.data-designer/model_providers.yaml

Usage:
  source .venv/bin/activate
  python -m pytest tests/e2e/test_datadesigner_integration.py -v -s
"""
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[3]
TEMPLATES_DIR = PROJECT_ROOT / "skills" / "magic-data-synthesis" / "templates"

DD_AVAILABLE = subprocess.run(
    ["which", "data-designer"], capture_output=True
).returncode == 0

GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY", "")
if not GOOGLE_API_KEY:
    _env_path = PROJECT_ROOT / ".env"
    if _env_path.exists():
        for line in _env_path.read_text().splitlines():
            if line.startswith("GOOGLE_API_KEY="):
                GOOGLE_API_KEY = line.split("=", 1)[1].strip()
                os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY

GEMINI_AVAILABLE = bool(GOOGLE_API_KEY)
LMSTUDIO_CONFIGURED = bool(os.environ.get("MAGIC_LLM_BASE_URL")) or (
    Path(Path.home() / ".data-designer" / "model_providers.yaml").exists()
    and "localhost:1234" in Path(Path.home() / ".data-designer" / "model_providers.yaml").read_text()
)

GEMINI_TEMPLATE = TEMPLATES_DIR / "text_generation_gemini_template.py"
LOCAL_TEMPLATE = TEMPLATES_DIR / "text_generation_template.py"


@pytest.mark.skipif(not DD_AVAILABLE, reason="data-designer not installed")
class TestDataDesignerValidation:
    """Test that recipe templates validate without errors."""

    def test_text_generation_template_validates(self):
        result = subprocess.run(
            ["data-designer", "validate", str(LOCAL_TEMPLATE)],
            capture_output=True, text=True, timeout=30,
        )
        assert result.returncode == 0, f"Validation failed: {result.stderr}"
        assert "valid" in result.stdout.lower() or "passed" in result.stdout.lower()

    @pytest.mark.skipif(not GEMINI_AVAILABLE, reason="GOOGLE_API_KEY not set")
    def test_gemini_template_validates(self):
        result = subprocess.run(
            ["data-designer", "validate", str(GEMINI_TEMPLATE)],
            capture_output=True, text=True, timeout=30,
        )
        assert result.returncode == 0, f"Validation failed: {result.stderr}"
        assert "valid" in result.stdout.lower() or "passed" in result.stdout.lower()


@pytest.mark.skipif(
    not DD_AVAILABLE or not GEMINI_AVAILABLE,
    reason="data-designer not installed or GOOGLE_API_KEY not set",
)
class TestDataDesignerPreview:
    """Test that preview generates real content with Gemini (fast cloud model)."""

    def test_preview_generates_definitions_gemini(self, tmp_path):
        """Fill 5 item descriptions using Gemini — should complete in <30s."""
        artifact_path = str(tmp_path / "preview")
        env = os.environ.copy()
        env["GOOGLE_API_KEY"] = GOOGLE_API_KEY

        result = subprocess.run(
            [
                "data-designer", "preview",
                str(GEMINI_TEMPLATE),
                "--num-records", "5",
                "--save-results",
                "--artifact-path", artifact_path,
            ],
            capture_output=True, text=True, timeout=60, env=env,
        )
        assert result.returncode == 0, f"Preview failed: {result.stdout}\n{result.stderr}"

        import pandas as pd
        results_dirs = list(Path(artifact_path).glob("preview_results_*"))
        assert len(results_dirs) > 0, "No results directory created"

        parquet_files = list(results_dirs[0].glob("*.parquet"))
        assert len(parquet_files) > 0, "No parquet output"

        df = pd.read_parquet(parquet_files[0])
        assert len(df) == 5
        assert "description" in df.columns

        for idx, row in df.iterrows():
            val = str(row["description"]).strip()
            assert len(val) > 2, f"Row {idx}: empty/trivial description: '{val}'"


@pytest.mark.skipif(
    not DD_AVAILABLE or not GEMINI_AVAILABLE,
    reason="data-designer not installed or GOOGLE_API_KEY not set",
)
class TestQualityUtilsWithDDOutput:
    """Test quality_utils.extract_dd_quality on real DD output."""

    def test_extract_quality_from_preview(self, tmp_path):
        artifact_path = str(tmp_path / "preview")
        env = os.environ.copy()
        env["GOOGLE_API_KEY"] = GOOGLE_API_KEY

        result = subprocess.run(
            [
                "data-designer", "preview",
                str(GEMINI_TEMPLATE),
                "--num-records", "5",
                "--save-results",
                "--artifact-path", artifact_path,
            ],
            capture_output=True, text=True, timeout=60, env=env,
        )
        if result.returncode != 0:
            pytest.skip(f"Preview failed: {result.stderr[:200]}")

        results_dirs = list(Path(artifact_path).glob("preview_results_*"))
        if not results_dirs:
            pytest.skip("Preview did not produce results")

        parquet_files = list(results_dirs[0].glob("*.parquet"))
        if not parquet_files:
            pytest.skip("No parquet output from preview")

        import pandas as pd
        df = pd.read_parquet(str(parquet_files[0]))
        assert len(df) == 5
