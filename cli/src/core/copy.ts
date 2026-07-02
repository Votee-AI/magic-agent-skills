import { existsSync } from 'node:fs';
import { readdir, readFile, writeFile, mkdir, cp, rm } from 'node:fs/promises';
import { join, resolve } from 'node:path';
import {
  type ToolConfig,
  type InstalledConfig,
  MAGIC_TOOLS,
  SKILL_DIRS,
  COMMAND_FILES,
  CONFIG_FILENAME,
} from './config.js';
import { type CommandAdapter, getAdapter } from './adapters.js';

export async function ensureDir(path: string): Promise<void> {
  await mkdir(path, { recursive: true });
}

export async function copySkills(
  projectPath: string,
  tool: ToolConfig,
  sourceDir: string,
  skillFilter?: string[],
): Promise<number> {
  if (!tool.skillsDir) return 0;

  const source = join(sourceDir, 'skills');
  const destBase = join(projectPath, tool.skillsDir, 'skills');
  let count = 0;

  const skillsToInstall = skillFilter ?? SKILL_DIRS;

  for (const skillDir of skillsToInstall) {
    const src = join(source, skillDir);
    if (!existsSync(src)) continue;

    const dest = join(destBase, skillDir);
    await ensureDir(dest);
    await cp(src, dest, { recursive: true, force: true });
    count++;
  }

  return count;
}

export async function copyCommands(
  projectPath: string,
  tool: ToolConfig,
  sourceDir: string,
): Promise<number> {
  if (!tool.commandsDir || !tool.commandFormat) return 0;

  const adapter = getAdapter(tool.commandFormat);
  if (!adapter) return 0;

  let count = 0;

  for (const [group, files] of Object.entries(COMMAND_FILES)) {
    const source = join(sourceDir, 'commands', group);
    if (!existsSync(source)) continue;

    // commandsDir is the literal base; append the group leaf so e.g.
    // Windsurf installs to `.windsurf/workflows/data`, not `.windsurf/data`.
    const destDir = join(projectPath, tool.commandsDir, group);
    await ensureDir(destDir);

    for (const file of files) {
      const srcPath = join(source, file);
      if (!existsSync(srcPath)) continue;

      const content = await readFile(srcPath, 'utf-8');
      const adapted = adapter.adapt(file, content, group);
      await writeFile(join(destDir, adapted.filename), adapted.content, 'utf-8');
      count++;
    }
  }

  return count;
}

export async function removeSkills(
  projectPath: string,
  tool: ToolConfig,
  skillFilter?: string[],
): Promise<number> {
  if (!tool.skillsDir) return 0;

  const destBase = join(projectPath, tool.skillsDir, 'skills');
  let count = 0;

  const skillsToRemove = skillFilter ?? SKILL_DIRS;

  for (const skillDir of skillsToRemove) {
    const dest = join(destBase, skillDir);
    if (existsSync(dest)) {
      await rm(dest, { recursive: true, force: true });
      count++;
    }
  }

  return count;
}

export async function removeCommands(
  projectPath: string,
  tool: ToolConfig,
): Promise<number> {
  if (!tool.commandsDir || !tool.commandFormat) return 0;

  const adapter = getAdapter(tool.commandFormat);
  if (!adapter) return 0;

  let count = 0;

  for (const [group, files] of Object.entries(COMMAND_FILES)) {
    // Identical path logic to copyCommands: commandsDir is the literal base.
    const destDir = join(projectPath, tool.commandsDir, group);
    if (!existsSync(destDir)) continue;

    for (const file of files) {
      const adapted = adapter.adapt(file, '', group).filename;
      const target = join(destDir, adapted);
      if (existsSync(target)) {
        await rm(target, { force: true });
        count++;
      }
    }

    const remaining = await readdir(destDir);
    if (remaining.length === 0) {
      await rm(destDir, { recursive: true, force: true });
    }
  }

  return count;
}

export function configPath(projectPath: string): string {
  return join(projectPath, CONFIG_FILENAME);
}

export class ConfigCorruptError extends Error {
  constructor(public readonly cause: unknown) {
    super(
      `Config file "${CONFIG_FILENAME}" is corrupt and could not be parsed — ` +
        `run \`init --force\` to recreate it.`,
    );
    this.name = 'ConfigCorruptError';
  }
}

export async function readConfig(
  projectPath: string,
): Promise<InstalledConfig | null> {
  const path = configPath(projectPath);
  if (!existsSync(path)) return null;
  const raw = await readFile(path, 'utf-8');

  let parsed: unknown;
  try {
    parsed = JSON.parse(raw);
  } catch (err) {
    throw new ConfigCorruptError(err);
  }

  if (typeof parsed !== 'object' || parsed === null) {
    throw new ConfigCorruptError(new Error('config is not an object'));
  }

  // Tolerate/repair missing required arrays so update/remove never throw
  // `undefined is not iterable` on a partially-written config.
  const obj = parsed as Record<string, unknown>;
  return {
    version: typeof obj.version === 'string' ? obj.version : '0.0.0',
    tools: Array.isArray(obj.tools) ? (obj.tools as string[]) : [],
    suites: Array.isArray(obj.suites) ? (obj.suites as string[]) : [],
    skills: Array.isArray(obj.skills) ? (obj.skills as string[]) : [],
    installedAt:
      typeof obj.installedAt === 'string'
        ? obj.installedAt
        : new Date().toISOString(),
    updatedAt:
      typeof obj.updatedAt === 'string'
        ? obj.updatedAt
        : new Date().toISOString(),
  };
}

export async function writeConfig(
  projectPath: string,
  config: InstalledConfig,
): Promise<void> {
  const path = configPath(projectPath);
  await writeFile(path, JSON.stringify(config, null, 2) + '\n', 'utf-8');
}

export function detectTools(projectPath: string): string[] {
  const detected: string[] = [];

  for (const tool of MAGIC_TOOLS) {
    if (!tool.skillsDir) continue;
    // Prefer a tool-specific marker when defined (avoids over-detecting tools
    // whose skillsDir is a generic shared dir like `.github`).
    const marker = tool.detectMarker ?? tool.skillsDir;
    if (existsSync(join(projectPath, marker))) {
      detected.push(tool.value);
    }
  }

  return detected;
}
