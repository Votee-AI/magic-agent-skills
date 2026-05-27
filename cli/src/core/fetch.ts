import { execSync } from 'node:child_process';
import { existsSync } from 'node:fs';
import { mkdtemp, rm } from 'node:fs/promises';
import { join } from 'node:path';
import { tmpdir } from 'node:os';

const DEFAULT_REPO = 'Votee-AI/magic-agent-skills';
const DEFAULT_REF = 'main';

export async function fetchFromGitHub(
  repo?: string,
  ref: string = DEFAULT_REF,
): Promise<string> {
  const resolvedRepo = repo ?? process.env.MAGIC_REPO ?? DEFAULT_REPO;
  const tmpDir = await mkdtemp(join(tmpdir(), 'magic-skills-'));

  // Try tarball first (fast, works for public repos)
  const tarballUrl = `https://github.com/${resolvedRepo}/archive/refs/heads/${ref}.tar.gz`;
  try {
    execSync(`curl -sfL "${tarballUrl}" | tar xz -C "${tmpDir}" --strip-components=1`, {
      stdio: 'pipe',
      timeout: 60000,
    });
    if (existsSync(join(tmpDir, 'skills'))) {
      return tmpDir;
    }
  } catch {
    // Tarball failed — try git clone fallback
  }

  // Fallback: git clone --depth 1 (works for private repos with SSH/HTTPS access)
  try {
    await rm(tmpDir, { recursive: true, force: true });
    execSync(
      `git clone --depth 1 --branch "${ref}" "https://github.com/${resolvedRepo}.git" "${tmpDir}"`,
      { stdio: 'pipe', timeout: 120000 },
    );
    return tmpDir;
  } catch {
    // Try SSH as last resort
  }

  try {
    await rm(tmpDir, { recursive: true, force: true });
    execSync(
      `git clone --depth 1 --branch "${ref}" "git@github.com:${resolvedRepo}.git" "${tmpDir}"`,
      { stdio: 'pipe', timeout: 120000 },
    );
    return tmpDir;
  } catch {
    await rm(tmpDir, { recursive: true, force: true });
    throw new Error(
      `Failed to fetch skills from ${resolvedRepo}.\n` +
      `Tried: tarball, HTTPS clone, SSH clone.\n` +
      `Override the repo with MAGIC_REPO=owner/repo environment variable.`,
    );
  }
}

export async function cleanupFetchDir(dir: string): Promise<void> {
  await rm(dir, { recursive: true, force: true });
}
