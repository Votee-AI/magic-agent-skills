import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { existsSync } from 'node:fs';
import { mkdtemp, rm, writeFile, readFile } from 'node:fs/promises';
import { join, resolve } from 'node:path';
import { tmpdir } from 'node:os';
import { fileURLToPath } from 'node:url';

const REPO_ROOT = resolve(fileURLToPath(import.meta.url), '..', '..', '..');

// --- Mocks -----------------------------------------------------------------

// fetchFromGitHub returns a sourceDir; point it at the real repo root which
// already has skills/ and commands/. cleanupFetchDir must NOT delete it.
vi.mock('../src/core/fetch.js', () => ({
  fetchFromGitHub: vi.fn(async () => REPO_ROOT),
  cleanupFetchDir: vi.fn(async () => {}),
}));

// Drive the prompts deterministically. Each test queues answers.
// We mock the custom prompts module (used by init's interactive flow) AND
// the @inquirer/prompts module (used by runPrompt / runConfirm fallback paths).
const selectMock = vi.fn();
const checkboxMock = vi.fn();

// BackSignal must be hoisted so the vi.mock factory (which is itself hoisted)
// can reference it, AND so test bodies can construct instances of the same class
// that init.ts will receive via its mocked import.
const { BackSignal, ExitPromptError } = await vi.hoisted(async () => {
  class BackSignal extends Error {
    constructor() {
      super('back');
      this.name = 'BackSignal';
    }
  }
  class ExitPromptError extends Error {
    constructor(message = 'User force closed the prompt with SIGINT') {
      super(message);
      this.name = 'ExitPromptError';
    }
  }
  return { BackSignal, ExitPromptError };
});

vi.mock('../src/core/prompts.js', () => ({
  customSelect: (...args: unknown[]) => selectMock(...args),
  customCheckbox: (...args: unknown[]) => checkboxMock(...args),
  BackSignal,
}));

vi.mock('@inquirer/prompts', () => ({
  select: (...args: unknown[]) => selectMock(...args),
  Separator: class {
    separator = '──';
    type = 'separator';
  },
}));

import { init } from '../src/commands/init.js';
import { configPath, readConfig } from '../src/core/copy.js';

let testDir: string;
let origCwd: string;
let origIsTTY: boolean | undefined;

beforeEach(async () => {
  testDir = await mkdtemp(join(tmpdir(), 'magic-init-test-'));
  origCwd = process.cwd();
  process.chdir(testDir);
  origIsTTY = process.stdin.isTTY;
  // Force interactive path so the prompt mocks are exercised.
  Object.defineProperty(process.stdin, 'isTTY', { value: true, configurable: true });
  selectMock.mockReset();
  checkboxMock.mockReset();
  process.exitCode = undefined;
});

afterEach(async () => {
  process.chdir(origCwd);
  Object.defineProperty(process.stdin, 'isTTY', {
    value: origIsTTY,
    configurable: true,
  });
  if (existsSync(testDir)) await rm(testDir, { recursive: true, force: true });
  process.exitCode = undefined;
});

/** Queue select() return values in call order. */
function queueSelect(...values: unknown[]): void {
  for (const v of values) {
    if (v instanceof Error) selectMock.mockImplementationOnce(() => Promise.reject(v));
    else selectMock.mockResolvedValueOnce(v);
  }
}

describe('init — interactive happy path (data suite, detected tool)', () => {
  it('installs the data suite and writes config', async () => {
    // selection-mode → data suite; tools step (no detected tools → checkbox);
    // confirm → yes.
    queueSelect('suite:data', 'yes');
    checkboxMock.mockResolvedValueOnce(['claude']); // tool checkbox

    await init({});

    expect(existsSync(configPath(testDir))).toBe(true);
    const cfg = await readConfig(testDir);
    expect(cfg!.suites).toEqual(['data']);
    expect(cfg!.tools).toEqual(['claude']);
    expect(cfg!.skills.length).toBeGreaterThan(0);
    expect(existsSync(join(testDir, '.claude/commands/data'))).toBe(true);
  });
});

