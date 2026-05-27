<!-- Natural Language Triggers: "what commands are available?", "help me", "show me the commands", "what can you do?", "list commands" -->
# /data-agent:help — MAGIC Command Reference

Display this table when the user asks for help or available commands.

## Available Commands

| Command | What It Does | When to Use |
|---------|-------------|-------------|
| `/data-agent:lifecycle` | Run the full data pipeline (Discover → Plan → Execute → Validate → Deliver) | Start or continue a phased data processing workflow |
| `/data-agent:status` | Quick snapshot of workspace state | See current phase, quality score, recent actions |
| `/data-agent:explore` | Enter interactive data exploration mode | Investigate data freely before committing to a plan |
| `/data-agent:findings` | Show structured findings from profiling/analysis | Review discovered issues as actionable proposals |
| `/data-agent:propose` | Generate a processing plan from findings | Get recommendations for how to handle discovered issues |
| `/data-agent:decide` | Record a user decision | Formalize a choice (e.g., "go with option A") |
| `/data-agent:spec` | Create or show the data processing spec | Define schema, quality targets, and processing steps |
| `/data-agent:review` | Review decisions and progress | See what's been decided and done so far |
| `/data-agent:init-workspace` | Initialize workspace directory structure | Start a new data project with standardized layout |
| `/data-agent:help` | Show this command reference | When you need a reminder of available commands |
| `/data-agent:rollback` | Revert to a previous checkpoint | Undo a processing step that produced bad results |
| `/data-agent:connect` | Connect to a database and inspect schema | Set up a database connection for data extraction |
| `/data-agent:deliver` | Deliver processed data to DB, HuggingFace, or local file | Export final results to an external destination |

**Tip:** You don't need to memorize these commands. Natural language works just as well — say "what's the quality score?" instead of `/data-agent:status`, or "help me clean this data" instead of remembering which skill to invoke.
