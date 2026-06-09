---
name: merge
description: >
  Carefully merge several child scaffold PRs (that all edit the same shared Kanaya code-gen
  SSOT + frontend-screen-* SKILLs) into ONE integration branch — resolving rule-ID collisions,
  duplicate rules, and §0 counter drift by hand so the scaffold (足場) is never silently
  broken. Output is a new branch (the skill asks its name); on request it pushes, opens a PR into
  the sprint branch, and closes the child PRs. Use this when 2+ open PRs touch the same scaffold
  rules/SKILL files. Trigger when the user types `/w3-rk-scaffold-merging:merge <PRs>`, or says
  "scaffold merge", "merge the child scaffold PRs", "merge the scaffold edits", "integrate scaffold
  PRs #a #b #c into the sprint branch".
---

# W3 Scaffold Merging

Merge multiple child scaffold PRs into one integration branch **without breaking the scaffold (足場)**.
Several PRs editing the same SSOT (`w3-frontend-standard.md`) + the same `frontend-screen-*/SKILL.md`
collide on rule IDs and §0 counters; a naive `git merge` silently produces duplicate IDs and wrong
counts. This skill applies each PR's intent **by hand**, resolves collisions/duplicates, reconciles
counters, and proves it with `scripts/verify_scaffold.py`. All knowledge is in `references/`; this
file is the conductor. Communicate with the user in **their language**; commit/file text is
**English or Japanese only**.

## Input

**The child PRs** to merge (numbers or URLs) — required. If missing, ask and stop. Then confirm they
are *overlapping scaffold* PRs (`merge-workflow.md §inputs`); if they don't overlap, a normal merge
suffices — say so and stop. The skill discovers the sprint branch from the PRs' base; if it can't, it
**asks** (`project-config.md §sprint-branch`).

## Reference map (read on demand — do not preload everything)

| File | Read it when |
|---|---|
| `references/project-config.md` | **First, always.** Repo + scaffold-file paths, sprint branch, git rules. |
| `references/merge-workflow.md` | The step-by-step spine (§inputs → §baseline → §diagnose → §integration-branch → §trunk-first → §per-pr-loop → §reconcile → §finish). |
| `references/conflict-resolution.md` | 🔴 The hard parts: §id-collision, §content-duplicate, §manual-not-merge, §counter-accounting, §counter-reconcile, §verify-each-step. |
| `references/verify-rules.md` | What `verify_scaffold.py` checks (§no-dup-id / §counter-*). Run it after every step. |
| `references/worked-example.md` | The real #10007/#9999/#9981/#10003 run — concrete shape of every step. |

## Workflow

1. **Config & classify** (`project-config.md` §repo; `merge-workflow.md §inputs`). Resolve the repo,
   read each PR's files, confirm they overlap on scaffold files. Discover/ask the sprint branch.
2. **Baseline & diagnose** (`§baseline`, `§diagnose`). Read the sprint branch's SSOT §0 (= ground
   truth + next-free-number map). Get each PR's behind/ahead vs the sprint tip.
3. **Integration branch** (`§integration-branch`). **Ask the user for the branch name**, create it off
   the sprint tip, **unset its upstream** off the base.
4. **Trunk first** (`§trunk-first`). Merge the cleanest/foundational PR (fast-forward if possible).
5. **Per-PR loop** (`§per-pr-loop` + `conflict-resolution.md`). For each remaining PR: read its full
   diff → verify landing zones → resolve collisions/duplicates → **apply by hand, edit by edit** →
   `verify_scaffold.py` + phrase/no-stray-ID grep → commit. **Never raw `git merge`** (`§manual-not-merge`).
6. **Reconcile counters** (`§reconcile` / `§counter-reconcile`). One `chore:` commit setting the
   declared §0 + sub-skill mirror counters to the grep-actual numbers. End on `verify_scaffold.py` OK.
7. **Finish** (`§finish`). The branch is ready, all local. **Ask the user**, one at a time: push? open
   a PR into the sprint branch (show title+body, get OK)? close the child PRs (flag close-not-merge)?

## Deliverables

- A new **integration branch** (user-named) in `CODE_REPO` with one commit per merged PR + one
  counter-reconcile commit; `verify_scaffold.py` clean. **Local by default — nothing pushed.**
- On the user's explicit go-ahead at §finish: the branch pushed, a PR opened into the sprint branch,
  and the child PRs commented + closed.

## Guardrails

- 🔴 **Never raw `git merge` the child branches** — apply by hand (`§manual-not-merge`). A naive merge
  silently appends duplicate rule IDs.
- 🔴 **Push / PR / close are outward-facing** — do them **only on the user's explicit yes**, one at a
  time; in auto mode treat `git push` as needing an explicit go-ahead (`project-config.md §git-rules`).
  Show the PR title+body before `gh pr create`.
- **Only edit the scaffold files** (`project-config.md §scaffold-files`) — never application source.
- **`verify_scaffold.py` must print `OK` before every commit** (`§verify-each-step`). A clean
  `git diff` is not sufficient — also grep for stray un-renamed collision IDs.
- **Conventional commits, no `Co-Authored-By` / no footer.** Never `git push --force`.
- File/commit text **English or Japanese only**; keep JP rule IDs / labels verbatim.

## Portability

Distributed as the `merge` skill of the `w3-rk-scaffold-merging` plugin (marketplace `w3-rk-skills`).
`scripts/verify_scaffold.py` + all `references/` are bundled; `CODE_REPO` resolves to the **session
cwd**, so no per-machine edit is needed. The only project-specific values are the scaffold-file paths
and §0 markers (`project-config.md §scaffold-files`, `verify_scaffold.py` `RE_*` block) and the sprint
branch (discovered from the PRs, else asked). No dependency on Claude Code memory files.
