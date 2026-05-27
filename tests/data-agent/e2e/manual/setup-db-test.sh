#!/bin/bash
# ============================================================
# Database Integration Manual Test — Quick Setup
# ============================================================
# Run this ONCE before testing. It:
#   1. Verifies the worktree and venv
#   2. Installs SQLAlchemy if missing
#   3. Creates/verifies the test SQLite fixture
#   4. Sets DATABASE_URL
#   5. Runs a quick smoke test
#   6. Tells you what to do next
# ============================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
WORKTREE_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
FIXTURE_DB="$WORKTREE_ROOT/tests/fixtures/test_database.sqlite"
VENV_PYTHON="$WORKTREE_ROOT/workspace/.venv/bin/python3"

echo "============================================"
echo "  Database Integration — Test Setup"
echo "============================================"
echo ""

# Step 1: Check we're in the right place
echo "1. Checking worktree..."
if [ ! -d "$WORKTREE_ROOT/skills/magic-data-loading" ]; then
    echo "   ERROR: Not in magic-db-integration worktree!"
    echo "   Run from: /path/to/magic-db-integration/tests/e2e/manual/"
    exit 1
fi
echo "   OK: $WORKTREE_ROOT"

# Step 2: Check/create venv
echo ""
echo "2. Checking venv..."
if [ ! -f "$VENV_PYTHON" ]; then
    echo "   Creating venv..."
    python3 -m venv "$WORKTREE_ROOT/workspace/.venv"
fi
echo "   OK: $VENV_PYTHON"

# Step 3: Install SQLAlchemy if needed
echo ""
echo "3. Checking SQLAlchemy..."
if ! "$VENV_PYTHON" -c "import sqlalchemy" 2>/dev/null; then
    echo "   Installing SQLAlchemy..."
    "$WORKTREE_ROOT/workspace/.venv/bin/pip" install 'sqlalchemy>=2.0' pandas -q
fi
SA_VERSION=$("$VENV_PYTHON" -c "import sqlalchemy; print(sqlalchemy.__version__)")
echo "   OK: SQLAlchemy $SA_VERSION"

# Step 4: Create/verify fixture database
echo ""
echo "4. Checking test fixture database..."
if [ ! -f "$FIXTURE_DB" ]; then
    echo "   Generating fixture..."
    "$VENV_PYTHON" "$WORKTREE_ROOT/tests/fixtures/create_test_db.py"
fi
TABLE_COUNT=$("$VENV_PYTHON" -c "
import sqlite3
conn = sqlite3.connect('$FIXTURE_DB')
tables = conn.execute(\"SELECT name FROM sqlite_master WHERE type='table'\").fetchall()
print(len(tables))
conn.close()
")
echo "   OK: $FIXTURE_DB ($TABLE_COUNT tables)"

# Step 5: Set DATABASE_URL
export DATABASE_URL="sqlite:///$FIXTURE_DB"
echo ""
echo "5. DATABASE_URL set:"
echo "   $DATABASE_URL"

# Step 6: Smoke test
echo ""
echo "6. Running smoke test..."
"$VENV_PYTHON" -c "
import sys
sys.path.insert(0, '$WORKTREE_ROOT/skills/magic-data-loading/scripts')
from connect_database import connect, health_check, list_tables
engine = connect('DATABASE_URL', read_only=True)
assert health_check(engine), 'Health check failed!'
tables = list_tables(engine)
assert len(tables) == 4, f'Expected 4 tables, got {len(tables)}'
print('   Smoke test PASSED: connected, 4 tables found')
"

# Done!
echo ""
echo "============================================"
echo "  SETUP COMPLETE"
echo "============================================"
echo ""
echo "The test database has:"
"$VENV_PYTHON" -c "
import sqlite3
conn = sqlite3.connect('$FIXTURE_DB')
for (name,) in conn.execute(\"SELECT name FROM sqlite_master WHERE type='table' ORDER BY name\").fetchall():
    count = conn.execute(f'SELECT COUNT(*) FROM {name}').fetchone()[0]
    print(f'   {name:20s} {count:>5} rows')
conn.close()
"
echo ""
echo "============================================"
echo "  HOW TO RUN MANUAL TESTS"
echo "============================================"
echo ""
echo "  Option A: Test scripts directly (quick verification)"
echo "  ─────────────────────────────────────────────────────"
echo "  export DATABASE_URL=\"$DATABASE_URL\""
echo "  # Connect:"
echo "  $VENV_PYTHON $WORKTREE_ROOT/skills/magic-data-loading/scripts/connect_database.py --env-var DATABASE_URL"
echo "  # Inspect:"
echo "  $VENV_PYTHON $WORKTREE_ROOT/skills/magic-data-loading/scripts/inspect_schema.py --env-var DATABASE_URL"
echo "  # Extract:"
echo "  $VENV_PYTHON $WORKTREE_ROOT/skills/magic-data-loading/scripts/extract_data.py --env-var DATABASE_URL --query 'SELECT * FROM customers' --limit 10"
echo ""
echo "  Option B: Test with Claude agent (full UX test)"
echo "  ─────────────────────────────────────────────────────"
echo "  1. Open a new terminal"
echo "  2. Run:"
echo "     cd $WORKTREE_ROOT"
echo "     export DATABASE_URL=\"$DATABASE_URL\""
echo "     claude"
echo "  3. Give Claude these prompts (from the manual test guide):"
echo ""
echo "     DB-01: \"I have a SQLite database. The connection string is in"
echo "             the DATABASE_URL environment variable. Connect to it"
echo "             and show me what's in there.\""
echo ""
echo "     DB-02: \"From my database, get all completed orders above \$500"
echo "             with customer names. Save as a checkpoint.\""
echo ""
echo "     DB-07: \"Analyze my customer orders database — understand the"
echo "             data, find which regions spend most, create a chart,"
echo "             and write a summary report.\""
echo ""
echo "  Full test guide: $SCRIPT_DIR/database-integration-manual-tests.md"
echo ""
