import { describe, it, expect } from 'vitest';
import {
  markdownAdapter,
  tomlAdapter,
  promptAdapter,
  getAdapter,
} from '../src/core/adapters.js';

const SAMPLE_COMMAND = `<!-- Natural Language Triggers: "explore this data", "investigate" -->

Enter data explore mode — an interactive thinking partner for investigating data.

Read the magic-data-exploration SKILL.md and follow its stance and instructions.

$ARGUMENTS
`;

describe('markdownAdapter', () => {
  it('passes through unchanged', () => {
    const result = markdownAdapter.adapt('explore.md', SAMPLE_COMMAND);
    expect(result.filename).toBe('explore.md');
    expect(result.content).toBe(SAMPLE_COMMAND);
  });
});

describe('tomlAdapter', () => {
  it('converts to TOML format', () => {
    const result = tomlAdapter.adapt('explore.md', SAMPLE_COMMAND);
    expect(result.filename).toBe('magic-explore.toml');
    expect(result.content).toContain('[command]');
    expect(result.content).toContain('name = "magic-explore"');
    expect(result.content).toContain('[command.prompt]');
    expect(result.content).toContain('text = """');
  });

  it('strips trigger comments from body', () => {
    const result = tomlAdapter.adapt('explore.md', SAMPLE_COMMAND);
    expect(result.content).not.toContain('Natural Language Triggers');
    expect(result.content).toContain('interactive thinking partner');
  });
});

describe('promptAdapter', () => {
  it('wraps in prompt format', () => {
    const result = promptAdapter.adapt('explore.md', SAMPLE_COMMAND);
    expect(result.filename).toBe('magic-explore.prompt.md');
    expect(result.content).toContain('---');
    expect(result.content).toContain('mode: agent');
    expect(result.content).toContain('description:');
  });

  it('strips trigger comments from body', () => {
    const result = promptAdapter.adapt('explore.md', SAMPLE_COMMAND);
    expect(result.content).not.toContain('Natural Language Triggers');
    expect(result.content).toContain('interactive thinking partner');
  });
});

describe('getAdapter', () => {
  it('returns correct adapter for each format', () => {
    expect(getAdapter('md')).toBe(markdownAdapter);
    expect(getAdapter('toml')).toBe(tomlAdapter);
    expect(getAdapter('prompt')).toBe(promptAdapter);
  });

  it('returns null for null/unknown', () => {
    expect(getAdapter(null)).toBeNull();
    expect(getAdapter('unknown')).toBeNull();
  });
});
