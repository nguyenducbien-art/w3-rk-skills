---
name: authoring
description: >
  Contributor guide for the **w3-rk-skills** Claude Code marketplace — how to add or extend a SKILL
  inside a plugin here, the house conventions, and the git / version / release flow. Use this when
  working IN the `w3-rk-skills` repo and the task is: "add a new skill", "create/extend a skill",
  "write a new skill into the w3-integration-test plugin", "add a new plugin", "how do I release /
  bump the version / publish so teammates get it", "keep the plugin and the copy-paste set in sync",
  or any change to a `plugins/**/skills/**` SKILL.md / references / scripts. Read this BEFORE editing
  so you follow the structure, the self-contained rule, the verify-heuristic pattern, and the
  version-bump release flow.
---

# Authoring skills in the `w3-rk-skills` marketplace

You are extending a **Claude Code marketplace repo** (`w3-rk-skills`). It IS the marketplace
(`.claude-plugin/marketplace.json`) and hosts plugins under `plugins/`; each plugin hosts skills
under `plugins/<plugin>/skills/<skill>/`. Teammates install a plugin and get its skills; they
**auto-update only when the plugin's `version` changes**. This guide is the conductor — the detail
lives in `references/`.

## 🔴 The 8 golden rules (violating these breaks the release or the team)

1. **Edit in the canonical repo:** `…/w3-rk-skills/plugins/<plugin>/skills/<skill>/`. NEVER edit the
   installed cache (`~/.claude/plugins/cache/…`) — Claude regenerates it from the marketplace and
   overwrites your edits.
2. **A skill's invoke command = its DIRECTORY name, namespaced by the plugin → `/<plugin>:<skill>`**
   (e.g. dir `generation` in plugin `w3-integration-test` → `/w3-integration-test:generation`). The
   `name:` field in front-matter is only a label; the directory name is what becomes the command.
3. **🔴 BUMP `version` in the plugin's `.claude-plugin/plugin.json` on EVERY change you want released**
   (semver: `1.0.x` patch / `1.x.0` feature / `x.0.0` breaking), then commit + push. **Auto-update
   fires ONLY when `version` changes** — a push that forgets the bump never reaches teammates. See
   `references/git-and-distribution.md`.
4. **Self-contained:** all rules inline under the skill's `references/`; bundle `scripts/` + `assets/`.
   No machine-specific absolute paths, no dependency on Claude Code memory files, no personal repo
   paths. A teammate must get identical behavior from a clean install.
5. **Comments / code / file text = English or Japanese only — never Vietnamese.** Skills communicate
   with the user in **their language (default English)**.
6. **Every machine-checkable rule gets a self-check** — a `verify()` warning in the generator script
   (and, for a gen↔review pair, a mirrored auto-flag in the reviewer + a line in the review
   checklist). This "rule = §section + verify heuristic + review mirror" lock-step is the house
   pattern (`references/authoring-conventions.md`).
7. **Test before commit:** `python3 -m py_compile` every script; run the generator end-to-end so its
   `verify()` prints `OK`; if a copy-paste twin exists, confirm 0 plugin-tokens leaked. 
8. **Git discipline:** conventional commits (`feat:`/`fix:`/`docs:`), **no `Co-Authored-By`**, **never
   `git push --force`**. Commit + bump are part of the change; push when the user asks.

## Workflow — add a NEW skill to an existing plugin

1. **Scaffold:** `plugins/<plugin>/skills/<new-skill>/` with `SKILL.md` (+ `references/`, `scripts/`,
   `assets/` as needed). Mirror the shape of `plugins/w3-integration-test/skills/generation/`.
2. **Write `SKILL.md`** = a *thin conductor*: front-matter (`name` + a `description` whose text carries
   the trigger phrases), then a short body: Input → Reference map (read-on-demand table) → Workflow →
   Deliverables → Guardrails. Knowledge goes in `references/`, NOT in SKILL.md. → `references/authoring-conventions.md`.
3. **Put the rules in `references/*.md`** (one concern per file, each rule a `§section`), generators in
   `scripts/*.py` (self-contained, `OUT_DIR = Path(__file__).resolve().parent`), binary templates in
   `assets/`.
4. **Add verify-heuristics** for the new rules (golden rule 6).
5. **Bump** the plugin's `version`; update the repo `README.md` (Plugins/Skills table) and, if it's a
   gen↔review pair, keep them in lock-step.
6. **Test → commit (`feat:`) → push.**

## Workflow — add a NEW plugin to the marketplace
Create `plugins/<plugin>/.claude-plugin/plugin.json` (`name`,`version`,`description`,`author`) +
`skills/<skill>/…`, then register it in `.claude-plugin/marketplace.json` `plugins[]`
(`{name, source:"./plugins/<plugin>", description}`). → `references/repo-and-distribution.md`.

## Reference map (read on demand)

| File | Read it when |
|---|---|
| `references/repo-and-distribution.md` | repo/marketplace/plugin/skill anatomy; how skills load & install; how `../sibling/` cross-refs work; the worked example (`w3-integration-test`); adding a plugin. |
| `references/authoring-conventions.md` | SKILL.md front-matter + conductor pattern; references/scripts/assets layout; the **verify-heuristic** + **gen↔review lock-step** patterns; language/self-contained rules. |
| `references/git-and-distribution.md` | branch, commit format, **version-bump release flow**, auto-update mechanics, local test commands, and the **plugin ↔ copy-paste dual-distribution** skin discipline. |

> The single best template to copy from is the live `w3-integration-test` plugin (skills `generation`
> + `review`). Read its `SKILL.md` + `references/` + `scripts/` before writing a new skill — it
> embodies every convention in this guide.
