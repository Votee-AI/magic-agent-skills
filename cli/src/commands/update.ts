import chalk from 'chalk';
import ora from 'ora';
import { getToolByValue } from '../core/config.js';
import {
  copySkills,
  copyCommands,
  readConfig,
  writeConfig,
} from '../core/copy.js';
import { fetchFromGitHub, cleanupFetchDir } from '../core/fetch.js';

export async function update(): Promise<void> {
  const projectPath = process.cwd();

  const config = await readConfig(projectPath);
  if (!config) {
    console.log(
      chalk.yellow('No MAGIC Agent Skills installation found. Run "init" first.'),
    );
    return;
  }

  const fetchSpinner = ora('Fetching latest skills from GitHub...').start();
  let sourceDir: string;
  try {
    sourceDir = await fetchFromGitHub();
    fetchSpinner.succeed('Fetched latest skills from GitHub.');
  } catch (err) {
    fetchSpinner.fail(err instanceof Error ? err.message : String(err));
    return;
  }

  try {
    const spinner = ora('Updating MAGIC Agent Skills...').start();

    const skillFilter = config.skills && config.skills.length > 0 ? config.skills : undefined;
    let totalSkills = 0;
    let totalCommands = 0;

    for (const toolValue of config.tools) {
      const tool = getToolByValue(toolValue);
      if (!tool) continue;

      totalSkills += await copySkills(projectPath, tool, sourceDir, skillFilter);
      totalCommands += await copyCommands(projectPath, tool, sourceDir);
    }

    await writeConfig(projectPath, {
      ...config,
      updatedAt: new Date().toISOString(),
    });

    spinner.succeed(
      `Updated ${totalSkills} skills and ${totalCommands} commands across ${config.tools.length} tool(s).`,
    );
  } finally {
    await cleanupFetchDir(sourceDir);
  }
}
