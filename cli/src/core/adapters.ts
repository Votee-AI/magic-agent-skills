export interface CommandAdapter {
  extension: string;
  adapt(filename: string, content: string): { filename: string; content: string };
}

function extractDescription(content: string): string {
  const lines = content.split('\n');
  for (const line of lines) {
    const trimmed = line.trim();
    if (trimmed && !trimmed.startsWith('<!--') && !trimmed.startsWith('#')) {
      return trimmed.slice(0, 120);
    }
  }
  return '';
}

function stripTriggerComment(content: string): string {
  return content.replace(/<!--\s*Natural Language Triggers:.*?-->\s*\n?/s, '');
}

export const markdownAdapter: CommandAdapter = {
  extension: '.md',
  adapt(filename, content) {
    return { filename, content };
  },
};

export const tomlAdapter: CommandAdapter = {
  extension: '.toml',
  adapt(filename, content) {
    const name = filename.replace(/\.md$/, '');
    const description = extractDescription(content);
    const body = stripTriggerComment(content);

    const toml = [
      `[command]`,
      `name = "magic-${name}"`,
      `description = ${JSON.stringify(description)}`,
      ``,
      `[command.prompt]`,
      `text = """`,
      body.trim(),
      `"""`,
      ``,
    ].join('\n');

    return { filename: `magic-${name}.toml`, content: toml };
  },
};

export const promptAdapter: CommandAdapter = {
  extension: '.prompt.md',
  adapt(filename, content) {
    const name = filename.replace(/\.md$/, '');
    const description = extractDescription(content);
    const body = stripTriggerComment(content);

    const prompt = [
      `---`,
      `mode: agent`,
      `description: ${JSON.stringify(description)}`,
      `---`,
      ``,
      body.trim(),
      ``,
    ].join('\n');

    return { filename: `magic-${name}.prompt.md`, content: prompt };
  },
};

const adapters: Record<string, CommandAdapter> = {
  md: markdownAdapter,
  toml: tomlAdapter,
  prompt: promptAdapter,
};

export function getAdapter(format: string | null): CommandAdapter | null {
  if (!format) return null;
  return adapters[format] ?? null;
}
