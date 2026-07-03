import { readdirSync, statSync } from 'node:fs';
import { join } from 'node:path';
import { SUITES, suiteForDir } from './suites.js';

export interface SuiteConfig {
  name: string;
  displayName: string;
  version: string;
  skills: string[];
  commandsDir: string | null;
}

export interface ManifestConfig {
  suites: Record<string, { skills: string[] }>;
}

/**
 * Discovers suites by scanning a skills directory and bucketing each subdir into
 * the first matching suite (most-specific-first, see suites.ts).
 * Works with any directory — fetched from GitHub, local repo, or bundled package.
 */
export function discoverManifest(skillsDir: string): ManifestConfig {
  const dirs = readdirSync(skillsDir).filter(d =>
    statSync(join(skillsDir, d)).isDirectory() && !d.startsWith('_')
  );

  const suites: Record<string, { skills: string[] }> = {};
  for (const suite of SUITES) {
    suites[suite.key] = { skills: [] };
  }
  for (const d of dirs) {
    const suite = suiteForDir(d);
    if (suite) suites[suite.key]!.skills.push(d);
  }
  for (const key of Object.keys(suites)) {
    suites[key]!.skills.sort();
  }

  return { suites };
}

/**
 * Builds suite configs from a discovered manifest.
 */
export function getSuiteConfigs(skillsDir: string, version: string): SuiteConfig[] {
  const manifest = discoverManifest(skillsDir);
  return SUITES.map((suite) => ({
    name: suite.key,
    displayName: suite.displayName,
    version,
    skills: manifest.suites[suite.key]?.skills ?? [],
    commandsDir: `commands/${suite.commandGroup}`,
  }));
}
