<!-- Natural Language Triggers: "what commands are available?", "help me", "show me the commands", "what can you do?", "list commands" -->
# /data:help — MAGIC Command Reference

Display this table when the user asks for help or available commands.

## Available Commands

| Command | What It Does | When to Use |
|---------|-------------|-------------|
| `/data:lifecycle` | Run the full data pipeline (Discover → Plan → Execute → Validate → Deliver) | Start or continue a phased data processing workflow |
| `/data:status` | Quick snapshot of workspace state | See current phase, quality score, recent actions |
| `/data:explore` | Enter interactive data exploration mode | Investigate data freely before committing to a plan |
| `/data:findings` | Show structured findings from profiling/analysis | Review discovered issues as actionable proposals |
| `/data:propose` | Generate a processing plan from findings | Get recommendations for how to handle discovered issues |
| `/data:decide` | Record a user decision | Formalize a choice (e.g., "go with option A") |
| `/data:spec` | Create or show the data processing spec | Define schema, quality targets, and processing steps |
| `/data:review` | Review decisions and progress | See what's been decided and done so far |
| `/data:init-workspace` | Initialize workspace directory structure | Start a new data project with standardized layout |
| `/data:help` | Show this command reference | When you need a reminder of available commands |
| `/data:rollback` | Revert to a previous checkpoint | Undo a processing step that produced bad results |
| `/data:connect` | Connect to a database and inspect schema | Set up a database connection for data extraction |
| `/data:deliver` | Deliver processed data to DB, HuggingFace, or local file | Export final results to an external destination |

**Tip:** You don't need to memorize these commands. Natural language works just as well — say "what's the quality score?" instead of `/data:status`, or "help me clean this data" instead of remembering which skill to invoke.
