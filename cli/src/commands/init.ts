import { existsSync } from 'node:fs';
import { readFile, rm } from 'node:fs/promises';
import { join } from 'node:path';
import { select, Separator } from '@inquirer/prompts';
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
  ConfigCorruptError,
} from '../core/copy.js';
import { getSuiteConfigs } from '../core/manifest.js';
import { fetchFromGitHub, cleanupFetchDir } from '../core/fetch.js';
import { customSelect, customCheckbox, BackSignal } from '../core/prompts.js';

const ACCENT = chalk.hex('#00BCD4');
const DIM = chalk.dim;

/** Sentinel value returned by a "← Back" choice in any select/checkbox. */
const BACK = '__back__';
const BACK_CHOICE = { name: '← Back', value: BACK } as const;

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
  console.log('  ' + DIM(`v${version} · ${totalSkills} skills · data + linguistic`));
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
  yes?: boolean;
  dryRun?: boolean;
}

type SuiteConfigs = ReturnType<typeof getSuiteConfigs>;

export async function init(options: InitOptions): Promise<void> {
  const projectPath = process.cwd();

  // --yes or a non-interactive (non-TTY) environment must never block on a prompt.
  const nonInteractive =
    !!options.yes || !!options.suites || !!options.skills || !process.stdin.isTTY;

  // Check for existing installation
  let existingConfig: InstalledConfig | null;
  try {
    existingConfig = await readConfig(projectPath);
  } catch (err) {
    if (err instanceof ConfigCorruptError) {
      console.log(chalk.red(`\n  ${err.message}\n`));
      process.exitCode = 1;
      return;
    }
    throw err;
  }

  let addMode = false;

  if (existingConfig && !options.force) {
    if (options.suites || options.skills) {
      addMode = true;
    } else if (nonInteractive) {
      // --yes on an existing install: default to "add more".
      addMode = true;
    } else {
      const existingCount = existingConfig.skills?.length ?? 0;
      const existingSuites = existingConfig.suites?.join(', ') || 'unknown';
      console.log(chalk.dim(`  Installed: ${existingCount} skills (${existingSuites})\n`));

      const action = await runPrompt(() =>
        select({
          message: 'MAGIC Agent Skills already installed. What would you like to do?',
          choices: [
            { name: 'Add more skills to this installation', value: 'add' },
            { name: 'Reinstall from scratch', value: 'reinstall' },
            { name: 'Cancel', value: 'cancel' },
          ],
        }),
      );

      if (action === 'cancel') {
        console.log(chalk.dim('  Cancelled.'));
        return;
      }
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
    const migrate = nonInteractive
      ? true
      : await runConfirm(
          'Existing MAGIC Data installation detected. Migrate to unified installer?',
          true,
        );
    if (migrate) {
      preSelectedSuites = ['data'];
      preSelectedTools = legacyConfig.tools ?? [];
    }
  }

  // Read version from local package.json
  const pkg = JSON.parse(
    await readFile(join(getPackageRoot(), 'package.json'), 'utf8'),
  ) as { version: string };

  // --- Fetch latest skills from GitHub ---
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
    const skillsDir = join(sourceDir, 'skills');
    let suiteConfigs: SuiteConfigs = [];
    try {
      suiteConfigs = getSuiteConfigs(skillsDir, pkg.version);
    } catch {
      // Manifest discovery failed — fall back to empty (backward compat)
      suiteConfigs = [];
    }

    // Show banner in interactive mode
    const isInteractive = !nonInteractive;
    if (isInteractive) {
      const totalSkills = suiteConfigs.reduce((sum, s) => sum + s.skills.length, 0);
      printBanner(pkg.version, totalSkills || 30);
    }

    // --- Resolve the selection (flags, pre-selection, or interactive). ---
    let selectedSkills: string[];
    let selectedSuites: string[];
    let selectedToolValues: string[];

    if (options.skills) {
      // --skills flag: explicit list
      selectedSkills = options.skills.split(',').map((s) => s.trim()).filter(Boolean);
      selectedSuites = resolveSuitesFromSkills(selectedSkills, suiteConfigs);
      selectedToolValues = resolveToolsNonInteractive(options, projectPath, preSelectedTools);
    } else if (options.suites) {
      // --suites flag
      const suiteArg = options.suites.trim();
      selectedSuites =
        suiteArg === 'all'
          ? suiteConfigs.map((s) => s.name)
          : suiteArg.split(',').map((s) => s.trim()).filter(Boolean);
      selectedSkills = resolveSkillsFromSuites(selectedSuites, suiteConfigs);
      selectedToolValues = resolveToolsNonInteractive(options, projectPath, preSelectedTools);
    } else if (nonInteractive) {
      // --yes / non-TTY with no explicit selection: accept sensible defaults.
      if (preSelectedSuites.length > 0) {
        selectedSuites = preSelectedSuites;
      } else if (suiteConfigs.length > 0) {
        selectedSuites = suiteConfigs.map((s) => s.name);
      } else {
        selectedSuites = ['data'];
      }
      selectedSkills = resolveSkillsFromSuites(selectedSuites, suiteConfigs);
      selectedToolValues = resolveToolsNonInteractive(options, projectPath, preSelectedTools);
    } else if (preSelectedSuites.length > 0) {
      // Pre-selected from legacy migration (tools also pre-selected).
      selectedSuites = preSelectedSuites;
      selectedSkills = resolveSkillsFromSuites(selectedSuites, suiteConfigs);
      selectedToolValues = resolveToolsNonInteractive(options, projectPath, preSelectedTools);
    } else {
      // Interactive flow with back-navigation. Returns null on a clean exit.
      const result = await runInteractive(suiteConfigs, projectPath);
      if (result === null) {
        console.log(chalk.dim('  Cancelled.'));
        return;
      }
      selectedSkills = result.skills;
      selectedSuites = result.suites;
      selectedToolValues = result.tools;
    }

    if (selectedToolValues.length === 0) {
      console.log(chalk.yellow('No tools selected. Aborting.'));
      return;
    }

    // --- Summary ---
    const totalCommandTools = selectedToolValues
      .map((v) => getToolByValue(v))
      .filter((t) => t && t.commandsDir && t.commandFormat).length;
    console.log('');
    console.log(
      chalk.bold(
        `  Plan: install ${selectedSkills.length || 'all'} skills` +
          `${totalCommandTools > 0 ? ' + commands' : ''}` +
          ` into ${selectedToolValues.length} tool(s): ${selectedToolValues.join(', ')}`,
      ),
    );
    console.log('');

    if (options.dryRun) {
      console.log(chalk.cyan('  --dry-run: no files were written.'));
      return;
    }

    // --- Installation (per-tool recovery: one failure must not abort the rest). ---
    const spinner = ora('Installing MAGIC Agent Skills...').start();
    let totalSkillsInstalled = 0;
    let totalCommandsInstalled = 0;
    const succeededTools: string[] = [];
    const failures: string[] = [];

    for (const toolValue of selectedToolValues) {
      const tool = getToolByValue(toolValue);
      if (!tool) {
        spinner.warn(`Unknown tool: ${toolValue}`);
        continue;
      }

      try {
        const skillFilter = selectedSkills.length > 0 ? selectedSkills : undefined;
        const skillCount = await copySkills(projectPath, tool, sourceDir, skillFilter);
        const cmdCount = await copyCommands(projectPath, tool, sourceDir);
        totalSkillsInstalled += skillCount;
        totalCommandsInstalled += cmdCount;
        succeededTools.push(toolValue);
      } catch (err) {
        const msg = err instanceof Error ? err.message : String(err);
        spinner.warn(`Failed to install for ${toolValue}: ${msg}`);
        failures.push(toolValue);
      }
    }

    // Write config reflecting only what actually succeeded.
    const now = new Date().toISOString();
    const mergedTools = addMode && existingConfig
      ? [...new Set([...existingConfig.tools, ...succeededTools])]
      : succeededTools;
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
    if (succeededTools.length > 0) {
      await writeConfig(projectPath, config);
    }

    // Remove legacy config if migrated
    if (legacyConfig && existsSync(legacyConfigPath)) {
      await rm(legacyConfigPath, { force: true });
    }

    if (succeededTools.length === 0) {
      spinner.fail('Installation failed for all selected tools.');
      process.exitCode = 1;
      return;
    }

    spinner.succeed(
      `Installed ${totalSkillsInstalled} skills and ${totalCommandsInstalled} commands for ${succeededTools.length} tool(s).`,
    );
    if (failures.length > 0) {
      console.log(chalk.yellow(`  Skipped (failed): ${failures.join(', ')}`));
    }
    console.log(chalk.green(`Config written to ${CONFIG_FILENAME}`));
  } catch (err) {
    if (err instanceof Error && err.name === 'ExitPromptError') {
      // Ctrl-C in a non-TTY / piped context: @inquirer/core rejects the prompt
      // with ExitPromptError (the raw keypress that core/prompts.ts intercepts on
      // a real TTY is never delivered here). Set 130 so the process still signals
      // an interrupt. On a real TTY this branch is not reached — the prompt's
      // keypress guard exits 130 synchronously first.
      process.exitCode = 130;
      return;
    }
    throw err;
  } finally {
    await cleanupFetchDir(sourceDir);
  }
}

