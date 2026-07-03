/**
 * Single source of truth for skill-suite definitions.
 *
 * ORDER MATTERS: the list is most-specific-first. `magic-linguistic-` must be
 * tested BEFORE the data `magic-` rule, or every linguistics skill would
 * mis-bucket into the data suite (since `magic-linguistic-*` also starts with
 * `magic-`).
 */
export const SUITES = [
  {
    key: 'linguistic',
    dirPrefix: 'magic-linguistic-',
    displayName: 'Linguistics',
    commandGroup: 'linguistic',
  },
  {
    key: 'data',
    dirPrefix: 'magic-',
    displayName: 'Data',
    commandGroup: 'data',
  },
] as const;

export type SuiteKey = (typeof SUITES)[number]['key'];

/**
 * Returns the suite a skill directory belongs to, or null if it matches none.
 * Tests suites in declaration order (most-specific-first).
 */
export const suiteForDir = (d: string): (typeof SUITES)[number] | null =>
  SUITES.find((s) => d.startsWith(s.dirPrefix)) ?? null;
