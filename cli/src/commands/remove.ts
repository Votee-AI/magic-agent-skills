import { existsSync } from 'node:fs';
import { rm } from 'node:fs/promises';
import { resolve } from 'node:path';
import chalk from 'chalk';
import ora from 'ora';
import { getToolByValue, CONFIG_FILENAME } from '../core/config.js';
import {
  readConfig,
  writeConfig,
  configPath,
  removeSkills,
  removeCommands,
} from '../core/copy.js';

export interface RemoveOptions {
  tools?: string;
}

export async function remove(options: RemoveOptions): Promise<void> {
  const projectPath = resolve('.');

  const config = await readConfig(projectPath);
  if (!config) {
    console.error(chalk.red('No installation found. Nothing to remove.'));
    process.exit(1);
  }

  const toolsToRemove = options.tools
    ? options.tools.split(',').map((t) => t.trim())
    : config.tools;

  const spinner = ora('Removing MAGIC Data Agent Skills...').start();
  let totalSkills = 0;
  let totalCommands = 0;

  for (const toolValue of toolsToRemove) {
    const tool = getToolByValue(toolValue);
    if (!tool) {
      spinner.warn(`Unknown tool: ${toolValue} — skipping`);
      continue;
    }

    spinner.text = `Removing from ${tool.name}...`;
    totalSkills += await removeSkills(projectPath, tool);
    totalCommands += await removeCommands(projectPath, tool);
  }

  // Update or remove config
  const remaining = config.tools.filter((t) => !toolsToRemove.includes(t));
  if (remaining.length === 0) {
    const cfgPath = configPath(projectPath);
    if (existsSync(cfgPath)) {
      await rm(cfgPath);
    }
    spinner.succeed(chalk.green('All MAGIC Data Agent Skills removed.'));
  } else {
    config.tools = remaining;
    config.updatedAt = new Date().toISOString();
    await writeConfig(projectPath, config);
    spinner.succeed(chalk.green(`Removed from: ${toolsToRemove.join(', ')}`));
    console.log(`  Remaining tools: ${remaining.join(', ')}`);
  }

  console.log(`  Removed ${totalSkills} skill directories, ${totalCommands} command files`);
}
