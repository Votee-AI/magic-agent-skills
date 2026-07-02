import { describe, it, expect } from 'vitest';
import {
  MAGIC_TOOLS,
  SKILL_DIRS,
  COMMAND_FILES,
  getToolByValue,
} from '../src/core/config.js';
import { suiteForDir } from '../src/core/suites.js';

describe('MAGIC_TOOLS registry', () => {
  it('has 30 tools', () => {
    expect(MAGIC_TOOLS.length).toBe(30);
  });

  it('has unique values', () => {
    const values = MAGIC_TOOLS.map((t) => t.value);
    expect(new Set(values).size).toBe(values.length);
  });

  it('includes core tools', () => {
    const values = MAGIC_TOOLS.map((t) => t.value);
    expect(values).toContain('claude');
    expect(values).toContain('cursor');
    expect(values).toContain('windsurf');
    expect(values).toContain('gemini');
    expect(values).toContain('codex');
    expect(values).toContain('github-copilot');
  });

  it('Claude has correct config', () => {
    const claude = getToolByValue('claude');
    expect(claude).toBeDefined();
    expect(claude!.skillsDir).toBe('.claude');
    // commandsDir is the literal BASE; copyCommands appends the group leaf.
    expect(claude!.commandsDir).toBe('.claude/commands');
    expect(claude!.commandFormat).toBe('md');
  });

  it('Gemini uses toml format', () => {
    const gemini = getToolByValue('gemini');
    expect(gemini).toBeDefined();
    expect(gemini!.commandFormat).toBe('toml');
  });

  it('GitHub Copilot uses prompt format', () => {
    const copilot = getToolByValue('github-copilot');
    expect(copilot).toBeDefined();
    expect(copilot!.commandFormat).toBe('prompt');
  });

  it('skills-only tools have null commandsDir', () => {
    const codex = getToolByValue('codex');
    expect(codex).toBeDefined();
    expect(codex!.commandsDir).toBeNull();
    expect(codex!.commandFormat).toBeNull();
  });

  it('AGENTS.md has undefined skillsDir', () => {
    const agents = getToolByValue('agents');
    expect(agents).toBeDefined();
    expect(agents!.skillsDir).toBeUndefined();
  });
});

describe('SKILL_DIRS', () => {
  it('has 30 skills', () => {
    expect(SKILL_DIRS.length).toBe(30);
  });

  it('includes data and linguistic skills', () => {
    // Use the ordered suite logic: magic-linguistic-* is matched before the
    // data magic-* rule, so the two suites partition cleanly (12 data, 18 ling).
    const dataSkills = SKILL_DIRS.filter((d) => suiteForDir(d)?.key === 'data');
    const linguisticSkills = SKILL_DIRS.filter((d) => suiteForDir(d)?.key === 'linguistic');
    expect(dataSkills.length).toBe(12);
    expect(linguisticSkills.length).toBe(18);
  });
});

describe('InstalledConfig interface', () => {
  it('includes suites and skills fields', () => {
    const config: import('../src/core/config.js').InstalledConfig = {
      version: '0.1.0',
      tools: ['claude'],
      suites: ['data'],
      skills: ['magic-data-loading'],
      installedAt: '2026-01-01T00:00:00.000Z',
      updatedAt: '2026-01-01T00:00:00.000Z',
    };
    expect(config.suites).toEqual(['data']);
    expect(config.skills).toEqual(['magic-data-loading']);
  });
});

describe('COMMAND_FILES', () => {
  it('has data and linguistic groups', () => {
    expect(COMMAND_FILES).toHaveProperty('data');
    expect(COMMAND_FILES).toHaveProperty('linguistic');
  });

  it('data has 13 commands', () => {
    expect(COMMAND_FILES['data'].length).toBe(13);
  });

  it('linguistic has 10 commands', () => {
    expect(COMMAND_FILES.linguistic.length).toBe(10);
  });

  it('all files end with .md', () => {
    for (const files of Object.values(COMMAND_FILES)) {
      for (const file of files) {
        expect(file).toMatch(/\.md$/);
      }
    }
  });
});
