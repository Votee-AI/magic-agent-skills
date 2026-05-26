#!/usr/bin/env python3
"""
Shared pytest fixtures for all unit tests.

Provides:
- Test data file paths
- Temporary workspace directories
- Script runner helper
- Python path configuration
"""

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Dict, Any, Tuple

import pytest


TESTS_DIR = Path(__file__).parent.parent
PROJECT_ROOT = TESTS_DIR.parent
SKILLS_DIR = PROJECT_ROOT / "skills"


@pytest.fixture
def tmp_workspace(tmp_path):
    """
    Temporary directory for test outputs.

    Returns:
        Path: Temporary directory path
    """
    workspace = tmp_path / "workspace"
    workspace.mkdir(parents=True, exist_ok=True)
    return workspace


@pytest.fixture
def test_data_dir():
    """
    Base directory for test data files.

    Returns:
        Path: Test data directory
    """
    return TESTS_DIR / "unit" / "test_data"


@pytest.fixture
def sample_clean_csv(test_data_dir, tmp_path):
    """
    Path to sample_clean.csv test data.
    Creates a clean CSV file if it doesn't exist.

    Returns:
        Path: Path to clean CSV file
    """
    csv_path = test_data_dir / "sample_clean.csv"

    if not csv_path.exists():
        # Create sample clean data
        test_data_dir.mkdir(parents=True, exist_ok=True)
        with open(csv_path, 'w') as f:
            f.write("id,name,age,score\n")
            f.write("1,Alice,25,85.5\n")
            f.write("2,Bob,30,92.0\n")
            f.write("3,Charlie,35,78.3\n")
            f.write("4,Diana,28,88.7\n")
            f.write("5,Eve,32,95.2\n")

    return csv_path


@pytest.fixture
def sample_missing_csv(test_data_dir):
    """
    Path to sample_missing.csv test data with missing values.
    Creates the file if it doesn't exist.

    Returns:
        Path: Path to CSV file with missing values
    """
    csv_path = test_data_dir / "sample_missing.csv"

    if not csv_path.exists():
        test_data_dir.mkdir(parents=True, exist_ok=True)
        with open(csv_path, 'w') as f:
            f.write("id,name,age,score\n")
            f.write("1,Alice,25,85.5\n")
            f.write("2,,30,\n")
            f.write("3,Charlie,,78.3\n")
            f.write("4,Diana,28,88.7\n")
            f.write("5,Eve,32,\n")

    return csv_path


@pytest.fixture
def sample_outliers_csv(test_data_dir):
    """
    Path to sample_outliers.csv test data with outliers.
    Creates the file if it doesn't exist.

    Returns:
        Path: Path to CSV file with outliers
    """
    csv_path = test_data_dir / "sample_outliers.csv"

    if not csv_path.exists():
        test_data_dir.mkdir(parents=True, exist_ok=True)
        with open(csv_path, 'w') as f:
            f.write("id,value\n")
            f.write("1,10\n")
            f.write("2,12\n")
            f.write("3,11\n")
            f.write("4,9\n")
            f.write("5,1000\n")  # Outlier
            f.write("6,10\n")
            f.write("7,11\n")
            f.write("8,-500\n")  # Outlier

    return csv_path


@pytest.fixture
def sample_text_csv(test_data_dir):
    """
    Path to sample_text.csv test data with text columns.
    Creates the file if it doesn't exist.

    Returns:
        Path: Path to CSV file with text data
    """
    csv_path = test_data_dir / "sample_text.csv"

    if not csv_path.exists():
        test_data_dir.mkdir(parents=True, exist_ok=True)
        with open(csv_path, 'w') as f:
            f.write("id,description\n")
            f.write("1,This is a short text.\n")
            f.write("2,This is a longer text with more words in it.\n")
            f.write("3,Short.\n")
            f.write("4,Medium length text here.\n")
            f.write("5,Another example of text data with various words.\n")

    return csv_path


@pytest.fixture
def sample_mixed_types_csv(test_data_dir):
    """
    Path to sample_mixed_types.csv test data with mixed data types.
    Creates the file if it doesn't exist.

    Returns:
        Path: Path to CSV file with mixed types
    """
    csv_path = test_data_dir / "sample_mixed_types.csv"

    if not csv_path.exists():
        test_data_dir.mkdir(parents=True, exist_ok=True)
        with open(csv_path, 'w') as f:
            f.write("id,name,age,active,salary\n")
            f.write("1,Alice,25,true,50000.50\n")
            f.write("2,Bob,30,false,60000.00\n")
            f.write("3,Charlie,35,true,75000.75\n")
            f.write("4,Diana,28,true,55000.25\n")

    return csv_path


