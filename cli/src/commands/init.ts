import { existsSync } from 'node:fs';
import { readFile, rm } from 'node:fs/promises';
import { join } from 'node:path';
import { select, checkbox, confirm, Separator } from '@inquirer/prompts';
import chalk from 'chalk';
import ora from 'ora';
import {
  MAGIC_TOOLS,
  CONFIG_FILENAME,
  getPackageRoot,
  getToolByValue,
  type InstalledConfig,
} from '../core/config.js';
import {
  copySkills,
  copyCommands,
  readConfig,
  writeConfig,
  detectTools,
  configPath,
} from '../core/copy.js';
import { getSuiteConfigs } from '../core/manifest.js';

const ACCENT = chalk.hex('#00BCD4');
const DIM = chalk.dim;

const LOGO = [
  '███╗   ███╗ █████╗  ██████╗ ██╗ ██████╗',
  '████╗ ████║██╔══██╗██╔════╝ ██║██╔════╝',
  '██╔████╔██║███████║██║  ███╗██║██║     ',
  '██║╚██╔╝██║██╔══██║██║   ██║██║██║     ',
  '██║ ╚═╝ ██║██║  ██║╚██████╔╝██║╚██████╗',
  '╚═╝     ╚═╝╚═╝  ╚═╝ ╚═════╝ ╚═╝ ╚═════╝',
];

function printBanner(version: string, totalSkills: number): void {
  const width = Math.min(process.stdout.columns || 80, 80);
  console.log('');
  if (width >= 60) {
    for (const line of LOGO) {
      console.log('  ' + ACCENT(line));
    }
    console.log('  ' + ACCENT.bold('  Agent Skills'));
  } else {
    console.log('  ' + ACCENT.bold('✦ MAGIC Agent Skills'));
  }
  console.log('');
  console.log('  ' + DIM(`v${version} · ${totalSkills} skills · data-agent + linguistic`));
  console.log('');
  console.log('  ' + DIM('─'.repeat(width - 4)));
  console.log('');
  console.log('');
}

const LEGACY_CONFIG_FILENAME = 'magic-data-agent-skills.json';

export interface InitOptions {
  tools?: string;
  suites?: string;
  skills?: string;
  force?: boolean;
}

