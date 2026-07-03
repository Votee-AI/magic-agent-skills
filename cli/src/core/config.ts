import { fileURLToPath } from 'node:url';
import { dirname, resolve } from 'node:path';

export interface ToolConfig {
  name: string;
  value: string;
  skillsDir: string | undefined;
  commandsDir: string | null;
  commandFormat: 'md' | 'toml' | 'prompt' | null;
  /**
   * Optional, more-specific marker for auto-detection. When set, `detectTools`
   * requires THIS path (relative to the project) to exist rather than just the
   * `skillsDir`. Used to avoid over-detecting tools whose `skillsDir` is a
   * generic shared directory (e.g. `.github`, which exists in most repos).
   */
  detectMarker?: string;
}

export interface InstalledConfig {
  version: string;
  tools: string[];
  suites: string[];
  skills: string[];
  installedAt: string;
  updatedAt: string;
}

// Adapted from OpenSpec's AI_TOOLS registry (MIT licensed)
// Extended with MAGIC-specific commandsDir and commandFormat fields.
//
// `commandsDir` is the LITERAL base directory under which the per-suite command
// group (e.g. `data`, `linguistic`) is created. copyCommands/removeCommands
// append the group leaf — so Claude installs to `.claude/commands/data` and
// `.claude/commands/linguistic`, Windsurf to `.windsurf/workflows/data`, etc.
// Do NOT bake a group leaf into these values.
export const MAGIC_TOOLS: ToolConfig[] = [
  { name: 'Amazon Q Developer', value: 'amazon-q', skillsDir: '.amazonq', commandsDir: '.amazonq/commands', commandFormat: 'md' },
  { name: 'Antigravity', value: 'antigravity', skillsDir: '.agent', commandsDir: '.agent/commands', commandFormat: 'md' },
  { name: 'Auggie (Augment CLI)', value: 'auggie', skillsDir: '.augment', commandsDir: '.augment/commands', commandFormat: 'md' },
  { name: 'Bob Shell', value: 'bob', skillsDir: '.bob', commandsDir: null, commandFormat: null },
  { name: 'Claude Code', value: 'claude', skillsDir: '.claude', commandsDir: '.claude/commands', commandFormat: 'md' },
  { name: 'Cline', value: 'cline', skillsDir: '.cline', commandsDir: '.cline/commands', commandFormat: 'md' },
  { name: 'Codex', value: 'codex', skillsDir: '.codex', commandsDir: null, commandFormat: null },
  { name: 'CodeBuddy Code (CLI)', value: 'codebuddy', skillsDir: '.codebuddy', commandsDir: '.codebuddy/commands', commandFormat: 'md' },
  { name: 'Continue', value: 'continue', skillsDir: '.continue', commandsDir: '.continue/prompts', commandFormat: 'prompt' },
  { name: 'CoStrict', value: 'costrict', skillsDir: '.cospec', commandsDir: null, commandFormat: null },
  { name: 'Crush', value: 'crush', skillsDir: '.crush', commandsDir: '.crush/commands', commandFormat: 'md' },
  { name: 'Cursor', value: 'cursor', skillsDir: '.cursor', commandsDir: '.cursor/commands', commandFormat: 'md' },
  { name: 'Factory Droid', value: 'factory', skillsDir: '.factory', commandsDir: null, commandFormat: null },
  { name: 'ForgeCode', value: 'forgecode', skillsDir: '.forge', commandsDir: null, commandFormat: null },
  { name: 'Gemini CLI', value: 'gemini', skillsDir: '.gemini', commandsDir: '.gemini/commands', commandFormat: 'toml' },
  { name: 'GitHub Copilot', value: 'github-copilot', skillsDir: '.github', commandsDir: '.github/prompts', commandFormat: 'prompt', detectMarker: '.github/copilot-instructions.md' },
  { name: 'iFlow', value: 'iflow', skillsDir: '.iflow', commandsDir: null, commandFormat: null },
  { name: 'Junie', value: 'junie', skillsDir: '.junie', commandsDir: '.junie/commands', commandFormat: 'md' },
  { name: 'Kilo Code', value: 'kilocode', skillsDir: '.kilocode', commandsDir: '.kilocode/commands', commandFormat: 'md' },
  { name: 'Kimi CLI', value: 'kimi', skillsDir: '.kimi', commandsDir: null, commandFormat: null },
  { name: 'Kiro', value: 'kiro', skillsDir: '.kiro', commandsDir: '.kiro/commands', commandFormat: 'md' },
  { name: 'Lingma', value: 'lingma', skillsDir: '.lingma', commandsDir: '.lingma/commands', commandFormat: 'toml' },
  { name: 'OpenCode', value: 'opencode', skillsDir: '.opencode', commandsDir: '.opencode/commands', commandFormat: 'md' },
  { name: 'Pi', value: 'pi', skillsDir: '.pi', commandsDir: null, commandFormat: null },
  { name: 'Qoder', value: 'qoder', skillsDir: '.qoder', commandsDir: '.qoder/commands', commandFormat: 'md' },
  { name: 'Qwen Code', value: 'qwen', skillsDir: '.qwen', commandsDir: '.qwen/commands', commandFormat: 'toml' },
  { name: 'RooCode', value: 'roocode', skillsDir: '.roo', commandsDir: '.roo/commands', commandFormat: 'md' },
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
  'magic-linguistic-annotate',
  'magic-linguistic-bitext',
  'magic-linguistic-codeswitch',
  'magic-linguistic-corpus',
  'magic-linguistic-discourse',
  'magic-linguistic-ethics',
  'magic-linguistic-eval',
  'magic-linguistic-historical',
  'magic-linguistic-lexicon',
  'magic-linguistic-morph',
  'magic-linguistic-orchestrator',
  'magic-linguistic-scope',
  'magic-linguistic-scripts',
  'magic-linguistic-semantics',
  'magic-linguistic-speech',
  'magic-linguistic-syntax',
  'magic-linguistic-tokenize',
  'magic-linguistic-transfer',
] as const;

export const COMMAND_FILES = {
  data: [
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
