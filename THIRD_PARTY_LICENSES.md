# Third-Party Licenses

MAGIC Agent Skills is licensed under **Apache-2.0** (see [`LICENSE`](LICENSE)). This
file is the **root inventory** of all third-party software the project depends on,
across both the **CLI installer** (`cli/`, npm) and the **skills** (`skills/`, pip).

It complements [`cli/LICENSE-THIRD-PARTY`](cli/LICENSE-THIRD-PARTY), which documents
code patterns *adapted* into the CLI (OpenSpec, MIT). That file is not deleted — this
root file is the single place to review every bundled / declared dependency.

> **License policy.** CI (`.github/workflows/ci.yml` → `license-check`) runs
> `pip-licenses --fail-on="GNU General Public License;AGPL;Server Side Public License;Business Source License;Commons Clause"`.
> The build fails on any GPL / AGPL / SSPL / BUSL / Commons-Clause dependency.
> **Status: clean** — every dependency below is permissive (MIT / BSD / Apache-2.0 /
> PSF) except `chardet` (LGPL-2.1+, weak copyleft, used unmodified as a library — not
> in the prohibited set). No strong-copyleft or source-available licenses are present.
>
> This is an **inventory only** — no dependency changes. Reconciled against the
> dependency audits in VOT-2103 / VOT-2104 and the existing `cli/LICENSE-THIRD-PARTY`.

## CLI — npm runtime dependencies (`cli/package.json`)

| Package | Version (range) | License |
|---|---|---|
| `chalk` | ^5.4.1 | MIT |
| `commander` | ^14.0.0 | MIT |
| `@inquirer/core` | ^10.3.2 | MIT |
| `@inquirer/prompts` | ^7.5.0 | MIT |
| `ora` | ^8.2.0 | MIT |
| `fast-glob` | ^3.3.3 | MIT |

### CLI — dev/build dependencies (not shipped in the published package)

| Package | License |
|---|---|
| `typescript` | Apache-2.0 |
| `vitest` | MIT |
| `@types/node` | MIT |

> The published npm package is a **thin installer** — it does not bundle skill
> content (it fetches skills from GitHub at install time). CI's `package-content`
> job enforces that `skills/` and `commands/` are never bundled.

## Skills — Python dependencies (`requirements.txt`)

| Package | Version (resolved) | License |
|---|---|---|
| `pandas` | 2.3.x | BSD-3-Clause |
| `numpy` | 2.4.x | BSD-3-Clause (AND 0BSD/MIT/Zlib/CC0 components) |
| `scipy` | 1.17.x | BSD-3-Clause |
| `matplotlib` | 3.10.x | PSF (matplotlib license, BSD-style) |
| `seaborn` | 0.13.x | BSD-3-Clause |
| `chardet` | 5.2.x | **LGPL-2.1-or-later** (weak copyleft — see note below) |
| `openpyxl` | 3.1.x | MIT |
| `pyarrow` | 19.x | Apache-2.0 |
| `PyYAML` | 6.0.x | MIT |
| `plotly` | 6.x | MIT |
| `pandera` | 0.31.x | MIT |
| `Jinja2` | 3.1.x | BSD-3-Clause |
| `tabulate` | 0.10.x | MIT |
| `pytest` | 9.x | MIT |
| `data-designer` (+ `-config`, `-engine`) | 0.6.0 | Apache-2.0 |
| `tiktoken` | 0.13.x | MIT |
| `rapidfuzz` | 3.x | MIT |
| `psutil` | 7.x | BSD-3-Clause |
| `SQLAlchemy` | 2.0.x | MIT |

Notable transitive families: `cycler` (BSD), `et_xmlfile` (MIT), `iniconfig` (MIT),
plus the standard BSD/MIT scientific-Python stack pulled by the above.

> **`chardet` (LGPL-2.1-or-later).** Used **unmodified** as an imported library by
> `magic-data-loading` for encoding detection. LGPL is weak copyleft and is **not** in
> the project's prohibited-license set (GPL/AGPL/SSPL/BUSL/Commons-Clause); it imposes
> no copyleft obligation on this project's own Apache-2.0 code. If an adopter needs to
> avoid LGPL entirely, encoding detection degrades gracefully (chardet is only used for
> the loading skill's charset sniffing).

## Verification

```bash
# Regenerate the pip inventory:
pip install pip-licenses && pip install -r requirements.txt
pip-licenses --format=markdown --with-urls

# Confirm no prohibited licenses (mirrors CI):
pip-licenses --fail-on="GNU General Public License;AGPL;Server Side Public License;Business Source License;Commons Clause"
```

*Last reconciled: 2026-06-25. Versions reflect the resolved environment; ranges are
the declared constraints in `requirements.txt` / `cli/package.json`.*
