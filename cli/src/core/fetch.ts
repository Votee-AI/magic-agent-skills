import { execFileSync } from 'node:child_process';
import { existsSync } from 'node:fs';
import { mkdtemp, rm } from 'node:fs/promises';
import { join } from 'node:path';
import { tmpdir } from 'node:os';

const DEFAULT_REPO = 'Votee-AI/magic-agent-skills';
const DEFAULT_REF = 'main';

// owner/repo with the GitHub-permitted charset. Rejects shell metacharacters,
// spaces, and path traversal so the value can never escape an argv slot.
const REPO_RE = /^[\w.-]+\/[\w.-]+$/;
// git refs: word chars plus the few separators branches/tags use. No shell
// metacharacters, whitespace, or leading dash (which could be read as a flag).
const REF_RE = /^[\w][\w./-]*$/;

function validateRepo(repo: string): string {
  if (!REPO_RE.test(repo)) {
    throw new Error(
      `Invalid repo "${repo}". Expected "owner/name" with only letters, ` +
        `digits, ".", "_", or "-".`,
    );
  }
  return repo;
}

function validateRef(ref: string): string {
  if (!REF_RE.test(ref)) {
    throw new Error(
      `Invalid ref "${ref}". Expected a branch/tag name with only letters, ` +
        `digits, ".", "_", "/", or "-".`,
    );
  }
  return ref;
}

export async function fetchFromGitHub(
  repo?: string,
  ref: string = DEFAULT_REF,
): Promise<string> {
  // Validate BEFORE any process spawn. resolvedRepo/ref are never interpolated
  // into a shell string — they are passed as discrete argv entries below.
  const resolvedRepo = validateRepo(repo ?? process.env.MAGIC_REPO ?? DEFAULT_REPO);
  const resolvedRef = validateRef(ref);
  const tmpDir = await mkdtemp(join(tmpdir(), 'magic-skills-'));

  // Try tarball first (fast, works for public repos). Do curl and tar as two
  // separate steps so a curl failure isn't masked by a successful tar over an
  // empty/partial stream (the old `curl | tar` swallowed pipefail).
  const tarballUrl = `https://github.com/${resolvedRepo}/archive/refs/heads/${resolvedRef}.tar.gz`;
  const tarballPath = join(tmpDir, 'archive.tar.gz');
  try {
    execFileSync('curl', ['-sfL', '-o', tarballPath, tarballUrl], {
      stdio: 'pipe',
      timeout: 60000,
    });
    execFileSync(
      'tar',
      ['xz', '-f', tarballPath, '-C', tmpDir, '--strip-components=1'],
      { stdio: 'pipe', timeout: 60000 },
    );
    await rm(tarballPath, { force: true });
    if (existsSync(join(tmpDir, 'skills'))) {
      return tmpDir;
    }
  } catch {
    // Tarball failed — try git clone fallback
  }

  // Fallback: git clone --depth 1 (works for private repos with SSH/HTTPS access)
  try {
    await rm(tmpDir, { recursive: true, force: true });
    execFileSync(
      'git',
      [
        'clone',
        '--depth',
        '1',
        '--branch',
        resolvedRef,
        `https://github.com/${resolvedRepo}.git`,
        tmpDir,
      ],
      { stdio: 'pipe', timeout: 120000 },
    );
    return tmpDir;
  } catch {
    // Try SSH as last resort
  }

  try {
    await rm(tmpDir, { recursive: true, force: true });
    execFileSync(
      'git',
      [
        'clone',
        '--depth',
        '1',
        '--branch',
        resolvedRef,
        `git@github.com:${resolvedRepo}.git`,
        tmpDir,
      ],
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
