import { readFileSync } from 'node:fs';
import { join } from 'node:path';
import { getPackageRoot } from './config.js';

export interface SuiteConfig {
  name: string;
  displayName: string;
  version: string;
  skills: string[];
  commandsDir: string | null;
}

export interface ManifestConfig {
  suites: Record<string, {
    skills: string[];
  }>;
}

export function loadManifest(): ManifestConfig {
  const manifestPath = join(getPackageRoot(), 'skills', 'manifest.json');
  try {
    const raw = readFileSync(manifestPath, 'utf8');
    return JSON.parse(raw) as ManifestConfig;
  } catch (err) {
    throw new Error(
      `Failed to load skills manifest at ${manifestPath}. ` +
      `Run "npm run build" or "bash scripts/copy-skills.sh" first.`,
    );
  }
}

export function getSuiteConfigs(): SuiteConfig[] {
  const manifest = loadManifest();
  const pkg = JSON.parse(
    readFileSync(join(getPackageRoot(), 'package.json'), 'utf8'),
  ) as { version: string };

  return [
    {
      name: 'data',
      displayName: 'Data Science',
      version: pkg.version,
      skills: manifest.suites['data']?.skills ?? [],
      commandsDir: 'commands/data-agent',
    },
    {
      name: 'linguistic',
      displayName: 'Linguistic',
      version: pkg.version,
      skills: manifest.suites['linguistic']?.skills ?? [],
      commandsDir: 'commands/linguistic',
    },
  ];
}
