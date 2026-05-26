import { existsSync } from 'node:fs';
import { resolve } from 'node:path';
import chalk from 'chalk';
import ora from 'ora';
import { checkbox } from '@inquirer/prompts';
import {
  MAGIC_TOOLS,
  type ToolConfig,
  type InstalledConfig,
  getToolByValue,
} from '../core/config.js';
import {
  copySkills,
  copyCommands,
  readConfig,
  writeConfig,
  detectTools,
  getSkillsSource,
} from '../core/copy.js';

export interface InitOptions {
  tools?: string;
  force?: boolean;
}

function resolveToolsArg(toolsArg: string): string[] {
  if (toolsArg === 'all') {
    return MAGIC_TOOLS.filter((t) => t.skillsDir).map((t) => t.value);
  }
  if (toolsArg === 'none') {
    return [];
  }
  return toolsArg.split(',').map((t) => t.trim()).filter(Boolean);
}

function validateTools(values: string[]): ToolConfig[] {
  const tools: ToolConfig[] = [];
  for (const value of values) {
    const tool = getToolByValue(value);
    if (!tool) {
      console.error(chalk.red(`Unknown tool: ${value}`));
      console.error(`Available: ${MAGIC_TOOLS.map((t) => t.value).join(', ')}`);
      process.exit(1);
    }
    if (!tool.skillsDir) {
      console.warn(chalk.yellow(`Skipping ${tool.name} — no skills directory defined`));
      continue;
    }
    tools.push(tool);
  }
  return tools;
}

export async function init(options: InitOptions): Promise<void> {
  const projectPath = resolve('.');

  // Check for existing installation
  const existing = await readConfig(projectPath);
  if (existing && !options.force) {
    console.log(chalk.yellow('MAGIC Agent Skills already installed.'));
    console.log(`Installed tools: ${existing.tools.join(', ')}`);
    console.log(`Use ${chalk.cyan('magic-agent-skills update')} to refresh, or pass ${chalk.cyan('--force')} to reinstall.`);
    return;
  }

  // Verify package has skills bundled
  const skillsSource = getSkillsSource();
  if (!existsSync(skillsSource)) {
    console.error(chalk.red('Skills not found in package. This is a packaging error.'));
    console.error(`Expected at: ${skillsSource}`);
    process.exit(1);
  }

  // Tool selection
  let selectedTools: ToolConfig[];

  if (options.tools) {
    const values = resolveToolsArg(options.tools);
    selectedTools = validateTools(values);
  } else {
    // Auto-detect tools present in the project
    const detected = detectTools(projectPath);

    const choices = MAGIC_TOOLS
      .filter((t) => t.skillsDir)
      .map((t) => ({
        name: `${t.name}${detected.includes(t.value) ? chalk.green(' (detected)') : ''}`,
        value: t.value,
        checked: detected.includes(t.value),
      }));

    console.log(chalk.bold('\n🔮 MAGIC Agent Skills Installer\n'));
    console.log('Select the AI tools you want to install skills for:\n');

    const selected = await checkbox({
      message: 'AI Tools',
      choices,
      pageSize: 15,
    });

    if (selected.length === 0) {
      console.log(chalk.yellow('No tools selected. Nothing to install.'));
      return;
    }

    selectedTools = validateTools(selected);
  }

  // Install
  const spinner = ora('Installing MAGIC Agent Skills...').start();
  let totalSkills = 0;
  let totalCommands = 0;
  const installedToolNames: string[] = [];

  for (const tool of selectedTools) {
    spinner.text = `Installing for ${tool.name}...`;

    const skills = await copySkills(projectPath, tool);
    const commands = await copyCommands(projectPath, tool);

    totalSkills += skills;
    totalCommands += commands;
    installedToolNames.push(tool.value);
  }

  // Write config
  const now = new Date().toISOString();
  const config: InstalledConfig = {
    version: '0.1.0',
    tools: installedToolNames,
    installedAt: existing?.installedAt ?? now,
    updatedAt: now,
  };
  await writeConfig(projectPath, config);

  spinner.succeed(chalk.green('MAGIC Agent Skills installed!'));

  // Summary
  console.log('');
  console.log(chalk.bold('Summary:'));
  for (const tool of selectedTools) {
    const hasCommands = tool.commandsDir && tool.commandFormat;
    console.log(
      `  ${chalk.cyan(tool.name)}: 30 skills${hasCommands ? ' + 23 commands' : ''}` +
      ` → ${chalk.dim(tool.skillsDir + '/')}`
    );
  }
  console.log('');
  console.log(`  Total: ${totalSkills} skill installations, ${totalCommands} command files`);
  console.log('');
  console.log(chalk.dim('Config saved to magic-agent-skills.json'));
  console.log(chalk.dim('Run `magic-agent-skills update` after upgrading the package.'));
}
