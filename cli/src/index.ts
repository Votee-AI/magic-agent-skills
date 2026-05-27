import { Command } from 'commander';
import { init } from './commands/init.js';
import { update } from './commands/update.js';
import { remove } from './commands/remove.js';

const program = new Command();

program
  .name('magic-agent-skills')
  .description('30 AI agent skills for data science and computational linguistics')
  .version('0.1.0');

program
  .command('init')
  .description('Install MAGIC skills and commands for your AI tools')
  .option('-t, --tools <tools>', 'Comma-separated tool IDs (e.g., claude,cursor) or "all"')
  .option('-s, --suites <suites>', 'Comma-separated suite names: all, data, linguistic')
  .option('--skills <skills>', 'Comma-separated skill names')
  .option('-f, --force', 'Overwrite existing installation')
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
