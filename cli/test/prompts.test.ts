/**
 * Real-keypress tests for customSelect and customCheckbox (S1–S6).
 *
 * We drive an actual ESC byte (0x1b) into the prompt via a PassThrough stream
 * flagged as a TTY, and a null output (WritableStream).  No real terminal needed.
 */
import { describe, it, expect, vi, afterEach } from 'vitest';
import { PassThrough, Writable } from 'node:stream';
import { BackSignal, customSelect, customCheckbox } from '../src/core/prompts.js';

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

/** Create a controllable stdin that @inquirer/core accepts. */
function makeTtyStream(): PassThrough {
  const stream = new PassThrough();
  // @inquirer/core checks input.isTTY / rl.input.isTTY
  (stream as unknown as { isTTY: boolean }).isTTY = true;
  return stream;
}

/** A writable that discards output (suppress inquirer rendering). */
function makeNullOutput(): Writable {
  return new Writable({ write(_chunk, _enc, cb) { cb(); } });
}

/**
 * Run a prompt function with controlled stdin/stdout.
 * Returns a Promise of the result (or rejects with whatever the prompt throws).
 */
function runPrompt<T>(
  promptFn: (context: { input: PassThrough; output: Writable }) => Promise<T>,
): { result: Promise<T>; stdin: PassThrough } {
  const stdin = makeTtyStream();
  const stdout = makeNullOutput();
  const result = promptFn({ input: stdin, output: stdout });
  return { result, stdin };
}

/** Send raw bytes to stdin after a short tick (to let prompt initialise). */
function sendAfterTick(stdin: PassThrough, bytes: Buffer, delayMs = 20): void {
  setTimeout(() => {
    stdin.push(bytes);
  }, delayMs);
}

// ESC = 0x1b (lone byte)
const ESC = Buffer.from([0x1b]);
// Up-arrow = ESC [ A
const UP_ARROW = Buffer.from([0x1b, 0x5b, 0x41]);
// Down-arrow = ESC [ B
const DOWN_ARROW = Buffer.from([0x1b, 0x5b, 0x42]);
// Enter = 0x0d
const ENTER = Buffer.from([0x0d]);
// Space = 0x20
const SPACE = Buffer.from([0x20]);

// ---------------------------------------------------------------------------
// S1 — ESC on a select step throws BackSignal
// ---------------------------------------------------------------------------
describe('S1 — customSelect: ESC throws BackSignal', () => {
  it('throws BackSignal when ESC is pressed', async () => {
    const { result, stdin } = runPrompt(({ input, output }) =>
      customSelect(
        {
          message: 'Pick one:',
          choices: [
            { name: 'Option A', value: 'a' },
            { name: 'Option B', value: 'b' },
          ],
        },
        { input, output },
      ),
    );

    sendAfterTick(stdin, ESC);

    await expect(result).rejects.toSatisfy(
      (err: unknown) => err instanceof BackSignal,
    );
  });
});

// ---------------------------------------------------------------------------
// S2 — ESC on a checkbox step throws BackSignal
// ---------------------------------------------------------------------------
describe('S2 — customCheckbox: ESC throws BackSignal', () => {
  it('throws BackSignal when ESC is pressed', async () => {
    const { result, stdin } = runPrompt(({ input, output }) =>
      customCheckbox(
        {
          message: 'Select skills:',
          choices: [
            { name: 'skill-a', value: 'skill-a', checked: false },
            { name: 'skill-b', value: 'skill-b', checked: false },
          ],
        },
        { input, output },
      ),
    );

    sendAfterTick(stdin, ESC);

    await expect(result).rejects.toSatisfy(
      (err: unknown) => err instanceof BackSignal,
    );
  });
});

// ---------------------------------------------------------------------------
// S4 — Arrow keys do NOT throw BackSignal; they move the cursor
// ---------------------------------------------------------------------------
describe('S4 — customSelect: arrow keys do not fire BackSignal', () => {
  it('Up/Down arrows move cursor and do not throw', async () => {
    const { result, stdin } = runPrompt(({ input, output }) =>
      customSelect(
        {
          message: 'Pick one:',
          choices: [
            { name: 'Option A', value: 'a' },
            { name: 'Option B', value: 'b' },
            { name: 'Option C', value: 'c' },
          ],
        },
        { input, output },
      ),
    );

    // Navigate down, then up, then confirm with Enter on first item ('a').
    sendAfterTick(stdin, DOWN_ARROW, 20);
    sendAfterTick(stdin, UP_ARROW, 40);
    sendAfterTick(stdin, ENTER, 60);

    const value = await result;
    // After down+up we should be back on 'a'
    expect(value).toBe('a');
  });
});

// ---------------------------------------------------------------------------
// S4 — Arrow keys on checkbox do NOT throw
// ---------------------------------------------------------------------------
describe('S4 — customCheckbox: arrow keys do not fire BackSignal', () => {
  it('Down then Enter submits the unchecked selection without throwing', async () => {
    const { result, stdin } = runPrompt(({ input, output }) =>
      customCheckbox(
        {
          message: 'Select:',
          choices: [
            { name: 'skill-a', value: 'skill-a', checked: false },
            { name: 'skill-b', value: 'skill-b', checked: false },
          ],
        },
        { input, output },
      ),
    );

    // Down, then Enter (no space — nothing checked).
    sendAfterTick(stdin, DOWN_ARROW, 20);
    sendAfterTick(stdin, ENTER, 40);

    const selected = await result;
    expect(Array.isArray(selected)).toBe(true);
    // Nothing was space-toggled so result is empty array.
    expect(selected).toEqual([]);
  });
});

