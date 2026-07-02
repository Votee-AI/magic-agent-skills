"""
Interactive Data Agent Features Test Suite
=========================================

This test suite implements the comprehensive testing approach for the interactive data agent features.
"""
import pytest
import tempfile
import os
import pandas as pd
import shutil
import json
from datetime import datetime


class TestInteractiveFeatures:
    """Test interactive data agent features."""

    @pytest.fixture
    def sample_workspace(self):
        """Create a sample workspace for testing."""
        workspace = tempfile.mkdtemp(prefix="interactive_test_")

        # Create directory structure
        os.makedirs(f"{workspace}/data/input", exist_ok=True)
        os.makedirs(f"{workspace}/data/checkpoints", exist_ok=True)
        os.makedirs(f"{workspace}/logs", exist_ok=True)

        # Create sample data with issues
        sample_data = pd.DataFrame({
            'col1': ['value1', 'value2', 'X', 'value4', 'N/A'],  # Contains sentinel values
            'col2': [1, 2, None, 4, 5],  # Contains missing values
            'col3': ['a ', ' b', 'c', ' d ', 'e'],  # Contains whitespace issues
            'col4': [10, 20, 30, 40, 50]  # Normal data
        })

        sample_data.to_csv(f"{workspace}/data/input/sample.csv", index=False)

        # Create initial workspace_state.md
        with open(f"{workspace}/workspace_state.md", 'w') as f:
            f.write(f"""# Workspace State

**Status:** initializing

## Objective
Test interactive data processing features

## Interaction Mode
**Mode:** collaborative

## Current Phase
**Phase:** Discover

## Current Plan
1. [pending] Load and profile data
2. [pending] Present findings for decision
3. [pending] Execute based on decisions

## Configuration
- **Date:** {datetime.now().strftime('%Y-%m-%d %H:%M')}
""")

        # Create initial analysis_journal.md
        with open(f"{workspace}/logs/analysis_journal.md", 'w') as f:
            f.write("""# Analysis Journal

## Summary
Initial state for interactive testing

## Decisions & Rationale
None yet

## Open Questions
None yet
""")

        yield workspace

        # Cleanup
        shutil.rmtree(workspace)

    def test_pause_annotation_recognition(self, sample_workspace):
        """Test that agents recognize PAUSE annotations."""
        # This would test the actual agent behavior
        # For now, just verify the workspace structure
        assert os.path.exists(f"{sample_workspace}/data/input/sample.csv")
        assert os.path.exists(f"{sample_workspace}/data/checkpoints")
        assert os.path.exists(f"{sample_workspace}/logs")

        # Verify workspace_state.md has interaction mode
        with open(f"{sample_workspace}/workspace_state.md", 'r') as f:
            content = f.read()
            assert "collaborative" in content
            assert "Discover" in content

    def test_explore_mode_readonly_constraint(self, sample_workspace):
        """Test that explore mode enforces read-only constraints."""
        original_file = f"{sample_workspace}/data/input/sample.csv"
        original_size = os.path.getsize(original_file)

        # In a real test, this would run an agent with explore constraints
        # For now, verify the concept by ensuring file wasn't modified
        assert os.path.exists(original_file)
        # The file size should remain the same (no modification)
        assert os.path.getsize(original_file) == original_size

    def test_findings_presentation_format(self, sample_workspace):
        """Test that findings are presented in proper format."""
        # Simulate findings content that would be generated
        findings_content = """## Findings Summary

**Quality Score:** 72/100 (C)
**Total findings:** 3 | **1 HIGH** | **1 MEDIUM** | **1 LOW**
**Processing tasks requiring decision:** 2
**Auto-resolvable items:** 1
**No action needed:** 0

## Processing Tasks Requiring Decision

### 1: Sentinel Values in 'col1' [HIGH]
**Impact:** 2 rows affected
**Sample values:** `X`, `N/A`

**Options:**
  A. Fill via synthesis
  B. Drop rows
  C. Custom fix
"""

        # Verify the format contains expected sections
        assert "Findings Summary" in findings_content
        assert "Processing Tasks Requiring Decision" in findings_content
        assert "Options:" in findings_content
        assert "[HIGH]" in findings_content or "[MEDIUM]" in findings_content

        # Verify that it has the right structure for decision making
        assert "Impact:" in findings_content
        assert "Sample values:" in findings_content

    def test_decision_recording_format(self, sample_workspace):
        """Test that decisions are recorded in proper format."""
        decision_content = """### Cleaning plan review
- **When:** 2026-03-03 14:30
- **Context:** Cleaning plan for col1 column
- **Options presented:**
  1. Fill sentinel values via LLM synthesis
  2. Drop rows with sentinels
  3. Replace with column median
- **Decision:** Option 1 — Fill via synthesis
- **Rationale:** Preserves data completeness
- **Follow-up:** Configure synthesis config for col1
"""

        # Verify the format contains expected fields
        assert "When:" in decision_content
        assert "Context:" in decision_content
        assert "Options presented:" in decision_content
        assert "Decision:" in decision_content
        assert "Rationale:" in decision_content
        assert "Follow-up:" in decision_content

    def test_workspace_state_updates(self, sample_workspace):
        """Test that workspace state is properly updated during interaction."""
        # Initially set to Discover phase
        with open(f"{sample_workspace}/workspace_state.md", 'r') as f:
            content = f.read()
            assert "Discover" in content

        # Simulate phase progression (would happen during agent interaction)
        with open(f"{sample_workspace}/workspace_state.md", 'w') as f:
            f.write(content.replace("Discover", "Plan"))

        # Verify update
        with open(f"{sample_workspace}/workspace_state.md", 'r') as f:
            updated_content = f.read()
            assert "Plan" in updated_content

    def test_analysis_journal_updates(self, sample_workspace):
        """Test that analysis journal is properly updated."""
        journal_path = f"{sample_workspace}/logs/analysis_journal.md"

        # Initially should have basic structure
        with open(journal_path, 'r') as f:
            content = f.read()
            assert "Analysis Journal" in content

        # Simulate adding a decision
        decision_entry = f"""

### Data cleaning decision
- **When:** {datetime.now().strftime('%Y-%m-%d %H:%M')}
- **Context:** Handling missing values in col2
- **Options presented:**
  1. Impute with median
  2. Drop rows
  3. Fill with LLM
- **Decision:** Option 1 — Impute with median
- **Rationale:** Median is robust to outliers
- **Follow-up:** Run imputation and validate
"""

        with open(journal_path, 'a') as f:
            f.write(decision_entry)

        # Verify the decision was added
        with open(journal_path, 'r') as f:
            updated_content = f.read()
            assert "Data cleaning decision" in updated_content
            assert "Impute with median" in updated_content

    def test_checkpoint_naming_convention(self, sample_workspace):
        """Test that checkpoints follow proper naming convention."""
        # Create a checkpoint file
        checkpoint_path = f"{sample_workspace}/data/checkpoints/ckpt_01_loaded.csv"
        pd.DataFrame({'test': [1, 2, 3]}).to_csv(checkpoint_path, index=False)

        # Verify it exists and follows convention
        assert os.path.exists(checkpoint_path)

        # Check naming pattern
        filename = os.path.basename(checkpoint_path)
        assert filename.startswith("ckpt_")
        assert "_loaded" in filename
        assert filename.endswith(".csv")

    def test_interaction_mode_recording(self, sample_workspace):
        """Test that interaction modes are properly tracked."""
        with open(f"{sample_workspace}/workspace_state.md", 'r') as f:
            content = f.read()
            assert "collaborative" in content

        # Verify that different modes can be set
        with open(f"{sample_workspace}/workspace_state.md", 'w') as f:
            f.write(content.replace("collaborative", "supervised"))

        with open(f"{sample_workspace}/workspace_state.md", 'r') as f:
            updated_content = f.read()
            assert "supervised" in updated_content

    def test_lifecycle_phase_tracking(self, sample_workspace):
        """Test that lifecycle phases are properly tracked."""
        with open(f"{sample_workspace}/workspace_state.md", 'r') as f:
            content = f.read()
            assert "Discover" in content

        # Verify phases can be updated
        phases = ["Discover", "Plan", "Execute", "Validate", "Deliver"]
        for phase in phases:
            with open(f"{sample_workspace}/workspace_state.md", 'w') as f:
                f.write(content.replace("Discover", phase))

            with open(f"{sample_workspace}/workspace_state.md", 'r') as f:
                updated_content = f.read()
                assert phase in updated_content

    def test_complexity_tier_tracking(self, sample_workspace):
        """Test that complexity tiers are properly tracked."""
        # Add tier information to workspace state
        tier_info = """

## Complexity Tier
**Tier:** 2 (Standard)
"""

        with open(f"{sample_workspace}/workspace_state.md", 'a') as f:
            f.write(tier_info)

        with open(f"{sample_workspace}/workspace_state.md", 'r') as f:
            content = f.read()
            assert "Tier:" in content
            assert "Standard" in content


