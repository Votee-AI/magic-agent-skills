import { existsSync } from 'node:fs';
import { rm } from 'node:fs/promises';
import { join } from 'node:path';
import chalk from 'chalk';
import ora from 'ora';
import { getToolByValue } from '../core/config.js';
import {
  removeSkills,
  removeCommands,
  readConfig,
  configPath,
} from '../core/copy.js';

export interface RemoveOptions {
  tools?: string;
}

export async function remove(options: RemoveOptions): Promise<void> {
  const projectPath = process.cwd();

  const config = await readConfig(projectPath);
  if (!config) {
    console.log(
      chalk.yellow('No MAGIC Agent Skills installation found.'),
    );
    return;
  }

  const toolValues = options.tools
    ? options.tools.split(',').map((s) => s.trim()).filter(Boolean)
    : config.tools;

  const skillFilter = config.skills && config.skills.length > 0 ? config.skills : undefined;

  const spinner = ora('Removing MAGIC Agent Skills...').start();
  let totalSkills = 0;
  let totalCommands = 0;

  for (const toolValue of toolValues) {
    const tool = getToolByValue(toolValue);
    if (!tool) continue;

    totalSkills += await removeSkills(projectPath, tool, skillFilter);
    totalCommands += await removeCommands(projectPath, tool);
  }

  // Only delete config if removing from all tools
  const removingAll =
    !options.tools || toolValues.length === config.tools.length;
  if (removingAll) {
    const cfgPath = configPath(projectPath);
    if (existsSync(cfgPath)) {
      await rm(cfgPath, { force: true });
    }
  }

  spinner.succeed(
    `Removed ${totalSkills} skills and ${totalCommands} commands from ${toolValues.length} tool(s).`,
  );
}
