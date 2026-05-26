import { resolve } from 'node:path';
import chalk from 'chalk';
import ora from 'ora';
import { getToolByValue } from '../core/config.js';
import { copySkills, copyCommands, readConfig, writeConfig } from '../core/copy.js';

export async function update(): Promise<void> {
  const projectPath = resolve('.');

  const config = await readConfig(projectPath);
  if (!config) {
    console.error(chalk.red('No installation found.'));
    console.error(`Run ${chalk.cyan('magic-agent-skills init')} first.`);
    process.exit(1);
  }

  const spinner = ora('Updating MAGIC Data Agent Skills...').start();
  let totalSkills = 0;
  let totalCommands = 0;

  for (const toolValue of config.tools) {
    const tool = getToolByValue(toolValue);
    if (!tool) {
      spinner.warn(`Unknown tool in config: ${toolValue} — skipping`);
      continue;
    }

    spinner.text = `Updating ${tool.name}...`;
    totalSkills += await copySkills(projectPath, tool);
    totalCommands += await copyCommands(projectPath, tool);
  }

  config.updatedAt = new Date().toISOString();
  await writeConfig(projectPath, config);

  spinner.succeed(chalk.green('Updated!'));
  console.log(`  ${totalSkills} skill installations, ${totalCommands} command files refreshed`);
  console.log(`  Tools: ${config.tools.join(', ')}`);
}