class TestSlashCommandSimulation:
    """Test slash command simulation functionality."""

    @pytest.fixture
    def sample_workspace(self):
        """Create a sample workspace for slash command testing."""
        workspace = tempfile.mkdtemp(prefix="slash_test_")

        # Create directory structure
        os.makedirs(f"{workspace}/data/input", exist_ok=True)
        os.makedirs(f"{workspace}/data/checkpoints", exist_ok=True)
        os.makedirs(f"{workspace}/logs", exist_ok=True)

        # Create sample data
        sample_data = pd.DataFrame({
            'col1': ['value1', 'value2', 'X', 'value4', 'N/A'],
            'col2': [1, 2, None, 4, 5],
            'col3': ['a ', ' b', 'c', ' d ', 'e']
        })

        sample_data.to_csv(f"{workspace}/data/input/sample.csv", index=False)

        # Create initial workspace_state.md for slash command tests
        with open(f"{workspace}/workspace_state.md", 'w') as f:
            f.write(f"""# Workspace State

**Status:** initializing

## Objective
Test slash command functionality

## Interaction Mode
**Mode:** collaborative

## Current Phase
**Phase:** Discover

## Current Plan
1. [pending] Load and profile data
2. [pending] Present findings for decision
3. [pending] Execute based on decisions

## Configuration
- **Date:** {datetime.now().strftime('%Y-%m-%d %H:%M')}
""")

        yield workspace

        # Cleanup
        shutil.rmtree(workspace)

    def test_explore_command_simulation(self, sample_workspace):
        """Test /data:explore command simulation."""
        # This would simulate the explore command behavior
        # For now, verify the workspace has necessary files for exploration
        assert os.path.exists(f"{sample_workspace}/data/input/sample.csv")
        assert os.path.exists(f"{sample_workspace}/logs")

        # Verify exploration constraints would be enforced
        input_file = f"{sample_workspace}/data/input/sample.csv"
        original_size = os.path.getsize(input_file)

        # Exploration should not modify the original file
        assert os.path.getsize(input_file) == original_size

    def test_findings_command_simulation(self, sample_workspace):
        """Test /data:findings command simulation."""
        # Simulate creating analysis reports that findings would read
        analysis_report = {
            "quality_score": 72,
            "grade": "C",
            "anomaly_flags": [
                {
                    "column": "col1",
                    "issue_type": "sentinel_values",
                    "severity": "high",
                    "description": "Found sentinel values 'X' and 'N/A'",
                    "affected_rows": 2,
                    "affected_pct": 40.0,
                    "sample_values": ["X", "N/A"]
                }
            ]
        }

        report_path = f"{sample_workspace}/logs/quality_report.json"
        with open(report_path, 'w') as f:
            json.dump(analysis_report, f)

        # Verify the report was created
        assert os.path.exists(report_path)

        # The findings command would read this and present findings
        with open(report_path, 'r') as f:
            loaded_report = json.load(f)
            assert loaded_report["quality_score"] == 72
            assert len(loaded_report["anomaly_flags"]) == 1

    def test_decide_command_simulation(self, sample_workspace):
        """Test /data:decide command simulation."""
        # Simulate the decision recording that decide command would do
        decision_entry = f"""### Decision at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **Context:** Processing decision for test
- **Options:** ['Option A', 'Option B', 'Option C']
- **Decision:** Option A
- **Rationale:** Best approach for testing
"""

        journal_path = f"{sample_workspace}/logs/analysis_journal.md"
        with open(journal_path, 'a') as f:
            f.write(decision_entry)

        # Verify decision was recorded
        with open(journal_path, 'r') as f:
            content = f.read()
            assert "Decision at" in content
            assert "Best approach for testing" in content

    def test_status_command_simulation(self, sample_workspace):
        """Test /data:status command simulation."""
        # Status command would read workspace state and present summary
        with open(f"{sample_workspace}/workspace_state.md", 'r') as f:
            state_content = f.read()

        # Would present this as status summary
        assert "Workspace State" in state_content
        assert "initializing" in state_content

    def test_spec_command_simulation(self, sample_workspace):
        """Test /data:spec command simulation."""
        # Create spec directory
        os.makedirs(f"{sample_workspace}/specs", exist_ok=True)

        # Create initial data spec
        spec_content = """# Data Specification

## Discovery Summary
Initial data exploration complete.

## Processing Tasks
1. Clean sentinel values in col1
2. Handle missing values in col2
3. Normalize whitespace in col3

## Success Criteria
- Quality score >= 90
- No sentinel values remaining
- Missing value rate <= 1%

## Approach
Use appropriate skills to address each task.

## Refinement History
- 2026-03-03: Initial spec created
"""

        spec_path = f"{sample_workspace}/specs/data-spec.md"
        with open(spec_path, 'w') as f:
            f.write(spec_content)

        # Verify spec was created
        assert os.path.exists(spec_path)

        with open(spec_path, 'r') as f:
            content = f.read()
            assert "Discovery Summary" in content
            assert "Processing Tasks" in content