export async function init(options: InitOptions): Promise<void> {
  const projectPath = process.cwd();

  // Check for existing installation
  const existingConfig = await readConfig(projectPath);
  let addMode = false;

  if (existingConfig && !options.force) {
    if (options.suites || options.skills) {
      addMode = true;
    } else {
      const existingCount = existingConfig.skills?.length ?? 0;
      const existingSuites = existingConfig.suites?.join(', ') || 'unknown';
      console.log(chalk.dim(`  Installed: ${existingCount} skills (${existingSuites})\n`));

      const action = await select({
        message: 'MAGIC Agent Skills already installed. What would you like to do?',
        choices: [
          { name: 'Add more skills to this installation', value: 'add' },
          { name: 'Reinstall from scratch', value: 'reinstall' },
          { name: 'Cancel', value: 'cancel' },
        ],
      });

      if (action === 'cancel') return;
      if (action === 'add') addMode = true;
      // 'reinstall' falls through to normal install flow
    }
  }

  // --- C4: Legacy config migration ---
  const legacyConfigPath = join(projectPath, LEGACY_CONFIG_FILENAME);
  let legacyConfig: InstalledConfig | null = null;
  let preSelectedTools: string[] = [];
  let preSelectedSuites: string[] = [];

  if (existsSync(legacyConfigPath) && legacyConfigPath !== configPath(projectPath)) {
    try {
      const raw = await readFile(legacyConfigPath, 'utf8');
      legacyConfig = JSON.parse(raw) as InstalledConfig;
    } catch {
      // Ignore corrupt legacy config
    }
  }

  if (legacyConfig && !options.suites && !options.skills) {
    const migrate = await confirm({
      message: 'Existing MAGIC Data installation detected. Migrate to unified installer?',
      default: true,
    });
    if (migrate) {
      preSelectedSuites = ['data'];
      preSelectedTools = legacyConfig.tools ?? [];
    }
  }

  // --- Suite / skill selection ---
  let selectedSkills: string[] = [];
  let selectedSuites: string[] = preSelectedSuites;

  let suiteConfigs: ReturnType<typeof getSuiteConfigs> = [];
  try {
    suiteConfigs = getSuiteConfigs();
  } catch {
    // Manifest not yet generated — fall back to data-only (backward compat)
    suiteConfigs = [];
  }

  // Show banner in interactive mode
  const isInteractive = !options.suites && !options.skills;
  if (isInteractive) {
    const totalSkills = suiteConfigs.reduce((sum, s) => sum + s.skills.length, 0);
    const pkg = JSON.parse(
      await readFile(join(getPackageRoot(), 'package.json'), 'utf8'),
    ) as { version: string };
    printBanner(pkg.version, totalSkills || 30);
  }

  if (options.skills) {
    // --skills flag: explicit list
    selectedSkills = options.skills.split(',').map((s) => s.trim()).filter(Boolean);
    selectedSuites = resolveSuitesFromSkills(selectedSkills, suiteConfigs);
  } else if (options.suites) {
    // --suites flag
    const suiteArg = options.suites.trim();
    if (suiteArg === 'all') {
      selectedSuites = suiteConfigs.map((s) => s.name);
    } else {
      selectedSuites = suiteArg.split(',').map((s) => s.trim()).filter(Boolean);
    }
    selectedSkills = resolveSkillsFromSuites(selectedSuites, suiteConfigs);
  } else if (preSelectedSuites.length > 0) {
    // Pre-selected from legacy migration
    selectedSkills = resolveSkillsFromSuites(preSelectedSuites, suiteConfigs);
  } else if (suiteConfigs.length > 0) {
    // Interactive suite/skill selection
    const totalSkills = suiteConfigs.reduce((sum, s) => sum + s.skills.length, 0);

    const selectionMode = await select({
      message: 'Which MAGIC skills would you like to install?',
      choices: [
        {
          name: `All MAGIC skills (${totalSkills} skills)`,
          value: 'all',
        },
        ...suiteConfigs.map((suite) => ({
          name: `${suite.displayName} suite (${suite.skills.length} skills)`,
          value: `suite:${suite.name}`,
        })),
        {
          name: 'Select individual skills',
          value: 'individual',
        },
      ],
    });

    if (selectionMode === 'all') {
      selectedSuites = suiteConfigs.map((s) => s.name);
      selectedSkills = resolveSkillsFromSuites(selectedSuites, suiteConfigs);
    } else if (selectionMode.startsWith('suite:')) {
      const suiteName = selectionMode.slice('suite:'.length);
      selectedSuites = [suiteName];
      selectedSkills = resolveSkillsFromSuites(selectedSuites, suiteConfigs);
    } else {
      // Individual skill selection with suite grouping
      const choices: Array<Separator | { name: string; value: string; checked: boolean }> = [];
      for (const suite of suiteConfigs) {
        choices.push(new Separator(`── ${suite.displayName} ──`));
        for (const skill of suite.skills) {
          choices.push({ name: skill, value: skill, checked: false });
        }
      }
      selectedSkills = await checkbox<string>({
        message: 'Select skills to install (space to toggle, enter to confirm):',
        choices,
      });
      selectedSuites = resolveSuitesFromSkills(selectedSkills, suiteConfigs);
    }
  } else {
    // No manifest — install all data skills (backward compat)
    selectedSuites = ['data'];
    selectedSkills = [];
  }

  // --- Tool selection ---
  const detectedToolValues = preSelectedTools.length > 0
    ? preSelectedTools
    : detectTools(projectPath);

  let selectedToolValues: string[];

  if (options.tools) {
    if (options.tools === 'all') {
      selectedToolValues = MAGIC_TOOLS.map((t) => t.value);
    } else {
      selectedToolValues = options.tools.split(',').map((s) => s.trim()).filter(Boolean);
    }
  } else if (detectedToolValues.length > 0) {
    const autoApply = await confirm({
      message: `Detected AI tools: ${detectedToolValues.join(', ')}. Install for these tools?`,
      default: true,
    });
    if (autoApply) {
      selectedToolValues = detectedToolValues;
    } else {
      selectedToolValues = await selectTools();
    }
  } else {
    selectedToolValues = await selectTools();
  }

  if (selectedToolValues.length === 0) {
    console.log(chalk.yellow('No tools selected. Aborting.'));
    return;
  }

  // --- Installation ---
  const spinner = ora('Installing MAGIC Agent Skills...').start();
  let totalSkillsInstalled = 0;
  let totalCommandsInstalled = 0;

  for (const toolValue of selectedToolValues) {
    const tool = getToolByValue(toolValue);
    if (!tool) {
      spinner.warn(`Unknown tool: ${toolValue}`);
      continue;
    }

    const skillFilter = selectedSkills.length > 0 ? selectedSkills : undefined;
    const skillCount = await copySkills(projectPath, tool, skillFilter);
    const cmdCount = await copyCommands(projectPath, tool);
    totalSkillsInstalled += skillCount;
    totalCommandsInstalled += cmdCount;
  }

  // Write config
  const now = new Date().toISOString();
  const pkg = JSON.parse(
    await readFile(join(getPackageRoot(), 'package.json'), 'utf8'),
  ) as { version: string };
  const mergedTools = addMode && existingConfig
    ? [...new Set([...existingConfig.tools, ...selectedToolValues])]
    : selectedToolValues;
  const mergedSuites = addMode && existingConfig
    ? [...new Set([...(existingConfig.suites ?? []), ...selectedSuites])]
    : selectedSuites;
  const mergedSkills = addMode && existingConfig
    ? [...new Set([...(existingConfig.skills ?? []), ...selectedSkills])]
    : selectedSkills;

  const config: InstalledConfig = {
    version: pkg.version,
    tools: mergedTools,
    suites: mergedSuites,
    skills: mergedSkills,
    installedAt: existingConfig?.installedAt ?? now,
    updatedAt: now,
  };
  await writeConfig(projectPath, config);

  // Remove legacy config if migrated
  if (legacyConfig && existsSync(legacyConfigPath)) {
    await rm(legacyConfigPath, { force: true });
  }

  spinner.succeed(
    `Installed ${totalSkillsInstalled} skills and ${totalCommandsInstalled} commands for ${selectedToolValues.length} tool(s).`,
  );
  console.log(chalk.green(`Config written to ${CONFIG_FILENAME}`));
}

async function selectTools(): Promise<string[]> {
  const choices = MAGIC_TOOLS.map((t) => ({
    name: t.name,
    value: t.value,
    checked: false,
  }));
  return checkbox<string>({
    message: 'Select AI tools to install MAGIC skills for:',
    choices,
  });
}

function resolveSkillsFromSuites(
  suiteNames: string[],
  suiteConfigs: ReturnType<typeof getSuiteConfigs>,
): string[] {
  const skills: string[] = [];
  for (const name of suiteNames) {
    const suite = suiteConfigs.find((s) => s.name === name);
    if (suite) {
      skills.push(...suite.skills);
    }
  }
  return skills;
}

function resolveSuitesFromSkills(
  skills: string[],
  suiteConfigs: ReturnType<typeof getSuiteConfigs>,
): string[] {
  const suites = new Set<string>();
  for (const skill of skills) {
    for (const suite of suiteConfigs) {
      if (suite.skills.includes(skill)) {
        suites.add(suite.name);
      }
    }
  }
  return [...suites];
}
