import { fileURLToPath } from 'node:url';
import { dirname, resolve } from 'node:path';

export interface ToolConfig {
  name: string;
  value: string;
  skillsDir: string | undefined;
  commandsDir: string | null;
  commandFormat: 'md' | 'toml' | 'prompt' | null;
}

export interface InstalledConfig {
  version: string;
  tools: string[];
  installedAt: string;
  updatedAt: string;
}

// Adapted from OpenSpec's AI_TOOLS registry (MIT licensed)
// Extended with MAGIC-specific commandsDir and commandFormat fields
export const MAGIC_TOOLS: ToolConfig[] = [
  { name: 'Amazon Q Developer', value: 'amazon-q', skillsDir: '.amazonq', commandsDir: '.amazonq/commands/magic', commandFormat: 'md' },
  { name: 'Antigravity', value: 'antigravity', skillsDir: '.agent', commandsDir: '.agent/commands/magic', commandFormat: 'md' },
  { name: 'Auggie (Augment CLI)', value: 'auggie', skillsDir: '.augment', commandsDir: '.augment/commands/magic', commandFormat: 'md' },
  { name: 'Bob Shell', value: 'bob', skillsDir: '.bob', commandsDir: null, commandFormat: null },
  { name: 'Claude Code', value: 'claude', skillsDir: '.claude', commandsDir: '.claude/commands/magic', commandFormat: 'md' },
  { name: 'Cline', value: 'cline', skillsDir: '.cline', commandsDir: '.cline/commands/magic', commandFormat: 'md' },
  { name: 'Codex', value: 'codex', skillsDir: '.codex', commandsDir: null, commandFormat: null },
  { name: 'CodeBuddy Code (CLI)', value: 'codebuddy', skillsDir: '.codebuddy', commandsDir: '.codebuddy/commands/magic', commandFormat: 'md' },
  { name: 'Continue', value: 'continue', skillsDir: '.continue', commandsDir: '.continue/prompts', commandFormat: 'prompt' },
  { name: 'CoStrict', value: 'costrict', skillsDir: '.cospec', commandsDir: null, commandFormat: null },
  { name: 'Crush', value: 'crush', skillsDir: '.crush', commandsDir: '.crush/commands/magic', commandFormat: 'md' },
  { name: 'Cursor', value: 'cursor', skillsDir: '.cursor', commandsDir: '.cursor/commands/magic', commandFormat: 'md' },
  { name: 'Factory Droid', value: 'factory', skillsDir: '.factory', commandsDir: null, commandFormat: null },
  { name: 'ForgeCode', value: 'forgecode', skillsDir: '.forge', commandsDir: null, commandFormat: null },
  { name: 'Gemini CLI', value: 'gemini', skillsDir: '.gemini', commandsDir: '.gemini/commands/magic', commandFormat: 'toml' },
  { name: 'GitHub Copilot', value: 'github-copilot', skillsDir: '.github', commandsDir: '.github/prompts', commandFormat: 'prompt' },
  { name: 'iFlow', value: 'iflow', skillsDir: '.iflow', commandsDir: null, commandFormat: null },
  { name: 'Junie', value: 'junie', skillsDir: '.junie', commandsDir: '.junie/commands/magic', commandFormat: 'md' },
  { name: 'Kilo Code', value: 'kilocode', skillsDir: '.kilocode', commandsDir: '.kilocode/commands/magic', commandFormat: 'md' },
  { name: 'Kimi CLI', value: 'kimi', skillsDir: '.kimi', commandsDir: null, commandFormat: null },
  { name: 'Kiro', value: 'kiro', skillsDir: '.kiro', commandsDir: '.kiro/commands/magic', commandFormat: 'md' },
  { name: 'Lingma', value: 'lingma', skillsDir: '.lingma', commandsDir: '.lingma/commands/magic', commandFormat: 'toml' },
  { name: 'OpenCode', value: 'opencode', skillsDir: '.opencode', commandsDir: '.opencode/commands/magic', commandFormat: 'md' },
  { name: 'Pi', value: 'pi', skillsDir: '.pi', commandsDir: null, commandFormat: null },
  { name: 'Qoder', value: 'qoder', skillsDir: '.qoder', commandsDir: '.qoder/commands/magic', commandFormat: 'md' },
  { name: 'Qwen Code', value: 'qwen', skillsDir: '.qwen', commandsDir: '.qwen/commands/magic', commandFormat: 'toml' },
  { name: 'RooCode', value: 'roocode', skillsDir: '.roo', commandsDir: '.roo/commands/magic', commandFormat: 'md' },
  { name: 'Trae', value: 'trae', skillsDir: '.trae', commandsDir: null, commandFormat: null },
  { name: 'Windsurf', value: 'windsurf', skillsDir: '.windsurf', commandsDir: '.windsurf/workflows', commandFormat: 'md' },
  { name: 'AGENTS.md', value: 'agents', skillsDir: undefined, commandsDir: null, commandFormat: null },
];

export const SKILL_DIRS = [
  'magic-data-cleaning',
  'magic-data-exploration',
  'magic-data-lifecycle',
  'magic-data-loading',
  'magic-data-profiling',
  'magic-data-synthesis',
  'magic-data-transformation',
  'magic-data-validation',
  'magic-data-visualization',
  'magic-report-generation',
  'magic-statistical-analysis',
  'magic-workspace-init',
  'linguistic-annotate',
  'linguistic-bitext',
  'linguistic-codeswitch',
  'linguistic-corpus',
  'linguistic-discourse',
  'linguistic-ethics',
  'linguistic-eval',
  'linguistic-historical',
  'linguistic-lexicon',
  'linguistic-morph',
  'linguistic-orchestrator',
  'linguistic-scope',
  'linguistic-scripts',
  'linguistic-semantics',
  'linguistic-speech',
  'linguistic-syntax',
  'linguistic-tokenize',
  'linguistic-transfer',
] as const;

export const COMMAND_FILES = {
  magic: [
    'connect.md',
    'decide.md',
    'deliver.md',
    'explore.md',
    'findings.md',
    'help.md',
    'init-workspace.md',
    'lifecycle.md',
    'propose.md',
    'review.md',
    'rollback.md',
    'spec.md',
    'status.md',
  ],
  linguistic: [
    'decide.md',
    'explore.md',
    'findings.md',
    'help.md',
    'lifecycle.md',
    'propose.md',
    'review.md',
    'rollback.md',
    'spec.md',
    'status.md',
  ],
} as const;

export const CONFIG_FILENAME = 'magic-agent-skills.json';

export function getPackageRoot(): string {
  const __filename = fileURLToPath(import.meta.url);
  // dist/core/config.js → package root
  return resolve(dirname(__filename), '..', '..');
}

export function getToolByValue(value: string): ToolConfig | undefined {
  return MAGIC_TOOLS.find((t) => t.value === value);
}