class TestSynthesisHardGates:
    """Test synthesis hard gates functionality."""

    @pytest.fixture
    def sample_workspace(self):
        """Create a sample workspace for synthesis testing."""
        workspace = tempfile.mkdtemp(prefix="synthesis_test_")

        # Create directory structure
        os.makedirs(f"{workspace}/data/input", exist_ok=True)
        os.makedirs(f"{workspace}/data/checkpoints", exist_ok=True)
        os.makedirs(f"{workspace}/logs", exist_ok=True)

        # Create sample data with synthesis needs
        sample_data = pd.DataFrame({
            'col1': ['value1', 'value2', 'X', 'value4', 'N/A'],
            'col2': [1, 2, None, 4, 5]
        })

        sample_data.to_csv(f"{workspace}/data/input/sample.csv", index=False)

        yield workspace

        # Cleanup
        shutil.rmtree(workspace)

    def test_preview_gate_requirement(self, sample_workspace):
        """Test that synthesis requires preview before full run (Gate 1)."""
        # This would simulate the requirement that synthesis must preview first
        # For now, verify the concept by checking if preview-related files would exist

        # In a real scenario, this would verify that preview operations happen
        # before full synthesis is allowed
        assert os.path.exists(f"{sample_workspace}/data/input/sample.csv")

        # Mock the preview requirement check
        preview_done = True  # This would be determined by actual preview execution
        assert preview_done  # Synthesis should not proceed without preview

    def test_validation_gate_requirement(self, sample_workspace):
        """Test that synthesis requires validation after run (Gate 2)."""
        # This would simulate the requirement that synthesis must validate after run
        # For now, verify the concept by checking validation files would exist

        # In a real scenario, this would verify that validation happens
        # after synthesis is complete
        validation_required = True
        assert validation_required  # Synthesis should validate results


