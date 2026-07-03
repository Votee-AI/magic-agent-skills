/**
 * Custom prompt implementations via @inquirer/core createPrompt + useKeypress.
 *
 * Differences from stock @inquirer/prompts select/checkbox:
 *  - A lone ESC keypress (key.name === 'escape') throws BackSignal instead of
 *    being silently ignored. Arrow escape sequences (key.name === 'up'/'down')
 *    are NOT affected — only a bare ESC is treated as back.
 *  - customCheckbox renders a visible "ESC ← Back" hint in the help line.
 *
 * Implementation note on error propagation:
 *   Throwing inside useKeypress produces an uncaught exception because the
 *   keypress event fires outside @inquirer/core's render try/catch. Instead,
 *   we set a boolean state flag (`backRequested`) and throw BackSignal during
 *   the *render* phase, which IS wrapped by the cycle try/catch that calls
 *   reject(error) on the underlying Promise.
 */

import {
  createPrompt,
  useState,
  useKeypress,
  usePrefix,
  usePagination,
  useMemo,
  makeTheme,
  isEnterKey,
  isUpKey,
  isDownKey,
  isSpaceKey,
  Separator,
  type KeypressEvent,
} from '@inquirer/core';
import chalk from 'chalk';

// ---------------------------------------------------------------------------
// BackSignal
// ---------------------------------------------------------------------------

/** Thrown by custom prompts when the user presses ESC (go back one step). */
export class BackSignal extends Error {
  constructor() {
    super('back');
    this.name = 'BackSignal';
  }
}

// ---------------------------------------------------------------------------
// Shared helpers
// ---------------------------------------------------------------------------

const ACCENT = chalk.hex('#00BCD4');

function isEscapeKey(key: KeypressEvent): boolean {
  return key.name === 'escape';
}

function isSelectable<T extends { disabled?: boolean | string }>(
  item: T | Separator,
): item is T {
  return !Separator.isSeparator(item) && !(item as T).disabled;
}

/** ES2022-safe last-index search (Array.findLastIndex is ES2023+). */
function findLastIndex<T>(arr: T[], predicate: (item: T) => boolean): number {
  for (let i = arr.length - 1; i >= 0; i--) {
    if (predicate(arr[i]!)) return i;
  }
  return -1;
}

// ---------------------------------------------------------------------------
// customSelect
// ---------------------------------------------------------------------------

export interface SelectChoice<T> {
  name: string;
  value: T;
  disabled?: boolean | string;
}

export interface SelectConfig<T> {
  message: string;
  choices: Array<SelectChoice<T> | Separator>;
  pageSize?: number;
  loop?: boolean;
}

type NormalizedSelectItem<T> = { name: string; value: T; disabled?: boolean | string };

function normalizeSelectChoices<T>(
  choices: Array<SelectChoice<T> | Separator>,
): Array<NormalizedSelectItem<T> | Separator> {
  return choices.map((c) => {
    if (Separator.isSeparator(c)) return c;
    return { name: c.name, value: c.value, disabled: c.disabled };
  });
}