interface InteractiveResult {
  skills: string[];
  suites: string[];
  tools: string[];
}

/**
 * Explicit step state-machine for the interactive flow. An ordered list of
 * steps share a single `answers` object and a cursor. A "← Back" choice (the
 * BACK sentinel, first option in each select/checkbox) decrements the cursor;
 * ESC (ExitPromptError) does the same. ESC/Back on the first step exits cleanly
 * (returns null). The natural last step is the install confirm.
 */
async function runInteractive(
  suiteConfigs: SuiteConfigs,
  projectPath: string,
): Promise<InteractiveResult | null> {
  const answers: {
    selectionMode?: string;
    skills?: string[];
    suites?: string[];
    tools?: string[];
    confirmed?: boolean;
  } = {};

  // 'next'/'back' move the cursor; 'skip' is for inapplicable steps and
  // continues travel in whatever direction the step was ENTERED from (so
  // back-navigation glides over skipped steps instead of bouncing forward).
  type Step = () => Promise<'next' | 'back' | 'skip'>;

  const detected = detectTools(projectPath);

  const stepSelectionMode: Step = async () => {
    if (suiteConfigs.length === 0) {
      // No manifest — default to data suite, skip selection.
      answers.suites = ['data'];
      answers.skills = [];
      answers.selectionMode = 'all';
      return 'skip';
    }
    const totalSkills = suiteConfigs.reduce((sum, s) => sum + s.skills.length, 0);
    const choice = await promptSelect<string>({
      message: 'Which MAGIC skills would you like to install?',
      choices: [
        { name: `All MAGIC skills (${totalSkills} skills)`, value: 'all' },
        ...suiteConfigs.map((suite) => ({
          name: `${suite.displayName} suite (${suite.skills.length} skills)`,
          value: `suite:${suite.name}`,
        })),
        { name: 'Select individual skills', value: 'individual' },
      ],
    });
    if (choice === BACK) return 'back';
    answers.selectionMode = choice;
    if (choice === 'all') {
      answers.suites = suiteConfigs.map((s) => s.name);
      answers.skills = resolveSkillsFromSuites(answers.suites, suiteConfigs);
    } else if (choice.startsWith('suite:')) {
      const suiteName = choice.slice('suite:'.length);
      answers.suites = [suiteName];
      answers.skills = resolveSkillsFromSuites(answers.suites, suiteConfigs);
    }
    return 'next';
  };

  const stepIndividualSkills: Step = async () => {
    if (answers.selectionMode !== 'individual') return 'skip';
    const choices: Array<Separator | { name: string; value: string; checked: boolean }> = [];
    for (const suite of suiteConfigs) {
      choices.push(new Separator(`── ${suite.displayName} ──`));
      for (const skill of suite.skills) {
        choices.push({ name: skill, value: skill, checked: false });
      }
    }
    const picked = await promptCheckbox({
      message: 'Select skills to install (space to toggle, enter to confirm):',
      choices,
    });
    answers.skills = picked;
    answers.suites = resolveSuitesFromSkills(picked, suiteConfigs);
    return 'next';
  };

  const stepTools: Step = async () => {
    let useDetected = false;
    if (detected.length > 0) {
      const choice = await promptSelect<string>({
        message: `Detected AI tools: ${detected.join(', ')}. Install for these tools?`,
        choices: [
          { name: 'Yes', value: 'yes' },
          { name: 'No', value: 'no' },
        ],
      });
      if (choice === BACK) return 'back';
      useDetected = choice === 'yes';
    }
    if (useDetected) {
      answers.tools = detected;
    } else {
      const picked = await promptCheckbox({
        message: 'Select AI tools to install MAGIC skills for:',
        choices: MAGIC_TOOLS.map((t) => ({ name: t.name, value: t.value, checked: false })),
      });
      answers.tools = picked;
    }
    return 'next';
  };

  const stepConfirm: Step = async () => {
    const toolList = (answers.tools ?? []).join(', ') || 'none';
    const skillCount = answers.skills?.length ?? 0;
    const choice = await promptSelect<string>({
      message: `Install ${skillCount || 'all'} skills into tools: ${toolList}?`,
      choices: [
        { name: 'Yes, install', value: 'yes' },
        { name: 'No, cancel', value: 'no' },
      ],
    });
    if (choice === BACK) return 'back';
    answers.confirmed = choice === 'yes';
    return 'next';
  };

  const steps: Step[] = [stepSelectionMode, stepIndividualSkills, stepTools, stepConfirm];

  let cursor = 0;
  // Direction we're currently traveling; 'skip' continues this direction.
  let direction: 1 | -1 = 1;
  while (cursor < steps.length) {
    let outcome: 'next' | 'back' | 'skip';
    try {
      outcome = await steps[cursor]!();
    } catch (err) {
      if (err instanceof BackSignal) {
        // ESC from a custom prompt — go back one step.
        outcome = 'back';
      } else {
        throw err;
      }
    }
    if (outcome === 'skip') {
      cursor += direction;
    } else if (outcome === 'back') {
      direction = -1;
      cursor -= 1;
    } else {
      direction = 1;
      cursor += 1;
    }
    if (cursor < 0) return null; // Back/ESC past the first step exits cleanly.
  }

  if (!answers.confirmed) return null;
  return {
    skills: answers.skills ?? [],
    suites: answers.suites ?? [],
    tools: answers.tools ?? [],
  };
}

