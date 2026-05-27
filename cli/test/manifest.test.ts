import { describe, it, expect, vi, beforeEach } from 'vitest';

// Mock the fs module before importing manifest
vi.mock('node:fs', () => ({
  readFileSync: vi.fn(),
}));

import { readFileSync } from 'node:fs';
import { loadManifest, getSuiteConfigs } from '../src/core/manifest.js';

const mockReadFileSync = readFileSync as ReturnType<typeof vi.fn>;

const SAMPLE_MANIFEST = {
  suites: {
    data: {
      skills: [
        'magic-data-cleaning',
        'magic-data-exploration',
        'magic-data-loading',
        'magic-data-profiling',
      ],
    },
    linguistic: {
      skills: [
        'linguistic-grammar',
        'linguistic-translation',
      ],
    },
  },
};

const SAMPLE_PKG = { version: '0.1.0' };

beforeEach(() => {
  vi.resetAllMocks();
});

describe('loadManifest', () => {
  it('parses manifest.json from skills directory', () => {
    mockReadFileSync.mockReturnValueOnce(JSON.stringify(SAMPLE_MANIFEST));
    const manifest = loadManifest();
    expect(manifest.suites['data']?.skills).toHaveLength(4);
    expect(manifest.suites['linguistic']?.skills).toHaveLength(2);
  });

  it('throws descriptive error when manifest missing', () => {
    mockReadFileSync.mockImplementationOnce(() => {
      throw new Error('ENOENT');
    });
    expect(() => loadManifest()).toThrow(
      /Failed to load skills manifest/,
    );
    expect(() => loadManifest()).toThrow(/copy-skills\.sh/);
  });
});

describe('getSuiteConfigs', () => {
  it('returns data and linguistic suite configs', () => {
    // manifest.json read, then package.json read
    mockReadFileSync
      .mockReturnValueOnce(JSON.stringify(SAMPLE_MANIFEST))
      .mockReturnValueOnce(JSON.stringify(SAMPLE_PKG));

    const configs = getSuiteConfigs();
    expect(configs).toHaveLength(2);

    const data = configs.find((c) => c.name === 'data');
    expect(data).toBeDefined();
    expect(data!.displayName).toBe('Data Science');
    expect(data!.skills).toHaveLength(4);
    expect(data!.commandsDir).toBe('commands/data-agent');

    const ling = configs.find((c) => c.name === 'linguistic');
    expect(ling).toBeDefined();
    expect(ling!.displayName).toBe('Linguistic');
    expect(ling!.skills).toHaveLength(2);
    expect(ling!.commandsDir).toBe('commands/linguistic');
  });

  it('uses version from package.json', () => {
    mockReadFileSync
      .mockReturnValueOnce(JSON.stringify(SAMPLE_MANIFEST))
      .mockReturnValueOnce(JSON.stringify({ version: '1.2.3' }));

    const configs = getSuiteConfigs();
    expect(configs[0]!.version).toBe('1.2.3');
    expect(configs[1]!.version).toBe('1.2.3');
  });

  it('returns empty skills array when suite missing from manifest', () => {
    const partialManifest = { suites: { data: { skills: ['magic-data-loading'] } } };
    mockReadFileSync
      .mockReturnValueOnce(JSON.stringify(partialManifest))
      .mockReturnValueOnce(JSON.stringify(SAMPLE_PKG));

    const configs = getSuiteConfigs();
    const ling = configs.find((c) => c.name === 'linguistic');
    expect(ling!.skills).toEqual([]);
  });
});