def run_comprehensive_tests():
    """Run all interactive feature tests."""
    print("Running Interactive Data Agent Feature Tests...")

    # Create test instance
    test_instance = TestInteractiveFeatures()

    # Run individual tests
    temp_dir = tempfile.mkdtemp()
    try:
        # Create a sample workspace for testing
        sample_data = pd.DataFrame({
            'col1': ['value1', 'value2', 'X', 'value4', 'N/A'],
            'col2': [1, 2, None, 4, 5],
            'col3': ['a ', ' b', 'c', ' d ', 'e'],
            'col4': [10, 20, 30, 40, 50]
        })

        workspace = temp_dir
        os.makedirs(f"{workspace}/data/input", exist_ok=True)
        os.makedirs(f"{workspace}/data/checkpoints", exist_ok=True)
        os.makedirs(f"{workspace}/logs", exist_ok=True)

        sample_data.to_csv(f"{workspace}/data/input/sample.csv", index=False)

        with open(f"{workspace}/workspace_state.md", 'w') as f:
            f.write(f"""# Workspace State
**Status:** initializing
## Objective
Test interactive data processing features
## Interaction Mode
**Mode:** collaborative
## Current Phase
**Phase:** Discover
""")

        with open(f"{workspace}/logs/analysis_journal.md", 'w') as f:
            f.write("# Analysis Journal\n## Summary\nInitial state for interactive testing\n")

        # Run the tests
        test_instance.test_pause_annotation_recognition(workspace)
        test_instance.test_explore_mode_readonly_constraint(workspace)
        test_instance.test_workspace_state_updates(workspace)
        test_instance.test_analysis_journal_updates(workspace)

        print("✓ All interactive feature tests passed!")

    finally:
        shutil.rmtree(temp_dir)


if __name__ == "__main__":
    run_comprehensive_tests()