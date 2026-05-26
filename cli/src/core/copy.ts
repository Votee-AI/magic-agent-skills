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
  getPackageRoot,
} from './config.js';
import { type CommandAdapter, getAdapter } from './adapters.js';

export async function ensureDir(path: string): Promise<void> {
  await mkdir(path, { recursive: true });
}

export function getSkillsSource(): string {
  return join(getPackageRoot(), 'skills');
}

export function getCommandsSource(): string {
  return join(getPackageRoot(), 'commands', 'magic');
}

export async function copySkills(
  projectPath: string,
  tool: ToolConfig,
): Promise<number> {
  if (!tool.skillsDir) return 0;

  const source = getSkillsSource();
  const destBase = join(projectPath, tool.skillsDir, 'skills');
  let count = 0;

  for (const skillDir of SKILL_DIRS) {
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
): Promise<number> {
  if (!tool.commandsDir || !tool.commandFormat) return 0;

  const adapter = getAdapter(tool.commandFormat);
  if (!adapter) return 0;

  const source = getCommandsSource();
  if (!existsSync(source)) return 0;

  const destDir = join(projectPath, tool.commandsDir);
  await ensureDir(destDir);

  let count = 0;
  for (const file of COMMAND_FILES) {
    const srcPath = join(source, file);
    if (!existsSync(srcPath)) continue;

    const content = await readFile(srcPath, 'utf-8');
    const adapted = adapter.adapt(file, content);
    await writeFile(join(destDir, adapted.filename), adapted.content, 'utf-8');
    count++;
  }

  return count;
}

export async function removeSkills(
  projectPath: string,
  tool: ToolConfig,
): Promise<number> {
  if (!tool.skillsDir) return 0;

  const destBase = join(projectPath, tool.skillsDir, 'skills');
  let count = 0;

  for (const skillDir of SKILL_DIRS) {
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
  if (!tool.commandsDir) return 0;

  const destDir = join(projectPath, tool.commandsDir);
  if (!existsSync(destDir)) return 0;

  const files = await readdir(destDir);
  let count = 0;

  for (const file of files) {
    if (file.startsWith('magic-') || COMMAND_FILES.includes(file as any)) {
      await rm(join(destDir, file), { force: true });
      count++;
    }
  }

  // Remove the directory if empty
  const remaining = await readdir(destDir);
  if (remaining.length === 0) {
    await rm(destDir, { recursive: true, force: true });
  }

  return count;
}

export function configPath(projectPath: string): string {
  return join(projectPath, CONFIG_FILENAME);
}

export async function readConfig(
  projectPath: string,
): Promise<InstalledConfig | null> {
  const path = configPath(projectPath);
  if (!existsSync(path)) return null;
  const raw = await readFile(path, 'utf-8');
  return JSON.parse(raw) as InstalledConfig;
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
    if (existsSync(join(projectPath, tool.skillsDir))) {
      detected.push(tool.value);
    }
  }

  return detected;
}
