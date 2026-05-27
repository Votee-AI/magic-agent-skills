#!/usr/bin/env python3
"""Root conftest — shared fixtures available to all tests (co-located and top-level)."""

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Dict, Any, Tuple

import pytest

PROJECT_ROOT = Path(__file__).parent
SKILLS_DIR = PROJECT_ROOT / "skills"
TEST_DATA_DIR = PROJECT_ROOT / "tests" / "test_data"


@pytest.fixture
def project_root():
    return PROJECT_ROOT


@pytest.fixture
def skills_dir():
    return SKILLS_DIR


@pytest.fixture
def tmp_workspace(tmp_path):
    workspace = tmp_path / "workspace"
    workspace.mkdir(parents=True, exist_ok=True)
    return workspace


@pytest.fixture
def test_data_dir():
    return TEST_DATA_DIR


@pytest.fixture
def sample_clean_csv(test_data_dir, tmp_path):
    csv_path = test_data_dir / "sample_clean.csv"
    if not csv_path.exists():
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
    csv_path = test_data_dir / "sample_outliers.csv"
    if not csv_path.exists():
        test_data_dir.mkdir(parents=True, exist_ok=True)
        with open(csv_path, 'w') as f:
            f.write("id,value\n")
            f.write("1,10\n2,12\n3,11\n4,9\n5,1000\n6,10\n7,11\n8,-500\n")
    return csv_path


@pytest.fixture
def sample_text_csv(test_data_dir):
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
    csv_path = test_data_dir / "sample_latin1.csv"
    test_data_dir.mkdir(parents=True, exist_ok=True)
    with open(csv_path, 'wb') as f:
        rows = [
            "id,name,description",
            "1,Caf\xe9,Une belle caf\xe9 parisienne avec de bons g\xe2teaux",
            "2,Na\xefve,Une fille tr\xe8s na\xefve et tr\xe8s sympathique",
            "3,R\xe9sum\xe9,Voici un r\xe9sum\xe9 complet et d\xe9taill\xe9",
            "4,C\xf4te,La c\xf4te d'Azur est tr\xe8s belle en \xe9t\xe9",
            "5,\xc9b\xe8ne,Le bois d'\xe9b\xe8ne est pr\xe9cieux et rare",
        ]
        f.write(b"\r\n".join(r.encode("latin-1") for r in rows) + b"\r\n")
    return csv_path


@pytest.fixture
def sample_jsonl(test_data_dir):
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
    csv_path = test_data_dir / "empty.csv"
    if not csv_path.exists():
        test_data_dir.mkdir(parents=True, exist_ok=True)
        csv_path.touch()
    return csv_path


@pytest.fixture
def run_script():
    def _run_script(script_path: str, *args, **kwargs) -> Tuple[Dict[str, Any], int]:
        full_script_path = SKILLS_DIR / script_path
        if not full_script_path.exists():
            return {"success": False, "error": f"Script not found: {full_script_path}"}, 1
        cmd = [sys.executable, str(full_script_path)] + list(args)
        env = os.environ.copy()
        if 'env' in kwargs:
            env.update(kwargs['env'])
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=kwargs.get('cwd'), env=env)
            try:
                output = json.loads(result.stdout)
            except json.JSONDecodeError:
                output = {"success": False, "error": "Failed to parse JSON output", "stdout": result.stdout, "stderr": result.stderr}
            return output, result.returncode
        except Exception as e:
            return {"success": False, "error": f"Failed to run script: {str(e)}"}, 1
    return _run_script
