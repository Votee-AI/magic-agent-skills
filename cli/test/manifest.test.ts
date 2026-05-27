import { describe, it, expect, beforeEach, afterEach } from 'vitest';
import { mkdtemp, mkdir, rm } from 'node:fs/promises';
import { join } from 'node:path';
import { tmpdir } from 'node:os';
import { existsSync } from 'node:fs';
import { discoverManifest, getSuiteConfigs } from '../src/core/manifest.js';

let testDir: string;

beforeEach(async () => {
  testDir = await mkdtemp(join(tmpdir(), 'magic-manifest-test-'));
});

afterEach(async () => {
  if (existsSync(testDir)) {
    await rm(testDir, { recursive: true, force: true });
  }
});

async function makeSkillDirs(skillsDir: string, names: string[]): Promise<void> {
  await mkdir(skillsDir, { recursive: true });
  for (const name of names) {
    await mkdir(join(skillsDir, name), { recursive: true });
  }
}

describe('discoverManifest', () => {
  it('discovers magic-* and linguistic-* dirs separately', async () => {
    const skillsDir = join(testDir, 'skills');
    await makeSkillDirs(skillsDir, [
      'magic-data-cleaning',
      'magic-data-exploration',
      'magic-data-loading',
      'magic-data-profiling',
      'linguistic-grammar',
      'linguistic-translation',
    ]);

    const manifest = discoverManifest(skillsDir);
    expect(manifest.suites['data-agent']?.skills).toHaveLength(4);
    expect(manifest.suites['linguistic']?.skills).toHaveLength(2);
  });

  it('excludes dirs starting with _', async () => {
    const skillsDir = join(testDir, 'skills');
    await makeSkillDirs(skillsDir, [
      'magic-data-loading',
      '_hidden-dir',
    ]);

    const manifest = discoverManifest(skillsDir);
    expect(manifest.suites['data-agent']?.skills).toEqual(['magic-data-loading']);
    expect(manifest.suites['linguistic']?.skills).toEqual([]);
  });

  it('returns sorted skill lists', async () => {
    const skillsDir = join(testDir, 'skills');
    await makeSkillDirs(skillsDir, [
      'magic-data-profiling',
      'magic-data-cleaning',
      'magic-data-loading',
    ]);

    const manifest = discoverManifest(skillsDir);
    expect(manifest.suites['data-agent']?.skills).toEqual([
      'magic-data-cleaning',
      'magic-data-loading',
      'magic-data-profiling',
    ]);
  });

  it('returns empty arrays when no matching dirs', async () => {
    const skillsDir = join(testDir, 'skills');
    await mkdir(skillsDir, { recursive: true });

    const manifest = discoverManifest(skillsDir);
    expect(manifest.suites['data-agent']?.skills).toEqual([]);
    expect(manifest.suites['linguistic']?.skills).toEqual([]);
  });
});

describe('getSuiteConfigs', () => {
  it('returns data and linguistic suite configs', async () => {
    const skillsDir = join(testDir, 'skills');
    await makeSkillDirs(skillsDir, [
      'magic-data-cleaning',
      'magic-data-exploration',
      'magic-data-loading',
      'magic-data-profiling',
      'linguistic-grammar',
      'linguistic-translation',
    ]);

    const configs = getSuiteConfigs(skillsDir, '0.1.0');
    expect(configs).toHaveLength(2);

    const data = configs.find((c) => c.name === 'data-agent');
    expect(data).toBeDefined();
    expect(data!.displayName).toBe('Data Agent');
    expect(data!.skills).toHaveLength(4);
    expect(data!.commandsDir).toBe('commands/data-agent');

    const ling = configs.find((c) => c.name === 'linguistic');
    expect(ling).toBeDefined();
    expect(ling!.displayName).toBe('Linguistic');
    expect(ling!.skills).toHaveLength(2);
    expect(ling!.commandsDir).toBe('commands/linguistic');
  });

  it('uses the provided version', async () => {
    const skillsDir = join(testDir, 'skills');
    await mkdir(skillsDir, { recursive: true });

    const configs = getSuiteConfigs(skillsDir, '1.2.3');
    expect(configs[0]!.version).toBe('1.2.3');
    expect(configs[1]!.version).toBe('1.2.3');
  });

  it('returns empty skills array when no matching dirs', async () => {
    const skillsDir = join(testDir, 'skills');
    await makeSkillDirs(skillsDir, ['magic-data-loading']);

    const configs = getSuiteConfigs(skillsDir, '0.1.0');
    const ling = configs.find((c) => c.name === 'linguistic');
    expect(ling!.skills).toEqual([]);
  });
});
