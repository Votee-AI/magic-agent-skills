import chalk from 'chalk';
import ora from 'ora';
import { getToolByValue } from '../core/config.js';
import {
  copySkills,
  copyCommands,
  readConfig,
  writeConfig,
} from '../core/copy.js';

export async function update(): Promise<void> {
  const projectPath = process.cwd();

  const config = await readConfig(projectPath);
  if (!config) {
    console.log(
      chalk.yellow('No MAGIC Agent Skills installation found. Run "init" first.'),
    );
    return;
  }

  const spinner = ora('Updating MAGIC Agent Skills...').start();

  const skillFilter = config.skills && config.skills.length > 0 ? config.skills : undefined;
  let totalSkills = 0;
  let totalCommands = 0;

  for (const toolValue of config.tools) {
    const tool = getToolByValue(toolValue);
    if (!tool) continue;

    totalSkills += await copySkills(projectPath, tool, skillFilter);
    totalCommands += await copyCommands(projectPath, tool);
  }

  await writeConfig(projectPath, {
    ...config,
    updatedAt: new Date().toISOString(),
  });

  spinner.succeed(
    `Updated ${totalSkills} skills and ${totalCommands} commands across ${config.tools.length} tool(s).`,
  );
}
