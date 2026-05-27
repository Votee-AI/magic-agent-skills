import { describe, it, expect } from 'vitest';
import {
  MAGIC_TOOLS,
  SKILL_DIRS,
  COMMAND_FILES,
  getToolByValue,
} from '../src/core/config.js';

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
    expect(claude!.commandsDir).toBe('.claude/commands/data-agent');
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

  it('includes data-agent and linguistic skills', () => {
    const dataSkills = SKILL_DIRS.filter((d) => d.startsWith('magic-'));
    const linguisticSkills = SKILL_DIRS.filter((d) => d.startsWith('linguistic-'));
    expect(dataSkills.length).toBe(12);
    expect(linguisticSkills.length).toBe(18);
  });
});

describe('COMMAND_FILES', () => {
  it('has data-agent and linguistic groups', () => {
    expect(COMMAND_FILES).toHaveProperty('data-agent');
    expect(COMMAND_FILES).toHaveProperty('linguistic');
  });

  it('data-agent has 13 commands', () => {
    expect(COMMAND_FILES['data-agent'].length).toBe(13);
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
