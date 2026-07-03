import { readFileSync } from 'node:fs';
import { join } from 'node:path';
import { Command } from 'commander';
import { init } from './commands/init.js';
import { update } from './commands/update.js';
import { remove } from './commands/remove.js';
import { getPackageRoot } from './core/config.js';

const VERSION = JSON.parse(
  readFileSync(join(getPackageRoot(), 'package.json'), 'utf8'),
).version as string;

// S5: Ctrl-C raises ExitPromptError from @inquirer/core's SIGINT handler.
// Catch it at the top level so it exits cleanly with code 130, no stack trace.
// (On a real raw-mode TTY the custom prompts in core/prompts.ts intercept the
// Ctrl-C keypress first and exit 130 directly; this handler is the safety net
// for non-TTY / piped contexts where the SIGINT rejection path is taken.)
process.on('unhandledRejection', (err: unknown) => {
  if (err instanceof Error && err.name === 'ExitPromptError') {
    process.exit(130);
  }
  // Re-throw anything else so Node prints it normally.
  throw err;
});

const program = new Command();

program
  .name('magic-agent-skills')
  .description('30 AI agent skills for data science and computational linguistics')
  .version(VERSION);

program
  .command('init')
  .description('Install MAGIC skills and commands for your AI tools')
  .option('-t, --tools <tools>', 'Comma-separated tool IDs (e.g., claude,cursor) or "all"')
  .option('-s, --suites <suites>', 'Comma-separated suite names: all, data, linguistic')
  .option('--skills <skills>', 'Comma-separated skill names')
  .option('-f, --force', 'Overwrite existing installation')
  .option('-y, --yes', 'Accept defaults and skip all interactive prompts')
  .option('--dry-run', 'Print the installation plan without writing anything')
  .action(init);

program
  .command('update')
  .description('Refresh installed skills and commands to the latest version')
  .action(update);

program
  .command('remove')
  .description('Remove installed MAGIC skills and commands')
  .option('-t, --tools <tools>', 'Remove from specific tools only (comma-separated)')
  .action(remove);

program.parse();