describe('init — back navigation', () => {
  it('steps back from the tools step to selection-mode, then forward again', async () => {
    // 1) selection-mode → suite:data
    // 2) tools checkbox REJECTS with BackSignal (the real back path — the
    //    custom checkbox throws BackSignal on ESC, it never resolves a sentinel)
    //    → runInteractive's catch maps it to 'back' → step back to selection-mode
    // 3) selection-mode → all
    // 4) tools checkbox → claude
    // 5) confirm → yes
    queueSelect('suite:data');
    checkboxMock.mockImplementationOnce(() => Promise.reject(new BackSignal())); // BackSignal from tools step
    queueSelect('all');
    checkboxMock.mockResolvedValueOnce(['claude']);
    queueSelect('yes');

    await init({});

    const cfg = await readConfig(testDir);
    expect(cfg!.tools).toEqual(['claude']);
    // "all" selection installs both suites.
    expect(cfg!.suites.length).toBeGreaterThanOrEqual(2);
  });

  it('exits cleanly when ESC is pressed on the first step (BackSignal, no config written)', async () => {
    // ESC on selection-mode (first step) → BackSignal → exits cleanly, returns null.
    queueSelect(new BackSignal());

    await init({});

    expect(existsSync(configPath(testDir))).toBe(false);
    // Clean exit — not an error code.
    expect(process.exitCode).toBeUndefined();
  });
});

describe('init — --dry-run', () => {
  it('writes nothing', async () => {
    await init({ suites: 'data', tools: 'claude', dryRun: true });
    expect(existsSync(configPath(testDir))).toBe(false);
    expect(existsSync(join(testDir, '.claude/skills'))).toBe(false);
  });
});

describe('init — --yes / non-interactive', () => {
  it('accepts defaults without prompting', async () => {
    await init({ yes: true, tools: 'claude' });
    expect(selectMock).not.toHaveBeenCalled();
    expect(checkboxMock).not.toHaveBeenCalled();
    const cfg = await readConfig(testDir);
    expect(cfg!.tools).toEqual(['claude']);
  });
});

describe('init — corrupt config', () => {
  it('emits a friendly error and sets a failing exit code', async () => {
    await writeFile(configPath(testDir), '{ broken json', 'utf-8');
    const errSpy = vi.spyOn(console, 'log').mockImplementation(() => {});

    await init({});

    expect(process.exitCode).toBe(1);
    const printed = errSpy.mock.calls.flat().join('\n');
    expect(printed).toMatch(/init --force/);
    errSpy.mockRestore();
    // No prompts should have run.
    expect(selectMock).not.toHaveBeenCalled();
  });
});

describe('init — reinstall vs add on an existing install', () => {
  it('add mode merges into the existing config', async () => {
    // Seed an existing install (data suite, claude).
    await init({ suites: 'data', tools: 'claude' });
    expect(existsSync(configPath(testDir))).toBe(true);

    // Re-run interactively: choose "add" (action prompt), then linguistic
    // suite. The seed left `.claude`, so tools-step prompts "use detected?" —
    // answer 'no' and pick both tools via the checkbox, then confirm 'yes'.
    queueSelect('add', 'suite:linguistic', 'no', 'yes');
    checkboxMock.mockResolvedValueOnce(['claude', 'cursor']);

    await init({});

    const cfg = await readConfig(testDir);
    expect(cfg!.suites).toContain('data');
    expect(cfg!.suites).toContain('linguistic');
    expect(cfg!.tools).toContain('claude');
    expect(cfg!.tools).toContain('cursor');
  });
});

describe('init — Ctrl-C fallback path (ExitPromptError)', () => {
  it('ExitPromptError rejection sets exit code 130 and writes no config', async () => {
    // NOTE on the real mechanism (verified in a live tmux PTY, not just here):
    // on a real raw-mode TTY the Ctrl-C 0x03 byte IS delivered to useKeypress as
    // a keypress {name:'c', ctrl:true}, so the guard in prompts.ts calls
    // process.exit(130) synchronously and this init catch is never reached.
    // This test covers the *fallback* path only — a non-TTY / piped context
    // where @inquirer/core's readline SIGINT handler rejects the prompt with
    // ExitPromptError instead. There, init's catch sets process.exitCode = 130.
    // (On a real TTY, relying on this rejection path alone fails: signal-exit
    // re-raises SIGINT and the process dies by signal mid-cleanup, discarding
    // process.exitCode — that was the original "exit 0" bug, fixed by the
    // synchronous keypress guard.)
    selectMock.mockRejectedValueOnce(new ExitPromptError());

    await init({});

    expect(process.exitCode).toBe(130);
    expect(existsSync(configPath(testDir))).toBe(false);
  });
});