@pytest.fixture
def sample_latin1_csv(test_data_dir):
    """
    Path to sample_latin1.csv test data with Latin-1 encoding.
    Creates the file if it doesn't exist.

    Returns:
        Path: Path to Latin-1 encoded CSV file
    """
    csv_path = test_data_dir / "sample_latin1.csv"

    # Always regenerate to ensure correct bytes for chardet detection
    test_data_dir.mkdir(parents=True, exist_ok=True)
    with open(csv_path, 'wb') as f:
        # Use binary mode to guarantee Latin-1 bytes (0x80-0xFF) are present.
        # These byte values are invalid UTF-8 start bytes, so chardet can
        # confidently identify the file as Latin-1 / ISO-8859-1.
        rows = [
            "id,name,description",
            "1,Caf\xe9,Une belle caf\xe9 parisienne avec de bons g\xe2teaux",
            "2,Na\xefve,Une fille tr\xe8s na\xefve et tr\xe8s sympathique",
            "3,R\xe9sum\xe9,Voici un r\xe9sum\xe9 complet et d\xe9taill\xe9",
            "4,C\xf4te,La c\xf4te d'Azur est tr\xe8s belle en \xe9t\xe9",
            "5,\xc9b\xe8ne,Le bois d'\xe9b\xe8ne est pr\xe9cieux et rare",
            "6,Fr\xe8re,Mon fr\xe8re est tr\xe8s g\xe9n\xe9reux envers nous",
            "7,Fen\xeatre,La fen\xeatre donne sur un joli jardin fleuri",
            "8,Syst\xe8me,Le syst\xe8me \xe9ducatif fran\xe7ais est r\xe9put\xe9",
            "9,L\xe9gende,Cette l\xe9gende est tr\xe8s populaire dans la r\xe9gion",
            "10,\xc9l\xe8ve,L'\xe9l\xe8ve a obtenu une excellente note \xe0 l'examen",
        ]
        f.write(b"\r\n".join(r.encode("latin-1") for r in rows) + b"\r\n")

    return csv_path


@pytest.fixture
def sample_jsonl(test_data_dir):
    """
    Path to sample.jsonl test data.
    Creates the file if it doesn't exist.

    Returns:
        Path: Path to JSONL file
    """
    jsonl_path = test_data_dir / "sample.jsonl"

    if not jsonl_path.exists():
        test_data_dir.mkdir(parents=True, exist_ok=True)
        with open(jsonl_path, 'w') as f:
            f.write('{"id": 1, "name": "Alice", "age": 25}\n')
            f.write('{"id": 2, "name": "Bob", "age": 30}\n')
            f.write('{"id": 3, "name": "Charlie", "age": 35}\n')

    return jsonl_path


@pytest.fixture
def empty_csv(test_data_dir):
    """
    Path to empty.csv test data (empty file).
    Creates the file if it doesn't exist.

    Returns:
        Path: Path to empty CSV file
    """
    csv_path = test_data_dir / "empty.csv"

    if not csv_path.exists():
        test_data_dir.mkdir(parents=True, exist_ok=True)
        csv_path.touch()

    return csv_path


@pytest.fixture
def run_script():
    """
    Helper function to run a script and parse JSON output.

    Returns:
        Function that accepts script path and arguments, returns (result_dict, exit_code)
    """
    def _run_script(script_path: str, *args, **kwargs) -> Tuple[Dict[str, Any], int]:
        """
        Run a script and parse its JSON output.

        Args:
            script_path: Path to script relative to skills/ directory
            *args: Additional positional arguments for the script
            **kwargs: Optional keyword arguments:
                - cwd: Working directory for subprocess
                - env: Environment variables

        Returns:
            (result_dict, exit_code): Parsed JSON result and exit code
        """
        # Build full script path
        full_script_path = SKILLS_DIR / script_path

        if not full_script_path.exists():
            return {
                "success": False,
                "error": f"Script not found: {full_script_path}"
            }, 1

        # Build command
        cmd = [sys.executable, str(full_script_path)] + list(args)

        # Set up environment
        env = os.environ.copy()
        if 'env' in kwargs:
            env.update(kwargs['env'])

        # Run subprocess
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=kwargs.get('cwd'),
                env=env
            )

            # Parse JSON output
            try:
                output = json.loads(result.stdout)
            except json.JSONDecodeError:
                output = {
                    "success": False,
                    "error": "Failed to parse JSON output",
                    "stdout": result.stdout,
                    "stderr": result.stderr
                }

            return output, result.returncode

        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to run script: {str(e)}"
            }, 1

    return _run_script
