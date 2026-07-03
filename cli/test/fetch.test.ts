import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { existsSync, mkdirSync } from 'node:fs';
import { rm } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { readdirSync } from 'node:fs';
import { join } from 'node:path';

// Mock child_process so no real network/git is invoked. We capture the argv
// arrays passed to execFileSync to prove user-controlled values are never
// interpolated into a shell string.
const execFileSyncMock = vi.fn();
vi.mock('node:child_process', () => ({
  execFileSync: (...args: unknown[]) => execFileSyncMock(...args),
}));

import { fetchFromGitHub } from '../src/core/fetch.js';

function cleanupTmpDirs(): void {
  // Best-effort cleanup of any magic-skills-* tmp dirs created by mkdtemp.
  for (const entry of readdirSync(tmpdir())) {
    if (entry.startsWith('magic-skills-')) {
      void rm(join(tmpdir(), entry), { recursive: true, force: true });
    }
  }
}

beforeEach(() => {
  execFileSyncMock.mockReset();
  delete process.env.MAGIC_REPO;
});

afterEach(() => {
  cleanupTmpDirs();
  delete process.env.MAGIC_REPO;
});

describe('fetchFromGitHub — input validation (P2: no shell injection)', () => {
  it('rejects a MAGIC_REPO injection string before spawning anything', async () => {
    process.env.MAGIC_REPO = 'owner/repo; rm -rf /';
    await expect(fetchFromGitHub()).rejects.toThrow(/Invalid repo/);
    expect(execFileSyncMock).not.toHaveBeenCalled();
  });

  it('rejects a repo with backtick/command-substitution metacharacters', async () => {
    await expect(fetchFromGitHub('owner/$(whoami)')).rejects.toThrow(/Invalid repo/);
    expect(execFileSyncMock).not.toHaveBeenCalled();
  });

  it('rejects a ref with shell metacharacters', async () => {
    await expect(
      fetchFromGitHub('owner/repo', 'main; echo pwned'),
    ).rejects.toThrow(/Invalid ref/);
    expect(execFileSyncMock).not.toHaveBeenCalled();
  });

  it('rejects a ref that starts with a dash (could be read as a flag)', async () => {
    await expect(fetchFromGitHub('owner/repo', '-x')).rejects.toThrow(/Invalid ref/);
    expect(execFileSyncMock).not.toHaveBeenCalled();
  });

  it('passes valid repo/ref as discrete argv entries, never a shell string', async () => {
    // Let the git-clone fallback "succeed" — recreate the clone target dir
    // (the real git would) so fetchFromGitHub returns an existing path. The
    // tarball branch falls through (no skills/), reaching git clone.
    execFileSyncMock.mockImplementation((cmd: string, argv: string[]) => {
      if (cmd === 'git' && argv.includes('clone')) {
        mkdirSync(argv[argv.length - 1]!, { recursive: true });
      }
      return Buffer.from('');
    });
    const dir = await fetchFromGitHub('My-Org.name/some_repo-1', 'release/v1.2.3');

    // Every spawn must use the execFileSync ARRAY form (no shell string), and
    // the repo/ref must appear as their own discrete argv entries.
    expect(execFileSyncMock).toHaveBeenCalled();
    const cmds = execFileSyncMock.mock.calls.map((c) => c[0]);
    expect(cmds).not.toContain('sh');
    expect(cmds).not.toContain('bash');
    for (const call of execFileSyncMock.mock.calls) {
      const argv = call[1];
      expect(Array.isArray(argv)).toBe(true);
      // No argv entry may smuggle a shell metacharacter.
      for (const arg of argv as string[]) {
        expect(arg).not.toMatch(/[;&|`$()]/);
      }
    }
    const gitClone = execFileSyncMock.mock.calls.find(
      (c) => c[0] === 'git' && (c[1] as string[]).includes('clone'),
    );
    expect(gitClone).toBeDefined();
    expect(gitClone![1]).toContain('release/v1.2.3');
    expect(existsSync(dir)).toBe(true);
    await rm(dir, { recursive: true, force: true });
  });
});

describe('fetchFromGitHub — failure surfaces a clear error', () => {
  it('throws a clear, actionable error when all fetch strategies fail', async () => {
    execFileSyncMock.mockImplementation(() => {
      throw new Error('network down');
    });
    await expect(fetchFromGitHub('owner/repo', 'main')).rejects.toThrow(
      /Failed to fetch skills from owner\/repo/,
    );
    await expect(fetchFromGitHub('owner/repo', 'main')).rejects.toThrow(
      /MAGIC_REPO=owner\/repo/,
    );
  });
});
