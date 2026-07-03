import chalk from 'chalk';
import ora from 'ora';
import { getToolByValue } from '../core/config.js';
import {
  copySkills,
  copyCommands,
  readConfig,
  writeConfig,
  ConfigCorruptError,
} from '../core/copy.js';
import { fetchFromGitHub, cleanupFetchDir } from '../core/fetch.js';

export async function update(): Promise<void> {
  const projectPath = process.cwd();

  let config;
  try {
    config = await readConfig(projectPath);
  } catch (err) {
    if (err instanceof ConfigCorruptError) {
      console.log(chalk.red(`\n  ${err.message}\n`));
      process.exitCode = 1;
      return;
    }
    throw err;
  }
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
    const failures: string[] = [];

    for (const toolValue of config.tools) {
      const tool = getToolByValue(toolValue);
      if (!tool) continue;

      try {
        totalSkills += await copySkills(projectPath, tool, sourceDir, skillFilter);
        totalCommands += await copyCommands(projectPath, tool, sourceDir);
      } catch (err) {
        const msg = err instanceof Error ? err.message : String(err);
        spinner.warn(`Failed to update ${toolValue}: ${msg}`);
        failures.push(toolValue);
      }
    }

    await writeConfig(projectPath, {
      ...config,
      updatedAt: new Date().toISOString(),
    });

    spinner.succeed(
      `Updated ${totalSkills} skills and ${totalCommands} commands across ${config.tools.length} tool(s).`,
    );
    if (failures.length > 0) {
      console.log(chalk.yellow(`  Skipped (failed): ${failures.join(', ')}`));
    }
  } finally {
    await cleanupFetchDir(sourceDir);
  }
}
