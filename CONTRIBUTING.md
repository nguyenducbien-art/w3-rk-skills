# CONTRIBUTING — how to author skills in `w3-rk-skills`

> **Handoff guide** for a Claude (or human) about to **add or extend a skill** in this repo.
> Read this BEFORE editing anything under `plugins/**`. It covers: the repo anatomy, how to write a
> skill, the house conventions (self-contained references, verify-heuristics, gen↔review lock-step),
> and the git / version / release + dual-distribution flow.
>
> 🟢 **The single best template to copy is the live `w3-integration-test` plugin** (skills
> `generation` + `review`). Read its `SKILL.md` + a couple of `references/*.md` + `scripts/*.py`
> before writing anything — it embodies every rule below in real form.

---

## 0. The 8 golden rules (break these and the release or the team breaks)

1. **Edit in this repo** (`…/w3-rk-skills/plugins/<plugin>/skills/<skill>/`). NEVER edit the installed
   cache (`~/.claude/plugins/cache/…`) — Claude regenerates it from the marketplace and overwrites you.
2. **A skill's invoke command = its DIRECTORY name, namespaced by the plugin → `/<plugin>:<skill>`.**
   The `name:` in front-matter is only a label; the directory name is the command. Name the dir to be
   the command you want, and keep `name:` equal to it.
3. **🔴 BUMP `version` in the plugin's `.claude-plugin/plugin.json` on EVERY change you want released**
   (semver), then commit + push. **Auto-update fires ONLY when `version` changes** — a push that forgets
   the bump never reaches teammates. (§3)
4. **Self-contained:** all rules inline under the skill's `references/`; bundle `scripts/` + `assets/`.
   No machine-specific absolute paths, no personal repo paths, no dependency on Claude Code memory.
   A teammate must get identical behavior from a clean install.
5. **Comments / code / file text = English or Japanese only — never Vietnamese.** Skills talk to the
   user in **their language (default English)**; JP labels/messages/codes stay **verbatim** (`「…」`,
   `E0xx`, `正常`/`異常`).
6. **Every machine-checkable rule gets a self-check** — a `verify()` warning in the generator script,
   plus (for a gen↔review pair) a mirrored auto-flag in the reviewer + a line in the review checklist.
   "rule = §section + verify heuristic + review mirror" is the house pattern. (§2)
7. **Test before commit:** `python3 -m py_compile` every script; run the generator so its `verify()`
   prints `OK`; if a copy-paste twin exists, confirm 0 plugin-tokens leaked. (§3)
8. **Git discipline:** conventional commits (`feat:`/`fix:`/`docs:`), **no `Co-Authored-By`**, **never
   `git push --force`**. Bump + commit are part of the change; push when the user asks.

---

## 1. Anatomy — marketplace / plugin / skill

```
w3-rk-skills/                                  ← the REPO *is* a Claude Code marketplace
├── .claude-plugin/marketplace.json            ← CATALOG: { name, owner, description, plugins[] }
├── README.md                                  ← user-facing (install / use / maintain)
├── CONTRIBUTING.md                            ← this guide
└── plugins/
    └── <plugin>/                              ← a PLUGIN (installable unit; has a version)
        ├── .claude-plugin/plugin.json         ← { name, version, description, author }
        └── skills/
            └── <skill>/                       ← a SKILL (the invocable unit)
                ├── SKILL.md                   ← front-matter + thin conductor body
                ├── references/*.md            ← knowledge, read on demand
                ├── scripts/*.py               ← generators/helpers (self-contained)
                └── assets/*                   ← binary templates etc.
```

- **marketplace.json** lists every plugin so `/plugin install <plugin>@w3-rk-skills` finds it.
  Entry: `{ "name": "<plugin>", "source": "./plugins/<plugin>", "description": "…" }`.
- **plugin.json** carries **`version`** — the only lever that triggers teammate auto-update.
- **A skill** = a directory with `SKILL.md`. Directory name = command (golden rule 2). A skill also
  **auto-triggers** (without typing the command) when the user's request matches the `description:`
  text — so write the trigger phrases INTO the description.

**Sibling cross-references:** skills in the same plugin sit side-by-side, so one can read another's
files with a relative path. `review` reads shared rules from `../generation/references/…`. Use this so
the generator owns the rule files and the reviewer reads them — no duplication.

**How skills reach a machine (two forms):**
- **Plugin form:** teammate runs `/plugin marketplace add <git-url>` then `/plugin install
  <plugin>@w3-rk-skills`. Claude caches the resolved skill under `~/.claude/plugins/cache/…` (generated
  — don't edit it). New session + version bump refreshes it.
- **Copy-paste form:** the same skill copied straight into a code repo's `.claude/skills/<skill>/` (no
  marketplace). The W3 skills keep a copy-paste twin — same content, different "skin" (§3).

