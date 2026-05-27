import { describe, it, expect, beforeEach, afterEach } from 'vitest';
import { existsSync } from 'node:fs';
import { readFile, writeFile, mkdir, rm, readdir } from 'node:fs/promises';
import { join, resolve } from 'node:path';
import { tmpdir } from 'node:os';
import { fileURLToPath } from 'node:url';

// The repo root contains skills/ and commands/ directories used as sourceDir in tests.
const REPO_ROOT = resolve(fileURLToPath(import.meta.url), '..', '..', '..');

import {
  copySkills,
  copyCommands,
  removeSkills,
  removeCommands,
  readConfig,
  writeConfig,
  detectTools,
} from '../src/core/copy.js';
import { getToolByValue } from '../src/core/config.js';

let testDir: string;

beforeEach(async () => {
  testDir = join(tmpdir(), `magic-test-${Date.now()}`);
  await mkdir(testDir, { recursive: true });
});

afterEach(async () => {
  if (existsSync(testDir)) {
    await rm(testDir, { recursive: true, force: true });
  }
});

describe('copySkills', () => {
  it('copies all 30 skills to Claude directory', async () => {
    const claude = getToolByValue('claude')!;
    await mkdir(join(testDir, '.claude'), { recursive: true });
    const count = await copySkills(testDir, claude, REPO_ROOT);

    expect(count).toBe(30);
    expect(existsSync(join(testDir, '.claude/skills/magic-data-loading'))).toBe(true);
    expect(existsSync(join(testDir, '.claude/skills/magic-data-loading/SKILL.md'))).toBe(true);
    expect(existsSync(join(testDir, '.claude/skills/linguistic-tokenize'))).toBe(true);
    expect(existsSync(join(testDir, '.claude/skills/linguistic-tokenize/SKILL.md'))).toBe(true);
  });

  it('returns 0 for tools without skillsDir', async () => {
    const agents = getToolByValue('agents')!;
    const count = await copySkills(testDir, agents, REPO_ROOT);
    expect(count).toBe(0);
  });

  it('respects skillFilter — only copies selected skills', async () => {
    const claude = getToolByValue('claude')!;
    await mkdir(join(testDir, '.claude'), { recursive: true });
    const count = await copySkills(testDir, claude, REPO_ROOT, ['magic-data-loading', 'magic-data-profiling']);

    expect(count).toBe(2);
    expect(existsSync(join(testDir, '.claude/skills/magic-data-loading'))).toBe(true);
    expect(existsSync(join(testDir, '.claude/skills/magic-data-profiling'))).toBe(true);
    expect(existsSync(join(testDir, '.claude/skills/magic-data-cleaning'))).toBe(false);
  });
});

describe('copyCommands', () => {
  it('copies both data-agent and linguistic commands for Claude', async () => {
    const claude = getToolByValue('claude')!;
    const count = await copyCommands(testDir, claude, REPO_ROOT);

    if (count > 0) {
      expect(existsSync(join(testDir, '.claude/commands/data-agent'))).toBe(true);
      expect(existsSync(join(testDir, '.claude/commands/linguistic'))).toBe(true);
      const dataFiles = await readdir(join(testDir, '.claude/commands/data-agent'));
      const lingFiles = await readdir(join(testDir, '.claude/commands/linguistic'));
      expect(dataFiles.some((f) => f.endsWith('.md'))).toBe(true);
      expect(lingFiles.some((f) => f.endsWith('.md'))).toBe(true);
    }
  });

  it('converts to toml for Gemini', async () => {
    const gemini = getToolByValue('gemini')!;
    const count = await copyCommands(testDir, gemini, REPO_ROOT);

    if (count > 0) {
      const files = await readdir(join(testDir, '.gemini/commands/data-agent'));
      expect(files.some((f) => f.endsWith('.toml'))).toBe(true);
    }
  });

  it('returns 0 for skills-only tools', async () => {
    const codex = getToolByValue('codex')!;
    const count = await copyCommands(testDir, codex, REPO_ROOT);
    expect(count).toBe(0);
  });
});

describe('removeSkills', () => {
  it('removes previously copied skills', async () => {
    const claude = getToolByValue('claude')!;
    await mkdir(join(testDir, '.claude'), { recursive: true });
    await copySkills(testDir, claude, REPO_ROOT);
    expect(existsSync(join(testDir, '.claude/skills/magic-data-loading'))).toBe(true);

    const removed = await removeSkills(testDir, claude);
    expect(removed).toBe(30);
    expect(existsSync(join(testDir, '.claude/skills/magic-data-loading'))).toBe(false);
  });

  it('removes only filtered skills when skillFilter provided', async () => {
    const claude = getToolByValue('claude')!;
    await mkdir(join(testDir, '.claude'), { recursive: true });
    await copySkills(testDir, claude, REPO_ROOT);

    const removed = await removeSkills(testDir, claude, ['magic-data-loading']);
    expect(removed).toBe(1);
    expect(existsSync(join(testDir, '.claude/skills/magic-data-loading'))).toBe(false);
    expect(existsSync(join(testDir, '.claude/skills/magic-data-profiling'))).toBe(true);
  });
});

describe('removeCommands', () => {
  it('removes previously copied commands', async () => {
    const claude = getToolByValue('claude')!;
    const copied = await copyCommands(testDir, claude, REPO_ROOT);
    if (copied > 0) {
      const removed = await removeCommands(testDir, claude);
      expect(removed).toBeGreaterThan(0);
    }
  });
});

describe('config read/write', () => {
  it('returns null for missing config', async () => {
    const config = await readConfig(testDir);
    expect(config).toBeNull();
  });

  it('roundtrips config with suites and skills', async () => {
    const config = {
      version: '0.1.0',
      tools: ['claude', 'cursor'],
      suites: ['data'],
      skills: ['magic-data-loading', 'magic-data-profiling'],
      installedAt: '2026-01-01T00:00:00.000Z',
      updatedAt: '2026-01-01T00:00:00.000Z',
    };
    await writeConfig(testDir, config);
    const read = await readConfig(testDir);
    expect(read).toEqual(config);
  });
});

describe('detectTools', () => {
  it('detects tools by directory presence', async () => {
    await mkdir(join(testDir, '.claude'), { recursive: true });
    await mkdir(join(testDir, '.cursor'), { recursive: true });

    const detected = detectTools(testDir);
    expect(detected).toContain('claude');
    expect(detected).toContain('cursor');
    expect(detected).not.toContain('windsurf');
  });

  it('returns empty for clean directory', () => {
    const detected = detectTools(testDir);
    expect(detected).toEqual([]);
  });
});
