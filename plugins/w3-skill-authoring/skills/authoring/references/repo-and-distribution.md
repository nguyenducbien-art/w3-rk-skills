# Repo / marketplace / plugin / skill anatomy

## The four layers

```
w3-rk-skills/                                  ← the REPO *is* a Claude Code marketplace
├── .claude-plugin/marketplace.json            ← the CATALOG: { name, owner, description, plugins[] }
├── README.md                                  ← human docs (install / use / maintain)
└── plugins/
    └── <plugin>/                              ← a PLUGIN (installable unit, has a version)
        ├── .claude-plugin/plugin.json         ← { name, version, description, author }
        └── skills/
            └── <skill>/                       ← a SKILL (the invocable unit)
                ├── SKILL.md                   ← front-matter + conductor body
                ├── references/*.md            ← knowledge, read on demand
                ├── scripts/*.py               ← generators/helpers (self-contained)
                └── assets/*                   ← binary templates etc.
```

- **marketplace.json** lists every plugin so `/plugin install <plugin>@<marketplace>` can find it.
  `plugins[]` entries: `{ "name": "<plugin>", "source": "./plugins/<plugin>", "description": "…" }`.
- **plugin.json** carries the **`version`** — the single lever that triggers teammate auto-update.
- **A skill** = a directory with `SKILL.md`. Its directory name is the command (see below).

## How a skill is invoked

The invoke command is the **skill's directory name, namespaced by its plugin**:
`/<plugin>:<skill-dir>`. Example: `plugins/w3-integration-test/skills/generation/` →
`/w3-integration-test:generation`. The `name:` in front-matter is just a display label — it does
**not** set the command. Autocomplete shows the bare skill name with a plugin tag; you cannot force a
different command string. So **name the directory to be the command you want.**

A skill also auto-triggers (without typing the command) when the user's request matches the
`description:` text — so write the trigger phrases INTO the description.

## How skills load on a machine (two distribution forms)

1. **Plugin form (this repo):** a teammate runs `/plugin marketplace add <git-url>` then
   `/plugin install <plugin>@w3-rk-skills`. Claude clones the marketplace to
   `~/.claude/plugins/marketplaces/<mp>/` and caches the resolved skill under
   `~/.claude/plugins/cache/<mp>/<plugin>/<version-or-sha>/skills/`. **That cache is generated — never
   edit it; edit the repo.** New session + version bump (or `/plugin marketplace update`) refreshes it.
2. **Copy-paste form:** the same skill, copied straight into a code repo's `.claude/skills/<skill>/`.
   No marketplace, no install — the new Claude just opens that repo. This repo keeps a copy-paste twin
   of the W3 skills outside the marketplace; the *content* is identical, only the "skin" differs
   (`git-and-distribution.md` §dual-distribution).

## Sibling cross-references (same plugin)

Skills in the **same plugin** sit side-by-side, so one can read another's references with a relative
path. The `review` skill reads the shared rules from `../generation/references/…` — that resolves
because both are under `…/w3-integration-test/skills/`. Use this to avoid duplicating rules across a
gen↔review pair: the generator owns the rule files, the reviewer reads them.

## Worked example — the `w3-integration-test` plugin

The reference implementation. Two sibling skills sharing one rule-set:

- **`generation`** — reads a W3 screen's source → fills `scripts/build_csv.py` (a per-screen tuple
  generator with a `verify()` self-check) → bilingual CSV → `scripts/build_xlsx.py` fills
  `assets/template.xlsx` → official Excel. All rules in `references/` (`project-config`,
  `mimosa-rules`, `writing-rules`, `test-categories`, `per-button-patterns`, `gates-workflow`,
  `output-rules`, `mimosa-facts`, gold example CSVs).
- **`review`** — reads an existing spec + the screen → Add/Modify/Delete report. Owns only
  `references/{review-workflow,review-checklist,report-format}.md` + `scripts/dump_tc.py`; reads every
  other rule from `../generation/references/`.

Before authoring anything new, **read that plugin's `SKILL.md` + a couple of its `references/` files**
— it demonstrates the conductor pattern, the read-on-demand reference map, the verify-heuristic, and
the gen↔review lock-step in real form.

## Adding a NEW plugin to the marketplace

1. Create `plugins/<plugin>/.claude-plugin/plugin.json`:
   ```json
   { "name": "<plugin>", "version": "1.0.0", "description": "<one line>", "author": { "name": "BienND" } }
   ```
2. Create `plugins/<plugin>/skills/<skill>/SKILL.md` (+ references/scripts/assets).
3. Register in `.claude-plugin/marketplace.json` `plugins[]`:
   ```json
   { "name": "<plugin>", "source": "./plugins/<plugin>", "description": "<one line>" }
   ```
4. Add a row to the repo `README.md` Plugins table. Commit (`feat:`), push.