**Add a NEW plugin:** create `plugins/<plugin>/.claude-plugin/plugin.json`
(`{name,version:"1.0.0",description,author}`) + `skills/<skill>/…`, then register it in
`marketplace.json` `plugins[]`, add a README row, commit `feat:`.

---

## 2. How to write a skill

### 2.1 `SKILL.md` front-matter
```yaml
---
name: <skill>              # label (keep equal to the directory name)
description: >             # 🔴 the most important field — Claude auto-triggers from this text.
  <one sentence: what it does>. Use this when <concrete situations>. Trigger when the user types
  `/<plugin>:<skill> <args>`, or says "<phrase 1>" / "<phrase 2>" / ... .
---
```
Pack the **trigger phrases** (verbatim user wordings + the slash command) into `description`. A vague
description never fires. Keep it to *what* + *when* (not how), under ~80 words.

### 2.2 `SKILL.md` body = a thin CONDUCTOR, not a manual
Knowledge lives in `references/`; the body just orchestrates. Canonical sections:
1. **Input** — required args; if missing, ask + stop. Optional inputs (e.g. an env block).
2. **Reference map** — a `| file | read it when |` table telling the model to **read on demand, not
   preload everything**. This is the core of the pattern: SKILL.md stays small.
3. **Workflow** — numbered steps, each pointing at the reference that governs it.
4. **Deliverables / Output** — exact location + filenames.
5. **Guardrails** — hard "never do X" rules.

🚫 Don't inline rules in SKILL.md. If you're explaining *how*, it belongs in a `references/*.md`
`§section` that the reference map points at.

### 2.3 `references/` — one concern per file, each rule a `§section`
- Split by concern (`writing-rules.md`, `output-rules.md`, `project-config.md`, …).
- Give every rule a stable **`## §slug`** heading so other files / the review checklist / the verify
  warnings can cite it by name (`§slug`).
- Prefer a short worked **✅ / ❌ example** per rule over prose — the model copies examples.
- Change a rule in ONE place (its §section); everything else cites it.

### 2.4 `scripts/` — self-contained Python
- Plain Python 3 + bundled libs (e.g. `openpyxl`). **No machine paths**: `OUT_DIR =
  Path(__file__).resolve().parent`; assets via `Path(__file__).resolve().parents[1] / "assets" / "…"`.
- A "template" generator (copied per-item, then filled) keeps a top **CONFIG block** + typed data
  lists + a `verify()` + a writer. (See `build_csv.py`.)
- Comments **English/Japanese only**. `python3 -m py_compile` must pass.

### 2.5 🔴 The verify-heuristic pattern (enforce every checkable rule)
A rule is only as strong as its enforcement. When a rule has a detectable shape, add a **low-noise
text heuristic** to the generator's `verify()` that warns on violation:
```python
def _bundled_outcome(cell):           # §expected: ≥2 outcomes on one EXPECTED line → split
    for ln in (cell or '').split('\n'):
        low = ln.lower()
        if ('modal' in low or 'is displayed' in low) and any(k in low for k in ('loading','is hidden','stays on the form')):
            return True
    return False
# inside verify():  if _bundled_outcome(ee): warn.append("TC..: split outcomes (§expected)")
```
Gate on a specific marker + exempt legitimate cases (a false positive trains people to ignore
warnings). **Unit-test the heuristic** on true-positive AND false-positive strings before shipping.
`verify()` prints `OK` or `WARN` lines — it never auto-fixes.

### 2.6 🔴 The gen ↔ review lock-step (paired skills)
When a generator has a reviewer twin, **every rule lives in three+ places, kept in sync**:
1. the **§section** in the generator's references (source of truth),
2. a **`verify()` heuristic** in the generator script,
3. the reviewer mirror — a `dump_tc.py` auto-flag (same heuristic) + a `review-checklist.md` line.

So one convention change touches the §section + gen verify + review checklist + review auto-flag (+ any
worked example). Updating only one silently drifts the pair. This is what keeps "what the reviewer
checks" == "what the generator must produce".

### 2.7 Self-containment (non-negotiable)
A rule learned in one session must be **baked into `references/`** (+ verify + review mirror), NOT left
in a personal memory note — a teammate on a clean install has neither your memory nor your paths.

---

## 3. Git, versioning & distribution

