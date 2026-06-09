# Project config — paths, branches, git rules

> Single source of the **repo**, the **scaffold files**, the **sprint branch**, and the **git
> discipline** for a scaffold merge. The skill is a **plugin** (installed outside the code repo), so
> `CODE_REPO` = the **session cwd** (the repo you opened Claude Code in). No per-machine path edit is
> needed; the only thing to confirm is the sprint branch (§sprint-branch — ask if unknown).

## §repo

`CODE_REPO` = the session's current working directory. Confirm it is the W3 code repo (markers under
cwd): `.claude/skills/frontend-mig-shared/rules/w3-frontend-standard.md` and
`resources/assets/javascripts/controllers/BaseController.js`. Markers not found → **ask the user** for
the repo path (do not guess). GitHub remote = `dialog-inc/w3package_v2` (confirm with `gh repo view`).

The child PRs to merge live on this remote; you read each via `gh pr view` / `gh pr diff` and check
them out with `gh pr checkout` or `git fetch origin <head-branch>` (read-only).

## §scaffold-files

The scaffold (足場) is the Kanaya code-gen skill set. The files that **multiple child PRs
collide on** — the ones this skill carefully merges — are:

| Role | Path (relative to `CODE_REPO`) |
|---|---|
| 🔴 **SSOT rules** (single source of truth; the `verify_scaffold.py` target) | `.claude/skills/frontend-mig-shared/rules/w3-frontend-standard.md` |
| Sub-skill: implementation | `.claude/skills/frontend-screen-implementation/SKILL.md` |
| Sub-skill: parity-review | `.claude/skills/frontend-screen-parity-review/SKILL.md` |
| Sub-skill: reference-build | `.claude/skills/frontend-screen-reference-build/SKILL.md` |
| Sub-skill: developer-test | `.claude/skills/frontend-screen-developer-test/SKILL.md` |
| Sub-skill: i18n-translation | `.claude/skills/frontend-screen-i18n-translation/SKILL.md` |
| Sub-skill: orchestrator | `.claude/skills/frontend-screen-development-orchestrator/SKILL.md` |
| Reference templates | `.claude/skills/frontend-mig-shared/reference/screens/_template/*.md`, `reference/conversion-mapping.md` |
| Code templates (hygen) | `frontend/_templates/{list,edit}-screen/**` |
| Docs | `docs/frontend_mig/screen-func-mapping/screen-id-mapping.md` |

The **SSOT `w3-frontend-standard.md`** is the file every rule lives in (§0 meta counters + §2 new
rules + §3 Anti-Pattern + §0 ID table) and the one most prone to ID collision / counter drift — it is
the file `verify_scaffold.py` checks. The "5-place bake" pattern means one rule usually touches the
SSOT + 3-4 sub-skill SKILLs, so child PRs overlap heavily across these files.

> If a project uses a different scaffold, list its SSOT + sub-skill files here and update the `RE_*`
> markers in `verify_scaffold.py` (`verify-rules.md §Adapting the markers`).

## §sprint-branch

Child PRs target a **sprint integration branch** (the merge destination). For W3 this is currently
`mimosa/frontend/develop/r20260601`, but it **rotates each sprint** — so do **not** hard-code it:

1. Read it from the child PRs: `gh pr view <pr> --json baseRefName` — every child PR's base IS the
   sprint branch (they all share one). Confirm all children share the same base.
2. If the children disagree or you cannot read them → **ask the user** which branch is the current
   sprint branch. Never guess.

## §git-rules

- **Conventional commits**, one logical change per commit: `feat:` / `fix:` / `docs:` / `chore:`.
  Format for this project: `{prefix}: [mimosa][frontend] {what} #{ref}` (vendor `[mimosa]`, not
  `[base]`). 🚫 **No `Co-Authored-By`, no AI/Claude footer** (any footer at all) in commits or PR bodies.
- 🔴 **Push is OFF by default.** Do `git push` / open a PR / close PRs **only when the user explicitly
  asks for that step** — and even then, in **auto mode treat `git push` as needing an explicit
  go-ahead** (the project's standing rule is "never push unless told"). Prepare locally; let the user
  confirm the outward-facing actions (`merge-workflow.md §finish`).
- 🚫 Never `git push --force`. Never edit application source (`controllers/`, `app/`, `frontend/apps/`)
  — this skill only edits the scaffold files in §scaffold-files.
- The integration branch must **not** keep its upstream pointing at the sprint/base branch — unset it
  before publishing (`merge-workflow.md §integration-branch`).