// ---------------------------------------------------------------------------
// S6 — Checkbox renders a visible ← Back / ESC hint
// ---------------------------------------------------------------------------
describe('S6 — customCheckbox: visible back affordance in render', () => {
  it('captured output contains ESC or ← Back hint', async () => {
    const chunks: string[] = [];
    const captureOutput = new Writable({
      write(chunk: Buffer, _enc: string, cb: () => void) {
        chunks.push(chunk.toString());
        cb();
      },
    });

    const stdin = makeTtyStream();
    const promptPromise = customCheckbox(
      {
        message: 'Select skills:',
        choices: [
          { name: 'skill-a', value: 'skill-a', checked: false },
        ],
      },
      { input: stdin, output: captureOutput },
    );

    // Let the prompt render one frame, then send Enter to close.
    await new Promise((resolve) => setTimeout(resolve, 30));
    stdin.push(ENTER);

    await promptPromise.catch(() => {}); // may resolve or throw; we only care about output

    const rendered = chunks.join('');
    // Must contain some back affordance (ESC or ← Back)
    expect(rendered).toMatch(/ESC|← Back|esc/i);
  });
});

// ---------------------------------------------------------------------------
// S5 — Ctrl-C calls process.exit(130) in both prompts
// ---------------------------------------------------------------------------

// Ctrl-C = raw byte 0x03
const CTRL_C = Buffer.from([0x03]);

describe('S5 — customSelect: Ctrl-C exits with code 130', () => {
  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('calls process.exit(130) when Ctrl-C is pressed', async () => {
    const exitSpy = vi.spyOn(process, 'exit').mockImplementation((() => undefined) as never);

    // process.exit is mocked to a no-op, so rl.close() causes @inquirer/core to
    // throw ExitPromptError. Attach a catch handler immediately to avoid an
    // unhandled rejection.
    const { result, stdin } = runPrompt(({ input, output }) =>
      customSelect(
        {
          message: 'Pick one:',
          choices: [
            { name: 'Option A', value: 'a' },
            { name: 'Option B', value: 'b' },
          ],
        },
        { input, output },
      ),
    );
    result.catch(() => {});

    sendAfterTick(stdin, CTRL_C);

    // Wait long enough for the keypress to be processed
    await new Promise((resolve) => setTimeout(resolve, 60));

    expect(exitSpy).toHaveBeenCalledWith(130);
  });
});

describe('S5 — customCheckbox: Ctrl-C exits with code 130', () => {
  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('calls process.exit(130) when Ctrl-C is pressed', async () => {
    const exitSpy = vi.spyOn(process, 'exit').mockImplementation((() => undefined) as never);

    // process.exit is mocked to a no-op, so rl.close() causes @inquirer/core to
    // throw ExitPromptError. Attach a catch handler immediately to avoid an
    // unhandled rejection.
    const { result, stdin } = runPrompt(({ input, output }) =>
      customCheckbox(
        {
          message: 'Select skills:',
          choices: [
            { name: 'skill-a', value: 'skill-a', checked: false },
            { name: 'skill-b', value: 'skill-b', checked: false },
          ],
        },
        { input, output },
      ),
    );
    result.catch(() => {});

    sendAfterTick(stdin, CTRL_C);

    // Wait long enough for the keypress to be processed
    await new Promise((resolve) => setTimeout(resolve, 60));

    expect(exitSpy).toHaveBeenCalledWith(130);
  });
});

// ---------------------------------------------------------------------------
// S5 (mechanism) — the Ctrl-C byte is delivered to useKeypress as a keypress
// (name 'c', ctrl true), and the in-prompt guard exits 130 *synchronously* from
// that keypress. This is the path proven on a real raw-mode TTY (5/5 runs). The
// guard must NOT depend on the prompt rejecting with ExitPromptError: on a real
// terminal signal-exit re-raises SIGINT and the process would die by signal
// mid-cleanup, discarding process.exitCode (the original "exit 0" bug).
// ---------------------------------------------------------------------------
describe('S5 (mechanism) — Ctrl-C exits 130 from the keypress, not via resolve', () => {
  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('exits 130 and the prompt never resolves to a value', async () => {
    const exitCodes: Array<number | undefined> = [];
    vi.spyOn(process, 'exit').mockImplementation(((code?: number) => {
      exitCodes.push(code);
      return undefined as never;
    }) as never);

    let resolvedValue: unknown = Symbol('unresolved');
    const { result, stdin } = runPrompt(({ input, output }) =>
      customSelect(
        {
          message: 'Pick one:',
          choices: [
            { name: 'Option A', value: 'a' },
            { name: 'Option B', value: 'b' },
          ],
        },
        { input, output },
      ),
    );
    result.then((v) => { resolvedValue = v; }).catch(() => {});

    sendAfterTick(stdin, CTRL_C);
    await new Promise((resolve) => setTimeout(resolve, 60));

    // The guard fired with 130 ...
    expect(exitCodes).toContain(130);
    // ... and the prompt did not resolve to one of the choice values
    // (proving the exit short-circuits the normal done() path).
    expect(resolvedValue).not.toBe('a');
    expect(resolvedValue).not.toBe('b');
  });
});

// ---------------------------------------------------------------------------
// BackSignal is exported and instanceof works
// ---------------------------------------------------------------------------
describe('BackSignal export', () => {
  it('is an Error subclass with name BackSignal', () => {
    const sig = new BackSignal();
    expect(sig).toBeInstanceOf(Error);
    expect(sig.name).toBe('BackSignal');
    expect(sig).toBeInstanceOf(BackSignal);
  });
});
