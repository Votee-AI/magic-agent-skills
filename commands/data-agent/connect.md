<!-- Natural Language Triggers: "connect to database", "connect to db", "database connection", "set up db connection", "connect to postgres", "connect to mysql", "connect to sqlite" -->

Connect to a database and verify the connection is healthy.

Read the `magic-data-loading` SKILL.md `## Database Loading` section for connection guidance.

**On entry:**
1. Ask user for connection details if not provided:
   - Environment variable name (default: `DATABASE_URL`)
   - Or help them construct a connection string for their dialect
2. Run `connect_database.py --env-var ENV_VAR` to establish connection
3. Run health check (`SELECT 1`)
4. List all tables with row counts via `inspect_schema.py`
5. Update `workspace_state.md` Data Source section with connection info
6. Suggest next steps: "explore schema", "extract data", or "profile a table"

**Important:** Connection is read-only by default. If user needs to write data, guide them to `/data-agent:deliver` instead.

$ARGUMENTS