/** customSelect() with a leading "← Back" sentinel choice. */
function promptSelect<T extends string>(opts: {
  message: string;
  choices: Array<{ name: string; value: T }>;
}): Promise<T | typeof BACK> {
  return customSelect<T | typeof BACK>({
    message: opts.message,
    choices: [BACK_CHOICE, ...opts.choices],
  });
}

/**
 * customCheckbox() — ESC throws BackSignal, caught by runInteractive.
 * Returns string[] on confirm; never returns the BACK sentinel (ESC rejects
 * with BackSignal instead, handled by the runInteractive loop).
 */
async function promptCheckbox(opts: {
  message: string;
  choices: Array<Separator | { name: string; value: string; checked: boolean }>;
}): Promise<string[]> {
  return customCheckbox({
    message: opts.message,
    choices: opts.choices,
  });
}

/**
 * Runs a stock @inquirer/prompts prompt. Stock inquirer throws ExitPromptError
 * only on Ctrl-C (ESC is inert there). The locked decision is Ctrl-C = hard
 * quit, exit 130, everywhere — so on ExitPromptError we exit 130 rather than
 * returning a fallback. These prompts run BEFORE the GitHub fetch, so there is
 * no temp dir to clean.
 */
async function runPrompt<T>(prompt: () => Promise<T>): Promise<T> {
  try {
    return await prompt();
  } catch (err) {
    if (err instanceof Error && err.name === 'ExitPromptError') {
      process.stdout.write('\n');
      process.exit(130);
    }
    throw err;
  }
}

/** confirm-style Yes/No via select so the default can be highlighted. */
async function runConfirm(message: string, defaultYes: boolean): Promise<boolean> {
  const choice = await runPrompt(() =>
    select<string>({
      message,
      choices: [
        { name: 'Yes', value: 'yes' },
        { name: 'No', value: 'no' },
      ],
      default: defaultYes ? 'yes' : 'no',
    }),
  );
  return choice === 'yes';
}

function resolveToolsNonInteractive(
  options: InitOptions,
  projectPath: string,
  preSelectedTools: string[],
): string[] {
  if (options.tools) {
    if (options.tools === 'all') return MAGIC_TOOLS.map((t) => t.value);
    return options.tools.split(',').map((s) => s.trim()).filter(Boolean);
  }
  if (preSelectedTools.length > 0) return preSelectedTools;
  const detected = detectTools(projectPath);
  return detected;
}

function resolveSkillsFromSuites(
  suiteNames: string[],
  suiteConfigs: SuiteConfigs,
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
  suiteConfigs: SuiteConfigs,
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
