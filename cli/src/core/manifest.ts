import { readdirSync, statSync } from 'node:fs';
import { join } from 'node:path';

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
 * Discovers suites by scanning a skills directory for magic-* and linguistic-* subdirs.
 * Works with any directory — fetched from GitHub, local repo, or bundled package.
 */
export function discoverManifest(skillsDir: string): ManifestConfig {
  const dirs = readdirSync(skillsDir).filter(d =>
    statSync(join(skillsDir, d)).isDirectory() && !d.startsWith('_')
  );
  return {
    suites: {
      'data-agent': { skills: dirs.filter(d => d.startsWith('magic-')).sort() },
      linguistic: { skills: dirs.filter(d => d.startsWith('linguistic-')).sort() },
    },
  };
}

/**
 * Builds suite configs from a discovered manifest.
 */
export function getSuiteConfigs(skillsDir: string, version: string): SuiteConfig[] {
  const manifest = discoverManifest(skillsDir);
  return [
    {
      name: 'data-agent',
      displayName: 'Data Agent',
      version,
      skills: manifest.suites['data-agent']?.skills ?? [],
      commandsDir: 'commands/data-agent',
    },
    {
      name: 'linguistic',
      displayName: 'Linguistic',
      version,
      skills: manifest.suites['linguistic']?.skills ?? [],
      commandsDir: 'commands/linguistic',
    },
  ];
}