export const customSelect = createPrompt(
  <T>(config: SelectConfig<T>, done: (value: T) => void) => {
    const { pageSize = 7, loop = true } = config;

    const items = useMemo(
      () => normalizeSelectChoices(config.choices),
      [config.choices],
    );

    const bounds = useMemo(() => {
      const first = items.findIndex(isSelectable);
      const last = findLastIndex(items, isSelectable);
      return { first: first === -1 ? 0 : first, last: last === -1 ? 0 : last };
    }, [items]);

    const [active, setActive] = useState(bounds.first);
    const [status, setStatus] = useState<'idle' | 'done'>('idle');
    // Flag set in keypress handler; checked in render to throw BackSignal.
    const [backRequested, setBackRequested] = useState(false);
    const theme = makeTheme({}, undefined);
    const prefix = usePrefix({ status, theme });

    useKeypress((key: KeypressEvent, rl) => {
      if (key.ctrl === true && key.name === 'c') {
        // Ctrl-C = hard quit (exit 130). On a raw-mode TTY the 0x03 byte is
        // delivered here as a keypress *synchronously*, before @inquirer/core's
        // readline 'SIGINT' handler rejects the prompt and before signal-exit
        // can re-raise the signal. Exiting synchronously here is the only path
        // that deterministically yields code 130: if we instead let the prompt
        // reject with ExitPromptError, signal-exit re-emits SIGINT and the
        // process dies by signal mid-cleanup, discarding our process.exitCode.
        rl.output?.write?.('\x1B[?25h'); // restore cursor (skipped by sync exit otherwise)
        rl.close();
        process.exit(130);
      }
      if (isEscapeKey(key)) {
        setBackRequested(true);
        return;
      }
      if (isEnterKey(key)) {
        const selected = items[active];
        if (selected && !Separator.isSeparator(selected) && isSelectable(selected)) {
          setStatus('done');
          done(selected.value);
        }
      } else if (isUpKey(key) || isDownKey(key)) {
        rl.clearLine(0);
        if (
          loop ||
          (isUpKey(key) && active !== bounds.first) ||
          (isDownKey(key) && active !== bounds.last)
        ) {
          const offset = isUpKey(key) ? -1 : 1;
          let next = active;
          do {
            next = (next + offset + items.length) % items.length;
          } while (!isSelectable(items[next]!));
          setActive(next);
        }
      }
    });

    // Throw during render phase so createPrompt's try/catch rejects the Promise.
    if (backRequested) {
      throw new BackSignal();
    }

    const message = ACCENT(config.message);

    // Compute pagination unconditionally — @inquirer/core hooks are positional,
    // so usePagination must run on every render regardless of status.
    const page = usePagination({
      items,
      active,
      renderItem({ item, isActive }) {
        if (Separator.isSeparator(item)) {
          return `  ${chalk.dim(item.separator)}`;
        }
        const cursor = isActive ? ACCENT('❯') : ' ';
        const label = isActive ? ACCENT(item.name) : item.name;
        return `${cursor} ${label}`;
      },
      pageSize,
      loop,
    });

    if (status === 'done') {
      const selected = items[active];
      const name =
        selected && !Separator.isSeparator(selected) ? selected.name : '';
      return `${prefix} ${message} ${chalk.cyan(name)}`;
    }

    const helpLine = chalk.dim('(↑↓ navigate · ⏎ select · ESC back)');

    return [`${prefix} ${message}`, page, helpLine].join('\n');
  },
) as <T>(config: SelectConfig<T>, context?: { input?: NodeJS.ReadableStream; output?: NodeJS.WritableStream }) => Promise<T>;

// ---------------------------------------------------------------------------
// customCheckbox
// ---------------------------------------------------------------------------

export interface CheckboxChoice {
  name: string;
  value: string;
  checked?: boolean;
  disabled?: boolean | string;
}

export interface CheckboxConfig {
  message: string;
  choices: Array<CheckboxChoice | Separator>;
  pageSize?: number;
  loop?: boolean;
}

type NormalizedCheckboxItem = {
  name: string;
  value: string;
  checked: boolean;
  disabled?: boolean | string;
};

function normalizeCheckboxChoices(
  choices: Array<CheckboxChoice | Separator>,
): Array<NormalizedCheckboxItem | Separator> {
  return choices.map((c) => {
    if (Separator.isSeparator(c)) return c;
    return {
      name: c.name,
      value: c.value,
      checked: c.checked ?? false,
      disabled: c.disabled,
    };
  });
}

