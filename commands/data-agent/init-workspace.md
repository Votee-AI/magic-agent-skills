<!-- Natural Language Triggers: "set up a workspace", "initialize workspace", "start a new data project", "create workspace" -->

Initialize a MAGIC data processing workspace. Follow these steps:

1. Read the workspace init skill at `skills/magic-workspace-init/SKILL.md` to understand the workspace directory convention and available options.

2. Determine the workspace path:
   - If the user provided a path argument, use that path
   - Otherwise, use the default: `./workspace/` relative to the current working directory

3. Create the workspace directory structure inline using the SKILL.md patterns (it's safe to run on existing workspaces — never removes files):
   ```python
   from pathlib import Path
   workspace = Path("<path>")
   for d in ["data/input", "data/checkpoints", "data/output", "logs", "specs", "reports", "charts"]:
       (workspace / d).mkdir(parents=True, exist_ok=True)
   ```

4. Verify the Python environment:
   - Check for `workspace/.venv/bin/python3` (preferred) or system Python
   - Verify key packages: pandas, numpy
   - Report any missing packages with install guidance

5. Check for existing data files in `data/input/` and mention them if present.

6. Present a report with these sections:

   **a. Workspace status** — directories created or already existed, any existing data files found

   **b. Python environment** — which Python is available, package status, install guidance if needed

   **c. LLM Configuration** — check for API keys in environment (`GOOGLE_API_KEY`, `HF_TOKEN`, etc.)

   **d. Getting started** — suggest first steps: load data, run `/data-agent:explore`, or `/data-agent:lifecycle`

7. Provide a comprehensive overview that helps users understand their workspace setup and next steps.