### 3.1 Branch & commit
- Work on **`main`** (small skills repo — no feature-branch ceremony).
- **Conventional commits:** `feat:` (new rule/skill/capability) · `fix:` (corrects wrong behavior) ·
  `docs:` (text only) · `refactor:` · `chore:`. One logical change per commit.
- 🚫 **No `Co-Authored-By` / no AI footer.** 🚫 **Never `git push --force`.** Push when the user asks.

### 3.2 🔴 Versioning — the release lever
`plugins/<plugin>/.claude-plugin/plugin.json` `version`. **Teammates auto-update ONLY when it changes.**
- **Bump on EVERY released change, in the same commit.** Semver:
  `1.0.x` patch (wording/heuristic/fix) · `1.x.0` feature (new rule/capability) · `x.0.0` breaking
  (output/invocation/layout change).
- A push that changes content **without** bumping `version` will **NOT reach** teammates — the #1
  release mistake.
- Found a bug in an already-pushed version? **Bump again** — re-pushing different content under the
  same number does not re-trigger auto-update.

### 3.3 How auto-update works (so you can reason about it)
1. `git push` updates the GitHub marketplace repo.
2. A teammate with **auto-update enabled** (OFF by default for third-party marketplaces — each enables
   it once via `/plugin` → Marketplaces tab) gets the new version on their **next new session**.
3. To get it now / if auto-update is off: `/plugin marketplace update w3-rk-skills`, then open a **new
   session** (a running session keeps the version it loaded at start).
4. Check installed version: `/plugin` → Manage plugins (or `~/.claude/plugins/installed_plugins.json`).

### 3.4 Test before commit
```bash
python3 -m py_compile plugins/<plugin>/skills/<skill>/scripts/*.py     # scripts compile
cd <a sample output dir> && python3 build_csv.py                       # generator → "verify: OK"
```
Unit-test any new `verify()` heuristic on a few strings (true + false positive) before shipping.

### 3.5 🔴 Dual-distribution: plugin ↔ copy-paste twin
The integration-test skills ship **two ways**; both must stay in sync:

| | Canonical (plugin) | Copy-paste twin |
|---|---|---|
| Where | `…/w3-rk-skills/plugins/w3-integration-test/skills/{generation,review}/` | `~/Downloads/files/w3-integration-test-{generation,review}/` |
| For | install the marketplace | copy a folder into `<repo>/.claude/skills/` |
| Versioned | yes (`plugin.json`) | no |

**Content (rules/scripts/assets) is identical; only the "skin" differs.** When you change a rule in the
plugin, port it to the twin. Most files are identical → `cp` verbatim; a few carry skin → `cp` then `sed`:

| Aspect | Plugin | Copy-paste twin |
|---|---|---|
| Skill dir / `name:` / trigger | `generation` / `/generation` | `w3-integration-test-generation` / `/w3-integration-test-generation` |
| `CODE_REPO` (project-config §1) | "the session cwd" | "the repo that contains this skill" |
| Output dir | `<cwd>/w3-rk-skills-output/w3-integration-test/<skill>/…` | `<skill>/output/…` |
| Review cross-ref | `../generation/references/` | `../w3-integration-test-generation/references/` |
| SKILL.md "Portability" / README | "distributed as a plugin" / short stub | "copy into `.claude/skills/`" / full self-contained doc |

```bash
# files WITH skin → cp then sed the skin back:
sed -i '' 's#<cwd>/w3-rk-skills-output/w3-integration-test/generation/#<skill>/output/#g' <gen file>
sed -i '' 's#\.\./generation/#../w3-integration-test-generation/#g' <review file>
# verify the port leaked no plugin tokens (must print nothing):
grep -rn 'w3-rk-skills-output\|\.\./generation/\|w3-rk-skills' <twin-dir>
```
For `SKILL.md` / `project-config.md` / `README.md` (most skin) — keep the twin's existing skin and port
only the new CONTENT; don't overwrite their skin sections.

---

## 4. Release checklist (run before `git push`)

- [ ] Rule baked in its `§section` (source of truth) with a worked ✅/❌ example.
- [ ] `verify()` heuristic added (low-noise, unit-tested); for a pair, the review auto-flag +
      `review-checklist.md` line mirror it.
- [ ] Scripts `py_compile` clean; generator `verify()` prints `OK`.
- [ ] **`version` bumped** in the right `plugin.json` (correct semver tier).
- [ ] `README.md` updated if a plugin/skill was added or a user-facing flow changed.
- [ ] Copy-paste twin synced (if the changed skill has one); `grep` shows 0 leaked plugin tokens.
- [ ] Conventional commit message; no `Co-Authored-By`.
