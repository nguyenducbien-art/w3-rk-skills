# Git, versioning & distribution

## Branch & commit

- Work on **`main`** (this is a small skills repo, not the product repo — no feature-branch ceremony).
- **Conventional commits:** `feat:` (new rule/skill/capability), `fix:` (corrects wrong behavior),
  `docs:` (text/guide only), `refactor:`, `chore:`. One logical change per commit.
- 🚫 **No `Co-Authored-By` / no AI/Claude footer** in commit messages.
- 🚫 **Never `git push --force`** (any form). 
- Bumping the version + committing are part of the change; **push when the user asks** (the user
  usually runs `git push` themselves).

## 🔴 Versioning — the release lever

`plugins/<plugin>/.claude-plugin/plugin.json` has a `version`. **Teammates auto-update ONLY when this
number changes.** So:

- **Bump `version` on EVERY change you intend to release** — same commit as the change. Semver:
  - `1.0.x` **patch** — wording/doc/heuristic tweak, bug fix, no behavior change for the user.
  - `1.x.0` **feature** — a new rule, a new TC type, a new capability.
  - `x.0.0` **breaking** — output format / invocation / file-layout change.
- A push that changes content **without** bumping `version` will **NOT reach** teammates (the cache
  keeps the old version). This is the #1 release mistake — always bump.
- If a version was already pushed and you find a bug in it, **bump again** (e.g. `1.0.2` → `1.0.3`) —
  re-pushing different content under the same number does not re-trigger auto-update.

## How auto-update actually works (so you can reason about it)

1. `git push` updates the GitHub marketplace repo.
2. On a teammate machine with **auto-update enabled** for the marketplace, the **next new session**
   pulls the marketplace clone, sees the higher `version`, and re-caches the plugin. (Auto-update for
   third-party marketplaces is **OFF by default** — each teammate enables it once via `/plugin` →
   Marketplaces tab, or an admin sets it in `managed-settings.json`.)
3. To get it **now** (or if auto-update is off): `/plugin marketplace update w3-rk-skills`, then open a
   **new session**. A session already running keeps the version it loaded at start.
4. Check the installed version via `/plugin` → Manage plugins (or read
   `~/.claude/plugins/installed_plugins.json`). The marketplace clone's available version is in
   `~/.claude/plugins/marketplaces/w3-rk-skills/plugins/<plugin>/.claude-plugin/plugin.json`.

## Test BEFORE you commit

```bash
# scripts compile
python3 -m py_compile plugins/<plugin>/skills/<skill>/scripts/*.py
# the generator runs clean (verify prints OK)
cd <a sample output dir> && python3 build_csv.py          # → "verify: OK"
# (paired skill) the reviewer's dumper compiles & flags correctly
python3 -m py_compile plugins/<plugin>/skills/<review>/scripts/dump_tc.py
```
Unit-test any new `verify()` heuristic on a few strings (true-positive + false-positive cases) before
shipping it — a noisy heuristic is worse than none.

## Release checklist (run through before `git push`)

- [ ] Rule baked in the `§section` (source of truth), with a worked ✅/❌ example.
- [ ] `verify()` heuristic added (low-noise, unit-tested) — and, for a pair, the review auto-flag +
      `review-checklist.md` line mirror it.
- [ ] Scripts `py_compile` clean; generator `verify()` prints `OK`.
- [ ] **`version` bumped** in the right `plugin.json` (correct semver tier).
- [ ] `README.md` updated if a plugin/skill was added or a user-facing flow changed.
- [ ] Copy-paste twin synced (below) if the changed skill has one.
- [ ] Conventional commit message; no `Co-Authored-By`.

---

## 🔴 Dual-distribution: plugin ↔ copy-paste twin

The W3 integration-test skills ship **two ways**, and both must stay in sync:

| | Canonical (plugin) | Copy-paste twin |
|---|---|---|
| Where | `…/w3-rk-skills/plugins/w3-integration-test/skills/{generation,review}/` | `~/Downloads/files/w3-integration-test-{generation,review}/` |
| For | teammates who install the marketplace | teammates who copy a folder into `<repo>/.claude/skills/` |
| Versioned | yes (`plugin.json`) | no (plain folders) |

**The CONTENT (rules/scripts/assets) is identical; only the "skin" differs.** When you change a rule
in the plugin, port it to the twin too. Most files are **identical** → copy verbatim; a few carry
skin → copy then `sed` the skin back.

### Skin differences (plugin → copy-paste)

| Aspect | Plugin | Copy-paste twin |
|---|---|---|
| Skill dir / `name:` | `generation` / `review` | `w3-integration-test-generation` / `w3-integration-test-review` |
| Trigger in SKILL.md | `/generation` | `/w3-integration-test-generation` |
| `CODE_REPO` (project-config §1) | "the session cwd" | "the repo that contains this skill" (`Path(__file__).parents[N]`) |
| Output dir | `<cwd>/w3-rk-skills-output/w3-integration-test/<skill>/…` | `<skill>/output/…` |
| Review cross-ref | `../generation/references/` | `../w3-integration-test-generation/references/` |
| SKILL.md "Portability" | "distributed as a plugin / marketplace" | "copy into `.claude/skills/`" |
| README per skill | short stub → repo README | full self-contained install/use/output doc |

### Sync procedure

- **Files with NO skin tokens** (most references + all scripts + `assets/template.xlsx`): `cp` verbatim.
- **Files WITH skin** (the few that mention an output path or a sibling cross-ref): `cp` then sed:
  ```bash
  # generation references that print an output path
  sed -i '' 's#<cwd>/w3-rk-skills-output/w3-integration-test/generation/#<skill>/output/#g' <file>
  # review references with the sibling cross-ref
  sed -i '' 's#\.\./generation/#../w3-integration-test-generation/#g' <file>
  ```
- **SKILL.md / project-config.md / README.md** carry the most skin — keep the twin's existing skin and
  port only the new CONTENT (don't overwrite their skin sections).
- **Verify the port:** `grep -rn 'w3-rk-skills-output\|\.\./generation/\|w3-rk-skills' <twin-dir>` must
  return **0** (no plugin tokens leaked); `py_compile` the twin's scripts.

> Why a twin at all: some teammates can't/won't install a marketplace and just paste a folder into
> their repo. The twin gives them the same skill with paths that work from inside the repo.