export const customCheckbox = createPrompt(
  (config: CheckboxConfig, done: (value: string[]) => void) => {
    const { pageSize = 7, loop = true } = config;

    const [items, setItems] = useState(() =>
      normalizeCheckboxChoices(config.choices),
    );

    const bounds = useMemo(() => {
      const first = items.findIndex(isSelectable);
      const last = findLastIndex(items, isSelectable);
      return { first: first === -1 ? 0 : first, last: last === -1 ? 0 : last };
    }, [items]);

    const [active, setActive] = useState(bounds.first);
    const [status, setStatus] = useState<'idle' | 'done'>('idle');
    // Flag set in keypress handler; checked in render to throw BackSignal.
    const [backRequested, setBackRequested] = useState(false);
    const theme = makeTheme({}, undefined);
    const prefix = usePrefix({ status, theme });

    useKeypress((key: KeypressEvent, rl) => {
      if (key.ctrl === true && key.name === 'c') {
        // Ctrl-C = hard quit (exit 130). On a raw-mode TTY the 0x03 byte is
        // delivered here as a keypress *synchronously*, before @inquirer/core's
        // readline 'SIGINT' handler rejects the prompt and before signal-exit
        // can re-raise the signal. Exiting synchronously here is the only path
        // that deterministically yields code 130: if we instead let the prompt
        // reject with ExitPromptError, signal-exit re-emits SIGINT and the
        // process dies by signal mid-cleanup, discarding our process.exitCode.
        rl.output?.write?.('\x1B[?25h'); // restore cursor (skipped by sync exit otherwise)
        rl.close();
        process.exit(130);
      }
      if (isEscapeKey(key)) {
        setBackRequested(true);
        return;
      }
      if (isEnterKey(key)) {
        const selected = items
          .filter((i): i is NormalizedCheckboxItem => !Separator.isSeparator(i) && i.checked)
          .map((i) => i.value);
        setStatus('done');
        done(selected);
      } else if (isUpKey(key) || isDownKey(key)) {
        rl.clearLine(0);
        if (
          loop ||
          (isUpKey(key) && active !== bounds.first) ||
          (isDownKey(key) && active !== bounds.last)
        ) {
          const offset = isUpKey(key) ? -1 : 1;
          let next = active;
          do {
            next = (next + offset + items.length) % items.length;
          } while (!isSelectable(items[next]!));
          setActive(next);
        }
      } else if (isSpaceKey(key)) {
        setItems(
          items.map((item, i) => {
            if (i !== active || Separator.isSeparator(item)) return item;
            return { ...item, checked: !item.checked };
          }),
        );
      }
    });

    // Throw during render phase so createPrompt's try/catch rejects the Promise.
    if (backRequested) {
      throw new BackSignal();
    }

    const message = ACCENT(config.message);

    // Compute pagination unconditionally — @inquirer/core hooks are positional,
    // so usePagination must run on every render regardless of status.
    const page = usePagination({
      items,
      active,
      renderItem({ item, isActive }) {
        if (Separator.isSeparator(item)) {
          return `  ${chalk.dim(item.separator)}`;
        }
        const cursor = isActive ? ACCENT('❯') : ' ';
        const checkbox = item.checked ? chalk.green('◉') : '◯';
        const label = isActive ? ACCENT(item.name) : item.name;
        return `${cursor} ${checkbox} ${label}`;
      },
      pageSize,
      loop,
    });

    if (status === 'done') {
      const selection = items
        .filter((i): i is NormalizedCheckboxItem => !Separator.isSeparator(i) && i.checked)
        .map((i) => i.name)
        .join(', ');
      return `${prefix} ${message} ${chalk.cyan(selection || '(none)')}`;
    }

    // S6: visible back affordance — must contain "ESC" and "← Back"
    const helpLine = chalk.dim('(↑↓ navigate · space toggle · ⏎ confirm · ESC ← Back)');

    return [`${prefix} ${message}`, page, helpLine].join('\n');
  },
) as (config: CheckboxConfig, context?: { input?: NodeJS.ReadableStream; output?: NodeJS.WritableStream }) => Promise<string[]>;
